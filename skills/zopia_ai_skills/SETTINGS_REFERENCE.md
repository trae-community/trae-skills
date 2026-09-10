# Settings Reference

All valid values for Zopia project settings fields.

## Required Fields (must be set before Agent chat)

| Field | Description | Valid Values |
|-------|-------------|--------------|
| `locale` | Dialogue / output language | Any ISO language code. Common: `zh-CN`, `en`, `ja` |
| `aspect_ratio` | Frame aspect ratio | `16:9` (landscape), `9:16` (portrait) |
| `style` | Visual style | See Style List below |

## Optional Fields

| Field | Description | Valid Values | Default |
|-------|-------------|--------------|---------|
| `video_model` | Video generation model | See Video Model List below | `generate_video_by_kling_o3` |
| `generation_method` | Generation workflow | Depends on model, see below | `n_grid` |
| `image_size` | Keyframe resolution | `1K`, `2K`, `4K` | `2K` |
| `video_resolution` | Video resolution | `480p`, `720p`, `1080p` | `480p` |

## Style List (`style` values)

| ID | Description |
|----|-------------|
| `anime_japanese_korean` | Japanese anime style |
| `realistic_3d_cg` | High-detail 3D CG realistic |
| `pixar_3d_cartoon` | Pixar 3D cartoon |
| `photorealistic_real_human` | Photorealistic real human |
| `3D_CG_Animation` | 3D CG animation / Chinese style |
| `anime_chibi` | Chibi / cute style |
| `anime_shinkai` | Makoto Shinkai style |
| `anime_ghibli` | Studio Ghibli style |
| `stylized_pixel` | Pixel art |

## Video Model List (`video_model` values)

| `video_model` Value | Model Name | Supported `generation_method` |
|---------------------|-----------|-------------------------------|
| `generate_video_by_kling_o3` ⭐ | Kling O3 | `n_grid`, `multi_ref`, `multi_ref_v2` |
| `generate_video_by_viduq3_pro` ⭐ | Vidu Q3 Pro | `n_grid` |
| `generate_video_by_kling_v3_0` | Kling v3.0 | `n_grid` |
| `generate_video_by_seedance_15` | Seedance 1.5 | `start_frame` |
| `generate_video_by_viduq2_pro` | Vidu Q2 Pro | `start_frame` |
| `generate_video_by_hailuo_02` | Hailuo 02 | `start_frame` |
| `generate_video_by_kling_v26_pro` | Kling v2.6 Pro | `start_frame` |
| `generate_video_by_wan26_i2v` | Wan 2.6 I2V | `start_frame` |
| `generate_video_by_wan26_i2v_flash` | Wan 2.6 Flash | `start_frame` |

⭐ = Recommended models.

## Generation Method (`generation_method` values)

| Value | Description | Use Case |
|-------|-------------|----------|
| `n_grid` | Multi-frame grid: AI auto-plans keyframe sequence, generates multiple shots at once | Recommended, good visual continuity |
| `multi_ref` | Multi-reference v1: uses multiple reference images to drive video | Kling O3 only, multi-subject scenes |
| `multi_ref_v2` | Multi-reference v2: improved version | Kling O3 only, prefer over v1 |
| `start_frame` | Start-frame driven: uses keyframe image as starting frame | Legacy model compatibility, precise first-frame control |
