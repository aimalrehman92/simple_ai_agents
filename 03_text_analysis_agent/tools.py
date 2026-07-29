"""Tools used by the text analysis agent."""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from typing import Any


WORD_PATTERN = re.compile(r"\b[\w'-]+\b", re.UNICODE)
SENTENCE_PATTERN = re.compile(r"[.!?]+")
DEFAULT_READING_SPEED = 200

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "he",
    "her",
    "his",
    "i",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "she",
    "that",
    "the",
    "their",
    "they",
    "this",
    "to",
    "was",
    "were",
    "will",
    "with",
    "you",
    "your",
}


def _parse_json(tool_input: str) -> dict[str, Any]:
    try:
        data = json.loads(tool_input)
    except json.JSONDecodeError as error:
        raise ValueError("Tool input must be valid JSON.") from error

    if not isinstance(data, dict):
        raise ValueError("Tool input must be a JSON object.")

    return data


def _get_text(data: dict[str, Any]) -> str:
    text = str(data.get("text", "")).strip()

    if not text:
        raise ValueError("A non-empty 'text' value is required.")

    return text


def _extract_words(text: str) -> list[str]:
    return WORD_PATTERN.findall(text)


def count_text(tool_input: str) -> str:
    """
    Count words, sentences, and characters.

    Expected input:
    {"text": "Your text here"}
    """

    data = _parse_json(tool_input)
    text = _get_text(data)

    words = _extract_words(text)
    sentence_count = len([item for item in SENTENCE_PATTERN.split(text) if item.strip()])
    character_count = len(text)
    character_count_no_spaces = len(re.sub(r"\s+", "", text))

    return "\n".join(
        [
            f"Words: {len(words)}",
            f"Sentences: {sentence_count}",
            f"Characters: {character_count}",
            f"Characters excluding spaces: {character_count_no_spaces}",
        ]
    )


def calculate_reading_time(tool_input: str) -> str:
    """
    Estimate reading time.

    Expected input:
    {"text": "Your text here"}
    or
    {"text": "Your text here", "words_per_minute": 220}
    """

    data = _parse_json(tool_input)
    text = _get_text(data)

    try:
        words_per_minute = int(data.get("words_per_minute", DEFAULT_READING_SPEED))
    except (TypeError, ValueError) as error:
        raise ValueError("words_per_minute must be an integer.") from error

    if words_per_minute <= 0:
        raise ValueError("words_per_minute must be greater than zero.")

    word_count = len(_extract_words(text))
    minutes = word_count / words_per_minute
    rounded_minutes = max(1, math.ceil(minutes))

    return (
        f"Estimated reading time: {rounded_minutes} minute(s) "
        f"for {word_count} words at {words_per_minute} words per minute."
    )


def extract_keywords(tool_input: str) -> str:
    """
    Extract frequent keywords.

    Expected input:
    {"text": "Your text here"}
    or
    {"text": "Your text here", "limit": 8}
    """

    data = _parse_json(tool_input)
    text = _get_text(data)

    try:
        limit = int(data.get("limit", 8))
    except (TypeError, ValueError) as error:
        raise ValueError("limit must be an integer.") from error

    if limit < 1 or limit > 20:
        raise ValueError("limit must be between 1 and 20.")

    words = [
        word.lower()
        for word in _extract_words(text)
        if len(word) > 2 and word.lower() not in STOPWORDS
    ]

    if not words:
        return "No meaningful keywords were found."

    counts = Counter(words)
    most_common = counts.most_common(limit)

    return "\n".join(
        f"{index}. {word} ({count})"
        for index, (word, count) in enumerate(most_common, start=1)
    )


def analyze_style(tool_input: str) -> str:
    """
    Calculate basic writing-style statistics.

    Expected input:
    {"text": "Your text here"}
    """

    data = _parse_json(tool_input)
    text = _get_text(data)

    words = _extract_words(text)
    sentences = [item.strip() for item in SENTENCE_PATTERN.split(text) if item.strip()]

    if not words:
        raise ValueError("The text does not contain any words.")

    average_word_length = sum(len(word) for word in words) / len(words)
    average_sentence_length = (
        len(words) / len(sentences) if sentences else float(len(words))
    )

    unique_word_ratio = len({word.lower() for word in words}) / len(words)

    return "\n".join(
        [
            f"Average word length: {average_word_length:.2f} characters",
            f"Average sentence length: {average_sentence_length:.2f} words",
            f"Unique-word ratio: {unique_word_ratio:.2%}",
        ]
    )