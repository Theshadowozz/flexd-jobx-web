from langgraph.graph import END, START, StateGraph

from app.agents.job_descriptor.nodes import JobNodes
from app.agents.job_descriptor.state import JobState
from app.agents.shared.context import ModelContext


def build_job_descriptor_graph(context: ModelContext):
    nodes = JobNodes(context)
    graph = StateGraph(JobState)
    for name in (
        "validate_job_input",
        "generate_job_draft",
        "normalize_requirements",
        "validate_grounding",
        "repair_draft",
        "build_draft_result",
    ):
        graph.add_node(name, getattr(nodes, name))
    graph.add_edge(START, "validate_job_input")
    graph.add_edge("validate_job_input", "generate_job_draft")
    graph.add_edge("generate_job_draft", "normalize_requirements")
    graph.add_edge("normalize_requirements", "validate_grounding")
    graph.add_conditional_edges(
        "validate_grounding",
        lambda s: (
            "repair_draft"
            if s["errors"] and s["repairs"] < context.max_repairs
            else "build_draft_result"
        ),
    )
    graph.add_edge("repair_draft", "generate_job_draft")
    graph.add_edge("build_draft_result", END)
    return graph.compile()
