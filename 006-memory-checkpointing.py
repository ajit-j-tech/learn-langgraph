from __future__ import annotations

from typing import Annotated, NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

try:
    from langgraph.checkpoint.memory import MemorySaver
except Exception:  # pragma: no cover - optional dependency fallback
    MemorySaver = None  # type: ignore[assignment]


class MemoryState(TypedDict):
    messages: Annotated[list, add_messages]
    user_name: NotRequired[str]
    favorite_topic: NotRequired[str]


def remember_user(state: MemoryState) -> dict:
    last_message = state["messages"][-1]["content"].lower()

    if "my name is" in last_message:
        name = state["messages"][-1]["content"].split("my name is", 1)[1].strip().rstrip(".")
        return {
            "user_name": name,
            "messages": [{"role": "assistant", "content": f"Noted. I will remember your name as {name}."}],
        }

    if "favorite topic is" in last_message:
        topic = state["messages"][-1]["content"].split("favorite topic is", 1)[1].strip().rstrip(".")
        return {
            "favorite_topic": topic,
            "messages": [{"role": "assistant", "content": f"Noted. Your favorite topic is {topic}."}],
        }

    if "what is my name" in last_message:
        name = state.get("user_name", "unknown")
        return {"messages": [{"role": "assistant", "content": f"Your name is {name}."}]}

    if "what is my favorite topic" in last_message:
        topic = state.get("favorite_topic", "unknown")
        return {"messages": [{"role": "assistant", "content": f"Your favorite topic is {topic}."}]}

    return {"messages": [{"role": "assistant", "content": "Tell me your name or favorite topic, or ask me to recall it."}]}


builder = StateGraph(MemoryState)
builder.add_node("remember_user", remember_user)
builder.add_edge(START, "remember_user")
builder.add_edge("remember_user", END)

checkpointer = MemorySaver() if MemorySaver is not None else None
graph = builder.compile(checkpointer=checkpointer)


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "user-001"}}

    first = graph.invoke(
        {"messages": [{"role": "user", "content": "My name is Anaya."}]},
        config=config,
    )
    print(first)

    second = graph.invoke(
        {"messages": [{"role": "user", "content": "What is my name?"}]},
        config=config,
    )
    print(second)
