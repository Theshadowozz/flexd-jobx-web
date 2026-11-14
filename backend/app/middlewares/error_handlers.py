import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException

from app.utils.exceptions import AppError

logger = logging.getLogger(__name__)


def error_response(status: int, message: str, errors: dict, headers=None):
    return JSONResponse(
        status_code=status,
        content={"message": {"error": message}, "error": errors, "data": {}},
        headers=headers,
    )


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError):
        headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
        return error_response(exc.status_code, exc.message, exc.errors, headers)

    @app.exception_handler(RequestValidationError)
    async def handle_validation(request: Request, exc: RequestValidationError):
        errors = {}
        for item in exc.errors():
            key = ".".join(str(part) for part in item["loc"] if part != "body") or "request"
            errors[key] = item["msg"]
        return error_response(422, "Validation failed", errors)

    @app.exception_handler(HTTPException)
    async def handle_http(request: Request, exc: HTTPException):
        return error_response(
            exc.status_code, str(exc.detail), {"request": str(exc.detail)}, exc.headers
        )

    @app.exception_handler(SQLAlchemyError)
    @app.exception_handler(Exception)
    async def handle_internal(request: Request, exc: Exception):
        # Exception strings/tracebacks can contain bound SQL values. Log type only.
        logger.error("Request %s failed: %s", request.state.request_id, type(exc).__name__)
        return error_response(500, "Internal server error", {"server": "Unable to process request"})
