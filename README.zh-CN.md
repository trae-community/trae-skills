# TRAE Agent Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

TRAE 社区维护的 Agent Skills 仓库。在 TRAE 中，技能（Skill）通过 `SKILL.md` 文件进行定义和管理。一个技能可以理解为提供给智能体的一套"能力手册"，并可按需携带脚本、模板、示例与相关资源。执行任务前，智能体会先扫描所有技能的简要描述，仅当判断任务与某个技能高度相关时，才会加载该技能的详细内容，从而减少 Token 消耗并避免无关信息干扰。

[English README](./README.md)

## 快速开始

1. 克隆本仓库到本地。
2. 将技能放到 TRAE 约定目录：
   - 项目技能：`.trae/skills/<skill-name>/SKILL.md`
   - 全局技能：`~/.trae/skills/<skill-name>/SKILL.md`
3. 在 TRAE 设置中刷新技能发现（不同版本的 TRAE 入口位置可能略有差异）。
4. 用自然语言提出与某个技能描述匹配的请求，例如：
   - "使用 webapp-testing 技能，为登录流程创建 Playwright 的端到端测试。"
   - "使用 release-notes 技能，根据最近的 PR 标题生成 Release Notes 草稿。"

## 什么是 Agent Skills？

Agent Skills 是一组可发现的文件夹，包含指令、脚本与资源；当任务命中某个技能的 `description` 时，智能体会动态加载该技能的详细内容并按其流程执行。典型技能以 `SKILL.md` 为核心，包含：

- YAML frontmatter 元信息（尤其是 `name` 和 `description`）
- Markdown 正文（步骤、规范、示例）

这种方式可以让智能体的“常驻指令”保持精简，把复杂的任务流程拆成模块化、可共享的能力。

## 技能 vs 其他功能（TRAE）

- 技能 vs 规则：规则采用全量加载机制，一旦开启对话就会持续占用上下文；技能采用按需加载，仅在实际需要时才注入上下文，从而显著降低 Token 消耗。
- 技能 vs MCP Server：技能用于描述 TRAE 如何完成任务，MCP Server 负责提供可被 TRAE 调用的工具。例如 Playwright MCP Server 提供页面操作能力，而测试类技能用于约定工程结构、POM 设计规范与常见用例编写/执行流程，指导 TRAE 在正确上下文中高效调用工具。

## 技能类型（TRAE）

- 全局技能：跨项目生效（通用开发范式、通用工具链使用、长期输出偏好等）。
- 项目技能：仅对当前项目生效（项目专属业务规则、技术方案约束、项目内生成测试/脚手架等工作流）。

## 仓库结构约定

本仓库建议遵循如下结构来组织技能：

```
skills/
  <skill-name>/
    SKILL.md
    (可选) scripts/
    (可选) examples/
    (可选) assets/
```

## 技能文件格式（SKILL.md）

每个技能必须包含 `SKILL.md`，并以 YAML frontmatter 开头：

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
- "Write Playwright tests for signup and password reset."
```

中文示例：

```md
---
name: webapp-testing
description: 使用 Playwright 为 Web 应用创建和运行基于浏览器的测试。
---

# Web 应用测试

## 我能做什么
- 为关键用户流程生成 Playwright 测试
- 提供本地运行测试的命令

## 何时使用
当您需要可靠的端到端浏览器测试时使用此技能。

## 示例
- "为注册和密码重置流程编写 Playwright 测试。"
```

元信息建议：

- `name`：小写 + 连字符（不要空格），尽量保持长期稳定
- `description`：同时写清“能做什么”和“什么时候用”（这是智能体选择是否加载的关键）

## 技能列表（Catalog）

随着贡献增加，这里会列出当前可用技能。

| 技能 | 描述 | 适用场景 | 状态 |
| --- | --- | --- | --- |
|（即将上线）|（即将上线）|（即将上线）| experimental |

> 提示：要把你的技能加入此目录，请在 PR 中更新此表格。

## 贡献指南

欢迎提交 PR。建议把每个技能做到“小而专”，并确保容易验证。

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
- License 与本仓库 LICENSE 兼容（或在技能内明确单独 License）

## License

见 [LICENSE](./LICENSE)。

## 免责声明

本仓库中的技能为社区/学习用途提供。请在你自己的环境中审阅并充分测试后再用于生产或安全敏感场景。

## 链接

- TRAE 官网：https://www.trae.cn/
- TRAE 技能文档：https://docs.trae.ai/ide/skills?_lang=zh
