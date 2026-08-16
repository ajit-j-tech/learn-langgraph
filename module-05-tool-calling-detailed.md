# Module 05 — Tool Calling (Detailed)

## Learning Objective

Understand how to let an LLM decide when to call tools inside a LangGraph workflow, and how to keep that execution controlled and recoverable.

By the end of this module, you should understand:

- Defining tools
- `ToolNode`
- Tool execution lifecycle
- Multiple tools
- Tool error handling
- Where tools fit in a graph

---

## 1. Why This Module Matters

LLMs are not enough when the workflow needs fresh, external, or deterministic data.

Tool calling closes that gap.

```text
User Query → LLM Decision → Tool Call → Tool Result → LLM Response
```

Use tools for:

- lookups
- calculations
- API calls
- database queries
- retrieval

Do not use tools as a substitute for simple local logic.

---

## 2. What a Tool Is

A tool is a function the model can request when it needs an external action.

Typical examples:

- customer lookup
- order status fetch
- calculator
- document search

Tools should be:

- small
- deterministic
- explicit in behavior
- easy to test

---

## 3. Tool Definition

A tool is usually a normal Python function with a clear input and output.

Example:

```python
def lookup_customer(customer_id: str) -> dict:
    return {
        "customer_id": customer_id,
        "name": "Asha Patel",
        "tier": "gold",
        "status": "active",
    }
```

The model does not execute this directly.
LangGraph routes execution to it.

---

## 4. Tool-Calling Flow

The standard flow is:

```text
User Message
   ↓
LLM decides whether a tool is needed
   ↓
ToolNode executes the tool
   ↓
Tool result goes back into messages
   ↓
LLM produces final answer
```

This keeps model reasoning and external execution separate.

---

## 5. `ToolNode`

`ToolNode` is the LangGraph node that executes requested tools.

It reads tool calls from messages and runs the matching Python function.

Use it when:

- the LLM may request a tool
- multiple tools may be available
- you want a standard tool execution path

---

## 6. Multiple Tools

Real workflows often expose more than one tool.

Example set:

- `lookup_customer`
- `get_order_status`
- `calculate_refund`

The LLM chooses which one to call based on the user request and context.

Keep tool names and descriptions specific so routing is reliable.

---

## 7. Tool Execution Lifecycle

The lifecycle is:

1. User provides input
2. LLM inspects input
3. LLM emits a tool call if needed
4. `ToolNode` executes the tool
5. Tool output is added back to messages
6. LLM reads the tool result
7. LLM returns the final response

Important point:

The LLM should not guess data that the tool can fetch.

---

## 8. Minimal Graph Pattern

```text
START → LLM Node → ToolNode → LLM Node → END
```

The LLM node decides whether to stop or call a tool.
If it calls a tool, the graph routes to `ToolNode`.

---

## 9. Tool Error Handling

Tool failures are expected.

Common failure cases:

- missing input
- invalid format
- network failure
- not found
- authorization failure

Handle errors by:

- validating inputs early
- returning clear error messages
- routing to fallback paths when needed
- avoiding uncaught exceptions in production workflows

Example fallback behavior:

```text
Tool failed → Return error state → Ask user for correction
```

---

## 10. Customer Lookup Mini-Project

This module’s mini-project is a customer lookup assistant.

### Goal

Answer questions like:

- “What is the status of customer C-102?”
- “Find the tier for customer 44.”
- “Look up customer details and summarize them.”

### Flow

```text
Question → Decide Tool → Lookup Customer → Summarize Result
```

### Why This Is a Good Example

- It needs external data
- The lookup is deterministic
- The response still benefits from LLM language generation

---

## 11. Design Rules

Use tools when:

- the answer lives outside the model
- the operation is deterministic
- the workflow needs a concrete action

Avoid tools when:

- a local function is enough
- the model is being asked to do direct reasoning only
- the action is unsafe without approval

---

## 12. Core Principle

```text
LLM decides.
Tool executes.
Graph controls.
```

