"""Loop 03 scaffold: call deterministic checks around registered tools."""

from __future__ import annotations

from typing import Any

from .loop_01_non_production import HarnessLoop
from harness.stage_05_antidotes import AntidoteRegistry


class HooksLoop(HarnessLoop):
    """A hook detects a lifecycle event; an antidote checks or enriches it."""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.antidotes = AntidoteRegistry()

    def before_tool_execution(
        self, tool_name: str, tool_input: dict[str, Any]
    ) -> str | None:
        print(f"HOOK pre-tool check: {tool_name}")
        reason = self.antidotes.pre_tool(tool_name, tool_input)
        if reason is not None:
            print(f"HOOK pre-tool validation: blocked {tool_name} ({reason})")
            self.state.tool_run_log.append({
                "component": "pre_tool_hook",
                "tool": tool_name,
                "input": tool_input,
                "status": "blocked",
                "reason": reason,
            })
            return f"BLOCKED BY HOOK: {reason}"

        print(f"HOOK pre-tool decision: continue {tool_name}")
        self.state.tool_run_log.append({
            "component": "pre_tool_hook",
            "tool": tool_name,
            "input": tool_input,
            "status": "continued",
        })
        return None

    def after_tool_execution(
        self, tool_name: str, tool_input: dict[str, Any], output: str
    ) -> list[str]:
        results = self.antidotes.post_tool(tool_name, tool_input, output, self.handlers)
        if not results:
            print(f"HOOK post-tool: no antidote for {tool_name}")
            return []

        print(f"HOOK post-tool evidence: {tool_name}")
        observations: list[str] = []
        for antidote_name, evidence in results:
            print(f"ANTIDOTE {antidote_name}: completed")
            self.state.tool_run_log.append({
                "component": "post_tool_antidote",
                "tool": tool_name,
                "antidote": antidote_name,
                "evidence": evidence,
            })
            observations.append(evidence)
        return observations

