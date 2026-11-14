from typing import Literal

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.configs.dependencies import require_admin
from app.controllers import artifact_contribution_controller
from app.schemas.artifact_contribution import (
    ArtifactContributionCreate,
    ArtifactContributionDetailResponse,
    ArtifactContributionListResponse,
    ArtifactContributionUpdate,
)
from app.schemas.response import EmptyResponse

router = APIRouter(
    prefix="/artifact-contributions",
    tags=["Artifact contributions"],
    dependencies=[Depends(require_admin)],
)


@router.post("", response_model=ArtifactContributionDetailResponse, status_code=201)
def create_artifact_contribution(
    payload: ArtifactContributionCreate,
    db: Session = Depends(get_db),
) -> ArtifactContributionDetailResponse:
    return artifact_contribution_controller.create_artifact_contribution(db=db, payload=payload)


@router.get("", response_model=ArtifactContributionListResponse, status_code=200)
def list_artifact_contributions(
    db: Session = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    artifact_id: int | None = Query(default=None, gt=0, le=18446744073709551615),
    contributor_user_id: int | None = Query(default=None, gt=0, le=18446744073709551615),
    claim_status: Literal["self_declared", "peer_confirmed", "organization_confirmed"]
    | None = Query(default=None),
) -> ArtifactContributionListResponse:
    return artifact_contribution_controller.list_artifact_contributions(
        db=db,
        offset=offset,
        limit=limit,
        artifact_id=artifact_id,
        contributor_user_id=contributor_user_id,
        claim_status=claim_status,
    )


@router.get(
    "/{artifact_contribution_id}",
    response_model=ArtifactContributionDetailResponse,
    status_code=200,
)
def get_artifact_contribution(
    artifact_contribution_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> ArtifactContributionDetailResponse:
    return artifact_contribution_controller.get_artifact_contribution(
        db=db, artifact_contribution_id=artifact_contribution_id
    )


@router.patch(
    "/{artifact_contribution_id}",
    response_model=ArtifactContributionDetailResponse,
    status_code=200,
)
def update_artifact_contribution(
    payload: ArtifactContributionUpdate,
    artifact_contribution_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> ArtifactContributionDetailResponse:
    return artifact_contribution_controller.update_artifact_contribution(
        db=db, payload=payload, artifact_contribution_id=artifact_contribution_id
    )


@router.delete("/{artifact_contribution_id}", response_model=EmptyResponse, status_code=200)
def delete_artifact_contribution(
    artifact_contribution_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> EmptyResponse:
    return artifact_contribution_controller.delete_artifact_contribution(
        db=db, artifact_contribution_id=artifact_contribution_id
    )
