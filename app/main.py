from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import diagnostics, health, ml_inference, ml_training, quote, retrieval, rules
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.db.session import Base, engine
from app.middleware.security_middleware import (
    RateLimitMiddleware,
    RateLimitRule,
    RequestSizeLimitMiddleware,
)

logger = get_logger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    settings.ensure_runtime_dirs()

    docs_url = "/docs" if settings.enable_api_docs else None
    redoc_url = "/redoc" if settings.enable_api_docs else None
    openapi_url = "/openapi.json" if settings.enable_api_docs else None

    app = FastAPI(
        title="Manufacturing AI Copilot",
        version="0.1.0",
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
    )

    Base.metadata.create_all(bind=engine)

    cors_origins = [
        origin.strip()
        for origin in settings.cors_allow_origins.split(",")
        if origin.strip()
    ]
    if not cors_origins:
        cors_origins = ["*"]
    if settings.app_env.lower() != "local" and cors_origins == ["*"]:
        logger.warning(
            "Wildcard CORS in non-local environment is disabled. "
            "Set CORS_ALLOW_ORIGINS to explicit UI origin(s)."
        )
        cors_origins = []
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        RequestSizeLimitMiddleware,
        max_body_bytes=max(1, settings.max_request_size_bytes),
    )
    if settings.rate_limit_enabled:
        app.add_middleware(
            RateLimitMiddleware,
            default_limit_per_minute=max(1, settings.rate_limit_default_per_minute),
            rules=[
                RateLimitRule(
                    path_prefix="/health",
                    limit_per_minute=settings.rate_limit_health_per_minute,
                ),
                RateLimitRule(
                    path_prefix="/quote/draft",
                    limit_per_minute=settings.rate_limit_quote_llm_per_minute,
                ),
                RateLimitRule(
                    path_prefix="/quote/answer",
                    limit_per_minute=settings.rate_limit_quote_llm_per_minute,
                ),
                RateLimitRule(
                    path_prefix="/quote",
                    limit_per_minute=settings.rate_limit_quote_per_minute,
                ),
                RateLimitRule(
                    path_prefix="/ml/predict",
                    limit_per_minute=settings.rate_limit_ml_per_minute,
                ),
                RateLimitRule(
                    path_prefix="/ml/explain",
                    limit_per_minute=settings.rate_limit_ml_per_minute,
                ),
                RateLimitRule(
                    path_prefix="/ml/train",
                    limit_per_minute=settings.rate_limit_admin_per_minute,
                ),
                RateLimitRule(
                    path_prefix="/retrieval/ingest",
                    limit_per_minute=settings.rate_limit_admin_per_minute,
                ),
                RateLimitRule(
                    path_prefix="/retrieval/reindex",
                    limit_per_minute=settings.rate_limit_admin_per_minute,
                ),
                RateLimitRule(
                    path_prefix="/retrieval/index",
                    limit_per_minute=settings.rate_limit_admin_per_minute,
                ),
            ],
        )

    app.include_router(health.router)
    app.include_router(quote.router)
    app.include_router(retrieval.router)
    app.include_router(rules.router)
    app.include_router(ml_training.router)
    app.include_router(ml_inference.router)
    app.include_router(diagnostics.router)

    @app.get("/")
    def root() -> dict:
        return {
            "service": "manufacturing-ai-copilot",
            "message": "API is running.",
            "env": settings.app_env,
        }

    logger.info("Application initialized")
    return app


app = create_app()
