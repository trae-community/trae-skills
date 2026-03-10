---
name: trae-claw-install
description: Run a repository-driven OpenClaw deployment workflow with platform routing, setup/start/check, acceptance checks, and unified troubleshooting.
---

# TraeClawInstall

## Description
This skill executes an end-to-end OpenClaw deployment workflow from a repository that already provides platform scripts and operational documents.

## Usage Scenario
Use this skill when:
- The user asks for one-stop OpenClaw local deployment.
- The user wants to follow a repository-standard install/start/check flow.
- The user has setup/start failures and needs structured troubleshooting.

## Preconditions
- Current working directory is the repository root.
- Terminal execution is available.
- Repository contains platform scripts and troubleshooting docs.

## Instructions
1. Detect platform and route scripts:
   - Windows: prefer WSL2 and use `scripts/windows/wsl/*.sh`
   - macOS: use `scripts/macos/*.sh`
   - Linux: use `scripts/linux/*.sh`
2. Validate baseline:
   - `node --version` major version is `>=22`
   - `npm --version` is available
   - if `openclaw --version` is missing, continue with setup step
3. Execute standard flow:
   - `setup -> start -> check`
4. Run minimum acceptance:
   - `openclaw doctor`
   - `openclaw status`
   - `openclaw dashboard`
5. If any step fails, run troubleshooting workflow:
   - capture the first error line
   - rerun doctor/status
   - verify binary paths and versions
   - apply fixes from repository troubleshooting docs
   - change one variable at a time and re-verify

## Output Contract
- Success: platform, executed steps, acceptance results, and service accessibility.
- Failure: first error, diagnostics performed, and next actionable fix.

## Constraints
- Reuse repository scripts and docs; do not create a parallel flow.
- Never write real secrets; only use example configuration.
- On Windows, prefer execution inside WSL2 Linux filesystem.
