from typing import Literal

from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.models.artifact import Artifact
from app.models.artifact_contribution import ArtifactContribution
from app.models.user import User
from app.schemas.artifact_contribution import ArtifactContributionCreate, ArtifactContributionUpdate
from app.utils.database_errors import translate_database_error
from app.utils.exceptions import AppError


def get_artifact_contribution(db: Session, artifact_contribution_id: int) -> ArtifactContribution:
    statement = select(ArtifactContribution).where(
        ArtifactContribution.id == artifact_contribution_id
    )
    artifact_contribution = db.scalar(statement)
    if artifact_contribution is None:
        raise AppError(
            status_code=404,
            category="not_found",
            errors={"artifact_contribution": "Data tidak ditemukan"},
        )
    return artifact_contribution


def list_artifact_contributions(
    db: Session,
    offset: int,
    limit: int,
    artifact_id: int | None = None,
    contributor_user_id: int | None = None,
    claim_status: Literal["self_declared", "peer_confirmed", "organization_confirmed"]
    | None = None,
) -> tuple[list[ArtifactContribution], int]:
    conditions = []
    if artifact_id is not None:
        conditions.append(ArtifactContribution.artifact_id == artifact_id)
    if contributor_user_id is not None:
        conditions.append(ArtifactContribution.contributor_user_id == contributor_user_id)
    if claim_status is not None:
        conditions.append(ArtifactContribution.claim_status == claim_status)
    total_statement = select(func.count()).select_from(ArtifactContribution).where(*conditions)
    total = db.scalar(total_statement) or 0
    statement = (
        select(ArtifactContribution)
        .where(*conditions)
        .order_by(ArtifactContribution.id)
        .offset(offset)
        .limit(limit)
    )
    records = list(db.scalars(statement).all())
    return (records, total)


def create_artifact_contribution(
    db: Session, payload: ArtifactContributionCreate
) -> ArtifactContribution:
    try:
        record = None
        values = {
            "role_title": payload.role_title,
            "contribution_description": payload.contribution_description,
            "contribution_share_percent": payload.contribution_share_percent,
            "claim_status": payload.claim_status,
            "artifact_id": payload.artifact_id,
            "contributor_user_id": payload.contributor_user_id,
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
        if values["contributor_user_id"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"contributor_user_id": "Field tidak boleh null"},
            )
        if values["contributor_user_id"] is not None:
            referenced_contributor_user_id = db.scalar(
                select(User)
                .where(User.id == values["contributor_user_id"])
                .with_for_update(read=True)
                .execution_options(populate_existing=True)
            )
            if referenced_contributor_user_id is None:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"contributor_user_id": "Referensi tidak ditemukan"},
                )
        if values["contribution_description"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"contribution_description": "Field tidak boleh null"},
            )
        if values["claim_status"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"claim_status": "Field tidak boleh null"},
            )
        record = ArtifactContribution(
            role_title=values["role_title"],
            contribution_description=values["contribution_description"],
            contribution_share_percent=values["contribution_share_percent"],
            claim_status=values["claim_status"],
            artifact_id=values["artifact_id"],
            contributor_user_id=values["contributor_user_id"],
        )
        db.add(record)
        db.flush()
        db.refresh(record)
        db.commit()
        return record
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "artifact_contribution")
        raise
    except Exception:
        db.rollback()
        raise


def update_artifact_contribution(
    db: Session, artifact_contribution_id: int, payload: ArtifactContributionUpdate
) -> ArtifactContribution:
    try:
        statement = (
            select(ArtifactContribution)
            .where(ArtifactContribution.id == artifact_contribution_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        record = db.scalar(statement)
        if record is None:
            raise AppError(
                status_code=404,
                category="not_found",
                errors={"artifact_contribution": "Data tidak ditemukan"},
            )
        values = {
            "role_title": payload.role_title
            if "role_title" in payload.model_fields_set
            else record.role_title,
            "contribution_description": payload.contribution_description
            if "contribution_description" in payload.model_fields_set
            else record.contribution_description,
            "contribution_share_percent": payload.contribution_share_percent
            if "contribution_share_percent" in payload.model_fields_set
            else record.contribution_share_percent,
            "claim_status": payload.claim_status
            if "claim_status" in payload.model_fields_set
            else record.claim_status,
            "artifact_id": record.artifact_id,
            "contributor_user_id": record.contributor_user_id,
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
        if values["contributor_user_id"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"contributor_user_id": "Field tidak boleh null"},
            )
        if values["contributor_user_id"] is not None:
            referenced_contributor_user_id = db.scalar(
                select(User)
                .where(User.id == values["contributor_user_id"])
                .with_for_update(read=True)
                .execution_options(populate_existing=True)
            )
            if referenced_contributor_user_id is None:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"contributor_user_id": "Referensi tidak ditemukan"},
                )
        if values["contribution_description"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"contribution_description": "Field tidak boleh null"},
            )
        if values["claim_status"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"claim_status": "Field tidak boleh null"},
            )
        if "role_title" in payload.model_fields_set:
            record.role_title = values["role_title"]
        if "contribution_description" in payload.model_fields_set:
            record.contribution_description = values["contribution_description"]
        if "contribution_share_percent" in payload.model_fields_set:
            record.contribution_share_percent = values["contribution_share_percent"]
        if "claim_status" in payload.model_fields_set:
            record.claim_status = values["claim_status"]
        db.flush()
        db.refresh(record)
        db.commit()
        return record
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "artifact_contribution")
        raise
    except Exception:
        db.rollback()
        raise


def delete_artifact_contribution(db: Session, artifact_contribution_id: int) -> None:
    try:
        statement = (
            select(ArtifactContribution)
            .where(ArtifactContribution.id == artifact_contribution_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        record = db.scalar(statement)
        if record is None:
            raise AppError(
                status_code=404,
                category="not_found",
                errors={"artifact_contribution": "Data tidak ditemukan"},
            )
        db.delete(record)
        db.commit()
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "artifact_contribution")
        raise
    except Exception:
        db.rollback()
        raise
