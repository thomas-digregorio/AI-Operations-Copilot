from fastapi import APIRouter

from app.schemas.ml import DriftSummaryRequest, DriftSummaryResponse
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
    out = monitoring_service.drift_summary(request.rows)
    return DriftSummaryResponse(**out)
