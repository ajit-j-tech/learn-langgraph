from typing import TypedDict

# Create the required state
class State(TypedDict):
    message: str
    age: int

# Create Node
def greeting(state: State):
    print("Greetings Node")

    return {
        "message": "Hello AJ"
    }

def add_age(state: State):
    print("Age Node")

    return {
        "age": 30
    }

# Create Graph
from langgraph.graph import StateGraph

graph_builder = StateGraph(state_schema=State)

# add the nodes to the Graph
graph_builder.add_node("greeting", greeting)
graph_builder.add_node("age", add_age)

# Connect the nodes via edges
from langgraph.graph import START, END
graph_builder.add_edge(START, "greeting")
graph_builder.add_edge("greeting", "age")
graph_builder.add_edge("age", END)

# compile the Graph
graph = graph_builder.compile()

# Execute the graph with empty state
result = graph.invoke({})
print(result)