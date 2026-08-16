# Module 01 — LangGraph Fundamentals (Summary)

## Core Definition

LangGraph is a framework for building stateful, graph-based workflows.

```text
Graph = Nodes + Edges + State
```

## Key Concepts

| Concept | Meaning |
|---|---|
| Graph | Workflow |
| Node | Python function or executable step |
| Edge | Defines what runs next |
| State | Shared workflow data |
| START | Entry point |
| END | Exit point |
| `compile()` | Prepares and validates the graph |
| `invoke()` | Executes the graph |

## Execution Lifecycle

```text
Define State
      ↓
Create Graph
      ↓
Add Nodes
      ↓
Add Edges
      ↓
Compile
      ↓
Invoke
```

## Node Contract

A node:

1. Receives state
2. Performs work
3. Returns a partial update

```python
def node(state):
    return {"result": "value"}
```

## Important Principle

Nodes do not call each other.

```text
Node A → Runtime → Node B
```

The runtime uses edges to determine execution.

## Agentic vs Non-Agentic

```text
LangGraph = Stateful orchestration

LLM + tools + reasoning loop = Agentic system
```

LangGraph can also orchestrate ordinary business workflows without an LLM.

## Golden Rules

- Graph = workflow
- Nodes = work
- Edges = control flow
- State = shared data
- `compile()` prepares
- `invoke()` runs
