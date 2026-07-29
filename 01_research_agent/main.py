from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from shared import Agent

from prompt import SYSTEM_PROMPT
from tools import calculate_paper_age, get_paper_details, search_arxiv


KNOWN_ACTIONS = {
    "search_arxiv": search_arxiv,
    "get_paper_details": get_paper_details,
    "calculate_paper_age": calculate_paper_age,
}


def main() -> None:
    agent = Agent(
        system_prompt=SYSTEM_PROMPT,
        known_actions=KNOWN_ACTIONS,
        max_turns=5,
    )

    question = input("Research question: ").strip()

    if not question:
        raise ValueError("A research question is required.")

    answer = agent.run(question)

    print("\nFinal response")
    print(answer)


if __name__ == "__main__":
    main()