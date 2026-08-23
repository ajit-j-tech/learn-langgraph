from __future__ import annotations

from typing import Annotated, NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

try:
    from langgraph.checkpoint.memory import MemorySaver
except Exception:  # pragma: no cover
    MemorySaver = None  # type: ignore[assignment]


class MemoryState(TypedDict):
    messages: Annotated[list, add_messages]
    user_name: NotRequired[str]


def remember(state: MemoryState) -> dict:
    text = state["messages"][-1]["content"].lower()
    if "my name is" in text:
        name = state["messages"][-1]["content"].split("my name is", 1)[1].strip().rstrip(".")
        return {"user_name": name}
    return {"messages": [{"role": "assistant", "content": f"Hello {state.get('user_name', 'there')}."}]}


builder = StateGraph(MemoryState)
builder.add_node("remember", remember)
builder.add_edge(START, "remember")
builder.add_edge("remember", END)

graph = builder.compile(checkpointer=MemorySaver() if MemorySaver else None)


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "memory-demo"}}
    print(graph.invoke({"messages": [{"role": "user", "content": "My name is Ajit."}]}, config=config))
    print(graph.invoke({"messages": [{"role": "user", "content": "What is my name?"}]}, config=config))
