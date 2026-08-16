# Module 03 — Building Workflows (Summary)

## Core Definition

LangGraph workflows use edges and routing to control execution order.

```text
State → Decision → Next Step
```

## Flow Patterns

### Sequential

```text
Step A → Step B → Step C
```

### Conditional Routing

```text
Condition
  ├── true → Path A
  └── false → Path B
```

### Loops

```text
Check → Done?
  ├── yes → END
  └── no  → Retry
```

### Parallel Branches

```text
One input → multiple independent nodes
```

### Fan-out / Fan-in

```text
Split work → run branches → aggregate result
```

## Key Rule

Edges control flow.
Nodes contain logic.
State carries decisions.

## Routing

Use a routing function to choose the next node based on state.

```python
def route(state):
    return "approve" if state["valid"] else "reject"
```

## Reducers

Needed when parallel branches update the same state key.

## Mini-Project

Order processing workflow:

```text
Receive Order → Validate → Check Inventory → Route → Fulfill / Reject
```

## Golden Principle

Use deterministic workflows when the process is known and explicit.
