from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import Citation


class RetrievalRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=10)


class RetrievalResponse(BaseModel):
    query: str
    hits: list[Citation] = Field(default_factory=list)


class RetrievalIngestResponse(BaseModel):
    status: str
    source_type: str
    files_discovered: int
    chunks_indexed: int
    message: str = ""


class RetrievalReindexResponse(BaseModel):
    status: str
    chunks_indexed: int = 0
    index_path: str | None = None
    message: str = ""


class IndexedDocumentItem(BaseModel):
    doc_id: int | None = None
    source_type: str
    title: str
    path_or_url: str
    checksum: str | None = None
    chunk_count: int = 0


class RetrievalDocsResponse(BaseModel):
    count: int
    docs: list[IndexedDocumentItem] = Field(default_factory=list)
