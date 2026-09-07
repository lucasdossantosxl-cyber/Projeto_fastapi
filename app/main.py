"""Application factory and entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import AdviceServiceError
from app.core.logging import configure_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup / shutdown events."""
    configure_logging()
    logger.info("Application starting up", extra={"version": settings.APP_VERSION})
    yield
    logger.info("Application shutting down")


def create_application() -> FastAPI:
    """Factory: build and configure the FastAPI app."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # Global exception handler for our custom exceptions
    @app.exception_handler(AdviceServiceError)
    async def advice_service_exception_handler(
        request: Request, exc: AdviceServiceError
    ) -> JSONResponse:
        logger.warning("AdviceServiceError caught", extra={
            "path": request.url.path,
            "error": exc.message,
            "status": exc.status_code,
        })
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    app.include_router(api_router)
    return app


app = create_application()
