from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CandidateProfile
from app.schemas.candidate_profile import CandidateProfileCreate, CandidateProfileUpdate
from app.services.validation import reject_nulls, require_account_type, validate_range
from app.utils.database_errors import translate_database_error
from app.utils.exceptions import AppError


async def list_candidate_profiles(db: AsyncSession, limit: int, offset: int):
    records = await db.scalars(
        select(CandidateProfile).order_by(CandidateProfile.user_id).limit(limit).offset(offset)
    )
    return list(records), await db.scalar(select(func.count()).select_from(CandidateProfile))


async def get_candidate_profile(db: AsyncSession, record_id: int):
    record = await db.get(CandidateProfile, record_id)
    if record is None:
        raise AppError(
            404, "Candidate profile not found", {"candidate_profile": "Record does not exist"}
        )
    return record


async def create_candidate_profile(db: AsyncSession, schema: CandidateProfileCreate):
    try:
        await require_account_type(db, schema.user_id, "user_id", "candidate")
        values = schema.model_dump()
        validate_range(values, "expected_salary_min", "expected_salary_max")
        record = CandidateProfile(**values)
        db.add(record)
        await db.flush()
        await db.refresh(record)
        await db.commit()
        return record
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "candidate_profile") from exc
    except Exception:
        await db.rollback()
        raise


async def update_candidate_profile(
    db: AsyncSession, record_id: int, schema: CandidateProfileUpdate
):
    try:
        record = await db.scalar(
            select(CandidateProfile)
            .where(CandidateProfile.user_id == record_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if record is None:
            raise AppError(
                404, "Candidate profile not found", {"candidate_profile": "Record does not exist"}
            )
        values = schema.model_dump(exclude_unset=True)
        reject_nulls(
            values,
            "country",
            "preferred_employment_type",
            "preferred_work_mode",
            "profile_visibility",
        )
        merged = {
            "expected_salary_min": record.expected_salary_min,
            "expected_salary_max": record.expected_salary_max,
            **values,
        }
        validate_range(merged, "expected_salary_min", "expected_salary_max")
        for field, value in values.items():
            setattr(record, field, value)
        await db.flush()
        await db.refresh(record)
        await db.commit()
        return record
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "candidate_profile") from exc
    except Exception:
        await db.rollback()
        raise


async def delete_candidate_profile(db: AsyncSession, record_id: int):
    try:
        record = await db.scalar(
            select(CandidateProfile).where(CandidateProfile.user_id == record_id).with_for_update()
        )
        if record is None:
            raise AppError(
                404, "Candidate profile not found", {"candidate_profile": "Record does not exist"}
            )
        await db.delete(record)
        await db.commit()
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "candidate_profile") from exc
    except Exception:
        await db.rollback()
        raise
