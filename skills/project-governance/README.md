# Project Governance

> **AI 会忘记上一会话做了什么——这个 Skill 让它记住。**

## 这段话是写给你的

你遇到过这些问题吗？

- **AI 换个会话就不认识项目了**——每次都要重新解释项目结构、规则、上次做到哪
- **AI 把历史文件当权威**——明明有稳定版本，AI 却找到了一堆旧的、过时的、废弃的文件
- **AI 重复犯同样的错误**——上次已经踩过的坑，这次又踩一遍，因为没有人告诉 AI"上次为什么错了"
- **AI 找不到文件**——"文件在哪里？""你告诉我路径"——你不能自己找吗？
- **AI 把文件乱放**——产物散落在各个目录，没有命名规则，没有归档纪律
- **项目越来越乱**——文件越来越多，但没人知道哪个是正式版本、哪个是实验版本、哪个已经废弃
- **"你不是应该记得吗？"**——AI 不记得，因为没人告诉它应该记得什么

这个 Skill 就是解决这些问题的。

## 适合谁

- **长期 AI 项目的负责人**：项目会持续很多天、很多会话，AI 换会话就"失忆"。
- **被 AI 反复坑过的开发者**：AI 用错版本、重复犯错、找不到文件，想让它"长记性"。
- **刚起步的 AI 辅助项目**：从第一天就建立规则，避免后期返工。
- **多 Agent / 多模型协作的项目**：换 Agent、换模型后仍能接着做。

不适合：一次性小任务、已有成熟治理体系的项目（直接改现有文件即可）。

## 它能做什么

建立一套**AI 能理解、人类能维护**的项目治理系统：

| 文件 | 做什么 |
|------|--------|
| `AGENTS.md` | 告诉 AI 这个项目怎么工作、什么能做什么不能做 |
| `index.md` | 文件地图——AI 不再问"文件在哪里" |
| `VERSIONS.md` | 权威版本索引——"哪个才是最终版" |
| `LESSONS.md` | 错误档案——"上次为什么错了，这次别再犯" |
| `session_handoff.md` | 会话交接——"上次做到哪了" |
| `CHANGELOG.md` | 变更记录——"项目为什么变成现在这样" |
| `whitelist.json` | 好参数——"这个方案已验证可用，优先用" |
| `blacklist.json` | 坏参数——"这个方案已验证失败，禁止用" |

## 快速开始

```bash
# 初始化治理工作区（一条命令生成全部 11 个文件）
python scripts/governance.py init --project-dir /path/to/project

# 验证参数注册表
python scripts/governance.py validate --project-dir /path/to/project

# 生成文件索引
python scripts/governance.py index --project-dir /path/to/project

# 健康检查
python scripts/governance.py check --project-dir /path/to/project
```

> 提示：`init` 只需指定 `--project-dir` 即可；`--project-name` 可选（默认 "My Project"）。所有命令都幂等，重复运行不会破坏已有文件。

## 核心设计

**记忆与治理的边界（Memory & Governance Boundary）**
AI 的记忆（Memory）是上下文来源，不是权威事实库。治理文件才是执行规范。当二者冲突时：
```
当前项目文件/冻结版本 > 治理文件 > 项目记忆 > 用户记忆 > AI 推测
```

**文件权威等级**
```
AUTHORITATIVE → STABLE → EXPERIMENTAL → HISTORICAL → DEPRECATED → ARCHIVED
```
文件存在 ≠ 文件有效。AI 必须先确认文件权威性，再使用。

**执行纪律**
- 先查 index，再找文件
- 参数从 whitelist 继承，blacklist 永久禁用参数一律不用
- 犯错→记录到 LESSONS→下次不再犯
- 每次会话结束写 session_handoff

## 命令行工具

`scripts/governance.py` 提供 4 个子命令，全部中文提示，出错时带 `HINT` 修复指引：

| 子命令 | 作用 | 关键参数 |
|--------|------|----------|
| `init` | 从模板生成治理工作区 | `--project-dir`（必填）、`--project-name`、`--force` |
| `validate` | 校验 blacklist/whitelist schema | `--project-dir`、`--relaxed`（宽松模式） |
| `index` | 重建 index.md 目录地图 | `--project-dir`、`--max-depth`、`--force`（覆盖人工内容保护）等 |
| `check` | 健康门禁：文件+注册表+索引 | `--project-dir` |

校验失败时，会逐条指出问题并给出修复方法，例如：

```
校验失败（VALIDATION FAILED）:
  - blacklist[2]: 缺少必填字段: permanent_ban
    HINT: permanent_ban = 是否永久禁用：true 或 false
修复方法：按上面的 HINT 修改注册表 JSON；字段完整说明见 README「注册表 Schema」或 templates 示例。
```

## 注册表 Schema

`blacklist.json` 必填字段：`id`、`reason`、`permanent_ban`、`alternative`、`test_ref`、`judge`、`scope`、`status`

`whitelist.json` 必填字段：`id`、`score`、`config`、`test_ref`、`judge`、`last_verified`、`scope`、`status`

字段取值约束：
- `judge`：`ai`（AI 评审）或 `human`（人工评审）
- `status`：`active`（在用）/ `superseded`（被取代）/ `deprecated`（已弃用）
- `permanent_ban`：`true` 或 `false`（布尔值，不加引号）
- `score`：0~1 的小数，>0.85 的组合会被优先继承

## 跨平台兼容

这个 Skill 遵循开放 Agent Skills 规范，一套 `SKILL.md` 可同时用于：

- **TraeWork / TraeCode**（自动识别，测试最充分）
- **Claude Code**（ClawHub 市场）
- **OpenClaw** 兼容的任意平台
- 其他支持 `AGENTS.md` 约定的 Agent

`governance.py` 仅依赖 Python 标准库，无网络、无第三方依赖，任何平台都能直接运行。

## 常见问题（FAQ）

**Q1：这个 Skill 和平台自带的"记忆"功能冲突吗？**
不冲突。记忆是上下文来源，治理文件是执行规范。当二者冲突时，治理文件优先（详见 SKILL.md「记忆与治理的边界」）。记忆里学到的持久约定，经人工确认后沉淀进治理文件。

**Q2：初始化之后还要改什么？**
只需编辑生成的 `AGENTS.md`：目录权限分区、自主权等级、产物存放规则、项目专属规则。通用核心规则保持原样即可。

**Q3：运行 `validate` 报错，说"缺少必填字段"，怎么改？**
报错会逐条列出缺失字段并给出 `HINT`（字段用途与示例）。按 HINT 补上即可。字段完整说明见 README「注册表 Schema」。

**Q4：`check` 说 index.md 过期了，怎么办？**
运行 `python scripts/governance.py index --project-dir <目录>` 重建索引，再重跑 `check`。`check` 会列出 Expected/Actual 差异清单（当前有哪些、期望有哪些），方便定位是新增了文件还是误改了 index。另外，`index` 只重写 `## Root layout` 的机器区块：如果它与 `## Change log` 之间有人工内容（如自定义 section），`index` 会默认停止并提示，确认要覆盖才需加 `--force`。

**Q5：会覆盖我已有的文件吗？**
不会。`init` 默认跳过已存在的文件，只有显式加 `--force` 才会覆盖；`index` 的 `--force` 只解除"人工内容保护"，不改变其他生成逻辑。

**Q6：在非 Trae 平台能用吗？**
能。治理文件（`AGENTS.md` 等）是业界通用约定，CLI 仅依赖 Python 标准库。差异仅在"自动 Skill 发现/加载"机制，其他平台可能需要手动接入 `SKILL.md` 或 `AGENTS.md`。

**Q7：`index` 生成的目录树里有些目录不想显示，怎么排除？**
默认已跳过 `.git`、`node_modules`、`venv`、`__pycache__` 等常见目录（见 `governance.py` 的 `SKIP_DIRS`），并排除所有以 `.` 开头的隐藏文件/目录。如需自定义，可修改 `SKIP_DIRS` 集合。

**Q8：多项目怎么管理？**
每个项目独立初始化一份治理工作区即可。治理文件是项目级的，互不干扰。

## 许可证

MIT-0
