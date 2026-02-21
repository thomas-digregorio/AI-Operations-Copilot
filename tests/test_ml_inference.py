from fastapi.testclient import TestClient

from app.main import app
from app.services.steel_model_service import FEATURE_COLUMNS, SteelModelService

client = TestClient(app)


def _sample_features():
    return {k: 0.1 for k in FEATURE_COLUMNS}


def test_scoring_endpoint_returns_schema_valid_response(synthetic_steel_dataset):
    svc = SteelModelService()
    svc.train(str(synthetic_steel_dataset))

    resp = client.post("/ml/predict/steel-faults", json={"features": _sample_features()})
    assert resp.status_code == 200
    body = resp.json()
    assert "predicted_class" in body
    assert "confidence" in body
    assert "probabilities" in body
