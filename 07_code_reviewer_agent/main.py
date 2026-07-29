from __future__ import annotations

from shared import Agent

from prompt import SYSTEM_PROMPT
from tools import (
    check_syntax,
    find_large_functions,
    find_long_lines,
    find_missing_docstrings,
    review_python_file,
    summarize_structure,
)


KNOWN_ACTIONS = {
    "check_syntax": check_syntax,
    "summarize_structure": summarize_structure,
    "find_long_lines": find_long_lines,
    "find_large_functions": find_large_functions,
    "find_missing_docstrings": find_missing_docstrings,
    "review_python_file": review_python_file,
}


def main() -> None:
    agent = Agent(
        system_prompt=SYSTEM_PROMPT,
        known_actions=KNOWN_ACTIONS,
        max_turns=6,
    )

    print("Python Code Reviewer Agent")
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