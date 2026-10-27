from __future__ import annotations

import json
from typing import Any


REQUIRED_KEYS = {
    "task_status",
    "efficiency_score",
    "critique",
    "systemic_failure_root_cause",
    "workflow_adjustments",
}

EVALUATION_INSTRUCTIONS = (
    "You are a retrospective evaluator reviewing a completed agent run using ONLY the supplied evidence. "
    "Judge goal fulfillment, loop or stall behavior, tool efficiency, and log sufficiency. "
    "Do not ask for or assume private model reasoning. "
    "When reading task_result, note that an 'iteration_limit' run was stopped by the harness at its cap, "
    "so final_output arrives empty due to truncation, not because the model refused to answer; "
    "do not critique truncation as though the model produced nothing. "
    "Return ONLY valid JSON with exact keys: "
    "task_status (SUCCESS, FAILED, or PARTIAL_SUCCESS), "
    "efficiency_score (a number from 0 to 1), "
    "critique, systemic_failure_root_cause, and workflow_adjustments."
)


def _evaluation_error(message: str) -> dict[str, Any]:
    """Return a schema-valid result explaining why evaluation could not finish."""
    return {
        "task_status": "FAILED",
        "efficiency_score": 0.0,
        "critique": message,
        "systemic_failure_root_cause": "Evaluation error",
        "workflow_adjustments": "None",
    }


def _parse_evaluation(raw_output: str) -> dict[str, Any]:
    """Validate raw evaluator text and coerce it into the required schema."""
    if not isinstance(raw_output, str) or not raw_output.strip():
        return _evaluation_error("Empty evaluator output.")

    cleaned = raw_output.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    try:
        parsed = json.loads(cleaned)
    except Exception as exc:
        return _evaluation_error(f"Invalid evaluator JSON: {exc}")

    if not isinstance(parsed, dict) or set(parsed.keys()) != REQUIRED_KEYS:
        return _evaluation_error("Evaluator JSON keys do not match REQUIRED_KEYS.")

    status = parsed.get("task_status")
    if status not in {"SUCCESS", "FAILED", "PARTIAL_SUCCESS"}:
        return _evaluation_error(f"Invalid task_status: {status}")

    score = parsed.get("efficiency_score")
    if isinstance(score, bool) or not isinstance(score, (int, float)) or not (0.0 <= float(score) <= 1.0):
        return _evaluation_error(f"Invalid efficiency_score: {score}")

    return {
        "task_status": status,
        "efficiency_score": float(score),
        "critique": str(parsed.get("critique", "")),
        "systemic_failure_root_cause": str(parsed.get("systemic_failure_root_cause", "")),
        "workflow_adjustments": str(parsed.get("workflow_adjustments", "")),
    }


def run_retrospective_evaluation(
    client: Any,
    deployment: str,
    original_prompt: str,
    execution_trace: list[dict[str, Any]],
    tool_run_log: list[dict[str, Any]],
    final_output: str,
    task_result: str,
) -> dict[str, Any]:
    """Return validated retrospective JSON for one finished task."""
    evidence = {
        "original_prompt": original_prompt,
        "execution_trace": execution_trace,
        "tool_run_log": tool_run_log,
        "final_output": final_output,
        "task_result": task_result,
    }
    try:
        review = client.responses.create(
            model=deployment,
            instructions=EVALUATION_INSTRUCTIONS,
            input=json.dumps(evidence),
        )
    except Exception as exc:
        return _evaluation_error(str(exc))

    return _parse_evaluation(review.output_text)
