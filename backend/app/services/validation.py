"""Named domain checks shared by explicit resource services; no generic CRUD."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ArtifactAnalysis, Skill, User
from app.utils.exceptions import AppError


def reject_nulls(values: dict, *fields: str) -> None:
    for field in fields:
        if field in values and values[field] is None:
            raise AppError(422, "Validation failed", {field: "Field cannot be null"})


def validate_range(values: dict, minimum: str, maximum: str) -> None:
    low, high = values.get(minimum), values.get(maximum)
    if low is not None and high is not None and low > high:
        raise AppError(
            422, "Validation failed", {maximum: f"Must be greater than or equal to {minimum}"}
        )


async def require_reference(db: AsyncSession, model, value: int | None, field: str):
    if value is None:
        return None
    key = next(iter(model.__table__.primary_key.columns)).name
    record = await db.scalar(
        select(model).where(getattr(model, key) == value).with_for_update(read=True)
    )
    if record is None:
        raise AppError(422, "Validation failed", {field: "Referenced record does not exist"})
    return record


async def require_account_type(db: AsyncSession, value: int, field: str, role: str) -> User:
    user = await require_reference(db, User, value, field)
    if user.account_type != role:
        raise AppError(422, "Validation failed", {field: f"Account must be {role}"})
    return user


async def validate_evidence_analysis(db: AsyncSession, analysis_id: int, artifact_id: int):
    analysis = await require_reference(db, ArtifactAnalysis, analysis_id, "analysis_id")
    if analysis.artifact_id != artifact_id:
        raise AppError(
            422, "Validation failed", {"analysis_id": "Analysis belongs to another artifact"}
        )


async def lock_skill_tree(db: AsyncSession) -> dict[int, Skill]:
    # Serialize hierarchy changes to prevent concurrent cycle creation.
    result = await db.scalars(
        select(Skill).order_by(Skill.id).with_for_update().execution_options(populate_existing=True)
    )
    return {skill.id: skill for skill in result}


def validate_skill_parent(skills: dict[int, Skill], parent_id: int | None, skill_id: int | None):
    visited = {skill_id} if skill_id is not None else set()
    while parent_id is not None:
        if parent_id in visited:
            raise AppError(
                422,
                "Validation failed",
                {"parent_skill_id": "Skill hierarchy cannot contain cycles"},
            )
        visited.add(parent_id)
        parent = skills.get(parent_id)
        if parent is None:
            raise AppError(
                422, "Validation failed", {"parent_skill_id": "Parent skill does not exist"}
            )
        parent_id = parent.parent_skill_id
