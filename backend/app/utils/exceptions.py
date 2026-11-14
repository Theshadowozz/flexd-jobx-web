from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.schemas.response import EmptyResponse
from app.utils.response import error_response


class AppError(Exception):
    def __init__(
        self,
        status_code: int,
        category: str,
        errors: dict[str, str],
        message: str = "Request gagal diproses",
        headers=None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.category = category
        self.errors = errors
        self.message = message
        self.headers = headers


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return error_response(
        status_code=exc.status_code,
        category=exc.category,
        message=exc.message,
        errors=exc.errors,
        headers=exc.headers,
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    descriptions = {
        "missing": "Field wajib diisi",
        "string_type": "Harus berupa teks",
        "string_too_short": "Teks terlalu pendek",
        "string_too_long": "Teks terlalu panjang",
        "extra_forbidden": "Field tidak diizinkan",
        "int_parsing": "Harus berupa bilangan bulat",
        "greater_than": "Nilai harus lebih besar dari batas minimum",
        "greater_than_equal": "Nilai kurang dari batas minimum",
        "less_than_equal": "Nilai melebihi batas maksimum",
        "json_invalid": "Format JSON tidak valid",
    }
    errors: dict[str, str] = {}
    for item in exc.errors():
        if item["type"] == "json_invalid":
            return error_response(
                status_code=400,
                category="bad_request",
                message="Request tidak valid",
                errors={"body": "Format JSON tidak valid"},
            )
        location = list(item["loc"])
        if location and location[0] == "body":
            location = location[1:]
        attribute = ".".join(map(str, location)) or "request"
        errors.setdefault(attribute, descriptions.get(item["type"], "Nilai tidak valid"))
    return error_response(
        status_code=422, category="validation", message="Validasi gagal", errors=errors
    )


async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
    descriptions = {
        400: "Request tidak valid",
        401: "Autentikasi diperlukan atau kredensial tidak valid",
        403: "Akses tidak diizinkan",
        404: "Endpoint atau data tidak ditemukan",
        405: "HTTP method tidak diizinkan",
        409: "Operasi berbenturan dengan data yang ada",
        413: "Ukuran request terlalu besar",
        422: "Validasi gagal",
        429: "Terlalu banyak request",
        500: "Terjadi kesalahan server",
        503: "Layanan sementara tidak tersedia",
    }
    description = descriptions.get(exc.status_code, "Request gagal diproses")
    return error_response(
        status_code=exc.status_code,
        category={
            400: "bad_request",
            401: "authentication",
            403: "authorization",
            404: "not_found",
            405: "method_not_allowed",
            409: "conflict",
            413: "payload_too_large",
            415: "unsupported_media_type",
            422: "validation",
            429: "rate_limit",
            502: "upstream_error",
            503: "service_unavailable",
            504: "timeout",
        }.get(exc.status_code, "internal"),
        message=description,
        errors={"request": description},
        headers=exc.headers,
    )


async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return error_response(
        status_code=500,
        message="Terjadi kesalahan server",
        errors={"server": "Request tidak dapat diproses"},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(HTTPException, http_error_handler)
    app.add_exception_handler(Exception, internal_error_handler)


ERROR_RESPONSES = {
    code: {"model": EmptyResponse, "description": description}
    for code, description in {
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not found",
        405: "Method not allowed",
        409: "Conflict",
        422: "Validation error",
        500: "Internal server error",
        503: "Service unavailable",
    }.items()
}
