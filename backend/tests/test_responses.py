import os
import unittest
from unittest.mock import patch

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from app.configs.settings import Settings
from app.utils.exceptions import register_exception_handlers


class Payload(BaseModel):
    name: str = Field(min_length=1)


class ResponseTests(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI(debug=False)
        register_exception_handlers(self.app)

        @self.app.post("/items")
        def create(payload: Payload):
            return payload

        @self.app.get("/auth")
        def auth():
            raise HTTPException(401, "private detail", headers={"WWW-Authenticate": "Bearer"})

        @self.app.get("/broken")
        def broken():
            raise RuntimeError("secret password")

    def test_validation_uses_field_errors_without_input(self):
        with TestClient(self.app) as client:
            response = client.post("/items", json={})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"], {"validation": {"name": "Field wajib diisi"}})
        self.assertEqual(response.json()["data"], {})

    def test_invalid_json_does_not_echo_input(self):
        with TestClient(self.app) as client:
            response = client.post(
                "/items", content='{"secret":', headers={"Content-Type": "application/json"}
            )
        self.assertEqual(response.status_code, 400)
        self.assertNotIn("secret", response.text)

    def test_auth_preserves_challenge_header(self):
        with TestClient(self.app) as client:
            response = client.get("/auth")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.headers["www-authenticate"], "Bearer")
        self.assertNotIn("private detail", response.text)

    def test_unknown_route_and_method_use_envelope(self):
        with TestClient(self.app) as client:
            for response in (client.get("/missing"), client.get("/items")):
                self.assertIn(response.status_code, (404, 405))
                self.assertEqual(set(response.json()), {"message", "error", "data"})

    def test_unhandled_error_is_sanitized(self):
        with TestClient(self.app, raise_server_exceptions=False) as client:
            response = client.get("/broken")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json()["error"], {"internal": {"server": "Request tidak dapat diproses"}}
        )
        self.assertNotIn("secret", response.text)

    def test_environment_prefixes_are_loaded(self):
        with patch.dict(
            os.environ,
            {
                "APP_CORS_ORIGINS": '["https://frontend.example"]',
                "STORAGE_ACL": "false",
                "STORAGE_SECRET": "storage-secret",
                "JWT_SECRET_KEY": "jwt-secret",
                "LLM_API_KEY": "llm-secret",
                "LLM_BASE_URL": "https://api.example/v1",
            },
        ):
            settings = Settings(_env_file=None)
        self.assertEqual(settings.app_cors_origins, ["https://frontend.example"])
        self.assertFalse(settings.storage_acl)
        for secret in ("storage-secret", "jwt-secret", "llm-secret"):
            self.assertNotIn(secret, repr(settings))
