# Module 04 — LLM Integration (Summary)

## Core Definition

LLMs are used as controlled reasoning nodes inside a LangGraph workflow.

```text
State → Prompt → LLM → Structured Result → Route
```

## Key Concepts

| Concept | Meaning |
|---|---|
| `ChatOpenAI` | Chat model interface |
| Messages | Structured conversation input |
| Prompt | Instructions given to the model |
| Structured output | Machine-readable model result |
| Context | State passed into the model |

## Where to Use LLMs

- classification
- extraction
- summarization
- rewriting
- interpretation

## Where Not to Use LLMs

- hard rules
- arithmetic
- permissions
- deterministic validation
- workflow control

## Prompt Design

Make prompts:

- specific
- bounded
- consistent
- testable

## Messages

Typical roles:

- `system`
- `user`
- `assistant`
- `tool`

## Structured Output

Prefer schema-shaped results over free text.

```python
class Classification(TypedDict):
    category: Literal["billing", "support", "sales", "other"]
    confidence: float
```

## Graph Pattern

```text
Prepare Context → Call LLM → Store Result → Route
```

## Mini-Project

Intelligent email classifier:

```text
Email → Prompt → LLM → Category → Queue
```

## Golden Principle

```text
Use the LLM for reasoning.
Use LangGraph for orchestration.
Use Python for rules.
```
