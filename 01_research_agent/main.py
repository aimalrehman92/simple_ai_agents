from __future__ import annotations

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