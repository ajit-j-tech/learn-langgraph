from __future__ import annotations

from typing import Annotated, Literal, NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

try:
    from langchain_core.messages import AIMessage
    from langchain_core.tools import tool
except Exception:  # pragma: no cover - optional dependency fallback
    AIMessage = None  # type: ignore[assignment]

    def tool(*args, **kwargs):  # type: ignore[override]
        def decorator(fn):
            return fn

        return decorator

try:
    from langchain_openai import ChatOpenAI
except Exception:  # pragma: no cover - optional dependency fallback
    ChatOpenAI = None  # type: ignore[assignment]


class MessageState(TypedDict):
    messages: Annotated[list, add_messages]
    route: NotRequired[Literal["tools", "final"]]


@tool
def lookup_customer(customer_id: str) -> dict:
    """Look up a customer by ID."""
    database = {
        "C-100": {"customer_id": "C-100", "name": "Asha Patel", "tier": "gold", "status": "active"},
        "C-101": {"customer_id": "C-101", "name": "Marcus Lee", "tier": "silver", "status": "paused"},
        "C-102": {"customer_id": "C-102", "name": "Nina Rao", "tier": "platinum", "status": "active"},
    }
    if customer_id not in database:
        return {"error": f"Customer {customer_id} not found"}
    return database[customer_id]


@tool
def get_customer_balance(customer_id: str) -> dict:
    """Return the current balance for a customer."""
    balances = {"C-100": 1200.50, "C-101": 0.0, "C-102": 845.75}
    if customer_id not in balances:
        return {"error": f"Balance not available for {customer_id}"}
    return {"customer_id": customer_id, "balance": balances[customer_id], "currency": "USD"}


tools = [lookup_customer, get_customer_balance]
tool_node = ToolNode(tools)


def call_llm(state: MessageState) -> dict:
    if ChatOpenAI is None:
        last = state["messages"][-1].content.lower()
        if "balance" in last:
            return {
                "messages": [
                    {
                        "role": "assistant",
                        "content": "I need to check the customer balance. Please provide a customer id like C-102.",
                    }
                ],
                "route": "final",
            }
        if "customer" in last:
            return {
                "messages": [
                    {
                        "role": "assistant",
                        "content": "I need to look up the customer. Please provide a customer id like C-102.",
                    }
                ],
                "route": "final",
            }
        return {"messages": [{"role": "assistant", "content": "Please ask for a customer lookup or balance check."}], "route": "final"}

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    llm_with_tools = llm.bind_tools(tools)
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


def route_tools(state: MessageState) -> Literal["tools", "final"]:
    last_message = state["messages"][-1]
    tool_calls = getattr(last_message, "tool_calls", None)
    if tool_calls:
        return "tools"
    return "final"


def finalize(state: MessageState) -> dict:
    if AIMessage is None:
        return {"route": "final"}

    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return {"route": "tools"}

    return {"route": "final"}


graph_builder = StateGraph(MessageState)
graph_builder.add_node("call_llm", call_llm)
graph_builder.add_node("tools", tool_node)
graph_builder.add_node("finalize", finalize)

graph_builder.add_edge(START, "call_llm")
graph_builder.add_conditional_edges("call_llm", route_tools, {"tools": "tools", "final": "finalize"})
graph_builder.add_edge("tools", "call_llm")
graph_builder.add_edge("finalize", END)

graph = graph_builder.compile()


if __name__ == "__main__":
    result = graph.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Look up customer C-102 and tell me their balance.",
                }
            ]
        }
    )
    print(result)
