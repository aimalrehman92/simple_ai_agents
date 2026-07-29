"""Tools used by the product comparison agent."""

from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from typing import Any


def _parse_json(tool_input: str) -> dict[str, Any]:
    try:
        data = json.loads(tool_input)
    except json.JSONDecodeError as error:
        raise ValueError("Tool input must be valid JSON.") from error

    if not isinstance(data, dict):
        raise ValueError("Tool input must be a JSON object.")

    return data


def _parse_price(value: Any) -> Decimal:
    try:
        price = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError("Price must be a valid number.") from error

    if price < 0:
        raise ValueError("Price cannot be negative.")

    return price.quantize(Decimal("0.01"))


def _parse_products(data: dict[str, Any]) -> list[dict[str, Any]]:
    products = data.get("products")

    if not isinstance(products, list) or not products:
        raise ValueError("'products' must be a non-empty list.")

    parsed_products: list[dict[str, Any]] = []

    for product in products:
        if not isinstance(product, dict):
            raise ValueError("Each product must be a JSON object.")

        name = str(product.get("name", "")).strip()
        price = _parse_price(product.get("price"))
        features = product.get("features", [])
        rating = product.get("rating")

        if not name:
            raise ValueError("Each product requires a name.")

        if not isinstance(features, list):
            raise ValueError("Product features must be a list.")

        cleaned_features = [
            str(feature).strip()
            for feature in features
            if str(feature).strip()
        ]

        parsed_rating: float | None = None

        if rating is not None:
            try:
                parsed_rating = float(rating)
            except (TypeError, ValueError) as error:
                raise ValueError("Rating must be numeric.") from error

            if not 0 <= parsed_rating <= 5:
                raise ValueError("Rating must be between 0 and 5.")

        parsed_products.append(
            {
                "name": name,
                "price": price,
                "features": cleaned_features,
                "rating": parsed_rating,
            }
        )

    return parsed_products


def compare_products(tool_input: str) -> str:
    """
    Compare products by price, rating, and listed features.

    Expected input:
    {
        "products": [
            {
                "name": "Product A",
                "price": 49.99,
                "rating": 4.4,
                "features": ["Feature 1", "Feature 2"]
            }
        ]
    }
    """

    data = _parse_json(tool_input)
    products = _parse_products(data)

    lines: list[str] = []

    for index, product in enumerate(products, start=1):
        rating = (
            f"{product['rating']:.1f}/5"
            if product["rating"] is not None
            else "not provided"
        )

        feature_text = (
            ", ".join(product["features"])
            if product["features"]
            else "none listed"
        )

        lines.extend(
            [
                f"{index}. {product['name']}",
                f"   Price: ${product['price']:.2f}",
                f"   Rating: {rating}",
                f"   Features: {feature_text}",
            ]
        )

    return "\n".join(lines)


def filter_by_budget(tool_input: str) -> str:
    """
    Return products whose price does not exceed a budget.

    Expected input:
    {
        "budget": 100,
        "products": [
            {"name": "Product A", "price": 49.99}
        ]
    }
    """

    data = _parse_json(tool_input)
    budget = _parse_price(data.get("budget"))
    products = _parse_products(data)

    matching_products = [
        product
        for product in products
        if product["price"] <= budget
    ]

    if not matching_products:
        return f"No products are available within a ${budget:.2f} budget."

    matching_products.sort(
        key=lambda product: (
            product["price"],
            product["name"].lower(),
        )
    )

    lines = [f"Products within a ${budget:.2f} budget:"]

    for product in matching_products:
        remaining = budget - product["price"]

        lines.append(
            f"- {product['name']}: ${product['price']:.2f} "
            f"(${remaining:.2f} under budget)"
        )

    return "\n".join(lines)


def find_cheapest_product(tool_input: str) -> str:
    """
    Find the least expensive product.

    Expected input:
    {
        "products": [
            {"name": "Product A", "price": 49.99}
        ]
    }
    """

    data = _parse_json(tool_input)
    products = _parse_products(data)

    cheapest_price = min(product["price"] for product in products)

    cheapest_products = [
        product
        for product in products
        if product["price"] == cheapest_price
    ]

    if len(cheapest_products) == 1:
        product = cheapest_products[0]

        return (
            f"The cheapest product is {product['name']} "
            f"at ${product['price']:.2f}."
        )

    names = ", ".join(product["name"] for product in cheapest_products)

    return (
        f"The lowest price is ${cheapest_price:.2f}. "
        f"The following products share that price: {names}."
    )


def rank_products(tool_input: str) -> str:
    """
    Rank products using price, rating, and required features.

    Expected input:
    {
        "products": [
            {
                "name": "Product A",
                "price": 49.99,
                "rating": 4.4,
                "features": ["Feature 1", "Feature 2"]
            }
        ],
        "budget": 100,
        "required_features": ["Feature 1"]
    }
    """

    data = _parse_json(tool_input)
    products = _parse_products(data)
    budget = _parse_price(data.get("budget"))

    required_features = data.get("required_features", [])

    if not isinstance(required_features, list):
        raise ValueError("'required_features' must be a list.")

    normalized_requirements = {
        str(feature).strip().lower()
        for feature in required_features
        if str(feature).strip()
    }

    ranked: list[tuple[float, dict[str, Any], int]] = []

    for product in products:
        product_features = {
            feature.lower()
            for feature in product["features"]
        }

        matched_features = len(
            normalized_requirements.intersection(product_features)
        )

        feature_score = (
            matched_features / len(normalized_requirements)
            if normalized_requirements
            else 1.0
        )

        rating_score = (
            product["rating"] / 5
            if product["rating"] is not None
            else 0.5
        )

        if product["price"] <= budget:
            price_score = float(
                (budget - product["price"]) / budget
            ) if budget > 0 else 1.0
        else:
            price_score = -float(
                (product["price"] - budget) / max(budget, Decimal("1.00"))
            )

        total_score = (
            feature_score * 0.5
            + rating_score * 0.3
            + price_score * 0.2
        )

        ranked.append(
            (
                total_score,
                product,
                matched_features,
            )
        )

    ranked.sort(
        key=lambda item: (
            -item[0],
            item[1]["price"],
            item[1]["name"].lower(),
        )
    )

    lines = []

    for index, (score, product, matched_features) in enumerate(
        ranked,
        start=1,
    ):
        budget_status = (
            "within budget"
            if product["price"] <= budget
            else "over budget"
        )

        lines.append(
            f"{index}. {product['name']} — score: {score:.3f}, "
            f"price: ${product['price']:.2f}, "
            f"{budget_status}, "
            f"matched features: "
            f"{matched_features}/{len(normalized_requirements)}"
        )

    return "\n".join(lines)