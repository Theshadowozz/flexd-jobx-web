from tests.test_crud_contract import create


async def test_last_admin_protection(api):
    for payload in ({"account_status": "inactive"}, {"account_type": "candidate"}):
        assert (await api.patch("/api/v1/users/1", json=payload)).status_code == 409
    assert (await api.delete("/api/v1/users/1")).status_code == 409


async def test_skill_cycle_duplicate_alias_and_null(api):
    first = await create(api, "skills", "skill", {"canonical_name": "UI", "slug": "ui"})
    second = await create(
        api,
        "skills",
        "skill",
        {"canonical_name": "React", "slug": "react", "parent_skill_id": first["id"]},
    )
    cycle = await api.patch(f"/api/v1/skills/{first['id']}", json={"parent_skill_id": second["id"]})
    assert cycle.status_code == 422
    await create(
        api, "skill-aliases", "skill_alias", {"skill_id": first["id"], "alias_name": "ReactJS"}
    )
    duplicate = await api.post(
        "/api/v1/skill-aliases", json={"skill_id": first["id"], "alias_name": "reactjs"}
    )
    assert duplicate.status_code == 409
    assert (
        await api.patch(f"/api/v1/skills/{first['id']}", json={"canonical_name": None})
    ).status_code == 422
    assert (await api.patch(f"/api/v1/skills/{first['id']}", json={})).status_code == 422
    assert (await api.get("/api/v1/skills?limit=101")).status_code == 422


async def test_foreign_keys_ranges_and_artifact_consistency(api):
    assert (await api.post("/api/v1/candidate-profiles", json={"user_id": "3"})).status_code == 422
    assert (
        await api.post(
            "/api/v1/candidate-profiles",
            json={"user_id": "2", "expected_salary_min": "100", "expected_salary_max": "50"},
        )
    ).status_code == 422
    artifact_payload = {"owner_user_id": "2", "title": "Work", "artifact_type": "document"}
    assert (await api.post("/api/v1/artifacts", json=artifact_payload)).status_code == 422
    first = await create(
        api, "artifacts", "artifact", {**artifact_payload, "storage_key": "jobx/first.pdf"}
    )
    second = await create(
        api, "artifacts", "artifact", {**artifact_payload, "storage_key": "jobx/second.pdf"}
    )
    analysis = await create(
        api, "artifact-analyses", "artifact_analysis", {"artifact_id": first["id"]}
    )
    skill = await create(api, "skills", "skill", {"canonical_name": "Python", "slug": "python"})
    evidence = {
        "artifact_id": second["id"],
        "analysis_id": analysis["id"],
        "skill_id": skill["id"],
        "confidence_score": "0.8",
        "evidence_kind": "direct",
    }
    assert (await api.post("/api/v1/artifact-skill-evidences", json=evidence)).status_code == 422
    assert (
        await api.patch(f"/api/v1/artifacts/{first['id']}", json={"storage_key": None})
    ).status_code == 422
    assert (
        await api.post("/api/v1/skill-aliases", json={"skill_id": "999", "alias_name": "Missing"})
    ).status_code == 422


async def test_delete_cascade_and_restrict(api):
    skill = await create(api, "skills", "skill", {"canonical_name": "Python", "slug": "python"})
    alias = await create(
        api, "skill-aliases", "skill_alias", {"skill_id": skill["id"], "alias_name": "Py"}
    )
    assert (await api.delete(f"/api/v1/skills/{skill['id']}")).status_code == 200
    assert (await api.get(f"/api/v1/skill-aliases/{alias['id']}")).status_code == 404
    await create(
        api,
        "job-posts",
        "job_post",
        {
            "user_id": "3",
            "title": "Developer",
            "business_problem": "Build",
            "employment_type": "full_time",
            "work_mode": "remote",
        },
    )
    assert (await api.delete("/api/v1/users/3")).status_code == 409
