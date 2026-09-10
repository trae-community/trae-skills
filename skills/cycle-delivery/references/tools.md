# Tool Reference

All operations are exposed by the `trae-cycle` MCP server. The schema returned by `tools/list` is authoritative. Tools marked **job** return immediately with a `jobId`; observe the result through `cycle_status` under `jobs`.

## Installation and Diagnostics

| Tool | Purpose |
| --- | --- |
| `cycle_setup` | Validates installation: role configuration, Git availability, writable data directory, control plane health. Run once per project before the first cycle. |
| `cycle_doctor` | Read-only diagnostics for the control plane, database, ledger and role configuration, with plain-language fixes. |
| `cycle_models` | Effective per-role model assignments without secrets, plus per-role token usage totals. |
| `cycle_limits` | Live admission policy: active workflow ceiling, lease duration, resource reserves, repair budget. |

## Workflow Lifecycle

| Tool | Purpose |
| --- | --- |
| `cycle_start` | Arms or launches a workflow from the exact user request. Arguments: `project_key`, `original_request` (verbatim), `mode` (`auto` \| `quick` \| `full`), optional `affected_paths`, optional `critical_downgrade_approval`. Fails closed when role configuration is missing or invalid. |
| `cycle_status` | Workflow state, repair budget and background job results. Arguments: `project_key`, optional `workflow_id`. |
| `cycle_tasks` | Durable task list with dependencies, attempts and states. |
| `cycle_evidence` | Registers executor evidence. Arguments: `project_key`, optional `workflow_id`, `session_id`, `files` (up to 1000), `metadata` (string values, each at most 512 characters). |
| `cycle_worktree` | Creates the isolated Git worktree for governed execution. Arguments: `project_key`, `workflow_id`, `project_directory` (the user's repository). Returns `{path, baseRevision}`; every edit belongs inside `path`, and `baseRevision` feeds `cycle_freeze`. |
| `cycle_index` **job** | Indexes the project repository for mandatory code intelligence. Arguments: `project_key`, `workflow_id`, `project_directory`. Binds the repository identity that `cycle_promote` verifies; run at least once per workflow before delivery. |
| `cycle_submit_architecture` | Submits the architect plan for validation and acceptance. Arguments: `project_key`, `workflow_id`, `plan` (ArchitecturePlan object). |
| `cycle_execution_report` | Reports execution outcome. Arguments: `project_key`, `workflow_id`, `outcome` (`blocked` \| `plan_defect`). |
| `cycle_freeze` **job** | Plans verification and freezes the exact candidate. Arguments: `project_key`, `workflow_id`, `base_revision` (40-character Git revision). Requires a clean worktree. |
| `cycle_verify` **job** | Runs the verification plan over the frozen candidate. Arguments: `project_key`, `workflow_id`, `candidate_id`, `plan_id`, optional `attestations` (managed browser attestations). |
| `cycle_review` | Submits one independent review verdict. Arguments: `project_key`, `workflow_id`, `candidate_id`, `verdict` (ReviewVerdict object). |
| `cycle_arbitrate` **job** | Submits the final arbiter verdict. Arguments: `project_key`, `workflow_id`, `candidate_id`, `verdict` (ArbiterVerdict object). |
| `cycle_promote` **job** | Delivers the approved exact bytes into the project directory. Arguments: `project_key`, `workflow_id`, `candidate_id`, `project_directory`. |
| `cycle_pause` / `cycle_resume` | Pause at the next safe boundary; reconcile and resume from the saved phase. |
| `cycle_retry` | Retries a classified transient failure without consuming a repair cycle. |
| `cycle_cancel` | Cancels the workflow. Requires `confirm: true` after explicit user approval. History and evidence are preserved. |

## Role Consultations

| Tool | Purpose |
| --- | --- |
| `cycle_role` **job** | Single-role consultation. Arguments: `operation`, `role`, `request`, optional `project_key`, `session_id`. The operation and role must be paired: `architect_consult`/`architect`, `functional_review`/`functional_reviewer`, `security_review`/`security_reviewer`, `arbiter_readiness` and `arbiter_verdict`/`arbiter`. `executor_feasibility` fails closed: executor analysis happens in the TRAE Work session. Advisory operations return an advisory object; review and arbitration operations return binding verdicts that must be submitted unmodified through `cycle_review` / `cycle_arbitrate`. |

## Goals

| Tool | Purpose |
| --- | --- |
| `cycle_goal_create` | Creates a durable multi-milestone goal. Requires `project_key`, `session_id`, `objective`, non-empty `success_criteria`; optional `constraints`, `non_goals`, `max_continuations` (1-255, default 5). |
| `cycle_goal_amend` | Appends an immutable amendment. |
| `cycle_goal_status` / `cycle_goal_list` | Inspect goals and their plans and linked workflows. |
| `cycle_goal_focus` | Focuses one goal in the session. |
| `cycle_goal_save_plan` | Saves a new immutable plan revision. Requires `source_session_id` and `content`. |
| `cycle_goal_link` | Links a completed-eligible workflow to a milestone. |
| `cycle_goal_control` | Applies one lifecycle transition: `start_planning`, `mark_ready`, `activate`, `pause`, `resume`, `block`, `resume_blocked`, `continue`, `request_completion`, `approve_completion`, `reject_completion`, `abort`. |

## Memory, History and Export

| Tool | Purpose |
| --- | --- |
| `cycle_memory_search` | Searches project knowledge. Arguments: `project_key`, `text`, optional `scope`, `confidence`, `limit` (1-1000, default 20). |
| `cycle_memory_explain` | Loads one entry with provenance. |
| `cycle_memory_remove` | Revokes an eligible entry. Requires `confirm: true`. |
| `cycle_history` | Queries the redacted audit trail. Optional `after_sequence`, `limit` (1-500, default 50). |
| `cycle_history_verify` | Verifies the hash chain and signed checkpoints locally. |
| `cycle_export` | Exports redacted history. Requires `confirm: true`. |

## Job Results

`cycle_status` returns a `jobs` array. Each entry: `jobId`, `tool`, `state` (`running` \| `done` \| `failed`), and `result` or `error`. A failed job surfaces the control plane's explanation; classify transient failures (endpoint unreachable, HTTP 429/5xx) for `cycle_retry` and permanent ones (configuration, malformed output) for user-facing correction.
