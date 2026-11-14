from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.models.artifact import Artifact
from app.models.user import User
from app.schemas import artifact as schema
from app.schemas.artifact import ArtifactCreate, ArtifactUpdate
from app.utils.database_errors import translate_database_error
from app.utils.exceptions import AppError


def get_artifact(db: Session, artifact_id: int) -> Artifact:
    statement = select(Artifact).where(Artifact.id == artifact_id)
    artifact = db.scalar(statement)
    if artifact is None:
        raise AppError(
            status_code=404, category="not_found", errors={"artifact": "Data tidak ditemukan"}
        )
    return artifact


def list_artifacts(
    db: Session,
    offset: int,
    limit: int,
    owner_user_id: int | None = None,
    artifact_type: schema.ArtifactType | None = None,
    visibility: schema.Visibility | None = None,
    processing_status: schema.ProcessingStatus | None = None,
    search: str | None = None,
) -> tuple[list[Artifact], int]:
    conditions = []
    if owner_user_id is not None:
        conditions.append(Artifact.owner_user_id == owner_user_id)
    if artifact_type is not None:
        conditions.append(Artifact.artifact_type == artifact_type)
    if visibility is not None:
        conditions.append(Artifact.visibility == visibility)
    if processing_status is not None:
        conditions.append(Artifact.processing_status == processing_status)
    if search:
        conditions.append(Artifact.title.contains(search, autoescape=True))
    total_statement = select(func.count()).select_from(Artifact).where(*conditions)
    total = db.scalar(total_statement) or 0
    statement = (
        select(Artifact).where(*conditions).order_by(Artifact.id).offset(offset).limit(limit)
    )
    records = list(db.scalars(statement).all())
    return (records, total)


def create_artifact(db: Session, payload: ArtifactCreate) -> Artifact:
    try:
        record = None
        values = {
            "title": payload.title,
            "artifact_type": payload.artifact_type,
            "description": payload.description,
            "source_url": payload.source_url,
            "storage_key": payload.storage_key,
            "mime_type": payload.mime_type,
            "visibility": payload.visibility,
            "project_started_at": payload.project_started_at,
            "project_completed_at": payload.project_completed_at,
            "processing_status": payload.processing_status,
            "metadata": payload.metadata,
            "owner_user_id": payload.owner_user_id,
        }
        payload.model_dump()
        if values["owner_user_id"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"owner_user_id": "Field tidak boleh null"},
            )
        if values["owner_user_id"] is not None:
            referenced_owner_user_id = db.scalar(
                select(User)
                .where(User.id == values["owner_user_id"])
                .with_for_update(read=True)
                .execution_options(populate_existing=True)
            )
            if referenced_owner_user_id is None:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"owner_user_id": "Referensi tidak ditemukan"},
                )
        if values["title"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"title": "Field tidak boleh null"},
            )
        if values["artifact_type"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"artifact_type": "Field tidak boleh null"},
            )
        if values["visibility"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"visibility": "Field tidak boleh null"},
            )
        if values["processing_status"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"processing_status": "Field tidak boleh null"},
            )
        for low, high in (("project_started_at", "project_completed_at"),):
            if (
                values.get(low) is not None
                and values.get(high) is not None
                and (values[low] > values[high])
            ):
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={high: "Nilai akhir tidak boleh lebih kecil dari nilai awal"},
                )
        if not (values.get("source_url") or values.get("storage_key")):
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"source_url": "Isi source_url atau storage_key"},
            )
        record = Artifact(
            title=values["title"],
            artifact_type=values["artifact_type"],
            description=values["description"],
            source_url=values["source_url"],
            storage_key=values["storage_key"],
            mime_type=values["mime_type"],
            visibility=values["visibility"],
            project_started_at=values["project_started_at"],
            project_completed_at=values["project_completed_at"],
            processing_status=values["processing_status"],
            metadata_json=values["metadata"],
            owner_user_id=values["owner_user_id"],
        )
        db.add(record)
        db.flush()
        db.refresh(record)
        db.commit()
        return record
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "artifact")
        raise
    except Exception:
        db.rollback()
        raise


def update_artifact(db: Session, artifact_id: int, payload: ArtifactUpdate) -> Artifact:
    try:
        statement = (
            select(Artifact)
            .where(Artifact.id == artifact_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        record = db.scalar(statement)
        if record is None:
            raise AppError(
                status_code=404, category="not_found", errors={"artifact": "Data tidak ditemukan"}
            )
        values = {
            "title": payload.title if "title" in payload.model_fields_set else record.title,
            "artifact_type": payload.artifact_type
            if "artifact_type" in payload.model_fields_set
            else record.artifact_type,
            "description": payload.description
            if "description" in payload.model_fields_set
            else record.description,
            "source_url": payload.source_url
            if "source_url" in payload.model_fields_set
            else record.source_url,
            "storage_key": payload.storage_key
            if "storage_key" in payload.model_fields_set
            else record.storage_key,
            "mime_type": payload.mime_type
            if "mime_type" in payload.model_fields_set
            else record.mime_type,
            "visibility": payload.visibility
            if "visibility" in payload.model_fields_set
            else record.visibility,
            "project_started_at": payload.project_started_at
            if "project_started_at" in payload.model_fields_set
            else record.project_started_at,
            "project_completed_at": payload.project_completed_at
            if "project_completed_at" in payload.model_fields_set
            else record.project_completed_at,
            "processing_status": payload.processing_status
            if "processing_status" in payload.model_fields_set
            else record.processing_status,
            "metadata": payload.metadata
            if "metadata" in payload.model_fields_set
            else record.metadata_json,
            "owner_user_id": record.owner_user_id,
        }
        payload.model_dump(exclude_unset=True)
        if values["owner_user_id"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"owner_user_id": "Field tidak boleh null"},
            )
        if values["owner_user_id"] is not None:
            referenced_owner_user_id = db.scalar(
                select(User)
                .where(User.id == values["owner_user_id"])
                .with_for_update(read=True)
                .execution_options(populate_existing=True)
            )
            if referenced_owner_user_id is None:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"owner_user_id": "Referensi tidak ditemukan"},
                )
        if values["title"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"title": "Field tidak boleh null"},
            )
        if values["artifact_type"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"artifact_type": "Field tidak boleh null"},
            )
        if values["visibility"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"visibility": "Field tidak boleh null"},
            )
        if values["processing_status"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"processing_status": "Field tidak boleh null"},
            )
        for low, high in (("project_started_at", "project_completed_at"),):
            if (
                values.get(low) is not None
                and values.get(high) is not None
                and (values[low] > values[high])
            ):
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={high: "Nilai akhir tidak boleh lebih kecil dari nilai awal"},
                )
        if not (values.get("source_url") or values.get("storage_key")):
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"source_url": "Isi source_url atau storage_key"},
            )
        if "title" in payload.model_fields_set:
            record.title = values["title"]
        if "artifact_type" in payload.model_fields_set:
            record.artifact_type = values["artifact_type"]
        if "description" in payload.model_fields_set:
            record.description = values["description"]
        if "source_url" in payload.model_fields_set:
            record.source_url = values["source_url"]
        if "storage_key" in payload.model_fields_set:
            record.storage_key = values["storage_key"]
        if "mime_type" in payload.model_fields_set:
            record.mime_type = values["mime_type"]
        if "visibility" in payload.model_fields_set:
            record.visibility = values["visibility"]
        if "project_started_at" in payload.model_fields_set:
            record.project_started_at = values["project_started_at"]
        if "project_completed_at" in payload.model_fields_set:
            record.project_completed_at = values["project_completed_at"]
        if "processing_status" in payload.model_fields_set:
            record.processing_status = values["processing_status"]
        if "metadata" in payload.model_fields_set:
            record.metadata_json = values["metadata"]
        db.flush()
        db.refresh(record)
        db.commit()
        return record
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "artifact")
        raise
    except Exception:
        db.rollback()
        raise


def delete_artifact(db: Session, artifact_id: int) -> None:
    try:
        statement = (
            select(Artifact)
            .where(Artifact.id == artifact_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        record = db.scalar(statement)
        if record is None:
            raise AppError(
                status_code=404, category="not_found", errors={"artifact": "Data tidak ditemukan"}
            )
        db.delete(record)
        db.commit()
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "artifact")
        raise
    except Exception:
        db.rollback()
        raise
