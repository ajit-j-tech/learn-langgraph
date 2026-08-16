# Module 05 — Tool Calling (Summary)

## Core Definition

Tools let an LLM request external functions inside a LangGraph workflow.

```text
User → LLM → ToolNode → LLM → Answer
```

## Key Concepts

| Concept | Meaning |
|---|---|
| Tool | A callable function exposed to the model |
| `ToolNode` | Executes tool calls |
| Lifecycle | LLM decides, tool runs, LLM responds |
| Multi-tool | More than one tool is available |
| Error handling | Safe fallback when tool execution fails |

## Where Tools Are Used

- lookups
- calculations
- API calls
- database access
- retrieval

## Tool Design Rules

- keep tools small
- make them deterministic
- use clear names
- validate inputs
- return structured output

## Error Handling

- validate early
- return clear failure states
- add fallback paths
- avoid uncaught tool exceptions

## Mini-Project

Customer lookup assistant:

```text
Question → Customer Lookup Tool → Summary
```

## Golden Principle

```text
LLM decides what to do.
Tool performs the action.
LangGraph controls the flow.
```

