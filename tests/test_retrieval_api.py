from fastapi.testclient import TestClient

from app.core.constants import INTERNAL_MOCK_DOCS_DIR, ULBRICH_PUBLIC_DIR
from app.main import app

client = TestClient(app)


def _seed_local_docs() -> tuple[str | None, str | None]:
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
    public_path.write_text(
        "Public corpus example for alloy certifications and delivery constraints.",
        encoding="utf-8",
    )
    internal_path.write_text(
        "# Internal\nThin foil requests should be escalated for engineering review.",
        encoding="utf-8",
    )
    return prior_public, prior_internal


def _restore_local_docs(prior_public: str | None, prior_internal: str | None) -> None:
    public_path = ULBRICH_PUBLIC_DIR / "sample_ulbrich.txt"
    internal_path = INTERNAL_MOCK_DOCS_DIR / "sample_internal.md"
    if prior_public is None:
        public_path.unlink(missing_ok=True)
    else:
        public_path.write_text(prior_public, encoding="utf-8")
    if prior_internal is None:
        internal_path.unlink(missing_ok=True)
    else:
        internal_path.write_text(prior_internal, encoding="utf-8")


def test_retrieval_ingest_reindex_and_docs_endpoints():
    prior_public, prior_internal = _seed_local_docs()
    try:
        public_resp = client.post("/retrieval/ingest/public")
        assert public_resp.status_code == 200
        assert "files_discovered" in public_resp.json()

        internal_resp = client.post("/retrieval/ingest/internal")
        assert internal_resp.status_code == 200
        assert "files_discovered" in internal_resp.json()

        reindex_resp = client.post("/retrieval/reindex")
        assert reindex_resp.status_code == 200
        assert reindex_resp.json()["status"] in {"ok", "empty"}

        docs_resp = client.get("/retrieval/docs")
        assert docs_resp.status_code == 200
        body = docs_resp.json()
        assert "count" in body
        assert "docs" in body
    finally:
        _restore_local_docs(prior_public, prior_internal)


def test_retrieval_search_endpoint_with_db_audit():
    prior_public, prior_internal = _seed_local_docs()
    try:
        client.post("/retrieval/reindex")
        resp = client.post("/retrieval/search", json={"query": "engineering review", "top_k": 3})
        assert resp.status_code == 200
        body = resp.json()
        assert "hits" in body
    finally:
        _restore_local_docs(prior_public, prior_internal)
