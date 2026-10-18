"""Pure, testable financial validation rules for Harvest records."""

from __future__ import annotations

import math


def nonnegative_amount(value: object, field_name: str = "Amount") -> float:
    try:
        amount = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a valid number.") from exc
    if not math.isfinite(amount):
        raise ValueError(f"{field_name} must be a finite number.")
    if amount < 0:
        raise ValueError(f"{field_name} cannot be negative.")
    return amount


def positive_amount(value: object, field_name: str = "Amount") -> float:
    amount = nonnegative_amount(value, field_name)
    if amount <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")
    return amount


def redeemed_total(pledged: object, already_paid: object, additional: object, payment_mode: str) -> float:
    """Return a valid new paid total, rejecting non-pledges and overpayment."""
    if payment_mode != "Pledge":
        raise ValueError("Only pledge records can receive pledge-redemption payments.")
    total = nonnegative_amount(pledged, "Pledged amount")
    paid = nonnegative_amount(already_paid, "Amount already paid")
    payment = positive_amount(additional, "Payment")
    new_paid = paid + payment
    if new_paid > total:
        raise ValueError("Payment exceeds the outstanding pledge balance.")
    return new_paid
