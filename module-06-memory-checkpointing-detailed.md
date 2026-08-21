# Module 06 - Memory and Checkpointing (Detailed)

## Learning Objective

Understand how LangGraph preserves state across runs, how thread identity separates conversations, and how checkpointing enables resuming execution.

By the end of this module, you should understand:

- Checkpointers
- Conversation memory
- Thread identity
- Resuming execution
- Persistent state

---

## 1. Why This Module Matters

Without memory, every run starts from zero.

That is fine for one-shot tasks, but not for real assistants.

Checkpointing lets the graph remember what happened before:

```text
Run 1 -> Save state
Run 2 -> Load state
Run 3 -> Continue from saved point
```

This is what makes multi-turn conversations and resumable workflows practical.

---

## 2. What Memory Means Here

In LangGraph, memory usually means persisted graph state, not model weights.

It allows the graph to remember:

- past messages
- workflow progress
- extracted data
- user choices
- intermediate decisions

The graph stores state between invocations when a checkpointer is configured.

---

## 3. What a Checkpointer Does

A checkpointer saves graph state after execution steps.

It also reloads the saved state when the same thread runs again.

Use it when you need:

- multi-turn chat
- recovery after interruption
- durable workflow state
- user-specific sessions

Without a checkpointer, state exists only for the current run.

---

## 4. Thread Identity

Thread identity separates one conversation from another.

Typical pattern:

```text
thread_id = "customer-123"
```

If two runs share the same thread id, they can resume the same state.
If they use different thread ids, they are isolated.

This is critical for:

- per-user memory
- session management
- workflow continuation

---

## 5. Resume Behavior

When a graph is invoked with the same thread id, it can continue from the latest saved checkpoint.

That means the second run does not need to resend all previous context manually.

Example flow:

```text
User asks question
Graph stores messages
User follows up later
Graph reloads prior state
```

This is the core of conversational memory.

---

## 6. Persistent State

Persistent state is graph state that survives between runs.

Common use cases:

- conversation history
- step counters
- approval flags
- extracted entities
- routing decisions

Use persistent state only for data that should survive between invocations.

Do not store large or sensitive data without a clear reason.

---

## 7. Minimal Mental Model

```text
Input -> Graph -> Checkpointer -> Saved State
Saved State -> Graph -> Next Input
```

The graph remains deterministic.
The checkpointer only preserves state.

---

## 8. Basic Graph Pattern

```text
START -> Node -> END
```

With checkpointing:

```text
START -> Node -> END
   ^        |
   |        v
   +-- Checkpoint Store
```

The store keeps the latest state for each thread.

---

## 9. What to Store in State

Good state values:

- messages
- ids
- flags
- small structured results
- routing markers

Poor state values:

- giant raw documents
- secrets
- temporary scratch data
- model internals

Keep state small and intentional.

---

## 10. Memory vs Context Window

Memory is not the same as sending a long prompt.

- Context window is what the model sees right now
- Memory is what the graph can reload later

You often combine both:

```text
Loaded state + new user input -> LLM -> new checkpoint
```

---

## 11. Mini-Project: Stateful Chat Assistant

Build a small assistant that remembers the user's name and preference.

Example behavior:

```text
User: My name is Anaya.
Assistant: Noted.

User: What is my name?
Assistant: Your name is Anaya.
```

This demonstrates:

- saving state
- reusing thread identity
- continuing the same conversation

---

## 12. Design Rules

Use checkpointing when:

- a conversation spans multiple turns
- a workflow must resume later
- the graph needs durable state

Avoid overusing checkpointing when:

- the task is one-shot
- state is disposable
- no continuation is needed

---

## 13. Core Principle

```text
Graph state is the memory.
Thread identity is the key.
Checkpointing makes it persistent.
```
