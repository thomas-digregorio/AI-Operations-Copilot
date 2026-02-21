from app.schemas.common import Citation


def build_citation(source: str, snippet: str, score: float | None = None) -> Citation:
    compact = " ".join(snippet.split())
    return Citation(source=source, snippet=compact[:300], score=score)
