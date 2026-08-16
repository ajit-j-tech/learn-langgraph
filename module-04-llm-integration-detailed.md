# Module 04 — LLM Integration (Detailed)

## Learning Objective

Understand how to place LLM calls inside LangGraph nodes and use them safely as part of a larger workflow.

By the end of this module, you should understand:

- `ChatOpenAI`
- Prompt construction
- Structured output
- Messages
- Passing context through the graph
- Where LLMs belong in a deterministic workflow

---

## 1. Why This Module Matters

Modules 1 to 3 covered graph structure, state, and workflow control.

Module 4 introduces the LLM as one node type inside the graph.

The key idea is simple:

```text
Deterministic workflow + LLM node = controlled reasoning system
```

LangGraph does not replace prompt engineering or model discipline.
It gives you explicit control over when the LLM runs, what it sees, and what it returns.

---

## 2. Where the LLM Fits

An LLM should usually be used for:

- classification
- extraction
- summarization
- rewriting
- interpretation
- fuzzy decision support

It should usually not be used for:

- hard business rules
- calculations
- permission checks
- deterministic validation
- state transitions that can be encoded directly

```text
State → Rule Node → LLM Node → Rule Node → Output
```

Use the LLM where language understanding is needed.
Use Python where the answer is already known.

---

## 3. `ChatOpenAI`

`ChatOpenAI` is the chat-model interface used to call OpenAI models from LangChain-style code.

Typical usage:

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")
```

You then pass messages to it.

Example:

```python
response = llm.invoke([
    {"role": "system", "content": "You classify emails."},
    {"role": "user", "content": "Please refund my last payment."}
])
```

The model returns a message object, not a final business decision by itself.

---

## 4. Messages

Chat models work on message sequences.

Common roles:

- `system`
- `user`
- `assistant`
- `tool`

Example:

```python
messages = [
    {"role": "system", "content": "You are a strict email classifier."},
    {"role": "user", "content": "Can you share the invoice for order 1042?"}
]
```

Why messages matter:

- they preserve context
- they separate instruction from input
- they support multi-turn reasoning
- they make the conversation structure explicit

In LangGraph, messages are often stored in state and passed from node to node.

---

## 5. Prompt Construction

A prompt is the instruction set given to the model.

Good prompts usually define:

- the role
- the task
- the allowed outputs
- the context fields
- the required format

Example:

```python
system_prompt = """
You are an email classifier.
Classify the message into one of:
- billing
- support
- sales
- other

Return only the category.
"""
```

Then combine it with the user content:

```python
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": email_text}
]
```

Good prompt construction is about reducing ambiguity.

---

## 6. Prompt Design Rules

Use prompts that are:

- specific
- bounded
- consistent
- testable

Avoid prompts that are:

- vague
- open-ended when a label is needed
- overloaded with unrelated instructions
- dependent on hidden assumptions

If the workflow needs a fixed output shape, say so directly.

---

## 7. Structured Output

Structured output means asking the model to return data in a defined schema.

Instead of:

```text
This looks like billing.
```

You want:

```python
{
    "category": "billing",
    "confidence": 0.92
}
```

This is important because downstream nodes need machine-readable output.

Example shape:

```python
from typing import TypedDict, Literal

class Classification(TypedDict):
    category: Literal["billing", "support", "sales", "other"]
    confidence: float
```

Structured output reduces parsing errors and makes workflows more reliable.

---

## 8. Why Structured Output Matters

Free-form text is hard to route on.

```text
"I think this is probably billing?"
```

That is weak for automation.

Structured output lets the graph make deterministic decisions:

```python
if result["category"] == "billing":
    return "billing_queue"
```

This is the bridge between language understanding and workflow control.

---

## 9. Passing Context Through the Graph

The graph state carries the context the LLM needs.

Example state:

```python
{
    "email_text": "Please cancel my subscription.",
    "customer_tier": "enterprise",
    "classification": None
}
```

A node reads from state, constructs the prompt, calls the model, and returns the result:

```python
def classify_email(state):
    email_text = state["email_text"]
    # build prompt from state
    # call model
    return {"classification": "support"}
```

This keeps the workflow explicit.

---

## 10. Minimal Graph Pattern

```text
START
  ↓
Prepare Prompt
  ↓
Call LLM
  ↓
Store Result
  ↓
END
```

The node sequence usually looks like this:

1. prepare context
2. call model
3. normalize output
4. write back to state

This is preferable to burying the entire flow inside one large prompt.

---

## 11. Email Classifier Mini-Project

This module’s mini-project is an intelligent email classifier.

### Typical Flow

```text
Incoming Email
    ↓
Build Prompt
    ↓
LLM Classification
    ↓
Route by Category
    ├── billing → Billing Queue
    ├── support → Support Queue
    ├── sales → Sales Queue
    └── other → Manual Review
```

### Example State

```python
{
    "email_text": "I was charged twice for invoice 4481.",
    "classification": {
        "category": "billing",
        "confidence": 0.96
    }
}
```

### What This Teaches

- prompt shaping
- message construction
- structured model output
- state-driven routing
- clean separation between reasoning and control flow

---

## 12. Practical Design Rule

Do not let the LLM decide everything.

Use the LLM for interpretation.
Use LangGraph for orchestration.
Use deterministic code for control.

```text
LLM = reasoning
Graph = orchestration
Python = rules
```

---

