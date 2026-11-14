import unittest

from fastapi.testclient import TestClient

from app.main import app

RESOURCES = (
    "users",
    "candidate-profiles",
    "company-profiles",
    "skills",
    "skill-aliases",
    "artifacts",
    "artifact-analyses",
    "artifact-contributions",
    "artifact-skill-evidences",
    "job-posts",
    "job-skill-requirements",
    "job-matches",
)


class CrudContractTests(unittest.TestCase):
    def test_all_resources_have_five_protected_operations(self):
        schema = app.openapi()
        with TestClient(app) as client:
            for resource in RESOURCES:
                with self.subTest(resource=resource):
                    path = f"/api/v1/{resource}"
                    self.assertIn(path, schema["paths"])
                    self.assertEqual(set(schema["paths"][path]), {"get", "post"})
                    detail = next(p for p in schema["paths"] if p.startswith(path + "/{"))
                    self.assertEqual(set(schema["paths"][detail]), {"get", "patch", "delete"})
                    response = client.get(path)
                    self.assertEqual(response.status_code, 401)
                    self.assertIn("authentication", response.json()["error"])

    def test_health_removed(self):
        with TestClient(app) as client:
            for path in ("/api/v1/health", "/api/v1/health/ready"):
                self.assertEqual(client.get(path).status_code, 404)

    def test_auth_endpoints_exist(self):
        paths = app.openapi()["paths"]
        for path in ("login", "me", "password"):
            self.assertIn(f"/api/v1/auth/{path}", paths)
