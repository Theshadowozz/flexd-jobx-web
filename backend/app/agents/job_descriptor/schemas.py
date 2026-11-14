from typing import Literal

from pydantic import Field

from app.agents.shared.contracts import Contract


class JobInput(Contract):
    business_problem: str = Field(min_length=1, pattern=r"\S", max_length=20000)
    # Facts supplied by employer. Every proposed requirement must cite this or business_problem.
    employer_facts: str = Field(default="", max_length=10000)


class Requirement(Contract):
    skill_name: str = Field(min_length=1)
    requirement_type: Literal["must_have", "preferred"]
    supporting_quote: str = Field(min_length=1)


class JobDraft(Contract):
    suggested_title: str = Field(min_length=1, max_length=200)
    job_summary: str = Field(min_length=1, max_length=5000)
    job_description: str = Field(min_length=1, max_length=20000)
    requirements: list[Requirement] = Field(default_factory=list, max_length=100)
    missing_information: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)


class CanonicalRequirement(Requirement):
    skill_id: str


class JobDraftResult(Contract):
    status: Literal["draft", "needs_review"]
    prompt_version: str
    draft: JobDraft | None = None
    requirements: list[CanonicalRequirement] = Field(default_factory=list)
    unresolved_skills: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
