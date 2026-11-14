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


class ArtifactContribution(Base):
    __tablename__ = "artifact_contribution"
    __table_args__ = (
        UniqueConstraint("artifact_id", "contributor_user_id"),
        CheckConstraint(
            "contribution_share_percent IS NULL OR "
            "(contribution_share_percent >= 0 AND contribution_share_percent <= 100)"
        ),
    )

    id = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    artifact_id = mapped_column(
        BIGINT(unsigned=True), ForeignKey("artifact.id", ondelete="CASCADE"), nullable=False
    )
    contributor_user_id = mapped_column(
        BIGINT(unsigned=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    role_title = mapped_column(String(150))
    contribution_description = mapped_column(Text, nullable=False)
    contribution_share_percent = mapped_column(Numeric(5, 2))
    claim_status = mapped_column(
        Enum("self_declared", "peer_confirmed", "organization_confirmed"),
        nullable=False,
        server_default="self_declared",
    )
    created_at = mapped_column(DATETIME, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = mapped_column(
        DATETIME,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )
