from typing import Literal

from pydantic import EmailStr, Field

from app.schemas.common import Input, Password, Patch, Timestamps, UnsignedId


class UserCreate(Input):
    name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    password: Password
    account_type: Literal["candidate", "employer", "admin"]
    account_status: Literal["active", "inactive"] = "active"


class UserUpdate(Patch):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    email: EmailStr | None = None
    password: Password | None = None
    account_type: Literal["candidate", "employer", "admin"] | None = None
    account_status: Literal["active", "inactive"] | None = None


class UserRead(Timestamps):
    id: UnsignedId
    name: str
    email: str
    account_type: str
    account_status: str
