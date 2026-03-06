# TRAE Agent Skills

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
| [git-commit-generator](skills/git-commit-generator/SKILL.md) | Generate standardized git commit messages based on code changes (diffs), following Conventional Commits specification. | Git Operations, Code Review | Stable |
| [cn-punctuation-checker](skills/cn-punctuation-checker/SKILL.md) | Checks Chinese text for incorrect English punctuation marks and supports batch fixing. | Chinese Copy Editing, Punctuation Correction | Stable |

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
