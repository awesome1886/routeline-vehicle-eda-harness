"""Deterministic check for duplicate vehicle comparisons."""

from __future__ import annotations

from typing import Any


def validate(tool_input: dict[str, Any]) -> str | None:
    """Return a reason when compare_vehicles repeats a stock ID."""
    stock_ids = tool_input.get("stock_ids") or []
    if len(stock_ids) != len(set(stock_ids)):
        return "Duplicate stock_ids are not allowed in compare_vehicles."
    return None

