from typing import Literal

from sqlalchemy.orm import Session

from app.schemas.artifact_skill_evidence import (
    ArtifactSkillEvidenceCreate,
    ArtifactSkillEvidenceDetailData,
    ArtifactSkillEvidenceDetailResponse,
    ArtifactSkillEvidenceListData,
    ArtifactSkillEvidenceListResponse,
    ArtifactSkillEvidenceRead,
    ArtifactSkillEvidenceUpdate,
)
from app.schemas.response import EmptyResponse, Pagination
from app.services import artifact_skill_evidence_service


def create_artifact_skill_evidence(
    db: Session, payload: ArtifactSkillEvidenceCreate
) -> ArtifactSkillEvidenceDetailResponse:
    artifact_skill_evidence = artifact_skill_evidence_service.create_artifact_skill_evidence(
        db=db, payload=payload
    )
    artifact_skill_evidence_data = ArtifactSkillEvidenceRead.model_validate(artifact_skill_evidence)
    return ArtifactSkillEvidenceDetailResponse(
        message={"success": "Data berhasil dibuat"},
        data=ArtifactSkillEvidenceDetailData(artifact_skill_evidence=artifact_skill_evidence_data),
    )


def get_artifact_skill_evidence(
    db: Session, artifact_skill_evidence_id: int
) -> ArtifactSkillEvidenceDetailResponse:
    artifact_skill_evidence = artifact_skill_evidence_service.get_artifact_skill_evidence(
        db=db, artifact_skill_evidence_id=artifact_skill_evidence_id
    )
    artifact_skill_evidence_data = ArtifactSkillEvidenceRead.model_validate(artifact_skill_evidence)
    return ArtifactSkillEvidenceDetailResponse(
        message={"success": "Data berhasil diambil"},
        data=ArtifactSkillEvidenceDetailData(artifact_skill_evidence=artifact_skill_evidence_data),
    )


def update_artifact_skill_evidence(
    db: Session, artifact_skill_evidence_id: int, payload: ArtifactSkillEvidenceUpdate
) -> ArtifactSkillEvidenceDetailResponse:
    artifact_skill_evidence = artifact_skill_evidence_service.update_artifact_skill_evidence(
        db=db, artifact_skill_evidence_id=artifact_skill_evidence_id, payload=payload
    )
    artifact_skill_evidence_data = ArtifactSkillEvidenceRead.model_validate(artifact_skill_evidence)
    return ArtifactSkillEvidenceDetailResponse(
        message={"success": "Data berhasil diperbarui"},
        data=ArtifactSkillEvidenceDetailData(artifact_skill_evidence=artifact_skill_evidence_data),
    )


def list_artifact_skill_evidences(
    db: Session,
    offset: int,
    limit: int,
    artifact_id: int | None = None,
    analysis_id: int | None = None,
    skill_id: int | None = None,
    review_status: Literal["ai_suggested", "candidate_confirmed", "reviewer_verified", "rejected"]
    | None = None,
) -> ArtifactSkillEvidenceListResponse:
    records, total = artifact_skill_evidence_service.list_artifact_skill_evidences(
        db=db,
        offset=offset,
        limit=limit,
        artifact_id=artifact_id,
        analysis_id=analysis_id,
        skill_id=skill_id,
        review_status=review_status,
    )
    items = [ArtifactSkillEvidenceRead.model_validate(record) for record in records]
    return ArtifactSkillEvidenceListResponse(
        message={"success": "Daftar data berhasil diambil"},
        data=ArtifactSkillEvidenceListData(
            artifact_skill_evidences=items,
            pagination=Pagination(offset=offset, limit=limit, total=total),
        ),
    )


def delete_artifact_skill_evidence(db: Session, artifact_skill_evidence_id: int) -> EmptyResponse:
    artifact_skill_evidence_service.delete_artifact_skill_evidence(
        db=db, artifact_skill_evidence_id=artifact_skill_evidence_id
    )
    return EmptyResponse(message={"success": "Data berhasil dihapus"}, data={})
