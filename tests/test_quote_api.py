from fastapi.testclient import TestClient

from app.main import app
from app.pipelines.build_synthetic_quote_data import main as seed_quote_data
from app.pipelines.ingest_internal_mock_docs import main as seed_docs

client = TestClient(app)


def _payload():
    return {
        "request_id": "REQ-API-1",
        "customer_name": "Acme",
        "alloy_name": "316L",
        "product_form": "foil",
        "thickness_mm": 0.04,
        "width_mm": 120,
        "qty_kg": 100,
        "cert_required": "EN_10204_3.1",
        "required_lead_time_days": 14,
        "special_requirements": "tight tolerance",
    }


def test_quote_validate_endpoint():
    seed_quote_data()
    resp = client.post("/quote/validate", json=_payload())
    assert resp.status_code == 200
    body = resp.json()
    assert "is_valid" in body
    assert "warnings" in body


def test_quote_draft_endpoint_fallback_mode(monkeypatch):
    seed_quote_data()
    seed_docs()
    from app.api.routers.quote import service

    monkeypatch.setattr(service.settings, "llm_provider", "disabled")

    resp = client.post("/quote/draft", json=_payload())
    assert resp.status_code == 200
    body = resp.json()
    assert body["used_fallback"] is True
    assert "draft" in body
    assert "recommended_options" in body
    assert "rule_violations" in body
    assert "assumptions" in body
    assert "similar_quotes" in body
    assert "confidence" in body


def test_quote_answer_endpoint_supports_question_field():
    seed_docs()
    resp = client.post(
        "/quote/answer",
        json={
            "question": "What are the lead-time policies for thin foil?",
            "top_k": 3,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "answer" in body
    assert "confidence" in body
    assert "warnings" in body


def test_quote_history_similar_endpoint():
    seed_quote_data()
    resp = client.get(
        "/quote/history/similar",
        params={
            "alloy_name": "316L",
            "product_form": "foil",
            "qty_kg": 120,
            "thickness_mm": 0.1,
            "width_mm": 150,
            "top_k": 5,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "matches" in body
