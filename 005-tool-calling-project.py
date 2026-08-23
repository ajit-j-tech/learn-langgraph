from __future__ import annotations

from typing import NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph


class LookupState(TypedDict):
    customer_id: str
    customer: NotRequired[dict]
    answer: NotRequired[str]


def lookup_customer(state: LookupState) -> dict:
    return {
        "customer": {
            "customer_id": state["customer_id"],
            "name": "Anaya Sharma",
            "tier": "gold",
        }
    }


def answer(state: LookupState) -> dict:
    customer = state["customer"]
    return {"answer": f"{customer['name']} is a {customer['tier']} customer."}


builder = StateGraph(LookupState)
builder.add_node("lookup_customer", lookup_customer)
builder.add_node("answer", answer)
builder.add_edge(START, "lookup_customer")
builder.add_edge("lookup_customer", "answer")
builder.add_edge("answer", END)

graph = builder.compile()


if __name__ == "__main__":
    print(graph.invoke({"customer_id": "CUST-1001"}))
