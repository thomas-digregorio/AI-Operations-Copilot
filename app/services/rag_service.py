from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.constants import INTERNAL_MOCK_DOCS_DIR, ULBRICH_PUBLIC_DIR
from app.db.crud.docs import create_retrieval_audit, list_documents, replace_documents_for_source
from app.schemas.common import Citation
from app.utils.citation_utils import build_citation
from app.utils.file_loaders import collect_documents
from app.utils.text_chunking import chunk_text


class RAGService:
    def __init__(self):
        self.settings = get_settings()

    def _embedding_model(self) -> Any:
        from langchain_huggingface import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(model_name=self.settings.embedding_model)

    def _index_path(self) -> Path:
        return Path(self.settings.vector_dir)

    @staticmethod
    def _source_dir(source_type: str) -> Path:
        source = source_type.lower()
        if source == "public":
            return ULBRICH_PUBLIC_DIR
        if source == "internal":
            return INTERNAL_MOCK_DOCS_DIR
        raise ValueError("source_type must be 'public' or 'internal'.")

    def ingest_source(self, source_type: str, db: Session | None = None) -> dict:
        docs = collect_documents(self._source_dir(source_type))
        chunks_indexed = sum(len(chunk_text(d.get("text", ""))) for d in docs)
        if db is not None:
            replace_documents_for_source(db, source_type=source_type, docs=docs)
        return {
            "status": "ok" if docs else "empty",
            "source_type": source_type,
            "files_discovered": len(docs),
            "chunks_indexed": chunks_indexed,
            "message": "" if docs else "No files found for source.",
        }

    def build_index(self, db: Session | None = None) -> dict:
        from langchain_community.vectorstores import FAISS

        public_docs = collect_documents(ULBRICH_PUBLIC_DIR)
        internal_docs = collect_documents(INTERNAL_MOCK_DOCS_DIR)

        if db is not None:
            replace_documents_for_source(db, source_type="public", docs=public_docs)
            replace_documents_for_source(db, source_type="internal", docs=internal_docs)

        documents: list[Document] = []
        for source_type, docs in [("public", public_docs), ("internal", internal_docs)]:
            for d in docs:
                for i, chunk in enumerate(chunk_text(d["text"])):
                    documents.append(
                        Document(
                            page_content=chunk,
                            metadata={
                                "source": d["source"],
                                "source_type": source_type,
                                "chunk_id": i,
                            },
                        )
                    )

        if not documents:
            return {"status": "empty", "chunks_indexed": 0, "message": "No source documents found."}

        embeddings = self._embedding_model()
        store = FAISS.from_documents(documents, embeddings)
        self._index_path().mkdir(parents=True, exist_ok=True)
        store.save_local(str(self._index_path()))
        return {
            "status": "ok",
            "chunks_indexed": len(documents),
            "index_path": str(self._index_path()),
            "message": "",
        }

    def _load_index(self):
        from langchain_community.vectorstores import FAISS

        index_path = self._index_path()
        if not index_path.exists() or not any(index_path.iterdir()):
            return None
        embeddings = self._embedding_model()
        return FAISS.load_local(str(index_path), embeddings, allow_dangerous_deserialization=True)

    def list_indexed_docs(self, db: Session | None = None) -> list[dict]:
        if db is not None:
            docs = list_documents(db)
            if docs:
                return docs

        files = []
        pairs = [("public", ULBRICH_PUBLIC_DIR), ("internal", INTERNAL_MOCK_DOCS_DIR)]
        for source_type, directory in pairs:
            for d in collect_documents(directory):
                files.append(
                    {
                        "doc_id": None,
                        "source_type": source_type,
                        "title": Path(d["source"]).name,
                        "path_or_url": d["source"],
                        "checksum": None,
                        "chunk_count": len(chunk_text(d["text"])),
                    }
                )
        return files

    def search(self, query: str, top_k: int = 5, db: Session | None = None) -> list[Citation]:
        store = self._load_index()
        if store is None:
            return []

        results = store.similarity_search_with_score(query, k=top_k)
        citations: list[Citation] = []
        for doc, score in results:
            citation = build_citation(
                source=str(doc.metadata.get("source", "unknown")),
                snippet=doc.page_content,
                score=float(score),
            )
            citations.append(citation)
            if db is not None:
                create_retrieval_audit(
                    db,
                    query=query,
                    source=citation.source,
                    score=float(citation.score or 0.0),
                )
        return citations
