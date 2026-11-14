from datetime import date
from typing import Any, Literal

from pydantic import Field

from app.schemas.common import Input, Patch, Timestamps, UnsignedId

ArtifactType = Literal[
    "github_repository", "document", "spreadsheet", "image", "video", "design_link", "other"
]
Visibility = Literal["private", "unlisted", "matching_employers", "public"]
Processing = Literal["not_started", "queued", "processing", "completed", "failed", "needs_review"]


class ArtifactCreate(Input):
    owner_user_id: UnsignedId
    title: str = Field(min_length=1, max_length=200)
    artifact_type: ArtifactType
    description: str | None = None
    source_url: str | None = Field(default=None, max_length=1000)
    storage_key: str | None = Field(default=None, max_length=500)
    mime_type: str | None = Field(default=None, max_length=150)
    visibility: Visibility = "matching_employers"
    project_started_at: date | None = None
    project_completed_at: date | None = None
    processing_status: Processing = "not_started"
    metadata: dict[str, Any] | None = None


class ArtifactUpdate(Patch):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    artifact_type: ArtifactType | None = None
    description: str | None = None
    source_url: str | None = Field(default=None, max_length=1000)
    storage_key: str | None = Field(default=None, max_length=500)
    mime_type: str | None = Field(default=None, max_length=150)
    visibility: Visibility | None = None
    project_started_at: date | None = None
    project_completed_at: date | None = None
    processing_status: Processing | None = None
    metadata: dict[str, Any] | None = None


class ArtifactRead(Timestamps):
    id: UnsignedId
    owner_user_id: UnsignedId
    title: str
    artifact_type: str
    description: str | None
    source_url: str | None
    storage_key: str | None
    mime_type: str | None
    visibility: str
    project_started_at: date | None
    project_completed_at: date | None
    processing_status: str
    metadata: dict[str, Any] | None = Field(validation_alias="metadata_json")
