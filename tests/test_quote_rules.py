from app.schemas.quote import QuoteRequest
from app.services.rule_engine_service import RuleEngineService


def _base_quote() -> QuoteRequest:
    return QuoteRequest(
        request_id="REQ-TEST",
        customer_name="Acme",
        alloy_name="316L",
        product_form="foil",
        thickness_mm=0.2,
        width_mm=120,
        qty_kg=220,
        cert_required="EN_10204_3.1",
        required_lead_time_days=21,
    )


def test_moq_check(ensure_rule_data):
    material_path, pricing_path = ensure_rule_data
    svc = RuleEngineService(material_path, pricing_path)
    q = _base_quote().model_copy(update={"qty_kg": 50})
    out = svc.validate_quote(q)
    assert any(w.code == "below_moq" for w in out.warnings)


def test_dimension_bounds_check(ensure_rule_data):
    material_path, pricing_path = ensure_rule_data
    svc = RuleEngineService(material_path, pricing_path)
    q = _base_quote().model_copy(update={"thickness_mm": 5.0})
    out = svc.validate_quote(q)
    assert any(w.code == "thickness_out_of_bounds" for w in out.warnings)


def test_cert_constraint_check(ensure_rule_data):
    material_path, pricing_path = ensure_rule_data
    svc = RuleEngineService(material_path, pricing_path)
    q = _base_quote().model_copy(update={"cert_required": "AS9100"})
    out = svc.validate_quote(q)
    assert any(w.code == "cert_mismatch" for w in out.warnings)


def test_engineering_escalation_trigger(ensure_rule_data):
    material_path, pricing_path = ensure_rule_data
    svc = RuleEngineService(material_path, pricing_path)
    q = _base_quote().model_copy(update={"thickness_mm": 0.03})
    out = svc.validate_quote(q)
    assert out.escalation_required is True
    assert any(w.code == "thin_foil_review" for w in out.warnings)
