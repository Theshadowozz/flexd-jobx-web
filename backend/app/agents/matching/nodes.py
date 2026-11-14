from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from openai import APIConnectionError, APIStatusError
from pydantic import ValidationError

from app.agents.matching.prompts import SYSTEM_PROMPT
from app.agents.matching.schemas import ExplanationSelection, MatchInput, MatchResult
from app.agents.matching.state import MatchState
from app.agents.shared.context import StructuredModel

FORMULA_VERSION = "matching-v1-experimental"
BASE_WEIGHTS = {
    "required": Decimal("0.50"),
    "preferred": Decimal("0.20"),
    "evidence": Decimal("0.20"),
    "preferences": Decimal("0.10"),
}
REVIEW_QUALITY = {
    "ai_suggested": Decimal("0.5"),
    "candidate_confirmed": Decimal("0.75"),
    "reviewer_verified": Decimal("1"),
}


@dataclass(frozen=True)
class MatchContext:
    model: StructuredModel | None = None


class MatchNodes:
    def __init__(self, context: MatchContext):
        self.context = context

    def validate_match_snapshot(self, state: MatchState):
        return {"input": MatchInput.model_validate(state["input"])}

    def aggregate_eligible_evidence(self, state: MatchState):
        quality = {}
        for item in state["input"].evidence:
            if item.review_status == "rejected":
                continue
            value = REVIEW_QUALITY[item.review_status]
            if item.evidence_kind == "inferred":
                value *= Decimal("0.6")
            quality[item.skill_id] = max(quality.get(item.skill_id, Decimal(0)), value)
        return {"quality": quality}

    def calculate_score_components(self, state: MatchState):
        value = state["input"]
        quality = state["quality"]
        components = {}
        for label, kind in (("required", "must_have"), ("preferred", "preferred")):
            items = [r for r in value.requirements if r.requirement_type == kind]
            if items:
                weight = sum((r.weight for r in items), Decimal(0))
                covered = sum((r.weight for r in items if r.skill_id in quality), Decimal(0))
                components[label] = 100 * covered / weight
        total = sum((r.weight for r in value.requirements), Decimal(0))
        components["evidence"] = (
            100
            * sum(
                (r.weight * quality.get(r.skill_id, Decimal(0)) for r in value.requirements),
                Decimal(0),
            )
            / total
        )
        if value.preference_factors:
            components["preferences"] = sum(value.preference_factors.values(), Decimal(0)) / len(
                value.preference_factors
            )
        denominator = sum((BASE_WEIGHTS[key] for key in components), Decimal(0))
        weights = {key: BASE_WEIGHTS[key] / denominator for key in components}
        score = sum((components[key] * weights[key] for key in components), Decimal(0))
        return {
            "components": components,
            "weights": weights,
            "score": score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        }

    def build_explanation_facts(self, state: MatchState):
        facts = {}
        for index, item in enumerate(state["input"].requirements):
            if item.skill_id in state["quality"]:
                statuses = sorted(
                    {
                        e.review_status
                        for e in state["input"].evidence
                        if e.skill_id == item.skill_id and e.review_status != "rejected"
                    }
                )
                facts[f"skill-{index}"] = (
                    f"{item.skill_name}: evidence tersedia ({', '.join(statuses)})."
                )
            else:
                facts[f"skill-{index}"] = (
                    f"{item.skill_name}: belum ditemukan evidence pada artifact yang dianalisis."
                )
        for key, component in state["components"].items():
            facts[f"component-{key}"] = f"{key}: {component.quantize(Decimal('0.01'))}/100."
        facts["score"] = f"Skor relevansi: {state['score']}/100, bukan probabilitas diterima."
        return {"facts": facts}

    async def generate_or_render_explanation(self, state: MatchState):
        if self.context.model is not None:
            try:
                output = await self.context.model.generate(
                    ExplanationSelection, SYSTEM_PROMPT, {"facts": state["facts"]}
                )
                output = ExplanationSelection.model_validate(output)
                return {"selected": output.fact_ids, "explanation_source": "model_selected_facts"}
            except (
                ValidationError,
                TimeoutError,
                ConnectionError,
                APIConnectionError,
                APIStatusError,
            ):
                pass
        return {"selected": list(state["facts"]), "explanation_source": "template"}

    def validate_explanation(self, state: MatchState):
        selected = state["selected"]
        if len(selected) != len(set(selected)) or set(selected) != set(state["facts"]):
            return {"selected": list(state["facts"]), "explanation_source": "template"}
        return {}

    def build_match_result(self, state: MatchState):
        return {
            "result": MatchResult(
                formula_version=FORMULA_VERSION,
                match_score=state["score"],
                score_breakdown=state["components"],
                effective_weights=state["weights"],
                explanation="\n".join(state["facts"][key] for key in state["selected"]),
                explanation_source=state["explanation_source"],
                limitations=[
                    "Experimental scoring policy, not a validated measure of competence.",
                    "Unknown preference factors and absent requirement groups are excluded; "
                    "remaining component weights are normalized.",
                    "AI-suggested evidence is included but assigned lower evidence quality.",
                ],
            )
        }
