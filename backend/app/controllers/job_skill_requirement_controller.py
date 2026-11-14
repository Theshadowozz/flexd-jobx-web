from typing import Literal

from sqlalchemy.orm import Session

from app.schemas.job_skill_requirement import (
    JobSkillRequirementCreate,
    JobSkillRequirementDetailData,
    JobSkillRequirementDetailResponse,
    JobSkillRequirementListData,
    JobSkillRequirementListResponse,
    JobSkillRequirementRead,
    JobSkillRequirementUpdate,
)
from app.schemas.response import EmptyResponse, Pagination
from app.services import job_skill_requirement_service


def create_job_skill_requirement(
    db: Session, payload: JobSkillRequirementCreate
) -> JobSkillRequirementDetailResponse:
    job_skill_requirement = job_skill_requirement_service.create_job_skill_requirement(
        db=db, payload=payload
    )
    job_skill_requirement_data = JobSkillRequirementRead.model_validate(job_skill_requirement)
    return JobSkillRequirementDetailResponse(
        message={"success": "Data berhasil dibuat"},
        data=JobSkillRequirementDetailData(job_skill_requirement=job_skill_requirement_data),
    )


def get_job_skill_requirement(
    db: Session, job_skill_requirement_id: int
) -> JobSkillRequirementDetailResponse:
    job_skill_requirement = job_skill_requirement_service.get_job_skill_requirement(
        db=db, job_skill_requirement_id=job_skill_requirement_id
    )
    job_skill_requirement_data = JobSkillRequirementRead.model_validate(job_skill_requirement)
    return JobSkillRequirementDetailResponse(
        message={"success": "Data berhasil diambil"},
        data=JobSkillRequirementDetailData(job_skill_requirement=job_skill_requirement_data),
    )


def update_job_skill_requirement(
    db: Session, job_skill_requirement_id: int, payload: JobSkillRequirementUpdate
) -> JobSkillRequirementDetailResponse:
    job_skill_requirement = job_skill_requirement_service.update_job_skill_requirement(
        db=db, job_skill_requirement_id=job_skill_requirement_id, payload=payload
    )
    job_skill_requirement_data = JobSkillRequirementRead.model_validate(job_skill_requirement)
    return JobSkillRequirementDetailResponse(
        message={"success": "Data berhasil diperbarui"},
        data=JobSkillRequirementDetailData(job_skill_requirement=job_skill_requirement_data),
    )


def list_job_skill_requirements(
    db: Session,
    offset: int,
    limit: int,
    job_id: int | None = None,
    skill_id: int | None = None,
    requirement_type: Literal["must_have", "preferred"] | None = None,
) -> JobSkillRequirementListResponse:
    records, total = job_skill_requirement_service.list_job_skill_requirements(
        db=db,
        offset=offset,
        limit=limit,
        job_id=job_id,
        skill_id=skill_id,
        requirement_type=requirement_type,
    )
    items = [JobSkillRequirementRead.model_validate(record) for record in records]
    return JobSkillRequirementListResponse(
        message={"success": "Daftar data berhasil diambil"},
        data=JobSkillRequirementListData(
            job_skill_requirements=items,
            pagination=Pagination(offset=offset, limit=limit, total=total),
        ),
    )


def delete_job_skill_requirement(db: Session, job_skill_requirement_id: int) -> EmptyResponse:
    job_skill_requirement_service.delete_job_skill_requirement(
        db=db, job_skill_requirement_id=job_skill_requirement_id
    )
    return EmptyResponse(message={"success": "Data berhasil dihapus"}, data={})
