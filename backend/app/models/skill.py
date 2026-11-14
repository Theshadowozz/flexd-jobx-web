from sqlalchemy import ForeignKey, String, Text, text
from sqlalchemy.dialects.mysql import BIGINT, DATETIME
from sqlalchemy.orm import mapped_column

from app.models.base import Base


class Skill(Base):
    __tablename__ = "skill"

    id = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    canonical_name = mapped_column(String(120), nullable=False)
    slug = mapped_column(String(140), nullable=False, unique=True)
    category = mapped_column(String(100))
    description = mapped_column(Text)
    parent_skill_id = mapped_column(
        BIGINT(unsigned=True), ForeignKey("skill.id", ondelete="SET NULL")
    )
    taxonomy_source = mapped_column(String(120))
    created_at = mapped_column(DATETIME, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
