from __future__ import annotations

from shared import Agent

from prompt import SYSTEM_PROMPT
from tools import (
    get_note_stats,
    list_notes,
    open_note,
    search_notes,
)


KNOWN_ACTIONS = {
    "list_notes": list_notes,
    "search_notes": search_notes,
    "open_note": open_note,
    "get_note_stats": get_note_stats,
}


def main() -> None:
    agent = Agent(
        system_prompt=SYSTEM_PROMPT,
        known_actions=KNOWN_ACTIONS,
        max_turns=6,
    )

    print("Notes Agent")
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