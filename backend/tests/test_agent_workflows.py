from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.agents.artifact_analysis.graph import build_artifact_analysis_graph
from app.agents.artifact_analysis.nodes import ArtifactContext
from app.agents.artifact_analysis.schemas import ArtifactDraft, ArtifactInput
from app.agents.job_descriptor.graph import build_job_descriptor_graph
from app.agents.job_descriptor.schemas import JobDraft, JobInput
from app.agents.matching.graph import build_matching_graph
from app.agents.matching.nodes import MatchContext
from app.agents.matching.schemas import MatchInput
from app.agents.shared.context import ModelContext
from app.agents.shared.contracts import ArtifactContent, SkillDefinition, SourceBlock
from app.agents.shared.structured_output import LangChainStructuredModel
from app.services.artifact_ingestion.dispatcher import ArtifactIngestor


class FakeModel:
    def __init__(self, *outputs):
        self.outputs = outputs
        self.calls = []

    async def generate(self, schema, prompt, payload):
        self.calls.append(payload)
        output = self.outputs[min(len(self.calls) - 1, len(self.outputs) - 1)]
        if isinstance(output, Exception):
            raise output
        return schema.model_validate(output)


class FakeReader:
    def __init__(self, text="from fastapi import FastAPI", **updates):
        self.content = ArtifactContent(
            source_revision="commit-abc",
            content_markdown=text,
            source_locations=[SourceBlock(block_id="main", location="app/main.py:1", text=text)],
            **updates,
        )

    async def read(self, reference):
        return self.content


CATALOG = (SkillDefinition(id="1", canonical_name="FastAPI", aliases=["fast api"]),)
ARTIFACT = ArtifactInput(
    artifact_type="github_repository",
    source_url="https://github.com/example/demo",
    candidate_role="Backend developer",
    contribution_description="Implemented API routes",
)


def artifact_draft(**updates):
    return {
        "summary": "Backend application",
        "evidence": [
            {
                "skill_name": "fast api",
                "block_id": "main",
                "evidence_excerpt": "import FastAPI",
                "evidence_kind": "direct",
                "confidence_score": "0.9000",
                **updates,
            }
        ],
    }


def artifact_graph(model, reader=None, **budgets):
    return build_artifact_analysis_graph(
        ArtifactContext(
            generation=ModelContext(model=model, skills=CATALOG),
            ingestor=ArtifactIngestor({"github_repository": reader or FakeReader()}),
            **budgets,
        )
    )


async def test_artifact_happy_path_and_deduplication():
    output = artifact_draft()
    output["evidence"] *= 2
    model = FakeModel(output)
    state = await artifact_graph(model).ainvoke({"input": ARTIFACT})
    result = state["result"]
    assert result.status == "completed"
    assert len(result.evidence) == 1
    assert result.evidence[0].skill_id == "1"
    assert result.evidence[0].skill_name == "FastAPI"
    assert result.evidence[0].review_status == "ai_suggested"
    assert result.evidence[0].evidence_location == "app/main.py:1"
    assert result.source_revision == "commit-abc"
    assert model.calls[0]["contribution_description"] == ARTIFACT.contribution_description


@pytest.mark.parametrize(
    "kind",
    ["github_repository", "document", "spreadsheet", "image", "video", "design_link", "other"],
)
async def test_unregistered_artifact_type_is_explicitly_unsupported(kind):
    model = FakeModel(artifact_draft())
    graph = build_artifact_analysis_graph(
        ArtifactContext(
            ModelContext(model=model),
            ArtifactIngestor(),
        )
    )
    result = await graph.ainvoke({"input": ARTIFACT.model_copy(update={"artifact_type": kind})})
    assert result["result"].status == "unsupported"
    assert not model.calls


async def test_registered_document_reader_uses_same_graph():
    model = FakeModel(artifact_draft())
    graph = build_artifact_analysis_graph(
        ArtifactContext(
            ModelContext(model=model, skills=CATALOG),
            ArtifactIngestor({"document": FakeReader()}),
        )
    )
    state = await graph.ainvoke(
        {"input": ARTIFACT.model_copy(update={"artifact_type": "document"})}
    )
    assert state["result"].status == "completed"


@pytest.mark.parametrize("updates", [{"block_id": "invented"}, {"evidence_excerpt": "fake quote"}])
async def test_invalid_citations_have_bounded_repair(updates):
    model = FakeModel(artifact_draft(**updates))
    result = (await artifact_graph(model).ainvoke({"input": ARTIFACT}))["result"]
    assert result.status == "needs_review"
    assert result.evidence == []
    assert len(model.calls) == 2


async def test_artifact_repair_recovers_from_invalid_schema():
    model = FakeModel({"summary": 1}, artifact_draft())
    result = (await artifact_graph(model).ainvoke({"input": ARTIFACT}))["result"]
    assert result.status == "completed"
    assert len(model.calls) == 2
    assert model.calls[1]["validation_feedback"]


async def test_unresolved_skill_is_not_created():
    model = FakeModel(artifact_draft(skill_name="Unknown framework"))
    result = (await artifact_graph(model).ainvoke({"input": ARTIFACT}))["result"]
    assert result.status == "needs_review"
    assert result.unresolved_skills == ["Unknown framework"]
    assert result.evidence == []


@pytest.mark.parametrize(
    "reader,budgets",
    [
        (FakeReader("api_key=not-a-real-secret"), {}),
        (FakeReader(), {"max_characters": 1}),
    ],
)
async def test_artifact_guard_prevents_model_calls(reader, budgets):
    model = FakeModel(artifact_draft())
    result = (await artifact_graph(model, reader, **budgets).ainvoke({"input": ARTIFACT}))["result"]
    assert result.status == "needs_review"
    assert not model.calls
    assert "not-a-real-secret" not in result.model_dump_json()


async def test_unexpected_model_failure_propagates_for_service_to_handle():
    model = FakeModel(RuntimeError("provider unavailable"))
    with pytest.raises(RuntimeError, match="provider unavailable"):
        await artifact_graph(model).ainvoke({"input": ARTIFACT})


JOB = JobInput(business_problem="Build API using FastAPI")


def job_draft(**updates):
    return {
        "suggested_title": "Backend Developer",
        "job_summary": "Build API",
        "job_description": "Develop API using FastAPI",
        "requirements": [
            {
                "skill_name": "FastAPI",
                "requirement_type": "must_have",
                "supporting_quote": "using FastAPI",
            }
        ],
        **updates,
    }


async def test_job_draft_never_approves_or_publishes():
    model = FakeModel(job_draft())
    result = (
        await build_job_descriptor_graph(ModelContext(model, CATALOG)).ainvoke({"input": JOB})
    )["result"]
    assert result.status == "draft"
    assert result.requirements[0].skill_id == "1"
    assert "approval_status" not in result.model_dump()
    assert "publication_status" not in result.model_dump()


async def test_job_grounding_failure_and_repair_limit():
    draft = job_draft()
    draft["requirements"][0]["supporting_quote"] = "invented requirement"
    model = FakeModel(draft)
    result = (
        await build_job_descriptor_graph(ModelContext(model, CATALOG)).ainvoke({"input": JOB})
    )["result"]
    assert result.status == "needs_review"
    assert result.draft is None
    assert not result.requirements
    assert len(model.calls) == 2


async def test_job_unknown_skill_needs_review():
    model = FakeModel(job_draft())
    result = (await build_job_descriptor_graph(ModelContext(model)).ainvoke({"input": JOB}))[
        "result"
    ]
    assert result.unresolved_skills == ["FastAPI"]
    assert result.status == "needs_review"


def match_input(**updates):
    return {
        "approval_status": "approved",
        "publication_status": "published",
        "requirements": [
            {"skill_id": "1", "skill_name": "FastAPI", "requirement_type": "must_have"}
        ],
        "evidence": [
            {
                "skill_id": "1",
                "evidence_kind": "direct",
                "review_status": "reviewer_verified",
                "evidence_location": "main.py:1",
            }
        ],
        **updates,
    }


async def test_match_score_decimal_and_unknown_preferences_excluded():
    result = (await build_matching_graph().ainvoke({"input": match_input()}))["result"]
    assert result.match_score == Decimal("100.00")
    assert isinstance(result.match_score, Decimal)
    assert "preferences" not in result.effective_weights
    assert "preferred" not in result.effective_weights
    assert sum(result.effective_weights.values()) == Decimal(1)
    assert result.explanation_source == "template"


async def test_rejected_evidence_excluded_and_duplicate_evidence_not_inflated():
    value = match_input()
    value["evidence"][0]["review_status"] = "rejected"
    result = (await build_matching_graph().ainvoke({"input": value}))["result"]
    assert result.match_score == Decimal("0.00")
    assert "belum ditemukan evidence" in result.explanation
    single = match_input()
    doubled = match_input(evidence=single["evidence"] * 2)
    one = (await build_matching_graph().ainvoke({"input": single}))["result"]
    two = (await build_matching_graph().ainvoke({"input": doubled}))["result"]
    assert one.match_score == two.match_score


@pytest.mark.parametrize("output", [{"fact_ids": ["invented"]}, TimeoutError(), {"fact_ids": []}])
async def test_matching_falls_back_without_hallucination(output):
    result = (
        await build_matching_graph(MatchContext(FakeModel(output))).ainvoke(
            {"input": match_input()}
        )
    )["result"]
    assert result.explanation_source == "template"
    assert "invented" not in result.explanation
    assert result.match_score == Decimal("100.00")


async def test_matching_model_can_only_order_known_facts():
    output = {"fact_ids": ["score", "skill-0", "component-required", "component-evidence"]}
    result = (
        await build_matching_graph(MatchContext(FakeModel(output))).ainvoke(
            {"input": match_input()}
        )
    )["result"]
    assert result.explanation_source == "model_selected_facts"
    assert result.explanation.startswith("Skor relevansi:")


def test_invalid_inputs_and_context_are_rejected():
    with pytest.raises(ValidationError):
        ArtifactDraft.model_validate(artifact_draft(confidence_score="1.1"))
    with pytest.raises(ValidationError):
        MatchInput.model_validate(match_input(publication_status="closed"))
    with pytest.raises(ValidationError):
        MatchInput.model_validate(match_input(preference_factors={"salary": "NaN"}))
    with pytest.raises(ValidationError):
        JobDraft.model_validate(job_draft(approval_status="approved"))
    with pytest.raises(ValueError):
        ModelContext(FakeModel(), max_repairs=10)


async def test_langchain_adapter_uses_structured_output_without_live_provider():
    class Runnable:
        async def ainvoke(self, messages):
            assert messages[0].type == "system"
            assert messages[1].type == "human"
            assert "Output JSON schema:" in messages[0].content
            return job_draft()

    class ChatModel:
        def with_structured_output(self, schema, *, method):
            assert schema is JobDraft
            assert method == "function_calling"
            return Runnable()

    adapter = LangChainStructuredModel(ChatModel(), method="function_calling")
    result = await adapter.generate(JobDraft, "Create draft", JOB.model_dump())
    assert isinstance(result, JobDraft)


async def test_alias_ambiguity_does_not_choose_arbitrary_skill():
    duplicate = SkillDefinition(id="2", canonical_name="Other", aliases=["fast api"])
    model = FakeModel(artifact_draft())
    graph = build_artifact_analysis_graph(
        ArtifactContext(
            generation=ModelContext(model, (*CATALOG, duplicate)),
            ingestor=ArtifactIngestor({"github_repository": FakeReader()}),
        )
    )
    result = (await graph.ainvoke({"input": ARTIFACT}))["result"]
    assert result.unresolved_skills == ["fast api"]
    assert not result.evidence


async def test_media_only_reader_needs_review_without_text_model_call():
    class MediaReader:
        async def read(self, reference):
            return ArtifactContent(source_revision="sha256-example", media_references=["frame-1"])

    model = FakeModel(artifact_draft())
    result = (await artifact_graph(model, MediaReader()).ainvoke({"input": ARTIFACT}))["result"]
    assert result.status == "needs_review"
    assert not model.calls
