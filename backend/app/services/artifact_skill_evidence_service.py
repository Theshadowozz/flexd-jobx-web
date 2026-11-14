from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Artifact, ArtifactSkillEvidence, Skill
from app.schemas.artifact_skill_evidence import (
    ArtifactSkillEvidenceCreate,
    ArtifactSkillEvidenceUpdate,
)
from app.services.validation import reject_nulls, require_reference, validate_evidence_analysis
from app.utils.database_errors import translate_database_error
from app.utils.exceptions import AppError


async def list_artifact_skill_evidences(db: AsyncSession, limit: int, offset: int):
    records = await db.scalars(
        select(ArtifactSkillEvidence).order_by(ArtifactSkillEvidence.id).limit(limit).offset(offset)
    )
    return list(records), await db.scalar(select(func.count()).select_from(ArtifactSkillEvidence))


async def get_artifact_skill_evidence(db: AsyncSession, record_id: int):
    record = await db.get(ArtifactSkillEvidence, record_id)
    if record is None:
        raise AppError(
            404,
            "Artifact skill evidence not found",
            {"artifact_skill_evidence": "Record does not exist"},
        )
    return record


async def create_artifact_skill_evidence(db: AsyncSession, schema: ArtifactSkillEvidenceCreate):
    try:
        await require_reference(db, Artifact, schema.artifact_id, "artifact_id")
        await validate_evidence_analysis(db, schema.analysis_id, schema.artifact_id)
        await require_reference(db, Skill, schema.skill_id, "skill_id")
        record = ArtifactSkillEvidence(**schema.model_dump())
        db.add(record)
        await db.flush()
        await db.refresh(record)
        await db.commit()
        return record
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "artifact_skill_evidence") from exc
    except Exception:
        await db.rollback()
        raise


async def update_artifact_skill_evidence(
    db: AsyncSession, record_id: int, schema: ArtifactSkillEvidenceUpdate
):
    try:
        record = await db.scalar(
            select(ArtifactSkillEvidence)
            .where(ArtifactSkillEvidence.id == record_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if record is None:
            raise AppError(
                404,
                "Artifact skill evidence not found",
                {"artifact_skill_evidence": "Record does not exist"},
            )
        values = schema.model_dump(exclude_unset=True)
        reject_nulls(values, "confidence_score", "evidence_kind", "review_status")
        for field, value in values.items():
            setattr(record, field, value)
        await db.flush()
        await db.refresh(record)
        await db.commit()
        return record
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "artifact_skill_evidence") from exc
    except Exception:
        await db.rollback()
        raise


async def delete_artifact_skill_evidence(db: AsyncSession, record_id: int):
    try:
        record = await db.scalar(
            select(ArtifactSkillEvidence)
            .where(ArtifactSkillEvidence.id == record_id)
            .with_for_update()
        )
        if record is None:
            raise AppError(
                404,
                "Artifact skill evidence not found",
                {"artifact_skill_evidence": "Record does not exist"},
            )
        await db.delete(record)
        await db.commit()
    except DBAPIError as exc:
        await db.rollback()
        raise translate_database_error(exc, "artifact_skill_evidence") from exc
    except Exception:
        await db.rollback()
        raise
