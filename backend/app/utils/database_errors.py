from sqlalchemy.exc import DBAPIError

from app.utils.exceptions import AppError


def translate_database_error(exc: DBAPIError, entity: str) -> AppError:
    code = exc.orig.args[0] if exc.orig and exc.orig.args else None
    if code == 1062 or "UNIQUE constraint failed" in str(exc.orig):
        return AppError(409, "Resource conflict", {entity: "Unique value already exists"})
    if code in (1451, 1452) or "FOREIGN KEY constraint failed" in str(exc.orig):
        return AppError(409, "Resource conflict", {entity: "Related data prevents this operation"})
    if code in (3819, 1264, 1406, 1048) or "CHECK constraint failed" in str(exc.orig):
        return AppError(422, "Validation failed", {entity: "Database constraint violated"})
    return AppError(500, "Internal server error", {"server": "Unable to process request"})
