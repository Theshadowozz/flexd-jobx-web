from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.configs.dependencies import require_admin
from app.controllers import artifact_analysis_controller
from app.schemas import artifact_analysis as schema
from app.schemas.artifact_analysis import (
    ArtifactAnalysisCreate,
    ArtifactAnalysisDetailResponse,
    ArtifactAnalysisListResponse,
    ArtifactAnalysisUpdate,
)
from app.schemas.response import EmptyResponse

router = APIRouter(
    prefix="/artifact-analyses", tags=["Artifact analyses"], dependencies=[Depends(require_admin)]
)


@router.post("", response_model=ArtifactAnalysisDetailResponse, status_code=201)
def create_artifact_analysis(
    payload: ArtifactAnalysisCreate,
    db: Session = Depends(get_db),
) -> ArtifactAnalysisDetailResponse:
    return artifact_analysis_controller.create_artifact_analysis(db=db, payload=payload)


@router.get("", response_model=ArtifactAnalysisListResponse, status_code=200)
def list_artifact_analyses(
    db: Session = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    artifact_id: int | None = Query(default=None, gt=0, le=18446744073709551615),
    analysis_status: schema.AnalysisStatus | None = Query(default=None),
    reviewed_by_user_id: int | None = Query(default=None, gt=0, le=18446744073709551615),
) -> ArtifactAnalysisListResponse:
    return artifact_analysis_controller.list_artifact_analyses(
        db=db,
        offset=offset,
        limit=limit,
        artifact_id=artifact_id,
        analysis_status=analysis_status,
        reviewed_by_user_id=reviewed_by_user_id,
    )


@router.get(
    "/{artifact_analysis_id}", response_model=ArtifactAnalysisDetailResponse, status_code=200
)
def get_artifact_analysis(
    artifact_analysis_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> ArtifactAnalysisDetailResponse:
    return artifact_analysis_controller.get_artifact_analysis(
        db=db, artifact_analysis_id=artifact_analysis_id
    )


@router.patch(
    "/{artifact_analysis_id}", response_model=ArtifactAnalysisDetailResponse, status_code=200
)
def update_artifact_analysis(
    payload: ArtifactAnalysisUpdate,
    artifact_analysis_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> ArtifactAnalysisDetailResponse:
    return artifact_analysis_controller.update_artifact_analysis(
        db=db, payload=payload, artifact_analysis_id=artifact_analysis_id
    )


@router.delete("/{artifact_analysis_id}", response_model=EmptyResponse, status_code=200)
def delete_artifact_analysis(
    artifact_analysis_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> EmptyResponse:
    return artifact_analysis_controller.delete_artifact_analysis(
        db=db, artifact_analysis_id=artifact_analysis_id
    )
