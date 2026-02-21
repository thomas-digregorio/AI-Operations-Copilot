from sqlalchemy.orm import Session

from app.db.models import PredictionAudit, TrainingRun


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
    db: Session, model_name: str, macro_f1: float, status: str = "completed"
) -> TrainingRun:
    row = TrainingRun(model_name=model_name, macro_f1=macro_f1, status=status)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
