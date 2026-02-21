from __future__ import annotations

from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import get_settings
from app.core.constants import INTERNAL_MOCK_DOCS_DIR, ULBRICH_PUBLIC_DIR
from app.schemas.common import Citation
from app.utils.citation_utils import build_citation
from app.utils.file_loaders import collect_documents
from app.utils.text_chunking import chunk_text


class RAGService:
    def __init__(self):
        self.settings = get_settings()

    def _embedding_model(self):
        return HuggingFaceEmbeddings(model_name=self.settings.embedding_model)

    def _index_path(self) -> Path:
        return Path(self.settings.vector_dir)

    def build_index(self) -> dict:
        docs = collect_documents(ULBRICH_PUBLIC_DIR) + collect_documents(INTERNAL_MOCK_DOCS_DIR)
        documents: list[Document] = []
        for d in docs:
            for i, chunk in enumerate(chunk_text(d["text"])):
                documents.append(
                    Document(
                        page_content=chunk,
                        metadata={"source": d["source"], "chunk_id": i},
                    )
                )

        if not documents:
            return {"status": "empty", "message": "No source documents found for indexing."}

        embeddings = self._embedding_model()
        store = FAISS.from_documents(documents, embeddings)
        self._index_path().mkdir(parents=True, exist_ok=True)
        store.save_local(str(self._index_path()))
        return {
            "status": "ok",
            "chunks_indexed": len(documents),
            "index_path": str(self._index_path()),
        }

    def _load_index(self) -> FAISS | None:
        index_path = self._index_path()
        if not index_path.exists() or not any(index_path.iterdir()):
            return None
        embeddings = self._embedding_model()
        return FAISS.load_local(str(index_path), embeddings, allow_dangerous_deserialization=True)

    def search(self, query: str, top_k: int = 5) -> list[Citation]:
        store = self._load_index()
        if store is None:
            return []

        results = store.similarity_search_with_score(query, k=top_k)
        citations: list[Citation] = []
        for doc, score in results:
            citations.append(
                build_citation(
                    source=str(doc.metadata.get("source", "unknown")),
                    snippet=doc.page_content,
                    score=float(score),
                )
            )
        return citations
