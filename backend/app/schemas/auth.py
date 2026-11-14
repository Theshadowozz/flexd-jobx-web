from typing import Literal

from pydantic import EmailStr, Field

from app.schemas.common import Input, Password


class Register(Input):
    name: str = Field(min_length=1, max_length=150, pattern=r"\S")
    email: EmailStr
    password: Password
    account_type: Literal["candidate", "employer"]


class Login(Input):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class ChangePassword(Input):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: Password
