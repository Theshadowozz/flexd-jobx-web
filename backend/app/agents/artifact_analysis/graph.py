from langgraph.graph import END, START, StateGraph

from app.agents.artifact_analysis.nodes import ArtifactContext, ArtifactNodes
from app.agents.artifact_analysis.state import ArtifactState


def build_artifact_analysis_graph(context: ArtifactContext):
    nodes = ArtifactNodes(context)
    graph = StateGraph(ArtifactState)
    for name in (
        "validate_artifact_input",
        "ingest_artifact",
        "normalize_and_sanitize_content",
        "analyze_artifact_with_contribution",
        "normalize_skills",
        "validate_evidence",
        "repair_output",
        "build_analysis_result",
    ):
        graph.add_node(name, getattr(nodes, name))
    graph.add_edge(START, "validate_artifact_input")
    graph.add_edge("validate_artifact_input", "ingest_artifact")
    graph.add_conditional_edges(
        "ingest_artifact",
        lambda s: "build_analysis_result" if "result" in s else "normalize_and_sanitize_content",
    )
    graph.add_conditional_edges(
        "normalize_and_sanitize_content",
        lambda s: (
            "build_analysis_result" if "result" in s else "analyze_artifact_with_contribution"
        ),
    )
    graph.add_edge("analyze_artifact_with_contribution", "normalize_skills")
    graph.add_edge("normalize_skills", "validate_evidence")
    graph.add_conditional_edges(
        "validate_evidence",
        lambda s: (
            "repair_output"
            if s["errors"] and s["repairs"] < context.generation.max_repairs
            else "build_analysis_result"
        ),
    )
    graph.add_edge("repair_output", "analyze_artifact_with_contribution")
    graph.add_edge("build_analysis_result", END)
    return graph.compile()
