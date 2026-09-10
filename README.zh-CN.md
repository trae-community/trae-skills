# TRAE Agent Skills

![TRAE Skills Banner](./assets/image/Skills.gif)

[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

TRAE 社区维护的 Agent Skills 仓库。

[English README](./README.md)

## 快速开始

1. 克隆本仓库到本地。
2. 将技能放到 TRAE 约定目录：
   - 项目技能：`.trae/skills/<skill-name>/SKILL.md`
   - 全局技能：`~/.trae/skills/<skill-name>/SKILL.md`
3. 在 TRAE 设置中刷新技能发现（不同版本的 TRAE 入口位置可能略有差异）。
4. 用自然语言提出与某个技能描述匹配的请求，例如：
   - "使用 git-commit-generator 技能，为当前变更生成提交信息。"
   - "使用 cn-punctuation-checker 技能，检查这份文档的中文标点。"

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

创建技能时，请使用[技能模板](skills/_template/SKILL.md)，并参阅[贡献指南](CONTRIBUTING.zh-CN.md)。

## 技能目录

| 技能 | 描述 | 使用场景 | 状态 |
| --- | --- | --- | --- |
| [daily-trend-writer](skills/daily-trend-writer/SKILL.md) | 全自动化的公众号内容生产流水线。每日发现实用工具、社区热点、教程经验等"小而美"选题，深挖后输出"咪蒙风格"与"技术干货"两篇高质量公众号文章。 | 内容创作, 公众号运营, 热点分析 | Stable |
| [git-commit-generator](skills/git-commit-generator/SKILL.md) | 根据代码变更（diffs）生成标准化、符合 Conventional Commits 规范的 git 提交信息。 | Git 操作, 代码评审 | Stable |
| [cn-punctuation-checker](skills/cn-punctuation-checker/SKILL.md) | 检查中文文案中错误使用的英文标点符号，并支持批量修复。 | 中文文案润色, 标点纠错 | Stable |
| [wechat-mini-program-development](skills/wechat-mini-program-development/SKILL.md) | 微信小程序开发专用技能，提供标准项目结构、请求封装和 API 管理。 | 微信小程序开发, 项目脚手架 | Stable |
| [kz-article-deep-analysis](skills/kz-article-deep-analysis/SKILL.md) | 深度解读非学术类文章（博客、随笔、评论），输出结构化分析报告（核心议题、核心主张、论证拓扑、认知增量）。 | 深度阅读, 文章分析 | Stable |
| [video-to-keyframes](skills/video-to-keyframes/SKILL.md) | 抽取视频帧、检测转场与分段、筛选候选关键帧，并生成可复筛的 HTML 画廊。 | 视频分析, 关键帧筛选, 分镜初筛 | Stable |
| [web-design-teroop](skills/web-design-teroop/SKILL.md) | 为新前端项目提供全面的设计指导，涵盖风格、Logo、图标和动画设计。 | 新项目, Web 设计, UI/UX, 品牌设计 | Stable |
| [entropy-box-zh](skills/entropy-box-zh/SKILL.md) | 以箱熵（Entropy Box）具身智能全景图与知识编译器为核心，把边界明确的具身智能技术需求转化为候选实现方法与有依据的工程工作流；支持全景定位、能力依赖分析、资产选型与证据核验。 | 具身智能研发, 技术全景分析, 能力分解, 依赖分析, 资产选型, 知识缺口分析 | Stable |
| [cloudbase](skills/cloudbase/SKILL.md) | 在 Trae 中进行腾讯云开发（CloudBase）开发：优先 MCP 工具，覆盖 Web / 微信小程序、登录鉴权、数据库、云函数、云托管、云存储与内置 AI。 | 云开发, CloudBase, Web, 小程序, Serverless | Stable |
| [project-governance](skills/project-governance/SKILL.md) | AI 辅助开发的项目治理工作区——项目协议（规则、权限、自主权等级）、目录索引、错误档案、会话交接、变更日志、稳定版本索引，以及 whitelist/blacklist 参数注册表，附带 scaffold/validate/index/check CLI。 | 项目搭建, AI Agent 接入, 参数版本管理, 项目治理 | Stable |
| [cycle-delivery](skills/cycle-delivery/SKILL.md) | 通过本地 MCP 控制平面进行证据门禁式软件交付：不可变请求、双盲评审、仲裁批准与字节级 Git 交付。需从项目 GitHub Release 安装 trae-cycle 二进制。 | 软件交付, 代码评审, 流程治理, Git | Stable |
| [docx-diff-comment](skills/docx-diff-comment/SKILL.md) | 对比两份 Word 文档差异，在新版本中对新增功能点添加批注，并生成新增需求人天估算表。 | 文档对比, Word 批注, 需求估算 | Stable |

## 贡献指南

请参阅 [CONTRIBUTING.zh-CN.md](./CONTRIBUTING.zh-CN.md)。

## License

见 [LICENSE](./LICENSE)。

## 免责声明

本仓库中的技能为社区/学习用途提供。请在你自己的环境中审阅并充分测试后再用于生产或安全敏感场景。

## 链接

- TRAE 官网：https://www.trae.cn/
- TRAE 技能文档：https://docs.trae.ai/ide/skills?_lang=zh
