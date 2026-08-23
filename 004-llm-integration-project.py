from __future__ import annotations

from typing import Literal, NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph


class EmailState(TypedDict):
    subject: str
    body: str
    category: NotRequired[Literal["billing", "support", "sales", "other"]]
    response: NotRequired[str]


def classify_email(state: EmailState) -> dict:
    text = f"{state['subject']} {state['body']}".lower()
    if "invoice" in text or "payment" in text:
        return {"category": "billing"}
    if "help" in text or "issue" in text:
        return {"category": "support"}
    if "buy" in text or "pricing" in text:
        return {"category": "sales"}
    return {"category": "other"}


def draft_response(state: EmailState) -> dict:
    return {
        "response": f"Category: {state['category']}. A human or LLM can draft the reply here."
    }


builder = StateGraph(EmailState)
builder.add_node("classify_email", classify_email)
builder.add_node("draft_response", draft_response)
builder.add_edge(START, "classify_email")
builder.add_edge("classify_email", "draft_response")
builder.add_edge("draft_response", END)

graph = builder.compile()


if __name__ == "__main__":
    print(graph.invoke({"subject": "Invoice question", "body": "Need help with payment status."}))
