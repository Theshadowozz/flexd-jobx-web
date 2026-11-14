from decimal import Decimal
from typing import Literal

from pydantic import Field

from app.schemas.common import Input, Patch, Read, Timestamps
from app.schemas.response import ApiResponse, Pagination


class ArtifactSkillEvidenceFields(Input):
    confidence_score: Decimal = Field(ge=0, le=1, max_digits=5, decimal_places=4)
    evidence_kind: Literal["direct", "inferred"]
    evidence_excerpt: str | None = Field(default=None, max_length=16000)
    evidence_location: str | None = Field(default=None, max_length=300)
    review_status: Literal[
        "ai_suggested", "candidate_confirmed", "reviewer_verified", "rejected"
    ] = "ai_suggested"


class ArtifactSkillEvidenceCreate(ArtifactSkillEvidenceFields):
    artifact_id: int = Field(gt=0, le=18446744073709551615)
    analysis_id: int = Field(gt=0, le=18446744073709551615)
    skill_id: int = Field(gt=0, le=18446744073709551615)


class ArtifactSkillEvidenceUpdate(ArtifactSkillEvidenceFields, Patch):
    confidence_score: Decimal | None = Field(
        default=None, ge=0, le=1, max_digits=5, decimal_places=4
    )
    evidence_kind: Literal["direct", "inferred"] | None = None


class ArtifactSkillEvidenceRead(ArtifactSkillEvidenceFields, Timestamps):
    model_config = {"from_attributes": True}
    id: int
    artifact_id: int
    analysis_id: int
    skill_id: int


class ArtifactSkillEvidenceDetailData(Read):
    artifact_skill_evidence: ArtifactSkillEvidenceRead


class ArtifactSkillEvidenceListData(Read):
    artifact_skill_evidences: list[ArtifactSkillEvidenceRead]
    pagination: Pagination


ArtifactSkillEvidenceDetailResponse = ApiResponse[ArtifactSkillEvidenceDetailData]
ArtifactSkillEvidenceListResponse = ApiResponse[ArtifactSkillEvidenceListData]
