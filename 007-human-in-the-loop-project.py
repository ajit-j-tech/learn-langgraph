from __future__ import annotations

from typing import Annotated, NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

try:
    from langgraph.checkpoint.memory import MemorySaver
except Exception:  # pragma: no cover
    MemorySaver = None  # type: ignore[assignment]

try:
    from langgraph.types import Command, interrupt
except Exception:  # pragma: no cover
    Command = None  # type: ignore[assignment]
    interrupt = None  # type: ignore[assignment]


class ApprovalState(TypedDict):
    messages: Annotated[list, add_messages]
    invoice_id: str
    amount: float
    approval: NotRequired[dict]
    status: NotRequired[str]


def prepare_review(state: ApprovalState) -> dict:
    payload = {"invoice_id": state["invoice_id"], "amount": state["amount"]}
    decision = interrupt(payload) if interrupt else {"status": "approved"}
    return {"approval": decision}


def apply_review(state: ApprovalState) -> dict:
    approval = state.get("approval", {})
    status = approval.get("status", "rejected")
    return {"status": status}


builder = StateGraph(ApprovalState)
builder.add_node("prepare_review", prepare_review)
builder.add_node("apply_review", apply_review)
builder.add_edge(START, "prepare_review")
builder.add_edge("prepare_review", "apply_review")
builder.add_edge("apply_review", END)

graph = builder.compile(checkpointer=MemorySaver() if MemorySaver else None)


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "invoice-1001"}}
    first = graph.invoke(
        {"messages": [{"role": "user", "content": "Approve invoice INV-1001"}], "invoice_id": "INV-1001", "amount": 1250.0},
        config=config,
    )
    print(first)
    if Command is not None:
        print(graph.invoke(Command(resume={"status": "approved"}), config=config))
