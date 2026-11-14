from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Skill, SkillAlias
from app.schemas.skill_alias import SkillAliasCreate, SkillAliasUpdate
from app.services.validation import reject_nulls, require_reference
from app.utils.database_errors import translate_database_error
from app.utils.exceptions import AppError


async def list_skill_aliases(db: AsyncSession, limit: int, offset: int):
    records = await db.scalars(
        select(SkillAlias).order_by(SkillAlias.id).limit(limit).offset(offset)
    )
    total = await db.scalar(select(func.count()).select_from(SkillAlias))
    return list(records), total


async def get_skill_alias(db: AsyncSession, record_id: int):
    record = await db.get(SkillAlias, record_id)
    if record is None:
        raise AppError(404, "Skill alias not found", {"skill_alias": "Record does not exist"})
    return record


async def create_skill_alias(db: AsyncSession, schema: SkillAliasCreate):
    try:
        await require_reference(db, Skill, schema.skill_id, "skill_id")
        alias = schema.alias_name.strip()
        if not alias:
            raise AppError(422, "Validation failed", {"alias_name": "Alias cannot be blank"})
        record = SkillAlias(
            skill_id=schema.skill_id, alias_name=alias, normalized_alias=alias.lower()
        )
        db.add(record)
        await db.flush()
        await db.refresh(record)
        await db.commit()
        return record
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "skill_alias") from exc
    except Exception:
        await db.rollback()
        raise


async def update_skill_alias(db: AsyncSession, record_id: int, schema: SkillAliasUpdate):
    try:
        record = await db.scalar(
            select(SkillAlias)
            .where(SkillAlias.id == record_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if record is None:
            raise AppError(404, "Skill alias not found", {"skill_alias": "Record does not exist"})
        values = schema.model_dump(exclude_unset=True)
        reject_nulls(values, "skill_id", "alias_name")
        if "skill_id" in values:
            await require_reference(db, Skill, values["skill_id"], "skill_id")
            record.skill_id = values["skill_id"]
        if "alias_name" in values:
            alias = values["alias_name"].strip()
            if not alias:
                raise AppError(422, "Validation failed", {"alias_name": "Alias cannot be blank"})
            record.alias_name = alias
            record.normalized_alias = alias.lower()
        await db.flush()
        await db.refresh(record)
        await db.commit()
        return record
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "skill_alias") from exc
    except Exception:
        await db.rollback()
        raise


async def delete_skill_alias(db: AsyncSession, record_id: int):
    try:
        record = await db.scalar(
            select(SkillAlias).where(SkillAlias.id == record_id).with_for_update()
        )
        if record is None:
            raise AppError(404, "Skill alias not found", {"skill_alias": "Record does not exist"})
        await db.delete(record)
        await db.commit()
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "skill_alias") from exc
    except Exception:
        await db.rollback()
        raise
