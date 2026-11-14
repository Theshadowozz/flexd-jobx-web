from sqlalchemy.orm import Session

from app.schemas import artifact_analysis as schema
from app.schemas.artifact_analysis import (
    ArtifactAnalysisCreate,
    ArtifactAnalysisDetailData,
    ArtifactAnalysisDetailResponse,
    ArtifactAnalysisListData,
    ArtifactAnalysisListResponse,
    ArtifactAnalysisRead,
    ArtifactAnalysisUpdate,
)
from app.schemas.response import EmptyResponse, Pagination
from app.services import artifact_analysis_service


def create_artifact_analysis(
    db: Session, payload: ArtifactAnalysisCreate
) -> ArtifactAnalysisDetailResponse:
    artifact_analysis = artifact_analysis_service.create_artifact_analysis(db=db, payload=payload)
    artifact_analysis_data = ArtifactAnalysisRead.model_validate(artifact_analysis)
    return ArtifactAnalysisDetailResponse(
        message={"success": "Data berhasil dibuat"},
        data=ArtifactAnalysisDetailData(artifact_analysis=artifact_analysis_data),
    )


def get_artifact_analysis(db: Session, artifact_analysis_id: int) -> ArtifactAnalysisDetailResponse:
    artifact_analysis = artifact_analysis_service.get_artifact_analysis(
        db=db, artifact_analysis_id=artifact_analysis_id
    )
    artifact_analysis_data = ArtifactAnalysisRead.model_validate(artifact_analysis)
    return ArtifactAnalysisDetailResponse(
        message={"success": "Data berhasil diambil"},
        data=ArtifactAnalysisDetailData(artifact_analysis=artifact_analysis_data),
    )


def update_artifact_analysis(
    db: Session, artifact_analysis_id: int, payload: ArtifactAnalysisUpdate
) -> ArtifactAnalysisDetailResponse:
    artifact_analysis = artifact_analysis_service.update_artifact_analysis(
        db=db, artifact_analysis_id=artifact_analysis_id, payload=payload
    )
    artifact_analysis_data = ArtifactAnalysisRead.model_validate(artifact_analysis)
    return ArtifactAnalysisDetailResponse(
        message={"success": "Data berhasil diperbarui"},
        data=ArtifactAnalysisDetailData(artifact_analysis=artifact_analysis_data),
    )


def list_artifact_analyses(
    db: Session,
    offset: int,
    limit: int,
    artifact_id: int | None = None,
    analysis_status: schema.AnalysisStatus | None = None,
    reviewed_by_user_id: int | None = None,
) -> ArtifactAnalysisListResponse:
    records, total = artifact_analysis_service.list_artifact_analyses(
        db=db,
        offset=offset,
        limit=limit,
        artifact_id=artifact_id,
        analysis_status=analysis_status,
        reviewed_by_user_id=reviewed_by_user_id,
    )
    items = [ArtifactAnalysisRead.model_validate(record) for record in records]
    return ArtifactAnalysisListResponse(
        message={"success": "Daftar data berhasil diambil"},
        data=ArtifactAnalysisListData(
            artifact_analyses=items, pagination=Pagination(offset=offset, limit=limit, total=total)
        ),
    )


def delete_artifact_analysis(db: Session, artifact_analysis_id: int) -> EmptyResponse:
    artifact_analysis_service.delete_artifact_analysis(
        db=db, artifact_analysis_id=artifact_analysis_id
    )
    return EmptyResponse(message={"success": "Data berhasil dihapus"}, data={})
