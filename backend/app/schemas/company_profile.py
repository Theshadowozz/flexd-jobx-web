from pydantic import Field

from app.schemas.common import Input, Patch, Read, Timestamps
from app.schemas.response import ApiResponse, Pagination


class CompanyProfileFields(Input):
    name: str = Field(min_length=1, max_length=180)
    industry: str | None = Field(default=None, max_length=120)
    description: str | None = Field(default=None, max_length=16000)
    logo_storage_key: str | None = Field(default=None, max_length=500)
    city: str | None = Field(default=None, max_length=120)
    province: str | None = Field(default=None, max_length=120)
    country: str = Field(default="Indonesia", min_length=1, max_length=100)


class CompanyProfileCreate(CompanyProfileFields):
    user_id: int = Field(gt=0, le=18446744073709551615)


class CompanyProfileUpdate(CompanyProfileFields, Patch):
    name: str | None = Field(default=None, min_length=1, max_length=180)


class CompanyProfileRead(CompanyProfileFields, Timestamps):
    model_config = {"from_attributes": True}
    id: int
    user_id: int


class CompanyProfileDetailData(Read):
    company_profile: CompanyProfileRead


class CompanyProfileListData(Read):
    company_profiles: list[CompanyProfileRead]
    pagination: Pagination


CompanyProfileDetailResponse = ApiResponse[CompanyProfileDetailData]
CompanyProfileListResponse = ApiResponse[CompanyProfileListData]
