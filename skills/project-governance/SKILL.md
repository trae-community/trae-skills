---
name: project-governance
version: "1.2.0"
title: Project Governance
description: 为 AI 长期项目建立「项目记忆 + 文件索引 + 工作规则 + 版本记录」的治理系统，让 AI 在长期项目里「不忘事、不乱改、不重复犯错」，换会话后仍能接着做。Set up and maintain a project governance workspace for AI-assisted long-running projects — project protocol (AGENTS.md), directory index (index.md), error log (LESSONS.md), session handoff, changelog, stable version index (VERSIONS.md), whitelist/blacklist parameter registries. Use when the user complains the project is messy, files are scattered or misplaced, the AI repeats mistakes or uses wrong versions, the user expects the AI to find files itself instead of asking for paths, when starting a new AI-assisted project, onboarding an AI agent into an existing project, or when a project lacks structured rules/versioning.
author: Century0327
license: MIT-0
template: skill
triggers:
  - 项目太乱
  - 找不到文件
  - 又用错版本
  - 上次做到哪
  - 建立规则
  - project is messy
  - find files yourself
  - wrong version
  - where were we
  - set up rules
token_budget: 20000
type: plugin
category: productivity
tags:
  - governance
  - project-management
  - ai-agents
  - version-control
  - documentation
difficulty: intermediate
permissions:
  read:
    - project files
  write:
    - project files
  network: none
examples:
  - input: "项目太乱了，帮我整理一下"
    output: "生成 AGENTS.md + index.md + VERSIONS.md + blacklist/whitelist，并运行健康检查"
  - input: "上次做到哪了？哪个版本才是最终版？"
    output: "读取 session_handoff.md → VERSIONS.md → index.md，报告当前状态与权威版本"
---

# Project Governance

> 给 AI 长期项目建立一套「项目记忆 + 文件索引 + 工作规则 + 版本记录」的管理系统，让 AI 换会话、换模型后仍能正确接着项目做，而不是重新猜项目。

## 目录

- [30 秒概览](#30-秒概览)
- [何时使用 / 何时不用](#何时使用--何时不用)
- [记忆与治理的边界](#记忆与治理的边界)
- [使用步骤](#使用步骤)
- [输入 / 输出](#输入--输出)
- [失败处理](#失败处理)
- [产出物](#产出物)
- [包结构](#包结构)
- [跨平台兼容](#跨平台兼容)
- [限制](#限制)

## 30 秒概览

这个 Skill 给项目增加 8 个东西：

1. 项目规则 —— AI 应该怎么做
2. 文件地图 —— 文件在哪里
3. 项目状态 —— 现在做到哪里
4. 错误记录 —— 以前踩过什么坑
5. 版本索引 —— 哪个版本才是真的
6. 黑白名单 —— 什么能用、什么不能用
7. 会话交接 —— 上一个 AI 做到哪里
8. 变更记录 —— 为什么这么改

核心目标：**让 AI 换会话、换模型、甚至换 Agent 后，仍然能正确接着项目做，而不是重新猜项目。**

## 何时使用 / 何时不用

### 何时使用

- 用户抱怨项目太乱、文件散落、AI 总是乱放文件（"你怎么又乱放文件"）。
- 用户期望 AI 自己找文件，而不是问路径（"你自己找"）。
- AI 反复犯同样的错误，或总是用错版本。
- 用户说"你不是应该记得吗？""上次不是已经验证过了吗？""哪个才是最终版？""别重新做，之前已经跑通了"——这些是记忆与治理边界场景，仅靠记忆不可靠。
- 开始一个新的 AI 辅助项目，希望从第一天起就让 Agent 遵循稳定协议。
- 把一个 AI Agent 接入一个没有规则、错误日志、参数注册表的既有项目。
- 项目已经变乱：文件散落、参数改了没记录、过去的错误反复出现。
- 想强制落地一些持久规则，例如"先查索引再找文件""先计划后执行""文件存在 ≠ 文件有效""参数选择以注册表为准"。

### 何时不用

- 一次性问答或小改动，不需要项目级约定。
- 项目已有成熟的治理体系，只需要微调某条规则——直接改现有治理文件即可。

## 记忆与治理的边界

平台记忆（如 Trae 的用户画像 / 项目记忆）是**上下文来源，不是权威事实库**。治理文件才是**项目执行规范**。两者互补：

| 层 | 回答什么 |
|---|---|
| 平台记忆 | "以前发生过什么 / 这个用户通常怎么工作" |
| 治理文件 | "这个项目现在必须怎么工作、文件在哪里、哪个版本是权威" |

冲突时的权威优先级：

1. 当前项目文件 / 冻结版本
2. 项目治理文件（`AGENTS.md`、`index.md`、`VERSIONS.md`、注册表）
3. 项目记忆
4. 用户长期记忆
5. AI 推测

当记忆与治理文件冲突时，**治理文件优先**。从记忆中学到的持久约定，必须经人工确认后沉淀进治理文件——记忆本身永远不会成为项目的权威。

## 使用步骤

### 第 1 步 —— 初始化

```bash
python scripts/governance.py init --project-dir /path/to/project --project-name "My Project"
```

从 `templates/` 生成 11 个治理文件（除非传 `--force`，否则不会覆盖已有文件）。

### 第 2 步 —— 定制

编辑生成的 `AGENTS.md`：目录权限分区、自主权等级、产物存放规则，以及"项目定制"下的项目专属规则。通用核心治理规则保持原样。

### 第 3 步 —— 日常维护（每个会话）

1. **会话开始**：读 `index.md` → `session_handoff.md` → `LESSONS.md`；生成参数前，读 `blacklist.json` / `whitelist.json`。
2. **工作中**：通过索引找文件（禁止盲目搜索）；优先继承 `score > 0.85` 的 whitelist 条目；绝不使用 `permanent_ban: true` 的参数；新错误记入 `LESSONS.md`。
3. **会话结束**：更新 `session_handoff.md`、`index.md`（文件变动）、`CHANGELOG.md`（决策）。

### 第 4 步 —— 校验、索引、检查

```bash
python scripts/governance.py validate --project-dir /path/to/project   # 注册表是否符合 schema
python scripts/governance.py index --project-dir /path/to/project      # 重建 index.md 目录地图（链接 + 备注）
python scripts/governance.py check --project-dir /path/to/project      # 健康门禁：文件 + 注册表 + 索引新鲜度
```

`index` 只重写 `## Root layout` 的机器区块，并更新头部 `Record time`（UTC）。
如果 `## Root layout` 与 `## Change log` 之间检测到人工内容（如自定义 section），
`index` 会默认停止并提示；确认要覆盖请加 `--force`（仅解除人工内容保护，
不改变其他生成逻辑）。`check` 在索引过期时会输出 Expected/Actual 差异清单。

## 输入 / 输出

- **输入**：一个项目目录（有无治理文件皆可）、一个项目名称、用户的治理痛点（文件乱、版本错、反复犯错、"你自己找"）。
- **输出**：一个治理工作区（`AGENTS.md`、`index.md`、`VERSIONS.md`、`LESSONS.md`、`session_handoff.md`、`CHANGELOG.md`、`whitelist.json` / `blacklist.json`），以及一个通过校验、索引最新的目录地图。

## 失败处理

- `init` 失败（路径无效、权限不足）：报告失败的具体命令与原因；不要部分初始化或猜测。
- `validate` 报 schema 错误：修复注册表条目；绝不绕过校验。
- `check` 失败（缺文件 / 索引过期）：先运行 `index`，再重跑 `check`；仍失败则报告给人类。
- 绝不伪造"通过"结果——如实报告哪些已验证、哪些没有。

## 产出物

| 文件 | 用途 |
|---|---|
| `AGENTS.md` | 项目协议：核心治理规则、权威等级、首次运行协议、权限分区、信任边界 |
| `index.md` + `index_notes.json` | 权威目录地图，带可点击链接与简短备注 |
| `VERSIONS.md` | 稳定版本索引，含人工判断 |
| `LESSONS.md` | AI 错误与纠正日志 |
| `session_handoff.md` | 会话结束交接 |
| `CHANGELOG.md` | 决策与版本历史 |
| `whitelist.json` / `blacklist.json` | 已验证 / 已失败参数注册表 |
| `ARCHITECTURE.md` / `PROJECT.md` | 架构与项目卡片 |

## 包结构

- `README.md` —— 完整包概览：核心 / CLI / Skill 适配结构、子命令、限制、FAQ
- `templates/` —— 治理文件模板
- `scripts/governance.py` —— init / validate / index / check CLI
- `tests/test_governance.py` —— 92 个边界测试用例（stdlib-only）

## 跨平台兼容

本 Skill 遵循开放 Agent Skills 规范，一套 `SKILL.md` 可同时用于：

- **TraeWork / TraeCode**（自动识别）
- **Claude Code**（ClawHub 市场）
- **OpenClaw** 兼容的任意平台
- 其他支持 `AGENTS.md` 约定的 Agent

治理文件与 CLI 保持 Agent 中立：`AGENTS.md` 是业界通用约定，`governance.py` 仅依赖 Python 标准库，无网络、无第三方依赖。

## 限制

- 自动 Skill 发现 / 加载机制因平台而异：本包在 Trae 上测试最充分，其他平台可能需要手动接入 `SKILL.md` 或 `AGENTS.md`。
- 治理文件是"规范"，不是"自动执行器"：Agent 是否遵守，取决于平台对 `AGENTS.md` 的支持程度。
- 复杂项目（多团队、多仓库）可能需要自行扩展模板与规则。
