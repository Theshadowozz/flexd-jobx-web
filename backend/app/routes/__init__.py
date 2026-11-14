from fastapi import APIRouter

from app.routes import (
    artifact,
    artifact_analysis,
    artifact_contribution,
    artifact_skill_evidence,
    auth,
    candidate_profile,
    company_profile,
    job_match,
    job_post,
    job_skill_requirement,
    skill,
    skill_alias,
    user,
)

router = APIRouter(prefix="/api/v1")
for resource in (
    auth,
    user,
    skill,
    skill_alias,
    candidate_profile,
    company_profile,
    artifact,
    artifact_analysis,
    artifact_contribution,
    artifact_skill_evidence,
    job_post,
    job_skill_requirement,
    job_match,
):
    router.include_router(resource.router)
