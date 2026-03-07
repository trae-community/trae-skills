#!/usr/bin/env python3
"""
Verify script for kz-doc-coauthoring

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


def _extract_frontmatter_value(frontmatter: str, key: str):
    match = re.search(rf"(?m)^{re.escape(key)}\s*(.+?)\s*$", frontmatter)
    if not match:
        return None
    value = match.group(1).strip()
    if value.startswith('"') and value.endswith('"') and len(value) >= 2:
        value = value[1:-1].strip()
    if value.startswith("'") and value.endswith("'") and len(value) >= 2:
        value = value[1:-1].strip()
    return value


def _extract_version_from_frontmatter(frontmatter: str):
    value = _extract_frontmatter_value(frontmatter, "version:")
    if not value:
        return None
    if not re.match(r"^\d+\.\d+\.\d+$", value):
        return None
    return value


def _extract_author_from_frontmatter(frontmatter: str):
    match = re.search(r"(?m)^\s*author:\s*(.+?)\s*$", frontmatter)
    if not match:
        return None
    value = match.group(1).strip()
    if value.startswith('"') and value.endswith('"') and len(value) >= 2:
        value = value[1:-1].strip()
    if value.startswith("'") and value.endswith("'") and len(value) >= 2:
        value = value[1:-1].strip()
    return value


def _extract_header_value(markdown: str, label: str):
    match = re.search(rf"(?m)^> \*\*{re.escape(label)}\*\*:\s*(.+?)\s*$", markdown)
    if not match:
        return None
    return match.group(1).strip()


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

        version = (
            _extract_version_from_frontmatter(frontmatter) if frontmatter else None
        )
        if frontmatter and not version:
            errors.append("SKILL.md frontmatter version must be semver like 1.0.0")

        if "## @工作流:" not in content:
            errors.append("SKILL.md must include a '## @工作流:' section")

        if "## @工作流: 意图识别与路由" not in content:
            errors.append("SKILL.md must include router workflow '意图识别与路由'")

        if "@跳转到:" not in content:
            errors.append("SKILL.md router must include at least one '@跳转到:'")

        if not re.search(r"(?m)^### @步骤\d+:", content):
            errors.append("SKILL.md must include at least one '### @步骤N:' section")

        if "## 最小模板规范" not in content:
            errors.append("SKILL.md must include a '## 最小模板规范' section")

        if "${DOC_PATH}" not in content:
            errors.append("SKILL.md must define and use ${DOC_PATH}")

        if "<!-- @产物: ${DOC_PATH} -->" not in content:
            errors.append(
                "SKILL.md must declare output artifact via '@产物: ${DOC_PATH}'"
            )

        if "- @动作:" not in content:
            errors.append("SKILL.md must include at least one '- @动作:' line")

        if "@验证点:" not in content:
            errors.append("SKILL.md must include '@验证点:' in step metadata")

        if "@验证方式:" not in content:
            errors.append("SKILL.md must include '@验证方式:' in step metadata")

        if "## 版本历史" not in content:
            errors.append("SKILL.md must include a '## 版本历史' section")
        elif version and f"**v{version}**" not in content:
            errors.append(f"SKILL.md version history must include v{version}")

        if version:
            header_version = _extract_header_value(content, "版本")
            if header_version != f"v{version}":
                errors.append("Header version must match frontmatter version")

        author = _extract_author_from_frontmatter(frontmatter) if frontmatter else None
        if author:
            header_author = _extract_header_value(content, "作者")
            if header_author != author:
                errors.append("Header author must match frontmatter metadata.author")

    if errors:
        for message in errors:
            print("ERROR: " + message)
        return 1

    print("OK: basic skill structure checks passed")


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
