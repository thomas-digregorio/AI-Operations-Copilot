from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.crud.predictions import create_prediction_audit
from app.db.session import get_db_session
from app.schemas.ml import (
    SteelFaultBatchPredictionRequest,
    SteelFaultBatchPredictionResponse,
    SteelFaultPredictionRequest,
    SteelFaultPredictionResult,
    SteelLocalExplainRequest,
    SteelLocalExplainResponse,
)
from app.services.explainability_service import ExplainabilityService
from app.services.steel_model_service import SteelModelService

router = APIRouter(prefix="/ml", tags=["ml-inference"])
model_service = SteelModelService()
explain_service = ExplainabilityService()


@router.post("/predict/steel-faults", response_model=SteelFaultPredictionResult)
def predict_steel_fault(
    request: SteelFaultPredictionRequest,
    db: Session = Depends(get_db_session),
) -> SteelFaultPredictionResult:
    out = model_service.predict_single(request.features)
    create_prediction_audit(
        db,
        predicted_class=out["predicted_class"],
        confidence=out["confidence"],
        has_explanation=False,
    )
    return SteelFaultPredictionResult(**out)


@router.post("/predict/steel-faults/batch", response_model=SteelFaultBatchPredictionResponse)
def predict_steel_fault_batch(
    request: SteelFaultBatchPredictionRequest,
) -> SteelFaultBatchPredictionResponse:
    out = model_service.predict_batch(request.rows)
    return SteelFaultBatchPredictionResponse(
        predictions=[SteelFaultPredictionResult(**row) for row in out]
    )


@router.post("/explain/local", response_model=SteelLocalExplainResponse)
def explain_local(request: SteelLocalExplainRequest) -> SteelLocalExplainResponse:
    out = explain_service.explain_local(request.features)
    return SteelLocalExplainResponse(**out)
