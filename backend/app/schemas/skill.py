from datetime import datetime

from pydantic import Field

from app.schemas.common import Input, Patch, Read
from app.schemas.response import ApiResponse, Pagination


class SkillCreate(Input):
    canonical_name: str = Field(min_length=1, max_length=120)
    slug: str = Field(min_length=1, max_length=140)
    category: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=16000)
    parent_skill_id: int | None = Field(default=None, gt=0, le=18446744073709551615)
    taxonomy_source: str | None = Field(default=None, max_length=120)


class SkillUpdate(Patch):
    canonical_name: str | None = Field(default=None, min_length=1, max_length=120)
    slug: str | None = Field(default=None, min_length=1, max_length=140)
    category: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=16000)
    parent_skill_id: int | None = Field(default=None, gt=0, le=18446744073709551615)
    taxonomy_source: str | None = Field(default=None, max_length=120)


class SkillRead(Read):
    id: int
    canonical_name: str
    slug: str
    category: str | None
    description: str | None
    parent_skill_id: int | None
    taxonomy_source: str | None
    created_at: datetime


class SkillDetailData(Read):
    skill: SkillRead


class SkillListData(Read):
    skills: list[SkillRead]
    pagination: Pagination


SkillDetailResponse = ApiResponse[SkillDetailData]
SkillListResponse = ApiResponse[SkillListData]
