from datetime import date
from typing import Literal

from pydantic import Field, JsonValue

from app.schemas.common import Input, Patch, Read, Timestamps
from app.schemas.response import ApiResponse, Pagination

ArtifactType = Literal[
    "github_repository", "document", "spreadsheet", "image", "video", "design_link", "other"
]
Visibility = Literal["private", "unlisted", "matching_employers", "public"]
ProcessingStatus = Literal[
    "not_started", "queued", "processing", "completed", "failed", "needs_review"
]


class ArtifactFields(Input):
    title: str = Field(min_length=1, max_length=200)
    artifact_type: ArtifactType
    description: str | None = Field(default=None, max_length=16000)
    source_url: str | None = Field(default=None, min_length=1, max_length=1000)
    storage_key: str | None = Field(default=None, min_length=1, max_length=500)
    mime_type: str | None = Field(default=None, max_length=150)
    visibility: Visibility = "matching_employers"
    project_started_at: date | None = None
    project_completed_at: date | None = None
    processing_status: ProcessingStatus = "not_started"
    metadata: JsonValue = None


class ArtifactCreate(ArtifactFields):
    owner_user_id: int = Field(gt=0, le=18446744073709551615)


class ArtifactUpdate(ArtifactFields, Patch):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    artifact_type: ArtifactType | None = None


class ArtifactRead(ArtifactFields, Timestamps):
    model_config = {"from_attributes": True}
    id: int
    owner_user_id: int
    metadata: JsonValue = Field(validation_alias="metadata_json")


class ArtifactDetailData(Read):
    artifact: ArtifactRead


class ArtifactListData(Read):
    artifacts: list[ArtifactRead]
    pagination: Pagination


ArtifactDetailResponse = ApiResponse[ArtifactDetailData]
ArtifactListResponse = ApiResponse[ArtifactListData]
