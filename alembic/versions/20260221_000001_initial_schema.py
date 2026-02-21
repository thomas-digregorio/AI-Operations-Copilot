"""Initial application schema

Revision ID: 20260221_000001
Revises:
Create Date: 2026-02-21 16:20:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260221_000001"
down_revision = None
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return inspector.has_table(table_name)


def _create_index_if_missing(index_name: str, table_name: str, columns: list[str]) -> None:
    inspector = sa.inspect(op.get_bind())
    if not inspector.has_table(table_name):
        return
    existing = {idx["name"] for idx in inspector.get_indexes(table_name)}
    if index_name not in existing:
        op.create_index(index_name, table_name, columns, unique=False)


def upgrade() -> None:
    if not _has_table("quote_audits"):
        op.create_table(
            "quote_audits",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("request_id", sa.String(length=64), nullable=False),
            sa.Column("action", sa.String(length=64), nullable=False),
            sa.Column("payload", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
    _create_index_if_missing("ix_quote_audits_request_id", "quote_audits", ["request_id"])

    if not _has_table("retrieval_audits"):
        op.create_table(
            "retrieval_audits",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("query", sa.Text(), nullable=False),
            sa.Column("source", sa.String(length=512), nullable=False),
            sa.Column("score", sa.Float(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _has_table("prediction_audits"):
        op.create_table(
            "prediction_audits",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("predicted_class", sa.String(length=64), nullable=False),
            sa.Column("confidence", sa.Float(), nullable=False),
            sa.Column("has_explanation", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _has_table("training_runs"):
        op.create_table(
            "training_runs",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("model_name", sa.String(length=128), nullable=False),
            sa.Column("status", sa.String(length=32), nullable=False),
            sa.Column("macro_f1", sa.Float(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _has_table("documents"):
        op.create_table(
            "documents",
            sa.Column("doc_id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("source_type", sa.String(length=32), nullable=False),
            sa.Column("title", sa.String(length=256), nullable=False),
            sa.Column("path_or_url", sa.String(length=1024), nullable=False),
            sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("checksum", sa.String(length=128), nullable=False),
            sa.Column("metadata_json", sa.Text(), nullable=False),
            sa.PrimaryKeyConstraint("doc_id"),
            sa.UniqueConstraint("path_or_url"),
        )
    _create_index_if_missing("ix_documents_checksum", "documents", ["checksum"])
    _create_index_if_missing("ix_documents_source_type", "documents", ["source_type"])

    if not _has_table("document_chunks"):
        op.create_table(
            "document_chunks",
            sa.Column("chunk_id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("doc_id", sa.Integer(), nullable=False),
            sa.Column("chunk_index", sa.Integer(), nullable=False),
            sa.Column("text", sa.Text(), nullable=False),
            sa.Column("embedding_ref", sa.String(length=256), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=False),
            sa.ForeignKeyConstraint(["doc_id"], ["documents.doc_id"]),
            sa.PrimaryKeyConstraint("chunk_id"),
        )
    _create_index_if_missing("ix_document_chunks_doc_id", "document_chunks", ["doc_id"])

    if not _has_table("quote_requests"):
        op.create_table(
            "quote_requests",
            sa.Column("request_id", sa.String(length=64), nullable=False),
            sa.Column("request_json", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.PrimaryKeyConstraint("request_id"),
        )

    if not _has_table("quote_drafts"):
        op.create_table(
            "quote_drafts",
            sa.Column("draft_id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("request_id", sa.String(length=64), nullable=False),
            sa.Column("response_json", sa.Text(), nullable=False),
            sa.Column("rule_results_json", sa.Text(), nullable=False),
            sa.Column("citations_json", sa.Text(), nullable=False),
            sa.Column("llm_model", sa.String(length=128), nullable=False),
            sa.Column("prompt_version", sa.String(length=64), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["request_id"], ["quote_requests.request_id"]),
            sa.PrimaryKeyConstraint("draft_id"),
        )
    _create_index_if_missing("ix_quote_drafts_request_id", "quote_drafts", ["request_id"])

    if not _has_table("quote_history"):
        op.create_table(
            "quote_history",
            sa.Column("quote_id", sa.String(length=64), nullable=False),
            sa.Column("quote_date", sa.String(length=32), nullable=False),
            sa.Column("customer_name", sa.String(length=256), nullable=True),
            sa.Column("alloy_name", sa.String(length=64), nullable=True),
            sa.Column("product_form", sa.String(length=64), nullable=True),
            sa.Column("thickness_mm", sa.Float(), nullable=True),
            sa.Column("width_mm", sa.Float(), nullable=True),
            sa.Column("qty_kg", sa.Float(), nullable=True),
            sa.Column("lead_time_days", sa.Integer(), nullable=True),
            sa.Column("cert_required", sa.String(length=128), nullable=True),
            sa.Column("price_total_usd", sa.Float(), nullable=True),
            sa.Column("status", sa.String(length=32), nullable=True),
            sa.PrimaryKeyConstraint("quote_id"),
        )
    _create_index_if_missing("ix_quote_history_alloy_name", "quote_history", ["alloy_name"])
    _create_index_if_missing("ix_quote_history_product_form", "quote_history", ["product_form"])
    _create_index_if_missing("ix_quote_history_quote_date", "quote_history", ["quote_date"])

    if not _has_table("ml_prediction_logs"):
        op.create_table(
            "ml_prediction_logs",
            sa.Column("prediction_id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("model_name", sa.String(length=128), nullable=False),
            sa.Column("model_version", sa.String(length=64), nullable=False),
            sa.Column("input_json", sa.Text(), nullable=False),
            sa.Column("output_json", sa.Text(), nullable=False),
            sa.Column("predicted_class", sa.String(length=64), nullable=False),
            sa.Column("confidence", sa.Float(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.PrimaryKeyConstraint("prediction_id"),
        )
    _create_index_if_missing("ix_ml_prediction_logs_created_at", "ml_prediction_logs", ["created_at"])
    _create_index_if_missing("ix_ml_prediction_logs_model_name", "ml_prediction_logs", ["model_name"])
    _create_index_if_missing(
        "ix_ml_prediction_logs_predicted_class",
        "ml_prediction_logs",
        ["predicted_class"],
    )

    if not _has_table("ml_training_runs"):
        op.create_table(
            "ml_training_runs",
            sa.Column("run_id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("model_name", sa.String(length=128), nullable=False),
            sa.Column("params_json", sa.Text(), nullable=False),
            sa.Column("metrics_json", sa.Text(), nullable=False),
            sa.Column("artifact_path", sa.String(length=512), nullable=False),
            sa.Column("status", sa.String(length=32), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.PrimaryKeyConstraint("run_id"),
        )
    _create_index_if_missing("ix_ml_training_runs_model_name", "ml_training_runs", ["model_name"])


def downgrade() -> None:
    op.drop_index("ix_ml_training_runs_model_name", table_name="ml_training_runs")
    op.drop_table("ml_training_runs")

    op.drop_index("ix_ml_prediction_logs_predicted_class", table_name="ml_prediction_logs")
    op.drop_index("ix_ml_prediction_logs_model_name", table_name="ml_prediction_logs")
    op.drop_index("ix_ml_prediction_logs_created_at", table_name="ml_prediction_logs")
    op.drop_table("ml_prediction_logs")

    op.drop_index("ix_quote_history_quote_date", table_name="quote_history")
    op.drop_index("ix_quote_history_product_form", table_name="quote_history")
    op.drop_index("ix_quote_history_alloy_name", table_name="quote_history")
    op.drop_table("quote_history")

    op.drop_index("ix_quote_drafts_request_id", table_name="quote_drafts")
    op.drop_table("quote_drafts")
    op.drop_table("quote_requests")

    op.drop_index("ix_document_chunks_doc_id", table_name="document_chunks")
    op.drop_table("document_chunks")
    op.drop_index("ix_documents_source_type", table_name="documents")
    op.drop_index("ix_documents_checksum", table_name="documents")
    op.drop_table("documents")

    op.drop_table("training_runs")
    op.drop_table("prediction_audits")
    op.drop_table("retrieval_audits")
    op.drop_index("ix_quote_audits_request_id", table_name="quote_audits")
    op.drop_table("quote_audits")
