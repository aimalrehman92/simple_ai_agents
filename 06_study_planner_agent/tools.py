"""Tools used by the study planner agent."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from typing import Any


def _parse_json(tool_input: str) -> dict[str, Any]:
    try:
        data = json.loads(tool_input)
    except json.JSONDecodeError as error:
        raise ValueError("Tool input must be valid JSON.") from error

    if not isinstance(data, dict):
        raise ValueError("Tool input must be a JSON object.")

    return data


def estimate_topic_hours(tool_input: str) -> str:
    """
    Estimate study time for a list of topics.

    Expected input:
    {
        "topics": [
            {"name": "Arrays", "difficulty": "easy"},
            {"name": "Dynamic Programming", "difficulty": "hard"}
        ]
    }
    """

    data = _parse_json(tool_input)
    topics = data.get("topics")

    if not isinstance(topics, list) or not topics:
        raise ValueError("'topics' must be a non-empty list.")

    difficulty_hours = {
        "easy": 2.0,
        "medium": 4.0,
        "hard": 7.0,
    }

    lines: list[str] = []
    total_hours = 0.0

    for index, topic in enumerate(topics, start=1):
        if not isinstance(topic, dict):
            raise ValueError("Each topic must be a JSON object.")

        name = str(topic.get("name", "")).strip()
        difficulty = str(topic.get("difficulty", "medium")).strip().lower()

        if not name:
            raise ValueError("Each topic requires a name.")

        if difficulty not in difficulty_hours:
            raise ValueError(
                "Difficulty must be one of: easy, medium, hard."
            )

        estimated_hours = difficulty_hours[difficulty]
        total_hours += estimated_hours

        lines.append(
            f"{index}. {name}: {estimated_hours:.1f} hour(s) "
            f"({difficulty})"
        )

    lines.append(f"Total estimated study time: {total_hours:.1f} hours.")

    return "\n".join(lines)


def prioritize_topics(tool_input: str) -> str:
    """
    Rank topics by importance and difficulty.

    Expected input:
    {
        "topics": [
            {
                "name": "Arrays",
                "importance": 5,
                "difficulty": 2
            }
        ]
    }
    """

    data = _parse_json(tool_input)
    topics = data.get("topics")

    if not isinstance(topics, list) or not topics:
        raise ValueError("'topics' must be a non-empty list.")

    ranked_topics: list[tuple[float, str, int, int]] = []

    for topic in topics:
        if not isinstance(topic, dict):
            raise ValueError("Each topic must be a JSON object.")

        name = str(topic.get("name", "")).strip()

        if not name:
            raise ValueError("Each topic requires a name.")

        try:
            importance = int(topic.get("importance"))
            difficulty = int(topic.get("difficulty"))
        except (TypeError, ValueError) as error:
            raise ValueError(
                "Importance and difficulty must be integers."
            ) from error

        if not 1 <= importance <= 5:
            raise ValueError("Importance must be between 1 and 5.")

        if not 1 <= difficulty <= 5:
            raise ValueError("Difficulty must be between 1 and 5.")

        score = (importance * 2) + difficulty

        ranked_topics.append(
            (score, name, importance, difficulty)
        )

    ranked_topics.sort(
        key=lambda item: (-item[0], -item[2], -item[3], item[1].lower())
    )

    lines = []

    for index, (score, name, importance, difficulty) in enumerate(
        ranked_topics,
        start=1,
    ):
        lines.append(
            f"{index}. {name} — priority score: {score:.1f}, "
            f"importance: {importance}, difficulty: {difficulty}"
        )

    return "\n".join(lines)


def create_study_schedule(tool_input: str) -> str:
    """
    Create a day-by-day study schedule.

    Expected input:
    {
        "topics": [
            {"name": "Arrays", "hours": 2},
            {"name": "Graphs", "hours": 5}
        ],
        "start_date": "2026-08-01",
        "daily_hours": 2
    }
    """

    data = _parse_json(tool_input)
    topics = data.get("topics")
    start_date_value = str(data.get("start_date", "")).strip()

    if not isinstance(topics, list) or not topics:
        raise ValueError("'topics' must be a non-empty list.")

    if not start_date_value:
        raise ValueError("'start_date' is required.")

    try:
        start_date = datetime.strptime(
            start_date_value,
            "%Y-%m-%d",
        ).date()
    except ValueError as error:
        raise ValueError(
            "start_date must use YYYY-MM-DD format."
        ) from error

    try:
        daily_hours = float(data.get("daily_hours"))
    except (TypeError, ValueError) as error:
        raise ValueError("daily_hours must be a number.") from error

    if daily_hours <= 0 or daily_hours > 12:
        raise ValueError("daily_hours must be greater than 0 and at most 12.")

    remaining_topics: list[dict[str, Any]] = []

    for topic in topics:
        if not isinstance(topic, dict):
            raise ValueError("Each topic must be a JSON object.")

        name = str(topic.get("name", "")).strip()

        if not name:
            raise ValueError("Each topic requires a name.")

        try:
            hours = float(topic.get("hours"))
        except (TypeError, ValueError) as error:
            raise ValueError(
                "Each topic's hours value must be numeric."
            ) from error

        if hours <= 0:
            raise ValueError("Topic hours must be greater than zero.")

        remaining_topics.append(
            {
                "name": name,
                "remaining_hours": hours,
            }
        )

    current_date = start_date
    topic_index = 0
    schedule_lines: list[str] = []
    day_number = 1

    while topic_index < len(remaining_topics):
        available_hours = daily_hours
        day_tasks: list[str] = []

        while available_hours > 0 and topic_index < len(remaining_topics):
            topic = remaining_topics[topic_index]
            study_hours = min(
                available_hours,
                topic["remaining_hours"],
            )

            day_tasks.append(
                f"{topic['name']} ({study_hours:.1f} hour(s))"
            )

            topic["remaining_hours"] -= study_hours
            available_hours -= study_hours

            if topic["remaining_hours"] <= 0:
                topic_index += 1

        schedule_lines.append(
            f"Day {day_number} — {current_date.isoformat()}: "
            + "; ".join(day_tasks)
        )

        current_date += timedelta(days=1)
        day_number += 1

    total_days = day_number - 1
    completion_date = current_date - timedelta(days=1)

    schedule_lines.append(
        f"Plan length: {total_days} day(s). "
        f"Expected completion date: {completion_date.isoformat()}."
    )

    return "\n".join(schedule_lines)


def calculate_days_until_deadline(tool_input: str) -> str:
    """
    Calculate the number of days until a deadline.

    Expected input:
    {"deadline": "2026-09-01"}

    Optional:
    {"deadline": "2026-09-01", "current_date": "2026-08-01"}
    """

    data = _parse_json(tool_input)

    deadline_value = str(data.get("deadline", "")).strip()
    current_date_value = str(data.get("current_date", "")).strip()

    if not deadline_value:
        raise ValueError("'deadline' is required.")

    try:
        deadline = datetime.strptime(
            deadline_value,
            "%Y-%m-%d",
        ).date()
    except ValueError as error:
        raise ValueError(
            "deadline must use YYYY-MM-DD format."
        ) from error

    if current_date_value:
        try:
            current_date = datetime.strptime(
                current_date_value,
                "%Y-%m-%d",
            ).date()
        except ValueError as error:
            raise ValueError(
                "current_date must use YYYY-MM-DD format."
            ) from error
    else:
        current_date = date.today()

    days_remaining = (deadline - current_date).days

    if days_remaining < 0:
        return (
            f"The deadline passed {abs(days_remaining)} day(s) ago."
        )

    if days_remaining == 0:
        return "The deadline is today."

    return f"{days_remaining} day(s) remain until the deadline."