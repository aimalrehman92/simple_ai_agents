"""Tools used by the file organizer agent."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any


SUPPORTED_CATEGORIES = {
    "images": {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"},
    "documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".md"},
    "spreadsheets": {".csv", ".xls", ".xlsx"},
    "presentations": {".ppt", ".pptx"},
    "audio": {".mp3", ".wav", ".aac", ".flac", ".m4a"},
    "videos": {".mp4", ".mov", ".avi", ".mkv", ".webm"},
    "archives": {".zip", ".tar", ".gz", ".rar", ".7z"},
    "code": {
        ".py",
        ".r",
        ".js",
        ".ts",
        ".java",
        ".c",
        ".cpp",
        ".html",
        ".css",
        ".sql",
        ".ipynb",
    },
}


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


def _category_for_file(file_path: Path) -> str:
    suffix = file_path.suffix.lower()

    for category, extensions in SUPPORTED_CATEGORIES.items():
        if suffix in extensions:
            return category

    return "other"


def list_files(tool_input: str) -> str:
    """
    List files in a directory.

    Expected input:
    {"directory": "/path/to/folder"}
    """

    data = _parse_json(tool_input)
    directory = _resolve_directory(data.get("directory"))

    files = sorted(
        item
        for item in directory.iterdir()
        if item.is_file()
    )

    if not files:
        return f"No files were found in {directory}."

    lines = []

    for index, file_path in enumerate(files, start=1):
        lines.append(
            f"{index}. {file_path.name} "
            f"({file_path.suffix.lower() or 'no extension'})"
        )

    return "\n".join(lines)


def classify_files(tool_input: str) -> str:
    """
    Classify files by extension.

    Expected input:
    {"directory": "/path/to/folder"}
    """

    data = _parse_json(tool_input)
    directory = _resolve_directory(data.get("directory"))

    files = sorted(
        item
        for item in directory.iterdir()
        if item.is_file()
    )

    if not files:
        return f"No files were found in {directory}."

    grouped: dict[str, list[str]] = {}

    for file_path in files:
        category = _category_for_file(file_path)
        grouped.setdefault(category, []).append(file_path.name)

    lines = []

    for category in sorted(grouped):
        lines.append(f"{category}:")
        lines.extend(f"- {name}" for name in grouped[category])

    return "\n".join(lines)


def preview_organization(tool_input: str) -> str:
    """
    Preview how files would be organized.

    Expected input:
    {"directory": "/path/to/folder"}
    """

    data = _parse_json(tool_input)
    directory = _resolve_directory(data.get("directory"))

    files = sorted(
        item
        for item in directory.iterdir()
        if item.is_file()
    )

    if not files:
        return f"No files were found in {directory}."

    lines = []

    for file_path in files:
        category = _category_for_file(file_path)
        destination = directory / category / file_path.name

        lines.append(
            f"{file_path.name} -> {destination.relative_to(directory)}"
        )

    return "\n".join(lines)


def organize_files(tool_input: str) -> str:
    """
    Move files into category folders.

    Expected input:
    {"directory": "/path/to/folder", "confirm": true}
    """

    data = _parse_json(tool_input)
    directory = _resolve_directory(data.get("directory"))
    confirm = data.get("confirm", False)

    if confirm is not True:
        raise ValueError(
            "File organization requires explicit confirmation with "
            '"confirm": true.'
        )

    files = sorted(
        item
        for item in directory.iterdir()
        if item.is_file()
    )

    if not files:
        return f"No files were found in {directory}."

    moved_files: list[str] = []

    for file_path in files:
        category = _category_for_file(file_path)
        destination_directory = directory / category
        destination_directory.mkdir(exist_ok=True)

        destination = destination_directory / file_path.name

        if destination.exists():
            counter = 1

            while True:
                candidate = destination_directory / (
                    f"{file_path.stem}_{counter}{file_path.suffix}"
                )

                if not candidate.exists():
                    destination = candidate
                    break

                counter += 1

        shutil.move(str(file_path), str(destination))

        moved_files.append(
            f"{file_path.name} -> {destination.relative_to(directory)}"
        )

    return "\n".join(
        [
            f"Moved {len(moved_files)} file(s):",
            *moved_files,
        ]
    )