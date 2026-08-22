# Module 07 - Human in the Loop (Summary)

## Core Definition

Human-in-the-loop adds a controlled pause in a LangGraph workflow so a person can approve, reject, or correct a decision before execution continues.

```text
Graph -> Pause -> Human decision -> Resume
```

## Key Concepts

| Concept | Meaning |
|---|---|
| Interrupt | Stops graph execution at a chosen point |
| Approval step | Collects decision context for review |
| Resume | Continues the same thread after input |
| Manual correction | Human updates the pending state and routed fields |

## Why It Matters

- reduces risky automation
- supports compliance and governance
- handles uncertain model decisions
- keeps irreversible actions controlled

## Where It Fits

- after extraction or scoring
- before final side effects
- at policy or risk boundaries

## Mini-Project

Invoice approval workflow:

```text
Analyze invoice -> pause for review -> human approves or corrects -> continue
```

Correction can update fields like:
- amount
- confidence
- reviewer
- approval status

## Golden Principle

```text
Automate the routine.
Pause for judgment.
Resume from the same state.
```
