from app.core.constants import INTERNAL_MOCK_DOCS_DIR, ULBRICH_PUBLIC_DIR
from app.services.rag_service import RAGService


def test_ingestion_and_retrieval_returns_citations(tmp_path):
    ULBRICH_PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    INTERNAL_MOCK_DOCS_DIR.mkdir(parents=True, exist_ok=True)

    (ULBRICH_PUBLIC_DIR / "sample_ulbrich.txt").write_text(
        "Ulbrich provides precision strip and foil alloys for demanding applications.",
        encoding="utf-8",
    )
    (INTERNAL_MOCK_DOCS_DIR / "sample_internal.md").write_text(
        "# Synthetic Internal Document\nThin foil below 0.05mm requires engineering review.",
        encoding="utf-8",
    )

    svc = RAGService()
    build = svc.build_index()
    assert build["status"] == "ok"

    hits = svc.search("thin foil engineering review", top_k=3)
    assert len(hits) > 0
    assert any("source" in h.model_dump() for h in hits)
