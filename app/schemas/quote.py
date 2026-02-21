from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import Citation, WarningItem


class QuoteRequest(BaseModel):
    request_id: str
    customer_name: str | None = None
    industry: str | None = None
    alloy_name: str | None = None
    alloy_family: str | None = None
    product_form: str | None = None
    thickness_mm: float | None = None
    width_mm: float | None = None
    qty_kg: float | None = None
    required_lead_time_days: int | None = None
    lead_time_requested_days: int | None = None
    cert_required: str | None = None
    temper: str | None = None
    finish: str | None = None
    application_description: str | None = None
    special_requirements: str | None = None

    @model_validator(mode="after")
    def normalize_lead_time(self) -> "QuoteRequest":
        if self.required_lead_time_days is None and self.lead_time_requested_days is not None:
            self.required_lead_time_days = self.lead_time_requested_days
        if self.lead_time_requested_days is None and self.required_lead_time_days is not None:
            self.lead_time_requested_days = self.required_lead_time_days
        return self


class QuoteValidationResponse(BaseModel):
    request_id: str
    is_valid: bool
    missing_fields: list[str] = Field(default_factory=list)
    warnings: list[WarningItem] = Field(default_factory=list)
    escalation_required: bool = False
    confidence: float = 0.0
    suggested_actions: list[str] = Field(default_factory=list)


class RuleViolation(BaseModel):
    rule_id: str
    severity: str
    passed: bool
    message: str
    field_refs: list[str] = Field(default_factory=list)


class RecommendedOption(BaseModel):
    option_id: str
    alloy_name: str | None = None
    product_form: str | None = None
    cert_required: str | None = None
    estimated_price_per_kg_low: float | None = None
    estimated_price_per_kg_high: float | None = None
    estimated_lead_time_days_low: int | None = None
    estimated_lead_time_days_high: int | None = None
    rationale: str


class SimilarQuoteItem(BaseModel):
    quote_id: str
    quote_date: str | None = None
    customer_name: str | None = None
    alloy_name: str | None = None
    product_form: str | None = None
    thickness_mm: float | None = None
    width_mm: float | None = None
    qty_kg: float | None = None
    cert_required: str | None = None
    lead_time_days: int | None = None
    price_total_usd: float | None = None
    status: str | None = None
    similarity_score: float | None = None


class QuoteDraftResponse(BaseModel):
    request_id: str
    draft: dict[str, Any]
    recommended_options: list[RecommendedOption] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)
    rule_violations: list[RuleViolation] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    warnings: list[WarningItem] = Field(default_factory=list)
    similar_quotes: list[SimilarQuoteItem] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    confidence: float = 0.0
    escalation_required: bool = False
    used_fallback: bool = False


class QuoteAnswerRequest(BaseModel):
    question: str | None = None
    query: str | None = None
    top_k: int = 5

    @model_validator(mode="after")
    def validate_question(self) -> "QuoteAnswerRequest":
        question = (self.question or self.query or "").strip()
        if not question:
            raise ValueError("Either 'question' or 'query' must be provided.")
        self.question = question
        self.query = question
        return self


class QuoteAnswerResponse(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    confidence: float = 0.0
    warnings: list[WarningItem] = Field(default_factory=list)


class SimilarQuoteQueryResponse(BaseModel):
    query: dict[str, Any]
    matches: list[SimilarQuoteItem] = Field(default_factory=list)
