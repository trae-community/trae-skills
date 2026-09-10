#!/usr/bin/env python3
"""项目治理工作区脚手架与参数注册表校验工具。

子命令:
  init      从 templates/ 生成 AGENTS.md、index.md、LESSONS.md、
            session_handoff.md、CHANGELOG.md、VERSIONS.md、
            blacklist.json、whitelist.json、index_notes.json。
  validate  校验 blacklist.json / whitelist.json 是否符合 schema。
  index     扫描文件系统，刷新 index.md 的目录地图区块（带可点击链接
            与 index_notes.json 中的简短备注）。
  check     检查治理工作区是否完整、有效、索引是否最新。

脚本是确定性的且幂等的：除非传 --force，否则不会覆盖已有文件。
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

TEMPLATE_FILES = [
    "AGENTS.md",
    "ARCHITECTURE.md",
    "PROJECT.md",
    "index.md",
    "index_notes.json",
    "LESSONS.md",
    "session_handoff.md",
    "CHANGELOG.md",
    "VERSIONS.md",
    "blacklist.json",
    "whitelist.json",
]

# Files that must exist for a governance workspace to be usable.
CORE_REQUIRED_FILES = [
    "AGENTS.md",
    "index.md",
    "session_handoff.md",
    "LESSONS.md",
    "CHANGELOG.md",
    "VERSIONS.md",
    "blacklist.json",
    "whitelist.json",
]

# Only placeholders that can be auto-filled are substituted; the rest stay
# as {{PLACEHOLDER}} for the user to fill in.
AUTO_PLACEHOLDERS = {
    "{{PROJECT_NAME}}": "My Project",
    "{{PROJECT_ROOT}}": ".",
    "{{DATE}}": date.today().isoformat(),
    "{{CHANGES}}": "Initial scaffold.",
}

SKIP_DIRS = {
    ".git", ".hg", ".svn", "__pycache__", ".pytest_cache", ".mypy_cache",
    "node_modules", ".venv", "venv", ".idea", ".vscode", "dist", "build",
}

BLACKLIST_REQUIRED = ["id", "reason", "permanent_ban", "alternative", "test_ref", "judge", "scope", "status"]
WHITELIST_REQUIRED = ["id", "score", "config", "test_ref", "judge", "last_verified", "scope", "status"]
VALID_STATUS = {"active", "superseded", "deprecated"}
VALID_JUDGE = {"ai", "human"}

# 字段用途说明，校验失败时提示用户"怎么改"。
FIELD_HELP = {
    "id": "唯一标识，如 test_20260801_v1_cfg7steps25",
    "reason": "一句话说明：为什么失败 / 为什么通过",
    "permanent_ban": "是否永久禁用：true 或 false",
    "alternative": "替代方案：推荐参数组合或文件路径",
    "test_ref": "测试记录引用：文件路径或版本号",
    "judge": "判定来源：ai（AI 评审）或 human（人工评审）",
    "scope": "适用范围：如 sdxl / all",
    "status": "状态：active（在用）/ superseded（被取代）/ deprecated（已弃用）",
    "score": "评分 0~1，>0.85 优先继承",
    "config": "参数配置：JSON 对象",
    "last_verified": "最后验证日期：YYYY-MM-DD",
}

DEFAULT_ROOT_SECTION = "## Root layout"
DEFAULT_CHANGELOG_SECTION = "## Change log"
DEFAULT_MAX_DEPTH = 4
DEFAULT_MAX_NOTE_LENGTH = 60

# 头部元数据注释中记录生效的 index 参数，check 优先读取（缺失时回退默认），
# 保证 index / check 参数同源、旧项目兼容。
META_OPEN = "<!-- index-meta:"
META_ITEM = re.compile(r"([a-z_]+)=(?:\"([^\"]*)\"|([^,\s]+))")


def _templates_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "templates"


def cmd_init(args: argparse.Namespace) -> int:
    project_dir = Path(args.project_dir).resolve()
    if project_dir.exists() and not project_dir.is_dir():
        print(f"错误：目标路径已存在且是一个文件，不是目录: {project_dir}")
        print("  HINT: 换一个不存在的目录路径，或先删除该文件再重试。")
        return 1
    project_dir.mkdir(parents=True, exist_ok=True)
    templates = _templates_dir()
    if not templates.is_dir():
        print(f"错误：找不到模板目录: {templates}")
        print("  HINT: 复制本 Skill 时请保留 templates/ 与 scripts/ 在同一目录下，不要只拷贝 scripts/。")
        return 1

    if getattr(args, "project_name", None):
        AUTO_PLACEHOLDERS["{{PROJECT_NAME}}"] = args.project_name

    created, skipped = [], []
    for name in TEMPLATE_FILES:
        dst = project_dir / name
        if dst.is_dir():
            print(f"错误：目标路径已存在且是一个目录，不是文件: {dst}")
            print("  HINT: 删除该同名目录，或换一个项目目录。")
            return 1
        if dst.exists() and not args.force:
            skipped.append(name)
            continue
        src = templates / name
        if not src.exists():
            print(f"错误：模板缺失: {src}")
            print("  HINT: 重新下载完整版 Skill 包，确保 templates/ 目录完整。")
            return 1
        text = src.read_text(encoding="utf-8")
        for key, value in AUTO_PLACEHOLDERS.items():
            text = text.replace(key, value)
        dst.write_text(text, encoding="utf-8")
        created.append(name)

    print(f"已在 {project_dir} 生成 {len(created)} 个治理文件")
    for name in created:
        print(f"  + {name}")
    if skipped:
        print(f"跳过 {len(skipped)} 个已存在的文件（如需覆盖请加 --force）:")
        for name in skipped:
            print(f"  = {name}")
    return 0


def _validate_registry(path: Path, required: list[str], label: str, relaxed: bool = False) -> list[str]:
    errors = []
    if not path.exists():
        errors.append(f"{label}: 文件不存在: {path}")
        errors.append("  HINT: 先运行 'governance.py init --project-dir <目录>' 生成注册表，或手动创建该文件。")
        return errors
    if not path.is_file():
        errors.append(f"{label}: 不是普通文件: {path}")
        return errors
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        errors.append(f"{label}: 文件不是有效的 UTF-8 文本: {exc}")
        errors.append("  HINT: 用 UTF-8 编码重新保存该 JSON 文件（不要用 GBK/ANSI）。")
        return errors
    except json.JSONDecodeError as exc:
        errors.append(f"{label}: JSON 格式错误，第 {exc.lineno} 行: {exc.msg}")
        errors.append("  HINT: 检查该行附近的引号/逗号/括号是否配对；可用 JSON 校验工具定位。")
        return errors
    if not isinstance(data, dict):
        errors.append(f"{label}: 顶层必须是 JSON 对象，当前是 {type(data).__name__}")
        errors.append("  HINT: 文件最外层应为 { \"blacklist\": [...] } 或 { \"whitelist\": [...] }。")
        return errors

    entries = data.get(label)
    if not isinstance(entries, list):
        errors.append(f"{label}: 顶层 '{label}' 必须是数组")
        errors.append("  HINT: 形如 { \"" + label + "\": [ { ...条目... } ] }。")
        return errors

    seen_ids = set()
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"{label}[{idx}]: 条目必须是对象")
            errors.append("  HINT: 每个条目用 { } 包裹，字段见 README「注册表 Schema」。")
            continue
        if not relaxed:
            missing = [f for f in required if f not in entry]
            if missing:
                errors.append(f"{label}[{idx}]: 缺少必填字段: {', '.join(missing)}")
                for f in missing:
                    errors.append(f"  HINT: {f} = {FIELD_HELP.get(f, '见 README「注册表 Schema」')}")
        if "id" in entry:
            if not isinstance(entry["id"], str):
                errors.append(f"{label}[{idx}]: id 必须是字符串，当前是 {entry['id']!r}")
                errors.append("  HINT: 给 id 加引号，如 \"id\": \"test_20260801_v1_cfg7steps25\"。")
            elif entry["id"] in seen_ids:
                errors.append(f"{label}[{idx}]: id 重复 '{entry['id']}'")
                errors.append("  HINT: 每个条目的 id 必须唯一，改成一个新标识。")
            else:
                seen_ids.add(entry["id"])
        if "status" in entry and entry["status"] not in VALID_STATUS:
            errors.append(f"{label}[{idx}]: status 无效 '{entry['status']}'（可选: {sorted(VALID_STATUS)}）")
            errors.append("  HINT: status 只能填 active / superseded / deprecated。")
        if "judge" in entry and entry["judge"] not in VALID_JUDGE:
            errors.append(f"{label}[{idx}]: judge 无效 '{entry['judge']}'（可选: {sorted(VALID_JUDGE)}）")
            errors.append("  HINT: judge 只能填 ai（AI 评审）或 human（人工评审）。")
        if label == "blacklist" and "permanent_ban" in entry and not isinstance(entry["permanent_ban"], bool):
            errors.append(f"{label}[{idx}]: permanent_ban 必须是布尔值，当前是 {entry['permanent_ban']!r}")
            errors.append("  HINT: permanent_ban 只能填 true 或 false（不要加引号）。")
        if label == "whitelist" and "score" in entry:
            score = entry["score"]
            if isinstance(score, bool) or not isinstance(score, (int, float)) or not 0 <= score <= 1:
                errors.append(f"{label}[{idx}]: score 必须是 0~1 的数字，当前是 {score!r}")
                errors.append("  HINT: score 填 0~1 之间的小数，如 0.9；>0.85 的组合会被优先继承。")
    return errors


def cmd_validate(args: argparse.Namespace) -> int:
    project_dir = Path(args.project_dir).resolve()
    relaxed = getattr(args, "relaxed", False)
    errors = []
    errors += _validate_registry(project_dir / "blacklist.json", BLACKLIST_REQUIRED, "blacklist", relaxed)
    errors += _validate_registry(project_dir / "whitelist.json", WHITELIST_REQUIRED, "whitelist", relaxed)
    if errors:
        print("校验失败（VALIDATION FAILED）:")
        for err in errors:
            print(f"  - {err}")
        print("修复方法：按上面的 HINT 修改注册表 JSON；字段完整说明见 README「注册表 Schema」或 templates 示例。")
        return 1
    mode = "relaxed " if relaxed else ""
    print(f"校验通过（VALIDATION PASSED）: blacklist.json 和 whitelist.json 符合 {mode}schema。")
    return 0


def _find_heading_line(text: str, heading: str) -> int:
    """Return the 0-based line index of the first heading equal to `heading`
    that is NOT inside a fenced code block, or -1 if not found."""
    lines = text.splitlines()
    in_fence = False
    fence_char = ""
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("```") or s.startswith("~~~"):
            ch = s[0]
            if in_fence and ch == fence_char:
                in_fence = False
                fence_char = ""
            elif not in_fence:
                in_fence = True
                fence_char = ch
            continue
        if in_fence:
            continue
        if s == heading or s.startswith(heading + " "):
            return i
    return -1


def _utc_today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _read_index_meta(text: str) -> dict:
    """Parse the `index-meta` HTML comment in index.md into a dict. Returns {}
    when absent (old projects) so callers fall back to defaults."""
    m = re.search(r"<!--\s*index-meta:.*?-->", text, re.S)
    if not m:
        return {}
    meta = {}
    for key, quoted, bare in META_ITEM.findall(m.group(0)):
        meta[key] = quoted if quoted else bare
    return meta


def _upsert_meta(text: str, params: dict, record_time: str) -> str:
    meta = (
        f"{META_OPEN} record_time={record_time}, "
        f"max_depth={params['max_depth']}, "
        f"max_note_length={params['max_note_length']}, "
        f"root_section=\"{params['root_section']}\", "
        f"changelog_section=\"{params['changelog_section']}\" -->"
    )
    if re.search(r"<!--\s*index-meta:", text):
        return re.sub(r"<!--\s*index-meta:.*?-->", meta, text, count=1, flags=re.S)
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.strip():
            lines.insert(i + 1, meta + "\n")
            break
    return "".join(lines)


def _resolve_index_params(args: argparse.Namespace, meta: dict | None = None) -> dict:
    """Index/check 参数同源：显式 CLI 参数 > 头部元数据 > 默认值。"""
    meta = meta or {}

    def pick(name: str, default):
        val = getattr(args, name, None)
        return default if val is None else val

    return {
        "max_depth": int(pick("max_depth", meta.get("max_depth", DEFAULT_MAX_DEPTH))),
        "max_note_length": int(pick("max_note_length", meta.get("max_note_length", DEFAULT_MAX_NOTE_LENGTH))),
        "root_section": pick("root_section", meta.get("root_section", DEFAULT_ROOT_SECTION)),
        "changelog_section": pick("changelog_section", meta.get("changelog_section", DEFAULT_CHANGELOG_SECTION)),
    }


def _update_record_time(text: str, record_time: str) -> str:
    """A-3：头部 Record time 由 index 命令独占更新。"""
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.startswith("Record time:"):
            lines[i] = f"Record time: {record_time}\n"
            break
    return "".join(lines)


def _find_manual_content(text: str, start: int, end: int) -> int:
    """Return the 1-based line number of the first line between `start` and
    `end` that is non-empty and outside a fenced code block, or -1 if none.

    Lines starting with '>' (blockquote) are treated as machine-authored
    template hints and ignored, keeping old projects compatible."""
    lines = text.splitlines()
    in_block = False
    for i in range(start + 1, end):
        s = lines[i].strip()
        if s.startswith("```") or s.startswith("~~~"):
            in_block = not in_block
            continue
        if in_block or not s or s.startswith(">"):
            continue
        return i + 1
    return -1


def _format_diff(actual: list[str], expected: list[str]) -> list[str]:
    sm = difflib.SequenceMatcher(a=actual, b=expected)
    out = []
    limit = 20
    for op, a1, a2, b1, b2 in sm.get_opcodes():
        if op == "equal":
            continue
        for line in actual[a1:a2]:
            out.append(f"当前（Actual）: {line}")
        for line in expected[b1:b2]:
            out.append(f"期望（Expected）: {line}")
        if len(out) >= limit:
            out.append(f"…（差异较多，仅显示前 {limit} 行）")
            break
    return out


def _index_state(project_dir: Path, index_path: Path, args: argparse.Namespace) -> tuple[bool, list[str]]:
    """Return (is_fresh, diff_lines). Structural problems yield (False, [])."""
    try:
        text = index_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return False, []
    params = _resolve_index_params(args, _read_index_meta(text))
    start = _find_heading_line(text, params["root_section"])
    end = _find_heading_line(text, params["changelog_section"])
    if start == -1 or end == -1 or end <= start:
        return False, []
    block = _extract_fenced_block(text, start, end)
    if block is None:
        return False, []
    notes = _load_notes(project_dir)
    tree = _build_tree(project_dir, params["max_depth"], notes, params["max_note_length"])
    actual = block.splitlines()
    if actual == tree:
        return True, []
    return False, _format_diff(actual, tree)


def _notes_stale_paths(project_dir: Path) -> list[str]:
    """A-9b warning 3：仅当 index_notes.json 存在（备注功能已启用）且 JSON
    可解析时，报告指向不存在路径的备注键。"""
    notes_path = project_dir / "index_notes.json"
    if not notes_path.is_file():
        return []
    try:
        data = json.loads(notes_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, OSError):
        return []
    if not isinstance(data, dict):
        return []
    stale = []
    for key in data:
        if not isinstance(key, str):
            continue
        if not (project_dir / key.rstrip("/")).exists():
            stale.append(key)
    return stale


def _unreplaced_placeholders(project_dir: Path) -> list[tuple[str, str]]:
    """A-9b warning 1：只检测 init 自动替换的占位符（AUTO_PLACEHOLDERS）。
    用户待填的 {{...}}（如 ARCHITECTURE 的示例区）不在检测范围，避免误报。"""
    found = []
    for name in CORE_REQUIRED_FILES + ["ARCHITECTURE.md", "PROJECT.md"]:
        p = project_dir / name
        if not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for key in AUTO_PLACEHOLDERS:
            if key in text:
                found.append((name, key))
    return found


def _version_consistency_warning(project_dir: Path) -> str | None:
    """A-9b warning 2：仅当能可靠解析版本时检测（项目含 SKILL.md frontmatter
    version 且 CHANGELOG.md 使用 '## [x.y.z]' 标题格式）。用户项目 CHANGELOG
    为表格格式时不检测，避免治理噪声。"""
    skill = project_dir / "SKILL.md"
    changelog = project_dir / "CHANGELOG.md"
    if not (skill.is_file() and changelog.is_file()):
        return None
    try:
        skill_text = skill.read_text(encoding="utf-8")
        cl_text = changelog.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None
    m = re.search(r"^version:\s*[\"']?([\w.]+)", skill_text, re.M)
    if not m:
        return None
    m2 = re.search(r"^##\s+\[([\w.]+)\]", cl_text, re.M)
    if not m2:
        return None
    skill_ver = m.group(1)
    cl_ver = m2.group(1)
    if skill_ver != cl_ver:
        return (f"版本不一致：SKILL.md 声明 version {skill_ver}，"
                f"CHANGELOG.md 最新版本为 [{cl_ver}]（发布新版本时请同步更新）")
    return None


def _link_target(rel: str) -> str:
    """Wrap a relative path in angle brackets when it contains characters that
    would break a bare markdown link (spaces, parens, angle brackets)."""
    if any(c in rel for c in " <>()"):
        return f"<{rel}>"
    return rel


def _load_notes(project_dir: Path) -> dict[str, str]:
    """Read index_notes.json into {rel_path: note}. Returns {} on any problem
    and prints a warning so the index command can degrade gracefully."""
    notes_path = project_dir / "index_notes.json"
    if not notes_path.exists():
        return {}
    if not notes_path.is_file():
        print("警告：index_notes.json 不是普通文件，已忽略备注。")
        return {}
    try:
        data = json.loads(notes_path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        print(f"警告：index_notes.json 不是有效的 UTF-8 文本（{exc}），已忽略备注。")
        return {}
    except json.JSONDecodeError as exc:
        print(f"警告：index_notes.json 第 {exc.lineno} 行 JSON 格式错误（{exc.msg}），已忽略备注。")
        return {}
    if not isinstance(data, dict):
        print("警告：index_notes.json 顶层必须是 JSON 对象，已忽略备注。")
        return {}
    return {str(k): str(v) for k, v in data.items() if isinstance(v, str)}


def _build_tree(root: Path, max_depth: int, notes: dict[str, str] | None = None,
                max_note_length: int = DEFAULT_MAX_NOTE_LENGTH) -> list[str]:
    notes = notes or {}
    lines = []

    def walk(path: Path, prefix: str, depth: int) -> None:
        if depth > max_depth:
            lines.append(f"{prefix}└── ...")
            return
        try:
            entries = sorted(
                (p for p in path.iterdir() if p.name not in SKIP_DIRS and not p.name.startswith(".")),
                key=lambda p: (p.is_file(), p.name.lower()),
            )
        except OSError:
            lines.append(f"{prefix}└── <unreadable>")
            return
        for i, entry in enumerate(entries):
            last = i == len(entries) - 1
            connector = "└── " if last else "├── "
            rel = entry.relative_to(root).as_posix()
            name = entry.name + ("/" if entry.is_dir() else "")
            line = f"{prefix}{connector}[{name}]({_link_target(rel)})"
            note = notes.get(rel) or notes.get(rel + "/")
            if note:
                if len(note) > max_note_length:
                    note = note[:max_note_length] + "…"
                line += f" — {note}"
            lines.append(line)
            if entry.is_dir():
                walk(entry, prefix + ("    " if last else "│   "), depth + 1)

    walk(root, "", 0)
    return lines


def _extract_fenced_block(text: str, start: int, end: int) -> str | None:
    """Return the content of the first fenced code block within lines
    [start, end), or None if no complete block is found."""
    lines = text.splitlines()
    content: list[str] = []
    in_block = False
    for i in range(start, end):
        s = lines[i].strip()
        if s.startswith("```"):
            if not in_block:
                in_block = True
            else:
                return "\n".join(content)
            continue
        if in_block:
            content.append(lines[i])
    return None


def _is_index_fresh(project_dir: Path, index_path: Path, args: argparse.Namespace) -> bool:
    return _index_state(project_dir, index_path, args)[0]


def cmd_index(args: argparse.Namespace) -> int:
    project_dir = Path(args.project_dir).resolve()
    index_path = project_dir / "index.md"
    if not index_path.exists():
        print(f"错误：找不到 index.md: {index_path}")
        print("  HINT: 先运行 'governance.py init --project-dir <目录>' 生成治理工作区，再执行 index。")
        return 1
    if not index_path.is_file():
        print(f"错误：index.md 不是普通文件: {index_path}")
        return 1

    params = _resolve_index_params(args)
    root_section = params["root_section"]
    changelog_section = params["changelog_section"]
    notes = _load_notes(project_dir)
    tree = _build_tree(project_dir, params["max_depth"], notes, params["max_note_length"])
    section = f"{root_section}\n```\n" + "\n".join(tree) + "\n```\n"

    try:
        text = index_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        print(f"错误：index.md 不是有效的 UTF-8 文本: {exc}")
        print("  HINT: 用 UTF-8 编码重新保存 index.md（不要用 GBK/ANSI）。")
        return 1
    start = _find_heading_line(text, root_section)
    end = _find_heading_line(text, changelog_section)
    if start == -1 or end == -1 or end <= start:
        print(f"错误：index.md 必须包含 '{root_section}' 且位于 '{changelog_section}' 之前。")
        print("  HINT: 检查 index.md 的标题是否被改动；或先用 init 重新生成。")
        return 1

    manual = _find_manual_content(text, start, end)
    if manual != -1 and not getattr(args, "force", False):
        print(f"错误：'{root_section}' 与 '{changelog_section}' 之间检测到人工内容（第 {manual} 行附近）。")
        print(f"  index.md 的目录树区块由 'governance.py index' 独占维护，手动编辑的内容会被整体覆盖。")
        print(f"  如需保留：把人工内容移到 '{changelog_section}' 之后，或写入 index_notes.json / 自定义 section。")
        print("  确认要覆盖请加 --force（仅解除人工内容保护，不改变其他生成逻辑）。")
        return 1

    lines = text.splitlines(keepends=True)
    new_text = "".join(lines[:start]) + section + "".join(lines[end:])
    record_time = _utc_today()
    new_text = _update_record_time(new_text, record_time)
    new_text = _upsert_meta(new_text, params, record_time)
    index_path.write_text(new_text, encoding="utf-8")
    print(f"已更新 {index_path} 的 '{root_section}' 区块（共 {len(tree)} 行，Record time: {record_time} UTC）。")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    project_dir = Path(args.project_dir).resolve()
    errors = []
    warnings = []

    for f in CORE_REQUIRED_FILES:
        p = project_dir / f
        if not p.exists():
            errors.append(f"缺少必需文件: {f}")
            errors.append("  HINT: 运行 'governance.py init --project-dir <目录>' 补齐缺失文件。")
        elif not p.is_file():
            errors.append(f"必需路径不是普通文件: {f}")

    errors += _validate_registry(project_dir / "blacklist.json", BLACKLIST_REQUIRED, "blacklist")
    errors += _validate_registry(project_dir / "whitelist.json", WHITELIST_REQUIRED, "whitelist")

    notes_path = project_dir / "index_notes.json"
    if notes_path.exists():
        if not notes_path.is_file():
            errors.append("index_notes.json 不是普通文件")
        else:
            try:
                data = json.loads(notes_path.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    errors.append("index_notes.json: 顶层必须是 JSON 对象")
            except UnicodeDecodeError as exc:
                errors.append(f"index_notes.json: 不是有效的 UTF-8 文本: {exc}")
            except json.JSONDecodeError as exc:
                errors.append(f"index_notes.json: 第 {exc.lineno} 行 JSON 格式错误: {exc.msg}")

    index_path = project_dir / "index.md"
    if index_path.is_file():
        fresh, diffs = _index_state(project_dir, index_path, args)
        if not fresh:
            errors.append("index.md 已过期（运行 'governance.py index' 更新）；Expected/Actual 差异：")
            errors.extend(diffs)

    for name, key in _unreplaced_placeholders(project_dir):
        warnings.append(f"{name} 仍包含未替换占位符 {key}（init 会自动替换；如为手动创建请填写或删除）")
    ver_warning = _version_consistency_warning(project_dir)
    if ver_warning:
        warnings.append(ver_warning)
    for key in _notes_stale_paths(project_dir):
        warnings.append(f"index_notes.json 备注指向不存在的路径: {key}（如已归档/移动，请更新或删除该备注）")

    if warnings:
        print("检测到警告（不阻塞，按需处理）:")
        for w in warnings:
            print(f"  ! {w}")

    if errors:
        print("健康检查未通过（CHECK FAILED）:")
        for err in errors:
            print(f"  - {err}")
        print("修复方法：按上面的 HINT 处理；全部通过后再次运行 check 确认。")
        return 1
    print("健康检查通过（CHECK PASSED）: 治理工作区完整、有效、索引最新。")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="从模板生成治理工作区")
    p_init.add_argument("--project-dir", required=True, help="目标项目目录")
    p_init.add_argument("--project-name", default="My Project", help="项目名称（默认: My Project）")
    p_init.add_argument("--force", action="store_true", help="覆盖已有文件")
    p_init.set_defaults(func=cmd_init)

    p_val = sub.add_parser("validate", help="校验 blacklist.json / whitelist.json 的 schema")
    p_val.add_argument("--project-dir", required=True, help="包含注册表的项目目录")
    p_val.add_argument("--relaxed", action="store_true",
                       help="不因缺少可选字段而失败（便于迁移旧注册表）")
    p_val.set_defaults(func=cmd_validate)

    p_idx = sub.add_parser("index", help="刷新 index.md 的目录地图区块")
    p_idx.add_argument("--project-dir", required=True, help="包含 index.md 的项目目录")
    p_idx.add_argument("--max-depth", type=int, default=None,
                       help=f"目录树最大深度（默认: {DEFAULT_MAX_DEPTH}；未传时读 index.md 头部元数据）")
    p_idx.add_argument("--root-section", default=None,
                       help=f"要替换的 index 区块标题（默认: '{DEFAULT_ROOT_SECTION}'；未传时读头部元数据）")
    p_idx.add_argument("--changelog-section", default=None,
                       help=f"目录地图结束处的区块标题（默认: '{DEFAULT_CHANGELOG_SECTION}'；未传时读头部元数据）")
    p_idx.add_argument("--max-note-length", type=int, default=None,
                       help=f"index_notes.json 备注截断前的最大长度（默认: {DEFAULT_MAX_NOTE_LENGTH}；未传时读头部元数据）")
    p_idx.add_argument("--force", action="store_true",
                       help="存在人工内容时强制覆盖（仅解除人工内容保护，不改变其他生成逻辑）")
    p_idx.set_defaults(func=cmd_index)

    p_chk = sub.add_parser("check", help="检查治理工作区是否完整、有效、索引最新")
    p_chk.add_argument("--project-dir", required=True, help="要检查的项目目录")
    p_chk.add_argument("--max-depth", type=int, default=None,
                       help=f"新鲜度检查用的目录树最大深度（默认: {DEFAULT_MAX_DEPTH}；未传时读 index.md 头部元数据）")
    p_chk.add_argument("--root-section", default=None,
                       help=f"要检查的 index 区块标题（默认: '{DEFAULT_ROOT_SECTION}'；未传时读头部元数据）")
    p_chk.add_argument("--changelog-section", default=None,
                       help=f"目录地图结束处的区块标题（默认: '{DEFAULT_CHANGELOG_SECTION}'；未传时读头部元数据）")
    p_chk.add_argument("--max-note-length", type=int, default=None,
                       help=f"新鲜度检查用的备注最大长度（默认: {DEFAULT_MAX_NOTE_LENGTH}；未传时读头部元数据）")
    p_chk.set_defaults(func=cmd_check)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:  # noqa: BLE001
        print(f"错误：发生意外异常: {exc}")
        print("  HINT: 检查参数与文件权限；若仍失败，可附带完整报错反馈给作者。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
