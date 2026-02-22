from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app


@pytest.fixture
def settings_override() -> Iterator:
    settings = get_settings()
    previous: dict[str, object] = {}

    def apply(**kwargs):
        for key, value in kwargs.items():
            if key not in previous:
                previous[key] = getattr(settings, key)
            setattr(settings, key, value)

    yield apply

    for key, value in previous.items():
        setattr(settings, key, value)


def _quote_payload(request_id: str) -> dict:
    return {
        "request_id": request_id,
        "alloy_name": "316L",
        "product_form": "foil",
        "thickness_mm": 0.04,
        "width_mm": 120.0,
        "qty_kg": 100.0,
        "required_lead_time_days": 14,
        "special_requirements": "tight tolerance",
    }


def test_admin_endpoint_requires_token_when_configured(settings_override):
    settings_override(
        app_env="cloud",
        admin_api_token="unit-test-token",
        rate_limit_enabled=False,
    )
    client = TestClient(create_app())

    response = client.post("/retrieval/reindex")
    assert response.status_code == 401
    assert "Invalid admin token" in response.text


def test_admin_endpoint_disabled_without_token_in_cloud(settings_override):
    settings_override(
        app_env="cloud",
        admin_api_token="",
        rate_limit_enabled=False,
    )
    client = TestClient(create_app())

    response = client.post("/ml/train/steel-faults", json={})
    assert response.status_code == 503
    assert "disabled" in response.text.lower()


def test_request_size_limit_blocks_large_payload(settings_override):
    settings_override(
        app_env="local",
        admin_api_token="",
        max_request_size_bytes=180,
        rate_limit_enabled=False,
    )
    client = TestClient(create_app())

    payload = _quote_payload("REQ-SIZE-1")
    payload["special_requirements"] = "X" * 2000
    response = client.post("/quote/validate", json=payload)
    assert response.status_code == 413


def test_rate_limit_enforced_on_quote_validate(settings_override):
    settings_override(
        app_env="local",
        rate_limit_enabled=True,
        rate_limit_default_per_minute=100,
        rate_limit_quote_per_minute=2,
        rate_limit_quote_llm_per_minute=2,
        max_request_size_bytes=1_000_000,
    )
    client = TestClient(create_app())

    first = client.post("/quote/validate", json=_quote_payload("REQ-RATE-1"))
    second = client.post("/quote/validate", json=_quote_payload("REQ-RATE-2"))
    third = client.post("/quote/validate", json=_quote_payload("REQ-RATE-3"))

    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 429
    assert "retry_after_seconds" in third.json()


def test_docs_hidden_when_disabled(settings_override):
    settings_override(
        app_env="cloud",
        enable_api_docs=False,
        rate_limit_enabled=False,
    )
    client = TestClient(create_app())

    response = client.get("/docs")
    assert response.status_code == 404


def test_wildcard_cors_disabled_in_non_local(settings_override):
    settings_override(
        app_env="cloud",
        cors_allow_origins="*",
        cors_allow_credentials=False,
        rate_limit_enabled=False,
    )
    client = TestClient(create_app())

    response = client.options(
        "/health",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in {
        key.lower(): value for key, value in response.headers.items()
    }
