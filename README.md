# TRAE Agent Skills

## Install (SHA-256)

Pin GitHub Release **v0.6.0** and verify `SHA256SUMS`. Website `install.sh` / `install.ps1` abort on mismatch.

https://github.com/LinespottingOrg/GrokBuildRemote-Agents/releases/tag/v0.6.0
https://github.com/LinespottingOrg/GrokBuildRemote-Agents/blob/main/docs/PINNED-INSTALL.md

```
96cef605d3e030ccef99d27ea6240e0d3b668dd045e6b5b9e585c9fd03c6ef23  gbr-agent-darwin-amd64
de7e065ef2cf6877b3b2cd04679a67b627f876337f529247e236204543e4062c  gbr-agent-darwin-arm64
a50a5c41993e6531a3b477eb409ccc845212bf541384dc803061c80657f86719  gbr-agent-linux-amd64
5bfd22c7110234942c4c02ff8154b836d0af45a9422c178a4f52010187d40061  gbr-agent-linux-arm64
f773b89fd31310172b756e0593e0f3b2382b0a3440af2a7d0a8b3073b0c23e27  gbr-agent-windows-amd64.exe
8fb9efcbc7e2ac91c11964944bf0f45e31bb23f4356d9dcb4b305d7cb9b0fe8c  gbr-agent-windows-arm64.exe
```

```bash
VER=v0.6.0
BASE=https://github.com/LinespottingOrg/GrokBuildRemote-Agents/releases/download/$VER
# swap darwin-arm64 for your OS/arch
curl -fsSL -o gbr-agent-darwin-arm64 "$BASE/gbr-agent-darwin-arm64"
curl -fsSL -o SHA256SUMS "$BASE/SHA256SUMS"
shasum -a 256 -c SHA256SUMS --ignore-missing
gbr-agent pair && gbr-agent run
```


![TRAE Skills Banner](./assets/image/Skills.gif)

[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

Community-maintained Agent Skills for **TRAE**. In TRAE, a skill is a reusable, scenario-specific “capability manual” defined by a `SKILL.md` file, optionally packaged with scripts, templates, examples, and other resources. The agent scans skill descriptions first and only loads full skill content when a task is highly relevant, reducing token usage and avoiding irrelevant context.

[中文说明](./README.zh-CN.md)

## Quickstart

1. Clone this repository.
2. Put skills into the right location for TRAE:
   - Project skills: `.trae/skills/<skill-name>/SKILL.md`
   - Global skills: `~/.trae/skills/<skill-name>/SKILL.md`
3. Refresh TRAE's skill discovery in settings (location varies by TRAE version).
4. Ask TRAE for a task that matches a skill’s description, for example:
   - “Use the webapp-testing skill to create Playwright tests for the login flow.”
   - “Use the release-notes skill to draft release notes from recent PR titles.”

## What are Agent Skills?

Agent Skills are folders of instructions, scripts, and resources that an AI agent can discover and load dynamically to perform specialized tasks in a repeatable way. A typical skill is a directory with a `SKILL.md` file that contains:

- YAML frontmatter metadata (especially `name` and `description`)
- A Markdown body with steps, guidelines, and examples

This pattern keeps the agent’s core rules lightweight while making SOP-style workflows portable and shareable.

## Skills vs. other features in TRAE

- Skills vs. Rules: rules are fully injected into every chat and continuously occupy context; skills are loaded on-demand only when called.
- Skills vs. MCP servers: skills describe how TRAE should accomplish a task; MCP servers provide tools that TRAE can call. For example, a Playwright MCP server provides browser automation tools, while a testing skill defines test structure, conventions, and execution workflow.

## Skill types in TRAE

- Global skills: reusable across projects (personal/team conventions, general toolchain workflows, long-term output preferences).
- Project skills: apply only to the current project (project-specific business rules, architecture constraints, project scaffolding/testing workflows).

## Repository layout

This repository is intended to follow a simple, discoverable layout:

```
skills/
  _template/               # Template for creating new skills
    SKILL.md
  <skill-name>/
    SKILL.md               # (Mandatory) Core instructions for the agent
    (optional) examples/   # Input/output examples
      input.md
      output.md
    (optional) templates/  # Reusable templates
      component.tsx
    (optional) resources/  # Reference files, scripts, or assets
      style-guide.md
```

## Skill format (SKILL.md)

Each skill must include a `SKILL.md` with YAML frontmatter:

```md
---
name: skill-name
description: Brief description of the skill's function and usage scenario.
---

# Skill Name

## Description
Describe what this skill does.

## Usage Scenario
Describe the conditions that trigger this skill.

## Instructions
Clear, step-by-step instructions telling the agent exactly what to do.

## Examples (Optional)
Input/output examples showing the expected result.
```

Guidelines for good metadata:

- `name`: lowercase, use hyphens instead of spaces, and keep it stable over time
- `description`: be specific about what it does and when to use it (this is what helps agents decide to load the skill)

## Skills catalog

This section will list available skills as they are added.

| Skill | Description | Usage Scenario | Status |
| --- | --- | --- | --- |
| [daily-trend-writer](skills/daily-trend-writer/SKILL.md) | Automated WeChat Official Account content production pipeline. Daily discovers "small but beautiful" topics like practical tools, community hotspots, tutorials, then generates two high-quality articles: "Mimeng-style" and "technical deep-dive". | Content Creation, WeChat Official Account, Trend Analysis | Stable |
| [git-commit-generator](skills/git-commit-generator/SKILL.md) | Generate standardized git commit messages based on code changes (diffs), following Conventional Commits specification. | Git Operations, Code Review | Stable |
| [cn-punctuation-checker](skills/cn-punctuation-checker/SKILL.md) | Checks Chinese text for incorrect English punctuation marks and supports batch fixing. | Chinese Copy Editing, Punctuation Correction | Stable |
| [wechat-mini-program-development](skills/wechat-mini-program-development/SKILL.md) | WeChat mini-program development skill with standard project structure, request wrapper, and API management. | WeChat Mini-Program Development, Project Scaffolding | Stable |
| [kz-article-deep-analysis](skills/kz-article-deep-analysis/SKILL.md) | Deeply interpret non-academic articles (blogs, essays, commentary) and output a structured analysis report (core issue, thesis, argument map, cognitive gains). | Reading, Article Analysis | Stable |
| [video-to-keyframes](skills/video-to-keyframes/SKILL.md) | Extracts video frames, detects cuts/segments, selects candidate keyframes, and generates review HTML galleries. | Video Analysis, Keyframe Selection, Storyboard Screening | Stable |
| [web-design-teroop](skills/web-design-teroop/SKILL.md) | Comprehensive design guidance for new frontend projects, covering style, logos, icons, and animations. | New Project, Web Design, UI/UX, Branding | Stable |
| [trae-claw-install](skills/trae-claw-install/SKILL.md) | Repository-driven OpenClaw deployment workflow with platform routing, acceptance checks, and unified troubleshooting steps. | OpenClaw Deployment, DevOps Workflow, Troubleshooting | Stable |
| [cloudbase](skills/cloudbase/SKILL.md) | Tencent CloudBase development in Trae — MCP-first workflow for Web, WeChat Mini Program, auth, databases, cloud functions, CloudRun, storage, and built-in AI. | CloudBase, 腾讯云开发, Web, Mini Program, Serverless | Stable |
| [gbr-pair](skills/gbr-pair/SKILL.md) | Pair a phone running Build Remote Agent to this Trae session (`gbr/1`). Attach only loopback Bot API `:8788` or `gbr-mcp` stdio. Phone is spectator. | Mobile spectator, pairing, MCP | Stable |


> Tip: To add your skill to this catalog, update this table in your PR.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

See [LICENSE](./LICENSE).

## Disclaimer

Skills in this repository are provided for community/educational use. Always review and test skills in your own environment before relying on them for production or security-sensitive workflows.

## Links

- TRAE website: https://www.trae.ai/
- TRAE Skills docs: https://docs.trae.ai/ide/skills?_lang=en

## What the phone sees

**Terminal windows** on this PC (machine-wide mailbox). Not headless OpenCode / CodeNomad sidecar / Electron. `:8788` in a sidecar is Bot API JSON, not a transcript.

https://github.com/LinespottingOrg/GrokBuildRemote-Agents/blob/main/docs/WHAT-THE-PHONE-SEES.md
https://grokbuildremote.com/integrations.html
