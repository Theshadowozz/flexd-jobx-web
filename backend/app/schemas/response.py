from typing import Generic, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class ApiResponse(BaseModel, Generic[DataT]):
    message: dict[str, str] = Field(default_factory=dict)
    error: dict[str, dict[str, str]] = Field(default_factory=dict)
    data: DataT


class Pagination(BaseModel):
    offset: int
    limit: int
    total: int


EmptyResponse = ApiResponse[dict[str, object]]
