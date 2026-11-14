import unittest

from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.configs.settings import Settings
from app.main import app


class ConfigurationTests(unittest.TestCase):
    def test_cors_allows_frontend_origin(self):
        with TestClient(app) as client:
            response = client.options(
                "/api/v1/users",
                headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["access-control-allow-origin"], "http://localhost:5173")

    def test_cors_rejects_unknown_origin(self):
        with TestClient(app) as client:
            response = client.options(
                "/api/v1/users",
                headers={
                    "Origin": "https://unknown.example",
                    "Access-Control-Request-Method": "GET",
                },
            )
        self.assertEqual(response.status_code, 400)

    def test_settings_validate_database_port(self):
        with self.assertRaises(ValidationError):
            Settings(_env_file=None, db_port=0)

    def test_database_url_preserves_special_password_characters(self):
        settings = Settings(_env_file=None, db_password="p@ss:/word#?")
        self.assertEqual(settings.database_url.password, "p@ss:/word#?")
        self.assertEqual(settings.database_url.drivername, "mysql+pymysql")

    def test_development_disables_tls_explicitly(self):
        self.assertTrue(Settings(_env_file=None).db_ssl_disabled)
