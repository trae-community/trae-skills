# 箱熵 API 使用参考

基础地址：`https://xiangshang.ngrok.app`

公开 API 无需密钥，支持中英文查询。以下示例针对2026-09-02复验的 API 2.0.0；接口行为
变化时，以在线 OpenAPI 文档为准。

## 搜索知识库

`POST /api/search`

```bash
curl --fail-with-body --silent --show-error \
  --max-time 60 \
  -X POST "https://xiangshang.ngrok.app/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "移动操作机器人的导航与抓取规划",
    "scope": "all",
    "top_k": 10,
    "mode": "hybrid",
    "rerank": false
  }'
```

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `query` | 是 | 自然语言需求或技术术语 |
| `scope` | 否 | 检索范围，默认 `all` |
| `top_k` | 否 | 返回数量，默认20 |
| `mode` | 否 | 检索模式，默认 `hybrid` |
| `rerank` | 否 | 是否精排，默认 `false` |

响应包含 `query` 和由服务定义的 `results` 对象。选择候选前先查看各结果分组和嵌套的
`record`。

响应结构速览（实测 /api/search，字段以在线 Schema 为准）：

- `results` 按三个作用域分组：`assets`（实现资产）、`caps`（能力）、`topics`（主题），
  每个命中包含 `record`、`matched`（vec/lex/graph）和 `score`；
- `chains`：检索命中的能力子图（锚点 + 层级/依赖边），用于理解能力间结构关系；
- `dup_folded` / `dup_of` / `dup_group`：折叠去重相关——同一能力可能以多条记录出现，
  呈现时按实体去重，不要重复计数；
- `low_confidence` 为 true、或 `record.provenance` 为 `generated`、来源带 `[待核查]` 时，
  该记录置信度低，引用前必须用上游来源复核，并向用户标注“已核验 / 待核查”。
- `score` / `rerank_score` 是排序分，不是事实置信度。

## 检索证据

`POST /api/evidence/search`

```bash
curl --fail-with-body --silent --show-error \
  --max-time 60 \
  -X POST "https://xiangshang.ngrok.app/api/evidence/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "机器人动态避障算法的工程对比",
    "top_k": 5,
    "mode": "hybrid",
    "rerank": true
  }'
```

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `query` | 是 | 自然语言问题或技术概念 |
| `topic` | 否 | 可选主题限制 |
| `top_k` | 否 | 返回数量，默认10 |
| `mode` | 否 | 检索模式，默认 `hybrid` |
| `rerank` | 否 | 是否精排，默认 `true` |

响应包含 `query`、`results` 数组和 `latency_ms`。引用结果时保留来源字段，不要把分数
当成证据。

## 查询实体

优先使用 `POST /api/lookup`。

```bash
curl --fail-with-body --silent --show-error \
  --max-time 60 \
  -X POST "https://xiangshang.ngrok.app/api/lookup" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "CAP_8a7a03ae",
    "format": "json"
  }'
```

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `query` | 是 | 关键词、中文名、`CAP_...` 或 `AST_...` |
| `type` | 否 | `topic`、`cap` 或 `asset` |
| `format` | 否 | `json` 或 `md`，默认 `json` |
| `list` | 否 | 是否返回候选列表 |
| `first` | 否 | 是否选择第一个精确或排序候选 |

响应可能包含 `found`、`query`、`entity_type`、`record`、`markdown` 和 `candidates`。
主题查询可能只返回摘要信息，不会批量返回完整主题内容。

调用精确 `CAP_...` 或 `AST_...` ID 时可以省略 `type`，由 ID 前缀自动识别实体类型。
这也是不同部署版本之间兼容性更好的调用方式。

注意：Lookup 的精确匹配对中文自然短语（如“柔性控制”“柔顺控制”）不保证命中，可能返回
`found: false` 或空候选列表。这不代表图谱里没有该概念——此时应改用 `/api/search`
再次确认。优先用精确 ID 或英文/技术别名调 Lookup。

## 生成候选工作流

`POST /api/consult`

```bash
curl --fail-with-body --silent --show-error \
  --max-time 200 \
  -X POST "https://xiangshang.ngrok.app/api/consult" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "为使用二维激光雷达的 ROS 2 差速移动机器人设计仿真优先的避障研发流程，控制周期不超过50毫秒，不依赖云端服务。",
    "top_k": 30,
    "rerank": true,
    "brief": false
  }'
```

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `question` | 是 | 完整工程问题和约束 |
| `top_k` | 否 | 10至100条候选，默认30 |
| `rerank` | 否 | 是否精排，默认 `true` |
| `prev_context` | 否 | 多轮设计中的前序结论 |
| `brief` | 否 | 是否只返回简要链路骨架，默认 `false` |

响应可能包含 `question`、`pool`、`task_steps`、`synthesis` 和 `latency_ms`。正常请求可能
需要30至180秒。返回的是候选工作流，必须继续核验证据、接口与用户约束。

`synthesis` 是可视化就绪的链路结构（由后端 integrate_planner 组装，即“LLM 返回后的
组装/可视化层”）：

- `mode`：`chains`（任务链方案）或 `nodes_only`（能力/资产清单与缺口）；
- `chains`：任务链列表，每条由步骤组成，步骤携带 `caps`（真实能力 ID 节点），允许分支
  与合并；可直接渲染为任务链图；
- `proposed_capabilities`：LLM 提议、尚未在注册表定义的新能力（`NEW_CAP_*`）；
- `gap_annotations` / `summary` / `completeness`：能力拥有/缺口统计与完整度；
- `explanation` / `warnings`：方案说明与告警（如“LLM 装配失败已回退”“能力引用全幻觉”）。

`brief=true` 时 `synthesis` 只保留 `mode` 与每条链的 `name`/`n_steps` 骨架。

## 运行要求

- 使用 `Content-Type: application/json`。
- 明确设置超时；Consult 至少180秒。
- 记录请求参数和返回的实体 ID，但不要记录无关凭据或项目隐私信息。
- 不要自动重复调用 Consult。
- API 版本变化后重新检查在线 Schema 和集成说明。

