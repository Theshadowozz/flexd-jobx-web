from datetime import datetime
from decimal import Decimal
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer, model_validator

UnsignedId = Annotated[
    int,
    Field(gt=0, le=18_446_744_073_709_551_615),
    PlainSerializer(str, return_type=str, when_used="json"),
]
UnsignedAmount = Annotated[
    int,
    Field(ge=0, le=18_446_744_073_709_551_615),
    PlainSerializer(str, return_type=str, when_used="json"),
]
Password = Annotated[str, Field(min_length=12, max_length=128)]
Score = Annotated[Decimal, Field(ge=0, le=100, max_digits=5, decimal_places=2)]
Confidence = Annotated[Decimal, Field(ge=0, le=1, max_digits=5, decimal_places=4)]


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Patch(Input):
    @model_validator(mode="after")
    def check_patch(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("At least one field is required")
        return self


class Read(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class Timestamps(Read):
    created_at: datetime
    updated_at: datetime
