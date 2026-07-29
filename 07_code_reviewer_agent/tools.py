"""Tools used by the Python code reviewer agent."""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


def _parse_json(tool_input: str) -> dict[str, Any]:
    try:
        data = json.loads(tool_input)
    except json.JSONDecodeError as error:
        raise ValueError("Tool input must be valid JSON.") from error

    if not isinstance(data, dict):
        raise ValueError("Tool input must be a JSON object.")

    return data


def _resolve_python_file(value: Any) -> Path:
    path = Path(str(value or "")).expanduser().resolve()

    if not path.exists():
        raise ValueError(f"File does not exist: {path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    if path.suffix.lower() != ".py":
        raise ValueError("Only Python files are supported.")

    return path


def _read_source(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("The file must use UTF-8 encoding.") from error
    except OSError as error:
        raise RuntimeError(f"Could not read file: {error}") from error


def check_syntax(tool_input: str) -> str:
    """
    Check whether a Python file contains valid syntax.

    Expected input:
    {"path": "/path/to/file.py"}
    """

    data = _parse_json(tool_input)
    path = _resolve_python_file(data.get("path"))
    source = _read_source(path)

    try:
        ast.parse(source, filename=str(path))
    except SyntaxError as error:
        line = error.lineno or "unknown"
        column = error.offset or "unknown"
        message = error.msg or "Invalid syntax"

        return (
            f"Syntax error in {path.name}\n"
            f"Line: {line}\n"
            f"Column: {column}\n"
            f"Message: {message}"
        )

    return f"No syntax errors found in {path.name}."


def summarize_structure(tool_input: str) -> str:
    """
    Summarize functions, classes, imports, and line count.

    Expected input:
    {"path": "/path/to/file.py"}
    """

    data = _parse_json(tool_input)
    path = _resolve_python_file(data.get("path"))
    source = _read_source(path)

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as error:
        raise ValueError(
            "The file must contain valid Python syntax before its structure "
            "can be summarized."
        ) from error

    functions = [
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]

    classes = [
        node.name
        for node in tree.body
        if isinstance(node, ast.ClassDef)
    ]

    imports: list[str] = []

    for node in tree.body:
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports.append(module)

    line_count = len(source.splitlines())

    lines = [
        f"File: {path.name}",
        f"Lines: {line_count}",
        f"Top-level functions: {len(functions)}",
        f"Top-level classes: {len(classes)}",
        f"Import statements: {len(imports)}",
    ]

    if functions:
        lines.append("Functions: " + ", ".join(functions))

    if classes:
        lines.append("Classes: " + ", ".join(classes))

    if imports:
        lines.append("Imported modules: " + ", ".join(imports))

    return "\n".join(lines)


def find_long_lines(tool_input: str) -> str:
    """
    Find lines longer than a selected limit.

    Expected input:
    {"path": "/path/to/file.py"}

    Optional:
    {"path": "/path/to/file.py", "max_length": 88}
    """

    data = _parse_json(tool_input)
    path = _resolve_python_file(data.get("path"))
    source = _read_source(path)

    try:
        max_length = int(data.get("max_length", 88))
    except (TypeError, ValueError) as error:
        raise ValueError("max_length must be an integer.") from error

    if max_length < 40 or max_length > 200:
        raise ValueError("max_length must be between 40 and 200.")

    violations: list[str] = []

    for line_number, line in enumerate(source.splitlines(), start=1):
        length = len(line)

        if length > max_length:
            preview = line.strip()

            if len(preview) > 100:
                preview = preview[:97] + "..."

            violations.append(
                f"Line {line_number}: {length} characters — {preview}"
            )

    if not violations:
        return (
            f"No lines exceed {max_length} characters in {path.name}."
        )

    return "\n".join(
        [
            f"Found {len(violations)} line(s) longer than "
            f"{max_length} characters:",
            *violations,
        ]
    )


def find_large_functions(tool_input: str) -> str:
    """
    Find functions longer than a selected line limit.

    Expected input:
    {"path": "/path/to/file.py"}

    Optional:
    {"path": "/path/to/file.py", "max_lines": 40}
    """

    data = _parse_json(tool_input)
    path = _resolve_python_file(data.get("path"))
    source = _read_source(path)

    try:
        max_lines = int(data.get("max_lines", 40))
    except (TypeError, ValueError) as error:
        raise ValueError("max_lines must be an integer.") from error

    if max_lines < 5 or max_lines > 300:
        raise ValueError("max_lines must be between 5 and 300.")

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as error:
        raise ValueError(
            "The file must contain valid Python syntax before function "
            "lengths can be checked."
        ) from error

    violations: list[str] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        if node.end_lineno is None:
            continue

        line_count = node.end_lineno - node.lineno + 1

        if line_count > max_lines:
            violations.append(
                f"{node.name}: {line_count} lines "
                f"(starts at line {node.lineno})"
            )

    if not violations:
        return (
            f"No functions exceed {max_lines} lines in {path.name}."
        )

    return "\n".join(
        [
            f"Found {len(violations)} function(s) longer than "
            f"{max_lines} lines:",
            *violations,
        ]
    )


def find_missing_docstrings(tool_input: str) -> str:
    """
    Find modules, classes, and functions without docstrings.

    Expected input:
    {"path": "/path/to/file.py"}
    """

    data = _parse_json(tool_input)
    path = _resolve_python_file(data.get("path"))
    source = _read_source(path)

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as error:
        raise ValueError(
            "The file must contain valid Python syntax before docstrings "
            "can be checked."
        ) from error

    missing: list[str] = []

    if ast.get_docstring(tree) is None:
        missing.append("Module docstring is missing.")

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if ast.get_docstring(node) is None:
                missing.append(
                    f"Class '{node.name}' at line {node.lineno}"
                )

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if ast.get_docstring(node) is None:
                missing.append(
                    f"Function '{node.name}' at line {node.lineno}"
                )

    if not missing:
        return f"No missing docstrings found in {path.name}."

    return "\n".join(
        [
            f"Found {len(missing)} missing docstring(s):",
            *missing,
        ]
    )


def review_python_file(tool_input: str) -> str:
    """
    Run a compact set of checks on one Python file.

    Expected input:
    {"path": "/path/to/file.py"}
    """

    data = _parse_json(tool_input)
    path_value = str(data.get("path", "")).strip()

    if not path_value:
        raise ValueError("'path' is required.")

    path_input = json.dumps({"path": path_value})

    results = [
        check_syntax(path_input),
        summarize_structure(path_input),
        find_long_lines(path_input),
        find_large_functions(path_input),
        find_missing_docstrings(path_input),
    ]

    return "\n\n".join(results)