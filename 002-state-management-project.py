from __future__ import annotations

from decimal import Decimal
from typing import Literal, NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph


class CustomerState(TypedDict):
    customer_id: str
    credit_limit: NotRequired[Decimal]
    balance: NotRequired[Decimal]
    risk_level: NotRequired[Literal["low", "medium", "high"]]


def load_customer(state: CustomerState) -> dict:
    return {"credit_limit": Decimal("5000"), "balance": Decimal("1250")}


def score_risk(state: CustomerState) -> dict:
    balance = state["balance"]
    credit_limit = state["credit_limit"]
    usage = balance / credit_limit
    risk = "high" if usage > 0.8 else "medium" if usage > 0.5 else "low"
    return {"risk_level": risk}


builder = StateGraph(CustomerState)
builder.add_node("load_customer", load_customer)
builder.add_node("score_risk", score_risk)
builder.add_edge(START, "load_customer")
builder.add_edge("load_customer", "score_risk")
builder.add_edge("score_risk", END)

graph = builder.compile()


if __name__ == "__main__":
    print(graph.invoke({"customer_id": "CUST-001"}))
