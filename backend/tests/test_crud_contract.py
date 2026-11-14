import pytest


async def create(api, path, key, payload):
    response = await api.post(f"/api/v1/{path}", json=payload)
    assert response.status_code == 201, response.text
    body = response.json()
    assert set(body) == {"message", "error", "data"}
    assert set(body["data"]) == {key}
    return body["data"][key]


@pytest.mark.asyncio
async def test_all_twelve_crud_resources(api):
    user = await create(
        api,
        "users",
        "user",
        {
            "name": "New candidate",
            "email": "new@example.com",
            "password": "new-password-123",
            "account_type": "candidate",
        },
    )
    skill = await create(api, "skills", "skill", {"canonical_name": "React", "slug": "react"})
    artifact = await create(
        api,
        "artifacts",
        "artifact",
        {
            "owner_user_id": "2",
            "title": "Portfolio",
            "artifact_type": "document",
            "source_url": "https://example.com/work",
            "metadata": {"language": "id"},
        },
    )
    analysis = await create(
        api, "artifact-analyses", "artifact_analysis", {"artifact_id": artifact["id"]}
    )
    job = await create(
        api,
        "job-posts",
        "job_post",
        {
            "user_id": "3",
            "title": "Developer",
            "business_problem": "Build product",
            "employment_type": "full_time",
            "work_mode": "remote",
        },
    )
    cases = [
        ("users", "user", "users", user, {"name": "Updated candidate"}, "id"),
        ("skills", "skill", "skills", skill, {"description": "UI library"}, "id"),
        ("artifacts", "artifact", "artifacts", artifact, {"title": "Updated portfolio"}, "id"),
        (
            "artifact-analyses",
            "artifact_analysis",
            "artifact_analyses",
            analysis,
            {"analysis_status": "completed"},
            "id",
        ),
        ("job-posts", "job_post", "job_posts", job, {"title": "Senior developer"}, "id"),
    ]
    specs = [
        (
            "candidate-profiles",
            "candidate_profile",
            "candidate_profiles",
            {"user_id": "2"},
            {"headline": "Developer"},
            "user_id",
        ),
        (
            "company-profiles",
            "company_profile",
            "company_profiles",
            {"user_id": "3", "name": "Flexd"},
            {"name": "Flexd team"},
            "id",
        ),
        (
            "skill-aliases",
            "skill_alias",
            "skill_aliases",
            {"skill_id": skill["id"], "alias_name": "ReactJS"},
            {"alias_name": "React JS"},
            "id",
        ),
        (
            "artifact-contributions",
            "artifact_contribution",
            "artifact_contributions",
            {
                "artifact_id": artifact["id"],
                "contributor_user_id": "2",
                "contribution_description": "Built UI",
            },
            {"role_title": "Developer"},
            "id",
        ),
        (
            "artifact-skill-evidences",
            "artifact_skill_evidence",
            "artifact_skill_evidences",
            {
                "artifact_id": artifact["id"],
                "analysis_id": analysis["id"],
                "skill_id": skill["id"],
                "confidence_score": "0.9",
                "evidence_kind": "direct",
            },
            {"review_status": "reviewer_verified"},
            "id",
        ),
        (
            "job-skill-requirements",
            "job_skill_requirement",
            "job_skill_requirements",
            {"job_id": job["id"], "skill_id": skill["id"]},
            {"weight": "2.00"},
            "id",
        ),
        (
            "job-matches",
            "job_match",
            "job_matches",
            {
                "job_id": job["id"],
                "candidate_user_id": "2",
                "match_score": "85.50",
                "score_breakdown": {},
                "explanation": "Skills match",
            },
            {"explanation": "Updated explanation"},
            "id",
        ),
    ]
    for path, key, plural, payload, update, pk in specs:
        record = await create(api, path, key, payload)
        cases.append((path, key, plural, record, update, pk))

    for path, key, plural, record, update, pk in cases:
        assert isinstance(record[pk], str)
        detail = await api.get(f"/api/v1/{path}/{record[pk]}")
        assert detail.status_code == 200, detail.text
        assert set(detail.json()["data"]) == {key}
        listing = await api.get(f"/api/v1/{path}?limit=1&offset=0")
        assert listing.status_code == 200, listing.text
        assert set(listing.json()["data"]) == {plural, "pagination"}
        patched = await api.patch(f"/api/v1/{path}/{record[pk]}", json=update)
        assert patched.status_code == 200, patched.text
        assert set(patched.json()["data"]) == {key}
        assert "password_hash" not in patched.text

    # Delete dependents before parents; validates all twelve DELETE operations.
    order = [
        "job-matches",
        "job-skill-requirements",
        "artifact-skill-evidences",
        "artifact-contributions",
        "skill-aliases",
        "artifact-analyses",
        "artifacts",
        "job-posts",
        "candidate-profiles",
        "company-profiles",
        "skills",
        "users",
    ]
    for path in order:
        case = next(c for c in cases if c[0] == path)
        record_id = case[3][case[5]]
        deleted = await api.delete(f"/api/v1/{path}/{record_id}")
        assert deleted.status_code == 200, deleted.text
        assert deleted.json()["data"] == {}
        missing = await api.get(f"/api/v1/{path}/{record_id}")
        assert missing.status_code == 404
        assert missing.json()["data"] == {}
