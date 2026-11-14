from sqlalchemy import CheckConstraint, Date, Enum, ForeignKey, String, Text, text
from sqlalchemy.dialects.mysql import BIGINT, DATETIME, JSON
from sqlalchemy.orm import mapped_column

from app.models.base import Base


class Artifact(Base):
    __tablename__ = "artifact"
    __table_args__ = (CheckConstraint("source_url IS NOT NULL OR storage_key IS NOT NULL"),)

    id = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    owner_user_id = mapped_column(
        BIGINT(unsigned=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    title = mapped_column(String(200), nullable=False)
    artifact_type = mapped_column(
        Enum(
            "github_repository", "document", "spreadsheet", "image", "video", "design_link", "other"
        ),
        nullable=False,
    )
    description = mapped_column(Text)
    source_url = mapped_column(String(1000))
    storage_key = mapped_column(String(500))
    mime_type = mapped_column(String(150))
    visibility = mapped_column(
        Enum("private", "unlisted", "matching_employers", "public"),
        nullable=False,
        server_default="matching_employers",
    )
    project_started_at = mapped_column(Date)
    project_completed_at = mapped_column(Date)
    processing_status = mapped_column(
        Enum("not_started", "queued", "processing", "completed", "failed", "needs_review"),
        nullable=False,
        server_default="not_started",
    )
    metadata_json = mapped_column("metadata", JSON(none_as_null=True))
    created_at = mapped_column(DATETIME, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = mapped_column(
        DATETIME,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )
