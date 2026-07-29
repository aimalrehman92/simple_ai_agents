"""Tools used by the dataset inspector agent."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


_DATASET: pd.DataFrame | None = None
_DATASET_PATH: Path | None = None


def _parse_json(tool_input: str) -> dict[str, Any]:
    try:
        data = json.loads(tool_input)
    except json.JSONDecodeError as error:
        raise ValueError("Tool input must be valid JSON.") from error

    if not isinstance(data, dict):
        raise ValueError("Tool input must be a JSON object.")

    return data


def _require_dataset() -> pd.DataFrame:
    if _DATASET is None:
        raise RuntimeError("No dataset has been loaded.")

    return _DATASET


def load_csv(tool_input: str) -> str:
    """
    Load a CSV file into the current session.

    Expected input:
    {"path": "/path/to/file.csv"}
    """

    global _DATASET, _DATASET_PATH

    data = _parse_json(tool_input)
    path = Path(str(data.get("path", ""))).expanduser().resolve()

    if not path.exists():
        raise ValueError(f"File does not exist: {path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    if path.suffix.lower() != ".csv":
        raise ValueError("Only CSV files are supported.")

    try:
        dataset = pd.read_csv(path)
    except Exception as error:
        raise RuntimeError(f"Could not read CSV file: {error}") from error

    _DATASET = dataset
    _DATASET_PATH = path

    return (
        f"Loaded {path.name} with "
        f"{dataset.shape[0]} rows and {dataset.shape[1]} columns."
    )


def get_dataset_shape(tool_input: str) -> str:
    """Return the number of rows and columns in the loaded dataset."""

    del tool_input

    dataset = _require_dataset()

    return (
        f"Rows: {dataset.shape[0]}\n"
        f"Columns: {dataset.shape[1]}"
    )


def get_column_names(tool_input: str) -> str:
    """Return column names and data types."""

    del tool_input

    dataset = _require_dataset()

    lines = [
        f"{index}. {column} ({dataset[column].dtype})"
        for index, column in enumerate(dataset.columns, start=1)
    ]

    return "\n".join(lines)


def calculate_missing_values(tool_input: str) -> str:
    """
    Report missing values for all columns or one column.

    Input may be:
    {}
    {"column": "age"}
    """

    data = _parse_json(tool_input) if tool_input.strip() else {}
    dataset = _require_dataset()

    column = str(data.get("column", "")).strip()

    if column:
        if column not in dataset.columns:
            raise ValueError(f"Unknown column: {column}")

        missing_count = int(dataset[column].isna().sum())
        percentage = (
            missing_count / len(dataset) * 100
            if len(dataset) > 0
            else 0.0
        )

        return (
            f"Column: {column}\n"
            f"Missing values: {missing_count}\n"
            f"Missing percentage: {percentage:.2f}%"
        )

    missing = dataset.isna().sum()
    percentages = (
        missing / len(dataset) * 100
        if len(dataset) > 0
        else missing.astype(float)
    )

    lines = []

    for column_name in dataset.columns:
        lines.append(
            f"{column_name}: {int(missing[column_name])} "
            f"({percentages[column_name]:.2f}%)"
        )

    return "\n".join(lines)


def summarize_column(tool_input: str) -> str:
    """
    Summarize one column.

    Expected input:
    {"column": "age"}
    """

    data = _parse_json(tool_input)
    dataset = _require_dataset()

    column = str(data.get("column", "")).strip()

    if not column:
        raise ValueError("A column name is required.")

    if column not in dataset.columns:
        raise ValueError(f"Unknown column: {column}")

    series = dataset[column]

    lines = [
        f"Column: {column}",
        f"Data type: {series.dtype}",
        f"Non-null values: {int(series.notna().sum())}",
        f"Missing values: {int(series.isna().sum())}",
        f"Unique values: {int(series.nunique(dropna=True))}",
    ]

    if pd.api.types.is_numeric_dtype(series):
        clean = series.dropna()

        if clean.empty:
            lines.append("No numeric values available for summary.")
        else:
            lines.extend(
                [
                    f"Mean: {clean.mean():.4f}",
                    f"Median: {clean.median():.4f}",
                    f"Standard deviation: {clean.std():.4f}",
                    f"Minimum: {clean.min():.4f}",
                    f"Maximum: {clean.max():.4f}",
                ]
            )
    else:
        top_values = series.dropna().astype(str).value_counts().head(5)

        if top_values.empty:
            lines.append("No values available for frequency summary.")
        else:
            lines.append("Most frequent values:")

            for value, count in top_values.items():
                lines.append(f"- {value}: {count}")

    return "\n".join(lines)


def preview_rows(tool_input: str) -> str:
    """
    Preview rows from the loaded dataset.

    Input may be:
    {}
    {"count": 5}
    """

    data = _parse_json(tool_input) if tool_input.strip() else {}
    dataset = _require_dataset()

    try:
        count = int(data.get("count", 5))
    except (TypeError, ValueError) as error:
        raise ValueError("count must be an integer.") from error

    if count < 1 or count > 20:
        raise ValueError("count must be between 1 and 20.")

    if dataset.empty:
        return "The loaded dataset contains no rows."

    return dataset.head(count).to_string(index=False)


def get_loaded_dataset(tool_input: str) -> str:
    """Return the path of the currently loaded dataset."""

    del tool_input

    _require_dataset()

    return f"Loaded dataset: {_DATASET_PATH}"