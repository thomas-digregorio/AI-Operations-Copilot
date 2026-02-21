from __future__ import annotations

import hashlib
import json

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import Document, DocumentChunk, RetrievalAudit
from app.utils.text_chunking import chunk_text


def create_retrieval_audit(db: Session, query: str, source: str, score: float) -> RetrievalAudit:
    row = RetrievalAudit(query=query, source=source, score=score)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def replace_documents_for_source(
    db: Session,
    source_type: str,
    docs: list[dict],
    embedding_ref: str = "faiss",
) -> dict:
    existing_doc_ids = [
        doc_id
        for (doc_id,) in db.query(Document.doc_id).filter(Document.source_type == source_type).all()
    ]
    if existing_doc_ids:
        db.query(DocumentChunk).filter(DocumentChunk.doc_id.in_(existing_doc_ids)).delete(
            synchronize_session=False
        )
    db.query(Document).filter(Document.source_type == source_type).delete(synchronize_session=False)
    db.flush()

    files_discovered = 0
    chunks_indexed = 0
    for doc in docs:
        text = str(doc.get("text", "")).strip()
        source = str(doc.get("source", "unknown"))
        if not text:
            continue

        files_discovered += 1
        checksum = hashlib.sha256(text.encode("utf-8")).hexdigest()
        entry = Document(
            source_type=source_type,
            title=source.rsplit("/", 1)[-1],
            path_or_url=source,
            checksum=checksum,
            metadata_json=json.dumps({"source_type": source_type}),
        )
        db.add(entry)
        db.flush()

        chunks = chunk_text(text)
        for idx, chunk in enumerate(chunks):
            db.add(
                DocumentChunk(
                    doc_id=entry.doc_id,
                    chunk_index=idx,
                    text=chunk,
                    embedding_ref=f"{embedding_ref}:{entry.doc_id}:{idx}",
                    metadata_json=json.dumps({"source": source}),
                )
            )
        chunks_indexed += len(chunks)

    db.commit()
    return {"files_discovered": files_discovered, "chunks_indexed": chunks_indexed}


def list_documents(db: Session) -> list[dict]:
    rows = (
        db.query(
            Document.doc_id,
            Document.source_type,
            Document.title,
            Document.path_or_url,
            Document.checksum,
            func.count(DocumentChunk.chunk_id).label("chunk_count"),
        )
        .outerjoin(DocumentChunk, Document.doc_id == DocumentChunk.doc_id)
        .group_by(
            Document.doc_id,
            Document.source_type,
            Document.title,
            Document.path_or_url,
            Document.checksum,
        )
        .order_by(Document.source_type, Document.title)
        .all()
    )
    return [
        {
            "doc_id": row.doc_id,
            "source_type": row.source_type,
            "title": row.title,
            "path_or_url": row.path_or_url,
            "checksum": row.checksum,
            "chunk_count": int(row.chunk_count or 0),
        }
        for row in rows
    ]
