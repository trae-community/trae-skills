---
name: "video-to-keyframes"
description: "Extracts video frames, detects cuts/segments, selects candidate keyframes, and generates review HTML galleries. Invoke when users ask for keyframes/cuts/segmentation/storyboard screening."
---

# 视频转关键帧（video-to-keyframes）

把用户提供的视频转成“候选帧池 → 转场/分段 → 候选关键帧集 → 复筛画廊页”，并把产物落盘到当天文件夹，方便后续分镜与生成。

## 何时调用

- 用户提供视频并说：抽帧/拆帧/关键帧/候选关键帧/镜头拆分/转场点/分段/分镜初筛
- 用户希望按固定工作流落盘，需要可复现的目录与文件（frames.json、cuts.json、segments.json、gallery.html 等）

## 依赖

- Python 3.10+
- numpy
- opencv-python

## 输入

- 视频文件路径（必填）
- 当天文件夹路径（可选，默认用视频所在目录；推荐 YYYY-MM-DD）
- 抽帧间隔（建议：30s≈1fps；变化快≈2fps）

## 输出（固定规范）

在 `<当天文件夹>` 下生成：

- `<当天文件夹>\_frames_<视频名>_<间隔>\`：候选帧池目录
  - `f_*.jpg`：抽帧图片
  - `frames.csv / frames.json / top_keep.json / meta.json`
  - `\_keyframe_candidates\`：候选关键帧集目录
    - `cuts.json`：转场点
    - `segments.json`：分段与每段代表帧
    - `segments_gallery.html`：分段可视化（每段1张代表帧）
    - `gallery.html`：候选关键帧画廊（逐个复筛）
    - `candidates.csv / candidates.json`
    - `selected.txt`：人工/AI复筛后的最终候选ID（每行一个 cand_id）
    - `prompt_pack.html`：复筛+提示词协作页（夜间模式，一键复制）
- `<当天文件夹>\<视频名>_拆分.txt`：汇总（转场点、分段、每段代表帧文件名）

## 一键运行（推荐）

```powershell
python .\skills\video-to-keyframes\resources\scripts\run_video_workflow.py "<视频路径>" --day-folder "<当天文件夹>" --every-seconds 0.5 --max-frames 600
```

注意：一键运行只负责产出文件，不等于完成复筛；必须打开 `gallery.html` 做人工/AI语义复筛，并把最终选择写入 `selected.txt`。

## 复筛要点（简版）

- 先看 `segments_gallery.html`：确认每段代表帧是否合理、分段是否过碎
- 再看 `gallery.html`：挑 6-12 张最“代表内容且可复现”的帧（不要只挑清晰但信息弱的帧）
- 将 cand_id 写入 `selected.txt`（每行一个三位数字或逗号分隔均可）

