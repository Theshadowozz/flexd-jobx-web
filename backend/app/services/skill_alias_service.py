from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.models.skill import Skill
from app.models.skill_alias import SkillAlias
from app.schemas.skill_alias import SkillAliasCreate, SkillAliasUpdate
from app.utils.database_errors import translate_database_error
from app.utils.exceptions import AppError


def get_skill_alias(db: Session, skill_alias_id: int) -> SkillAlias:
    statement = select(SkillAlias).where(SkillAlias.id == skill_alias_id)
    skill_alias = db.scalar(statement)
    if skill_alias is None:
        raise AppError(
            status_code=404, category="not_found", errors={"skill_alias": "Data tidak ditemukan"}
        )
    return skill_alias


def list_skill_aliases(
    db: Session, offset: int, limit: int, skill_id: int | None = None, search: str | None = None
) -> tuple[list[SkillAlias], int]:
    conditions = []
    if skill_id is not None:
        conditions.append(SkillAlias.skill_id == skill_id)
    if search:
        conditions.append(SkillAlias.alias_name.contains(search, autoescape=True))
    total_statement = select(func.count()).select_from(SkillAlias).where(*conditions)
    total = db.scalar(total_statement) or 0
    statement = (
        select(SkillAlias).where(*conditions).order_by(SkillAlias.id).offset(offset).limit(limit)
    )
    records = list(db.scalars(statement).all())
    return (records, total)


def create_skill_alias(db: Session, payload: SkillAliasCreate) -> SkillAlias:
    try:
        record = None
        values = {
            "skill_id": payload.skill_id,
            "alias_name": payload.alias_name,
            "normalized_alias": payload.normalized_alias,
        }
        payload.model_dump()
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
        if values["alias_name"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"alias_name": "Field tidak boleh null"},
            )
        if values["normalized_alias"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"normalized_alias": "Field tidak boleh null"},
            )
        record = SkillAlias(
            skill_id=values["skill_id"],
            alias_name=values["alias_name"],
            normalized_alias=values["normalized_alias"],
        )
        db.add(record)
        db.flush()
        db.refresh(record)
        db.commit()
        return record
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "skill_alias")
        raise
    except Exception:
        db.rollback()
        raise


def update_skill_alias(db: Session, skill_alias_id: int, payload: SkillAliasUpdate) -> SkillAlias:
    try:
        statement = (
            select(SkillAlias)
            .where(SkillAlias.id == skill_alias_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        record = db.scalar(statement)
        if record is None:
            raise AppError(
                status_code=404,
                category="not_found",
                errors={"skill_alias": "Data tidak ditemukan"},
            )
        values = {
            "skill_id": record.skill_id,
            "alias_name": payload.alias_name
            if "alias_name" in payload.model_fields_set
            else record.alias_name,
            "normalized_alias": payload.normalized_alias
            if "normalized_alias" in payload.model_fields_set
            else record.normalized_alias,
        }
        payload.model_dump(exclude_unset=True)
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
        if values["alias_name"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"alias_name": "Field tidak boleh null"},
            )
        if values["normalized_alias"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"normalized_alias": "Field tidak boleh null"},
            )
        if "alias_name" in payload.model_fields_set:
            record.alias_name = values["alias_name"]
        if "normalized_alias" in payload.model_fields_set:
            record.normalized_alias = values["normalized_alias"]
        db.flush()
        db.refresh(record)
        db.commit()
        return record
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "skill_alias")
        raise
    except Exception:
        db.rollback()
        raise


def delete_skill_alias(db: Session, skill_alias_id: int) -> None:
    try:
        statement = (
            select(SkillAlias)
            .where(SkillAlias.id == skill_alias_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        record = db.scalar(statement)
        if record is None:
            raise AppError(
                status_code=404,
                category="not_found",
                errors={"skill_alias": "Data tidak ditemukan"},
            )
        db.delete(record)
        db.commit()
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "skill_alias")
        raise
    except Exception:
        db.rollback()
        raise
