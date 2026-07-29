"""Tools used by the statistics agent."""

from __future__ import annotations

import json
import math
import statistics
from typing import Any


def _parse_json(tool_input: str) -> dict[str, Any]:
    try:
        data = json.loads(tool_input)
    except json.JSONDecodeError as error:
        raise ValueError("Tool input must be valid JSON.") from error

    if not isinstance(data, dict):
        raise ValueError("Tool input must be a JSON object.")

    return data


def _parse_values(data: dict[str, Any]) -> list[float]:
    values = data.get("values")

    if not isinstance(values, list) or not values:
        raise ValueError("'values' must be a non-empty list.")

    parsed_values: list[float] = []

    for value in values:
        try:
            number = float(value)
        except (TypeError, ValueError) as error:
            raise ValueError("All values must be numeric.") from error

        if not math.isfinite(number):
            raise ValueError("Values must be finite numbers.")

        parsed_values.append(number)

    return parsed_values


def calculate_descriptive_statistics(tool_input: str) -> str:
    """
    Calculate common descriptive statistics.

    Expected input:
    {"values": [12, 15, 18, 20]}
    """

    data = _parse_json(tool_input)
    values = _parse_values(data)

    mean = statistics.fmean(values)
    median = statistics.median(values)
    minimum = min(values)
    maximum = max(values)
    value_range = maximum - minimum

    modes = statistics.multimode(values)
    mode_text = (
        ", ".join(f"{value:.4f}" for value in modes)
        if len(modes) < len(values)
        else "No unique mode"
    )

    lines = [
        f"Count: {len(values)}",
        f"Mean: {mean:.4f}",
        f"Median: {median:.4f}",
        f"Mode: {mode_text}",
        f"Minimum: {minimum:.4f}",
        f"Maximum: {maximum:.4f}",
        f"Range: {value_range:.4f}",
    ]

    if len(values) >= 2:
        lines.extend(
            [
                f"Sample variance: {statistics.variance(values):.4f}",
                f"Sample standard deviation: {statistics.stdev(values):.4f}",
            ]
        )
    else:
        lines.extend(
            [
                "Sample variance: undefined for fewer than 2 values",
                "Sample standard deviation: undefined for fewer than 2 values",
            ]
        )

    return "\n".join(lines)


def calculate_z_score(tool_input: str) -> str:
    """
    Calculate a z-score.

    Expected input:
    {"value": 85, "mean": 70, "standard_deviation": 10}
    """

    data = _parse_json(tool_input)

    try:
        value = float(data.get("value"))
        mean = float(data.get("mean"))
        standard_deviation = float(data.get("standard_deviation"))
    except (TypeError, ValueError) as error:
        raise ValueError(
            "value, mean, and standard_deviation must be numeric."
        ) from error

    if not all(
        math.isfinite(number)
        for number in (value, mean, standard_deviation)
    ):
        raise ValueError("Inputs must be finite numbers.")

    if standard_deviation <= 0:
        raise ValueError("standard_deviation must be greater than zero.")

    z_score = (value - mean) / standard_deviation

    return (
        f"Z-score: {z_score:.4f}\n"
        f"The value is {abs(z_score):.4f} standard deviation(s) "
        f"{'above' if z_score > 0 else 'below' if z_score < 0 else 'from'} "
        f"the mean."
    )


def calculate_confusion_matrix_metrics(tool_input: str) -> str:
    """
    Calculate binary classification metrics.

    Expected input:
    {
        "true_positive": 40,
        "false_positive": 10,
        "true_negative": 35,
        "false_negative": 5
    }
    """

    data = _parse_json(tool_input)

    field_names = (
        "true_positive",
        "false_positive",
        "true_negative",
        "false_negative",
    )

    counts: dict[str, int] = {}

    for field_name in field_names:
        try:
            value = int(data.get(field_name))
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"{field_name} must be a non-negative integer."
            ) from error

        if value < 0:
            raise ValueError(
                f"{field_name} must be a non-negative integer."
            )

        counts[field_name] = value

    true_positive = counts["true_positive"]
    false_positive = counts["false_positive"]
    true_negative = counts["true_negative"]
    false_negative = counts["false_negative"]

    total = (
        true_positive
        + false_positive
        + true_negative
        + false_negative
    )

    if total == 0:
        raise ValueError("At least one confusion-matrix count must be positive.")

    def safe_divide(numerator: float, denominator: float) -> float | None:
        if denominator == 0:
            return None

        return numerator / denominator

    accuracy = safe_divide(
        true_positive + true_negative,
        total,
    )
    precision = safe_divide(
        true_positive,
        true_positive + false_positive,
    )
    recall = safe_divide(
        true_positive,
        true_positive + false_negative,
    )
    specificity = safe_divide(
        true_negative,
        true_negative + false_positive,
    )

    if precision is None or recall is None or precision + recall == 0:
        f1_score = None
    else:
        f1_score = 2 * precision * recall / (precision + recall)

    def format_metric(name: str, value: float | None) -> str:
        if value is None:
            return f"{name}: undefined"

        return f"{name}: {value:.4f}"

    return "\n".join(
        [
            format_metric("Accuracy", accuracy),
            format_metric("Precision", precision),
            format_metric("Recall", recall),
            format_metric("Specificity", specificity),
            format_metric("F1 score", f1_score),
        ]
    )


def calculate_correlation(tool_input: str) -> str:
    """
    Calculate Pearson correlation between two numeric lists.

    Expected input:
    {
        "x": [1, 2, 3, 4],
        "y": [2, 4, 5, 8]
    }
    """

    data = _parse_json(tool_input)

    x_values = data.get("x")
    y_values = data.get("y")

    if not isinstance(x_values, list) or not isinstance(y_values, list):
        raise ValueError("'x' and 'y' must be lists.")

    if len(x_values) != len(y_values):
        raise ValueError("'x' and 'y' must have the same length.")

    if len(x_values) < 2:
        raise ValueError("At least two paired observations are required.")

    parsed_x: list[float] = []
    parsed_y: list[float] = []

    for x_value, y_value in zip(x_values, y_values):
        try:
            x_number = float(x_value)
            y_number = float(y_value)
        except (TypeError, ValueError) as error:
            raise ValueError("All x and y values must be numeric.") from error

        if not math.isfinite(x_number) or not math.isfinite(y_number):
            raise ValueError("All x and y values must be finite.")

        parsed_x.append(x_number)
        parsed_y.append(y_number)

    if len(set(parsed_x)) == 1 or len(set(parsed_y)) == 1:
        raise ValueError(
            "Correlation is undefined when either variable has no variation."
        )

    mean_x = statistics.fmean(parsed_x)
    mean_y = statistics.fmean(parsed_y)

    numerator = sum(
        (x - mean_x) * (y - mean_y)
        for x, y in zip(parsed_x, parsed_y)
    )

    denominator_x = sum((x - mean_x) ** 2 for x in parsed_x)
    denominator_y = sum((y - mean_y) ** 2 for y in parsed_y)

    correlation = numerator / math.sqrt(
        denominator_x * denominator_y
    )

    

    if correlation > 0:
        direction = "positive"
    elif correlation < 0:
        direction = "negative"
    else:
        direction = "no linear"

    strength = abs(correlation)

    if strength < 0.3:
        magnitude = "weak"
    elif strength < 0.7:
        magnitude = "moderate"
    else:
        magnitude = "strong"

    return (
        f"Pearson correlation: {correlation:.4f}\n"
        f"Interpretation: {magnitude} {direction} linear relationship."
    )