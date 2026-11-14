from sqlalchemy.orm import Session

from app.configs.settings import get_settings
from app.models.user import User
from app.schemas.auth import Login, PasswordChange, TokenData, TokenResponse
from app.schemas.response import EmptyResponse
from app.schemas.user import UserDetailData, UserDetailResponse, UserRead
from app.services import auth_service


def login(payload: Login, db: Session) -> TokenResponse:
    user, token = auth_service.login(db, payload)
    return TokenResponse(
        message={"success": "Login berhasil"},
        data=TokenData(
            access_token=token,
            expires_in=get_settings().jwt_access_token_expire_minutes * 60,
            user=UserRead.model_validate(user),
        ),
    )


def me(user: User) -> UserDetailResponse:
    return UserDetailResponse(
        message={"success": "Akun berhasil diambil"},
        data=UserDetailData(user=UserRead.model_validate(user)),
    )


def password(payload: PasswordChange, db: Session, user: User) -> EmptyResponse:
    auth_service.change_password(db, user, payload)
    return EmptyResponse(message={"success": "Password berhasil diperbarui"}, data={})
