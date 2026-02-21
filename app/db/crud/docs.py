from sqlalchemy.orm import Session

from app.db.models import RetrievalAudit


def create_retrieval_audit(db: Session, query: str, source: str, score: float) -> RetrievalAudit:
    row = RetrievalAudit(query=query, source=source, score=score)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
