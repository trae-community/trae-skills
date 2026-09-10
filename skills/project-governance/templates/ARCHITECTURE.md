# {{PROJECT_NAME}} — System Architecture

> 本文档是系统架构的权威来源，定义组件如何组合。架构变更时更新；维护术语表，
> 让人与 AI 共享同一套词汇。

以下为示例条目（**DRAFT — 未经验证**）。开始记录前请整体替换为本项目真实
架构，或删除本节；未完成梳理前保留 DRAFT 标注，不得当作已确认事实：

## Overview
本项目由三个模块组成：输入解析、核心处理、输出生成，模块间通过 JSON 接口解耦。

## Components
| Component | Responsibility | Key files | Notes |
|---|---|---|---|
| 输入解析 | 读取并校验用户输入 | src/input.py | 示例 |
| 核心处理 | 执行业务逻辑 | src/core.py | 示例 |
| 输出生成 | 格式化并写出结果 | src/output.py | 示例 |

## Data & Interfaces
| Data / interface | Schema / format | Producer | Consumer |
|---|---|---|---|
| user_input | JSON | 输入解析 | 核心处理 |
| result | JSON | 核心处理 | 输出生成 |

## Conventions & Hard Constraints
- 模块间禁止循环依赖。
- 所有外部输入必须校验后再进入核心逻辑。

## Terminology Table
| Term | Meaning |
|---|---|
| DRAFT | 草案：未经人工确认的内容，不得作为权威 |
