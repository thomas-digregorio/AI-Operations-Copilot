from fastapi import APIRouter

from app.schemas.retrieval import RetrievalRequest, RetrievalResponse
from app.services.rag_service import RAGService

router = APIRouter(prefix="/retrieval", tags=["retrieval"])
service = RAGService()


@router.post("/search", response_model=RetrievalResponse)
def search_docs(request: RetrievalRequest) -> RetrievalResponse:
    hits = service.search(request.query, request.top_k)
    return RetrievalResponse(query=request.query, hits=hits)


@router.post("/index")
def build_index() -> dict:
    return service.build_index()
