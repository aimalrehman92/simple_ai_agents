from __future__ import annotations

import unittest
from unittest.mock import patch

from shared.agent import Agent


class FakeChatBot:
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.prompts: list[str] = []
        self.reset_count = 0

    def __call__(self, prompt: str) -> str:
        self.prompts.append(prompt)

        if not self.responses:
            raise RuntimeError("No fake responses remain.")

        return self.responses.pop(0)

    def reset(self) -> None:
        self.reset_count += 1


class AgentLoopTests(unittest.TestCase):
    def test_returns_direct_answer(self) -> None:
        fake_bot = FakeChatBot(
            [
                "Answer: Jakarta is the capital of Indonesia.",
            ]
        )

        with patch("shared.agent.ChatBot", return_value=fake_bot):
            agent = Agent(
                system_prompt="Test prompt",
                known_actions={"uppercase": str.upper},
                max_turns=3,
                verbose=False,
            )

        result = agent.run("What is the capital of Indonesia?")

        self.assertEqual(
            result,
            "Answer: Jakarta is the capital of Indonesia.",
        )
        self.assertEqual(
            fake_bot.prompts,
            ["What is the capital of Indonesia?"],
        )
        self.assertEqual(fake_bot.reset_count, 1)

    def test_executes_tool_and_returns_final_answer(self) -> None:
        fake_bot = FakeChatBot(
            [
                (
                    "Thought: I should transform the text.\n"
                    "Action: uppercase: hello world\n"
                    "PAUSE"
                ),
                "Answer: HELLO WORLD",
            ]
        )

        calls: list[str] = []

        def uppercase(value: str) -> str:
            calls.append(value)
            return value.upper()

        with patch("shared.agent.ChatBot", return_value=fake_bot):
            agent = Agent(
                system_prompt="Test prompt",
                known_actions={"uppercase": uppercase},
                max_turns=3,
                verbose=False,
            )

        result = agent.run("Convert this text to uppercase.")

        self.assertEqual(result, "Answer: HELLO WORLD")
        self.assertEqual(calls, ["hello world"])
        self.assertEqual(
            fake_bot.prompts,
            [
                "Convert this text to uppercase.",
                "Observation: HELLO WORLD",
            ],
        )

    def test_rejects_unknown_action(self) -> None:
        fake_bot = FakeChatBot(
            [
                (
                    "Thought: I need another tool.\n"
                    "Action: missing_tool: test\n"
                    "PAUSE"
                ),
            ]
        )

        with patch("shared.agent.ChatBot", return_value=fake_bot):
            agent = Agent(
                system_prompt="Test prompt",
                known_actions={"uppercase": str.upper},
                max_turns=3,
                verbose=False,
            )

        with self.assertRaisesRegex(
            ValueError,
            "Unknown action 'missing_tool'",
        ):
            agent.run("Use a missing tool.")

    def test_tool_error_becomes_observation(self) -> None:
        fake_bot = FakeChatBot(
            [
                (
                    "Thought: I should run the tool.\n"
                    "Action: failing_tool: input\n"
                    "PAUSE"
                ),
                "Answer: The tool failed.",
            ]
        )

        def failing_tool(_: str) -> str:
            raise RuntimeError("Something went wrong.")

        with patch("shared.agent.ChatBot", return_value=fake_bot):
            agent = Agent(
                system_prompt="Test prompt",
                known_actions={"failing_tool": failing_tool},
                max_turns=3,
                verbose=False,
            )

        result = agent.run("Run the failing tool.")

        self.assertEqual(result, "Answer: The tool failed.")
        self.assertEqual(
            fake_bot.prompts[1],
            (
                "Observation: Tool 'failing_tool' failed with "
                "RuntimeError: Something went wrong."
            ),
        )

    def test_stops_after_maximum_turns(self) -> None:
        fake_bot = FakeChatBot(
            [
                "Action: uppercase: first",
                "Action: uppercase: second",
            ]
        )

        with patch("shared.agent.ChatBot", return_value=fake_bot):
            agent = Agent(
                system_prompt="Test prompt",
                known_actions={"uppercase": str.upper},
                max_turns=2,
                verbose=False,
            )

        with self.assertRaisesRegex(
            RuntimeError,
            "did not produce a final answer within 2 turns",
        ):
            agent.run("Keep using tools.")


if __name__ == "__main__":
    unittest.main()