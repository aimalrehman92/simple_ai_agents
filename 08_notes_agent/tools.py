"""Tools used by the notes agent."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


SUPPORTED_EXTENSIONS = {".txt", ".md"}


def _parse_json(tool_input: str) -> dict[str, Any]:
    try:
        data = json.loads(tool_input)
    except json.JSONDecodeError as error:
        raise ValueError("Tool input must be valid JSON.") from error

    if not isinstance(data, dict):
        raise ValueError("Tool input must be a JSON object.")

    return data


def _resolve_directory(value: Any) -> Path:
    directory = Path(str(value or "")).expanduser().resolve()

    if not directory.exists():
        raise ValueError(f"Directory does not exist: {directory}")

    if not directory.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")

    return directory


def _resolve_note(directory: Path, filename: Any) -> Path:
    name = str(filename or "").strip()

    if not name:
        raise ValueError("A note filename is required.")

    note_path = (directory / name).resolve()

    try:
        note_path.relative_to(directory)
    except ValueError as error:
        raise ValueError("The note must be inside the selected directory.") from error

    if not note_path.exists():
        raise ValueError(f"Note does not exist: {note_path.name}")

    if not note_path.is_file():
        raise ValueError(f"Path is not a file: {note_path.name}")

    if note_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError("Only .txt and .md notes are supported.")

    return note_path


def _read_note(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("The note must use UTF-8 encoding.") from error
    except OSError as error:
        raise RuntimeError(f"Could not read note: {error}") from error


def list_notes(tool_input: str) -> str:
    """
    List supported notes in a directory.

    Expected input:
    {"directory": "/path/to/notes"}
    """

    data = _parse_json(tool_input)
    directory = _resolve_directory(data.get("directory"))

    notes = sorted(
        path
        for path in directory.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not notes:
        return f"No supported notes were found in {directory}."

    lines = []

    for index, note in enumerate(notes, start=1):
        relative_path = note.relative_to(directory)
        lines.append(f"{index}. {relative_path}")

    return "\n".join(lines)


def search_notes(tool_input: str) -> str:
    """
    Search note contents for a phrase.

    Expected input:
    {
        "directory": "/path/to/notes",
        "query": "conformal prediction"
    }

    Optional:
    {
        "directory": "/path/to/notes",
        "query": "conformal prediction",
        "max_results": 10
    }
    """

    data = _parse_json(tool_input)
    directory = _resolve_directory(data.get("directory"))
    query = str(data.get("query", "")).strip()

    if not query:
        raise ValueError("A non-empty search query is required.")

    try:
        max_results = int(data.get("max_results", 10))
    except (TypeError, ValueError) as error:
        raise ValueError("max_results must be an integer.") from error

    if max_results < 1 or max_results > 50:
        raise ValueError("max_results must be between 1 and 50.")

    query_pattern = re.compile(re.escape(query), flags=re.IGNORECASE)
    results: list[str] = []

    notes = sorted(
        path
        for path in directory.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    for note in notes:
        content = _read_note(note)

        for line_number, line in enumerate(content.splitlines(), start=1):
            if not query_pattern.search(line):
                continue

            snippet = line.strip()

            if len(snippet) > 180:
                snippet = snippet[:177] + "..."

            relative_path = note.relative_to(directory)

            results.append(
                f"{relative_path}, line {line_number}: {snippet}"
            )

            if len(results) >= max_results:
                return "\n".join(results)

    if not results:
        return f"No matches were found for '{query}'."

    return "\n".join(results)


def open_note(tool_input: str) -> str:
    """
    Read one note.

    Expected input:
    {
        "directory": "/path/to/notes",
        "filename": "research/ideas.md"
    }
    """

    data = _parse_json(tool_input)
    directory = _resolve_directory(data.get("directory"))
    note_path = _resolve_note(directory, data.get("filename"))

    content = _read_note(note_path).strip()

    if not content:
        return f"{note_path.name} is empty."

    max_characters = 12000

    if len(content) > max_characters:
        content = content[:max_characters].rstrip()
        content += "\n\n[Note truncated after 12,000 characters.]"

    return "\n".join(
        [
            f"Note: {note_path.relative_to(directory)}",
            "",
            content,
        ]
    )


def get_note_stats(tool_input: str) -> str:
    """
    Return basic statistics for one note.

    Expected input:
    {
        "directory": "/path/to/notes",
        "filename": "research/ideas.md"
    }
    """

    data = _parse_json(tool_input)
    directory = _resolve_directory(data.get("directory"))
    note_path = _resolve_note(directory, data.get("filename"))
    content = _read_note(note_path)

    words = re.findall(r"\b[\w'-]+\b", content)
    lines = content.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]

    return "\n".join(
        [
            f"Note: {note_path.relative_to(directory)}",
            f"Words: {len(words)}",
            f"Lines: {len(lines)}",
            f"Non-empty lines: {len(non_empty_lines)}",
            f"Characters: {len(content)}",
        ]
    )