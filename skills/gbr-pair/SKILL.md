---
name: gbr-pair
description: Pair a phone running Build Remote Agent to this Trae desktop session via gbr/1. Use when the user wants a mobile spectator. Attach only Bot API 127.0.0.1:8788 or gbr-mcp stdio. Requires gbr-agent v0.6.0+ on the host.
---

# Build Remote Agent pairing

## Description

Pair the Build Remote Agent phone app to this Trae session through the free MIT `gbr-agent`. Phone is spectator + veto, not orchestrator. Protocol `gbr/1` — do not invent a fourth pair protocol.

Independent product by Linespotting AB. Not affiliated with xAI or SpaceX.

Website: https://grokbuildremote.com/
Agent: https://github.com/LinespottingOrg/GrokBuildRemote-Agents

## Usage Scenario

Trigger this skill when:

- The user asks to pair a phone, spectate from mobile, or attach Build Remote Agent.
- The user wants inject/veto from a phone while Trae runs on the desktop.

## Instructions

1. Install the host agent (macOS/Linux): `curl -fsSL https://grokbuildremote.com/install.sh | bash`
2. Confirm version: `gbr-agent version` must print **v0.6.0+**.
3. Pair: `gbr-agent pair` — browser QR **and** printed 8-char code.
4. Phone: open Build Remote Agent → scan QR **or** type the 8-char code.
5. Run: `gbr-agent run` (leave it running).
6. Attach only:
   - HTTP Bot API: `http://127.0.0.1:8788`
   - MCP stdio: `node GrokBuildRemote-Agents/mcp/gbr-mcp/bin/gbr-mcp.js` (clone the agent repo, `npm install` in `mcp/gbr-mcp`)
7. Trae project MCP (`.trae/mcp.json`) may declare the same stdio server. Do not put mailbox keys in git.
8. Verify: `curl -sS http://127.0.0.1:8788/health` and `/v1/sessions`.
9. Unpair on the phone before a new mailbox. Force-close is not enough.

Loop: diagnose → open/attach → lock → inject → wait idle → harvest excerpt → iterate or close.

## Examples

**Input:** "Pair my phone so I can watch this Trae session."

**Output:** Run install → `gbr-agent pair && gbr-agent run`, tell the user to scan QR or type the 8-char code, then confirm `curl -sS http://127.0.0.1:8788/health` is ok. Do not ask for mailbox keys in chat to commit them.
