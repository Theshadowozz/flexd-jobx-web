from sqlalchemy import ForeignKey, String, Text, text
from sqlalchemy.dialects.mysql import BIGINT, DATETIME
from sqlalchemy.orm import mapped_column

from app.models.base import Base


class CompanyProfile(Base):
    __tablename__ = "company_profile"

    id = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    name = mapped_column(String(180), nullable=False)
    industry = mapped_column(String(120))
    description = mapped_column(Text)
    logo_storage_key = mapped_column(String(500))
    city = mapped_column(String(120))
    province = mapped_column(String(120))
    country = mapped_column(String(100), nullable=False, server_default="Indonesia")
    created_at = mapped_column(DATETIME, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = mapped_column(
        DATETIME,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )
