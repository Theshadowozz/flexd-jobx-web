from langgraph.graph import END, START, StateGraph

from app.agents.matching.nodes import MatchContext, MatchNodes
from app.agents.matching.state import MatchState


def build_matching_graph(context: MatchContext | None = None):
    nodes = MatchNodes(context or MatchContext())
    graph = StateGraph(MatchState)
    names = (
        "validate_match_snapshot",
        "aggregate_eligible_evidence",
        "calculate_score_components",
        "build_explanation_facts",
        "generate_or_render_explanation",
        "validate_explanation",
        "build_match_result",
    )
    previous = START
    for name in names:
        graph.add_node(name, getattr(nodes, name))
        graph.add_edge(previous, name)
        previous = name
    graph.add_edge(previous, END)
    return graph.compile()
