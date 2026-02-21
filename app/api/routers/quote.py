from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.crud.quotes import create_quote_audit
from app.db.session import get_db_session
from app.schemas.quote import (
    QuoteAnswerRequest,
    QuoteAnswerResponse,
    QuoteDraftResponse,
    QuoteRequest,
    QuoteValidationResponse,
)
from app.services.quote_assistant_service import QuoteAssistantService

router = APIRouter(prefix="/quote", tags=["quote"])
service = QuoteAssistantService()


@router.post("/validate", response_model=QuoteValidationResponse)
def validate_quote(
    quote: QuoteRequest, db: Session = Depends(get_db_session)
) -> QuoteValidationResponse:
    result = service.validate(quote)
    create_quote_audit(db, quote.request_id, "validate", result.model_dump())
    return result


@router.post("/draft", response_model=QuoteDraftResponse)
def draft_quote(quote: QuoteRequest, db: Session = Depends(get_db_session)) -> QuoteDraftResponse:
    result = service.draft(quote)
    create_quote_audit(db, quote.request_id, "draft", result.model_dump())
    return result


@router.post("/answer", response_model=QuoteAnswerResponse)
def answer_quote(request: QuoteAnswerRequest) -> QuoteAnswerResponse:
    return service.answer(request.query, request.top_k)
