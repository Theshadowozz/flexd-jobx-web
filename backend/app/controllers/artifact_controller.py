from sqlalchemy.orm import Session

from app.schemas import artifact as schema
from app.schemas.artifact import (
    ArtifactCreate,
    ArtifactDetailData,
    ArtifactDetailResponse,
    ArtifactListData,
    ArtifactListResponse,
    ArtifactRead,
    ArtifactUpdate,
)
from app.schemas.response import EmptyResponse, Pagination
from app.services import artifact_service


def create_artifact(db: Session, payload: ArtifactCreate) -> ArtifactDetailResponse:
    artifact = artifact_service.create_artifact(db=db, payload=payload)
    artifact_data = ArtifactRead.model_validate(artifact)
    return ArtifactDetailResponse(
        message={"success": "Data berhasil dibuat"}, data=ArtifactDetailData(artifact=artifact_data)
    )


def get_artifact(db: Session, artifact_id: int) -> ArtifactDetailResponse:
    artifact = artifact_service.get_artifact(db=db, artifact_id=artifact_id)
    artifact_data = ArtifactRead.model_validate(artifact)
    return ArtifactDetailResponse(
        message={"success": "Data berhasil diambil"},
        data=ArtifactDetailData(artifact=artifact_data),
    )


def update_artifact(
    db: Session, artifact_id: int, payload: ArtifactUpdate
) -> ArtifactDetailResponse:
    artifact = artifact_service.update_artifact(db=db, artifact_id=artifact_id, payload=payload)
    artifact_data = ArtifactRead.model_validate(artifact)
    return ArtifactDetailResponse(
        message={"success": "Data berhasil diperbarui"},
        data=ArtifactDetailData(artifact=artifact_data),
    )


def list_artifacts(
    db: Session,
    offset: int,
    limit: int,
    owner_user_id: int | None = None,
    artifact_type: schema.ArtifactType | None = None,
    visibility: schema.Visibility | None = None,
    processing_status: schema.ProcessingStatus | None = None,
    search: str | None = None,
) -> ArtifactListResponse:
    records, total = artifact_service.list_artifacts(
        db=db,
        offset=offset,
        limit=limit,
        owner_user_id=owner_user_id,
        artifact_type=artifact_type,
        visibility=visibility,
        processing_status=processing_status,
        search=search,
    )
    items = [ArtifactRead.model_validate(record) for record in records]
    return ArtifactListResponse(
        message={"success": "Daftar data berhasil diambil"},
        data=ArtifactListData(
            artifacts=items, pagination=Pagination(offset=offset, limit=limit, total=total)
        ),
    )


def delete_artifact(db: Session, artifact_id: int) -> EmptyResponse:
    artifact_service.delete_artifact(db=db, artifact_id=artifact_id)
    return EmptyResponse(message={"success": "Data berhasil dihapus"}, data={})
