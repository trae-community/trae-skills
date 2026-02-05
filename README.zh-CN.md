# TRAE Agent Skills（中文）

TRAE 社区维护的 Agent Skills 仓库。在 TRAE 中，技能（Skill）通过 `SKILL.md` 文件进行定义和管理。一个技能可以理解为提供给智能体的一套“专业能力说明书”，并可按需携带脚本、模板、示例与相关资源。执行任务前，智能体会先扫描所有技能的简要描述，仅当判断任务与某个技能高度相关时，才会加载该技能的详细内容，从而减少 Token 消耗并避免无关信息干扰。

[English README](./README.md)

## 快速开始

1. 克隆本仓库到本地。
2. 将技能放到 TRAE 约定目录：
   - 项目技能：`.trae/skills/<skill-name>/SKILL.md`
   - 全局技能：`~/.trae/skills/<skill-name>/SKILL.md`
3. 在 TRAE 中刷新/配置技能发现（不同版本的 TRAE 入口/命名可能略有差异）。
4. 用自然语言提出与某个 skill 描述匹配的请求，例如：
   - “使用 webapp-testing skill，为登录流程创建 Playwright 的端到端测试。”
   - “使用 release-notes skill，根据最近的 PR 标题生成 Release Notes 草稿。”

## 什么是 Agent Skills？

Agent Skills 是一组可发现的文件夹，包含指令、脚本与资源；当任务命中某个 skill 的 `description` 时，Agent 会动态加载该 skill 的详细内容并按其流程执行。典型 skill 以 `SKILL.md` 为核心，包含：

- YAML frontmatter 元信息（尤其是 `name` 和 `description`）
- Markdown 正文（步骤、规范、示例）

这种方式可以让 Agent 的“常驻指令”保持精简，把复杂的任务流程拆成模块化、可共享的能力。

## 技能 vs 其他功能（TRAE）

- 技能 vs 规则：规则采用全量加载机制，一旦开启对话就会持续占用上下文；技能采用按需加载，仅在实际需要时才注入上下文，从而显著降低 Token 消耗。
- 技能 vs MCP Server：技能用于描述 TRAE 如何完成任务，MCP Server 负责提供可被 TRAE 调用的工具。例如 Playwright MCP Server 提供页面操作能力，而测试类技能用于约定工程结构、POM 设计规范与常见用例编写/执行流程，指导 TRAE 在正确上下文中高效调用工具。

## 技能类型（TRAE）

- 全局技能：跨项目生效（通用开发范式、通用工具链使用、长期输出偏好等）。
- 项目技能：仅对当前项目生效（项目专属业务规则、技术方案约束、项目内生成测试/脚手架等工作流）。

## 仓库结构约定

本仓库建议遵循如下结构来组织 skills：

```
skills/
  <skill-name>/
    SKILL.md
    (可选) scripts/
    (可选) examples/
    (可选) assets/
```

## Skill 文件格式（SKILL.md）

每个 skill 必须包含 `SKILL.md`，并以 YAML frontmatter 开头：

```md
---
name: webapp-testing
description: Create and run browser-based tests with Playwright for web apps.
---

# Web App Testing

## What I do
- Generate Playwright tests for key user flows
- Provide commands to run tests locally

## When to use
Use this skill when you need reliable end-to-end browser tests.

## Examples
- “Write Playwright tests for signup and password reset.”
```

元信息建议：

- `name`：小写 + 连字符（不要空格），尽量保持长期稳定
- `description`：同时写清“能做什么”和“什么时候用”（这是 agent 选择是否加载的关键）

## Skills 列表（Catalog）

随着贡献增加，这里会列出当前可用 skills。

| Skill | 描述 | 适用场景 | 状态 |
| --- | --- | --- | --- |
|（即将上线）|（即将上线）|（即将上线）| experimental |

## 贡献指南

欢迎提交 PR。建议把每个 skill 做到“小而专”，并确保容易验证。

### 质量要求（Quality bar）

- 结构清晰：说明“做什么/何时用/如何做”，并包含可执行步骤与示例
- 不要包含敏感信息：密钥、Token、内网地址、客户数据等
- 命令可复制粘贴、默认安全（避免破坏性操作）
- 尽量输出可复用的结构化结果（模板、清单、固定格式）

### 命名约定

- 目录名必须与 frontmatter 的 `name` 一致
- 使用 `lowercase-hyphenated` 风格命名
- 避免含糊的名字（例如 `misc`、`helpers`）

### PR 自检清单

- 存在 `skills/<skill-name>/SKILL.md`，且 frontmatter 包含 `name`、`description`
- 至少包含 1 个使用示例
- 若引用目录内文件，使用相对路径链接
- License 与本仓库 LICENSE 兼容（或在 skill 内明确单独 License）

## License

见 [LICENSE](./LICENSE)。

## 免责声明

本仓库 skills 为社区/学习用途提供。请在你自己的环境中审阅并充分测试后再用于生产或安全敏感场景。

## 链接

- TRAE 官网：https://www.trae.cn/
- TRAE 技能文档：https://docs.trae.ai/ide/skills?_lang=zh
