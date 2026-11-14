from datetime import UTC, datetime, timedelta
from functools import lru_cache
from uuid import uuid4

import jwt
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

from app.configs.settings import get_settings

password_hash = PasswordHash.recommended()


@lru_cache
def dummy_hash() -> str:
    return password_hash.hash(uuid4().hex)


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return password_hash.verify(password, hashed)
    except (ValueError, TypeError, UnknownHashError):
        return False


def create_access_token(user_id: int) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    return jwt.encode(
        {
            "sub": str(user_id),
            "iat": now,
            "exp": now + timedelta(minutes=settings.jwt_access_token_expire_minutes),
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
            "jti": uuid4().hex,
        },
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> int:
    settings = get_settings()
    payload = jwt.decode(
        token,
        settings.jwt_secret_key.get_secret_value(),
        algorithms=[settings.jwt_algorithm],
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
        options={"require": ["sub", "iat", "exp", "iss", "aud", "jti"]},
    )
    user_id = int(payload["sub"])
    if not 0 < user_id <= 18_446_744_073_709_551_615:
        raise ValueError("Invalid subject")
    return user_id
