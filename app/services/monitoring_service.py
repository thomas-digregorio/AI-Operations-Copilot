from __future__ import annotations

import json

import pandas as pd

from app.core.constants import DEFAULT_METRICS_PATH


class MonitoringService:
    def drift_summary(self, rows: list[dict[str, float]], threshold: float = 1.0) -> dict:
        if not DEFAULT_METRICS_PATH.exists():
            raise FileNotFoundError("Metrics artifact missing. Train model first.")
        with DEFAULT_METRICS_PATH.open("r", encoding="utf-8") as f:
            metrics = json.load(f)

        feature_stats = metrics.get("train_feature_stats", {})
        if not feature_stats:
            return {"feature_shift_summary": {}, "drift_flags": []}

        df = pd.DataFrame(rows)
        summary = {}
        flags = []
        for feature, stat in feature_stats.items():
            if feature not in df.columns:
                continue
            mean_train = float(stat.get("mean", 0.0))
            std_train = float(stat.get("std", 1.0)) or 1.0
            mean_batch = float(df[feature].mean())
            shift = abs(mean_batch - mean_train) / std_train
            summary[feature] = round(shift, 4)
            if shift > threshold:
                flags.append(feature)

        return {"feature_shift_summary": summary, "drift_flags": flags}
