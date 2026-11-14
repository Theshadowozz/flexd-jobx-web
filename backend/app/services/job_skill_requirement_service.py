from typing import Literal

from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.models.job_post import JobPost
from app.models.job_skill_requirement import JobSkillRequirement
from app.models.skill import Skill
from app.schemas.job_skill_requirement import JobSkillRequirementCreate, JobSkillRequirementUpdate
from app.utils.database_errors import translate_database_error
from app.utils.exceptions import AppError


def get_job_skill_requirement(db: Session, job_skill_requirement_id: int) -> JobSkillRequirement:
    statement = select(JobSkillRequirement).where(
        JobSkillRequirement.id == job_skill_requirement_id
    )
    job_skill_requirement = db.scalar(statement)
    if job_skill_requirement is None:
        raise AppError(
            status_code=404,
            category="not_found",
            errors={"job_skill_requirement": "Data tidak ditemukan"},
        )
    return job_skill_requirement


def list_job_skill_requirements(
    db: Session,
    offset: int,
    limit: int,
    job_id: int | None = None,
    skill_id: int | None = None,
    requirement_type: Literal["must_have", "preferred"] | None = None,
) -> tuple[list[JobSkillRequirement], int]:
    conditions = []
    if job_id is not None:
        conditions.append(JobSkillRequirement.job_id == job_id)
    if skill_id is not None:
        conditions.append(JobSkillRequirement.skill_id == skill_id)
    if requirement_type is not None:
        conditions.append(JobSkillRequirement.requirement_type == requirement_type)
    total_statement = select(func.count()).select_from(JobSkillRequirement).where(*conditions)
    total = db.scalar(total_statement) or 0
    statement = (
        select(JobSkillRequirement)
        .where(*conditions)
        .order_by(JobSkillRequirement.id)
        .offset(offset)
        .limit(limit)
    )
    records = list(db.scalars(statement).all())
    return (records, total)


def create_job_skill_requirement(
    db: Session, payload: JobSkillRequirementCreate
) -> JobSkillRequirement:
    try:
        record = None
        values = {
            "requirement_type": payload.requirement_type,
            "minimum_level": payload.minimum_level,
            "weight": payload.weight,
            "requirement_note": payload.requirement_note,
            "job_id": payload.job_id,
            "skill_id": payload.skill_id,
        }
        payload.model_dump()
        if values["job_id"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"job_id": "Field tidak boleh null"},
            )
        if values["job_id"] is not None:
            referenced_job_id = db.scalar(
                select(JobPost)
                .where(JobPost.id == values["job_id"])
                .with_for_update(read=True)
                .execution_options(populate_existing=True)
            )
            if referenced_job_id is None:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"job_id": "Referensi tidak ditemukan"},
                )
        if values["skill_id"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"skill_id": "Field tidak boleh null"},
            )
        if values["skill_id"] is not None:
            referenced_skill_id = db.scalar(
                select(Skill)
                .where(Skill.id == values["skill_id"])
                .with_for_update(read=True)
                .execution_options(populate_existing=True)
            )
            if referenced_skill_id is None:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"skill_id": "Referensi tidak ditemukan"},
                )
        if values["requirement_type"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"requirement_type": "Field tidak boleh null"},
            )
        if values["weight"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"weight": "Field tidak boleh null"},
            )
        record = JobSkillRequirement(
            requirement_type=values["requirement_type"],
            minimum_level=values["minimum_level"],
            weight=values["weight"],
            requirement_note=values["requirement_note"],
            job_id=values["job_id"],
            skill_id=values["skill_id"],
        )
        db.add(record)
        db.flush()
        db.refresh(record)
        db.commit()
        return record
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "job_skill_requirement")
        raise
    except Exception:
        db.rollback()
        raise


def update_job_skill_requirement(
    db: Session, job_skill_requirement_id: int, payload: JobSkillRequirementUpdate
) -> JobSkillRequirement:
    try:
        statement = (
            select(JobSkillRequirement)
            .where(JobSkillRequirement.id == job_skill_requirement_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        record = db.scalar(statement)
        if record is None:
            raise AppError(
                status_code=404,
                category="not_found",
                errors={"job_skill_requirement": "Data tidak ditemukan"},
            )
        values = {
            "requirement_type": payload.requirement_type
            if "requirement_type" in payload.model_fields_set
            else record.requirement_type,
            "minimum_level": payload.minimum_level
            if "minimum_level" in payload.model_fields_set
            else record.minimum_level,
            "weight": payload.weight if "weight" in payload.model_fields_set else record.weight,
            "requirement_note": payload.requirement_note
            if "requirement_note" in payload.model_fields_set
            else record.requirement_note,
            "job_id": record.job_id,
            "skill_id": record.skill_id,
        }
        payload.model_dump(exclude_unset=True)
        if values["job_id"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"job_id": "Field tidak boleh null"},
            )
        if values["job_id"] is not None:
            referenced_job_id = db.scalar(
                select(JobPost)
                .where(JobPost.id == values["job_id"])
                .with_for_update(read=True)
                .execution_options(populate_existing=True)
            )
            if referenced_job_id is None:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"job_id": "Referensi tidak ditemukan"},
                )
        if values["skill_id"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"skill_id": "Field tidak boleh null"},
            )
        if values["skill_id"] is not None:
            referenced_skill_id = db.scalar(
                select(Skill)
                .where(Skill.id == values["skill_id"])
                .with_for_update(read=True)
                .execution_options(populate_existing=True)
            )
            if referenced_skill_id is None:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"skill_id": "Referensi tidak ditemukan"},
                )
        if values["requirement_type"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"requirement_type": "Field tidak boleh null"},
            )
        if values["weight"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"weight": "Field tidak boleh null"},
            )
        if "requirement_type" in payload.model_fields_set:
            record.requirement_type = values["requirement_type"]
        if "minimum_level" in payload.model_fields_set:
            record.minimum_level = values["minimum_level"]
        if "weight" in payload.model_fields_set:
            record.weight = values["weight"]
        if "requirement_note" in payload.model_fields_set:
            record.requirement_note = values["requirement_note"]
        db.flush()
        db.refresh(record)
        db.commit()
        return record
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "job_skill_requirement")
        raise
    except Exception:
        db.rollback()
        raise


def delete_job_skill_requirement(db: Session, job_skill_requirement_id: int) -> None:
    try:
        statement = (
            select(JobSkillRequirement)
            .where(JobSkillRequirement.id == job_skill_requirement_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        record = db.scalar(statement)
        if record is None:
            raise AppError(
                status_code=404,
                category="not_found",
                errors={"job_skill_requirement": "Data tidak ditemukan"},
            )
        db.delete(record)
        db.commit()
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "job_skill_requirement")
        raise
    except Exception:
        db.rollback()
        raise
