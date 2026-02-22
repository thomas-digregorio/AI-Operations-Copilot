from functools import lru_cache

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.crud.predictions import create_ml_prediction_log, create_prediction_audit
from app.db.session import get_db_session
from app.schemas.ml import (
    SteelFaultBatchPredictionRequest,
    SteelFaultBatchPredictionResponse,
    SteelFaultPredictionRequest,
    SteelFaultPredictionResult,
    SteelGlobalExplainResponse,
    SteelLocalExplainRequest,
    SteelLocalExplainResponse,
)
from app.services.explainability_service import ExplainabilityService
from app.services.steel_model_service import SteelModelService

router = APIRouter(prefix="/ml", tags=["ml-inference"])


@lru_cache(maxsize=1)
def get_model_service() -> SteelModelService:
    return SteelModelService()


@lru_cache(maxsize=1)
def get_explainability_service() -> ExplainabilityService:
    return ExplainabilityService()


@router.post("/predict/steel-faults", response_model=SteelFaultPredictionResult)
def predict_steel_fault(
    request: SteelFaultPredictionRequest,
    db: Session = Depends(get_db_session),
    model_service: SteelModelService = Depends(get_model_service),
) -> SteelFaultPredictionResult:
    out = model_service.predict_single(request.features)
    create_prediction_audit(
        db,
        predicted_class=out["predicted_class"],
        confidence=out["confidence"],
        has_explanation=False,
    )
    create_ml_prediction_log(
        db,
        model_name="steel_fault_xgb",
        model_version="v1",
        input_payload=request.features,
        output_payload=out,
        predicted_class=out["predicted_class"],
        confidence=out["confidence"],
    )
    return SteelFaultPredictionResult(**out)


@router.post("/predict/steel-faults/batch", response_model=SteelFaultBatchPredictionResponse)
def predict_steel_fault_batch(
    request: SteelFaultBatchPredictionRequest,
    db: Session = Depends(get_db_session),
    model_service: SteelModelService = Depends(get_model_service),
) -> SteelFaultBatchPredictionResponse:
    out = model_service.predict_batch(request.rows)
    for row_in, row_out in zip(request.rows, out, strict=False):
        create_ml_prediction_log(
            db,
            model_name="steel_fault_xgb",
            model_version="v1",
            input_payload=row_in,
            output_payload=row_out,
            predicted_class=row_out["predicted_class"],
            confidence=float(row_out["confidence"]),
        )
    return SteelFaultBatchPredictionResponse(
        predictions=[SteelFaultPredictionResult(**row) for row in out]
    )


@router.post("/explain/local", response_model=SteelLocalExplainResponse)
def explain_local(
    request: SteelLocalExplainRequest,
    db: Session = Depends(get_db_session),
    explain_service: ExplainabilityService = Depends(get_explainability_service),
) -> SteelLocalExplainResponse:
    out = explain_service.explain_local(request.features)
    create_prediction_audit(
        db,
        predicted_class=out["predicted_class"],
        confidence=1.0,
        has_explanation=True,
    )
    return SteelLocalExplainResponse(**out)


@router.get("/explain/global", response_model=SteelGlobalExplainResponse)
def explain_global(top_k: int = Query(default=20, ge=1, le=100)) -> SteelGlobalExplainResponse:
    explain_service = get_explainability_service()
    out = explain_service.explain_global(top_k=top_k)
    return SteelGlobalExplainResponse(**out)
