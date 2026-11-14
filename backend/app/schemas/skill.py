from datetime import datetime

from pydantic import Field

from app.schemas.common import Input, Patch, Read, UnsignedId


class SkillCreate(Input):
    canonical_name: str = Field(min_length=1, max_length=120)
    slug: str = Field(min_length=1, max_length=140, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    category: str | None = Field(default=None, max_length=100)
    description: str | None = None
    parent_skill_id: UnsignedId | None = None
    taxonomy_source: str | None = Field(default=None, max_length=120)


class SkillUpdate(Patch):
    canonical_name: str | None = Field(default=None, min_length=1, max_length=120)
    slug: str | None = Field(
        default=None, min_length=1, max_length=140, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
    )
    category: str | None = Field(default=None, max_length=100)
    description: str | None = None
    parent_skill_id: UnsignedId | None = None
    taxonomy_source: str | None = Field(default=None, max_length=120)


class SkillRead(Read):
    id: UnsignedId
    canonical_name: str
    slug: str
    category: str | None
    description: str | None
    parent_skill_id: UnsignedId | None
    taxonomy_source: str | None
    created_at: datetime
