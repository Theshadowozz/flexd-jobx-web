from typing import Literal

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.configs.dependencies import require_admin
from app.controllers import artifact_skill_evidence_controller
from app.schemas.artifact_skill_evidence import (
    ArtifactSkillEvidenceCreate,
    ArtifactSkillEvidenceDetailResponse,
    ArtifactSkillEvidenceListResponse,
    ArtifactSkillEvidenceUpdate,
)
from app.schemas.response import EmptyResponse

router = APIRouter(
    prefix="/artifact-skill-evidences",
    tags=["Artifact skill evidences"],
    dependencies=[Depends(require_admin)],
)


@router.post("", response_model=ArtifactSkillEvidenceDetailResponse, status_code=201)
def create_artifact_skill_evidence(
    payload: ArtifactSkillEvidenceCreate,
    db: Session = Depends(get_db),
) -> ArtifactSkillEvidenceDetailResponse:
    return artifact_skill_evidence_controller.create_artifact_skill_evidence(db=db, payload=payload)


@router.get("", response_model=ArtifactSkillEvidenceListResponse, status_code=200)
def list_artifact_skill_evidences(
    db: Session = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    artifact_id: int | None = Query(default=None, gt=0, le=18446744073709551615),
    analysis_id: int | None = Query(default=None, gt=0, le=18446744073709551615),
    skill_id: int | None = Query(default=None, gt=0, le=18446744073709551615),
    review_status: Literal["ai_suggested", "candidate_confirmed", "reviewer_verified", "rejected"]
    | None = Query(default=None),
) -> ArtifactSkillEvidenceListResponse:
    return artifact_skill_evidence_controller.list_artifact_skill_evidences(
        db=db,
        offset=offset,
        limit=limit,
        artifact_id=artifact_id,
        analysis_id=analysis_id,
        skill_id=skill_id,
        review_status=review_status,
    )


@router.get(
    "/{artifact_skill_evidence_id}",
    response_model=ArtifactSkillEvidenceDetailResponse,
    status_code=200,
)
def get_artifact_skill_evidence(
    artifact_skill_evidence_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> ArtifactSkillEvidenceDetailResponse:
    return artifact_skill_evidence_controller.get_artifact_skill_evidence(
        db=db, artifact_skill_evidence_id=artifact_skill_evidence_id
    )


@router.patch(
    "/{artifact_skill_evidence_id}",
    response_model=ArtifactSkillEvidenceDetailResponse,
    status_code=200,
)
def update_artifact_skill_evidence(
    payload: ArtifactSkillEvidenceUpdate,
    artifact_skill_evidence_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> ArtifactSkillEvidenceDetailResponse:
    return artifact_skill_evidence_controller.update_artifact_skill_evidence(
        db=db, payload=payload, artifact_skill_evidence_id=artifact_skill_evidence_id
    )


@router.delete("/{artifact_skill_evidence_id}", response_model=EmptyResponse, status_code=200)
def delete_artifact_skill_evidence(
    artifact_skill_evidence_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> EmptyResponse:
    return artifact_skill_evidence_controller.delete_artifact_skill_evidence(
        db=db, artifact_skill_evidence_id=artifact_skill_evidence_id
    )
