import re
from dataclasses import dataclass

from pydantic import ValidationError

from app.agents.artifact_analysis.prompts import PROMPT_VERSION, SYSTEM_PROMPT
from app.agents.artifact_analysis.schemas import (
    AnalysisResult,
    ArtifactDraft,
    ArtifactInput,
    ValidatedEvidence,
)
from app.agents.artifact_analysis.state import ArtifactState
from app.agents.shared.context import ModelContext, resolve_skill
from app.services.artifact_ingestion.dispatcher import ArtifactIngestor, UnsupportedArtifactError

# Defense in depth only; actual readers must filter secrets before returning content.
SECRET_PATTERN = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|"
    r"\bAKIA[A-Z0-9]{16}\b|\bgh[pousr]_[A-Za-z0-9_]+\b|"
    r"(?i:\b(?:password|api[_-]?key|secret|token)\s*[:=]\s*\S+)"
)


@dataclass(frozen=True)
class ArtifactContext:
    generation: ModelContext
    ingestor: ArtifactIngestor
    max_characters: int = 100_000
    max_blocks: int = 100

    def __post_init__(self):
        if self.max_characters < 1 or self.max_blocks < 1:
            raise ValueError("Artifact budgets must be positive")


class ArtifactNodes:
    def __init__(self, context: ArtifactContext):
        self.context = context

    def validate_artifact_input(self, state: ArtifactState):
        value = ArtifactInput.model_validate(state["input"])
        if not (value.source_url or value.storage_key):
            raise ValueError("Artifact source_url or storage_key is required")
        return {"input": value, "repairs": 0, "errors": []}

    async def ingest_artifact(self, state: ArtifactState):
        try:
            content = await self.context.ingestor.read(state["input"])
            return {"content": content}
        except UnsupportedArtifactError:
            return {
                "result": AnalysisResult(
                    status="unsupported",
                    prompt_version=PROMPT_VERSION,
                    limitations=["No reader available for this artifact type/format."],
                )
            }

    def normalize_and_sanitize_content(self, state: ArtifactState):
        content = state["content"]
        blocks = content.source_locations
        total = len(content.content_markdown) + sum(len(block.text) for block in blocks)
        reason = None
        if total > self.context.max_characters or len(blocks) > self.context.max_blocks:
            reason = "Artifact exceeds configured analysis budget."
        elif not blocks:
            reason = "No citable text extracted; a supported reader/model is required."
        elif len({block.block_id for block in blocks}) != len(blocks):
            reason = "Source block identifiers must be unique."
        elif SECRET_PATTERN.search(content.model_dump_json()):
            reason = "Potential secret detected; content was not sent to model."
        if reason:
            return {
                "result": AnalysisResult(
                    status="needs_review",
                    prompt_version=PROMPT_VERSION,
                    source_revision=content.source_revision,
                    limitations=[reason],
                )
            }
        # Media references are not dereferenced or sent as arbitrary URLs by this text scaffold.
        return {"content": content.model_copy(update={"media_references": []})}

    async def analyze_artifact_with_contribution(self, state: ArtifactState):
        content = state["content"]
        payload = {
            "candidate_role": state["input"].candidate_role,
            "contribution_description": state["input"].contribution_description,
            "content": content.model_dump(mode="json"),
            "catalog": [s.model_dump() for s in self.context.generation.skills],
            "validation_feedback": state["errors"],
        }
        try:
            result = await self.context.generation.model.generate(
                ArtifactDraft, SYSTEM_PROMPT, payload
            )
            return {"draft": ArtifactDraft.model_validate(result), "errors": []}
        except ValidationError:
            return {"errors": ["Output does not conform to ArtifactDraft schema."]}

    def normalize_skills(self, state: ArtifactState):
        if state["errors"]:
            return {}
        canonical_ids = {}
        unresolved = []
        for item in state["draft"].evidence:
            skill = resolve_skill(item.skill_name, self.context.generation.skills)
            if skill is None:
                unresolved.append(item.skill_name)
            else:
                canonical_ids[item.skill_name] = skill.id
        return {"canonical_ids": canonical_ids, "unresolved": sorted(set(unresolved))}

    def validate_evidence(self, state: ArtifactState):
        if state["errors"]:
            return {}
        blocks = {block.block_id: block for block in state["content"].source_locations}
        errors = []
        if SECRET_PATTERN.search(state["draft"].model_dump_json()):
            errors.append("Potential secret detected in generated output.")
        for item in state["draft"].evidence:
            block = blocks.get(item.block_id)
            if block is None or item.evidence_excerpt not in block.text:
                errors.append("Evidence must quote a real supplied source block.")
        return {"errors": list(dict.fromkeys(errors))}

    def repair_output(self, state: ArtifactState):
        return {"repairs": state["repairs"] + 1}

    def build_analysis_result(self, state: ArtifactState):
        if "result" in state:
            return {}
        content = state["content"]
        if state["errors"]:
            return {
                "result": AnalysisResult(
                    status="needs_review",
                    prompt_version=PROMPT_VERSION,
                    source_revision=content.source_revision,
                    limitations=state["errors"],
                )
            }
        draft = state["draft"]
        blocks = {block.block_id: block for block in content.source_locations}
        evidence: dict[str, ValidatedEvidence] = {}
        unresolved = state["unresolved"]
        catalog = {skill.id: skill for skill in self.context.generation.skills}
        for item in draft.evidence:
            skill_id = state["canonical_ids"].get(item.skill_name)
            if skill_id is None:
                continue
            skill = catalog[skill_id]
            validated = ValidatedEvidence(
                **item.model_dump(exclude={"skill_name"}),
                skill_name=skill.canonical_name,
                skill_id=skill.id,
                evidence_location=blocks[item.block_id].location,
            )
            # Unique (analysis_id, skill_id): keep first valid citation deterministically.
            evidence.setdefault(skill.id, validated)
        return {
            "result": AnalysisResult(
                status="needs_review" if unresolved else "completed",
                prompt_version=PROMPT_VERSION,
                source_revision=content.source_revision,
                summary=draft.summary,
                evidence=list(evidence.values()),
                unresolved_skills=sorted(set(unresolved)),
                limitations=[
                    *content.limitations,
                    *content.processing_warnings,
                    *draft.limitations,
                    "Individual authorship is not independently verified.",
                    "Text-only scaffold; visual content is not analyzed.",
                ],
            )
        }
