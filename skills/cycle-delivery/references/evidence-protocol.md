# Evidence Protocol

Evidence is the only currency verification, reviews and arbitration accept. Work without registered evidence cannot pass a gate, and a gate that cannot be evidenced fails as `unavailable`.

## What Counts as Evidence

- **Command evidence**: a terminal or build command, its exit code, and its output. Register the output file and the identifying metadata.
- **Test evidence**: test runs covering the changed scopes, with pass/fail counts.
- **Browser evidence**: a UI flow exercised through TRAE Work `/browser_use`, with the checked URL, the performed actions and the observed outcome.
- **File evidence**: artifacts the verifier can hash and bind (reports, screenshots, exported results).

## Registering Evidence

Call `cycle_evidence` with:

- `project_key` and, when in a workflow, `workflow_id` and `session_id`;
- `files`: paths of artifacts to bind, at most 1000;
- `metadata`: string key/value pairs, each value at most 512 characters.

Use stable metadata keys so later phases can query consistently:

- `kind`: `command` | `test` | `browser` | `artifact`;
- `command` or `url`: what was exercised;
- `exit_code` or `outcome`: `passed` | `failed` | `unavailable`;
- `summary`: one line describing what the evidence proves.

Register evidence when it is produced. Batch-registering at the end invites gaps between claims and proof.

## Browser Flows

1. Run the flow with `/browser_use` under TRAE Work permissions: navigate, act, observe.
2. Capture what proves the requirement: final URL, observed state, screenshot artifact path.
3. Register immediately with `cycle_evidence`, `kind=browser`, the URL, the outcome and the artifact path in `files`.
4. When the workflow reaches verification, pass the corresponding managed attestations to `cycle_verify` so the control plane can bind each browser record to the frozen candidate digest.

Late file changes invalidate bound evidence: if anything changes after freeze, evidence must be regenerated over the new candidate. Never fabricate or hand-edit evidence values; the chain records what was registered, not what was claimed.

## Boundaries

- Secret material never goes into evidence: no keys, tokens, passwords or dump files containing them.
- Evidence metadata describes, it does not assert conclusions. "tests: 42 passed" is evidence; "the feature works" is not.
- `unavailable` is a failing state, not a skip: a required gate without a project-native command must be resolved by adding the command or changing the plan, never by relabeling.
