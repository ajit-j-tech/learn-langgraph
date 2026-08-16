# Module 02 — State Management (Summary)

## Core Definition

State is the shared workflow data object and the single source of truth.

```text
Read State
      ↓
Perform Work
      ↓
Return Partial Update
      ↓
Runtime Merges Update
```

## Node Contract

Every node:

1. Reads state
2. Performs logic
3. Returns only changed fields

```python
def validate(state):
    return {"validated": True}
```

## `TypedDict`

Defines the expected state schema.

```python
class State(TypedDict):
    customer_id: str
    validated: NotRequired[bool]
```

Important:

- Provides static typing
- Does not enforce runtime validation
- Use `NotRequired` for fields added later

## Merge Behavior

### Sequential

Later update wins.

```text
discount = 10
      ↓
discount = 20
```

Final:

```python
{"discount": 20}
```

### Parallel

Different keys can merge safely.

Same key requires a reducer.

## Reducers

Reducers define how concurrent updates are combined.

```python
from typing import Annotated
import operator

class State(TypedDict):
    logs: Annotated[list[str], operator.add]
```

Typical uses:

- Logs
- Messages
- Findings
- Events
- Aggregated results

## Nested State

Group related domain data.

```python
class Employee(TypedDict):
    employee_id: str
    name: str

class State(TypedDict):
    employee: Employee
```

Do not assume nested dictionaries are deep-merged automatically.

## Enterprise Design Rules

- Model business objects, not node outputs
- Use domain-specific field names
- Separate inputs, working data, decisions, outputs, and metadata
- Store references instead of large payloads
- Never store secrets
- Avoid duplicate state
- Keep operational metadata separate

## Universal State Structure

```python
class WorkflowState(TypedDict):

    # Inputs

    # Retrieved Data

    # Derived Data

    # Decisions

    # Human Actions

    # Outputs

    # Metadata
```

## Golden Principle

```text
State models the business.

Nodes implement business logic.

Edges model the business process.
```
