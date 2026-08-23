from __future__ import annotations

from typing import Literal, NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph


Agent = Literal["researcher", "analyst", "verifier", "FINISH"]


class ResearchState(TypedDict):
    question: str
    findings: NotRequired[list[dict]]
    analysis: NotRequired[str]
    verification: NotRequired[str]
    next_agent: NotRequired[Agent]
    final_answer: NotRequired[str]


def supervisor(state: ResearchState) -> dict:
    if not state.get("findings"):
        return {"next_agent": "researcher"}
    if not state.get("analysis"):
        return {"next_agent": "analyst"}
    if not state.get("verification"):
        return {"next_agent": "verifier"}
    return {"next_agent": "FINISH"}


def researcher(_: ResearchState) -> dict:
    return {"findings": [{"claim": "LangGraph uses explicit nodes and edges.", "source": "https://langchain-ai.github.io/langgraph/"}]}


def analyst(state: ResearchState) -> dict:
    claim = state["findings"][0]["claim"]
    return {"analysis": f"Evidence indicates: {claim}"}


def verifier(state: ResearchState) -> dict:
    return {"verification": "Verified: no unsupported claims in the current draft."}


def finalize(state: ResearchState) -> dict:
    return {"final_answer": f"{state['analysis']} {state['verification']}"}


builder = StateGraph(ResearchState)
builder.add_node("supervisor", supervisor)
builder.add_node("researcher", researcher)
builder.add_node("analyst", analyst)
builder.add_node("verifier", verifier)
builder.add_node("finalize", finalize)
builder.add_edge(START, "supervisor")
builder.add_conditional_edges(
    "supervisor",
    lambda state: state.get("next_agent", "FINISH"),
    {"researcher": "researcher", "analyst": "analyst", "verifier": "verifier", "FINISH": "finalize"},
)
builder.add_edge("researcher", "supervisor")
builder.add_edge("analyst", "supervisor")
builder.add_edge("verifier", "supervisor")
builder.add_edge("finalize", END)

graph = builder.compile()


if __name__ == "__main__":
    print(graph.invoke({"question": "How does LangGraph coordinate specialists?"}))
