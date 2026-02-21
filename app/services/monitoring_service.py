from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.core.constants import DEFAULT_METRICS_PATH, DEFAULT_MODEL_PATH, EVALS_DIR, ROOT_DIR
from app.db.models import MLPredictionLog


class MonitoringService:
    def drift_summary(self, rows: list[dict[str, float]], threshold: float = 1.0) -> dict:
        if not DEFAULT_METRICS_PATH.exists():
            raise FileNotFoundError("Metrics artifact missing. Train model first.")
        with DEFAULT_METRICS_PATH.open("r", encoding="utf-8") as f:
            metrics = json.load(f)

        feature_stats = metrics.get("train_feature_stats", {})
        if not feature_stats:
            return {
                "feature_shift_summary": {},
                "drift_flags": [],
                "missing_features": [],
                "unknown_features": [],
                "rows_evaluated": len(rows),
                "threshold": threshold,
                "mean_shift": 0.0,
                "max_shift": 0.0,
                "severity": "low",
            }

        if not rows:
            return {
                "feature_shift_summary": {},
                "drift_flags": [],
                "missing_features": sorted(feature_stats.keys()),
                "unknown_features": [],
                "rows_evaluated": 0,
                "threshold": threshold,
                "mean_shift": 0.0,
                "max_shift": 0.0,
                "severity": "critical",
            }

        df = pd.DataFrame(rows)
        summary: dict[str, float] = {}
        flags: list[str] = []
        expected_features = set(feature_stats.keys())
        present_features = set(df.columns)
        missing_features = sorted(expected_features - present_features)
        unknown_features = sorted(present_features - expected_features)

        for feature, stat in feature_stats.items():
            if feature not in df.columns:
                continue
            mean_train = float(stat.get("mean", 0.0))
            std_train = float(stat.get("std", 1.0)) or 1.0
            mean_batch = float(pd.to_numeric(df[feature], errors="coerce").mean())
            shift = abs(mean_batch - mean_train) / std_train
            summary[feature] = round(shift, 4)
            if shift > threshold:
                flags.append(feature)

        mean_shift = float(np.mean(list(summary.values()))) if summary else 0.0
        max_shift = float(max(summary.values())) if summary else 0.0
        severity = self._severity(max_shift, len(flags), len(summary), threshold)

        return {
            "feature_shift_summary": summary,
            "drift_flags": flags,
            "missing_features": missing_features,
            "unknown_features": unknown_features,
            "rows_evaluated": int(len(df)),
            "threshold": threshold,
            "mean_shift": round(mean_shift, 4),
            "max_shift": round(max_shift, 4),
            "severity": severity,
        }

    def evaluation_report(self) -> dict:
        eval_summary_path = EVALS_DIR / "steel_eval_summary.json"
        report = {
            "model_artifact_exists": False,
            "metrics_artifact_exists": DEFAULT_METRICS_PATH.exists(),
            "macro_f1": None,
            "accuracy": None,
            "label_count": 0,
            "confusion_matrix_present": False,
            "performance_status": "missing",
            "performance_notes": [],
            "metrics_path": self._pretty_path(DEFAULT_METRICS_PATH),
            "eval_summary_path": self._pretty_path(eval_summary_path),
        }
        notes: list[str] = []

        report["model_artifact_exists"] = DEFAULT_MODEL_PATH.exists()

        if not DEFAULT_METRICS_PATH.exists():
            notes.append("Model metrics file is missing; run training pipeline.")
            report["performance_notes"] = notes
            return report

        with DEFAULT_METRICS_PATH.open("r", encoding="utf-8") as f:
            metrics = json.load(f)

        macro_f1 = float(metrics.get("macro_f1", 0.0))
        accuracy = float(metrics.get("report", {}).get("accuracy", 0.0))
        labels = metrics.get("label_columns", [])
        confusion_matrix_present = bool(metrics.get("confusion_matrix"))

        report["macro_f1"] = round(macro_f1, 4)
        report["accuracy"] = round(accuracy, 4)
        report["label_count"] = int(len(labels))
        report["confusion_matrix_present"] = confusion_matrix_present

        if macro_f1 >= 0.8:
            status = "pass"
            notes.append("Macro F1 is above target threshold (0.80).")
        elif macro_f1 >= 0.7:
            status = "warn"
            notes.append("Macro F1 is acceptable but below preferred target (0.80).")
        else:
            status = "fail"
            notes.append("Macro F1 is below minimum acceptable threshold (0.70).")

        if not confusion_matrix_present:
            notes.append("Confusion matrix missing from training metrics.")
            if status == "pass":
                status = "warn"

        if eval_summary_path.exists():
            with eval_summary_path.open("r", encoding="utf-8") as f:
                eval_summary = json.load(f)
            if not eval_summary.get("has_confusion_matrix", False):
                notes.append("Evaluation summary indicates missing confusion matrix.")
                if status == "pass":
                    status = "warn"
        else:
            notes.append("Eval summary missing; run evaluation pipeline.")
            if status == "pass":
                status = "warn"

        report["performance_status"] = status
        report["performance_notes"] = notes
        return report

    def prediction_monitoring_summary(self, db: Session, window_days: int = 30) -> dict:
        cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
        rows = (
            db.query(MLPredictionLog)
            .filter(MLPredictionLog.created_at >= cutoff)
            .order_by(MLPredictionLog.created_at.asc())
            .all()
        )
        if not rows:
            return {
                "total_predictions": 0,
                "average_confidence": 0.0,
                "class_distribution": {},
                "daily_prediction_counts": [],
            }

        total = len(rows)
        avg_conf = sum(float(r.confidence) for r in rows) / total
        class_dist = Counter(r.predicted_class for r in rows)

        by_day = defaultdict(int)
        for row in rows:
            day_key = row.created_at.date().isoformat()
            by_day[day_key] += 1
        daily_counts = [{"date": day, "count": count} for day, count in sorted(by_day.items())]

        return {
            "total_predictions": total,
            "average_confidence": round(avg_conf, 4),
            "class_distribution": dict(sorted(class_dist.items())),
            "daily_prediction_counts": daily_counts,
        }

    @staticmethod
    def _severity(max_shift: float, flag_count: int, observed_count: int, threshold: float) -> str:
        if observed_count == 0:
            return "critical"
        flag_ratio = flag_count / observed_count
        if max_shift >= threshold * 2.0 or flag_ratio >= 0.5:
            return "critical"
        if max_shift >= threshold * 1.5 or flag_ratio >= 0.3:
            return "high"
        if flag_count > 0:
            return "medium"
        return "low"

    @staticmethod
    def _pretty_path(path: Path) -> str:
        try:
            return str(path.relative_to(ROOT_DIR))
        except ValueError:
            return str(path)
