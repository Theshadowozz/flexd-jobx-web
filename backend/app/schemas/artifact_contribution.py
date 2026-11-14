from decimal import Decimal
from typing import Literal

from pydantic import Field

from app.schemas.common import Input, Patch, Read, Timestamps
from app.schemas.response import ApiResponse, Pagination


class ArtifactContributionFields(Input):
    role_title: str | None = Field(default=None, max_length=150)
    contribution_description: str = Field(min_length=1, max_length=16000)
    contribution_share_percent: Decimal | None = Field(
        default=None, ge=0, le=100, max_digits=5, decimal_places=2
    )
    claim_status: Literal["self_declared", "peer_confirmed", "organization_confirmed"] = (
        "self_declared"
    )


class ArtifactContributionCreate(ArtifactContributionFields):
    artifact_id: int = Field(gt=0, le=18446744073709551615)
    contributor_user_id: int = Field(gt=0, le=18446744073709551615)


class ArtifactContributionUpdate(ArtifactContributionFields, Patch):
    contribution_description: str | None = Field(default=None, min_length=1, max_length=16000)


class ArtifactContributionRead(ArtifactContributionFields, Timestamps):
    model_config = {"from_attributes": True}
    id: int
    artifact_id: int
    contributor_user_id: int


class ArtifactContributionDetailData(Read):
    artifact_contribution: ArtifactContributionRead


class ArtifactContributionListData(Read):
    artifact_contributions: list[ArtifactContributionRead]
    pagination: Pagination


ArtifactContributionDetailResponse = ApiResponse[ArtifactContributionDetailData]
ArtifactContributionListResponse = ApiResponse[ArtifactContributionListData]
