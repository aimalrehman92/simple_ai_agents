from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from shared import Agent

from prompt import SYSTEM_PROMPT
from tools import (
    add_expense,
    calculate_total,
    check_budget,
    clear_expenses,
    list_expenses,
)


KNOWN_ACTIONS = {
    "add_expense": add_expense,
    "calculate_total": calculate_total,
    "check_budget": check_budget,
    "list_expenses": list_expenses,
    "clear_expenses": clear_expenses,
}


def main() -> None:
    agent = Agent(
        system_prompt=SYSTEM_PROMPT,
        known_actions=KNOWN_ACTIONS,
        max_turns=8,
    )

    print("Expense Agent")
    print("Type 'exit' to stop.\n")

    while True:
        question = input("You: ").strip()

        if not question:
            continue

        if question.lower() in {"exit", "quit"}:
            break

        answer = agent.run(question)

        print("\nAgent:")
        print(answer)
        print()


if __name__ == "__main__":
    main()