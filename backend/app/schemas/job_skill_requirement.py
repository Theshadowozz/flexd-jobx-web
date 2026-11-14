from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field

from app.schemas.common import Input, Patch, Read, UnsignedId

RequirementType = Literal["must_have", "preferred"]
Level = Literal["beginner", "intermediate", "advanced", "expert"]
Weight = Annotated[Decimal, Field(ge=0, max_digits=5, decimal_places=2)]


class JobSkillRequirementCreate(Input):
    job_id: UnsignedId
    skill_id: UnsignedId
    requirement_type: RequirementType = "must_have"
    minimum_level: Level | None = None
    weight: Weight = Decimal("1.00")
    requirement_note: str | None = Field(default=None, max_length=500)


class JobSkillRequirementUpdate(Patch):
    requirement_type: RequirementType | None = None
    minimum_level: Level | None = None
    weight: Weight | None = None
    requirement_note: str | None = Field(default=None, max_length=500)


class JobSkillRequirementRead(Read):
    id: UnsignedId
    job_id: UnsignedId
    skill_id: UnsignedId
    requirement_type: str
    minimum_level: str | None
    weight: Decimal
    requirement_note: str | None
    created_at: datetime
