from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.configs.dependencies import require_admin
from app.controllers import artifact_controller
from app.schemas import artifact as schema
from app.schemas.artifact import (
    ArtifactCreate,
    ArtifactDetailResponse,
    ArtifactListResponse,
    ArtifactUpdate,
)
from app.schemas.response import EmptyResponse

router = APIRouter(prefix="/artifacts", tags=["Artifacts"], dependencies=[Depends(require_admin)])


@router.post("", response_model=ArtifactDetailResponse, status_code=201)
def create_artifact(
    payload: ArtifactCreate,
    db: Session = Depends(get_db),
) -> ArtifactDetailResponse:
    return artifact_controller.create_artifact(db=db, payload=payload)


@router.get("", response_model=ArtifactListResponse, status_code=200)
def list_artifacts(
    db: Session = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    owner_user_id: int | None = Query(default=None, gt=0, le=18446744073709551615),
    artifact_type: schema.ArtifactType | None = Query(default=None),
    visibility: schema.Visibility | None = Query(default=None),
    processing_status: schema.ProcessingStatus | None = Query(default=None),
    search: str | None = Query(default=None, max_length=200),
) -> ArtifactListResponse:
    return artifact_controller.list_artifacts(
        db=db,
        offset=offset,
        limit=limit,
        owner_user_id=owner_user_id,
        artifact_type=artifact_type,
        visibility=visibility,
        processing_status=processing_status,
        search=search,
    )


@router.get("/{artifact_id}", response_model=ArtifactDetailResponse, status_code=200)
def get_artifact(
    artifact_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> ArtifactDetailResponse:
    return artifact_controller.get_artifact(db=db, artifact_id=artifact_id)


@router.patch("/{artifact_id}", response_model=ArtifactDetailResponse, status_code=200)
def update_artifact(
    payload: ArtifactUpdate,
    artifact_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> ArtifactDetailResponse:
    return artifact_controller.update_artifact(db=db, payload=payload, artifact_id=artifact_id)


@router.delete("/{artifact_id}", response_model=EmptyResponse, status_code=200)
def delete_artifact(
    artifact_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> EmptyResponse:
    return artifact_controller.delete_artifact(db=db, artifact_id=artifact_id)
