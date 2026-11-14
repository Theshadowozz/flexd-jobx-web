import jwt
import pytest

from app.configs.settings import get_settings
from app.utils.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hashes():
    hashed = hash_password("password-with-spaces  ")
    assert verify_password("password-with-spaces  ", hashed)
    assert not verify_password("password-with-spaces", hashed)
    assert not verify_password("example", "unknown-hash")


def test_expired_token():
    settings = get_settings()
    claims = jwt.decode(create_access_token(1), options={"verify_signature": False})
    claims["exp"] = 1
    expired = jwt.encode(claims, settings.jwt_secret_key.get_secret_value(), algorithm="HS256")
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(expired)
