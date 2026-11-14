from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ArtifactType = Literal[
    "github_repository", "document", "spreadsheet", "image", "video", "design_link", "other"
]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SkillDefinition(Contract):
    id: str = Field(min_length=1)
    canonical_name: str = Field(min_length=1)
    aliases: list[str] = Field(default_factory=list)


class SourceBlock(Contract):
    """Reader-provided citation, not a location invented by a model."""

    block_id: str = Field(min_length=1)
    location: str = Field(min_length=1, max_length=300)
    text: str = Field(min_length=1)


class ArtifactContent(Contract):
    source_revision: str = Field(min_length=1)
    content_markdown: str = ""
    source_locations: list[SourceBlock] = Field(default_factory=list)
    media_references: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    processing_warnings: list[str] = Field(default_factory=list)


class ArtifactReference(Contract):
    artifact_type: ArtifactType
    source_url: str | None = None
    storage_key: str | None = None
