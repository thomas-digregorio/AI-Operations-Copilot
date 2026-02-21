from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.ml import (
    DriftSummaryRequest,
    DriftSummaryResponse,
    EvaluationReportResponse,
    PredictionMonitoringResponse,
)
from app.services.diagnostics_service import DiagnosticsService
from app.services.monitoring_service import MonitoringService

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])
diagnostics_service = DiagnosticsService()
monitoring_service = MonitoringService()


@router.get("/status")
def diagnostics_status() -> dict:
    return diagnostics_service.status()


@router.post("/drift-summary", response_model=DriftSummaryResponse)
def drift_summary(request: DriftSummaryRequest) -> DriftSummaryResponse:
    out = monitoring_service.drift_summary(request.rows, threshold=request.threshold)
    return DriftSummaryResponse(**out)


@router.get("/eval-report", response_model=EvaluationReportResponse)
def eval_report() -> EvaluationReportResponse:
    out = monitoring_service.evaluation_report()
    return EvaluationReportResponse(**out)


@router.get("/prediction-summary", response_model=PredictionMonitoringResponse)
def prediction_summary(
    window_days: int = 30,
    db: Session = Depends(get_db_session),
) -> PredictionMonitoringResponse:
    out = monitoring_service.prediction_monitoring_summary(db=db, window_days=window_days)
    return PredictionMonitoringResponse(**out)
