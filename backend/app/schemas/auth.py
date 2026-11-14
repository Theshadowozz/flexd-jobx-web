from pydantic import EmailStr, Field, SecretStr

from app.schemas.common import Input, Read
from app.schemas.response import ApiResponse
from app.schemas.user import UserRead


class Login(Input):
    email: EmailStr = Field(max_length=255)
    password: SecretStr = Field(min_length=1, max_length=256)


class PasswordChange(Input):
    current_password: SecretStr = Field(min_length=1, max_length=256)
    new_password: SecretStr = Field(min_length=12, max_length=256)


class TokenData(Read):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserRead


TokenResponse = ApiResponse[TokenData]
