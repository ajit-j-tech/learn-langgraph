# Module 08 - Multi-Agent Systems (Detailed)

## Learning Objective

Design a LangGraph system in which a supervisor routes work to focused specialists, preserves an explicit state contract, and terminates safely.

By the end of this module, you should be able to:

- distinguish workflow orchestration from multi-agent coordination
- define specialist responsibilities and input/output contracts
- route work through a supervisor without uncontrolled delegation loops
- pass structured findings through shared graph state
- evaluate quality, cost, and termination behavior

---

## 1. The Core Idea

A multi-agent system is a graph of narrowly scoped workers coordinated around one user goal. It is not a group chat.

```text
User request
    |
Supervisor (plan + route)
    |
Researcher / Analyst / Verifier
    |
Supervisor (synthesize or continue)
    |
Final answer
```

Each agent has a clear responsibility, allowed tools, expected output schema, and completion condition.

---

## 2. Start With a Workflow

Use a normal LangGraph workflow when the sequence is known and routing can be implemented as code.

```text
extract -> validate -> enrich -> persist
```

Use a multi-agent design only when the task needs judgment about which role should act next, or benefits from genuinely different perspectives.

Multi-agent systems add latency, token cost, and more failure modes. Role separation must justify that overhead.

---

## 3. Supervisor Pattern

The supervisor coordinates work. It should not redo specialist work.

Its responsibilities are:

- inspect the current state
- choose the next eligible specialist or `FINISH`
- create a bounded, well-scoped subtask
- determine whether evidence is sufficient for a final response

Treat routing as structured data rather than prose. A useful decision schema is:

```python
from typing import Literal
from pydantic import BaseModel, Field


class RouteDecision(BaseModel):
    next_agent: Literal["researcher", "analyst", "verifier", "FINISH"]
    task: str = Field(description="A specific task for the selected agent")
    rationale: str = Field(description="Why this is the next useful step")
```

Validate `next_agent` before routing. Never permit an LLM to create arbitrary node names or tool access.

---

## 4. Specialist Agents

A specialist should own one capability and return one predictable type of result.

| Agent | Responsibility | Typical output |
|---|---|---|
| Researcher | Find relevant evidence | Claims with sources |
| Analyst | Compare and reason over evidence | Decision or synthesis |
| Verifier | Identify unsupported claims and conflicts | Pass/fail checks and gaps |
| Writer | Turn approved material into user-facing text | Final draft |

Avoid generic roles such as `helper` or `expert`. They obscure routing decisions and make evaluation impossible.

---

## 5. Shared State Is the Contract

Agents should communicate through typed state, not by relying on a long transcript alone.

```python
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class Finding(TypedDict):
    claim: str
    sources: list[str]
    confidence: Literal["low", "medium", "high"]


class ResearchState(TypedDict):
    user_question: str
    messages: Annotated[list, add_messages]
    findings: list[Finding]
    next_agent: str
    iteration: int
    final_answer: str | None
```

Keep state small and intentional:

- store durable artifacts such as findings, decisions, and citations
- keep agent-private scratch work out of shared state when possible
- add only fields that later nodes need
- make every node return a partial state update

---

## 6. Delegation Contract

Every handoff needs four things:

1. A bounded task: `Find two primary sources about X.`
2. Required inputs: question, constraints, and relevant prior findings.
3. Required outputs: a schema, not free-form commentary.
4. A completion rule: what counts as enough work.

Weak delegation: `Research this topic.`

Strong delegation: `Find up to three primary sources that support or refute claim X. Return claim, URL, publication date, and confidence. Do not draft the final answer.`

---

## 7. GPT-5.6 Terra in This Module

Use `gpt-5.6-terra` when building the learning project: it balances intelligence and cost, supports configurable reasoning, structured outputs, function calling, and Responses API tools. Those capabilities fit supervisor routing and specialist tool use. Start with `reasoning.effort="medium"`; lower it for simple routing and increase it only when evaluation shows a quality need.

Keep the model behind configuration so the graph design remains model-independent:

```python
MODEL_NAME = "gpt-5.6-terra"
SUPERVISOR_REASONING = "medium"
SPECIALIST_REASONING = "low"
```

Model capability does not replace graph controls. The graph must still enforce allowed routes, iteration limits, schemas, and final-answer criteria.

---

## 8. Safe Control Flow

Every multi-agent graph needs explicit guards:

- maximum iteration count
- an allowlist of route targets
- a `FINISH` path to `END`
- fallback behavior when a specialist fails or returns invalid data
- a rule preventing the same task from being delegated repeatedly

```text
if iteration >= MAX_ITERATIONS: finish with known gaps
elif route is FINISH: synthesize and end
elif route is allowed: call selected specialist
else: record invalid route and finish safely
```

Termination is a product requirement, not an implementation detail.

---

## 9. Minimal Graph Shape

```text
START -> supervisor
supervisor -> researcher
supervisor -> analyst
supervisor -> verifier
researcher -> supervisor
analyst -> supervisor
verifier -> supervisor
supervisor -> END
```

Use conditional edges from the supervisor. Specialists normally return control to the supervisor rather than routing directly to each other; this keeps authority centralized and traces easy to read.

---

## 10. Mini-Project: Evidence-Backed Research Agent

Build a research assistant that answers a question with traceable evidence.

### Requirements

1. Accept a research question and explicit constraints.
2. Route to a researcher for source-backed findings.
3. Route to an analyst only after enough findings exist.
4. Route to a verifier before finalizing.
5. Return a concise answer, citations, known gaps, and a confidence level.

### Acceptance Criteria

- The supervisor can select only known agents or `FINISH`.
- Each finding includes a claim, source, and confidence.
- The graph ends within the configured iteration limit.
- Unsupported claims appear in `known_gaps`, not in the final answer as facts.
- A trace shows every routing decision and specialist result.

---

## 11. Evaluation Checklist

Test the system with representative questions, not only happy paths.

- Routing: does the supervisor select the right role?
- Grounding: are final claims supported by collected findings?
- Termination: does every path reach `END`?
- Recovery: what happens after a tool failure or malformed output?
- Cost: does adding an agent improve quality enough to justify the extra calls?

## Design Principle

Use deterministic code for constraints, routing allowlists, validation, and termination. Use agents for bounded reasoning and interpretation inside those constraints.
