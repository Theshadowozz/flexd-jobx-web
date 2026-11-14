from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import mapped_column

from app.models.base import Base


class SkillAlias(Base):
    __tablename__ = "skill_alias"

    id = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    skill_id = mapped_column(
        BIGINT(unsigned=True), ForeignKey("skill.id", ondelete="CASCADE"), nullable=False
    )
    alias_name = mapped_column(String(140), nullable=False)
    normalized_alias = mapped_column(String(140), nullable=False, unique=True)
