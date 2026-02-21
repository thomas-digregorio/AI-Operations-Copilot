from fastapi import APIRouter

from app.schemas.rules import RulesValidationRequest, RulesValidationResponse
from app.services.rule_engine_service import RuleEngineService

router = APIRouter(prefix="/rules", tags=["rules"])
service = RuleEngineService()


@router.post("/validate", response_model=RulesValidationResponse)
def validate_rules(request: RulesValidationRequest) -> RulesValidationResponse:
    return RulesValidationResponse(result=service.validate_quote(request.quote))
