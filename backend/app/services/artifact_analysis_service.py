from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Artifact, ArtifactAnalysis, User
from app.schemas.artifact_analysis import ArtifactAnalysisCreate, ArtifactAnalysisUpdate
from app.services.validation import reject_nulls, require_reference
from app.utils.database_errors import translate_database_error
from app.utils.exceptions import AppError


async def list_artifact_analyses(db: AsyncSession, limit: int, offset: int):
    records = await db.scalars(
        select(ArtifactAnalysis).order_by(ArtifactAnalysis.id).limit(limit).offset(offset)
    )
    return list(records), await db.scalar(select(func.count()).select_from(ArtifactAnalysis))


async def get_artifact_analysis(db: AsyncSession, record_id: int):
    record = await db.get(ArtifactAnalysis, record_id)
    if record is None:
        raise AppError(
            404, "Artifact analysis not found", {"artifact_analysis": "Record does not exist"}
        )
    return record


async def create_artifact_analysis(db: AsyncSession, schema: ArtifactAnalysisCreate):
    try:
        await require_reference(db, Artifact, schema.artifact_id, "artifact_id")
        await require_reference(db, User, schema.reviewed_by_user_id, "reviewed_by_user_id")
        record = ArtifactAnalysis(**schema.model_dump())
        db.add(record)
        await db.flush()
        await db.refresh(record)
        await db.commit()
        return record
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "artifact_analysis") from exc
    except Exception:
        await db.rollback()
        raise


async def update_artifact_analysis(
    db: AsyncSession, record_id: int, schema: ArtifactAnalysisUpdate
):
    try:
        record = await db.scalar(
            select(ArtifactAnalysis)
            .where(ArtifactAnalysis.id == record_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if record is None:
            raise AppError(
                404, "Artifact analysis not found", {"artifact_analysis": "Record does not exist"}
            )
        values = schema.model_dump(exclude_unset=True)
        reject_nulls(values, "analysis_status")
        if "reviewed_by_user_id" in values:
            await require_reference(db, User, values["reviewed_by_user_id"], "reviewed_by_user_id")
        for field, value in values.items():
            setattr(record, field, value)
        await db.flush()
        await db.refresh(record)
        await db.commit()
        return record
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "artifact_analysis") from exc
    except Exception:
        await db.rollback()
        raise


async def delete_artifact_analysis(db: AsyncSession, record_id: int):
    try:
        record = await db.scalar(
            select(ArtifactAnalysis).where(ArtifactAnalysis.id == record_id).with_for_update()
        )
        if record is None:
            raise AppError(
                404, "Artifact analysis not found", {"artifact_analysis": "Record does not exist"}
            )
        await db.delete(record)
        await db.commit()
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "artifact_analysis") from exc
    except Exception:
        await db.rollback()
        raise
