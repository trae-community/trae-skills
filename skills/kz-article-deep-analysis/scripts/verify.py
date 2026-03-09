#!/usr/bin/env python3
"""
Verify script for article-deep-analysis

This script provides deterministic checks that complement SKILL.md instructions.
"""

import argparse
import re
import sys
from pathlib import Path


def _read_text(path: Path):
    return path.read_text(encoding="utf-8")


def _extract_frontmatter(markdown: str):
    match = re.match(r"\A---\s*\n([\s\S]*?)\n---\s*\n", markdown)
    if not match:
        return None
    return match.group(1)


def _has_required_frontmatter(frontmatter: str):
    required_keys = ["name:", "description:", "version:"]
    return all(key in frontmatter for key in required_keys)


def verify(skill_dir: Path):
    errors = []

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append("Missing SKILL.md: " + str(skill_md))
    else:
        try:
            content = _read_text(skill_md)
        except Exception as e:
            errors.append("Failed to read SKILL.md: " + str(e))
            content = ""

        frontmatter = _extract_frontmatter(content) if content else None
        if not frontmatter:
            errors.append("SKILL.md missing YAML frontmatter (--- ... ---)")
        elif not _has_required_frontmatter(frontmatter):
            errors.append("SKILL.md frontmatter must include name/description/version")

        if "## @工作流:" not in content:
            errors.append("SKILL.md must include a '## @工作流:' section")

        if "## 版本历史" not in content:
            errors.append("SKILL.md must include a '## 版本历史' section")

    if not (skill_dir / "references" / "methodology.md").exists():
        errors.append("Missing references/methodology.md")

    if not (skill_dir / "assets" / "template.md").exists():
        errors.append("Missing assets/template.md")

    if errors:
        for message in errors:
            print("ERROR: " + message)
        return 1

    print("OK: basic skill structure checks passed")
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", required=True, help="Skill folder path")
    args = parser.parse_args()

    skill_dir = Path(args.skill).resolve()
    if not skill_dir.exists():
        print("ERROR: skill folder not found: " + str(skill_dir))
        sys.exit(1)

    sys.exit(verify(skill_dir))

if __name__ == "__main__":
    main()
