from __future__ import annotations

from typing import NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph


class ProductionState(TypedDict):
    user_id: str
    customer_id: str
    authorized: NotRequired[bool]
    retries: NotRequired[int]
    final_answer: NotRequired[str]


def validate(state: ProductionState) -> dict:
    if not state["customer_id"].startswith("CUST-"):
        return {"final_answer": "Invalid input."}
    return {}


def authorize(state: ProductionState) -> dict:
    if state["user_id"] not in {"alice", "ops"}:
        return {"authorized": False, "final_answer": "Unauthorized."}
    return {"authorized": True}


def respond(state: ProductionState) -> dict:
    if state.get("final_answer"):
        return {}
    return {"final_answer": f"Customer workflow completed for {state['customer_id']}."}


builder = StateGraph(ProductionState)
builder.add_node("validate", validate)
builder.add_node("authorize", authorize)
builder.add_node("respond", respond)
builder.add_edge(START, "validate")
builder.add_edge("validate", "authorize")
builder.add_edge("authorize", "respond")
builder.add_edge("respond", END)

graph = builder.compile()


if __name__ == "__main__":
    print(graph.invoke({"user_id": "alice", "customer_id": "CUST-1001"}))
