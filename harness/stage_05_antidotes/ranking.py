"""Deterministic check for unsafe inventory-ranking arguments."""

from __future__ import annotations

from typing import Any


SUPPORTED_METRICS = frozenset({
    "reliability_score_10", "owner_satisfaction_10",
    "three_year_value_retention_pct", "five_year_value_retention_pct",
    "owners_who_would_buy_again_pct", "cargo_cuft", "horsepower",
    "warranty_months_remaining", "dealer_discount_usd", "year",
    "price_usd", "mileage", "distance_miles",
    "avg_annual_repair_cost_usd", "complaints_per_100_vehicles",
    "avg_annual_insurance_usd", "avg_annual_fuel_or_energy_usd",
    "previous_owners",
})


def validate(tool_input: dict[str, Any]) -> str | None:
    """Return a reason for unsupported or negative ranking weights."""
    weights = tool_input.get("weights")
    if not isinstance(weights, dict) or not weights:
        return "Ranking requires a non-empty weights dictionary."
    for metric, weight in weights.items():
        if metric not in SUPPORTED_METRICS:
            return f"Unsupported ranking metric: {metric}."
        if not isinstance(weight, (int, float)) or weight < 0:
            return f"Negative ranking weight is not allowed for {metric}: {weight}."
    return None

