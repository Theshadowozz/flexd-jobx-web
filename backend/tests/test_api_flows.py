import importlib
import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import BigInteger, Integer, create_engine, event
from sqlalchemy.dialects.mysql import DATETIME, JSON, LONGTEXT
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.configs.database import get_db
from app.configs.settings import get_settings
from app.main import app
from app.models import User
from app.models.base import Base
from app.services.auth_service import _attempts
from app.utils.security import hash_password


@compiles(DATETIME, "sqlite")
def sqlite_datetime(element, compiler, **kw):
    return "DATETIME"


@compiles(JSON, "sqlite")
def sqlite_json(element, compiler, **kw):
    return "JSON"


@compiles(LONGTEXT, "sqlite")
def sqlite_longtext(element, compiler, **kw):
    return "TEXT"


class ApiFlowTests(unittest.TestCase):
    """Portable functional tests; not a substitute for MySQL integration tests."""

    @classmethod
    def setUpClass(cls):
        cls.types = []
        for table in Base.metadata.tables.values():
            for column in table.columns:
                if isinstance(column.type, BigInteger):
                    cls.types.append((column, column.type))
                    column.type = column.type.with_variant(Integer(), "sqlite")

    @classmethod
    def tearDownClass(cls):
        for column, original in cls.types:
            column.type = original

    def setUp(self):
        self.env = patch.dict(os.environ, {"JWT_SECRET_KEY": "x" * 48})
        self.env.start()
        get_settings.cache_clear()
        _attempts.clear()
        self.engine = create_engine(
            "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
        )

        @event.listens_for(self.engine, "connect")
        def enable_fk(connection, record):
            connection.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(self.engine)
        with Session(self.engine) as db:
            db.add(
                User(
                    id=1,
                    name="Admin",
                    email="admin@example.com",
                    account_type="admin",
                    account_status="active",
                    password_hash=hash_password("valid-password-123"),
                )
            )
            db.commit()

        def database():
            with Session(self.engine) as db:
                yield db

        app.dependency_overrides[get_db] = database
        self.client = TestClient(app)
        self.client.__enter__()
        login = self.client.post(
            "/api/v1/auth/login",
            json={"email": "admin@example.com", "password": "valid-password-123"},
        )
        self.assertEqual(login.status_code, 200, login.text)
        self.headers = {"Authorization": "Bearer " + login.json()["data"]["access_token"]}

    def tearDown(self):
        self.client.__exit__(None, None, None)
        app.dependency_overrides.clear()
        self.engine.dispose()
        self.env.stop()
        get_settings.cache_clear()

    def request(self, method, path, **kwargs):
        return self.client.request(method, "/api/v1/" + path, headers=self.headers, **kwargs)

    def create(self, resource, key, payload):
        response = self.request("POST", resource, json=payload)
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()["data"][key]

    def fixtures(self):
        candidate = self.create(
            "users",
            "user",
            {
                "name": "Candidate",
                "email": "c@example.com",
                "password": "candidate-password",
                "account_type": "candidate",
            },
        )
        employer = self.create(
            "users",
            "user",
            {
                "name": "Employer",
                "email": "e@example.com",
                "password": "employer-password",
                "account_type": "employer",
            },
        )
        skill = self.create("skills", "skill", {"canonical_name": "Python", "slug": "python"})
        artifact = self.create(
            "artifacts",
            "artifact",
            {
                "owner_user_id": candidate["id"],
                "title": "Project",
                "artifact_type": "document",
                "storage_key": "jobx/test.pdf",
                "metadata": {"source": "test"},
            },
        )
        analysis = self.create(
            "artifact-analyses", "artifact_analysis", {"artifact_id": artifact["id"]}
        )
        job = self.create(
            "job-posts",
            "job_post",
            {
                "user_id": employer["id"],
                "title": "Engineer",
                "business_problem": "Build API",
                "employment_type": "full_time",
                "work_mode": "remote",
            },
        )
        return candidate, employer, skill, artifact, analysis, job

    def test_crud_for_all_twelve_resources(self):
        c, e, s, a, analysis, job = self.fixtures()
        entries = [
            ("users", "user", "users", c["id"], {"name": "Changed"}),
            ("skills", "skill", "skills", s["id"], {"description": "Changed"}),
            ("artifacts", "artifact", "artifacts", a["id"], {"title": "Changed"}),
            (
                "artifact-analyses",
                "artifact_analysis",
                "artifact_analyses",
                analysis["id"],
                {"extracted_summary": "Changed"},
            ),
            ("job-posts", "job_post", "job_posts", job["id"], {"title": "Changed"}),
        ]
        specs = [
            (
                "candidate-profiles",
                "candidate_profile",
                "candidate_profiles",
                {"user_id": c["id"]},
                {"headline": "Changed"},
            ),
            (
                "company-profiles",
                "company_profile",
                "company_profiles",
                {"user_id": e["id"], "name": "Company"},
                {"description": "Changed"},
            ),
            (
                "skill-aliases",
                "skill_alias",
                "skill_aliases",
                {"skill_id": s["id"], "alias_name": "Py", "normalized_alias": "py"},
                {"alias_name": "PY"},
            ),
            (
                "artifact-contributions",
                "artifact_contribution",
                "artifact_contributions",
                {
                    "artifact_id": a["id"],
                    "contributor_user_id": c["id"],
                    "contribution_description": "Built API",
                },
                {"role_title": "Engineer"},
            ),
            (
                "artifact-skill-evidences",
                "artifact_skill_evidence",
                "artifact_skill_evidences",
                {
                    "artifact_id": a["id"],
                    "analysis_id": analysis["id"],
                    "skill_id": s["id"],
                    "confidence_score": "0.9000",
                    "evidence_kind": "direct",
                },
                {"evidence_excerpt": "Python"},
            ),
            (
                "job-skill-requirements",
                "job_skill_requirement",
                "job_skill_requirements",
                {"job_id": job["id"], "skill_id": s["id"]},
                {"weight": "2.00"},
            ),
            (
                "job-matches",
                "job_match",
                "job_matches",
                {
                    "job_id": job["id"],
                    "candidate_user_id": c["id"],
                    "match_score": "90.00",
                    "score_breakdown": {},
                    "explanation": "Strong match",
                },
                {"explanation": "Changed"},
            ),
        ]
        for resource, single, plural, payload, changes in specs:
            record = self.create(resource, single, payload)
            entries.append(
                (resource, single, plural, record.get("id", record.get("user_id")), changes)
            )
        for resource, single, plural, record_id, changes in entries:
            with self.subTest(resource=resource):
                detail = self.request("GET", f"{resource}/{record_id}")
                self.assertEqual(detail.status_code, 200, detail.text)
                self.assertIn(single, detail.json()["data"])
                listed = self.request("GET", resource)
                self.assertEqual(listed.status_code, 200, listed.text)
                self.assertGreaterEqual(listed.json()["data"]["pagination"]["total"], 1)
                self.assertIn(plural, listed.json()["data"])
                changed = self.request("PATCH", f"{resource}/{record_id}", json=changes)
                self.assertEqual(changed.status_code, 200, changed.text)
                for field, value in changes.items():
                    self.assertEqual(changed.json()["data"][single][field], value)
        # Children before parents to exercise explicit deletes without invalidating fixtures.
        for index in (11, 10, 9, 8, 7, 6, 5, 3, 2, 4, 1, 0):
            resource, _, _, record_id, _ = entries[index]
            deleted = self.request("DELETE", f"{resource}/{record_id}")
            self.assertEqual(deleted.status_code, 200, deleted.text)
            self.assertEqual(deleted.json()["data"], {})
            self.assertEqual(self.request("GET", f"{resource}/{record_id}").status_code, 404)

    def test_passwords_never_leak_and_candidate_cannot_use_admin_crud(self):
        c, *_ = self.fixtures()
        body = self.request("GET", "users").text
        self.assertNotIn("password", body)
        result = self.client.post(
            "/api/v1/auth/login", json={"email": "c@example.com", "password": "candidate-password"}
        )
        token = result.json()["data"]["access_token"]
        result = self.client.get("/api/v1/users", headers={"Authorization": "Bearer " + token})
        self.assertEqual(result.status_code, 403)
        self.assertEqual(
            self.request("PATCH", "users/1", json={"account_status": "inactive"}).status_code, 409
        )

    def test_validation_conflicts_and_rollback(self):
        c, e, s, a, analysis, job = self.fixtures()
        for payload in ({}, {"id": 9}, {"slug": None}):
            self.assertEqual(
                self.request("PATCH", f"skills/{s['id']}", json=payload).status_code, 422
            )
        duplicate = self.request(
            "POST", "skills", json={"canonical_name": "Other", "slug": "python"}
        )
        self.assertEqual(duplicate.status_code, 409)
        self.assertEqual(self.request("GET", "skills").json()["data"]["pagination"]["total"], 1)
        invalid = self.request("POST", "candidate-profiles", json={"user_id": e["id"]})
        self.assertEqual(invalid.status_code, 422)
        self.assertEqual(
            self.request(
                "POST",
                "skill-aliases",
                json={"skill_id": 999, "alias_name": "x", "normalized_alias": "x"},
            ).status_code,
            422,
        )
        child = self.create(
            "skills",
            "skill",
            {"canonical_name": "Child", "slug": "child", "parent_skill_id": s["id"]},
        )
        self.assertEqual(
            self.request(
                "PATCH", f"skills/{s['id']}", json={"parent_skill_id": child["id"]}
            ).status_code,
            422,
        )
        self.create(
            "candidate-profiles",
            "candidate_profile",
            {"user_id": c["id"], "expected_salary_min": 10, "expected_salary_max": 20},
        )
        self.assertEqual(
            self.request(
                "PATCH", f"candidate-profiles/{c['id']}", json={"expected_salary_min": 30}
            ).status_code,
            422,
        )
        self.assertEqual(
            self.request("PATCH", f"artifacts/{a['id']}", json={"storage_key": None}).status_code,
            422,
        )
        self.assertEqual(
            self.request(
                "PATCH", f"job-posts/{job['id']}", json={"publication_status": "published"}
            ).status_code,
            409,
        )

    def test_evidence_cannot_reference_different_artifact(self):
        c, _, s, a, analysis, _ = self.fixtures()
        other = self.create(
            "artifacts",
            "artifact",
            {
                "owner_user_id": c["id"],
                "title": "Other",
                "artifact_type": "document",
                "source_url": "https://example.com",
            },
        )
        response = self.request(
            "POST",
            "artifact-skill-evidences",
            json={
                "artifact_id": other["id"],
                "analysis_id": analysis["id"],
                "skill_id": s["id"],
                "confidence_score": "1.0",
                "evidence_kind": "direct",
            },
        )
        self.assertEqual(response.status_code, 422)

    def test_match_decisions_derive_status_and_timestamps(self):
        c, _, _, _, _, job = self.fixtures()
        record = self.create(
            "job-matches",
            "job_match",
            {
                "job_id": job["id"],
                "candidate_user_id": c["id"],
                "match_score": "80",
                "score_breakdown": {},
                "explanation": "Match",
            },
        )
        path = f"job-matches/{record['id']}"
        result = self.request("PATCH", path, json={"candidate_decision": "accepted"})
        self.assertEqual(result.status_code, 200, result.text)
        self.assertEqual(result.json()["data"]["job_match"]["match_status"], "one_side_interested")
        self.assertIsNotNone(result.json()["data"]["job_match"]["candidate_decided_at"])
        result = self.request("PATCH", path, json={"employer_decision": "accepted"})
        self.assertEqual(result.json()["data"]["job_match"]["match_status"], "mutually_accepted")

    def test_password_change_and_token_validation(self):
        response = self.request(
            "PATCH",
            "auth/password",
            json={
                "current_password": "valid-password-123",
                "new_password": "new-valid-password-123",
            },
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(
            self.client.post(
                "/api/v1/auth/login",
                json={"email": "admin@example.com", "password": "valid-password-123"},
            ).status_code,
            401,
        )
        self.assertEqual(
            self.client.get(
                "/api/v1/auth/me", headers={"Authorization": "Bearer invalid"}
            ).status_code,
            401,
        )

    def test_schema_patch_rejects_empty_for_every_resource(self):
        for name in (
            "user",
            "skill",
            "skill_alias",
            "candidate_profile",
            "company_profile",
            "artifact",
            "artifact_analysis",
            "artifact_contribution",
            "artifact_skill_evidence",
            "job_post",
            "job_skill_requirement",
            "job_match",
        ):
            module = importlib.import_module("app.schemas." + name)
            schema = getattr(module, "".join(part.title() for part in name.split("_")) + "Update")
            with self.subTest(name=name), self.assertRaises(ValueError):
                schema.model_validate({})

    def test_inactive_account_rejected_for_login_and_existing_token(self):
        self.fixtures()
        login = self.client.post(
            "/api/v1/auth/login", json={"email": "c@example.com", "password": "candidate-password"}
        )
        token = login.json()["data"]["access_token"]
        candidate_id = login.json()["data"]["user"]["id"]
        changed = self.request(
            "PATCH", f"users/{candidate_id}", json={"account_status": "inactive"}
        )
        self.assertEqual(changed.status_code, 200, changed.text)
        self.assertEqual(
            self.client.get(
                "/api/v1/auth/me", headers={"Authorization": "Bearer " + token}
            ).status_code,
            401,
        )
        self.assertEqual(
            self.client.post(
                "/api/v1/auth/login",
                json={"email": "c@example.com", "password": "candidate-password"},
            ).status_code,
            401,
        )

    def test_pagination_filters_and_metadata_output(self):
        _, _, _, artifact, _, _ = self.fixtures()
        self.assertEqual(artifact["metadata"], {"source": "test"})
        body = self.request("GET", "users?account_type=candidate&limit=1").json()["data"]
        self.assertEqual(body["pagination"], {"offset": 0, "limit": 1, "total": 1})
        self.assertEqual(body["users"][0]["account_type"], "candidate")
        self.assertEqual(self.request("GET", "users?limit=101").status_code, 422)
        self.assertEqual(self.request("GET", "users?offset=-1").status_code, 422)
        self.assertEqual(self.request("GET", "users?offset=100").json()["data"]["users"], [])
