from fastapi import APIRouter

from app.schemas.ml import DriftSummaryRequest, DriftSummaryResponse, EvaluationReportResponse
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
