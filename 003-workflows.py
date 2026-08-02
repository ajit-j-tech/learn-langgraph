from decimal import Decimal
from typing import NotRequired, TypedDict, Literal


class Payment(TypedDict):
    payment_id: str
    payment_reference: str
    payment_date: str
    customer_number: NotRequired[str]
    amount: Decimal


class Invoice(TypedDict):
    invoice_id: str
    invoice_number: str
    customer_number: str
    open_amount: Decimal


class Remittance(TypedDict):
    payment_reference: NotRequired[str]
    customer_number: NotRequired[str]
    remittance_amount: Decimal
    invoice_numbers: list[str]


class PaymentMatch(TypedDict):
    payment_id: str
    invoice_ids: list[str]
    matched_amount: Decimal
    confidence: float


class CashApplicationState(TypedDict):

    # Input
    email: str

    # Derived from input
    remittance: NotRequired[Remittance]

    # Retrieved data
    bank_payments: NotRequired[list[Payment]]
    open_invoices: NotRequired[list[Invoice]]

    # Derived data
    matches: NotRequired[list[PaymentMatch]]

    # Decision
    decision = NotRequired[Literal["auto_apply", "not_match", "human_review"]]

    # Result
    matching_status = NotRequired[str]

"""
Remittance Workflow Nodes
"""
def read_remittance(
    state: CashApplicationState,
) -> dict:

    print("Reading remittance...")
    print("****************** EMAIL ******************")
    print(state)
    print("****************** EMAIL ******************")
    print()

    return {
        "remittance": {
            "payment_reference": "PAY-REF-1001",
            "customer_number": "CUST-001",
            "remittance_amount": Decimal("5000.00"),
            "invoice_numbers": ["INV-1001"]
        }
    }

def fetch_bank_payments(
    state: CashApplicationState,
) -> dict:

    print("Fetching bank payments...")
    print("****************** PAYMENTS ******************")
    print(state)
    print("****************** PAYMENTS ******************")
    print()

    payments = [
        {
            "payment_id": "PAY-001",
            "payment_reference": "PAY-REF-1001",
            "payment_date": "2026-08-01",
            "customer_number": "CUST-001",
            "amount": Decimal("5000.00"),
        }
    ]

    return {
        "bank_payments": payments
    }

def fetch_open_invoices(
    state: CashApplicationState,
) -> dict:

    print("Fetching open invoices...")
    print("****************** INVOICES ******************")
    print(state)
    print("****************** INVOICES ******************")
    print()

    remittance = state["remittance"]

    invoices = [
        {
            "invoice_id": "INV-ID-001",
            "invoice_number": "INV-1001",
            "customer_number": "CUST-001",
            "open_amount": Decimal("5000.00"),
        },
        {
            "invoice_id": "INV-ID-002",
            "invoice_number": "INV-1002",
            "customer_number": "CUST-001",
            "open_amount": Decimal("2500.00"),
        },
    ]

    requested_invoice_numbers = remittance["invoice_numbers"]

    matching_invoices = [
        invoice
        for invoice in invoices
        if invoice["invoice_number"] in requested_invoice_numbers
    ]

    return {
        "open_invoices": matching_invoices
    }

def match_transactions(
    state: CashApplicationState,
) -> dict:

    print("Matching transactions...")
    print("****************** MATCHES ******************")
    print(state)
    print("****************** MATCHES ******************")
    print()

    remittance = state["remittance"]
    payments = state["bank_payments"]
    invoices = state["open_invoices"]

    matches: list[PaymentMatch] = []

    for payment in payments:

        matched_invoices = [
            invoice
            for invoice in invoices
            if invoice["customer_number"]
            == remittance.get("customer_number")
        ]

        invoice_total = sum(
            invoice["open_amount"]
            for invoice in matched_invoices
        )

        if (
            payment["amount"] == invoice_total
            and payment["amount"]
            == remittance["remittance_amount"]
        ):
            matches.append(
                {
                    "payment_id": payment["payment_id"],
                    "invoice_ids": [
                        invoice["invoice_id"]
                        for invoice in matched_invoices
                    ],
                    "matched_amount": payment["amount"],
                    "confidence": 1.0,
                }
            )

    return {
        "matches": matches
    }

def evaluate_matches(
    state: CashApplicationState,
) -> dict:

    matches = state.get("matches", [])

    if not matches:
        return {
            "application_decision": "no_match",
            "matching_status": "unmatched",
        }

    highest_confidence = max(
        match["confidence"]
        for match in matches
    )

    if highest_confidence >= 0.95:
        return {
            "application_decision": "auto_apply",
            "matching_status": "matched",
        }

    return {
        "application_decision": "human_review",
        "matching_status": "review_required",
    }

def route_application(
    state: CashApplicationState,
) -> Literal["auto_apply", "human_review", "no_match"]:

    return state["application_decision"]

def auto_apply(
    state: CashApplicationState,
) -> dict:

    print("Automatically applying cash")

    return {
        "matching_status": "applied"
    }


def human_review(
    state: CashApplicationState,
) -> dict:

    print("Sending for human review")

    return {
        "matching_status": "pending_review"
    }


def handle_no_match(
    state: CashApplicationState,
) -> dict:

    print("No matching transaction found")

    return {
        "matching_status": "unmatched"
    }

# Build the LangGraph Workflow
from langgraph.graph import END, START, StateGraph

builder = StateGraph(CashApplicationState)

builder.add_node("read_remittance", read_remittance)
builder.add_node("fetch_bank_payments", fetch_bank_payments)
builder.add_node("fetch_open_invoices", fetch_open_invoices)
builder.add_node("match_transactions", match_transactions)
builder.add_node("auto_apply", auto_apply)
builder.add_node("human_review", human_review)
builder.add_node("no_match", handle_no_match)
builder.add_node("evaluate_matches", evaluate_matches)

builder.add_edge(START, "read_remittance")

builder.add_edge("read_remittance", "fetch_bank_payments")
builder.add_edge("read_remittance", "fetch_open_invoices")

builder.add_edge("fetch_bank_payments", "match_transactions")
builder.add_edge("fetch_open_invoices", "match_transactions")

builder.add_edge(
    "match_transactions",
    "evaluate_matches",
)

builder.add_conditional_edges(
    "evaluate_matches",
    route_application,
    {
        "auto_apply": "auto_apply",
        "human_review": "human_review",
        "no_match": "no_match",
    },
)

builder.add_edge("auto_apply", END)
builder.add_edge("human_review", END)
builder.add_edge("no_match", END)

graph = builder.compile()

# FINAL SINGLE SHOT RESPONSE
result = graph.invoke({"email": "Payment reference PAY-REF-1001 for invoice INV-1001"})
print("-----------------------------------")
print(result)
print("-----------------------------------")

# STREAMED OUTPUT
# for update in graph.stream({"email": "Payment reference PAY-REF-1001 for invoice INV-1001"}, stream_mode="values"):
#     print(update)