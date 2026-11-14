from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.models import ArtifactAnalysis, User
from app.models.artifact import Artifact
from app.schemas import artifact_analysis as schema
from app.schemas.artifact_analysis import ArtifactAnalysisCreate, ArtifactAnalysisUpdate
from app.utils.database_errors import translate_database_error
from app.utils.exceptions import AppError


def get_artifact_analysis(db: Session, artifact_analysis_id: int) -> ArtifactAnalysis:
    statement = select(ArtifactAnalysis).where(ArtifactAnalysis.id == artifact_analysis_id)
    artifact_analysis = db.scalar(statement)
    if artifact_analysis is None:
        raise AppError(
            status_code=404,
            category="not_found",
            errors={"artifact_analysis": "Data tidak ditemukan"},
        )
    return artifact_analysis


def list_artifact_analyses(
    db: Session,
    offset: int,
    limit: int,
    artifact_id: int | None = None,
    analysis_status: schema.AnalysisStatus | None = None,
    reviewed_by_user_id: int | None = None,
) -> tuple[list[ArtifactAnalysis], int]:
    conditions = []
    if artifact_id is not None:
        conditions.append(ArtifactAnalysis.artifact_id == artifact_id)
    if analysis_status is not None:
        conditions.append(ArtifactAnalysis.analysis_status == analysis_status)
    if reviewed_by_user_id is not None:
        conditions.append(ArtifactAnalysis.reviewed_by_user_id == reviewed_by_user_id)
    total_statement = select(func.count()).select_from(ArtifactAnalysis).where(*conditions)
    total = db.scalar(total_statement) or 0
    statement = (
        select(ArtifactAnalysis)
        .where(*conditions)
        .order_by(ArtifactAnalysis.id)
        .offset(offset)
        .limit(limit)
    )
    records = list(db.scalars(statement).all())
    return (records, total)


def create_artifact_analysis(db: Session, payload: ArtifactAnalysisCreate) -> ArtifactAnalysis:
    try:
        record = None
        values = {
            "analysis_status": payload.analysis_status,
            "model_provider": payload.model_provider,
            "model_name": payload.model_name,
            "prompt_version": payload.prompt_version,
            "extracted_summary": payload.extracted_summary,
            "raw_result": payload.raw_result,
            "error_message": payload.error_message,
            "reviewed_by_user_id": payload.reviewed_by_user_id,
            "artifact_id": payload.artifact_id,
        }
        changes = payload.model_dump()
        now = datetime.now(UTC).replace(tzinfo=None)
        if "reviewed_by_user_id" in changes:
            changes["reviewed_at"] = now if changes["reviewed_by_user_id"] else None
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
        if values["analysis_status"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"analysis_status": "Field tidak boleh null"},
            )
        if values["reviewed_by_user_id"] is not None:
            referenced_reviewed_by_user_id = db.scalar(
                select(User)
                .where(User.id == values["reviewed_by_user_id"])
                .with_for_update(read=True)
                .execution_options(populate_existing=True)
            )
            if referenced_reviewed_by_user_id is None:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"reviewed_by_user_id": "Referensi tidak ditemukan"},
                )
        if values.get("reviewed_by_user_id") is not None:
            reviewer = db.get(User, values["reviewed_by_user_id"])
            if reviewer.account_type != "admin":
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"reviewed_by_user_id": "Reviewer harus admin"},
                )
        record = ArtifactAnalysis(
            analysis_status=values["analysis_status"],
            model_provider=values["model_provider"],
            model_name=values["model_name"],
            prompt_version=values["prompt_version"],
            extracted_summary=values["extracted_summary"],
            raw_result=values["raw_result"],
            error_message=values["error_message"],
            reviewed_by_user_id=values["reviewed_by_user_id"],
            artifact_id=values["artifact_id"],
            reviewed_at=changes.get("reviewed_at"),
        )
        db.add(record)
        db.flush()
        db.refresh(record)
        db.commit()
        return record
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "artifact_analysis")
        raise
    except Exception:
        db.rollback()
        raise


def update_artifact_analysis(
    db: Session, artifact_analysis_id: int, payload: ArtifactAnalysisUpdate
) -> ArtifactAnalysis:
    try:
        statement = (
            select(ArtifactAnalysis)
            .where(ArtifactAnalysis.id == artifact_analysis_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        record = db.scalar(statement)
        if record is None:
            raise AppError(
                status_code=404,
                category="not_found",
                errors={"artifact_analysis": "Data tidak ditemukan"},
            )
        values = {
            "analysis_status": payload.analysis_status
            if "analysis_status" in payload.model_fields_set
            else record.analysis_status,
            "model_provider": payload.model_provider
            if "model_provider" in payload.model_fields_set
            else record.model_provider,
            "model_name": payload.model_name
            if "model_name" in payload.model_fields_set
            else record.model_name,
            "prompt_version": payload.prompt_version
            if "prompt_version" in payload.model_fields_set
            else record.prompt_version,
            "extracted_summary": payload.extracted_summary
            if "extracted_summary" in payload.model_fields_set
            else record.extracted_summary,
            "raw_result": payload.raw_result
            if "raw_result" in payload.model_fields_set
            else record.raw_result,
            "error_message": payload.error_message
            if "error_message" in payload.model_fields_set
            else record.error_message,
            "reviewed_by_user_id": payload.reviewed_by_user_id
            if "reviewed_by_user_id" in payload.model_fields_set
            else record.reviewed_by_user_id,
            "artifact_id": record.artifact_id,
        }
        changes = payload.model_dump(exclude_unset=True)
        now = datetime.now(UTC).replace(tzinfo=None)
        if "reviewed_by_user_id" in changes:
            changes["reviewed_at"] = now if changes["reviewed_by_user_id"] else None
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
        if values["analysis_status"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"analysis_status": "Field tidak boleh null"},
            )
        if values["reviewed_by_user_id"] is not None:
            referenced_reviewed_by_user_id = db.scalar(
                select(User)
                .where(User.id == values["reviewed_by_user_id"])
                .with_for_update(read=True)
                .execution_options(populate_existing=True)
            )
            if referenced_reviewed_by_user_id is None:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"reviewed_by_user_id": "Referensi tidak ditemukan"},
                )
        if values.get("reviewed_by_user_id") is not None:
            reviewer = db.get(User, values["reviewed_by_user_id"])
            if reviewer.account_type != "admin":
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"reviewed_by_user_id": "Reviewer harus admin"},
                )
        if "analysis_status" in payload.model_fields_set:
            record.analysis_status = values["analysis_status"]
        if "model_provider" in payload.model_fields_set:
            record.model_provider = values["model_provider"]
        if "model_name" in payload.model_fields_set:
            record.model_name = values["model_name"]
        if "prompt_version" in payload.model_fields_set:
            record.prompt_version = values["prompt_version"]
        if "extracted_summary" in payload.model_fields_set:
            record.extracted_summary = values["extracted_summary"]
        if "raw_result" in payload.model_fields_set:
            record.raw_result = values["raw_result"]
        if "error_message" in payload.model_fields_set:
            record.error_message = values["error_message"]
        if "reviewed_by_user_id" in payload.model_fields_set:
            record.reviewed_by_user_id = values["reviewed_by_user_id"]
        if "reviewed_at" in changes:
            record.reviewed_at = changes["reviewed_at"]
        db.flush()
        db.refresh(record)
        db.commit()
        return record
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "artifact_analysis")
        raise
    except Exception:
        db.rollback()
        raise


def delete_artifact_analysis(db: Session, artifact_analysis_id: int) -> None:
    try:
        statement = (
            select(ArtifactAnalysis)
            .where(ArtifactAnalysis.id == artifact_analysis_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        record = db.scalar(statement)
        if record is None:
            raise AppError(
                status_code=404,
                category="not_found",
                errors={"artifact_analysis": "Data tidak ditemukan"},
            )
        db.delete(record)
        db.commit()
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "artifact_analysis")
        raise
    except Exception:
        db.rollback()
        raise
