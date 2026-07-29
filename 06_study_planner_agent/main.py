from __future__ import annotations

from shared import Agent

from prompt import SYSTEM_PROMPT
from tools import (
    calculate_days_until_deadline,
    create_study_schedule,
    estimate_topic_hours,
    prioritize_topics,
)


KNOWN_ACTIONS = {
    "estimate_topic_hours": estimate_topic_hours,
    "prioritize_topics": prioritize_topics,
    "create_study_schedule": create_study_schedule,
    "calculate_days_until_deadline": calculate_days_until_deadline,
}


def main() -> None:
    agent = Agent(
        system_prompt=SYSTEM_PROMPT,
        known_actions=KNOWN_ACTIONS,
        max_turns=8,
    )

    print("Study Planner Agent")
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