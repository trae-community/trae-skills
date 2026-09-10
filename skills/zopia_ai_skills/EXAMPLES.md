# Conversation Examples

Practical examples of multi-turn Agent conversations and video generation best practices.

## Multi-turn Conversation: Screenplay -> Characters -> Storyboard

### Round 1: Generate Screenplay

Do not pass `session_id` on the first call. The response returns a `session_id` for subsequent calls.

```bash
curl -X POST "https://zopia.ai/api/v1/agent/chat" \
  -H "Authorization: Bearer zopia-xxxx" \
  -H "Content-Type: application/json" \
  -d '{"base_id":"base_xxx","message":"Please generate a three-act screenplay on a campus youth theme"}'
```

### Round 2: Generate Character Designs

Use the `session_id` returned from the previous response.

```bash
curl -X POST "https://zopia.ai/api/v1/agent/chat" \
  -H "Authorization: Bearer zopia-xxxx" \
  -H "Content-Type: application/json" \
  -d '{"base_id":"base_xxx","session_id":"session_xxx","message":"Please generate detailed character designs for the main characters, including design illustrations"}'
```

### Round 3: Generate Storyboard

```bash
curl -X POST "https://zopia.ai/api/v1/agent/chat" \
  -H "Authorization: Bearer zopia-xxxx" \
  -H "Content-Type: application/json" \
  -d '{"base_id":"base_xxx","session_id":"session_xxx","message":"Please generate a storyboard for Act 1, listing all shots with their framing and descriptions"}'
```

## Video Generation Best Practices

**Video generation is expensive. Always confirm the number of shots with the user before generating. Never generate all shots at once.**

### Recommended flow:

1. After storyboarding completes, check `workspace.files[].record_count` for the total number of shots
2. Ask the user how many shots to generate and which range
3. Generate in batches of 3-5 shots

### Batch Generation

```bash
# Generate first batch (shots 1-3)
curl -X POST "https://zopia.ai/api/v1/agent/chat" \
  -H "Authorization: Bearer zopia-xxxx" \
  -H "Content-Type: application/json" \
  -d '{"base_id":"base_xxx","session_id":"session_xxx","message":"Start generating videos for shot1 through shot3"}'

# Continue with next batch (shots 4-6)
curl -X POST "https://zopia.ai/api/v1/agent/chat" \
  -H "Authorization: Bearer zopia-xxxx" \
  -H "Content-Type: application/json" \
  -d '{"base_id":"base_xxx","session_id":"session_xxx","message":"Continue generating shots 4 through 6"}'
```

### Regenerate a Specific Shot

```bash
curl -X POST "https://zopia.ai/api/v1/agent/chat" \
  -H "Authorization: Bearer zopia-xxxx" \
  -H "Content-Type: application/json" \
  -d '{"base_id":"base_xxx","session_id":"session_xxx","message":"Please regenerate the video for shot 2, change the camera movement to a slow push-in"}'
```

## End-to-End Quick Start

```bash
# 1. Create project
curl -X POST "https://zopia.ai/api/base/create" \
  -H "Authorization: Bearer zopia-xxxx" \
  -H "Content-Type: application/json" \
  -d '{"baseName":"Agent Demo","lang":"zh-CN"}'

# 2. Save settings (locale, aspect_ratio, style are required)
curl -X POST "https://zopia.ai/api/base/settings" \
  -H "Authorization: Bearer zopia-xxxx" \
  -H "Content-Type: application/json" \
  -d '{"base_id":"base_xxx","settings":{"locale":"zh-CN","aspect_ratio":"16:9","style":"anime_japanese_korean","generation_method":"n_grid"}}'

# 3. Chat with Agent
curl -X POST "https://zopia.ai/api/v1/agent/chat" \
  -H "Authorization: Bearer zopia-xxxx" \
  -H "Content-Type: application/json" \
  -d '{"base_id":"base_xxx","message":"Please generate a three-act campus-themed screenplay"}'
```
