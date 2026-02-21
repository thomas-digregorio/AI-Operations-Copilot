from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import MLPredictionLog, MLTrainingRun, PredictionAudit, TrainingRun


def create_prediction_audit(
    db: Session, predicted_class: str, confidence: float, has_explanation: bool
) -> PredictionAudit:
    row = PredictionAudit(
        predicted_class=predicted_class,
        confidence=confidence,
        has_explanation=has_explanation,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def create_training_run(
    db: Session,
    model_name: str,
    macro_f1: float,
    status: str = "completed",
) -> TrainingRun:
    row = TrainingRun(model_name=model_name, macro_f1=macro_f1, status=status)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def create_ml_prediction_log(
    db: Session,
    model_name: str,
    model_version: str,
    input_payload: dict[str, Any],
    output_payload: dict[str, Any],
    predicted_class: str,
    confidence: float,
) -> MLPredictionLog:
    row = MLPredictionLog(
        model_name=model_name,
        model_version=model_version,
        input_json=json.dumps(input_payload, default=str),
        output_json=json.dumps(output_payload, default=str),
        predicted_class=predicted_class,
        confidence=confidence,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def create_ml_training_run(
    db: Session,
    model_name: str,
    params_payload: dict[str, Any],
    metrics_payload: dict[str, Any],
    artifact_path: str,
    status: str = "completed",
) -> MLTrainingRun:
    row = MLTrainingRun(
        model_name=model_name,
        params_json=json.dumps(params_payload, default=str),
        metrics_json=json.dumps(metrics_payload, default=str),
        artifact_path=artifact_path,
        status=status,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
