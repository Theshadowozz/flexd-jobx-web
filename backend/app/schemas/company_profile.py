from pydantic import Field

from app.schemas.common import Input, Patch, Timestamps, UnsignedId


class CompanyProfileCreate(Input):
    user_id: UnsignedId
    name: str = Field(min_length=1, max_length=180)
    industry: str | None = Field(default=None, max_length=120)
    description: str | None = None
    logo_storage_key: str | None = Field(default=None, max_length=500)
    city: str | None = Field(default=None, max_length=120)
    province: str | None = Field(default=None, max_length=120)
    country: str = Field(default="Indonesia", min_length=1, max_length=100)


class CompanyProfileUpdate(Patch):
    name: str | None = Field(default=None, min_length=1, max_length=180)
    industry: str | None = Field(default=None, max_length=120)
    description: str | None = None
    logo_storage_key: str | None = Field(default=None, max_length=500)
    city: str | None = Field(default=None, max_length=120)
    province: str | None = Field(default=None, max_length=120)
    country: str | None = Field(default=None, min_length=1, max_length=100)


class CompanyProfileRead(Timestamps):
    id: UnsignedId
    user_id: UnsignedId
    name: str
    industry: str | None
    description: str | None
    logo_storage_key: str | None
    city: str | None
    province: str | None
    country: str
