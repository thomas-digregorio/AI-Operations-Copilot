from fastapi import FastAPI

from app.api.routers import diagnostics, health, ml_inference, ml_training, quote, retrieval, rules
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.db.session import Base, engine

logger = get_logger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    settings.ensure_runtime_dirs()

    app = FastAPI(title="Manufacturing AI Copilot", version="0.1.0")

    Base.metadata.create_all(bind=engine)

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
