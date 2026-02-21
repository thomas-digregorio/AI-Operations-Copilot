from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import QuoteAudit, QuoteDraftRecord, QuoteRequestRecord


def create_quote_audit(db: Session, request_id: str, action: str, payload: dict) -> QuoteAudit:
    row = QuoteAudit(request_id=request_id, action=action, payload=json.dumps(payload, default=str))
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def upsert_quote_request(
    db: Session,
    request_id: str,
    request_payload: dict[str, Any],
) -> QuoteRequestRecord:
    row = db.get(QuoteRequestRecord, request_id)
    payload_str = json.dumps(request_payload, default=str)
    if row is None:
        row = QuoteRequestRecord(request_id=request_id, request_json=payload_str)
        db.add(row)
    else:
        row.request_json = payload_str
    db.commit()
    db.refresh(row)
    return row


def create_quote_draft_record(
    db: Session,
    request_id: str,
    response_payload: dict[str, Any],
    rule_results: dict[str, Any],
    citations: list[dict[str, Any]],
    llm_model: str,
    prompt_version: str = "v1",
) -> QuoteDraftRecord:
    row = QuoteDraftRecord(
        request_id=request_id,
        response_json=json.dumps(response_payload, default=str),
        rule_results_json=json.dumps(rule_results, default=str),
        citations_json=json.dumps(citations, default=str),
        llm_model=llm_model,
        prompt_version=prompt_version,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
