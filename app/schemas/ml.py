from typing import Any

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


class DriftSummaryResponse(BaseModel):
    feature_shift_summary: dict[str, float]
    drift_flags: list[str]
