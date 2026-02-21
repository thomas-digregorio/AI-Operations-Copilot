from pydantic import BaseModel, Field

from app.schemas.common import Citation


class RetrievalRequest(BaseModel):
    query: str
    top_k: int = 5


class RetrievalResponse(BaseModel):
    query: str
    hits: list[Citation] = Field(default_factory=list)
