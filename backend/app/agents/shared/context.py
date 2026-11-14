from dataclasses import dataclass
from typing import Protocol

from pydantic import BaseModel

from app.agents.shared.contracts import SkillDefinition


class StructuredModel(Protocol):
    async def generate(self, schema: type[BaseModel], prompt: str, payload: dict) -> BaseModel:
        """Return schema-validated output; never execute tools from model output."""
        ...


@dataclass(frozen=True)
class ModelContext:
    model: StructuredModel
    skills: tuple[SkillDefinition, ...] = ()
    max_repairs: int = 1

    def __post_init__(self):
        if not 0 <= self.max_repairs <= 2:
            raise ValueError("max_repairs must be between 0 and 2")
        ids = [skill.id for skill in self.skills]
        if len(ids) != len(set(ids)):
            raise ValueError("Skill catalog IDs must be unique")


def resolve_skill(name: str, skills: tuple[SkillDefinition, ...]) -> SkillDefinition | None:
    normalized = name.strip().lower()
    matches = [
        skill
        for skill in skills
        if normalized in {value.strip().lower() for value in [skill.canonical_name, *skill.aliases]}
    ]
    # Ambiguous aliases never resolve by ordering or model-generated IDs.
    return matches[0] if len(matches) == 1 else None
