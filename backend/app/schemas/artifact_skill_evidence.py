from typing import Literal

from pydantic import Field

from app.schemas.common import Confidence, Input, Patch, Timestamps, UnsignedId

EvidenceKind = Literal["direct", "inferred"]
ReviewStatus = Literal["ai_suggested", "candidate_confirmed", "reviewer_verified", "rejected"]


class ArtifactSkillEvidenceCreate(Input):
    artifact_id: UnsignedId
    analysis_id: UnsignedId
    skill_id: UnsignedId
    confidence_score: Confidence
    evidence_kind: EvidenceKind
    evidence_excerpt: str | None = None
    evidence_location: str | None = Field(default=None, max_length=300)
    review_status: ReviewStatus = "ai_suggested"


class ArtifactSkillEvidenceUpdate(Patch):
    confidence_score: Confidence | None = None
    evidence_kind: EvidenceKind | None = None
    evidence_excerpt: str | None = None
    evidence_location: str | None = Field(default=None, max_length=300)
    review_status: ReviewStatus | None = None


class ArtifactSkillEvidenceRead(Timestamps):
    id: UnsignedId
    artifact_id: UnsignedId
    analysis_id: UnsignedId
    skill_id: UnsignedId
    confidence_score: Confidence
    evidence_kind: str
    evidence_excerpt: str | None
    evidence_location: str | None
    review_status: str
