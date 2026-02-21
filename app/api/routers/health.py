from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "service": "manufacturing-ai-copilot",
        "version": "0.1.0",
        "app_env": settings.app_env,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "vector_store": settings.vector_store,
        "llm_provider": settings.llm_provider,
    }
