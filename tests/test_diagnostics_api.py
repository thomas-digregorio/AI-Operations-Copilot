import json

from fastapi.testclient import TestClient

from app.main import app
from app.pipelines.ingest_internal_mock_docs import main as seed_docs
from app.services.steel_model_service import FEATURE_COLUMNS, SteelModelService

client = TestClient(app)


def _sample_rows(rows: int = 4) -> list[dict[str, float]]:
    payload = []
    for i in range(rows):
        row = {k: 0.1 for k in FEATURE_COLUMNS}
        row["X_Minimum"] = 40 + i
        row["Y_Minimum"] = 1000 + (10 * i)
        payload.append(row)
    return payload


def test_diagnostics_status_exposes_safe_summary():
    seed_docs()
    response = client.get("/diagnostics/status")
    assert response.status_code == 200
    body = response.json()
    assert "config_summary" in body
    assert "indexed_doc_sources" in body
    assert "openai_api_key" not in json.dumps(body).lower()


def test_drift_summary_endpoint_returns_hardened_fields(synthetic_steel_dataset):
    svc = SteelModelService()
    svc.train(str(synthetic_steel_dataset))

    response = client.post(
        "/diagnostics/drift-summary",
        json={"rows": _sample_rows(), "threshold": 0.8},
    )
    assert response.status_code == 200
    body = response.json()
    assert "severity" in body
    assert body["rows_evaluated"] == 4
    assert "mean_shift" in body
    assert "max_shift" in body
    assert "missing_features" in body
    assert "unknown_features" in body


def test_eval_report_endpoint_returns_status(synthetic_steel_dataset):
    svc = SteelModelService()
    svc.train(str(synthetic_steel_dataset))

    response = client.get("/diagnostics/eval-report")
    assert response.status_code == 200
    body = response.json()
    assert body["performance_status"] in {"pass", "warn", "fail", "missing"}
    assert "metrics_path" in body


def test_prediction_summary_endpoint_tracks_persistent_logs(synthetic_steel_dataset):
    svc = SteelModelService()
    svc.train(str(synthetic_steel_dataset))
    sample = {k: 0.2 for k in FEATURE_COLUMNS}
    pred = client.post("/ml/predict/steel-faults", json={"features": sample})
    assert pred.status_code == 200

    response = client.get("/diagnostics/prediction-summary", params={"window_days": 90})
    assert response.status_code == 200
    body = response.json()
    assert body["total_predictions"] >= 1
    assert "class_distribution" in body
    assert "daily_prediction_counts" in body
