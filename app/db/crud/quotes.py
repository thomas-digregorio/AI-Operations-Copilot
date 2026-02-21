import json

from sqlalchemy.orm import Session

from app.db.models import QuoteAudit


def create_quote_audit(db: Session, request_id: str, action: str, payload: dict) -> QuoteAudit:
    row = QuoteAudit(request_id=request_id, action=action, payload=json.dumps(payload, default=str))
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
