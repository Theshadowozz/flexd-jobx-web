import os
import unittest
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import jwt

from app.configs.settings import get_settings
from app.services.auth_service import _attempts, check_rate_limit
from app.utils.exceptions import AppError
from app.utils.security import create_token, decode_token, hash_password, verify_password


class SecurityTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"JWT_SECRET_KEY": "test-key-" * 8})
        self.env.start()
        get_settings.cache_clear()

    def tearDown(self):
        self.env.stop()
        get_settings.cache_clear()
        _attempts.clear()

    def test_argon2_hash_and_invalid_legacy_hash(self):
        encoded = hash_password("my-test-password")
        self.assertTrue(encoded.startswith("$argon2id$"))
        self.assertTrue(verify_password("my-test-password", encoded))
        self.assertFalse(verify_password("wrong", encoded))
        self.assertFalse(verify_password("wrong", "unknown-legacy-format"))

    def test_roundtrip_and_missing_secret_fail_closed(self):
        self.assertEqual(decode_token(create_token(123)), 123)
        with patch.dict(os.environ, {"JWT_SECRET_KEY": ""}):
            get_settings.cache_clear()
            with self.assertRaises(AppError) as result:
                create_token(123)
            self.assertEqual(result.exception.status_code, 503)

    def test_expired_wrong_issuer_audience_algorithm_and_missing_claims(self):
        settings = get_settings()
        now = datetime.now(UTC)
        claims = {
            "sub": "1",
            "iat": now,
            "exp": now + timedelta(minutes=1),
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
        }
        variants = [
            ({**claims, "exp": now - timedelta(seconds=1)}, "HS256"),
            ({**claims, "iss": "other"}, "HS256"),
            ({**claims, "aud": "other"}, "HS256"),
            ({**claims, "sub": "0"}, "HS256"),
            ({k: v for k, v in claims.items() if k != "exp"}, "HS256"),
            (claims, "HS384"),
        ]
        for payload, algorithm in variants:
            token = jwt.encode(
                payload, settings.jwt_secret_key.get_secret_value(), algorithm=algorithm
            )
            with self.subTest(payload=payload), self.assertRaises(AppError) as result:
                decode_token(token)
            self.assertEqual(result.exception.status_code, 401)

    def test_login_rate_limit_and_retry_header(self):
        _attempts.clear()
        for _ in range(10):
            check_rate_limit("test-client")
        with self.assertRaises(AppError) as result:
            check_rate_limit("test-client")
        self.assertEqual(result.exception.status_code, 429)
        self.assertIn("Retry-After", result.exception.headers)
