from functools import lru_cache

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.pipelines.ingest_internal_mock_docs import main as ingest_internal_pipeline
from app.pipelines.ingest_ulbrich_public_docs import main as ingest_public_pipeline
from app.schemas.retrieval import (
    RetrievalDocsResponse,
    RetrievalIngestResponse,
    RetrievalReindexResponse,
    RetrievalRequest,
    RetrievalResponse,
)
from app.services.rag_service import RAGService

router = APIRouter(prefix="/retrieval", tags=["retrieval"])


@lru_cache(maxsize=1)
def get_rag_service() -> RAGService:
    return RAGService()


@router.post("/search", response_model=RetrievalResponse)
def search_docs(
    request: RetrievalRequest,
    db: Session = Depends(get_db_session),
    service: RAGService = Depends(get_rag_service),
) -> RetrievalResponse:
    hits = service.search(request.query, request.top_k, db=db)
    return RetrievalResponse(query=request.query, hits=hits)


@router.post("/ingest/public", response_model=RetrievalIngestResponse)
def ingest_public_docs(
    db: Session = Depends(get_db_session),
    service: RAGService = Depends(get_rag_service),
) -> RetrievalIngestResponse:
    ingest_public_pipeline()
    out = service.ingest_source("public", db=db)
    return RetrievalIngestResponse(**out)


@router.post("/ingest/internal", response_model=RetrievalIngestResponse)
def ingest_internal_docs(
    db: Session = Depends(get_db_session),
    service: RAGService = Depends(get_rag_service),
) -> RetrievalIngestResponse:
    ingest_internal_pipeline()
    out = service.ingest_source("internal", db=db)
    return RetrievalIngestResponse(**out)


@router.post("/reindex", response_model=RetrievalReindexResponse)
def reindex_docs(
    db: Session = Depends(get_db_session),
    service: RAGService = Depends(get_rag_service),
) -> RetrievalReindexResponse:
    out = service.build_index(db=db)
    return RetrievalReindexResponse(**out)


@router.post("/index", response_model=RetrievalReindexResponse)
def build_index(
    db: Session = Depends(get_db_session),
    service: RAGService = Depends(get_rag_service),
) -> RetrievalReindexResponse:
    out = service.build_index(db=db)
    return RetrievalReindexResponse(**out)


@router.get("/docs", response_model=RetrievalDocsResponse)
def get_docs(
    db: Session = Depends(get_db_session),
    service: RAGService = Depends(get_rag_service),
) -> RetrievalDocsResponse:
    docs = service.list_indexed_docs(db=db)
    return RetrievalDocsResponse(count=len(docs), docs=docs)
