from pydantic import BaseModel

from app.schemas.quote import QuoteRequest, QuoteValidationResponse


class RulesValidationRequest(BaseModel):
    quote: QuoteRequest


class RulesValidationResponse(BaseModel):
    result: QuoteValidationResponse
