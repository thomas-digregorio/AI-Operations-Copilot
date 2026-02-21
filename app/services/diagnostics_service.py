from __future__ import annotations

from app.core.constants import DEFAULT_METRICS_PATH, DEFAULT_MODEL_PATH, VECTOR_DIR


class DiagnosticsService:
    def status(self) -> dict:
        return {
            "model_artifact_exists": DEFAULT_MODEL_PATH.exists(),
            "metrics_artifact_exists": DEFAULT_METRICS_PATH.exists(),
            "vector_index_exists": VECTOR_DIR.exists() and any(VECTOR_DIR.iterdir()),
            "vector_index_path": str(VECTOR_DIR),
            "model_path": str(DEFAULT_MODEL_PATH),
            "metrics_path": str(DEFAULT_METRICS_PATH),
        }
