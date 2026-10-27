"""Deterministic checks and evidence for chart calls."""

from __future__ import annotations

from typing import Any


def validate(tool_input: dict[str, Any]) -> str | None:
    """Return a blocking reason when the chart population is not declared."""
    if "filters" not in tool_input or not isinstance(tool_input["filters"], list):
        return "Chart requires a declared population via filters (use filters: [] for full dataset)."
    return None

def build_evidence(handlers: Any, tool_input: dict[str, Any]) -> str:
    """Return numbers behind a successfully generated chart."""
    evidence = handlers.plot_evidence(tool_input)
    return f"ANTIDOTE: {evidence}"


