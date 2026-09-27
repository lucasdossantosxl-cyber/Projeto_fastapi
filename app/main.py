"""Fábrica da aplicação e ciclo de vida dos recursos."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import AdviceServiceError
from app.core.logging import configure_logging, get_logger
from app.services.history_service import initialize_database

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    await run_in_threadpool(initialize_database)
    async with httpx.AsyncClient(timeout=settings.ADVICE_API_TIMEOUT) as client:
        app.state.http_client = client
        logger.info("Aplicação iniciada")
        yield
    logger.info("Aplicação encerrada")


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    @app.exception_handler(AdviceServiceError)
    async def service_error_handler(request: Request, exc: AdviceServiceError) -> JSONResponse:
        logger.warning("%s: %s (HTTP %s)", request.url.path, exc.message, exc.status_code)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    app.include_router(api_router)
    return app


app = create_application()
