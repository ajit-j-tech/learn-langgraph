# Agentic Systems Learning Syllabus

## Objective

Learn to design and build production-oriented agentic systems using LangGraph, progressing from explicit workflows and state management to LLMs, tools, memory, human approval, multi-agent coordination, MCP, and enterprise reliability.

## Progress legend

- ✅ Completed
- 🚧 In progress
- ⬜ Not started

## Learning path

### ✅ Module 0 — Environment Setup

- Python virtual environments
- LangGraph and supporting dependencies
- OpenAI configuration
- Project structure
- Basic logging and debugging setup

### ✅ Module 1 — LangGraph Fundamentals

- What a graph represents
- State, nodes, and edges
- `START` and `END`
- Graph compilation
- Graph execution with `invoke()`
- How node updates are merged into shared state
- Why nodes do not call one another directly

**Mini-project:** Hello World graph

**Exercise:**

1. Add a third node that adds `city` to state.
2. Pass `name` in the initial state.
3. Generate the greeting from `state["name"]`.

### ✅ Module 2 — State Management

- `TypedDict`
- Shared state
- Partial state updates
- Immutable-update mindset
- Reducers

**Mini-project:** Multi-step customer processing workflow

### ✅ Module 3 — Building Workflows

- Sequential execution
- Conditional routing
- Loops
- Parallel branches
- Fan-out and fan-in

**Mini-project:** Order processing workflow

### ✅ Module 4 — LLM Integration

- `ChatOpenAI`
- Prompt construction
- Structured output
- Messages
- Passing context through the graph

**Mini-project:** Intelligent email classifier

### ✅ Module 5 — Tool Calling

- Defining tools
- `ToolNode`
- Tool execution lifecycle
- Multiple tools
- Tool error handling

**Mini-project:** Customer lookup assistant

### ⬜ Module 6 — Memory and Checkpointing

- Checkpointers
- Conversation memory
- Thread identity
- Resuming execution
- Persistent state

### ⬜ Module 7 — Human in the Loop

- Interrupts
- Approval steps
- Resuming after an interrupt
- Manual corrections

**Mini-project:** Invoice approval workflow

### ⬜ Module 8 — Multi-Agent Systems

- Supervisor pattern
- Specialist agents
- Delegation
- Inter-agent communication
- When a workflow is better than multiple agents

**Mini-project:** Research agent system

### ⬜ Module 9 — MCP Integration

- Connecting to MCP servers
- Discovering and invoking MCP tools
- Authentication
- Transport concepts
- Error handling

**Mini-project:** Customer information assistant using MCP

### ⬜ Module 10 — Enterprise Patterns

- Retries and failure recovery
- Observability and tracing
- Streaming
- Logging
- Configuration management
- Testing and evaluation
- Guardrails
- Cost and latency optimization
- Security and authorization boundaries

### ⬜ Module 11 — Capstone: Cash Application Agent

```text
Read Email
    ↓
Extract Remittance
    ↓
Fetch Bank Payments
    ↓
Matching Engine
    ↓
Confidence Check
    ↓
Human Approval
    ↓
Post Cash
```

The capstone will combine deterministic processing, LLM reasoning, tools, state, conditional routing, persistence, human approval, recovery, observability, and testing.

## Lesson format

Each lesson follows this sequence:

1. Concept — what it is and why it matters
2. Architecture — where it fits in the system
3. Minimal code
4. Line-by-line explanation
5. Exercise
6. Mini-project or practical extension

## Core design principle

Use deterministic code for rules and known business logic. Use an LLM only where interpretation or reasoning is genuinely required. LangGraph coordinates both through explicit state and execution paths.
