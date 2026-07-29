"""OpenAI chatbot wrapper used by the example agents."""

from __future__ import annotations

import os
from typing import Final

from openai import OpenAI


DEFAULT_MODEL: Final[str] = "gpt-5.4-nano"


class ChatBot:
    """A small stateful wrapper around the OpenAI Responses API."""

    def __init__(
        self,
        system_prompt: str = "",
        model: str = DEFAULT_MODEL,
        api_key: str | None = None,
    ) -> None:
        """
        Initialize the chatbot.

        Args:
            system_prompt: Instructions that define the chatbot's behavior.
            model: OpenAI model used to generate responses.
            api_key: Optional API key. When omitted, OPENAI_API_KEY is used.
        """
        resolved_api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not resolved_api_key:
            raise ValueError(
                "OpenAI API key not found. Set the OPENAI_API_KEY "
                "environment variable before running an agent."
            )

        self.client = OpenAI(api_key=resolved_api_key)
        self.system_prompt = system_prompt.strip()
        self.model = model
        self.previous_response_id: str | None = None

    def __call__(self, prompt: str) -> str:
        """
        Send a prompt to the model and return its text response.

        The previous response ID is retained so the model can follow the
        ongoing agent conversation without resending the full history.
        """
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt must be a non-empty string.")

        request = {
            "model": self.model,
            "input": prompt.strip(),
            "store": True,
        }

        if self.system_prompt:
            request["instructions"] = self.system_prompt

        if self.previous_response_id:
            request["previous_response_id"] = self.previous_response_id

        response = self.client.responses.create(**request)

        output_text = response.output_text.strip()

        if not output_text:
            raise RuntimeError("The model returned an empty response.")

        self.previous_response_id = response.id

        return output_text

    def reset(self) -> None:
        """Clear the stored conversation state."""
        self.previous_response_id = None