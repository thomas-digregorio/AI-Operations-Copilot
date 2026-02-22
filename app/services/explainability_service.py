from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd

from app.core.constants import DEFAULT_FEATURES_PATH, DEFAULT_MODEL_PATH


class ExplainabilityService:
    def _load_model_meta(self):
        if not DEFAULT_MODEL_PATH.exists() or not DEFAULT_FEATURES_PATH.exists():
            raise FileNotFoundError("Model artifacts missing. Train model before explanation.")

        model = joblib.load(DEFAULT_MODEL_PATH)
        with DEFAULT_FEATURES_PATH.open("r", encoding="utf-8") as f:
            meta = json.load(f)
        return model, meta["feature_columns"], meta["label_columns"]

    def explain_local(self, features: dict[str, float]) -> dict:
        import shap

        model, feature_columns, label_columns = self._load_model_meta()

        row = pd.DataFrame(
            [[float(features.get(c, 0.0)) for c in feature_columns]],
            columns=feature_columns,
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

    def explain_global(self, top_k: int = 20) -> dict:
        model, feature_columns, _label_columns = self._load_model_meta()

        if hasattr(model, "feature_importances_"):
            importances = np.asarray(model.feature_importances_, dtype=float)
        else:
            importances = np.zeros(len(feature_columns), dtype=float)

        limit = min(len(feature_columns), len(importances))
        importance_map = {feature_columns[i]: float(importances[i]) for i in range(limit)}
        ranked = sorted(importance_map.items(), key=lambda kv: kv[1], reverse=True)
        if top_k > 0:
            ranked = ranked[:top_k]
        ranked_map = {k: round(v, 8) for k, v in ranked}
        return {
            "model_name": "steel_fault_xgb",
            "feature_importance": ranked_map,
            "top_features": [k for k, _ in ranked],
        }
