from datetime import datetime
from typing import Literal

from pydantic import Field, JsonValue

from app.schemas.common import Input, Patch, Read, Timestamps
from app.schemas.response import ApiResponse, Pagination

EmploymentType = Literal["full_time", "part_time", "contract", "internship", "freelance"]
WorkMode = Literal["onsite", "hybrid", "remote"]


class JobPostFields(Input):
    title: str = Field(min_length=1, max_length=200)
    business_problem: str = Field(min_length=1, max_length=16000)
    job_summary: str | None = Field(default=None, max_length=16000)
    job_description: str | None = Field(default=None, max_length=1000000)
    employment_type: EmploymentType
    work_mode: WorkMode
    city: str | None = Field(default=None, max_length=120)
    province: str | None = Field(default=None, max_length=120)
    country: str = Field(default="Indonesia", min_length=1, max_length=100)
    salary_min: int | None = Field(default=None, ge=0, le=18446744073709551615)
    salary_max: int | None = Field(default=None, ge=0, le=18446744073709551615)
    currency: str = Field(default="IDR", pattern=r"^[A-Z]{3}$")
    ai_generation_metadata: JsonValue = None
    approval_status: Literal["draft", "pending_approval", "approved", "rejected"] = "draft"
    publication_status: Literal["unpublished", "published", "paused", "closed"] = "unpublished"
    closes_at: datetime | None = None


class JobPostCreate(JobPostFields):
    user_id: int = Field(gt=0, le=18446744073709551615)


class JobPostUpdate(JobPostFields, Patch):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    business_problem: str | None = Field(default=None, min_length=1, max_length=16000)
    employment_type: EmploymentType | None = None
    work_mode: WorkMode | None = None


class JobPostRead(JobPostFields, Timestamps):
    model_config = {"from_attributes": True}
    id: int
    user_id: int
    published_at: datetime | None


class JobPostDetailData(Read):
    job_post: JobPostRead


class JobPostListData(Read):
    job_posts: list[JobPostRead]
    pagination: Pagination


JobPostDetailResponse = ApiResponse[JobPostDetailData]
JobPostListResponse = ApiResponse[JobPostListData]
