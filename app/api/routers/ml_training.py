from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.crud.predictions import create_training_run
from app.db.session import get_db_session
from app.schemas.ml import TrainSteelFaultModelRequest, TrainSteelFaultModelResponse
from app.services.steel_model_service import SteelModelService

router = APIRouter(prefix="/ml", tags=["ml-training"])
service = SteelModelService()


@router.post("/train/steel-faults", response_model=TrainSteelFaultModelResponse)
def train_steel_fault_model(
    request: TrainSteelFaultModelRequest,
    db: Session = Depends(get_db_session),
) -> TrainSteelFaultModelResponse:
    result = service.train(dataset_path=request.dataset_path)
    macro_f1 = float(result["metrics"].get("macro_f1", 0.0))
    create_training_run(db, model_name="steel_fault_xgb", macro_f1=macro_f1, status="completed")
    return TrainSteelFaultModelResponse(
        status="completed",
        model_path=result["model_path"],
        metrics_path=result["metrics_path"],
        metrics=result["metrics"],
    )
