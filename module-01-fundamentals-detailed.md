# Module 01 — LangGraph Fundamentals (Detailed)

## Learning Objective

Understand the core execution model of LangGraph before introducing LLMs, tools, memory, or agents.

By the end of this module, you should understand:

- What a graph represents
- What nodes and edges are
- How shared state flows through a graph
- The purpose of `START` and `END`
- What `compile()` does
- What `invoke()` does
- Why nodes do not call each other directly
- Why LangGraph can be used beyond agentic systems

---

## 1. LangGraph in One Sentence

LangGraph is a framework for building stateful, graph-based workflows.

It can orchestrate:

- LLM calls
- Tools
- APIs
- Databases
- Human approvals
- Deterministic business logic
- Long-running workflows

LangGraph itself is not the LLM and is not inherently agentic.

```text
Your Application
      ↓
LangGraph Runtime
      ↓
Nodes: Python / LLM / API / Tool / Human
```

---

## 2. What Is a Graph?

A graph is a workflow represented as connected steps.

Example:

```text
Receive Order
      ↓
Validate Order
      ↓
Calculate Tax
      ↓
Generate Invoice
```

Each step is a node.

Each arrow is an edge.

In LangGraph:

```text
Graph = Nodes + Edges + State
```

---

## 3. Core Terminology

| Concept | Meaning |
|---|---|
| Graph | The workflow |
| Node | A Python function or executable step |
| Edge | Defines what runs next |
| State | Shared workflow data |
| START | Entry point |
| END | Exit point |
| `compile()` | Validates and prepares the graph |
| `invoke()` | Executes the graph |

---

## 4. What Is a Node?

A node is typically a Python function.

```python
def greet(state):
    return {"message": "Hello"}
```

A node:

1. Receives the current state
2. Performs work
3. Returns a partial state update

A node may contain:

- Plain Python logic
- An LLM call
- A database query
- An API request
- A tool call
- Human approval logic

LangGraph does not care what the node does internally.

---

## 5. What Is an Edge?

An edge defines execution order.

```text
Node A → Node B
```

Example:

```python
graph_builder.add_edge("greeting", "age")
```

This does not call the `age` function directly.

It tells the graph runtime:

> After `greeting` completes, schedule `age`.

---

## 6. What Is State?

State is the shared data object that evolves throughout execution.

Example:

```python
{
    "name": "AJ",
    "message": "Hello AJ",
    "age": 30
}
```

Each node receives the current state and may return updates.

Example evolution:

```text
{}
    ↓
{"message": "Hello AJ"}
    ↓
{"message": "Hello AJ", "age": 30}
```

State is introduced here at a basic level. Its deeper behavior is covered in Module 2.

---

## 7. START and END

`START` and `END` are special LangGraph nodes.

```text
START
   ↓
Greeting
   ↓
Age
   ↓
END
```

- `START` identifies the first executable node.
- `END` marks successful completion.

They are imported from:

```python
from langgraph.graph import START, END
```

---

## 8. Graph Lifecycle

Every LangGraph program follows this lifecycle:

```text
Define State
      ↓
Create Graph Builder
      ↓
Add Nodes
      ↓
Add Edges
      ↓
Compile Graph
      ↓
Invoke Graph
```

### Step 1 — Define State

```python
from typing import TypedDict

class State(TypedDict):
    message: str
    age: int
```

### Step 2 — Define Nodes

```python
def greeting(state: State):
    return {"message": "Hello AJ"}

def add_age(state: State):
    return {"age": 30}
```

### Step 3 — Create Graph Builder

```python
from langgraph.graph import StateGraph

graph_builder = StateGraph(State)
```

### Step 4 — Register Nodes

```python
graph_builder.add_node("greeting", greeting)
graph_builder.add_node("age", add_age)
```

### Step 5 — Add Edges

```python
from langgraph.graph import START, END

graph_builder.add_edge(START, "greeting")
graph_builder.add_edge("greeting", "age")
graph_builder.add_edge("age", END)
```

### Step 6 — Compile

```python
graph = graph_builder.compile()
```

### Step 7 — Invoke

```python
result = graph.invoke({})
```

---

## 9. Complete Example

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    message: str
    age: int


def greeting(state: State):
    print("Greeting Node")
    return {"message": "Hello AJ"}


def add_age(state: State):
    print("Age Node")
    return {"age": 30}


graph_builder = StateGraph(State)

graph_builder.add_node("greeting", greeting)
graph_builder.add_node("age", add_age)

graph_builder.add_edge(START, "greeting")
graph_builder.add_edge("greeting", "age")
graph_builder.add_edge("age", END)

graph = graph_builder.compile()

result = graph.invoke({})

print(result)
```

Expected output:

```text
Greeting Node
Age Node
{'message': 'Hello AJ', 'age': 30}
```

---

## 10. What `compile()` Does

`compile()` does not execute the workflow.

It prepares the graph for execution.

Conceptually, it:

- Validates the graph structure
- Verifies node and edge references
- Creates an executable graph object
- Prepares runtime behavior

Think of it as preparing a workflow definition before running it.

```text
Graph Definition
      ↓
compile()
      ↓
Executable Graph
```

---

## 11. What `invoke()` Does

`invoke()` starts execution.

```python
result = graph.invoke(initial_state)
```

Execution flow:

```text
Initial State
      ↓
START
      ↓
First Node
      ↓
State Update
      ↓
Next Node
      ↓
END
      ↓
Final State
```

The argument passed to `invoke()` is the initial state.

---

## 12. Nodes Do Not Call Each Other

This is a critical architectural distinction.

Normal Python:

```python
def a():
    b()
```

LangGraph:

```text
Node A
   ↓
LangGraph Runtime
   ↓
Node B
```

The graph runtime controls execution based on edges.

This enables:

- Conditional routing
- Parallel execution
- Loops
- Retries
- Checkpointing
- Resume after interruption
- Human-in-the-loop

If nodes directly called each other, the runtime would lose control over orchestration.

---

## 13. LangGraph Is Not Mandatory for Agentic Systems Only

LangGraph can be used for non-agentic stateful workflows.

Example:

```text
Receive Order
      ↓
Validate Inventory
      ↓
Process Payment
      ↓
Manager Approval
      ↓
Arrange Shipment
```

No LLM is required.

A useful distinction:

```text
LangGraph = Stateful orchestration runtime

LLM + tools + reasoning loop = Agentic behavior
```

LangGraph becomes agentic only when nodes use LLM reasoning, tool selection, planning, or autonomous routing.

---

## 14. When LangGraph Is Appropriate

LangGraph is useful when workflows require:

- Shared state
- Branching
- Loops
- Parallel execution
- Long-running processes
- Persistence
- Human approval
- Resume after interruption
- Multiple external systems

For a simple sequential Python script, LangGraph may be unnecessary.

---

## 15. Mental Model

```text
State moves through the graph.

Nodes transform state.

Edges control movement.

The runtime controls execution.
```

---

## 16. Common Mistakes

### Mistake 1 — Treating LangGraph as the AI

LangGraph is the orchestration layer, not the model.

### Mistake 2 — Making nodes call each other

Edges should define execution order.

### Mistake 3 — Returning complete state from every node

Nodes should normally return only updates.

### Mistake 4 — Using LangGraph for a trivial script

Use it where orchestration complexity justifies it.

### Mistake 5 — Confusing compile and execute

- `compile()` prepares
- `invoke()` runs

---

## 17. Key Takeaways

- A graph represents a workflow.
- A node is an executable step.
- An edge controls execution order.
- State is shared workflow data.
- `START` and `END` define boundaries.
- `compile()` prepares the graph.
- `invoke()` executes it.
- Nodes do not call one another directly.
- LangGraph can orchestrate both agentic and non-agentic workflows.
