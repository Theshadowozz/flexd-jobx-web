from pydantic import Field

from app.schemas.common import Input, Patch, Read, UnsignedId


class SkillAliasCreate(Input):
    skill_id: UnsignedId
    alias_name: str = Field(min_length=1, max_length=140)


class SkillAliasUpdate(Patch):
    skill_id: UnsignedId | None = None
    alias_name: str | None = Field(default=None, min_length=1, max_length=140)


class SkillAliasRead(Read):
    id: UnsignedId
    skill_id: UnsignedId
    alias_name: str
    normalized_alias: str
