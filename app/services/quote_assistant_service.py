from __future__ import annotations

import json
from typing import Any

import httpx
import pandas as pd
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.constants import PRICING_RULES_PATH
from app.schemas.common import WarningItem
from app.schemas.quote import (
    QuoteAnswerResponse,
    QuoteDraftResponse,
    QuoteRequest,
    QuoteValidationResponse,
    RecommendedOption,
    RuleViolation,
    SimilarQuoteItem,
    SimilarQuoteQueryResponse,
)
from app.services.quote_history_service import QuoteHistoryService
from app.services.rag_service import RAGService
from app.services.rule_engine_service import RuleEngineService


class QuoteAssistantService:
    def __init__(self):
        self.settings = get_settings()
        self.rule_engine = RuleEngineService()
        self.rag_service = RAGService()
        self.history_service = QuoteHistoryService()

    def validate(self, quote: QuoteRequest) -> QuoteValidationResponse:
        return self.rule_engine.validate_quote(quote)

    def answer(self, query: str, top_k: int = 5, db: Session | None = None) -> QuoteAnswerResponse:
        citations = self.rag_service.search(query, top_k=top_k, db=db)
        if not citations:
            return QuoteAnswerResponse(
                answer="No indexed citations available yet. Ingest and index local docs first.",
                citations=[],
                confidence=0.0,
                warnings=[
                    WarningItem(
                        code="no_citations",
                        message="No retrieval context is indexed yet. Run ingestion/reindex first.",
                    )
                ],
            )

        answer = (
            "Retrieved relevant guidance from local corpus. "
            "Use citations for traceable quote support."
        )
        avg_score = sum(float(c.score or 0.0) for c in citations) / len(citations)
        confidence = max(0.25, min(0.95, 1.0 / (1.0 + max(0.0, avg_score))))
        return QuoteAnswerResponse(
            answer=answer,
            citations=citations,
            confidence=round(confidence, 3),
            warnings=[],
        )

    def similar_quotes(self, quote: QuoteRequest, top_k: int = 5) -> SimilarQuoteQueryResponse:
        matches = self.history_service.find_similar_quotes(
            alloy_name=quote.alloy_name,
            product_form=quote.product_form,
            qty_kg=quote.qty_kg,
            thickness_mm=quote.thickness_mm,
            width_mm=quote.width_mm,
            top_k=top_k,
        )
        return SimilarQuoteQueryResponse(query=quote.model_dump(), matches=matches)

    def _price_band(self, alloy_name: str | None) -> tuple[float | None, float | None]:
        if not PRICING_RULES_PATH.exists():
            return None, None
        df = pd.read_csv(PRICING_RULES_PATH)
        rows = df[df["rule_type"].str.lower().eq("price_band")]
        if alloy_name:
            rows = rows[rows["alloy_name"].str.lower().eq(alloy_name.lower())]
        if rows.empty:
            return None, None
        row = rows.iloc[0]
        return float(row.get("price_per_kg_low", 0.0)), float(row.get("price_per_kg_high", 0.0))

    def _price_hint(self, alloy_name: str | None, qty_kg: float | None) -> str:
        low, high = self._price_band(alloy_name)
        if low is None or high is None:
            return "No matching price band found."
        if qty_kg:
            return (
                f"Estimated unit range ${low:.2f}-${high:.2f}/kg; "
                f"order estimate ${low * qty_kg:.2f}-${high * qty_kg:.2f}."
            )
        return f"Estimated unit range ${low:.2f}-${high:.2f}/kg."

    def _rule_violations(self, validation: QuoteValidationResponse) -> list[RuleViolation]:
        violations: list[RuleViolation] = []
        field_map = {
            "thickness_out_of_bounds": ["thickness_mm"],
            "width_out_of_bounds": ["width_mm"],
            "unsupported_form": ["product_form"],
            "unsupported_alloy": ["alloy_name"],
            "below_moq": ["qty_kg"],
            "cert_mismatch": ["cert_required"],
            "lead_time_risk": ["required_lead_time_days"],
            "thin_foil_review": ["thickness_mm"],
            "special_requirement_review": ["special_requirements"],
        }
        severity_map = {
            "thickness_out_of_bounds": "error",
            "width_out_of_bounds": "error",
            "unsupported_form": "error",
            "unsupported_alloy": "error",
            "below_moq": "warning",
            "cert_mismatch": "warning",
            "lead_time_risk": "warning",
            "thin_foil_review": "warning",
            "special_requirement_review": "warning",
        }
        for warning in validation.warnings:
            violations.append(
                RuleViolation(
                    rule_id=warning.code,
                    severity=severity_map.get(warning.code, "warning"),
                    passed=False,
                    message=warning.message,
                    field_refs=field_map.get(warning.code, []),
                )
            )
        return violations

    def _recommended_options(
        self,
        quote: QuoteRequest,
        validation: QuoteValidationResponse,
    ) -> list[RecommendedOption]:
        price_low, price_high = self._price_band(quote.alloy_name)
        base_lead = quote.required_lead_time_days or quote.lead_time_requested_days or 21
        lead_low = max(7, base_lead)
        lead_high = lead_low + 7

        rationale = "Deterministic option based on pricing bands and rule engine output."
        if validation.escalation_required:
            rationale = (
                "Engineering review required; option shown as baseline pending "
                "constraint clearance."
            )
        option = RecommendedOption(
            option_id="opt-primary",
            alloy_name=quote.alloy_name,
            product_form=quote.product_form,
            cert_required=quote.cert_required,
            estimated_price_per_kg_low=price_low,
            estimated_price_per_kg_high=price_high,
            estimated_lead_time_days_low=int(lead_low),
            estimated_lead_time_days_high=int(lead_high),
            rationale=rationale,
        )
        return [option]

    @staticmethod
    def _assumptions(quote: QuoteRequest, validation: QuoteValidationResponse) -> list[str]:
        assumptions: list[str] = []
        if quote.cert_required is None:
            assumptions.append("Certification defaults to standard mill cert unless specified.")
        if quote.temper is None:
            assumptions.append(
                "Temper assumed from typical catalog default for requested alloy/form."
            )
        if quote.finish is None:
            assumptions.append("Finish assumed to standard production finish.")
        if quote.required_lead_time_days is None:
            assumptions.append("Lead time estimated using alloy baseline due to missing request.")
        if validation.missing_fields:
            assumptions.append(
                "Incomplete input fields require final commercial review before release."
            )
        return assumptions

    def _llm_summary(self, draft: dict[str, Any]) -> str | None:
        if self.settings.llm_provider.lower() != "ollama":
            return None
        prompt = (
            "Summarize this quote draft in 3 concise bullet points for an internal sales handoff. "
            f"Draft JSON: {json.dumps(draft)}"
        )
        payload = {"model": self.settings.llm_model, "prompt": prompt, "stream": False}
        try:
            response = httpx.post(
                f"{self.settings.ollama_base_url}/api/generate",
                json=payload,
                timeout=20,
            )
            response.raise_for_status()
            return response.json().get("response", "").strip() or None
        except Exception:
            return None

    def draft(self, quote: QuoteRequest, db: Session | None = None) -> QuoteDraftResponse:
        validation = self.validate(quote)
        search_query = (
            f"{quote.alloy_name or ''} {quote.product_form or ''} {quote.cert_required or ''}"
        ).strip()
        citations = self.rag_service.search(search_query, top_k=5, db=db)
        similar = self.history_service.find_similar_quotes(
            alloy_name=quote.alloy_name,
            product_form=quote.product_form,
            qty_kg=quote.qty_kg,
            thickness_mm=quote.thickness_mm,
            width_mm=quote.width_mm,
            top_k=5,
        )
        rule_violations = self._rule_violations(validation)
        assumptions = self._assumptions(quote, validation)
        recommended_options = self._recommended_options(quote, validation)

        draft = {
            "request_id": quote.request_id,
            "customer_name": quote.customer_name,
            "alloy_name": quote.alloy_name,
            "product_form": quote.product_form,
            "dimensions": {"thickness_mm": quote.thickness_mm, "width_mm": quote.width_mm},
            "qty_kg": quote.qty_kg,
            "cert_required": quote.cert_required,
            "lead_time_days": quote.required_lead_time_days,
            "price_hint": self._price_hint(quote.alloy_name, quote.qty_kg),
            "recommended_options": [opt.model_dump() for opt in recommended_options],
            "rule_violations": [v.model_dump() for v in rule_violations],
            "assumptions": assumptions,
            "escalation_required": validation.escalation_required,
            "similar_quotes": similar,
            "confidence": validation.confidence,
        }

        llm_summary = self._llm_summary(draft)
        used_fallback = llm_summary is None
        draft["summary"] = (
            llm_summary
            if llm_summary is not None
            else "Deterministic draft generated; LLM summary unavailable, fallback used."
        )

        return QuoteDraftResponse(
            request_id=quote.request_id,
            draft=draft,
            recommended_options=recommended_options,
            missing_fields=validation.missing_fields,
            rule_violations=rule_violations,
            assumptions=assumptions,
            warnings=validation.warnings,
            similar_quotes=[SimilarQuoteItem(**row) for row in similar],
            citations=citations,
            confidence=validation.confidence,
            escalation_required=validation.escalation_required,
            used_fallback=used_fallback,
        )
