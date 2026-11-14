from sqlalchemy import CheckConstraint, Enum, ForeignKey, Numeric, String, UniqueConstraint, text
from sqlalchemy.dialects.mysql import BIGINT, DATETIME
from sqlalchemy.orm import mapped_column

from app.models.base import Base


class JobSkillRequirement(Base):
    __tablename__ = "job_skill_requirement"
    __table_args__ = (UniqueConstraint("job_id", "skill_id"), CheckConstraint("weight >= 0"))

    id = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    job_id = mapped_column(
        BIGINT(unsigned=True), ForeignKey("job_post.id", ondelete="CASCADE"), nullable=False
    )
    skill_id = mapped_column(
        BIGINT(unsigned=True), ForeignKey("skill.id", ondelete="RESTRICT"), nullable=False
    )
    requirement_type = mapped_column(
        Enum("must_have", "preferred"), nullable=False, server_default="must_have"
    )
    minimum_level = mapped_column(Enum("beginner", "intermediate", "advanced", "expert"))
    weight = mapped_column(Numeric(5, 2), nullable=False, server_default="1.00")
    requirement_note = mapped_column(String(500))
    created_at = mapped_column(DATETIME, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
