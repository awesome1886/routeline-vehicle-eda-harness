"""Loop 03 component: route tool events to deterministic antidotes."""

from __future__ import annotations

from typing import Any

from . import plotting, ranking, vehicles


class AntidoteRegistry:
    """Return deterministic decisions or evidence for registered tools."""

    def pre_tool(self, tool_name: str, tool_input: dict[str, Any]) -> str | None:
        # The hook calls this before the handler. A returned reason blocks it.
        validators = {
            "rank_inventory": ranking.validate,
            "plot_data": plotting.validate,
            "compare_vehicles": vehicles.validate,
        }
        validator = validators.get(tool_name)
        return validator(tool_input) if validator else None

    def post_tool(
        self,
        tool_name: str,
        tool_input: dict[str, Any],
        output: str,
        handlers: Any,
    ) -> list[tuple[str, str]]:
        if not output or output.startswith(("BLOCKED", "DENIED", "ERROR")):
            return []
        if tool_name == "plot_data":
            evidence = plotting.build_evidence(handlers, tool_input)
            return [("plot-evidence", evidence)]
        return []

