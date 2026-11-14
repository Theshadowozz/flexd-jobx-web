from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import JobPost, JobSkillRequirement, Skill
from app.schemas.job_skill_requirement import JobSkillRequirementCreate, JobSkillRequirementUpdate
from app.services.validation import reject_nulls, require_reference
from app.utils.database_errors import translate_database_error
from app.utils.exceptions import AppError


async def list_job_skill_requirements(db: AsyncSession, limit: int, offset: int):
    records = await db.scalars(
        select(JobSkillRequirement).order_by(JobSkillRequirement.id).limit(limit).offset(offset)
    )
    return list(records), await db.scalar(select(func.count()).select_from(JobSkillRequirement))


async def get_job_skill_requirement(db: AsyncSession, record_id: int):
    record = await db.get(JobSkillRequirement, record_id)
    if record is None:
        raise AppError(
            404,
            "Job skill requirement not found",
            {"job_skill_requirement": "Record does not exist"},
        )
    return record


async def create_job_skill_requirement(db: AsyncSession, schema: JobSkillRequirementCreate):
    try:
        await require_reference(db, JobPost, schema.job_id, "job_id")
        await require_reference(db, Skill, schema.skill_id, "skill_id")
        record = JobSkillRequirement(**schema.model_dump())
        db.add(record)
        await db.flush()
        await db.refresh(record)
        await db.commit()
        return record
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "job_skill_requirement") from exc
    except Exception:
        await db.rollback()
        raise


async def update_job_skill_requirement(
    db: AsyncSession, record_id: int, schema: JobSkillRequirementUpdate
):
    try:
        record = await db.scalar(
            select(JobSkillRequirement)
            .where(JobSkillRequirement.id == record_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if record is None:
            raise AppError(
                404,
                "Job skill requirement not found",
                {"job_skill_requirement": "Record does not exist"},
            )
        values = schema.model_dump(exclude_unset=True)
        reject_nulls(values, "requirement_type", "weight")
        for field, value in values.items():
            setattr(record, field, value)
        await db.flush()
        await db.refresh(record)
        await db.commit()
        return record
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "job_skill_requirement") from exc
    except Exception:
        await db.rollback()
        raise


async def delete_job_skill_requirement(db: AsyncSession, record_id: int):
    try:
        record = await db.scalar(
            select(JobSkillRequirement).where(JobSkillRequirement.id == record_id).with_for_update()
        )
        if record is None:
            raise AppError(
                404,
                "Job skill requirement not found",
                {"job_skill_requirement": "Record does not exist"},
            )
        await db.delete(record)
        await db.commit()
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "job_skill_requirement") from exc
    except Exception:
        await db.rollback()
        raise
