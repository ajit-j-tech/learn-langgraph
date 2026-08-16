# Module 03 — Building Workflows (Detailed)

## Learning Objective

Understand how to design LangGraph workflows that branch, loop, and run in parallel.

By the end of this module, you should understand:

- Sequential execution
- Conditional routing
- Loops
- Parallel branches
- Fan-out and fan-in
- When workflow design is better than agentic reasoning

---

## 1. Why This Module Matters

Modules 1 and 2 covered graph structure and state.

Module 3 is about control flow.

This is where LangGraph becomes useful for real business processes:

- order processing
- approval flows
- document pipelines
- verification steps
- triage systems

The key idea is simple:

```text
State tells you what happened.
Edges tell you what happens next.
```

---

## 2. Sequential Execution

Sequential execution means one step runs after another.

```text
START
  ↓
Validate Order
  ↓
Calculate Tax
  ↓
Generate Invoice
  ↓
END
```

Use this when the workflow has a fixed order.

### Example

```python
graph_builder.add_edge("validate_order", "calculate_tax")
graph_builder.add_edge("calculate_tax", "generate_invoice")
```

This does not call functions directly.
It declares control flow.

---

## 3. Conditional Routing

Conditional routing chooses the next node based on state.

```text
Validate Order
    ↓
 Is valid?
  ├── yes → Fulfill Order
  └── no  → Reject Order
```

This is used for decisions such as:

- valid vs invalid
- high risk vs low risk
- auto-approve vs manual review
- retry vs stop

### Routing Function

```python
from typing import Literal

def route_order(state) -> Literal["fulfill", "reject"]:
    if state["is_valid"]:
        return "fulfill"
    return "reject"
```

The router decides the next path.
The graph runtime executes that path.

---

## 4. Loops

Loops are used when a workflow must repeat until a condition is met.

```text
Check Status
   ↓
Done?
  ├── yes → END
  └── no  → Wait / Retry / Check Status
```

Typical loop use cases:

- polling external systems
- retrying transient failures
- iterative refinement
- rechecking approvals

### Important Rule

Loops must have a termination condition.
Without one, the workflow can run forever.

---

## 5. Parallel Branches

Parallel branches run multiple nodes from the same state.

```text
             ┌→ Fetch Credit Data
Fetch Order → ├→ Fetch Inventory
             └→ Fetch Customer History
```

Use this when work can happen independently.

Benefits:

- lower latency
- better throughput
- cleaner separation of concerns

---

## 6. Fan-out and Fan-in

Fan-out means splitting one step into many parallel branches.

Fan-in means collecting the results back together.

```text
           Fan-out
              ↓
        A   B   C
         \  |  /
          Fan-in
             ↓
      Aggregate Result
```

This pattern is common in:

- search and retrieval
- document analysis
- multi-source verification
- scoring and ranking

### Why Reducers Matter Here

Parallel branches may update shared state.

If multiple branches write the same field, you need a reducer or aggregation strategy.

---

## 7. Order Processing Mini-Project

This module’s mini-project is an order processing workflow.

### Typical Flow

```text
Receive Order
    ↓
Validate Order
    ↓
Check Inventory
    ↓
Route by Availability
   ├── in stock → Reserve Items → Charge Payment → Create Shipment
   └── out of stock → Backorder or Reject
```

### State Examples

```python
{
    "order_id": "ORD-1001",
    "is_valid": True,
    "inventory_available": False,
    "route": "backorder"
}
```

### What This Teaches

- sequential step chaining
- branch selection from state
- repeatable control flow
- business-process modeling

---

## 8. Design Rules for Workflows

- Use sequential flow for fixed processes
- Use routing for decisions
- Use loops only with a stop condition
- Use parallel branches for independent work
- Use fan-in only when you need aggregation
- Keep business logic in nodes, not edges

---

## 9. When Workflow Beats Agentic Reasoning

Use a workflow when:

- the process is known
- the steps are deterministic
- the control path is explicit
- compliance matters
- debugging must be easy

Use an agent only when:

- the next step cannot be predetermined
- reasoning is genuinely needed
- tool selection depends on context

LangGraph supports both, but workflows should come first.

---

## 10. Lesson Sequence

1. Concept — control flow in LangGraph
2. Architecture — sequential, branching, looping, parallel execution
3. Minimal code
4. Line-by-line explanation
5. Exercise
6. Order processing extension

---

## 11. Core Principle

```text
Nodes do the work.
Edges shape the process.
State drives decisions.
```
