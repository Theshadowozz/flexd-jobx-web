from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Skill
from app.schemas.skill import SkillCreate, SkillUpdate
from app.services.validation import lock_skill_tree, reject_nulls, validate_skill_parent
from app.utils.database_errors import translate_database_error
from app.utils.exceptions import AppError


async def list_skills(db: AsyncSession, limit: int, offset: int):
    records = await db.scalars(select(Skill).order_by(Skill.id).limit(limit).offset(offset))
    return list(records), await db.scalar(select(func.count()).select_from(Skill))


async def get_skill(db: AsyncSession, record_id: int):
    record = await db.get(Skill, record_id)
    if record is None:
        raise AppError(404, "Skill not found", {"skill": "Record does not exist"})
    return record


async def create_skill(db: AsyncSession, schema: SkillCreate):
    try:
        skills = await lock_skill_tree(db)
        validate_skill_parent(skills, schema.parent_skill_id, None)
        record = Skill(**schema.model_dump())
        db.add(record)
        await db.flush()
        await db.refresh(record)
        await db.commit()
        return record
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "skill") from exc
    except Exception:
        await db.rollback()
        raise


async def update_skill(db: AsyncSession, record_id: int, schema: SkillUpdate):
    try:
        skills = await lock_skill_tree(db)
        record = skills.get(record_id)
        if record is None:
            raise AppError(404, "Skill not found", {"skill": "Record does not exist"})
        values = schema.model_dump(exclude_unset=True)
        reject_nulls(values, "canonical_name", "slug")
        if "parent_skill_id" in values:
            validate_skill_parent(skills, values["parent_skill_id"], record_id)
        for field, value in values.items():
            setattr(record, field, value)
        await db.flush()
        await db.refresh(record)
        await db.commit()
        return record
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "skill") from exc
    except Exception:
        await db.rollback()
        raise


async def delete_skill(db: AsyncSession, record_id: int):
    try:
        skills = await lock_skill_tree(db)
        record = skills.get(record_id)
        if record is None:
            raise AppError(404, "Skill not found", {"skill": "Record does not exist"})
        await db.delete(record)
        await db.commit()
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "skill") from exc
    except Exception:
        await db.rollback()
        raise
