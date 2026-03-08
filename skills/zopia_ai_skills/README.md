# Zopia AI Skills

> **AI-Driven Video Production Platform** -- From screenplay to finished video, powered by natural language conversations.

[中文文档](./README_CN.md) | English

---

## What is Zopia?

[Zopia](https://zopia.ai) is an AI-driven video production platform. Through its API, you can create projects, configure visual styles, and then converse with an intelligent Agent that **automatically** handles the full production pipeline:

```
Screenplay Writing -> Character Design -> Storyboard Illustration -> Video Generation
```

No manual intervention is needed between stages -- simply describe your creative vision in natural language, and the Agent orchestrates every step.

## Key Features

- **Natural Language Driven** -- Describe your story in plain language; the Agent translates it into a professional production pipeline
- **Full Production Pipeline** -- Covers screenplay, character design, storyboard keyframes, and video clips end-to-end
- **Multi-Turn Conversations** -- Iterate and refine through continuous dialogue with session persistence
- **Multiple Visual Styles** -- 9 built-in styles from Japanese anime to photorealistic, pixel art to Pixar 3D
- **Multiple Video Models** -- 9 video generation models including Kling O3, Vidu Q3 Pro, Seedance 1.5, and more
- **Flexible Configuration** -- Aspect ratio, resolution, generation method, and style are all configurable per project
- **Batch Video Generation** -- Generate video clips in controllable batches of 3-5 shots to manage costs
- **Credit System** -- Query balance and track usage via API

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Zopia Platform                     │
│                                                         │
│  ┌─────────┐    ┌──────────────────────────────────┐    │
│  │  Your   │───>│          Agent (AI Core)          │    │
│  │  App    │<───│                                   │    │
│  └─────────┘    │  ┌──────────────┐ ┌────────────┐ │    │
│    REST API     │  │ Screenplay   │ │ Character  │ │    │
│                 │  │ Writer       │ │ Designer   │ │    │
│                 │  └──────────────┘ └────────────┘ │    │
│                 │  ┌──────────────┐ ┌────────────┐ │    │
│                 │  │ Storyboard   │ │   Video    │ │    │
│                 │  │ Artist       │ │ Producer   │ │    │
│                 │  └──────────────┘ └────────────┘ │    │
│                 └──────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

The Agent internally dispatches four specialized tools:

| Tool | Role |
|------|------|
| `screenplay_writer` | Generates structured screenplays with acts and scenes |
| `character_designer` | Creates detailed character designs with visual illustrations |
| `storyboard_artist` | Produces keyframe storyboards with shot-by-shot breakdowns |
| `video_producer` | Generates video clips from storyboard frames |

## Workflow

```
1. Create Project
       │
       v
2. Save Settings (locale, aspect_ratio, style)
       │
       v
3. Agent Chat (multi-turn)
   ├── "Write a screenplay about..."  --> screenplay_writer
   ├── "Design the characters..."     --> character_designer
   ├── "Create storyboard for Act 1"  --> storyboard_artist
   └── "Generate videos for shots 1-3"--> video_producer
       │
       v
4. View Results on https://zopia.ai/base/{project_id}
```

## Quick Start

### 1. Get Your API Token

Visit [zopia.ai/settings/api-tokens](https://zopia.ai/settings/api-tokens), log in, and click **"Generate New Token"**.

- Format: `zopia-xxxxxxxxxxxx`
- Validity: 30 days

### 2. Create a Project

```bash
curl -X POST "https://zopia.ai/api/base/create" \
  -H "Authorization: Bearer zopia-xxxx" \
  -H "Content-Type: application/json" \
  -d '{"baseName": "My First Video", "lang": "en"}'
```

### 3. Configure Settings

```bash
curl -X POST "https://zopia.ai/api/base/settings" \
  -H "Authorization: Bearer zopia-xxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "base_id": "base_xxx",
    "settings": {
      "locale": "en",
      "aspect_ratio": "16:9",
      "style": "anime_japanese_korean",
      "generation_method": "n_grid"
    }
  }'
```

### 4. Chat with the Agent

```bash
# Round 1: Generate screenplay (no session_id needed)
curl -X POST "https://zopia.ai/api/v1/agent/chat" \
  -H "Authorization: Bearer zopia-xxxx" \
  -H "Content-Type: application/json" \
  -d '{"base_id": "base_xxx", "message": "Generate a three-act screenplay about a campus love story"}'

# Round 2: Design characters (use session_id from Round 1 response)
curl -X POST "https://zopia.ai/api/v1/agent/chat" \
  -H "Authorization: Bearer zopia-xxxx" \
  -H "Content-Type: application/json" \
  -d '{"base_id": "base_xxx", "session_id": "session_xxx", "message": "Design the main characters with illustrations"}'

# Round 3: Create storyboard
curl -X POST "https://zopia.ai/api/v1/agent/chat" \
  -H "Authorization: Bearer zopia-xxxx" \
  -H "Content-Type: application/json" \
  -d '{"base_id": "base_xxx", "session_id": "session_xxx", "message": "Create a storyboard for Act 1 with all shots"}'

# Round 4: Generate videos in batches
curl -X POST "https://zopia.ai/api/v1/agent/chat" \
  -H "Authorization: Bearer zopia-xxxx" \
  -H "Content-Type: application/json" \
  -d '{"base_id": "base_xxx", "session_id": "session_xxx", "message": "Generate videos for shots 1 through 3"}'
```

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/base/create` | Create a new project |
| `POST` | `/api/base/settings` | Save project settings |
| `GET`  | `/api/base/settings?base_id=xxx` | Read current settings |
| `POST` | `/api/v1/agent/chat` | Chat with the AI Agent |
| `GET`  | `/api/base/list` | List all projects |
| `GET`  | `/api/base/{id}` | Get project details |
| `GET`  | `/api/billing/getBalance` | Query credit balance |

Base URL: `https://zopia.ai`

All requests require the header:
```
Authorization: Bearer <TOKEN>
```

For complete request/response schemas, see [API_REFERENCE.md](./API_REFERENCE.md).

## Configuration Options

### Visual Styles

| Style ID | Description |
|----------|-------------|
| `anime_japanese_korean` | Japanese anime style |
| `realistic_3d_cg` | High-detail 3D CG realistic |
| `pixar_3d_cartoon` | Pixar 3D cartoon |
| `photorealistic_real_human` | Photorealistic real human |
| `3D_CG_Animation` | 3D CG animation / Chinese style |
| `anime_chibi` | Chibi / cute style |
| `anime_shinkai` | Makoto Shinkai style |
| `anime_ghibli` | Studio Ghibli style |
| `stylized_pixel` | Pixel art |

### Video Models

| Model | ID | Recommended Methods |
|-------|----|---------------------|
| Kling O3 *(recommended)* | `generate_video_by_kling_o3` | `n_grid`, `multi_ref`, `multi_ref_v2` |
| Vidu Q3 Pro *(recommended)* | `generate_video_by_viduq3_pro` | `n_grid` |
| Kling v3.0 | `generate_video_by_kling_v3_0` | `n_grid` |
| Seedance 1.5 | `generate_video_by_seedance_15` | `start_frame` |
| Vidu Q2 Pro | `generate_video_by_viduq2_pro` | `start_frame` |
| Hailuo 02 | `generate_video_by_hailuo_02` | `start_frame` |
| Kling v2.6 Pro | `generate_video_by_kling_v26_pro` | `start_frame` |
| Wan 2.6 I2V | `generate_video_by_wan26_i2v` | `start_frame` |
| Wan 2.6 Flash | `generate_video_by_wan26_i2v_flash` | `start_frame` |

### Generation Methods

| Method | Description |
|--------|-------------|
| `n_grid` *(recommended)* | Multi-frame grid -- AI auto-plans keyframe sequence with good visual continuity |
| `multi_ref` | Multi-reference v1 -- uses multiple reference images (Kling O3 only) |
| `multi_ref_v2` | Multi-reference v2 -- improved version (Kling O3 only) |
| `start_frame` | Start-frame driven -- uses keyframe as the first frame for precise control |

### Resolution Options

| Setting | Options | Default |
|---------|---------|---------|
| Keyframe (`image_size`) | `1K`, `2K`, `4K` | `2K` |
| Video (`video_resolution`) | `480p`, `720p`, `1080p` | `480p` |
| Aspect Ratio (`aspect_ratio`) | `16:9`, `9:16` | -- |

## Multi-Turn Session Management

- **First call**: Omit `session_id`. The response returns a generated `session_id`.
- **Subsequent calls**: Pass the `session_id` to continue the same conversation.
- **New conversation**: Omit `session_id` again to start fresh.
- **Concurrency**: Only one request per `session_id` at a time. Returns `409` if busy.

## Best Practices

1. **Always configure settings first** -- `locale`, `aspect_ratio`, and `style` are required before chatting with the Agent
2. **Confirm shot count before generating videos** -- Video generation is resource-intensive; check `workspace.files[].record_count` after storyboarding
3. **Generate videos in batches** -- Use batches of 3-5 shots to manage costs and allow review between batches
4. **Use `n_grid` generation method** -- Provides the best visual continuity across shots
5. **Wait for responses** -- Image and video generation can be slow; always wait for completion before the next request

## Error Codes

| Code | Meaning |
|------|---------|
| `400` | Bad parameters or missing required settings |
| `401` | Unauthenticated or token expired |
| `402` | Insufficient credits |
| `403` | No permission (not project owner) |
| `404` | Resource not found |
| `409` | Session busy -- another request is still running |

## Documentation

| File | Description |
|------|-------------|
| [SKILL.md](./SKILL.md) | Skill description and overview |
| [API_REFERENCE.md](./API_REFERENCE.md) | Complete API request/response schemas |
| [SETTINGS_REFERENCE.md](./SETTINGS_REFERENCE.md) | All valid configuration values |
| [EXAMPLES.md](./EXAMPLES.md) | Conversation examples and best practices |

## Links

- **Platform**: [https://zopia.ai](https://zopia.ai)
- **API Tokens**: [https://zopia.ai/settings/api-tokens](https://zopia.ai/settings/api-tokens)

## License

See the [LICENSE](../LICENSE) file for details.
