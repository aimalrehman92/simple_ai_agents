from __future__ import annotations

from shared import Agent

from prompt import SYSTEM_PROMPT
from tools import (
    analyze_style,
    calculate_reading_time,
    count_text,
    extract_keywords,
)


KNOWN_ACTIONS = {
    "count_text": count_text,
    "calculate_reading_time": calculate_reading_time,
    "extract_keywords": extract_keywords,
    "analyze_style": analyze_style,
}


def main() -> None:
    agent = Agent(
        system_prompt=SYSTEM_PROMPT,
        known_actions=KNOWN_ACTIONS,
        max_turns=6,
    )

    print("Text Analysis Agent")
    print("Paste or type the text you want to analyze.")
    print("Press Enter twice when finished.\n")

    lines: list[str] = []

    while True:
        line = input()

        if not line:
            break

        lines.append(line)

    text = "\n".join(lines).strip()

    if not text:
        raise ValueError("Text is required.")

    question = (
        "Analyze the following text. Report its counts, estimated reading time, "
        "main keywords, and basic writing-style statistics.\n\n"
        f"{text}"
    )

    answer = agent.run(question)

    print("\nFinal response")
    print(answer)


if __name__ == "__main__":
    main()