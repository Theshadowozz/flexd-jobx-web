from sqlalchemy import Enum, ForeignKey, String, Text, text
from sqlalchemy.dialects.mysql import BIGINT, DATETIME, JSON
from sqlalchemy.orm import mapped_column

from app.models.base import Base


class ArtifactAnalysis(Base):
    __tablename__ = "artifact_analysis"

    id = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    artifact_id = mapped_column(
        BIGINT(unsigned=True), ForeignKey("artifact.id", ondelete="CASCADE"), nullable=False
    )
    analysis_status = mapped_column(
        Enum("queued", "processing", "completed", "failed", "needs_human_review"),
        nullable=False,
        server_default="queued",
    )
    model_provider = mapped_column(String(80))
    model_name = mapped_column(String(120))
    prompt_version = mapped_column(String(80))
    extracted_summary = mapped_column(Text)
    raw_result = mapped_column(JSON(none_as_null=True))
    error_message = mapped_column(Text)
    reviewed_by_user_id = mapped_column(
        BIGINT(unsigned=True), ForeignKey("user.id", ondelete="SET NULL")
    )
    reviewed_at = mapped_column(DATETIME)
    created_at = mapped_column(DATETIME, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
