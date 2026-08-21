# Module 06 - Memory and Checkpointing (Summary)

## Core Definition

Checkpointing lets LangGraph save and reload state so a workflow can continue across runs.

```text
Run -> Save State -> Later Run -> Resume State
```

## Key Concepts

| Concept | Meaning |
|---|---|
| Checkpointer | Saves graph state |
| Memory | Persisted conversation or workflow state |
| Thread identity | Key that separates sessions |
| Resume | Continue from saved state |
| Persistent state | Data kept across invocations |

## What It Enables

- multi-turn chat
- session continuity
- workflow recovery
- durable progress tracking

## State to Persist

- messages
- user identifiers
- workflow flags
- extracted data
- routing markers

## Design Rules

- keep state small
- use thread ids consistently
- store only what must survive
- avoid putting secrets in state

## Mini-Project

Stateful chat assistant:

```text
User says name -> graph stores it -> later turn recalls it
```

## Golden Principle

```text
State is remembered.
Thread id selects the session.
Checkpointing makes continuation possible.
```
