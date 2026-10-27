from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from harness.stage_03_tools import registry as _tool_registry

_REGISTERED_TOOLS = frozenset(
    re.findall(r'"name"\s*:\s*"([^"]+)"', Path(_tool_registry.__file__).read_text(encoding="utf-8"))
)


class PermissionPolicy:
    """Return allow, require_approval, or deny for each registered tool."""

    APPROVAL_REQUIRED = frozenset({"plot_data", "rank_inventory"})
    ALLOWED = (
        frozenset({
            "load_skill",
            "submit_plan",
            "list_datasets",
            "dataset_info",
            "sample_rows",
            "value_counts",
            "group_summary",
            "filter_rows",
            "correlation",
            "data_quality_report",
            "compare_vehicles",
        })
        | (_REGISTERED_TOOLS - APPROVAL_REQUIRED)
    )

    def decide(self, tool_name: str, tool_input: dict[str, Any]) -> tuple[str, str]:
        if tool_name in self.ALLOWED:
            return ("allow", f"{tool_name} is an allowed read-only EDA tool.")
        if tool_name in self.APPROVAL_REQUIRED:
            return ("require_approval", f"{tool_name} is a protected tool and requires approval.")
        return ("deny", f"{tool_name} is not an allowed tool.")
