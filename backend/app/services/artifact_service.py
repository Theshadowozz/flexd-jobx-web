from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Artifact, User
from app.schemas.artifact import ArtifactCreate, ArtifactUpdate
from app.services.validation import reject_nulls, require_reference, validate_range
from app.utils.database_errors import translate_database_error
from app.utils.exceptions import AppError


def validate_artifact(values: dict):
    if not values.get("source_url") and not values.get("storage_key"):
        raise AppError(
            422, "Validation failed", {"artifact": "source_url or storage_key is required"}
        )
    validate_range(values, "project_started_at", "project_completed_at")


async def list_artifacts(db: AsyncSession, limit: int, offset: int):
    records = await db.scalars(select(Artifact).order_by(Artifact.id).limit(limit).offset(offset))
    return list(records), await db.scalar(select(func.count()).select_from(Artifact))


async def get_artifact(db: AsyncSession, record_id: int):
    record = await db.get(Artifact, record_id)
    if record is None:
        raise AppError(404, "Artifact not found", {"artifact": "Record does not exist"})
    return record


async def create_artifact(db: AsyncSession, schema: ArtifactCreate):
    try:
        await require_reference(db, User, schema.owner_user_id, "owner_user_id")
        values = schema.model_dump()
        validate_artifact(values)
        values["metadata_json"] = values.pop("metadata")
        record = Artifact(**values)
        db.add(record)
        await db.flush()
        await db.refresh(record)
        await db.commit()
        return record
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "artifact") from exc
    except Exception:
        await db.rollback()
        raise


async def update_artifact(db: AsyncSession, record_id: int, schema: ArtifactUpdate):
    try:
        record = await db.scalar(
            select(Artifact)
            .where(Artifact.id == record_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if record is None:
            raise AppError(404, "Artifact not found", {"artifact": "Record does not exist"})
        values = schema.model_dump(exclude_unset=True)
        reject_nulls(values, "title", "artifact_type", "visibility", "processing_status")
        validate_artifact(
            {
                "source_url": record.source_url,
                "storage_key": record.storage_key,
                "project_started_at": record.project_started_at,
                "project_completed_at": record.project_completed_at,
                **values,
            }
        )
        if "metadata" in values:
            values["metadata_json"] = values.pop("metadata")
        for field, value in values.items():
            setattr(record, field, value)
        await db.flush()
        await db.refresh(record)
        await db.commit()
        return record
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "artifact") from exc
    except Exception:
        await db.rollback()
        raise


async def delete_artifact(db: AsyncSession, record_id: int):
    try:
        record = await db.scalar(select(Artifact).where(Artifact.id == record_id).with_for_update())
        if record is None:
            raise AppError(404, "Artifact not found", {"artifact": "Record does not exist"})
        await db.delete(record)
        await db.commit()
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "artifact") from exc
    except Exception:
        await db.rollback()
        raise
