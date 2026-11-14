from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import Field

from app.schemas.common import Input, Patch, Read, Timestamps
from app.schemas.response import ApiResponse, Pagination

EmploymentPreference = Literal[
    "full_time", "part_time", "contract", "internship", "freelance", "any"
]
WorkPreference = Literal["onsite", "hybrid", "remote", "any"]
ProfileVisibility = Literal["private", "matching_only", "public"]


class CandidateProfileFields(Input):
    headline: str | None = Field(default=None, max_length=180)
    biography: str | None = Field(default=None, max_length=16000)
    city: str | None = Field(default=None, max_length=120)
    province: str | None = Field(default=None, max_length=120)
    country: str = Field(default="Indonesia", min_length=1, max_length=100)
    years_experience: Decimal | None = Field(default=None, ge=0, max_digits=4, decimal_places=1)
    preferred_employment_type: EmploymentPreference = "any"
    preferred_work_mode: WorkPreference = "any"
    expected_salary_min: int | None = Field(default=None, ge=0, le=18446744073709551615)
    expected_salary_max: int | None = Field(default=None, ge=0, le=18446744073709551615)
    available_from: date | None = None
    profile_visibility: ProfileVisibility = "matching_only"


class CandidateProfileCreate(CandidateProfileFields):
    user_id: int = Field(gt=0, le=18446744073709551615)


class CandidateProfileUpdate(CandidateProfileFields, Patch):
    pass


class CandidateProfileRead(CandidateProfileFields, Timestamps):
    model_config = {"from_attributes": True}
    user_id: int


class CandidateProfileDetailData(Read):
    candidate_profile: CandidateProfileRead


class CandidateProfileListData(Read):
    candidate_profiles: list[CandidateProfileRead]
    pagination: Pagination


CandidateProfileDetailResponse = ApiResponse[CandidateProfileDetailData]
CandidateProfileListResponse = ApiResponse[CandidateProfileListData]
