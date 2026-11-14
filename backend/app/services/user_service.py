from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CandidateProfile, CompanyProfile, JobMatch, JobPost, User
from app.schemas.user import UserCreate, UserUpdate
from app.services.validation import reject_nulls
from app.utils.database_errors import translate_database_error
from app.utils.exceptions import AppError
from app.utils.security import hash_password


async def list_users(db: AsyncSession, limit: int, offset: int):
    records = await db.scalars(select(User).order_by(User.id).limit(limit).offset(offset))
    return list(records), await db.scalar(select(func.count()).select_from(User))


async def get_user(db: AsyncSession, record_id: int):
    record = await db.get(User, record_id)
    if record is None:
        raise AppError(404, "User not found", {"user": "Record does not exist"})
    return record


async def lock_users(db: AsyncSession) -> dict[int, User]:
    # Consistent lock order protects concurrent last-admin changes.
    records = await db.scalars(
        select(User).order_by(User.id).with_for_update().execution_options(populate_existing=True)
    )
    return {user.id: user for user in records}


def protect_last_admin(users: dict[int, User], record: User):
    if record.account_type == "admin" and record.account_status == "active":
        active = sum(
            u.account_type == "admin" and u.account_status == "active" for u in users.values()
        )
        if active <= 1:
            raise AppError(409, "Resource conflict", {"user": "Last active admin must be retained"})


async def create_user(db: AsyncSession, schema: UserCreate):
    try:
        values = schema.model_dump(exclude={"password"})
        values["email"] = str(schema.email).lower()
        values["password_hash"] = hash_password(schema.password)
        record = User(**values)
        db.add(record)
        await db.flush()
        await db.refresh(record)
        await db.commit()
        return record
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "user") from exc
    except Exception:
        await db.rollback()
        raise


async def update_user(db: AsyncSession, record_id: int, schema: UserUpdate):
    try:
        users = await lock_users(db)
        record = users.get(record_id)
        if record is None:
            raise AppError(404, "User not found", {"user": "Record does not exist"})
        values = schema.model_dump(exclude_unset=True)
        reject_nulls(values, "name", "email", "password", "account_type", "account_status")
        role = values.get("account_type", record.account_type)
        status = values.get("account_status", record.account_status)
        if role != "admin" or status != "active":
            protect_last_admin(users, record)
        if role != record.account_type:
            candidate = await db.get(CandidateProfile, record.id)
            company = await db.scalar(
                select(CompanyProfile.id).where(CompanyProfile.user_id == record.id)
            )
            jobs = await db.scalar(select(JobPost.id).where(JobPost.user_id == record.id).limit(1))
            matches = await db.scalar(
                select(JobMatch.id).where(JobMatch.candidate_user_id == record.id).limit(1)
            )
            if any(value is not None for value in (candidate, company, jobs, matches)):
                raise AppError(
                    409,
                    "Resource conflict",
                    {"account_type": "Remove role-specific data before changing role"},
                )
        if "email" in values:
            values["email"] = str(values["email"]).lower()
        if "password" in values:
            values["password_hash"] = hash_password(values.pop("password"))
        for field, value in values.items():
            setattr(record, field, value)
        await db.flush()
        await db.refresh(record)
        await db.commit()
        return record
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "user") from exc
    except Exception:
        await db.rollback()
        raise


async def delete_user(db: AsyncSession, record_id: int):
    try:
        users = await lock_users(db)
        record = users.get(record_id)
        if record is None:
            raise AppError(404, "User not found", {"user": "Record does not exist"})
        protect_last_admin(users, record)
        await db.delete(record)
        await db.commit()
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "user") from exc
    except Exception:
        await db.rollback()
        raise
