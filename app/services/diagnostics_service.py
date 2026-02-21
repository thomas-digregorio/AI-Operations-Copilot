from __future__ import annotations

from pathlib import Path

from app.core.config import get_settings
from app.core.constants import (
    DEFAULT_METRICS_PATH,
    DEFAULT_MODEL_PATH,
    INTERNAL_MOCK_DOCS_DIR,
    ROOT_DIR,
    ULBRICH_PUBLIC_DIR,
    VECTOR_DIR,
)


class DiagnosticsService:
    def status(self) -> dict:
        settings = get_settings()
        indexed_docs = self._indexed_docs()
        return {
            "model_artifact_exists": DEFAULT_MODEL_PATH.exists(),
            "metrics_artifact_exists": DEFAULT_METRICS_PATH.exists(),
            "vector_index_exists": VECTOR_DIR.exists() and any(VECTOR_DIR.iterdir()),
            "vector_index_path": str(VECTOR_DIR),
            "model_path": str(DEFAULT_MODEL_PATH),
            "metrics_path": str(DEFAULT_METRICS_PATH),
            "indexed_doc_count": len(indexed_docs),
            "indexed_doc_sources": indexed_docs,
            "config_summary": {
                "app_env": settings.app_env,
                "database_backend": (
                    "sqlite" if settings.database_url.startswith("sqlite") else "postgres_or_other"
                ),
                "vector_store": settings.vector_store,
                "embedding_provider": settings.embedding_provider,
                "embedding_model": settings.embedding_model,
                "llm_provider": settings.llm_provider,
                "llm_model": settings.llm_model,
                "ollama_base_url": settings.ollama_base_url,
            },
            "prompt_files": self._prompt_files(),
        }

    def _indexed_docs(self) -> list[str]:
        sources = self._list_files(INTERNAL_MOCK_DOCS_DIR) + self._list_files(ULBRICH_PUBLIC_DIR)
        return sorted(sources)

    def _prompt_files(self) -> list[str]:
        prompt_dir = ROOT_DIR / "prompts"
        return self._list_files(prompt_dir)

    @staticmethod
    def _list_files(path: Path) -> list[str]:
        if not path.exists():
            return []
        items = [p for p in path.iterdir() if p.is_file()]
        out: list[str] = []
        for item in items:
            try:
                out.append(str(item.relative_to(ROOT_DIR)))
            except ValueError:
                out.append(str(item))
        return sorted(out)
