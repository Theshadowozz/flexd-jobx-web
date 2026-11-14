from sqlalchemy import CheckConstraint, Enum, ForeignKey, Numeric, Text, UniqueConstraint, text
from sqlalchemy.dialects.mysql import BIGINT, DATETIME, JSON
from sqlalchemy.orm import mapped_column

from app.models.base import Base


class JobMatch(Base):
    __tablename__ = "job_match"
    __table_args__ = (
        UniqueConstraint("job_id", "candidate_user_id"),
        CheckConstraint("match_score >= 0 AND match_score <= 100"),
    )

    id = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    job_id = mapped_column(
        BIGINT(unsigned=True), ForeignKey("job_post.id", ondelete="CASCADE"), nullable=False
    )
    candidate_user_id = mapped_column(
        BIGINT(unsigned=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    match_score = mapped_column(Numeric(5, 2), nullable=False)
    score_breakdown = mapped_column(JSON(none_as_null=True), nullable=False)
    explanation = mapped_column(Text, nullable=False)
    candidate_decision = mapped_column(
        Enum("pending", "accepted", "rejected"), nullable=False, server_default="pending"
    )
    employer_decision = mapped_column(
        Enum("pending", "accepted", "rejected"), nullable=False, server_default="pending"
    )
    match_status = mapped_column(
        Enum("recommended", "one_side_interested", "mutually_accepted", "rejected", "expired"),
        nullable=False,
        server_default="recommended",
    )
    calculated_at = mapped_column(
        DATETIME, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    candidate_decided_at = mapped_column(DATETIME)
    employer_decided_at = mapped_column(DATETIME)
    updated_at = mapped_column(
        DATETIME,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )
