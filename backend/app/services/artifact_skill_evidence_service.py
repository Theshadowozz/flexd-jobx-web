from typing import Literal

from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.models import ArtifactAnalysis
from app.models.artifact import Artifact
from app.models.artifact_skill_evidence import ArtifactSkillEvidence
from app.models.skill import Skill
from app.schemas.artifact_skill_evidence import (
    ArtifactSkillEvidenceCreate,
    ArtifactSkillEvidenceUpdate,
)
from app.utils.database_errors import translate_database_error
from app.utils.exceptions import AppError


def get_artifact_skill_evidence(
    db: Session, artifact_skill_evidence_id: int
) -> ArtifactSkillEvidence:
    statement = select(ArtifactSkillEvidence).where(
        ArtifactSkillEvidence.id == artifact_skill_evidence_id
    )
    artifact_skill_evidence = db.scalar(statement)
    if artifact_skill_evidence is None:
        raise AppError(
            status_code=404,
            category="not_found",
            errors={"artifact_skill_evidence": "Data tidak ditemukan"},
        )
    return artifact_skill_evidence


def list_artifact_skill_evidences(
    db: Session,
    offset: int,
    limit: int,
    artifact_id: int | None = None,
    analysis_id: int | None = None,
    skill_id: int | None = None,
    review_status: Literal["ai_suggested", "candidate_confirmed", "reviewer_verified", "rejected"]
    | None = None,
) -> tuple[list[ArtifactSkillEvidence], int]:
    conditions = []
    if artifact_id is not None:
        conditions.append(ArtifactSkillEvidence.artifact_id == artifact_id)
    if analysis_id is not None:
        conditions.append(ArtifactSkillEvidence.analysis_id == analysis_id)
    if skill_id is not None:
        conditions.append(ArtifactSkillEvidence.skill_id == skill_id)
    if review_status is not None:
        conditions.append(ArtifactSkillEvidence.review_status == review_status)
    total_statement = select(func.count()).select_from(ArtifactSkillEvidence).where(*conditions)
    total = db.scalar(total_statement) or 0
    statement = (
        select(ArtifactSkillEvidence)
        .where(*conditions)
        .order_by(ArtifactSkillEvidence.id)
        .offset(offset)
        .limit(limit)
    )
    records = list(db.scalars(statement).all())
    return (records, total)


def create_artifact_skill_evidence(
    db: Session, payload: ArtifactSkillEvidenceCreate
) -> ArtifactSkillEvidence:
    try:
        record = None
        values = {
            "confidence_score": payload.confidence_score,
            "evidence_kind": payload.evidence_kind,
            "evidence_excerpt": payload.evidence_excerpt,
            "evidence_location": payload.evidence_location,
            "review_status": payload.review_status,
            "artifact_id": payload.artifact_id,
            "analysis_id": payload.analysis_id,
            "skill_id": payload.skill_id,
        }
        payload.model_dump()
        if values["artifact_id"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"artifact_id": "Field tidak boleh null"},
            )
        if values["artifact_id"] is not None:
            referenced_artifact_id = db.scalar(
                select(Artifact)
                .where(Artifact.id == values["artifact_id"])
                .with_for_update(read=True)
                .execution_options(populate_existing=True)
            )
            if referenced_artifact_id is None:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"artifact_id": "Referensi tidak ditemukan"},
                )
        if values["analysis_id"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"analysis_id": "Field tidak boleh null"},
            )
        if values["analysis_id"] is not None:
            referenced_analysis_id = db.scalar(
                select(ArtifactAnalysis)
                .where(ArtifactAnalysis.id == values["analysis_id"])
                .with_for_update(read=True)
                .execution_options(populate_existing=True)
            )
            if referenced_analysis_id is None:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"analysis_id": "Referensi tidak ditemukan"},
                )
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
        if values["confidence_score"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"confidence_score": "Field tidak boleh null"},
            )
        if values["evidence_kind"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"evidence_kind": "Field tidak boleh null"},
            )
        if values["review_status"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"review_status": "Field tidak boleh null"},
            )
        analysis = db.get(ArtifactAnalysis, values["analysis_id"])
        if analysis.artifact_id != values["artifact_id"]:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"analysis_id": "Analysis bukan milik artifact tersebut"},
            )
        record = ArtifactSkillEvidence(
            confidence_score=values["confidence_score"],
            evidence_kind=values["evidence_kind"],
            evidence_excerpt=values["evidence_excerpt"],
            evidence_location=values["evidence_location"],
            review_status=values["review_status"],
            artifact_id=values["artifact_id"],
            analysis_id=values["analysis_id"],
            skill_id=values["skill_id"],
        )
        db.add(record)
        db.flush()
        db.refresh(record)
        db.commit()
        return record
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "artifact_skill_evidence")
        raise
    except Exception:
        db.rollback()
        raise


def update_artifact_skill_evidence(
    db: Session, artifact_skill_evidence_id: int, payload: ArtifactSkillEvidenceUpdate
) -> ArtifactSkillEvidence:
    try:
        statement = (
            select(ArtifactSkillEvidence)
            .where(ArtifactSkillEvidence.id == artifact_skill_evidence_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        record = db.scalar(statement)
        if record is None:
            raise AppError(
                status_code=404,
                category="not_found",
                errors={"artifact_skill_evidence": "Data tidak ditemukan"},
            )
        values = {
            "confidence_score": payload.confidence_score
            if "confidence_score" in payload.model_fields_set
            else record.confidence_score,
            "evidence_kind": payload.evidence_kind
            if "evidence_kind" in payload.model_fields_set
            else record.evidence_kind,
            "evidence_excerpt": payload.evidence_excerpt
            if "evidence_excerpt" in payload.model_fields_set
            else record.evidence_excerpt,
            "evidence_location": payload.evidence_location
            if "evidence_location" in payload.model_fields_set
            else record.evidence_location,
            "review_status": payload.review_status
            if "review_status" in payload.model_fields_set
            else record.review_status,
            "artifact_id": record.artifact_id,
            "analysis_id": record.analysis_id,
            "skill_id": record.skill_id,
        }
        payload.model_dump(exclude_unset=True)
        if values["artifact_id"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"artifact_id": "Field tidak boleh null"},
            )
        if values["artifact_id"] is not None:
            referenced_artifact_id = db.scalar(
                select(Artifact)
                .where(Artifact.id == values["artifact_id"])
                .with_for_update(read=True)
                .execution_options(populate_existing=True)
            )
            if referenced_artifact_id is None:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"artifact_id": "Referensi tidak ditemukan"},
                )
        if values["analysis_id"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"analysis_id": "Field tidak boleh null"},
            )
        if values["analysis_id"] is not None:
            referenced_analysis_id = db.scalar(
                select(ArtifactAnalysis)
                .where(ArtifactAnalysis.id == values["analysis_id"])
                .with_for_update(read=True)
                .execution_options(populate_existing=True)
            )
            if referenced_analysis_id is None:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"analysis_id": "Referensi tidak ditemukan"},
                )
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
        if values["confidence_score"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"confidence_score": "Field tidak boleh null"},
            )
        if values["evidence_kind"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"evidence_kind": "Field tidak boleh null"},
            )
        if values["review_status"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"review_status": "Field tidak boleh null"},
            )
        analysis = db.get(ArtifactAnalysis, values["analysis_id"])
        if analysis.artifact_id != values["artifact_id"]:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"analysis_id": "Analysis bukan milik artifact tersebut"},
            )
        if "confidence_score" in payload.model_fields_set:
            record.confidence_score = values["confidence_score"]
        if "evidence_kind" in payload.model_fields_set:
            record.evidence_kind = values["evidence_kind"]
        if "evidence_excerpt" in payload.model_fields_set:
            record.evidence_excerpt = values["evidence_excerpt"]
        if "evidence_location" in payload.model_fields_set:
            record.evidence_location = values["evidence_location"]
        if "review_status" in payload.model_fields_set:
            record.review_status = values["review_status"]
        db.flush()
        db.refresh(record)
        db.commit()
        return record
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "artifact_skill_evidence")
        raise
    except Exception:
        db.rollback()
        raise


def delete_artifact_skill_evidence(db: Session, artifact_skill_evidence_id: int) -> None:
    try:
        statement = (
            select(ArtifactSkillEvidence)
            .where(ArtifactSkillEvidence.id == artifact_skill_evidence_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        record = db.scalar(statement)
        if record is None:
            raise AppError(
                status_code=404,
                category="not_found",
                errors={"artifact_skill_evidence": "Data tidak ditemukan"},
            )
        db.delete(record)
        db.commit()
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "artifact_skill_evidence")
        raise
    except Exception:
        db.rollback()
        raise
