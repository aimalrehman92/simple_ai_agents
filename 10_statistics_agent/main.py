from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from shared import Agent

from prompt import SYSTEM_PROMPT
from tools import (
    calculate_confusion_matrix_metrics,
    calculate_correlation,
    calculate_descriptive_statistics,
    calculate_z_score,
)


KNOWN_ACTIONS = {
    "calculate_descriptive_statistics": calculate_descriptive_statistics,
    "calculate_z_score": calculate_z_score,
    "calculate_confusion_matrix_metrics": calculate_confusion_matrix_metrics,
    "calculate_correlation": calculate_correlation,
}


def main() -> None:
    agent = Agent(
        system_prompt=SYSTEM_PROMPT,
        known_actions=KNOWN_ACTIONS,
        max_turns=6,
    )

    print("Statistics Agent")
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