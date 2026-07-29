"""Reusable execution loop for the example agents."""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping

from shared.chatbot import ChatBot


Tool = Callable[[str], str]

ACTION_PATTERN = re.compile(
    r"^Action:\s*([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.+)$",
    re.MULTILINE,
)


class Agent:
    """An LLM-driven agent that can select and run Python tools."""

    def __init__(
        self,
        system_prompt: str,
        known_actions: Mapping[str, Tool],
        max_turns: int = 5,
        model: str | None = None,
        verbose: bool = True,
    ) -> None:
        if not system_prompt.strip():
            raise ValueError("A non-empty system prompt is required.")

        if not known_actions:
            raise ValueError("At least one action must be provided.")

        if max_turns < 1:
            raise ValueError("max_turns must be at least 1.")

        self.max_turns = max_turns
        self.known_actions = dict(known_actions)
        self.verbose = verbose

        chatbot_options = {"system_prompt": system_prompt}

        if model is not None:
            chatbot_options["model"] = model

        self.bot = ChatBot(**chatbot_options)

    def run(self, question: str) -> str:
        """Run the agent until it produces a final answer."""

        if not isinstance(question, str) or not question.strip():
            raise ValueError("Question must be a non-empty string.")

        self.bot.reset()
        next_prompt = question.strip()

        for turn in range(1, self.max_turns + 1):
            result = self.bot(next_prompt)

            if self.verbose:
                print(f"\nTurn {turn}")
                print(result)

            action_match = ACTION_PATTERN.search(result)

            if action_match is None:
                return result

            action_name, action_input = action_match.groups()
            action_input = action_input.strip()

            if action_name not in self.known_actions:
                available = ", ".join(sorted(self.known_actions))

                raise ValueError(
                    f"Unknown action '{action_name}'. "
                    f"Available actions: {available}"
                )

            if self.verbose:
                print(f"\nRunning: {action_name}({action_input!r})")

            try:
                observation = self.known_actions[action_name](action_input)
            except Exception as error:
                observation = (
                    f"Tool '{action_name}' failed with "
                    f"{type(error).__name__}: {error}"
                )

            if observation is None:
                observation = "The tool completed without returning a result."
            elif not isinstance(observation, str):
                observation = str(observation)

            if self.verbose:
                print(f"Observation: {observation}")

            next_prompt = f"Observation: {observation}"

        raise RuntimeError(
            f"The agent did not produce a final answer within "
            f"{self.max_turns} turns."
        )