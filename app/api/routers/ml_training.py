from functools import lru_cache

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import require_admin_token
from app.db.crud.predictions import create_ml_training_run, create_training_run
from app.db.session import get_db_session
from app.schemas.ml import TrainSteelFaultModelRequest, TrainSteelFaultModelResponse
from app.services.steel_model_service import SteelModelService

router = APIRouter(prefix="/ml", tags=["ml-training"])


@lru_cache(maxsize=1)
def get_model_service() -> SteelModelService:
    return SteelModelService()


@router.post("/train/steel-faults", response_model=TrainSteelFaultModelResponse)
def train_steel_fault_model(
    request: TrainSteelFaultModelRequest,
    db: Session = Depends(get_db_session),
    service: SteelModelService = Depends(get_model_service),
    _admin: None = Depends(require_admin_token),
) -> TrainSteelFaultModelResponse:
    selected_model = request.model_type.lower()
    if selected_model not in {"xgboost", "xgb", "xgbclassifier"}:
        selected_model = "xgboost"

    result = service.train(dataset_path=request.dataset_path, random_seed=request.random_seed)
    macro_f1 = float(result["metrics"].get("macro_f1", 0.0))
    create_training_run(db, model_name="steel_fault_xgb", macro_f1=macro_f1, status="completed")
    create_ml_training_run(
        db=db,
        model_name="steel_fault_xgb",
        params_payload={
            "dataset_path": request.dataset_path,
            "model_type_requested": request.model_type,
            "model_type_used": selected_model,
            "use_business_enriched_features": request.use_business_enriched_features,
            "random_seed": request.random_seed,
        },
        metrics_payload=result["metrics"],
        artifact_path=result["model_path"],
        status="completed",
    )
    return TrainSteelFaultModelResponse(
        status="completed",
        model_type=selected_model,
        model_path=result["model_path"],
        metrics_path=result["metrics_path"],
        metrics=result["metrics"],
    )
