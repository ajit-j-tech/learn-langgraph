from __future__ import annotations

from typing import NotRequired, TypedDict, Annotated, Literal

from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver

# Prepare the State
class InvoiceState(TypedDict):
    messages: Annotated[list, add_messages]
    invoice_id: str
    amount: NotRequired[float]
    confidence: NotRequired[float]
    review_decision: NotRequired[dict]
    approval_status: NotRequired[Literal["pending", "approved", "rejected", "in_review", "corrected"]]
    reviewer: NotRequired[str]
    corrected_amount: NotRequired[float]
    corrected_confidence: NotRequired[float]

# Review Invoice Node definition
def review_invoice(state: InvoiceState) -> dict:
    invoice_amount = state["amount"]
    invoice_confidence = state["confidence"]

    if invoice_amount < 1000 and invoice_confidence >= 0.90:
        return {
            "approval_status": "approved",
            "messages": [{"role": "assistant", "content": "Auto-approved via threashold"}]
        }

    # Review Payload for Human
    review_payload = {
        "review_status": "pending",
        "reviewer": "human",
        "invoice_id": state["invoice_id"],
        "amount": invoice_amount,
        "confidence": invoice_confidence
    }

    return {
        "review_decision": interrupt(review_payload),
        "approval_status": "pending"
    }

# Apply decision Node definition
def apply_decision(state: InvoiceState) -> dict:
    decision = state.get("review_decision", {}) # For auto approve you might not get this key
    invoice_id = state["invoice_id"]
    invoice_confidence = state["confidence"]

    print(f"Here are the details of Invoice: {invoice_id}: ")
    print(f"Invoice Amount: {state['amount']}")
    print(f"System Confidence: {invoice_confidence}")
    print(f"Review Status: {state['approval_status']}")
    print("Overall Details: ")
    print(decision)

    print("\n")

    review_status = decision.get("review_status") if isinstance(decision, dict) else None

    if review_status == "corrected":
        corrected_amount = float(decision["amount"])
        corrected_confidence = float(decision["confidence"])
        return {
            "reviewer": decision.get("reviewer", "human"),
            "approval_status": "corrected",
            "amount": corrected_amount,
            "confidence": corrected_confidence,
            "corrected_amount": corrected_amount,
            "corrected_confidence": corrected_confidence,
            "review_decision": {
                "review_status": "corrected",
                "reviewer": decision.get("reviewer", "human"),
                "amount": corrected_amount,
                "confidence": corrected_confidence
            }
        }

    if review_status == "rejected":
        return {
            "reviewer": decision.get("reviewer", "human") if isinstance(decision, dict) else "human",
            "approval_status": "rejected",
            "review_decision": {
                "review_status": "rejected",
                "reviewer": decision.get("reviewer", "human") if isinstance(decision, dict) else "human"
            }
        }

    return {
        "reviewer": "Ajit",
        "approval_status": "approved",
        "review_decision": {
            "review_status": "reviewed",
            "reviewer": "Ajit"
        }
    }

# Prepare the Graph
graph_builder = StateGraph(state_schema=InvoiceState)

# Add the nodes
graph_builder.add_node("review_invoice", review_invoice)
graph_builder.add_node("apply_decision", apply_decision)

# Add the edges for exuection
graph_builder.add_edge(START, "review_invoice")
graph_builder.add_edge("review_invoice", "apply_decision")
graph_builder.add_edge("apply_decision", END)

# compile the Graph
checkpointer = MemorySaver()
graph = graph_builder.compile(checkpointer=checkpointer)

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "thread-001"}}

    review = graph.invoke({
        "invoice_id": input("Invoice ID: "),
        "amount": float(input("Invoice Amount: ")),
        "confidence": float(input("Invoice Confidence (0.00-1.00): "))
    }, config=config)

    print(review)

    # Lets resume it now
    print("\nResuming the Workflow.......\n")

    resumed = graph.invoke(Command(resume={
        **review["__interrupt__"][0].value
    }), config=config)

    print("\n")
    print(resumed)
