from typing import TypedDict

from app.agents.artifact_analysis.schemas import AnalysisResult, ArtifactDraft, ArtifactInput
from app.agents.shared.contracts import ArtifactContent


class ArtifactState(TypedDict, total=False):
    input: ArtifactInput
    content: ArtifactContent
    draft: ArtifactDraft
    canonical_ids: dict[str, str]
    unresolved: list[str]
    errors: list[str]
    repairs: int
    result: AnalysisResult
