from app.core.constants import INTERNAL_MOCK_DOCS_DIR, ULBRICH_PUBLIC_DIR
from app.services.rag_service import RAGService


def test_ingestion_and_retrieval_returns_citations(tmp_path):
    ULBRICH_PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    INTERNAL_MOCK_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    public_path = ULBRICH_PUBLIC_DIR / "sample_ulbrich.txt"
    internal_path = INTERNAL_MOCK_DOCS_DIR / "sample_internal.md"
    prior_public = (
        public_path.read_text(encoding="utf-8", errors="ignore") if public_path.exists() else None
    )
    prior_internal = (
        internal_path.read_text(encoding="utf-8", errors="ignore")
        if internal_path.exists()
        else None
    )
    try:
        public_path.write_text(
            "Ulbrich provides precision strip and foil alloys for demanding applications.",
            encoding="utf-8",
        )
        internal_path.write_text(
            "# Synthetic Internal Document\nThin foil below 0.05mm requires engineering review.",
            encoding="utf-8",
        )

        svc = RAGService()
        build = svc.build_index()
        assert build["status"] == "ok"

        hits = svc.search("thin foil engineering review", top_k=3)
        assert len(hits) > 0
        assert any("source" in h.model_dump() for h in hits)
    finally:
        if prior_public is None:
            public_path.unlink(missing_ok=True)
        else:
            public_path.write_text(prior_public, encoding="utf-8")
        if prior_internal is None:
            internal_path.unlink(missing_ok=True)
        else:
            internal_path.write_text(prior_internal, encoding="utf-8")
