from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from app.schemas.common import Input, Patch, Read, UnsignedId

AnalysisStatus = Literal["queued", "processing", "completed", "failed", "needs_human_review"]


class ArtifactAnalysisCreate(Input):
    artifact_id: UnsignedId
    analysis_status: AnalysisStatus = "queued"
    model_provider: str | None = Field(default="openai-compatible", max_length=80)
    model_name: str | None = Field(default=None, max_length=120)
    prompt_version: str | None = Field(default=None, max_length=80)
    extracted_summary: str | None = None
    raw_result: dict[str, Any] | None = None
    error_message: str | None = None
    reviewed_by_user_id: UnsignedId | None = None
    reviewed_at: datetime | None = None


class ArtifactAnalysisUpdate(Patch):
    analysis_status: AnalysisStatus | None = None
    model_provider: str | None = Field(default=None, max_length=80)
    model_name: str | None = Field(default=None, max_length=120)
    prompt_version: str | None = Field(default=None, max_length=80)
    extracted_summary: str | None = None
    raw_result: dict[str, Any] | None = None
    error_message: str | None = None
    reviewed_by_user_id: UnsignedId | None = None
    reviewed_at: datetime | None = None


class ArtifactAnalysisRead(Read):
    id: UnsignedId
    artifact_id: UnsignedId
    analysis_status: str
    model_provider: str | None
    model_name: str | None
    prompt_version: str | None
    extracted_summary: str | None
    raw_result: dict[str, Any] | None
    error_message: str | None
    reviewed_by_user_id: UnsignedId | None
    reviewed_at: datetime | None
    created_at: datetime
