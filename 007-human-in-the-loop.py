from __future__ import annotations

from typing import Annotated, NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

try:
    from langgraph.checkpoint.memory import MemorySaver
except Exception:  # pragma: no cover - optional dependency fallback
    MemorySaver = None  # type: ignore[assignment]

try:
    from langgraph.types import Command, interrupt
except Exception:  # pragma: no cover - optional dependency fallback
    Command = None  # type: ignore[assignment]
    interrupt = None  # type: ignore[assignment]


class InvoiceState(TypedDict):
    messages: Annotated[list, add_messages]
    invoice_id: NotRequired[str]
    amount: NotRequired[float]
    confidence: NotRequired[float]
    review_decision: NotRequired[dict]
    approval_status: NotRequired[str]
    corrected_amount: NotRequired[float]


def prepare_review(state: InvoiceState) -> dict:
    amount = state.get("amount", 0.0)
    confidence = state.get("confidence", 0.0)

    if confidence >= 0.95 and amount < 1000:
        return {
            "approval_status": "auto_approved",
            "messages": [{"role": "assistant", "content": "Invoice auto-approved."}],
        }

    review_payload = {
        "invoice_id": state.get("invoice_id", "unknown"),
        "amount": amount,
        "confidence": confidence,
    }

    if interrupt is not None:
        decision = interrupt(review_payload)
    else:  # pragma: no cover - fallback for reading only
        decision = {"approval_status": "pending_review"}

    return {"review_decision": decision}


def apply_decision(state: InvoiceState) -> dict:
    decision = state.get("review_decision", {})

    if isinstance(decision, dict):
        if decision.get("approval_status") == "approved":
            return {
                "approval_status": "approved",
                "messages": [{"role": "assistant", "content": "Invoice approved by human."}],
            }

        if decision.get("approval_status") == "corrected":
            return {
                "approval_status": "corrected",
                "corrected_amount": float(decision["corrected_amount"]),
                "messages": [
                    {
                        "role": "assistant",
                        "content": f"Invoice corrected to {decision['corrected_amount']}.",
                    }
                ],
            }

    return {
        "approval_status": "rejected",
        "messages": [{"role": "assistant", "content": "Invoice rejected."}],
    }


builder = StateGraph(InvoiceState)
builder.add_node("prepare_review", prepare_review)
builder.add_node("apply_decision", apply_decision)
builder.add_edge(START, "prepare_review")
builder.add_edge("prepare_review", "apply_decision")
builder.add_edge("apply_decision", END)

checkpointer = MemorySaver() if MemorySaver is not None else None
graph = builder.compile(checkpointer=checkpointer)


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "invoice-1001"}}

    first_run = graph.invoke(
        {
            "messages": [{"role": "user", "content": "Review invoice INV-1001"}],
            "invoice_id": "INV-1001",
            "amount": 1250.0,
            "confidence": 0.82,
        },
        config=config,
    )
    print(first_run)

    print("-----------------------------")
    print("Resuming the Graph Workflow")
    print("-----------------------------")

    if Command is not None:
        resumed = graph.invoke(
            Command(
                resume={
                    "approval_status": "approved",
                    "reviewer": "human",
                }
            ),
            config=config,
        )
        print(resumed)
