# Zopia AI Skills

> **AI 驱动的视频制作平台** -- 从剧本到成片，用自然语言对话完成全流程制作。

中文 | [English](./README.md)

---

## Zopia 是什么？

[Zopia](https://zopia.ai) 是一个 AI 驱动的视频制作平台。通过 API，你可以创建项目、配置视觉风格，然后与智能 Agent 进行对话，Agent 会**自动**完成完整的制作流程：

```
剧本创作 -> 角色设计 -> 分镜绘制 -> 视频生成
```

各阶段之间无需人工干预 -- 只需用自然语言描述你的创意构想，Agent 会自动调度每一个环节。

## 核心特性

- **自然语言驱动** -- 用日常语言描述故事，Agent 自动将其转化为专业制作流程
- **全流程覆盖** -- 涵盖剧本、角色设计、分镜关键帧、视频片段的端到端制作
- **多轮对话** -- 通过持续对话进行迭代和优化，支持会话持久化
- **多种视觉风格** -- 内置 9 种风格，从日系动漫到写实风格、像素风到皮克斯 3D
- **多种视频模型** -- 支持 9 种视频生成模型，包括 Kling O3、Vidu Q3 Pro、Seedance 1.5 等
- **灵活配置** -- 画面比例、分辨率、生成方式、视觉风格均可按项目配置
- **批量视频生成** -- 可控的分批生成（每批 3-5 个镜头），便于控制成本
- **积分系统** -- 通过 API 查询余额和跟踪用量

## 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                      Zopia 平台                          │
│                                                         │
│  ┌─────────┐    ┌──────────────────────────────────┐    │
│  │  你的   │───>│          Agent（AI 核心）          │    │
│  │  应用   │<───│                                   │    │
│  └─────────┘    │  ┌──────────────┐ ┌────────────┐ │    │
│    REST API     │  │   剧本创作    │ │  角色设计   │ │    │
│                 │  │   Writer     │ │  Designer  │ │    │
│                 │  └──────────────┘ └────────────┘ │    │
│                 │  ┌──────────────┐ ┌────────────┐ │    │
│                 │  │   分镜绘制    │ │  视频生成   │ │    │
│                 │  │   Artist     │ │  Producer  │ │    │
│                 │  └──────────────┘ └────────────┘ │    │
│                 └──────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

Agent 内部调度四个专业工具：

| 工具 | 职能 |
|------|------|
| `screenplay_writer` | 生成包含幕和场景的结构化剧本 |
| `character_designer` | 创建详细的角色设计，附带视觉设计图 |
| `storyboard_artist` | 制作分镜关键帧，逐镜头分解 |
| `video_producer` | 根据分镜画面生成视频片段 |

## 工作流程

```
1. 创建项目
       │
       v
2. 保存设置（locale、aspect_ratio、style）
       │
       v
3. Agent 对话（多轮）
   ├── "写一个关于...的剧本"        --> screenplay_writer
   ├── "设计主要角色..."            --> character_designer
   ├── "为第一幕创建分镜"           --> storyboard_artist
   └── "生成第 1-3 个镜头的视频"    --> video_producer
       │
       v
4. 在 https://zopia.ai/base/{project_id} 查看成果
```

## 快速开始

### 1. 获取 API Token

访问 [zopia.ai/settings/api-tokens](https://zopia.ai/settings/api-tokens)，登录后点击 **"Generate New Token"**。

- 格式：`zopia-xxxxxxxxxxxx`
- 有效期：30 天

### 2. 创建项目

```bash
curl -X POST "https://zopia.ai/api/base/create" \
  -H "Authorization: Bearer zopia-xxxx" \
  -H "Content-Type: application/json" \
  -d '{"baseName": "我的第一个视频", "lang": "zh-CN"}'
```

### 3. 配置项目设置

```bash
curl -X POST "https://zopia.ai/api/base/settings" \
  -H "Authorization: Bearer zopia-xxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "base_id": "base_xxx",
    "settings": {
      "locale": "zh-CN",
      "aspect_ratio": "16:9",
      "style": "anime_japanese_korean",
      "generation_method": "n_grid"
    }
  }'
```

### 4. 与 Agent 对话

```bash
# 第一轮：生成剧本（无需传 session_id）
curl -X POST "https://zopia.ai/api/v1/agent/chat" \
  -H "Authorization: Bearer zopia-xxxx" \
  -H "Content-Type: application/json" \
  -d '{"base_id": "base_xxx", "message": "请生成一个三幕式的校园青春主题剧本"}'

# 第二轮：设计角色（使用第一轮返回的 session_id）
curl -X POST "https://zopia.ai/api/v1/agent/chat" \
  -H "Authorization: Bearer zopia-xxxx" \
  -H "Content-Type: application/json" \
  -d '{"base_id": "base_xxx", "session_id": "session_xxx", "message": "请为主要角色生成详细的角色设计，包含设计图"}'

# 第三轮：绘制分镜
curl -X POST "https://zopia.ai/api/v1/agent/chat" \
  -H "Authorization: Bearer zopia-xxxx" \
  -H "Content-Type: application/json" \
  -d '{"base_id": "base_xxx", "session_id": "session_xxx", "message": "请为第一幕生成分镜，列出所有镜头的景别和描述"}'

# 第四轮：分批生成视频
curl -X POST "https://zopia.ai/api/v1/agent/chat" \
  -H "Authorization: Bearer zopia-xxxx" \
  -H "Content-Type: application/json" \
  -d '{"base_id": "base_xxx", "session_id": "session_xxx", "message": "开始生成第 1 到第 3 个镜头的视频"}'
```

## API 接口一览

### 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/base/create` | 创建新项目 |
| `POST` | `/api/base/settings` | 保存项目设置 |
| `GET`  | `/api/base/settings?base_id=xxx` | 读取当前设置 |
| `POST` | `/api/v1/agent/chat` | 与 AI Agent 对话 |
| `GET`  | `/api/base/list` | 列出所有项目 |
| `GET`  | `/api/base/{id}` | 获取项目详情 |
| `GET`  | `/api/billing/getBalance` | 查询积分余额 |

基础地址：`https://zopia.ai`

所有请求需要在 Header 中携带：
```
Authorization: Bearer <TOKEN>
```

完整的请求/响应格式请参阅 [API_REFERENCE.md](./API_REFERENCE.md)。

## 配置选项

### 视觉风格

| 风格 ID | 说明 |
|---------|------|
| `anime_japanese_korean` | 日系动漫风格 |
| `realistic_3d_cg` | 高精度 3D CG 写实 |
| `pixar_3d_cartoon` | 皮克斯 3D 卡通 |
| `photorealistic_real_human` | 照片级写实真人 |
| `3D_CG_Animation` | 3D CG 动画 / 国风 |
| `anime_chibi` | Q版 / 萌系风格 |
| `anime_shinkai` | 新海诚风格 |
| `anime_ghibli` | 吉卜力风格 |
| `stylized_pixel` | 像素风 |

### 视频模型

| 模型 | ID | 推荐生成方式 |
|------|----|-------------|
| Kling O3 *（推荐）* | `generate_video_by_kling_o3` | `n_grid`、`multi_ref`、`multi_ref_v2` |
| Vidu Q3 Pro *（推荐）* | `generate_video_by_viduq3_pro` | `n_grid` |
| Kling v3.0 | `generate_video_by_kling_v3_0` | `n_grid` |
| Seedance 1.5 | `generate_video_by_seedance_15` | `start_frame` |
| Vidu Q2 Pro | `generate_video_by_viduq2_pro` | `start_frame` |
| Hailuo 02 | `generate_video_by_hailuo_02` | `start_frame` |
| Kling v2.6 Pro | `generate_video_by_kling_v26_pro` | `start_frame` |
| Wan 2.6 I2V | `generate_video_by_wan26_i2v` | `start_frame` |
| Wan 2.6 Flash | `generate_video_by_wan26_i2v_flash` | `start_frame` |

### 生成方式

| 方式 | 说明 |
|------|------|
| `n_grid` *（推荐）* | 多帧网格 -- AI 自动规划关键帧序列，视觉连续性好 |
| `multi_ref` | 多参考 v1 -- 使用多张参考图驱动视频（仅限 Kling O3） |
| `multi_ref_v2` | 多参考 v2 -- 改进版本（仅限 Kling O3） |
| `start_frame` | 首帧驱动 -- 使用关键帧作为起始帧，精准控制第一帧 |

### 分辨率选项

| 设置 | 可选值 | 默认值 |
|------|--------|--------|
| 关键帧（`image_size`） | `1K`、`2K`、`4K` | `2K` |
| 视频（`video_resolution`） | `480p`、`720p`、`1080p` | `480p` |
| 画面比例（`aspect_ratio`） | `16:9`（横屏）、`9:16`（竖屏） | -- |

## 多轮会话管理

- **首次调用**：不传 `session_id`，响应会返回一个生成的 `session_id`
- **后续调用**：传入 `session_id` 继续同一会话
- **新建会话**：再次不传 `session_id` 即可开启新对话
- **并发限制**：每个 `session_id` 同一时间只允许一个请求，忙碌时返回 `409`

## 最佳实践

1. **务必先配置设置** -- `locale`、`aspect_ratio` 和 `style` 是与 Agent 对话前的必填项
2. **生成视频前确认镜头数** -- 视频生成消耗较多资源，在分镜完成后检查 `workspace.files[].record_count` 获取总镜头数
3. **分批生成视频** -- 每批 3-5 个镜头，便于控制成本和在批次间进行审查
4. **优先使用 `n_grid` 生成方式** -- 提供最佳的镜头间视觉连续性
5. **等待响应完成** -- 图片和视频生成可能较慢，务必等待完成后再发送下一个请求

## 错误码

| 状态码 | 含义 |
|--------|------|
| `400` | 参数错误或缺少必填设置 |
| `401` | 未认证或 Token 已过期 |
| `402` | 积分不足 |
| `403` | 无权限（非项目所有者） |
| `404` | 资源未找到 |
| `409` | 会话忙碌 -- 上一个请求仍在处理中 |

## 文档索引

| 文件 | 说明 |
|------|------|
| [SKILL.md](./SKILL.md) | Skill 描述与概览 |
| [API_REFERENCE.md](./API_REFERENCE.md) | 完整的 API 请求/响应格式 |
| [SETTINGS_REFERENCE.md](./SETTINGS_REFERENCE.md) | 所有有效的配置值 |
| [EXAMPLES.md](./EXAMPLES.md) | 对话示例与最佳实践 |

## 相关链接

- **平台地址**：[https://zopia.ai](https://zopia.ai)
- **API Token 管理**：[https://zopia.ai/settings/api-tokens](https://zopia.ai/settings/api-tokens)

## 许可证

详见 [LICENSE](../LICENSE) 文件。
