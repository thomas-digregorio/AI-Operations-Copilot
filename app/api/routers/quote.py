from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.crud.quotes import (
    create_quote_audit,
    create_quote_draft_record,
    upsert_quote_request,
)
from app.db.session import get_db_session
from app.schemas.quote import (
    QuoteAnswerRequest,
    QuoteAnswerResponse,
    QuoteDraftResponse,
    QuoteRequest,
    QuoteValidationResponse,
    SimilarQuoteQueryResponse,
)
from app.services.quote_assistant_service import QuoteAssistantService

router = APIRouter(prefix="/quote", tags=["quote"])
service = QuoteAssistantService()


@router.post("/validate", response_model=QuoteValidationResponse)
def validate_quote(
    quote: QuoteRequest,
    db: Session = Depends(get_db_session),
) -> QuoteValidationResponse:
    upsert_quote_request(db, quote.request_id, quote.model_dump())
    result = service.validate(quote)
    create_quote_audit(db, quote.request_id, "validate", result.model_dump())
    return result


@router.post("/draft", response_model=QuoteDraftResponse)
def draft_quote(
    quote: QuoteRequest,
    db: Session = Depends(get_db_session),
) -> QuoteDraftResponse:
    upsert_quote_request(db, quote.request_id, quote.model_dump())
    result = service.draft(quote, db=db)
    create_quote_draft_record(
        db=db,
        request_id=quote.request_id,
        response_payload=result.model_dump(),
        rule_results={
            "missing_fields": result.missing_fields,
            "rule_violations": [row.model_dump() for row in result.rule_violations],
            "warnings": [w.model_dump() for w in result.warnings],
            "escalation_required": result.escalation_required,
        },
        citations=[c.model_dump() for c in result.citations],
        llm_model=(
            service.settings.llm_model if not result.used_fallback else "deterministic-fallback"
        ),
    )
    create_quote_audit(db, quote.request_id, "draft", result.model_dump())
    return result


@router.post("/answer", response_model=QuoteAnswerResponse)
def answer_quote(
    request: QuoteAnswerRequest,
    db: Session = Depends(get_db_session),
) -> QuoteAnswerResponse:
    return service.answer(request.question or request.query or "", request.top_k, db=db)


@router.get("/history/similar", response_model=SimilarQuoteQueryResponse)
def similar_quote_history(
    alloy_name: str | None = Query(default=None),
    product_form: str | None = Query(default=None),
    qty_kg: float | None = Query(default=None),
    thickness_mm: float | None = Query(default=None),
    width_mm: float | None = Query(default=None),
    top_k: int = Query(default=5, ge=1, le=20),
) -> SimilarQuoteQueryResponse:
    probe = QuoteRequest(
        request_id="history-similar-query",
        alloy_name=alloy_name,
        product_form=product_form,
        qty_kg=qty_kg,
        thickness_mm=thickness_mm,
        width_mm=width_mm,
    )
    return service.similar_quotes(probe, top_k=top_k)
