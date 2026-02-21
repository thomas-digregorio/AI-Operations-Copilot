from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd
import shap

from app.core.constants import DEFAULT_FEATURES_PATH, DEFAULT_MODEL_PATH


class ExplainabilityService:
    def explain_local(self, features: dict[str, float]) -> dict:
        if not DEFAULT_MODEL_PATH.exists() or not DEFAULT_FEATURES_PATH.exists():
            raise FileNotFoundError("Model artifacts missing. Train model before explanation.")

        model = joblib.load(DEFAULT_MODEL_PATH)
        with DEFAULT_FEATURES_PATH.open("r", encoding="utf-8") as f:
            meta = json.load(f)
        feature_columns = meta["feature_columns"]
        label_columns = meta["label_columns"]

        row = pd.DataFrame(
            [[float(features.get(c, 0.0)) for c in feature_columns]], columns=feature_columns
        )

        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(row)

        probabilities = model.predict_proba(row)[0]
        pred_idx = int(np.argmax(probabilities))

        # shap_values may be list[class] or ndarray depending on model/lib version.
        if isinstance(shap_values, list):
            contrib = shap_values[pred_idx][0]
            base_value = float(explainer.expected_value[pred_idx])
        else:
            contrib = shap_values[0, :, pred_idx] if shap_values.ndim == 3 else shap_values[0]
            base_value = float(
                explainer.expected_value[pred_idx]
                if np.ndim(explainer.expected_value)
                else explainer.expected_value
            )

        contributions = {feature_columns[i]: float(contrib[i]) for i in range(len(feature_columns))}
        contributions = dict(
            sorted(contributions.items(), key=lambda kv: abs(kv[1]), reverse=True)[:10]
        )

        return {
            "predicted_class": label_columns[pred_idx],
            "base_value": base_value,
            "feature_contributions": contributions,
        }
