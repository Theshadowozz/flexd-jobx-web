from collections.abc import Mapping

from fastapi.responses import JSONResponse

from app.schemas.response import EmptyResponse


def error_response(
    *,
    status_code: int,
    message: str,
    errors: dict[str, str],
    category: str = "internal",
    headers: Mapping[str, str] | None = None,
):
    return JSONResponse(
        status_code=status_code,
        headers=headers,
        content=EmptyResponse(
            message={"error": message},
            error={category: errors},
            data={},
        ).model_dump(mode="json"),
    )
