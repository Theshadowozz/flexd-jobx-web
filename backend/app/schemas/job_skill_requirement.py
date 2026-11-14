from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import Field

from app.schemas.common import Input, Patch, Read
from app.schemas.response import ApiResponse, Pagination


class JobSkillRequirementFields(Input):
    requirement_type: Literal["must_have", "preferred"] = "must_have"
    minimum_level: Literal["beginner", "intermediate", "advanced", "expert"] | None = None
    weight: Decimal = Field(default=Decimal("1.00"), ge=0, max_digits=5, decimal_places=2)
    requirement_note: str | None = Field(default=None, max_length=500)


class JobSkillRequirementCreate(JobSkillRequirementFields):
    job_id: int = Field(gt=0, le=18446744073709551615)
    skill_id: int = Field(gt=0, le=18446744073709551615)


class JobSkillRequirementUpdate(JobSkillRequirementFields, Patch):
    pass


class JobSkillRequirementRead(JobSkillRequirementFields, Read):
    model_config = {"from_attributes": True}
    id: int
    job_id: int
    skill_id: int
    created_at: datetime


class JobSkillRequirementDetailData(Read):
    job_skill_requirement: JobSkillRequirementRead


class JobSkillRequirementListData(Read):
    job_skill_requirements: list[JobSkillRequirementRead]
    pagination: Pagination


JobSkillRequirementDetailResponse = ApiResponse[JobSkillRequirementDetailData]
JobSkillRequirementListResponse = ApiResponse[JobSkillRequirementListData]
