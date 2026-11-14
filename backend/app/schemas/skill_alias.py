from pydantic import Field

from app.schemas.common import Input, Patch, Read
from app.schemas.response import ApiResponse, Pagination


class SkillAliasCreate(Input):
    skill_id: int = Field(gt=0, le=18446744073709551615)
    alias_name: str = Field(min_length=1, max_length=140)
    normalized_alias: str = Field(min_length=1, max_length=140)


class SkillAliasUpdate(Patch):
    alias_name: str | None = Field(default=None, min_length=1, max_length=140)
    normalized_alias: str | None = Field(default=None, min_length=1, max_length=140)


class SkillAliasRead(Read):
    id: int
    skill_id: int
    alias_name: str
    normalized_alias: str


class SkillAliasDetailData(Read):
    skill_alias: SkillAliasRead


class SkillAliasListData(Read):
    skill_aliases: list[SkillAliasRead]
    pagination: Pagination


SkillAliasDetailResponse = ApiResponse[SkillAliasDetailData]
SkillAliasListResponse = ApiResponse[SkillAliasListData]
