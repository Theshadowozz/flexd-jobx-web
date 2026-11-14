from sqlalchemy import CheckConstraint, Date, Enum, ForeignKey, Numeric, String, Text, text
from sqlalchemy.dialects.mysql import BIGINT, DATETIME
from sqlalchemy.orm import mapped_column

from app.models.base import Base


class CandidateProfile(Base):
    __tablename__ = "candidate_profile"
    __table_args__ = (
        CheckConstraint(
            "expected_salary_min IS NULL OR expected_salary_max IS NULL "
            "OR expected_salary_min <= expected_salary_max"
        ),
    )

    user_id = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
        autoincrement=False,
    )
    headline = mapped_column(String(180))
    biography = mapped_column(Text)
    city = mapped_column(String(120))
    province = mapped_column(String(120))
    country = mapped_column(String(100), nullable=False, server_default="Indonesia")
    years_experience = mapped_column(Numeric(4, 1))
    preferred_employment_type = mapped_column(
        Enum("full_time", "part_time", "contract", "internship", "freelance", "any"),
        nullable=False,
        server_default="any",
    )
    preferred_work_mode = mapped_column(
        Enum("onsite", "hybrid", "remote", "any"), nullable=False, server_default="any"
    )
    expected_salary_min = mapped_column(BIGINT(unsigned=True))
    expected_salary_max = mapped_column(BIGINT(unsigned=True))
    available_from = mapped_column(Date)
    profile_visibility = mapped_column(
        Enum("private", "matching_only", "public"), nullable=False, server_default="matching_only"
    )
    created_at = mapped_column(DATETIME, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = mapped_column(
        DATETIME,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )
