from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.configs.database import get_db
from app.models.user import User
from app.utils.exceptions import AppError
from app.utils.security import decode_access_token

bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    error = AppError(401, "Authentication failed", {"auth": "Valid access token required"})
    if credentials is None:
        raise error
    try:
        user_id = decode_access_token(credentials.credentials)
    except (InvalidTokenError, ValueError, TypeError) as exc:
        raise error from exc
    user = await db.get(User, user_id)
    if user is None or user.account_status != "active":
        raise error
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.account_type != "admin":
        raise AppError(403, "Access denied", {"auth": "Admin access required"})
    return user
