import pytest
from pydantic import ValidationError

from app.schemas.ml import SteelFaultPredictionRequest
from app.schemas.quote import QuoteRequest


def test_quote_schema_valid():
    q = QuoteRequest(
        request_id="REQ-1",
        customer_name="A",
        product_form="foil",
        thickness_mm=0.1,
        width_mm=10,
        qty_kg=50,
    )
    assert q.request_id == "REQ-1"


def test_quote_schema_invalid_missing_request_id():
    with pytest.raises(ValidationError):
        QuoteRequest(
            customer_name="A", product_form="foil", thickness_mm=0.1, width_mm=10, qty_kg=50
        )


def test_ml_prediction_schema_valid():
    req = SteelFaultPredictionRequest(features={"X_Minimum": 1.0})
    assert "X_Minimum" in req.features
