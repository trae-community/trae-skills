# Contributing to TRAE Agent Skills

PRs are welcome. Please keep skills small, task-focused, and easy to verify.

## Creating a New Skill

1.  Copy the template from `skills/_template/` to `skills/<your-skill-name>/`.
2.  Update `SKILL.md` with your skill's logic.
3.  Add any necessary resources or examples.

## Quality bar

- Clear “what/when/how” structure with steps and examples
- No secrets (API keys, tokens, internal URLs, customer data) in instructions or scripts
- Commands are copy-pasteable and scoped (avoid destructive defaults)
- Prefer deterministic outputs (templates, checklists, structured formats)
- Prefer English for Skills. If other languages are required for special cases, please explain in the PR

## Naming conventions

- Directory name must match the skill `name`
- Use `lowercase-hyphenated` names (no spaces)
- Avoid ambiguous names like `helpers` or `misc`

## Pull request checklist

- `skills/<skill-name>/SKILL.md` exists and has valid frontmatter (`name`, `description`)
- Includes at least 1 usage examples
- References files in the skill directory using relative links (if any)
- License is compatible with this repository’s LICENSE (or explicitly included per-skill)
- Update the **Skills catalog** in `README.md` with your new skill
- Verify the skill in Trae client before submitting to ensure it works as expected
- Including screenshots in the PR is recommended
