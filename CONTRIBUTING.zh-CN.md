# 贡献指南

欢迎提交 PR。建议把每个技能做到“小而专”，并确保容易验证。

## 创建新技能

1.  将模板从 `skills/_template/` 复制到 `skills/<your-skill-name>/`。
2.  更新 `SKILL.md` 中的技能逻辑。
3.  添加必要的资源或示例。

## 质量要求（Quality bar）

- 结构清晰：说明“做什么/何时用/如何做”，并包含可执行步骤与示例
- 不要包含敏感信息：密钥、Token、内网地址、客户数据等
- 命令可复制粘贴、默认安全（避免破坏性操作）
- 尽量输出可复用的结构化结果（模板、清单、固定格式）
- 优先使用英文编写 Skill，如果特殊情况需要使用其他语言，请在 PR 时说明

## 命名约定

- 目录名必须与 frontmatter 的 `name` 一致
- 使用 `lowercase-hyphenated` 风格命名
- 避免含糊的名字（例如 `misc`、`helpers`）

## PR 自检清单

- 存在 `skills/<skill-name>/SKILL.md`，且 frontmatter 包含 `name`、`description`
- 至少包含 1 个使用示例
- 若引用目录内文件，使用相对路径链接
- License 与本仓库 LICENSE 兼容（或在技能内明确单独 License）
- 在 `README.zh-CN.md` 的 **技能目录** 中更新你的新技能
- 提交前请务必在 Trae 客户端中加载并验证该 Skill，确保功能符合预期
- 建议在 PR 中附带运行截图
