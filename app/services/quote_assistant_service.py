from __future__ import annotations

import json

import httpx
import pandas as pd

from app.core.config import get_settings
from app.core.constants import PRICING_RULES_PATH
from app.schemas.quote import (
    QuoteAnswerResponse,
    QuoteDraftResponse,
    QuoteRequest,
    QuoteValidationResponse,
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

    def answer(self, query: str, top_k: int = 5) -> QuoteAnswerResponse:
        citations = self.rag_service.search(query, top_k=top_k)
        if not citations:
            return QuoteAnswerResponse(
                answer="No indexed citations available yet. Ingest and index local docs first.",
                citations=[],
            )
        answer = (
            "Retrieved relevant guidance from local corpus. "
            "Use citations for traceable quote support."
        )
        return QuoteAnswerResponse(answer=answer, citations=citations)

    def _price_hint(self, alloy_name: str | None, qty_kg: float | None) -> str:
        if not PRICING_RULES_PATH.exists():
            return "Pricing rules not seeded yet."
        df = pd.read_csv(PRICING_RULES_PATH)
        rows = df[df["rule_type"].str.lower().eq("price_band")]
        if alloy_name:
            rows = rows[rows["alloy_name"].str.lower().eq(alloy_name.lower())]
        if rows.empty:
            return "No matching price band found."
        row = rows.iloc[0]
        low = float(row.get("price_per_kg_low", 0.0))
        high = float(row.get("price_per_kg_high", 0.0))
        if qty_kg:
            return (
                f"Estimated unit range ${low:.2f}-${high:.2f}/kg; "
                f"order estimate ${low * qty_kg:.2f}-${high * qty_kg:.2f}."
            )
        return f"Estimated unit range ${low:.2f}-${high:.2f}/kg."

    def _llm_summary(self, draft: dict) -> str | None:
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

    def draft(self, quote: QuoteRequest) -> QuoteDraftResponse:
        validation = self.validate(quote)
        search_query = (
            f"{quote.alloy_name or ''} "
            f"{quote.product_form or ''} "
            f"{quote.cert_required or ''}"
        ).strip()
        citations = self.rag_service.search(
            search_query,
            top_k=5,
        )
        similar = self.history_service.find_similar_quotes(
            alloy_name=quote.alloy_name,
            product_form=quote.product_form,
            qty_kg=quote.qty_kg,
            top_k=3,
        )

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
            missing_fields=validation.missing_fields,
            warnings=validation.warnings,
            citations=citations,
            escalation_required=validation.escalation_required,
            used_fallback=used_fallback,
        )
