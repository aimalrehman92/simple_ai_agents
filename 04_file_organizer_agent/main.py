from __future__ import annotations

from shared import Agent

from prompt import SYSTEM_PROMPT
from tools import (
    classify_files,
    list_files,
    organize_files,
    preview_organization,
)


KNOWN_ACTIONS = {
    "list_files": list_files,
    "classify_files": classify_files,
    "preview_organization": preview_organization,
    "organize_files": organize_files,
}


def main() -> None:
    agent = Agent(
        system_prompt=SYSTEM_PROMPT,
        known_actions=KNOWN_ACTIONS,
        max_turns=6,
    )

    print("File Organizer Agent")
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