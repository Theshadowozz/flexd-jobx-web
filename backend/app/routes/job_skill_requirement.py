from typing import Literal

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.configs.dependencies import require_admin
from app.controllers import job_skill_requirement_controller
from app.schemas.job_skill_requirement import (
    JobSkillRequirementCreate,
    JobSkillRequirementDetailResponse,
    JobSkillRequirementListResponse,
    JobSkillRequirementUpdate,
)
from app.schemas.response import EmptyResponse

router = APIRouter(
    prefix="/job-skill-requirements",
    tags=["Job skill requirements"],
    dependencies=[Depends(require_admin)],
)


@router.post("", response_model=JobSkillRequirementDetailResponse, status_code=201)
def create_job_skill_requirement(
    payload: JobSkillRequirementCreate,
    db: Session = Depends(get_db),
) -> JobSkillRequirementDetailResponse:
    return job_skill_requirement_controller.create_job_skill_requirement(db=db, payload=payload)


@router.get("", response_model=JobSkillRequirementListResponse, status_code=200)
def list_job_skill_requirements(
    db: Session = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    job_id: int | None = Query(default=None, gt=0, le=18446744073709551615),
    skill_id: int | None = Query(default=None, gt=0, le=18446744073709551615),
    requirement_type: Literal["must_have", "preferred"] | None = Query(default=None),
) -> JobSkillRequirementListResponse:
    return job_skill_requirement_controller.list_job_skill_requirements(
        db=db,
        offset=offset,
        limit=limit,
        job_id=job_id,
        skill_id=skill_id,
        requirement_type=requirement_type,
    )


@router.get(
    "/{job_skill_requirement_id}", response_model=JobSkillRequirementDetailResponse, status_code=200
)
def get_job_skill_requirement(
    job_skill_requirement_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> JobSkillRequirementDetailResponse:
    return job_skill_requirement_controller.get_job_skill_requirement(
        db=db, job_skill_requirement_id=job_skill_requirement_id
    )


@router.patch(
    "/{job_skill_requirement_id}", response_model=JobSkillRequirementDetailResponse, status_code=200
)
def update_job_skill_requirement(
    payload: JobSkillRequirementUpdate,
    job_skill_requirement_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> JobSkillRequirementDetailResponse:
    return job_skill_requirement_controller.update_job_skill_requirement(
        db=db, payload=payload, job_skill_requirement_id=job_skill_requirement_id
    )


@router.delete("/{job_skill_requirement_id}", response_model=EmptyResponse, status_code=200)
def delete_job_skill_requirement(
    job_skill_requirement_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> EmptyResponse:
    return job_skill_requirement_controller.delete_job_skill_requirement(
        db=db, job_skill_requirement_id=job_skill_requirement_id
    )
