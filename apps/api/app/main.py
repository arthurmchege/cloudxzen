import logging
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes.health import router as health_router
from app.api.routes.services import router as services_router
from app.core.config import Settings, get_settings
from app.core.errors import (
    database_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.core.logging import configure_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    settings = get_settings()
    logger.info("application_startup environment=%s", settings.environment)
    yield
    logger.info("application_shutdown")


def create_app(settings: Settings | None = None) -> FastAPI:
    runtime_settings = settings or get_settings()
    application = FastAPI(
        title="CloudXzen API",
        description="Backend API for the CloudXzen Service Reliability Journal.",
        version="0.1.0",
        docs_url=None if runtime_settings.is_production else "/docs",
        redoc_url=None if runtime_settings.is_production else "/redoc",
        openapi_url=None if runtime_settings.is_production else "/openapi.json",
        lifespan=lifespan,
    )

    application.add_exception_handler(HTTPException, http_exception_handler)
    application.add_exception_handler(RequestValidationError, validation_exception_handler)
    application.add_exception_handler(SQLAlchemyError, database_exception_handler)

    @application.middleware("http")
    async def request_logging_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        started_at = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - started_at) * 1000
            logger.exception(
                "request_failed request_id=%s method=%s path=%s duration_ms=%.2f",
                request_id,
                request.method,
                request.url.path,
                duration_ms,
            )
            raise

        duration_ms = (time.perf_counter() - started_at) * 1000
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request_complete request_id=%s method=%s path=%s status_code=%s duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response

    application.include_router(health_router)
    application.include_router(services_router)
    return application


app = create_app()
