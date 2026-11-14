from typing import Literal

from sqlalchemy.orm import Session

from app.schemas.artifact_contribution import (
    ArtifactContributionCreate,
    ArtifactContributionDetailData,
    ArtifactContributionDetailResponse,
    ArtifactContributionListData,
    ArtifactContributionListResponse,
    ArtifactContributionRead,
    ArtifactContributionUpdate,
)
from app.schemas.response import EmptyResponse, Pagination
from app.services import artifact_contribution_service


def create_artifact_contribution(
    db: Session, payload: ArtifactContributionCreate
) -> ArtifactContributionDetailResponse:
    artifact_contribution = artifact_contribution_service.create_artifact_contribution(
        db=db, payload=payload
    )
    artifact_contribution_data = ArtifactContributionRead.model_validate(artifact_contribution)
    return ArtifactContributionDetailResponse(
        message={"success": "Data berhasil dibuat"},
        data=ArtifactContributionDetailData(artifact_contribution=artifact_contribution_data),
    )


def get_artifact_contribution(
    db: Session, artifact_contribution_id: int
) -> ArtifactContributionDetailResponse:
    artifact_contribution = artifact_contribution_service.get_artifact_contribution(
        db=db, artifact_contribution_id=artifact_contribution_id
    )
    artifact_contribution_data = ArtifactContributionRead.model_validate(artifact_contribution)
    return ArtifactContributionDetailResponse(
        message={"success": "Data berhasil diambil"},
        data=ArtifactContributionDetailData(artifact_contribution=artifact_contribution_data),
    )


def update_artifact_contribution(
    db: Session, artifact_contribution_id: int, payload: ArtifactContributionUpdate
) -> ArtifactContributionDetailResponse:
    artifact_contribution = artifact_contribution_service.update_artifact_contribution(
        db=db, artifact_contribution_id=artifact_contribution_id, payload=payload
    )
    artifact_contribution_data = ArtifactContributionRead.model_validate(artifact_contribution)
    return ArtifactContributionDetailResponse(
        message={"success": "Data berhasil diperbarui"},
        data=ArtifactContributionDetailData(artifact_contribution=artifact_contribution_data),
    )


def list_artifact_contributions(
    db: Session,
    offset: int,
    limit: int,
    artifact_id: int | None = None,
    contributor_user_id: int | None = None,
    claim_status: Literal["self_declared", "peer_confirmed", "organization_confirmed"]
    | None = None,
) -> ArtifactContributionListResponse:
    records, total = artifact_contribution_service.list_artifact_contributions(
        db=db,
        offset=offset,
        limit=limit,
        artifact_id=artifact_id,
        contributor_user_id=contributor_user_id,
        claim_status=claim_status,
    )
    items = [ArtifactContributionRead.model_validate(record) for record in records]
    return ArtifactContributionListResponse(
        message={"success": "Daftar data berhasil diambil"},
        data=ArtifactContributionListData(
            artifact_contributions=items,
            pagination=Pagination(offset=offset, limit=limit, total=total),
        ),
    )


def delete_artifact_contribution(db: Session, artifact_contribution_id: int) -> EmptyResponse:
    artifact_contribution_service.delete_artifact_contribution(
        db=db, artifact_contribution_id=artifact_contribution_id
    )
    return EmptyResponse(message={"success": "Data berhasil dihapus"}, data={})
