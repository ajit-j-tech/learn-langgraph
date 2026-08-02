"""
Workflow Statement Management Template
---------------------------------------

1. Input
2. Retreived Information
3. Derived Information
4. Decision Data
    - Automation
    - Human In The Loop (HITL)
5. Result
"""

from datetime import date
from decimal import Decimal
from typing import Literal, NotRequired, TypedDict


class Payment(TypedDict):
    payment_id: str
    payment_date: date
    account_number: str
    amount: Decimal


class Invoice(TypedDict):
    invoice_id: str
    invoice_number: str
    amount: Decimal
    customer_number: str


class Remittance(TypedDict):
    customer_number: NotRequired[str]
    amount: Decimal
    invoice_numbers: list[str]


class PaymentMatch(TypedDict):
    payment_id: str
    invoice_ids: list[str]
    matched_amount: Decimal
    confidence: float


class CashAppState(TypedDict):

    # Input
    email: str

    # Derived from input
    remittance: NotRequired[Remittance]

    # Retrieved information
    bank_payments: NotRequired[list[Payment]]
    invoices: NotRequired[list[Invoice]]

    # Derived information
    matches: NotRequired[list[PaymentMatch]]

    # Decision data
    application_decision: NotRequired[
        Literal["auto_apply", "human_review", "no_match"]
    ]

    # Result
    matching_status: NotRequired[
        Literal["pending", "matched", "partially_matched", "unmatched", "applied"]
    ]