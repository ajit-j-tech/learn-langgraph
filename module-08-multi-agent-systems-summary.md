# Module 08 - Multi-Agent Systems (Summary)

## Core Definition

A multi-agent system is a LangGraph that coordinates narrowly scoped agents through explicit shared state and controlled routing.

```text
User -> Supervisor -> Specialist -> Supervisor -> Final answer
```

## Choose the Right Design

| Use a workflow when | Use multi-agent coordination when |
|---|---|
| Steps and routing are known | The next role requires judgment |
| Rules can be expressed in code | Distinct expertise improves the outcome |
| Low latency and cost matter most | Work decomposes into bounded subtasks |

## Key Concepts

| Concept | Rule |
|---|---|
| Supervisor | Routes only to allowed agents or `FINISH` |
| Specialist | Owns one narrow responsibility and output schema |
| Shared state | Stores durable artifacts, decisions, and findings |
| Delegation | Defines task, inputs, outputs, and completion rule |
| Termination | Uses an iteration limit and explicit path to `END` |

## GPT-5.6 Terra

Use `gpt-5.6-terra` for the module project. It supports reasoning controls, structured outputs, function calling, and Responses API tools. Start the supervisor at medium reasoning effort and specialists at low; validate changes with evaluation data.

## Mini-Project

Build an evidence-backed research assistant:

```text
Question -> researcher -> analyst -> verifier -> final answer
```

The final result must include answer, citations, confidence, and known gaps.

## Golden Principle

```text
Use deterministic code to control the graph.
Use agents for bounded reasoning inside it.
```
