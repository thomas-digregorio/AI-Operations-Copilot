from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# Backward-compatible audit tables
class QuoteAudit(Base):
    __tablename__ = "quote_audits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(64), index=True)
    action: Mapped[str] = mapped_column(String(64))
    payload: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class RetrievalAudit(Base):
    __tablename__ = "retrieval_audits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    query: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(512))
    score: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class PredictionAudit(Base):
    __tablename__ = "prediction_audits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    predicted_class: Mapped[str] = mapped_column(String(64))
    confidence: Mapped[float] = mapped_column(Float)
    has_explanation: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class TrainingRun(Base):
    __tablename__ = "training_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_name: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32), default="completed")
    macro_f1: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


# Design-spec parity tables
class Document(Base):
    __tablename__ = "documents"

    doc_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_type: Mapped[str] = mapped_column(String(32), index=True)
    title: Mapped[str] = mapped_column(String(256))
    path_or_url: Mapped[str] = mapped_column(String(1024), unique=True)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    checksum: Mapped[str] = mapped_column(String(128), index=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    chunk_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doc_id: Mapped[int] = mapped_column(ForeignKey("documents.doc_id"), index=True)
    chunk_index: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    embedding_ref: Mapped[str | None] = mapped_column(String(256), nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")


class QuoteRequestRecord(Base):
    __tablename__ = "quote_requests"

    request_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    request_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class QuoteDraftRecord(Base):
    __tablename__ = "quote_drafts"

    draft_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(
        ForeignKey("quote_requests.request_id"),
        index=True,
    )
    response_json: Mapped[str] = mapped_column(Text)
    rule_results_json: Mapped[str] = mapped_column(Text, default="{}")
    citations_json: Mapped[str] = mapped_column(Text, default="[]")
    llm_model: Mapped[str] = mapped_column(String(128), default="deterministic-fallback")
    prompt_version: Mapped[str] = mapped_column(String(64), default="v1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class QuoteHistoryRecord(Base):
    __tablename__ = "quote_history"

    quote_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    quote_date: Mapped[str] = mapped_column(String(32), index=True)
    customer_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    alloy_name: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    product_form: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    thickness_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    width_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    qty_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    lead_time_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cert_required: Mapped[str | None] = mapped_column(String(128), nullable=True)
    price_total_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str | None] = mapped_column(String(32), nullable=True)


class MLPredictionLog(Base):
    __tablename__ = "ml_prediction_logs"

    prediction_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_name: Mapped[str] = mapped_column(String(128), index=True)
    model_version: Mapped[str] = mapped_column(String(64), default="v1")
    input_json: Mapped[str] = mapped_column(Text)
    output_json: Mapped[str] = mapped_column(Text)
    predicted_class: Mapped[str] = mapped_column(String(64), index=True)
    confidence: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        index=True,
    )


class MLTrainingRun(Base):
    __tablename__ = "ml_training_runs"

    run_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_name: Mapped[str] = mapped_column(String(128), index=True)
    params_json: Mapped[str] = mapped_column(Text, default="{}")
    metrics_json: Mapped[str] = mapped_column(Text, default="{}")
    artifact_path: Mapped[str] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(32), default="completed")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
