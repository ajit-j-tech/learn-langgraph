from __future__ import annotations

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class OrderState(TypedDict):
    order_id: str
    payment_status: Literal["paid", "unpaid"]
    stock_status: Literal["available", "backorder"]
    decision: str


def validate_order(state: OrderState) -> dict:
    return {"decision": "validate"}


def route(state: OrderState) -> str:
    if state["payment_status"] != "paid":
        return "reject"
    if state["stock_status"] != "available":
        return "backorder"
    return "fulfill"


def reject(_: OrderState) -> dict:
    return {"decision": "rejected"}


def backorder(_: OrderState) -> dict:
    return {"decision": "backordered"}


def fulfill(_: OrderState) -> dict:
    return {"decision": "fulfilled"}


builder = StateGraph(OrderState)
builder.add_node("validate_order", validate_order)
builder.add_node("reject", reject)
builder.add_node("backorder", backorder)
builder.add_node("fulfill", fulfill)
builder.add_edge(START, "validate_order")
builder.add_conditional_edges(
    "validate_order",
    route,
    {"reject": "reject", "backorder": "backorder", "fulfill": "fulfill"},
)
builder.add_edge("reject", END)
builder.add_edge("backorder", END)
builder.add_edge("fulfill", END)

graph = builder.compile()


if __name__ == "__main__":
    print(graph.invoke({"order_id": "ORD-1", "payment_status": "paid", "stock_status": "available", "decision": ""}))
