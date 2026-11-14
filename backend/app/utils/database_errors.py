from sqlalchemy.exc import IntegrityError, OperationalError

from app.utils.exceptions import AppError


def translate_database_error(exc, entity: str):
    code = exc.orig.args[0] if exc.orig.args else None
    if isinstance(exc, IntegrityError):
        if code in (1062, 1451) or "UNIQUE constraint failed" in str(exc.orig):
            raise AppError(
                409, "conflict", {entity: "Data duplikat atau masih digunakan data lain"}
            ) from exc
        if code in (1452, 3819, 4025) or "constraint failed" in str(exc.orig):
            raise AppError(
                422, "validation", {entity: "Referensi atau nilai data tidak valid"}
            ) from exc
    if isinstance(exc, OperationalError):
        if code in (1205, 1213):
            raise AppError(
                409, "conflict", {entity: "Perubahan bersamaan; ulangi request"}
            ) from exc
        if code in (2002, 2003, 2006, 2013):
            raise AppError(
                503, "service_unavailable", {"database": "Database tidak tersedia"}
            ) from exc
    raise exc
