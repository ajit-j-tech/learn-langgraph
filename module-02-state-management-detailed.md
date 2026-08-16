# Module 02 — State Management (Detailed)

## Learning Objective

Understand how LangGraph represents, updates, merges, and designs workflow state.

By the end of this module, you should understand:

- State as the single source of truth
- `TypedDict`
- Required and optional fields
- Partial state updates
- Merge behavior
- Nested state behavior
- Reducers
- Parallel update conflicts
- Enterprise state design patterns
- Operational metadata separation

---

## 1. State as the Single Source of Truth

State is the shared workflow object passed across nodes.

Instead of passing many independent variables:

```python
customer
discount
risk
quote
payment
```

LangGraph uses one shared object:

```python
state
```

Example:

```python
{
    "customer": {...},
    "discount": 15,
    "risk_score": 0.12,
    "quote": {...}
}
```

Each node reads the fields it needs and returns the fields it updates.

---

## 2. State as a Shared Whiteboard

Think of state as a shared whiteboard.

```text
          State

Node A reads and updates
Node B reads and updates
Node C reads and updates
```

Nodes do not pass independent return values directly to each other.

The runtime manages state evolution.

---

## 3. State Is Not Memory

State and memory are different.

### State

Current workflow data:

```python
{
    "customer_id": "C-100",
    "discount": 15
}
```

### Memory

Information retained across conversations or prior executions.

Memory is covered separately in the checkpointing and memory module.

---

## 4. State Is the Contract Between Nodes

Each node agrees to:

1. Read what it needs from state
2. Perform its logic
3. Return only its updates

```text
Read State
      ↓
Perform Work
      ↓
Return Partial Update
```

This is the fundamental LangGraph node contract.

---

## 5. Why Use `TypedDict`?

A normal dictionary provides no static schema.

```python
state = {
    "employee_id": "EMP-101",
    "documents_verified": True
}
```

A typo may remain unnoticed until runtime:

```python
state["document_verified"]
```

`TypedDict` defines expected keys and types.

```python
from typing import TypedDict

class EmployeeState(TypedDict):
    employee_id: str
    documents_verified: bool
```

Benefits:

- Editor support
- Autocomplete
- Static type checking
- Clear state contract
- Better maintainability

---

## 6. `TypedDict` Does Not Validate at Runtime

`TypedDict` is primarily a static typing mechanism.

This may still run:

```python
state: EmployeeState = {
    "employee_id": 100
}
```

Even though the declared type is `str`.

For runtime validation, use a runtime validation model such as Pydantic.

---

## 7. Required and Optional Fields

A workflow often begins with only a subset of its final state.

Example initial state:

```python
{
    "employee_id": "EMP-101"
}
```

Later nodes add:

- `documents_verified`
- `corporate_email`
- `laptop_asset_id`

Use `NotRequired` for fields created later.

```python
from typing import NotRequired, TypedDict

class EmployeeOnboardingState(TypedDict):
    employee_id: str
    documents_verified: NotRequired[bool]
    corporate_email: NotRequired[str]
    laptop_asset_id: NotRequired[str]
    manager_notified: NotRequired[bool]
```

Here:

- `employee_id` is required
- Other fields are added during execution

---

## 8. `total=False`

An alternative is:

```python
class EmployeeOnboardingState(TypedDict, total=False):
    employee_id: str
    documents_verified: bool
    corporate_email: str
```

This makes all fields optional.

It is convenient but more permissive.

For enterprise workflows, explicit `NotRequired` fields usually communicate intent more clearly.

---

## 9. Partial State Updates

The state schema represents the complete possible state.

A node should return only its updates.

```python
def validate_documents(state: EmployeeOnboardingState):
    return {
        "documents_verified": True
    }
```

Input state:

```python
{
    "employee_id": "EMP-101"
}
```

Node output:

```python
{
    "documents_verified": True
}
```

Merged state:

```python
{
    "employee_id": "EMP-101",
    "documents_verified": True
}
```

The node output is a state update, not the complete state.

---

## 10. Why Nodes Should Not Mutate State Directly

Avoid:

```python
state["documents_verified"] = True
return state
```

Prefer:

```python
return {"documents_verified": True}
```

This allows the LangGraph runtime to control:

- Merge behavior
- Parallel writes
- Checkpointing
- Deterministic updates
- Reducers
- Resume behavior

The node receives a state snapshot and returns an update.

---

## 11. State Update Lifecycle

```text
Current State
      ↓
Node Receives State
      ↓
Node Performs Logic
      ↓
Node Returns Partial Update
      ↓
LangGraph Merges Update
      ↓
Next Node Receives New State
```

---

## 12. Sequential Merge Behavior

Suppose Node A returns:

```python
{"discount": 10}
```

Node B later returns:

```python
{"discount": 20}
```

In a sequential graph:

```text
Node A → Node B
```

The later update replaces the earlier value.

Final state:

```python
{"discount": 20}
```

---

## 13. Parallel Merge Behavior

Consider:

```text
          START
         /     \
        ↓       ↓
     Node A   Node B
         \     /
          ↓   ↓
           END
```

If Node A and Node B update different keys, LangGraph can merge them.

Node A:

```python
{"customer_name": "AJ"}
```

Node B:

```python
{"customer_address": "Mumbai"}
```

Result:

```python
{
    "customer_name": "AJ",
    "customer_address": "Mumbai"
}
```

No conflict exists.

---

## 14. Parallel Write Conflict

If both branches update the same key:

Node A:

```python
{"logs": ["Customer extracted"]}
```

Node B:

```python
{"logs": ["Address extracted"]}
```

LangGraph cannot infer whether it should:

- Keep A
- Keep B
- Concatenate both
- Deduplicate values
- Pick the latest
- Pick the highest-priority result

This is why reducers exist.

---

## 15. Reducers

A reducer defines how multiple updates to the same state key should be combined.

Example:

```python
from typing import Annotated
import operator

class State(TypedDict):
    logs: Annotated[list[str], operator.add]
```

This means:

> When multiple updates target `logs`, combine them using list addition.

Node A:

```python
{"logs": ["Customer extracted"]}
```

Node B:

```python
{"logs": ["Address extracted"]}
```

Merged result:

```python
{
    "logs": [
        "Customer extracted",
        "Address extracted"
    ]
}
```

---

## 16. Why `Annotated`?

`Annotated` attaches metadata to a type.

```python
Annotated[list[str], operator.add]
```

The underlying type is:

```python
list[str]
```

The extra metadata tells LangGraph which reducer to use.

---

## 17. Custom Reducers

Reducers can implement domain-specific merge logic.

Example:

```python
def highest_score(old: float, new: float) -> float:
    return max(old, new)
```

State:

```python
class State(TypedDict):
    confidence: Annotated[float, highest_score]
```

If two branches produce:

```python
0.72
```

and:

```python
0.95
```

The merged value becomes:

```python
0.95
```

---

## 18. When Reducers Are Needed

Reducers are useful when:

- Parallel branches update the same key
- Multiple tools contribute to one collection
- Multiple agents produce findings
- Logs or events are accumulated
- Messages are appended
- Results must be aggregated

Reducers are not only a list-append feature. They express merge semantics.

---

## 19. Nested State

Related fields should often be grouped.

Instead of:

```python
class State(TypedDict):
    employee_first_name: str
    employee_last_name: str
    employee_department: str
```

Prefer:

```python
class Employee(TypedDict):
    employee_id: str
    first_name: str
    last_name: str
    department: str

class State(TypedDict):
    employee: Employee
```

This better reflects business objects.

---

## 20. Nested Dictionaries Are Not Deep-Merged Automatically

Suppose the state contains:

```python
{
    "employee": {
        "employee_id": "EMP-101",
        "first_name": "AJ"
    }
}
```

A node returns:

```python
{
    "employee": {
        "department": "Engineering"
    }
}
```

Do not assume the nested dictionary will be deep-merged.

The top-level `employee` value may be replaced.

Safer pattern:

```python
def assign_department(state: State):
    updated_employee = {
        **state["employee"],
        "department": "Engineering"
    }

    return {
        "employee": updated_employee
    }
```

---

## 21. Model the Business, Not the Nodes

Bad design:

```python
class State(TypedDict):
    node1_result: str
    node2_result: str
    node3_result: str
```

This couples state to graph implementation.

Better:

```python
class CashApplicationState(TypedDict):
    remittance: Remittance
    bank_payments: list[Payment]
    matches: list[Match]
```

The state should describe the business domain.

---

## 22. Separate State by Lifecycle

A useful enterprise pattern:

```python
class WorkflowState(TypedDict):

    # Inputs

    # Retrieved Data

    # Derived Data

    # Decisions

    # Human Actions

    # Final Outputs

    # Metadata
```

This makes the workflow lifecycle visible from the state schema.

---

## 23. Store References Instead of Large Payloads

Avoid storing large binary files or huge documents directly in state.

Prefer:

```python
attachment_id: str
document_uri: str
storage_reference: str
```

Benefits:

- Smaller checkpoints
- Lower serialization overhead
- Easier persistence
- Cleaner observability

---

## 24. Do Not Store Secrets in State

Avoid storing:

- API keys
- Passwords
- JWTs
- Client secrets
- Access tokens

State may be:

- Persisted
- Logged
- Inspected
- Checkpointed

Credentials belong in a secret manager or runtime configuration.

---

## 25. Separate Business Data from Operational Metadata

Example:

```python
class WorkflowMetadata(TypedDict):
    execution_id: str
    started_at: str
    current_step: str
    retry_count: int
```

Then:

```python
class CashApplicationState(TypedDict):
    metadata: WorkflowMetadata
    email: Email
    remittance: NotRequired[Remittance]
    matches: NotRequired[list[Match]]
```

Operational metadata should not pollute domain objects.

---

## 26. Enterprise State Examples

### Customer Support

```python
class CustomerSupportState(TypedDict):
    user_message: str
    customer: NotRequired[Customer]
    intent: NotRequired[str]
    kb_articles: NotRequired[list[KnowledgeArticle]]
    response: NotRequired[str]
    escalation_required: NotRequired[bool]
    resolution_status: NotRequired[str]
```

### Cash Application

```python
class CashApplicationState(TypedDict):
    email: Email
    remittance: NotRequired[Remittance]
    bank_payments: NotRequired[list[Payment]]
    open_receivables: NotRequired[list[Invoice]]
    matches: NotRequired[list[Match]]
    confidence_score: NotRequired[float]
    approval_status: NotRequired[str]
    posting_result: NotRequired[PostingResult]
```

### Invoice Approval

```python
class InvoiceApprovalState(TypedDict):
    invoice: Invoice
    extracted_fields: NotRequired[InvoiceData]
    vendor: NotRequired[Vendor]
    validation_result: NotRequired[ValidationResult]
    approval: NotRequired[ApprovalDecision]
    posting_result: NotRequired[PostingResult]
```

### IT Incident Management

```python
class IncidentState(TypedDict):
    incident: Incident
    category: NotRequired[str]
    assigned_team: NotRequired[Team]
    troubleshooting_steps: NotRequired[list[str]]
    resolution: NotRequired[Resolution]
```

### Procurement

```python
class ProcurementState(TypedDict):
    purchase_request: PurchaseRequest
    budget: NotRequired[Budget]
    vendors: NotRequired[list[Vendor]]
    selected_vendor: NotRequired[Vendor]
    approval: NotRequired[ApprovalDecision]
    purchase_order: NotRequired[PurchaseOrder]
```

### Order-to-Cash

```python
class OrderState(TypedDict):
    sales_order: SalesOrder
    credit_result: NotRequired[CreditResult]
    inventory_result: NotRequired[InventoryResult]
    pricing: NotRequired[PricingResult]
    invoice: NotRequired[Invoice]
    shipment: NotRequired[Shipment]
```

---

## 27. Universal Enterprise Pattern

Most workflow states follow this lifecycle:

```text
Input
   ↓
Retrieved Data
   ↓
Derived Data
   ↓
Decision Data
   ↓
Human Action
   ↓
Final Output
```

This structure is reusable across domains.

---

## 28. State Architecture Principle

```text
State models the business.

Nodes implement the business logic.

Edges model the business process.
```

This is the central design principle of LangGraph state modeling.

---

## 29. Common Mistakes

### Mistake 1 — Using generic field names

Avoid:

```python
result
data
response
temp
```

Prefer domain-specific names.

### Mistake 2 — Duplicating data

Do not store the same business value in multiple places.

### Mistake 3 — Mixing operational and domain fields

Separate metadata from business objects.

### Mistake 4 — Storing large payloads

Store references where practical.

### Mistake 5 — Storing secrets

Never place credentials in workflow state.

### Mistake 6 — Assuming deep merge

Nested dictionaries require explicit update handling.

### Mistake 7 — Designing state around node names

State should survive node refactoring.

---

## 30. Key Takeaways

- State is the single source of truth.
- `TypedDict` defines the static contract.
- Nodes return partial updates.
- LangGraph merges updates.
- Sequential updates overwrite prior values.
- Parallel writes to the same key require reducers.
- Nested dictionaries are not automatically deep-merged.
- Enterprise state should model business objects.
- Operational metadata should be separated.
- Secrets should never be stored in state.
