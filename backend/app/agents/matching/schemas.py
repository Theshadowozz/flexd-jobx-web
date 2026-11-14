from decimal import Decimal
from typing import Literal

from pydantic import Field, model_validator

from app.agents.shared.contracts import Contract


class MatchRequirement(Contract):
    skill_id: str = Field(min_length=1)
    skill_name: str = Field(min_length=1)
    requirement_type: Literal["must_have", "preferred"]
    weight: Decimal = Field(default=Decimal("1"), gt=0, le=100)


class MatchEvidence(Contract):
    skill_id: str = Field(min_length=1)
    evidence_kind: Literal["direct", "inferred"]
    review_status: Literal["ai_suggested", "candidate_confirmed", "reviewer_verified", "rejected"]
    evidence_location: str = Field(min_length=1)


class MatchInput(Contract):
    """Service supplies only authorized, current, visibility-filtered evidence snapshots."""

    approval_status: Literal["approved"]
    publication_status: Literal["published"]
    # Service checks closes_at against its UTC clock before creating this snapshot.
    requirements: list[MatchRequirement] = Field(max_length=100)
    evidence: list[MatchEvidence] = Field(default_factory=list, max_length=1000)
    # Service computes available preference factors; unknown factors must be omitted.
    preference_factors: dict[
        Literal["employment_type", "work_mode", "location", "salary"], Decimal
    ] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_snapshot(self):
        ids = [item.skill_id for item in self.requirements]
        if not ids or len(ids) != len(set(ids)):
            raise ValueError("At least one requirement and unique skill IDs required")
        if any(
            not value.is_finite() or not 0 <= value <= 100
            for value in self.preference_factors.values()
        ):
            raise ValueError("Preference factors must be finite and between 0 and 100")
        return self


class ExplanationSelection(Contract):
    """Model may select known facts, never invent prose or alter numeric score."""

    fact_ids: list[str] = Field(min_length=1, max_length=200)


class MatchResult(Contract):
    formula_version: str
    match_score: Decimal
    score_breakdown: dict[str, Decimal]
    effective_weights: dict[str, Decimal]
    explanation: str
    explanation_source: Literal["model_selected_facts", "template"]
    limitations: list[str]
