from typing import Literal

from pydantic import Field

from app.schemas.common import Input, Patch, Score, Timestamps, UnsignedId

ClaimStatus = Literal["self_declared", "peer_confirmed", "organization_confirmed"]


class ArtifactContributionCreate(Input):
    artifact_id: UnsignedId
    contributor_user_id: UnsignedId
    role_title: str | None = Field(default=None, max_length=150)
    contribution_description: str = Field(min_length=1)
    contribution_share_percent: Score | None = None
    claim_status: ClaimStatus = "self_declared"


class ArtifactContributionUpdate(Patch):
    role_title: str | None = Field(default=None, max_length=150)
    contribution_description: str | None = Field(default=None, min_length=1)
    contribution_share_percent: Score | None = None
    claim_status: ClaimStatus | None = None


class ArtifactContributionRead(Timestamps):
    id: UnsignedId
    artifact_id: UnsignedId
    contributor_user_id: UnsignedId
    role_title: str | None
    contribution_description: str
    contribution_share_percent: Score | None
    claim_status: str
