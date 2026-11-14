from sqlalchemy import func, or_, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.models.skill import Skill
from app.schemas.skill import SkillCreate, SkillUpdate
from app.utils.database_errors import translate_database_error
from app.utils.exceptions import AppError


def lock_skill_hierarchy(db: Session) -> None:
    db.scalars(
        select(Skill).order_by(Skill.id).with_for_update().execution_options(populate_existing=True)
    ).all()


def get_skill(db: Session, skill_id: int) -> Skill:
    statement = select(Skill).where(Skill.id == skill_id)
    skill = db.scalar(statement)
    if skill is None:
        raise AppError(
            status_code=404, category="not_found", errors={"skill": "Data tidak ditemukan"}
        )
    return skill


def list_skills(
    db: Session,
    offset: int,
    limit: int,
    category: str | None = None,
    parent_skill_id: int | None = None,
    search: str | None = None,
) -> tuple[list[Skill], int]:
    conditions = []
    if category is not None:
        conditions.append(Skill.category == category)
    if parent_skill_id is not None:
        conditions.append(Skill.parent_skill_id == parent_skill_id)
    if search:
        conditions.append(
            or_(
                Skill.canonical_name.contains(search, autoescape=True),
                Skill.slug.contains(search, autoescape=True),
            )
        )
    total_statement = select(func.count()).select_from(Skill).where(*conditions)
    total = db.scalar(total_statement) or 0
    statement = select(Skill).where(*conditions).order_by(Skill.id).offset(offset).limit(limit)
    records = list(db.scalars(statement).all())
    return (records, total)


def create_skill(db: Session, payload: SkillCreate) -> Skill:
    try:
        lock_skill_hierarchy(db)
        record = None
        values = {
            "canonical_name": payload.canonical_name,
            "slug": payload.slug,
            "category": payload.category,
            "description": payload.description,
            "parent_skill_id": payload.parent_skill_id,
            "taxonomy_source": payload.taxonomy_source,
        }
        payload.model_dump()
        if values["canonical_name"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"canonical_name": "Field tidak boleh null"},
            )
        if values["slug"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"slug": "Field tidak boleh null"},
            )
        if values["parent_skill_id"] is not None:
            referenced_parent_skill_id = db.scalar(
                select(Skill)
                .where(Skill.id == values["parent_skill_id"])
                .with_for_update(read=True)
                .execution_options(populate_existing=True)
            )
            if referenced_parent_skill_id is None:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"parent_skill_id": "Referensi tidak ditemukan"},
                )
        parent_id, visited = (values.get("parent_skill_id"), set())
        while parent_id is not None:
            if parent_id in visited or (record is not None and parent_id == record.id):
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"parent_skill_id": "Hierarki skill tidak boleh membentuk siklus"},
                )
            visited.add(parent_id)
            parent = db.get(Skill, parent_id)
            parent_id = parent.parent_skill_id if parent else None
        record = Skill(
            canonical_name=values["canonical_name"],
            slug=values["slug"],
            category=values["category"],
            description=values["description"],
            parent_skill_id=values["parent_skill_id"],
            taxonomy_source=values["taxonomy_source"],
        )
        db.add(record)
        db.flush()
        db.refresh(record)
        db.commit()
        return record
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "skill")
        raise
    except Exception:
        db.rollback()
        raise


def update_skill(db: Session, skill_id: int, payload: SkillUpdate) -> Skill:
    try:
        lock_skill_hierarchy(db)
        statement = (
            select(Skill)
            .where(Skill.id == skill_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        record = db.scalar(statement)
        if record is None:
            raise AppError(
                status_code=404, category="not_found", errors={"skill": "Data tidak ditemukan"}
            )
        values = {
            "canonical_name": payload.canonical_name
            if "canonical_name" in payload.model_fields_set
            else record.canonical_name,
            "slug": payload.slug if "slug" in payload.model_fields_set else record.slug,
            "category": payload.category
            if "category" in payload.model_fields_set
            else record.category,
            "description": payload.description
            if "description" in payload.model_fields_set
            else record.description,
            "parent_skill_id": payload.parent_skill_id
            if "parent_skill_id" in payload.model_fields_set
            else record.parent_skill_id,
            "taxonomy_source": payload.taxonomy_source
            if "taxonomy_source" in payload.model_fields_set
            else record.taxonomy_source,
        }
        payload.model_dump(exclude_unset=True)
        if values["canonical_name"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"canonical_name": "Field tidak boleh null"},
            )
        if values["slug"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"slug": "Field tidak boleh null"},
            )
        if values["parent_skill_id"] is not None:
            referenced_parent_skill_id = db.scalar(
                select(Skill)
                .where(Skill.id == values["parent_skill_id"])
                .with_for_update(read=True)
                .execution_options(populate_existing=True)
            )
            if referenced_parent_skill_id is None:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"parent_skill_id": "Referensi tidak ditemukan"},
                )
        parent_id, visited = (values.get("parent_skill_id"), set())
        while parent_id is not None:
            if parent_id in visited or (record is not None and parent_id == record.id):
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"parent_skill_id": "Hierarki skill tidak boleh membentuk siklus"},
                )
            visited.add(parent_id)
            parent = db.get(Skill, parent_id)
            parent_id = parent.parent_skill_id if parent else None
        if "canonical_name" in payload.model_fields_set:
            record.canonical_name = values["canonical_name"]
        if "slug" in payload.model_fields_set:
            record.slug = values["slug"]
        if "category" in payload.model_fields_set:
            record.category = values["category"]
        if "description" in payload.model_fields_set:
            record.description = values["description"]
        if "parent_skill_id" in payload.model_fields_set:
            record.parent_skill_id = values["parent_skill_id"]
        if "taxonomy_source" in payload.model_fields_set:
            record.taxonomy_source = values["taxonomy_source"]
        db.flush()
        db.refresh(record)
        db.commit()
        return record
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "skill")
        raise
    except Exception:
        db.rollback()
        raise


def delete_skill(db: Session, skill_id: int) -> None:
    try:
        lock_skill_hierarchy(db)
        statement = (
            select(Skill)
            .where(Skill.id == skill_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        record = db.scalar(statement)
        if record is None:
            raise AppError(
                status_code=404, category="not_found", errors={"skill": "Data tidak ditemukan"}
            )
        db.delete(record)
        db.commit()
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "skill")
        raise
    except Exception:
        db.rollback()
        raise
