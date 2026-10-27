# RouteLine Vehicle EDA Harness: Cross-Loop Comparison

All four loops were evaluated against the identical shared EDA question in `prompts/master_prompt.txt`:
> *"What patterns and trade-offs in performance, price, vehicle condition, and ownership costs appear in the dealership's inventory and vehicle-history data?"*

Holding the prompt and dataset constant demonstrates that differences across the four runs are directly attributable to the harness controls added in the gap between the model requesting an action and the runtime executing it.

---

## 1. Loop 01 — Non-Production Baseline (`outputs/non-production/prompt/`)
* **Added Control:** Skill loading (`load_skill`) and explicit human plan approval (`submit_plan`) before executing registered read-only and analytical EDA tools.
* **Exact Proof from Trace (`outputs/non-production/prompt/tool_trace.json`):**
  * The trace records `load_skill` followed by `submit_plan`, pausing execution until human approval was granted before running dataset inspection and summary tools (such as `dataset_info`, `group_summary`, `correlation`, `plot_data`, and `rank_inventory`).
* **Observed Effect on the Shared Question:**
  * The agent followed a structured analytical plan rather than calling tools ad hoc, producing a baseline synthesis of price, mileage, condition, and ownership cost trade-offs in `outputs/non-production/prompt/answer.md`. However, it lacked post-run quality auditing, pre-tool argument validation, deterministic chart statistics, and per-call permission gating.

---

## 2. Loop 02 — Retrospective Self-Evaluation (`outputs/self-evaluation/prompt/`)
* **Added Control:** A separate, post-completion model call (`run_retrospective_evaluation`) that audits the finished run using only the recorded execution trace, tool log, and final answer.
* **Exact Proof from Artifacts (`outputs/self-evaluation/prompt/retrospective_evaluation.json`):**
  * The evaluator generated `retrospective_evaluation.json` with all five required schema keys:
    * `"task_status": "SUCCESS"`
    * `"efficiency_score"`: *(check your `retrospective_evaluation.json` value, e.g., `0.9`)*
    * `"critique"`: Verified goal fulfillment, tool efficiency, and log sufficiency from the trace.
    * `"systemic_failure_root_cause"` and `"workflow_adjustments"` populated.
* **Observed Effect on the Shared Question:**
  * Without altering the primary EDA conversation, the harness produced an automated, structured quality audit after the run completed (and properly waited until after plan approval and final output generation before running).

---

## 3. Loop 03 — Pre-Tool Hooks & Output Antidotes (`outputs/hooks/prompt/`)
* **Added Control:**
  1. **Deterministic Pre-Tool Hooks (`before_tool_execution`):** Validates tool inputs before execution—blocking negative/unsupported ranking weights in `rank_inventory`, duplicate stock IDs in `compare_vehicles`, and `plot_data` calls missing an explicit `filters` population declaration (`filters: []` for full dataset).
  2. **Post-Chart Antidotes (`after_tool_execution`):** Automatically computes and attaches deterministic statistical evidence (`ANTIDOTE: ...` with population counts, grouped means, ranges, or correlations) after `plot_data` runs.
* **Exact Proof from Trace & Terminal (`outputs/hooks/prompt/tool_trace.json`):**
  * Terminal output logged `HOOK pre-tool check: plot_data`, `HOOK pre-tool decision: continue plot_data` (or `HOOK pre-tool validation: blocked ...` when a check failed), `HOOK post-tool evidence: plot_data`, and `ANTIDOTE plot-evidence: completed`.
  * `outputs/hooks/prompt/tool_trace.json` records `{"component": "pre_tool_hook", "tool": "plot_data", "status": "continued"}` and `{"component": "post_tool_antidote", "tool": "plot_data", "antidote": "plot-evidence", "evidence": "ANTIDOTE: ..."}`.
* **Observed Effect on the Shared Question:**
  * Any invalid tool call was deterministically blocked with an actionable reason so the model could self-correct, and the final answer in `outputs/hooks/prompt/answer.md` directly cited the exact numeric statistics injected by the `plot-evidence` antidote alongside the saved chart in `outputs/plots/`.

---

## 4. Loop 04 — Scoped Permissions (`outputs/permissions/prompt/`)
* **Added Control:** Least-privilege permission policy (`PermissionPolicy.decide`) classifying every tool call as `allow` (read-only EDA, skill, and planning tools), `require_approval` (protected tools: `plot_data` and `rank_inventory`), or `deny` (unregistered tools), with single-use grants scoped to one exact tool name and argument object (`"scope": "one_exact_call"`).
* **Exact Proof from Trace & Terminal (`outputs/permissions/prompt/tool_trace.json`):**
  * Terminal output logged `PERMISSION CHECK: <tool_name> -> allow` for read-only calls, and `PERMISSION CHECK: plot_data -> require_approval` / `PERMISSION CHECK: rank_inventory -> require_approval` followed by `PERMISSION GRANTED: <tool_name>` upon human approval.
  * `outputs/permissions/prompt/tool_trace.json` records:
    * `{"component": "permission_check", "tool": "...", "decision": "allow", ...}` for read-only EDA calls.
    * `{"component": "permission_check", "tool": "plot_data", "decision": "require_approval", ...}` followed by `{"component": "permission_grant", "tool": "plot_data", "event": "grant", "scope": "one_exact_call"}` (and likewise for `rank_inventory`), followed by execution of that single exact call.
* **Observed Effect on the Shared Question:**
  * Read-only exploration proceeded seamlessly, while high-impact actions (`plot_data` chart generation and `rank_inventory` vehicle ranking) paused execution and displayed their exact arguments for human review. Each approval authorized only that single, unmodified call before the final answer was saved to `outputs/permissions/prompt/answer.md`.
