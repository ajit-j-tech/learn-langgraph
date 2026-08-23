# Module 09 - MCP Integration (Summary)

## Core Definition

MCP lets a LangGraph system discover and invoke external tools through a standard client-server contract.

```text
Graph -> MCP adapter -> Tool
```

## Key Concepts

| Concept | Rule |
|---|---|
| Connection | Keep server and transport details in the adapter layer |
| Authentication | Handle secrets outside prompts and shared state |
| Discovery | Ask the server what tools exist before calling them |
| Invocation | Validate tool name and arguments before execution |
| Error handling | Store failures as structured state |

## Safe Design

The graph must still control:

- allowed tools
- allowed inputs
- retry behavior
- fallback paths

## Mini-Project

Build a customer information assistant:

```text
customer_id -> discover tool -> invoke MCP tool -> summarize result
```

The final output should use only retrieved data and should capture failures cleanly.

## Golden Principle

```text
Use MCP to standardize integration.
Use LangGraph to control execution.
```
