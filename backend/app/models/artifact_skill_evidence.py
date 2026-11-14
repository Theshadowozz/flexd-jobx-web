from sqlalchemy import (
    CheckConstraint,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.mysql import BIGINT, DATETIME
from sqlalchemy.orm import mapped_column

from app.models.base import Base


class ArtifactSkillEvidence(Base):
    __tablename__ = "artifact_skill_evidence"
    __table_args__ = (
        UniqueConstraint("analysis_id", "skill_id"),
        CheckConstraint("confidence_score >= 0 AND confidence_score <= 1"),
    )

    id = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    artifact_id = mapped_column(
        BIGINT(unsigned=True), ForeignKey("artifact.id", ondelete="CASCADE"), nullable=False
    )
    analysis_id = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("artifact_analysis.id", ondelete="CASCADE"),
        nullable=False,
    )
    skill_id = mapped_column(
        BIGINT(unsigned=True), ForeignKey("skill.id", ondelete="RESTRICT"), nullable=False
    )
    confidence_score = mapped_column(Numeric(5, 4), nullable=False)
    evidence_kind = mapped_column(Enum("direct", "inferred"), nullable=False)
    evidence_excerpt = mapped_column(Text)
    evidence_location = mapped_column(String(300))
    review_status = mapped_column(
        Enum("ai_suggested", "candidate_confirmed", "reviewer_verified", "rejected"),
        nullable=False,
        server_default="ai_suggested",
    )
    created_at = mapped_column(DATETIME, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = mapped_column(
        DATETIME,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )
