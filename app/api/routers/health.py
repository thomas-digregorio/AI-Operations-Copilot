from datetime import datetime

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "app_env": settings.app_env,
        "timestamp": datetime.utcnow().isoformat(),
        "vector_store": settings.vector_store,
        "llm_provider": settings.llm_provider,
    }
