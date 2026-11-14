from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field

from app.schemas.common import Input, Patch, Timestamps, UnsignedAmount, UnsignedId

Employment = Literal["full_time", "part_time", "contract", "internship", "freelance", "any"]
WorkMode = Literal["onsite", "hybrid", "remote", "any"]
Visibility = Literal["private", "matching_only", "public"]
Experience = Annotated[Decimal, Field(ge=0, max_digits=4, decimal_places=1)]


class CandidateProfileCreate(Input):
    user_id: UnsignedId
    headline: str | None = Field(default=None, max_length=180)
    biography: str | None = None
    city: str | None = Field(default=None, max_length=120)
    province: str | None = Field(default=None, max_length=120)
    country: str = Field(default="Indonesia", min_length=1, max_length=100)
    years_experience: Experience | None = None
    preferred_employment_type: Employment = "any"
    preferred_work_mode: WorkMode = "any"
    expected_salary_min: UnsignedAmount | None = None
    expected_salary_max: UnsignedAmount | None = None
    available_from: date | None = None
    profile_visibility: Visibility = "matching_only"


class CandidateProfileUpdate(Patch):
    headline: str | None = Field(default=None, max_length=180)
    biography: str | None = None
    city: str | None = Field(default=None, max_length=120)
    province: str | None = Field(default=None, max_length=120)
    country: str | None = Field(default=None, min_length=1, max_length=100)
    years_experience: Experience | None = None
    preferred_employment_type: Employment | None = None
    preferred_work_mode: WorkMode | None = None
    expected_salary_min: UnsignedAmount | None = None
    expected_salary_max: UnsignedAmount | None = None
    available_from: date | None = None
    profile_visibility: Visibility | None = None


class CandidateProfileRead(Timestamps):
    user_id: UnsignedId
    headline: str | None
    biography: str | None
    city: str | None
    province: str | None
    country: str
    years_experience: Decimal | None
    preferred_employment_type: str
    preferred_work_mode: str
    expected_salary_min: UnsignedAmount | None
    expected_salary_max: UnsignedAmount | None
    available_from: date | None
    profile_visibility: str
