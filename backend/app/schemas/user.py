from datetime import datetime
from typing import Literal

from pydantic import EmailStr, Field, SecretStr

from app.schemas.common import Input, Patch, Read
from app.schemas.response import ApiResponse, Pagination

AccountType = Literal["candidate", "employer", "admin"]
AccountStatus = Literal["active", "inactive"]


class UserCreate(Input):
    name: str = Field(min_length=1, max_length=150)
    email: EmailStr = Field(max_length=255)
    password: SecretStr = Field(min_length=12, max_length=256)
    account_type: AccountType
    account_status: AccountStatus = "active"


class UserUpdate(Patch):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    email: EmailStr | None = Field(default=None, max_length=255)
    account_type: AccountType | None = None
    account_status: AccountStatus | None = None


class UserRead(Read):
    id: int
    name: str
    email: str
    account_type: AccountType
    account_status: AccountStatus
    created_at: datetime
    updated_at: datetime


class UserDetailData(Read):
    user: UserRead


class UserListData(Read):
    users: list[UserRead]
    pagination: Pagination


UserDetailResponse = ApiResponse[UserDetailData]
UserListResponse = ApiResponse[UserListData]
