import pytest

from app.utils.security import create_access_token

RESOURCES = [
    "users",
    "candidate-profiles",
    "company-profiles",
    "artifacts",
    "artifact-analyses",
    "artifact-contributions",
    "artifact-skill-evidences",
    "skills",
    "skill-aliases",
    "job-posts",
    "job-skill-requirements",
    "job-matches",
]


@pytest.mark.parametrize("resource", RESOURCES)
async def test_all_resource_operations_require_admin(api, resource):
    api.headers["Authorization"] = f"Bearer {create_access_token(2)}"
    for method, suffix, payload in [
        ("GET", "", None),
        ("GET", "/1", None),
        ("POST", "", {}),
        ("PATCH", "/1", {}),
        ("DELETE", "/1", None),
    ]:
        response = await api.request(method, f"/api/v1/{resource}{suffix}", json=payload)
        assert response.status_code == 403, response.text
        assert response.json()["data"] == {}
