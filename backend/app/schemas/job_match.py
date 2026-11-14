from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from app.schemas.common import Input, Patch, Read, Score, UnsignedId

Decision = Literal["pending", "accepted", "rejected"]
MatchStatus = Literal[
    "recommended", "one_side_interested", "mutually_accepted", "rejected", "expired"
]


class JobMatchCreate(Input):
    job_id: UnsignedId
    candidate_user_id: UnsignedId
    match_score: Score
    score_breakdown: dict[str, Any]
    explanation: str = Field(min_length=1)
    candidate_decision: Decision = "pending"
    employer_decision: Decision = "pending"
    match_status: MatchStatus = "recommended"
    candidate_decided_at: datetime | None = None
    employer_decided_at: datetime | None = None


class JobMatchUpdate(Patch):
    match_score: Score | None = None
    score_breakdown: dict[str, Any] | None = None
    explanation: str | None = Field(default=None, min_length=1)
    candidate_decision: Decision | None = None
    employer_decision: Decision | None = None
    match_status: MatchStatus | None = None
    candidate_decided_at: datetime | None = None
    employer_decided_at: datetime | None = None


class JobMatchRead(Read):
    id: UnsignedId
    job_id: UnsignedId
    candidate_user_id: UnsignedId
    match_score: Score
    score_breakdown: dict[str, Any]
    explanation: str
    candidate_decision: str
    employer_decision: str
    match_status: str
    calculated_at: datetime
    candidate_decided_at: datetime | None
    employer_decided_at: datetime | None
    updated_at: datetime
