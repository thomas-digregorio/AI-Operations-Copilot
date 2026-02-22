from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from app.core.constants import (
    DEFAULT_FEATURES_PATH,
    DEFAULT_METRICS_PATH,
    DEFAULT_MODEL_PATH,
    STEEL_RAW_DIR,
)
from app.utils.metrics import multiclass_metrics

FEATURE_COLUMNS = [
    "X_Minimum",
    "X_Maximum",
    "Y_Minimum",
    "Y_Maximum",
    "Pixels_Areas",
    "X_Perimeter",
    "Y_Perimeter",
    "Sum_of_Luminosity",
    "Minimum_of_Luminosity",
    "Maximum_of_Luminosity",
    "Length_of_Conveyer",
    "TypeOfSteel_A300",
    "TypeOfSteel_A400",
    "Steel_Plate_Thickness",
    "Edges_Index",
    "Empty_Index",
    "Square_Index",
    "Outside_X_Index",
    "Edges_X_Index",
    "Edges_Y_Index",
    "Outside_Global_Index",
    "LogOfAreas",
    "Log_X_Index",
    "Log_Y_Index",
    "Orientation_Index",
    "Luminosity_Index",
    "SigmoidOfAreas",
]

LABEL_COLUMNS = [
    "Pastry",
    "Z_Scratch",
    "K_Scatch",
    "Stains",
    "Dirtiness",
    "Bumps",
    "Other_Faults",
]


class SteelModelService:
    def _resolve_dataset_path(self, dataset_path: str | None = None) -> Path:
        if dataset_path:
            return Path(dataset_path)
        candidates = list(STEEL_RAW_DIR.glob("*.csv")) + list(STEEL_RAW_DIR.glob("*.data"))
        if not candidates:
            raise FileNotFoundError(
                "Steel dataset file not found. Place CSV/data file under "
                "data/raw/steel_plates_faults/."
            )
        return candidates[0]

    def load_raw_dataset(self, dataset_path: str | None = None) -> pd.DataFrame:
        path = self._resolve_dataset_path(dataset_path)
        expected = len(FEATURE_COLUMNS) + len(LABEL_COLUMNS)
        df = self._read_dataset_with_supported_delimiters(path, expected)
        df.columns = FEATURE_COLUMNS + LABEL_COLUMNS
        return df

    def _read_dataset_with_supported_delimiters(
        self, path: Path, expected_cols: int
    ) -> pd.DataFrame:
        # UCI Faults.NNA is typically tab-delimited; tests use comma-separated CSV.
        candidates: list[tuple[str, str | None]] = [
            ("tab", "\t"),
            ("comma", ","),
            ("semicolon", ";"),
            ("whitespace", r"\s+"),
        ]
        tried: list[str] = []
        last_shape: tuple[int, int] | None = None
        for label, sep in candidates:
            tried.append(label)
            kwargs = {"header": None}
            if sep is not None:
                kwargs["sep"] = sep
                kwargs["engine"] = "python"
            df = pd.read_csv(path, **kwargs)
            last_shape = df.shape
            if df.shape[1] == expected_cols:
                return df

        raise ValueError(
            f"Unexpected steel dataset shape: {last_shape}. Expected {expected_cols} columns. "
            f"Tried delimiters: {tried}."
        )

    def convert_multiclass_labels(self, df: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
        y_idx = df[LABEL_COLUMNS].values.argmax(axis=1)
        X = df[FEATURE_COLUMNS].copy()
        return X, y_idx

    def train(self, dataset_path: str | None = None, random_seed: int = 42) -> dict:
        from xgboost import XGBClassifier

        df = self.load_raw_dataset(dataset_path)
        X, y = self.convert_multiclass_labels(df)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=random_seed, stratify=y
        )

        model = XGBClassifier(
            n_estimators=250,
            max_depth=6,
            learning_rate=0.08,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="multi:softprob",
            num_class=len(LABEL_COLUMNS),
            eval_metric="mlogloss",
            n_jobs=4,
            tree_method="hist",
            random_state=random_seed,
        )
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        metrics = multiclass_metrics(y_test, y_pred, labels=list(range(len(LABEL_COLUMNS))))

        DEFAULT_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, DEFAULT_MODEL_PATH)

        with DEFAULT_FEATURES_PATH.open("w", encoding="utf-8") as f:
            json.dump(
                {"feature_columns": FEATURE_COLUMNS, "label_columns": LABEL_COLUMNS}, f, indent=2
            )

        train_stats = {
            col: {"mean": float(X_train[col].mean()), "std": float(X_train[col].std() or 1.0)}
            for col in FEATURE_COLUMNS
        }
        payload = {
            **metrics,
            "feature_columns": FEATURE_COLUMNS,
            "label_columns": LABEL_COLUMNS,
            "train_feature_stats": train_stats,
        }
        with DEFAULT_METRICS_PATH.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        return {
            "model_path": str(DEFAULT_MODEL_PATH),
            "metrics_path": str(DEFAULT_METRICS_PATH),
            "metrics": payload,
        }

    def _load_model(self):
        if not DEFAULT_MODEL_PATH.exists() or not DEFAULT_FEATURES_PATH.exists():
            raise FileNotFoundError("Model artifacts missing. Run training first.")
        model = joblib.load(DEFAULT_MODEL_PATH)
        with DEFAULT_FEATURES_PATH.open("r", encoding="utf-8") as f:
            meta = json.load(f)
        return model, meta["feature_columns"], meta["label_columns"]

    def predict_single(self, features: dict[str, float]) -> dict:
        model, feature_columns, label_columns = self._load_model()
        row = pd.DataFrame(
            [[float(features.get(c, 0.0)) for c in feature_columns]], columns=feature_columns
        )
        prob = model.predict_proba(row)[0]
        idx = int(np.argmax(prob))
        return {
            "predicted_class": label_columns[idx],
            "confidence": float(prob[idx]),
            "probabilities": {label_columns[i]: float(prob[i]) for i in range(len(label_columns))},
        }

    def predict_batch(self, rows: list[dict[str, float]]) -> list[dict]:
        return [self.predict_single(r) for r in rows]
