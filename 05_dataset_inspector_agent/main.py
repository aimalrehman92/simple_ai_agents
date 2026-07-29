from __future__ import annotations

from shared import Agent

from prompt import SYSTEM_PROMPT
from tools import (
    calculate_missing_values,
    get_column_names,
    get_dataset_shape,
    get_loaded_dataset,
    load_csv,
    preview_rows,
    summarize_column,
)


KNOWN_ACTIONS = {
    "load_csv": load_csv,
    "get_dataset_shape": get_dataset_shape,
    "get_column_names": get_column_names,
    "calculate_missing_values": calculate_missing_values,
    "summarize_column": summarize_column,
    "preview_rows": preview_rows,
    "get_loaded_dataset": get_loaded_dataset,
}


def main() -> None:
    agent = Agent(
        system_prompt=SYSTEM_PROMPT,
        known_actions=KNOWN_ACTIONS,
        max_turns=8,
    )

    print("Dataset Inspector Agent")
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