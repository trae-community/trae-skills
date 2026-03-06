# TRAE Agent Skills


![TRAE Skills Banner](./assets/image/Skills.gif)

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
  _template/               # 新建技能的模板
    SKILL.md
  <skill-name>/
    SKILL.md               # （必须）智能体的核心指令
    (optional) examples/   # （可选）输入/输出示例
      input.md
      output.md
    (optional) templates/  # （可选）可复用的模板
      component.tsx
    (optional) resources/  # （可选）参考文件、运行脚本或素材
      style-guide.md
```

## 技能文件格式（SKILL.md）

每个技能必须包含 `SKILL.md`，并以 YAML frontmatter 开头：

```md
---
name: 技能名称
description: 简要描述这个技能的功能和使用场景
---

# 技能名称

## 描述
描述这个技能的作用。

## 使用场景
描述触发这个技能的条件。

## 指令
清晰的分步说明，告诉智能体具体怎么做。

## 示例 (可选)
输入/输出示例，展示预期效果。
```

元信息建议：

- `name`：小写 + 连字符（不要空格），尽量保持长期稳定
- `description`：同时写清“能做什么”和“什么时候用”（这是智能体选择是否加载的关键）

## 技能目录

本章节将列出可用的技能。

| 技能 | 描述 | 使用场景 | 状态 |
| --- | --- | --- | --- |
| [git-commit-generator](skills/git-commit-generator/SKILL.md) | 根据代码变更（diffs）生成标准化、符合 Conventional Commits 规范的 git 提交信息。 | Git 操作, 代码评审 | Stable |
| [cn-punctuation-checker](skills/cn-punctuation-checker/SKILL.md) | 检查中文文案中错误使用的英文标点符号，并支持批量修复。 | 中文文案润色, 标点纠错 | Stable |

> 提示：要把你的技能加入此目录，请在 PR 中更新此表格。

## 贡献指南

请参阅 [CONTRIBUTING.zh-CN.md](./CONTRIBUTING.zh-CN.md)。

## License

见 [LICENSE](./LICENSE)。

## 免责声明

本仓库中的技能为社区/学习用途提供。请在你自己的环境中审阅并充分测试后再用于生产或安全敏感场景。

## 链接

- TRAE 官网：https://www.trae.cn/
- TRAE 技能文档：https://docs.trae.ai/ide/skills?_lang=zh
