from typing import Any, Literal

from pydantic import BaseModel, Field


class TrainSteelFaultModelRequest(BaseModel):
    dataset_path: str | None = None


class TrainSteelFaultModelResponse(BaseModel):
    status: str
    model_path: str
    metrics_path: str
    metrics: dict[str, Any]


class SteelFaultPredictionRequest(BaseModel):
    features: dict[str, float]


class SteelFaultBatchPredictionRequest(BaseModel):
    rows: list[dict[str, float]]


class SteelFaultPredictionResult(BaseModel):
    predicted_class: str
    confidence: float
    probabilities: dict[str, float] = Field(default_factory=dict)


class SteelFaultBatchPredictionResponse(BaseModel):
    predictions: list[SteelFaultPredictionResult] = Field(default_factory=list)


class SteelLocalExplainRequest(BaseModel):
    features: dict[str, float]


class SteelLocalExplainResponse(BaseModel):
    predicted_class: str
    base_value: float
    feature_contributions: dict[str, float]


class DriftSummaryRequest(BaseModel):
    rows: list[dict[str, float]]
    threshold: float = Field(default=1.0, ge=0.3, le=3.0)


class DriftSummaryResponse(BaseModel):
    feature_shift_summary: dict[str, float] = Field(default_factory=dict)
    drift_flags: list[str] = Field(default_factory=list)
    missing_features: list[str] = Field(default_factory=list)
    unknown_features: list[str] = Field(default_factory=list)
    rows_evaluated: int = 0
    threshold: float = 1.0
    mean_shift: float = 0.0
    max_shift: float = 0.0
    severity: Literal["low", "medium", "high", "critical"] = "low"


class EvaluationReportResponse(BaseModel):
    model_artifact_exists: bool
    metrics_artifact_exists: bool
    macro_f1: float | None = None
    accuracy: float | None = None
    label_count: int = 0
    confusion_matrix_present: bool = False
    performance_status: Literal["pass", "warn", "fail", "missing"]
    performance_notes: list[str] = Field(default_factory=list)
    metrics_path: str
    eval_summary_path: str
