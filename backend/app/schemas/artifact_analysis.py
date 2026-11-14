from datetime import datetime
from typing import Literal

from pydantic import Field, JsonValue

from app.schemas.common import Input, Patch, Read
from app.schemas.response import ApiResponse, Pagination

AnalysisStatus = Literal["queued", "processing", "completed", "failed", "needs_human_review"]


class ArtifactAnalysisFields(Input):
    analysis_status: AnalysisStatus = "queued"
    model_provider: str | None = Field(default=None, max_length=80)
    model_name: str | None = Field(default=None, max_length=120)
    prompt_version: str | None = Field(default=None, max_length=80)
    extracted_summary: str | None = Field(default=None, max_length=16000)
    raw_result: JsonValue = None
    error_message: str | None = Field(default=None, max_length=16000)
    reviewed_by_user_id: int | None = Field(default=None, gt=0, le=18446744073709551615)


class ArtifactAnalysisCreate(ArtifactAnalysisFields):
    artifact_id: int = Field(gt=0, le=18446744073709551615)


class ArtifactAnalysisUpdate(ArtifactAnalysisFields, Patch):
    pass


class ArtifactAnalysisRead(ArtifactAnalysisFields, Read):
    model_config = {"from_attributes": True}
    id: int
    artifact_id: int
    reviewed_at: datetime | None
    created_at: datetime


class ArtifactAnalysisDetailData(Read):
    artifact_analysis: ArtifactAnalysisRead


class ArtifactAnalysisListData(Read):
    artifact_analyses: list[ArtifactAnalysisRead]
    pagination: Pagination


ArtifactAnalysisDetailResponse = ApiResponse[ArtifactAnalysisDetailData]
ArtifactAnalysisListResponse = ApiResponse[ArtifactAnalysisListData]
