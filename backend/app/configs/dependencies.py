from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.models.user import User
from app.utils.exceptions import AppError
from app.utils.security import decode_token

bearer = HTTPBearer(auto_error=False)


def current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> User:
    if credentials is None:
        raise AppError(
            401,
            "authentication",
            {"token": "Autentikasi diperlukan"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.get(User, decode_token(credentials.credentials))
    if user is None or user.account_status != "active":
        raise AppError(
            401,
            "authentication",
            {"token": "Akun tidak tersedia atau tidak aktif"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_admin(user: User = Depends(current_user)) -> User:
    if user.account_type != "admin":
        raise AppError(403, "authorization", {"permission": "Akses hanya untuk admin"})
    return user
