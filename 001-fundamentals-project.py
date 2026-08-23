from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class GreetingState(TypedDict):
    name: str
    city: str
    greeting: str


def add_name(state: GreetingState) -> dict:
    return {"name": state.get("name", "Learner")}


def add_city(state: GreetingState) -> dict:
    return {"city": "Pune"}


def greet(state: GreetingState) -> dict:
    return {"greeting": f"Hello {state['name']} from {state['city']}."}


builder = StateGraph(GreetingState)
builder.add_node("add_name", add_name)
builder.add_node("add_city", add_city)
builder.add_node("greet", greet)
builder.add_edge(START, "add_name")
builder.add_edge("add_name", "add_city")
builder.add_edge("add_city", "greet")
builder.add_edge("greet", END)

graph = builder.compile()


if __name__ == "__main__":
    result = graph.invoke({"name": "Ajit", "city": ""})
    print(result["greeting"])
