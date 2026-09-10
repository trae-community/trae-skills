# TRAE Agent Skills

![TRAE Skills Banner](./assets/image/Skills.gif)

[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

Community-maintained Agent Skills for **TRAE**.

[中文说明](./README.zh-CN.md)

## Quickstart

1. Clone this repository.
2. Put skills into the right location for TRAE:
   - Project skills: `.trae/skills/<skill-name>/SKILL.md`
   - Global skills: `~/.trae/skills/<skill-name>/SKILL.md`
3. Refresh TRAE's skill discovery in settings (location varies by TRAE version).
4. Ask TRAE for a task that matches a skill’s description, for example:
   - “Use the git-commit-generator skill to draft a commit message for the current changes.”
   - “Use the cn-punctuation-checker skill to check Chinese punctuation in this document.”

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

To create a skill, start with the [skill template](skills/_template/SKILL.md) and follow the [contributing guide](CONTRIBUTING.md).

## Skills catalog

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
| [project-governance](skills/project-governance/SKILL.md) | Project governance workspace for AI-assisted development — project protocol (rules, permissions, autonomy levels), directory index, lessons log, session handoff, changelog, version index, and whitelist/blacklist parameter registries, with a scaffold/validate/index/check CLI. | Project Setup, AI Agent Onboarding, Parameter Versioning, Project Governance | Stable |
| [cycle-delivery](skills/cycle-delivery/SKILL.md) | Evidence-gated software delivery through a local MCP control plane: immutable request, blind reviews, arbiter approval and exact-byte Git delivery. Requires the trae-cycle binary from the project GitHub release. | Software Delivery, Code Review, Governance, Git | Stable |
| [gbr-pair](skills/gbr-pair/SKILL.md) | Pair a phone running Build Remote Agent to this Trae session (`gbr/1`). Attach only loopback Bot API `:8788` or `gbr-mcp` stdio. Phone is spectator. | Mobile spectator, pairing, MCP | Stable |
| [docx-diff-comment](skills/docx-diff-comment/SKILL.md) | Compare two Word documents to find new features in V2, add comments to the V2 document for each new feature, and generate a requirements table with effort estimation in person-days. | Document Comparison, Word Comments, Requirements Estimation | Stable |

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

See [LICENSE](./LICENSE).

## Disclaimer

Skills in this repository are provided for community/educational use. Always review and test skills in your own environment before relying on them for production or security-sensitive workflows.

## Links

- TRAE website: https://www.trae.ai/
- TRAE Skills docs: https://docs.trae.ai/ide/skills?_lang=en
