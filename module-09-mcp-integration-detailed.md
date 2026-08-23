# Module 09 - MCP Integration (Detailed)

## Learning Objective

Connect LangGraph to MCP tools through a controlled adapter layer, so the graph can discover capabilities, invoke them safely, and handle failures without breaking the workflow.

By the end of this module, you should understand:

- Connecting to MCP servers
- Discovering and invoking MCP tools
- Authentication
- Transport concepts
- Error handling

---

## 1. Why This Module Matters

MCP gives your graph access to external systems through a standard tool contract.

That matters because most real assistants need data and actions outside the model:

- customer records
- docs and files
- calendars
- CRMs
- internal APIs

The graph should not hardcode every integration. It should call a stable adapter.

---

## 2. What MCP Adds

MCP separates capability discovery from tool execution.

```text
Graph -> MCP client -> Server -> Tool
```

The graph asks:

- what tools exist
- what inputs they expect
- how to call them
- how to recover from failure

This keeps the agent layer cleaner and the integration boundary explicit.

---

## 3. Connection Model

An MCP client connects to one or more servers.

Typical concerns:

- server address
- transport type
- auth token or credentials
- tool schema discovery

Keep connection details out of graph logic. Put them in a client or adapter layer.

---

## 4. Transport Concepts

Transport is how the client and server communicate.

Common mental model:

- stdio for local processes
- HTTP or streaming HTTP for remote services
- structured request and response messages

The important point is not the transport itself. It is that the tool contract stays the same while the wire changes.

---

## 5. Authentication

Some MCP servers are public. Many are not.

You may need:

- API keys
- bearer tokens
- OAuth-based access
- service credentials

Authentication should live in the connector layer, not inside prompts or node logic.

Never pass secrets through shared graph state unless there is a hard requirement and a safe boundary.

---

## 6. Discovery and Invocation

Discovery means asking the MCP server what it exposes.

Invocation means calling a tool with validated input.

Good flow:

```text
Discover tools -> validate tool name -> validate arguments -> invoke -> parse response
```

Bad flow:

```text
Let the LLM invent tool names and raw payloads
```

The graph must still enforce an allowlist.

---

## 7. Error Handling

External tools fail.

Design for:

- server unavailable
- auth failure
- invalid input
- timeout
- malformed tool response

Convert those failures into structured state, not runtime chaos.

Useful state fields:

- `tool_errors`
- `last_tool_name`
- `last_tool_result`
- `known_gaps`
- `retry_count`

---

## 8. State Contract

The graph should keep only durable integration results in shared state.

```python
from typing import Literal, NotRequired, TypedDict


class MCPState(TypedDict):
    customer_id: str
    requested_tool: NotRequired[str]
    tool_result: NotRequired[dict]
    tool_errors: NotRequired[list[str]]
    next_step: NotRequired[Literal["lookup", "summarize", "finish"]]
```

Keep raw transport details and secrets outside state.

---

## 9. Safe Routing

Use the graph to decide when to call an MCP tool.

```text
START -> identify need -> choose allowed tool -> invoke adapter -> finalize
```

The LLM may help with reasoning, but the graph controls:

- allowed servers
- allowed tools
- argument shape
- retry policy
- fallback behavior

---

## 10. Mini-Project: Customer Information Assistant

Build an assistant that:

1. accepts a customer id
2. discovers a customer lookup tool
3. invokes the tool through an adapter
4. stores the result in graph state
5. returns a concise customer summary

### Acceptance Criteria

- tool names come from an allowlist
- auth is handled outside the prompt
- failures are captured in state
- the graph can fall back cleanly if MCP is unavailable
- the final answer uses only retrieved data

---

## 11. Design Rules

Use MCP when:

- the same external capability should work across agents or apps
- you want a standard integration boundary
- tool discovery matters
- you need cleaner separation between reasoning and execution

Do not use MCP as a shortcut for sloppy tool design.

The graph still needs explicit control over what can run, when, and with which inputs.
