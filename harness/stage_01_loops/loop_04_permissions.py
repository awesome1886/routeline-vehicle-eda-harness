"""Loop 04 scaffold: authorize each protected request before it runs."""

from __future__ import annotations

from typing import Any

from .loop_01_non_production import HarnessLoop
from harness.stage_06_permissions import PermissionPolicy


class PermissionsLoop(HarnessLoop):
    """A grant applies to one exact tool name and argument object."""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.permissions = PermissionPolicy()

    @staticmethod
    def _same_request(left: dict[str, Any] | None, right: dict[str, Any]) -> bool:
        """Report whether a stored grant covers exactly this request."""
        if not isinstance(left, dict) or not isinstance(right, dict):
            return False
        return left.get("tool") == right.get("tool") and left.get("input") == right.get("input")

    def before_tool_execution(
        self, tool_name: str, tool_input: dict[str, Any]
    ) -> str | None:
        current_request = {"tool": tool_name, "input": tool_input}
        if self._same_request(self.state.granted_permission, current_request):
            self.state.granted_permission = None
            return None

        decision, reason = self.permissions.decide(tool_name, tool_input)
        self.state.tool_run_log.append({
            "component": "permission_check",
            "tool": tool_name,
            "input": tool_input,
            "decision": decision,
            "reason": reason,
        })
        print(f"PERMISSION CHECK: {tool_name} -> {decision}")

        if decision == "allow":
            return None
        if decision == "require_approval":
            self.state.permission_request = current_request
            self.state.permission_required = True
            return f"BLOCKED: {reason}"
        return f"DENIED: {reason}"

    def pause_status(self) -> str | None:
        if self.state.permission_required:
            return "permission_required"
        return None

    def grant_pending_permission(self) -> None:
        pending = self.state.permission_request
        if not pending:
            return
        self.state.granted_permission = pending
        self.state.permission_request = None
        self.state.permission_required = False
        self.state.tool_run_log.append({
            "component": "permission_grant",
            "tool": pending["tool"],
            "input": pending["input"],
            "event": "grant",
            "scope": "one_exact_call",
        })
        print(f"PERMISSION GRANTED: {pending['tool']}")

    def resume_after_permission(
        self,
        permission_response: Any,
        tool_results: list[dict[str, Any]],
        starting_loop: int,
    ) -> dict[str, Any]:
        followup_input = [
            *tool_results,
            {
                "role": "user",
                "content": (
                    "Permission granted for that exact call. "
                    "Please reissue the identical tool call and arguments now."
                ),
            },
        ]
        return self.agent_loop(
            followup_input,
            previous_response_id=permission_response.id,
            starting_loop=starting_loop,
        )


