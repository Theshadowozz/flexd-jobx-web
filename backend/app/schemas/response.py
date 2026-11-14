from typing import Generic, TypeVar

from pydantic import BaseModel, Field

Data = TypeVar("Data", bound=BaseModel)


class Pagination(BaseModel):
    total: int
    limit: int
    offset: int


class EmptyData(BaseModel):
    pass


class Response(BaseModel, Generic[Data]):
    message: dict[str, str]
    error: dict[str, str] = Field(default_factory=dict)
    data: Data
