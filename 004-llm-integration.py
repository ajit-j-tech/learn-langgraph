from __future__ import annotations

import json
import os
from typing import Literal, NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph

try:
    from langchain_openai import ChatOpenAI
except Exception:  # pragma: no cover - optional dependency fallback
    ChatOpenAI = None  # type: ignore[assignment]


class EmailClassification(TypedDict):
    category: Literal["billing", "support", "sales", "other"]
    confidence: float
    reasoning: str


class EmailClassifierState(TypedDict):
    email_text: str
    prompt: NotRequired[str]
    classification: NotRequired[EmailClassification]
    route: NotRequired[Literal["billing_queue", "support_queue", "sales_queue", "manual_review"]]


def build_prompt(state: EmailClassifierState) -> dict:
    email_text = state["email_text"]
    prompt = (
        "You are an email classifier.\n"
        "Classify the email into one of: billing, support, sales, other.\n"
        "Return a JSON object with keys category, confidence and reasoning.\n\n"
        f"Email:\n{email_text}"
    )
    print("Building prompt")
    return {"prompt": prompt}


def call_model(state: EmailClassifierState) -> dict:
    print("Calling model")

    if ChatOpenAI is None or not os.getenv("OPENAI_API_KEY"):
        text = state["email_text"].lower()
        if any(word in text for word in ["invoice", "charge", "refund", "billing", "payment"]):
            classification: EmailClassification = {"category": "billing", "confidence": 0.96, "reasoining": "NOT_AVAILABLE"}
        elif any(word in text for word in ["bug", "error", "issue", "broken", "help"]):
            classification = {"category": "support", "confidence": 0.94, "reasoining": "NOT_AVAILABLE"}
        elif any(word in text for word in ["buy", "pricing", "demo", "trial", "sales"]):
            classification = {"category": "sales", "confidence": 0.91, "reasoining": "NOT_AVAILABLE"}
        else:
            classification = {"category": "other", "confidence": 0.72, "reasoining": "NOT_AVAILABLE"}
        return {"classification": classification}

    llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0)
    prompt = state["prompt"]
    response = llm.invoke(
        [
            {"role": "system", "content": "Return only category, confidence and reasoning"},
            {"role": "user", "content": prompt},
        ]
    )

    text = getattr(response, "content", "")

    data = json.loads(text)

    category = data["category"]
    confidence = data["confidence"]
    reasoning = data["reasoning"]

    return {"classification": {"category": category, "confidence": confidence, "reasoning": reasoning}}


def route_email(state: EmailClassifierState) -> Literal[
    "billing_queue",
    "support_queue",
    "sales_queue",
    "manual_review",
]:
    category = state["classification"]["category"]
    print("Routing email")
    if category == "billing":
        return "billing_queue"
    if category == "support":
        return "support_queue"
    if category == "sales":
        return "sales_queue"
    return "manual_review"


def billing_queue(state: EmailClassifierState) -> dict:
    print("Sending to billing queue")
    return {"route": "billing_queue"}


def support_queue(state: EmailClassifierState) -> dict:
    print("Sending to support queue")
    return {"route": "support_queue"}


def sales_queue(state: EmailClassifierState) -> dict:
    print("Sending to sales queue")
    return {"route": "sales_queue"}


def manual_review(state: EmailClassifierState) -> dict:
    print("Sending to manual review")
    return {"route": "manual_review"}


graph_builder = StateGraph(EmailClassifierState)

graph_builder.add_node("build_prompt", build_prompt)
graph_builder.add_node("call_model", call_model)
graph_builder.add_node("billing_queue", billing_queue)
graph_builder.add_node("support_queue", support_queue)
graph_builder.add_node("sales_queue", sales_queue)
graph_builder.add_node("manual_review", manual_review)

graph_builder.add_edge(START, "build_prompt")
graph_builder.add_edge("build_prompt", "call_model")
graph_builder.add_conditional_edges(
    "call_model",
    route_email,
    {
        "billing_queue": "billing_queue",
        "support_queue": "support_queue",
        "sales_queue": "sales_queue",
        "manual_review": "manual_review",
    },
)
graph_builder.add_edge("billing_queue", END)
graph_builder.add_edge("support_queue", END)
graph_builder.add_edge("sales_queue", END)
graph_builder.add_edge("manual_review", END)

graph = graph_builder.compile()


if __name__ == "__main__":
    result = graph.invoke(
        {
            "email_text": "Please refund the duplicate charge on invoice 4481.",
        }
    )
    print(result)
