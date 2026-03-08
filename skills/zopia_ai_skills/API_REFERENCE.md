# API Reference

Complete request/response schemas for all Zopia API endpoints.

## POST /api/base/create

Create a new project.

**Request**:

```json
{
  "baseName": "My Project",
  "lang": "zh-CN"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `baseName` | string | No | Project name (auto-generated if omitted) |
| `lang` | string | No | UI language: `zh-CN` or `en` (inferred from Accept-Language if omitted) |

**Response** (`201`):

```json
{
  "success": true,
  "data": {
    "baseId": "base_xxx",
    "baseName": "My Project"
  }
}
```

---

## POST /api/base/settings

Save project settings. Performs a shallow merge with existing settings, allowing incremental updates.

**Request**:

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

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `base_id` | string | Yes | Project ID |
| `settings` | object | Yes | Settings key-value pairs |

**Response**:

```json
{
  "success": true,
  "settings": {
    "locale": "zh-CN",
    "aspect_ratio": "16:9",
    "style": "anime_japanese_korean"
  }
}
```

---

## GET /api/base/settings

Read current project settings.

**Query Parameters**: `base_id` (required)

**Response**:

```json
{
  "success": true,
  "settings": {
    "locale": "zh-CN",
    "aspect_ratio": "16:9",
    "style": "anime_japanese_korean"
  }
}
```

---

## POST /api/v1/agent/chat

Chat with the project Agent. Returns the full result synchronously.

**Request**:

```json
{
  "base_id": "base_xxx",
  "message": "Please generate a three-act screenplay on a campus theme",
  "session_id": "session_xxx"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `base_id` | string | Yes | Project ID |
| `message` | string | Yes | Natural language instruction |
| `session_id` | string | No | Session ID for multi-turn conversation; omit to start new |

**Language rule**: Agent reply language follows `settings.locale`.

**Concurrency rule**: Only one request per `session_id` at a time. Returns `409` if a previous request is still running.

**Prerequisites**: `locale`, `aspect_ratio`, and `style` must be saved in project settings. Returns `400` with `missing_fields` if incomplete.

**Success Response**:

```json
{
  "success": true,
  "session_id": "session_xxx",
  "base_id": "base_xxx",
  "base_url": "https://zopia.ai/base/base_xxx",
  "reply": {
    "agent": "screenplay_writer",
    "text": "Agent's text reply"
  },
  "actions": [
    {
      "tool_name": "write_screenplay",
      "status": "success",
      "result": {
        "content": "...",
        "ui_display_content": "..."
      }
    }
  ],
  "workspace": {
    "files": [
      {
        "file_id": "file_xxx",
        "name": "Screenplay",
        "docu_type": "text",
        "record_count": 0
      }
    ]
  }
}
```

**Response fields**:

| Field | Description |
|-------|-------------|
| `reply.agent` | The Agent role that responded |
| `reply.text` | Agent's full text reply |
| `actions` | Tools invoked by the Agent and their results |
| `workspace.files` | Current file list with record counts per table |

**Error Response (settings incomplete)**:

```json
{
  "success": false,
  "error": "basic_settings_incomplete",
  "missing_fields": ["locale", "style"],
  "reference": {
    "locale": "Dialogue language, e.g.: en, zh-CN, ja",
    "aspect_ratio": "Aspect ratio: 16:9 | 9:16",
    "style": "Style ID: anime_japanese_korean | realistic_3d_cg | ..."
  }
}
```

---

## GET /api/base/list

List all projects for the current user, ordered by update time (newest first).

**Response**:

```json
{
  "success": true,
  "data": [
    {
      "id": "base_xxx",
      "name": "My Project",
      "thumbnails": ["https://..."],
      "createdAt": "2025-01-01T00:00:00.000Z",
      "updatedAt": "2025-01-02T00:00:00.000Z"
    }
  ]
}
```

---

## GET /api/base/{id}

Get project details including session list and settings.

**Response**:

```json
{
  "name": "My Project",
  "user_id": 123,
  "sessions": [
    {
      "id": "session_xxx",
      "title": "Campus Screenplay",
      "created_at": "...",
      "updated_at": "..."
    }
  ],
  "settings": {
    "locale": "zh-CN",
    "aspect_ratio": "16:9",
    "style": "anime_japanese_korean"
  },
  "profile": {
    "username": "user1",
    "image_url": "https://..."
  }
}
```

---

## GET /api/billing/getBalance

Query credit balance.

**Response**:

```json
{
  "accounts": [
    {
      "id": 1,
      "credit_type": "free",
      "balance": "100.00",
      "created_at": "...",
      "expires_at": "..."
    }
  ],
  "summary": {
    "totalBalance": 100.0,
    "totalHeld": 0.0,
    "totalAvailable": 100.0
  }
}
```
