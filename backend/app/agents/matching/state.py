from decimal import Decimal
from typing import TypedDict

from app.agents.matching.schemas import MatchInput, MatchResult


class MatchState(TypedDict, total=False):
    input: MatchInput
    quality: dict[str, Decimal]
    components: dict[str, Decimal]
    weights: dict[str, Decimal]
    score: Decimal
    facts: dict[str, str]
    selected: list[str]
    explanation_source: str
    result: MatchResult
