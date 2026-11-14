from typing import TypedDict

from app.agents.job_descriptor.schemas import (
    CanonicalRequirement,
    JobDraft,
    JobDraftResult,
    JobInput,
)


class JobState(TypedDict, total=False):
    input: JobInput
    draft: JobDraft
    requirements: list[CanonicalRequirement]
    unresolved: list[str]
    errors: list[str]
    repairs: int
    result: JobDraftResult
