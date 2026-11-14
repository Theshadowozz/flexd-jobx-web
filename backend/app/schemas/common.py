from datetime import datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Patch(Input):
    @model_validator(mode="after")
    def check_patch(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("At least one field is required")
        return self


class Read(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Timestamps(Read):
    created_at: datetime
    updated_at: datetime
