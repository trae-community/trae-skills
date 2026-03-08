---
name: zopia-api
description: "Drive AI video production via the Zopia API: create projects, configure styles, chat with the Agent to generate screenplays/characters/storyboards/videos, and query project status and credits. Use when the user wants to create AI video projects or interact with the Zopia platform through its API."
---

# Zopia External Agent Skill

Zopia is an AI-driven video production platform. Through its API you can create projects, configure settings, then converse with the platform's built-in Agent, which automatically handles screenplay writing, character design, storyboard illustration, and video generation.

## Authentication

Guide the user to visit `https://zopia.ai/settings/api-tokens`, log in, and click "Generate New Token".

- Format: `zopia-xxxxxxxxxxxx`
- Validity: 30 days

Include in every request header:

```
Authorization: Bearer <TOKEN>
```

## Recommended Workflow

```
Create Project -> Save Settings (locale/style/aspect_ratio/generation_method) -> Multi-turn Agent Chat -> View Results
```

Agent chat is the core interaction. Describe your needs in natural language and the Agent will automatically dispatch tools to:
- Write screenplays (`screenplay_writer`)
- Design characters (`character_designer`)
- Draw storyboard keyframes (`storyboard_artist`)
- Generate video clips (`video_producer`)

**Multi-turn conversations**: Do not pass `session_id` on the first call; the response will return a generated `session_id`. Pass that `session_id` on subsequent calls to continue within the same session. Omitting `session_id` starts a new conversation.

## Core API Endpoints

### 1. Create Project

```
POST https://zopia.ai/api/base/create
```

Body: `{ "baseName": "My Project", "lang": "zh-CN" }`

Returns `baseId` used in all subsequent calls.

### 2. Save Settings (required before Agent chat)

```
POST https://zopia.ai/api/base/settings
```

Body:

```json
{
  "base_id": "base_xxx",
  "settings": {
    "locale": "zh-CN",
    "aspect_ratio": "16:9",
    "style": "anime_japanese_korean",
    "generation_method": "n_grid"
  }
}
```

**Three fields are required** before Agent chat: `locale`, `aspect_ratio`, `style`.
**Always pass `generation_method`** explicitly; server defaults to `n_grid` if omitted.

### 3. Agent Chat

```
POST https://zopia.ai/api/v1/agent/chat
```

Body:

```json
{
  "base_id": "base_xxx",
  "message": "Please generate a three-act screenplay on a campus theme",
  "session_id": "session_xxx"
}
```

- `base_id`: required
- `message`: required, natural language instruction
- `session_id`: optional, for continuing a conversation

**Concurrency**: Only one request per `session_id` at a time; returns `409` if another is still running.
**Latency**: Image, storyboard, and video generation can be slow. Wait for each response before sending the next request.

### 4. Other Endpoints

- `GET /api/base/settings?base_id=base_xxx` - Read current settings
- `GET /api/base/list` - List all projects (newest first)
- `GET /api/base/{id}` - Project details including sessions and settings
- `GET /api/billing/getBalance` - Query credit balance

For full API details, request bodies, and response schemas, see [API_REFERENCE.md](API_REFERENCE.md).
For all settings values (styles, video models, generation methods), see [SETTINGS_REFERENCE.md](SETTINGS_REFERENCE.md).
For conversation examples and video generation best practices, see [EXAMPLES.md](EXAMPLES.md).

## Video Generation Best Practices

**Video generation is expensive. Always confirm the number of shots with the user before generating. Never generate all shots at once.**

After storyboarding, use `workspace.files[].record_count` to get the shot count, ask the user which range to generate, then generate in batches of 3-5 shots.

## Error Codes

| Code | Meaning |
|------|---------|
| `400` | Bad parameters / missing settings |
| `401` | Unauthenticated or token expired |
| `402` | Insufficient credits |
| `403` | No permission (not project owner) |
| `404` | Resource not found |
| `409` | Session already running, retry later |

## Quick Start

```bash
# 1. Create project
curl -X POST "https://zopia.ai/api/base/create" \
  -H "Authorization: Bearer zopia-xxxx" \
  -H "Content-Type: application/json" \
  -d '{"baseName":"Agent Demo","lang":"zh-CN"}'

# 2. Save settings
curl -X POST "https://zopia.ai/api/base/settings" \
  -H "Authorization: Bearer zopia-xxxx" \
  -H "Content-Type: application/json" \
  -d '{"base_id":"base_xxx","settings":{"locale":"zh-CN","aspect_ratio":"16:9","style":"anime_japanese_korean","generation_method":"n_grid"}}'

# 3. Start chatting
curl -X POST "https://zopia.ai/api/v1/agent/chat" \
  -H "Authorization: Bearer zopia-xxxx" \
  -H "Content-Type: application/json" \
  -d '{"base_id":"base_xxx","message":"Please generate a three-act campus-themed screenplay"}'
```
