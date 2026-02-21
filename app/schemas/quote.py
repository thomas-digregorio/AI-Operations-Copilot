from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import Citation, WarningItem


class QuoteRequest(BaseModel):
    request_id: str
    customer_name: str | None = None
    alloy_name: str | None = None
    product_form: str | None = None
    thickness_mm: float | None = None
    width_mm: float | None = None
    qty_kg: float | None = None
    required_lead_time_days: int | None = None
    cert_required: str | None = None
    temper: str | None = None
    special_requirements: str | None = None


class QuoteValidationResponse(BaseModel):
    request_id: str
    is_valid: bool
    missing_fields: list[str] = Field(default_factory=list)
    warnings: list[WarningItem] = Field(default_factory=list)
    escalation_required: bool = False
    confidence: float = 0.0
    suggested_actions: list[str] = Field(default_factory=list)


class QuoteDraftResponse(BaseModel):
    request_id: str
    draft: dict[str, Any]
    missing_fields: list[str] = Field(default_factory=list)
    warnings: list[WarningItem] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    escalation_required: bool = False
    used_fallback: bool = False


class QuoteAnswerRequest(BaseModel):
    query: str
    top_k: int = 5


class QuoteAnswerResponse(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)
