from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Artifact, ArtifactContribution, User
from app.schemas.artifact_contribution import ArtifactContributionCreate, ArtifactContributionUpdate
from app.services.validation import reject_nulls, require_reference
from app.utils.database_errors import translate_database_error
from app.utils.exceptions import AppError


async def list_artifact_contributions(db: AsyncSession, limit: int, offset: int):
    records = await db.scalars(
        select(ArtifactContribution).order_by(ArtifactContribution.id).limit(limit).offset(offset)
    )
    return list(records), await db.scalar(select(func.count()).select_from(ArtifactContribution))


async def get_artifact_contribution(db: AsyncSession, record_id: int):
    record = await db.get(ArtifactContribution, record_id)
    if record is None:
        raise AppError(
            404,
            "Artifact contribution not found",
            {"artifact_contribution": "Record does not exist"},
        )
    return record


async def create_artifact_contribution(db: AsyncSession, schema: ArtifactContributionCreate):
    try:
        await require_reference(db, Artifact, schema.artifact_id, "artifact_id")
        await require_reference(db, User, schema.contributor_user_id, "contributor_user_id")
        record = ArtifactContribution(**schema.model_dump())
        db.add(record)
        await db.flush()
        await db.refresh(record)
        await db.commit()
        return record
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "artifact_contribution") from exc
    except Exception:
        await db.rollback()
        raise


async def update_artifact_contribution(
    db: AsyncSession, record_id: int, schema: ArtifactContributionUpdate
):
    try:
        record = await db.scalar(
            select(ArtifactContribution)
            .where(ArtifactContribution.id == record_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if record is None:
            raise AppError(
                404,
                "Artifact contribution not found",
                {"artifact_contribution": "Record does not exist"},
            )
        values = schema.model_dump(exclude_unset=True)
        reject_nulls(values, "contribution_description", "claim_status")
        for field, value in values.items():
            setattr(record, field, value)
        await db.flush()
        await db.refresh(record)
        await db.commit()
        return record
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "artifact_contribution") from exc
    except Exception:
        await db.rollback()
        raise


async def delete_artifact_contribution(db: AsyncSession, record_id: int):
    try:
        record = await db.scalar(
            select(ArtifactContribution)
            .where(ArtifactContribution.id == record_id)
            .with_for_update()
        )
        if record is None:
            raise AppError(
                404,
                "Artifact contribution not found",
                {"artifact_contribution": "Record does not exist"},
            )
        await db.delete(record)
        await db.commit()
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "artifact_contribution") from exc
    except Exception:
        await db.rollback()
        raise
