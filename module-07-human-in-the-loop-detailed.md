# Module 07 - Human in the Loop (Detailed)

## Learning Objective

Understand how to pause a LangGraph workflow for human review, resume execution after approval, and apply manual corrections without breaking the graph model.

By the end of this module, you should understand:

- Interrupts
- Approval steps
- Resuming after an interrupt
- Manual corrections

---

## 1. Why This Module Matters

Not every step should be automatic.

Some actions need a person to confirm them before the workflow continues:

- posting payments
- approving invoices
- sending customer-facing messages
- making compliance-sensitive decisions

Human-in-the-loop keeps the system controlled while still allowing automation everywhere else.

---

## 2. What an Interrupt Is

An interrupt is a deliberate pause in graph execution.

The graph stops at a chosen point and waits for an external decision.

```text
Workflow running -> Interrupt -> Human review -> Resume
```

Use interrupts when:

- the action is risky
- the model is uncertain
- business policy requires approval
- a person needs to correct data before continuing

---

## 3. Approval Steps

An approval step is a node that prepares decision data for a human.

Typical approval payload:

- invoice id
- extracted amount
- confidence score
- current review status
- reviewer identity
- fields that may need correction

The graph should present clear context so the human can decide quickly.

---

## 4. Resuming After an Interrupt

When the human responds, the graph continues from the paused point.

That means you do not restart the whole workflow from scratch.

```text
Run 1 -> pause
Run 2 -> resume from same thread
```

This only works cleanly when checkpointing is enabled and thread identity is consistent.

---

## 5. Manual Corrections

Sometimes the human does not just approve or reject.

They correct the data:

- fix invoice amount
- replace a missing customer id
- choose the right match
- add a note for downstream steps

The workflow should treat the correction as updated state and continue from there.

In practice, this means the resumed decision can overwrite fields such as:

- amount
- confidence
- reviewer
- approval status

The correction is not just a note. It becomes the next state.

---

## 6. Minimal Mental Model

```text
Input -> Validate -> Interrupt for review -> Human decision -> Continue
```

The graph remains deterministic.
The human supplies the decision at the pause point.

---

## 7. Where This Fits in the System

Human review usually sits after:

- extraction
- matching
- scoring
- rule checks

and before:

- posting
- sending
- finalizing
- committing side effects

This creates a control boundary before irreversible actions.

---

## 8. Minimal Graph Pattern

```text
START -> Prepare Review -> Interrupt -> Apply Decision -> END
```

The graph gathers evidence first.
Then it waits for approval.
Then it resumes with the approved or corrected decision.

---

## 9. Invoice Approval Mini-Project

Build a workflow that:

1. receives an invoice candidate
2. checks amount and match confidence
3. pauses if approval is needed
4. resumes when a human approves, rejects, or corrects it
5. writes the final decision and any corrected fields into state

Example decision types:

- approve
- reject
- correct amount
- correct confidence
- send back for review

---

## 10. Design Rules

Use human-in-the-loop when:

- the cost of a wrong action is high
- the model is uncertain
- policy requires review
- the user should control the final step

Keep the approval payload:

- short
- structured
- easy to inspect
- focused on the decision

Do not pause on every step.
Only interrupt where human judgment adds value.
