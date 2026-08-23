from __future__ import annotations

import logging
import time
from typing import NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("enterprise-patterns")

MAX_RETRIES = 1
ALLOWED_USERS = {"alice", "ops"}


class WorkflowState(TypedDict):
    user_id: str
    customer_id: str
    authorized: NotRequired[bool]
    retries: NotRequired[int]
    lookup_result: NotRequired[dict]
    error: NotRequired[str]
    final_answer: NotRequired[str]


def log_step(name: str, start: float, state: WorkflowState) -> None:
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        {
            "node": name,
            "customer_id": state.get("customer_id"),
            "retries": state.get("retries", 0),
            "elapsed_ms": elapsed_ms,
        }
    )


def validate_input(state: WorkflowState) -> dict:
    start = time.perf_counter()
    customer_id = state.get("customer_id", "")
    if not customer_id or not customer_id.startswith("CUST-"):
        log_step("validate_input", start, state)
        return {"error": "Invalid customer id.", "final_answer": "Request rejected."}

    log_step("validate_input", start, state)
    return {"retries": 0}


def authorize(state: WorkflowState) -> dict:
    start = time.perf_counter()
    authorized = state["user_id"] in ALLOWED_USERS
    log_step("authorize", start, state)
    if not authorized:
        return {"authorized": False, "error": "Unauthorized user."}
    return {"authorized": True}


def lookup_customer(state: WorkflowState) -> dict:
    start = time.perf_counter()
    retries = state.get("retries", 0)

    if retries < MAX_RETRIES and state["customer_id"] == "CUST-FAIL":
        log_step("lookup_customer", start, state)
        return {"retries": retries + 1, "error": "Transient lookup failure."}

    if state["customer_id"] == "CUST-404":
        log_step("lookup_customer", start, state)
        return {"error": "Customer not found."}

    result = {
        "customer_id": state["customer_id"],
        "status": "active",
        "tier": "gold",
    }
    log_step("lookup_customer", start, state)
    return {"lookup_result": result}


def decide_next(state: WorkflowState) -> str:
    if state.get("error"):
        if state["error"] == "Transient lookup failure." and state.get("retries", 0) <= MAX_RETRIES:
            return "lookup_customer"
        return "finalize"
    if "lookup_result" not in state:
        return "lookup_customer"
    return "finalize"


def finalize(state: WorkflowState) -> dict:
    start = time.perf_counter()
    if state.get("error"):
        log_step("finalize", start, state)
        return {"final_answer": f"Workflow stopped: {state['error']}"}

    result = state.get("lookup_result", {})
    log_step("finalize", start, state)
    return {
        "final_answer": (
            f"Customer {result.get('customer_id')} is {result.get('status')} "
            f"with tier {result.get('tier')}."
        )
    }


builder = StateGraph(WorkflowState)
builder.add_node("validate_input", validate_input)
builder.add_node("authorize", authorize)
builder.add_node("lookup_customer", lookup_customer)
builder.add_node("finalize", finalize)

builder.add_edge(START, "validate_input")
builder.add_edge("validate_input", "authorize")
builder.add_conditional_edges(
    "authorize",
    lambda state: "finalize" if state.get("error") else "lookup_customer",
    {"lookup_customer": "lookup_customer", "finalize": "finalize"},
)
builder.add_conditional_edges(
    "lookup_customer",
    decide_next,
    {"lookup_customer": "lookup_customer", "finalize": "finalize"},
)
builder.add_edge("finalize", END)

graph = builder.compile()


if __name__ == "__main__":
    result = graph.invoke({"user_id": "alice", "customer_id": "CUST-1001"})
    print(result["final_answer"])
