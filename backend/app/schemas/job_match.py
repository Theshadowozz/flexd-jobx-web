from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import Field, JsonValue

from app.schemas.common import Input, Patch, Read
from app.schemas.response import ApiResponse, Pagination

Decision = Literal["pending", "accepted", "rejected"]
MatchStatus = Literal[
    "recommended", "one_side_interested", "mutually_accepted", "rejected", "expired"
]


class JobMatchFields(Input):
    match_score: Decimal = Field(ge=0, le=100, max_digits=5, decimal_places=2)
    score_breakdown: dict[str, JsonValue]
    explanation: str = Field(min_length=1, max_length=16000)
    candidate_decision: Decision = "pending"
    employer_decision: Decision = "pending"
    match_status: MatchStatus = "recommended"


class JobMatchCreate(JobMatchFields):
    job_id: int = Field(gt=0, le=18446744073709551615)
    candidate_user_id: int = Field(gt=0, le=18446744073709551615)


class JobMatchUpdate(JobMatchFields, Patch):
    match_score: Decimal | None = Field(default=None, ge=0, le=100, max_digits=5, decimal_places=2)
    score_breakdown: dict[str, JsonValue] | None = None
    explanation: str | None = Field(default=None, min_length=1, max_length=16000)


class JobMatchRead(JobMatchFields, Read):
    model_config = {"from_attributes": True}
    id: int
    job_id: int
    candidate_user_id: int
    calculated_at: datetime
    candidate_decided_at: datetime | None
    employer_decided_at: datetime | None
    updated_at: datetime


class JobMatchDetailData(Read):
    job_match: JobMatchRead


class JobMatchListData(Read):
    job_matches: list[JobMatchRead]
    pagination: Pagination


JobMatchDetailResponse = ApiResponse[JobMatchDetailData]
JobMatchListResponse = ApiResponse[JobMatchListData]
