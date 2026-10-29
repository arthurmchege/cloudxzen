import logging

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class ErrorResponse(BaseModel):
    class Error(BaseModel):
        code: str
        message: str
        details: list[dict] | None = None

    error: Error


async def validation_exception_handler(
    _: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed.",
                "details": jsonable_encoder(exc.errors()),
            }
        },
    )


async def http_exception_handler(
    _: Request,
    exc: HTTPException,
) -> JSONResponse:
    code = {
        404: "not_found",
        409: "conflict",
    }.get(exc.status_code, "http_error")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": str(exc.detail),
            }
        },
        headers=exc.headers,
    )


async def database_exception_handler(
    request: Request,
    exc: SQLAlchemyError,
) -> JSONResponse:
    logger.exception(
        "database_error method=%s path=%s",
        request.method,
        request.url.path,
        exc_info=exc,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "database_error",
                "message": "The request could not be completed.",
            }
        },
    )
