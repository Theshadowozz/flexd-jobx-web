from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CompanyProfile
from app.schemas.company_profile import CompanyProfileCreate, CompanyProfileUpdate
from app.services.validation import reject_nulls, require_account_type
from app.utils.database_errors import translate_database_error
from app.utils.exceptions import AppError


async def list_company_profiles(db: AsyncSession, limit: int, offset: int):
    records = await db.scalars(
        select(CompanyProfile).order_by(CompanyProfile.id).limit(limit).offset(offset)
    )
    return list(records), await db.scalar(select(func.count()).select_from(CompanyProfile))


async def get_company_profile(db: AsyncSession, record_id: int):
    record = await db.get(CompanyProfile, record_id)
    if record is None:
        raise AppError(
            404, "Company profile not found", {"company_profile": "Record does not exist"}
        )
    return record


async def create_company_profile(db: AsyncSession, schema: CompanyProfileCreate):
    try:
        await require_account_type(db, schema.user_id, "user_id", "employer")
        record = CompanyProfile(**schema.model_dump())
        db.add(record)
        await db.flush()
        await db.refresh(record)
        await db.commit()
        return record
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "company_profile") from exc
    except Exception:
        await db.rollback()
        raise


async def update_company_profile(db: AsyncSession, record_id: int, schema: CompanyProfileUpdate):
    try:
        record = await db.scalar(
            select(CompanyProfile)
            .where(CompanyProfile.id == record_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if record is None:
            raise AppError(
                404, "Company profile not found", {"company_profile": "Record does not exist"}
            )
        values = schema.model_dump(exclude_unset=True)
        reject_nulls(values, "name", "country")
        for field, value in values.items():
            setattr(record, field, value)
        await db.flush()
        await db.refresh(record)
        await db.commit()
        return record
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "company_profile") from exc
    except Exception:
        await db.rollback()
        raise


async def delete_company_profile(db: AsyncSession, record_id: int):
    try:
        record = await db.scalar(
            select(CompanyProfile).where(CompanyProfile.id == record_id).with_for_update()
        )
        if record is None:
            raise AppError(
                404, "Company profile not found", {"company_profile": "Record does not exist"}
            )
        await db.delete(record)
        await db.commit()
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "company_profile") from exc
    except Exception:
        await db.rollback()
        raise
