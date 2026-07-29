from __future__ import annotations

from shared import Agent

from prompt import SYSTEM_PROMPT
from tools import (
    compare_products,
    filter_by_budget,
    find_cheapest_product,
    rank_products,
)


KNOWN_ACTIONS = {
    "compare_products": compare_products,
    "filter_by_budget": filter_by_budget,
    "find_cheapest_product": find_cheapest_product,
    "rank_products": rank_products,
}


def main() -> None:
    agent = Agent(
        system_prompt=SYSTEM_PROMPT,
        known_actions=KNOWN_ACTIONS,
        max_turns=6,
    )

    print("Product Comparison Agent")
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