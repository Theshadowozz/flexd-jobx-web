from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.configs.settings import get_settings
from app.utils.exceptions import AppError

hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return hasher.hash(password)


def verify_password(password: str, encoded: str) -> bool:
    try:
        return hasher.verify(encoded, password)
    except (VerificationError, InvalidHashError):
        return False


def jwt_settings():
    settings = get_settings()
    if len(settings.jwt_secret_key.get_secret_value().encode()) < 32:
        raise AppError(503, "service_unavailable", {"authentication": "JWT belum dikonfigurasi"})
    return settings


def create_token(user_id: int) -> str:
    settings = jwt_settings()
    now = datetime.now(UTC)
    return jwt.encode(
        {
            "sub": str(user_id),
            "iat": now,
            "exp": now + timedelta(minutes=settings.jwt_access_token_expire_minutes),
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
        },
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str) -> int:
    settings = jwt_settings()
    try:
        claims = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            options={"require": ["sub", "exp", "iat", "iss", "aud"]},
        )
        subject = claims["sub"]
        if not isinstance(subject, str) or not subject.isdecimal():
            raise ValueError("Invalid subject")
        user_id = int(subject)
        if not 0 < user_id <= 18446744073709551615:
            raise ValueError("Invalid subject")
        return user_id
    except (jwt.InvalidTokenError, ValueError) as exc:
        raise AppError(
            401,
            "authentication",
            {"token": "Token tidak valid atau kedaluwarsa"},
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
