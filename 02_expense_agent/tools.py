"""Tools used by the expense agent."""

from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from typing import Any


_EXPENSES: list[dict[str, Any]] = []


def _parse_json(value: str) -> dict[str, Any]:
    try:
        data = json.loads(value)
    except json.JSONDecodeError as error:
        raise ValueError("Tool input must be valid JSON.") from error

    if not isinstance(data, dict):
        raise ValueError("Tool input must be a JSON object.")

    return data


def _parse_amount(value: Any) -> Decimal:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError("Amount must be a valid number.") from error

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    return amount.quantize(Decimal("0.01"))


def add_expense(tool_input: str) -> str:
    """
    Add an expense to the current session.

    Expected input:
    {"description": "Coffee", "amount": 4.50, "category": "food"}
    """

    data = _parse_json(tool_input)

    description = str(data.get("description", "")).strip()
    category = str(data.get("category", "uncategorized")).strip().lower()
    amount = _parse_amount(data.get("amount"))

    if not description:
        raise ValueError("Expense description is required.")

    if not category:
        category = "uncategorized"

    expense = {
        "description": description,
        "amount": amount,
        "category": category,
    }

    _EXPENSES.append(expense)

    return (
        f"Added expense: {description}, "
        f"${amount:.2f}, category: {category}. "
        f"Current expense count: {len(_EXPENSES)}."
    )


def calculate_total(tool_input: str) -> str:
    """
    Calculate the total spending.

    Input may be:
    {}
    {"category": "food"}
    """

    data = _parse_json(tool_input) if tool_input.strip() else {}
    category = str(data.get("category", "")).strip().lower()

    matching_expenses = [
        expense
        for expense in _EXPENSES
        if not category or expense["category"] == category
    ]

    total = sum(
        (expense["amount"] for expense in matching_expenses),
        start=Decimal("0.00"),
    )

    if category:
        return (
            f"Total spending in category '{category}': "
            f"${total:.2f} across {len(matching_expenses)} expense(s)."
        )

    return (
        f"Total spending: ${total:.2f} "
        f"across {len(matching_expenses)} expense(s)."
    )


def check_budget(tool_input: str) -> str:
    """
    Compare current spending with a budget.

    Expected input:
    {"budget": 100}
    {"budget": 100, "category": "food"}
    """

    data = _parse_json(tool_input)

    budget = _parse_amount(data.get("budget"))
    category = str(data.get("category", "")).strip().lower()

    matching_expenses = [
        expense
        for expense in _EXPENSES
        if not category or expense["category"] == category
    ]

    total = sum(
        (expense["amount"] for expense in matching_expenses),
        start=Decimal("0.00"),
    )

    difference = budget - total
    scope = f" for category '{category}'" if category else ""

    if difference >= 0:
        return (
            f"Spending{scope} is within budget. "
            f"Spent: ${total:.2f}. Budget: ${budget:.2f}. "
            f"Remaining: ${difference:.2f}."
        )

    return (
        f"Spending{scope} is over budget. "
        f"Spent: ${total:.2f}. Budget: ${budget:.2f}. "
        f"Exceeded by: ${abs(difference):.2f}."
    )


def list_expenses(tool_input: str) -> str:
    """
    List expenses recorded in the current session.

    Input may be:
    {}
    {"category": "food"}
    """

    data = _parse_json(tool_input) if tool_input.strip() else {}
    category = str(data.get("category", "")).strip().lower()

    matching_expenses = [
        expense
        for expense in _EXPENSES
        if not category or expense["category"] == category
    ]

    if not matching_expenses:
        return "No matching expenses have been recorded."

    lines = []

    for index, expense in enumerate(matching_expenses, start=1):
        lines.append(
            f"{index}. {expense['description']} — "
            f"${expense['amount']:.2f} "
            f"({expense['category']})"
        )

    return "\n".join(lines)


def clear_expenses(tool_input: str) -> str:
    """Clear all expenses stored in the current session."""

    del tool_input

    count = len(_EXPENSES)
    _EXPENSES.clear()

    return f"Cleared {count} expense(s) from the current session."