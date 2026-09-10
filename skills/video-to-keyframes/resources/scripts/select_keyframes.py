import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np


@dataclass
class Cand:
    group_id: int
    cand_id: int
    timestamp_s: float
    src_file: str
    out_file: str
    score: float
    sharpness: float
    brightness: float
    contrast: float
    saturation: float
    motion: float | None
    description: str


@dataclass
class Cut:
    index_left: int
    index_right: int
    t_left: float
    t_right: float
    cut_t: float
    dhash_dist: int


@dataclass
class Segment:
    seg_id: int
    start_t: float
    end_t: float
    rep_t: float
    rep_file: str
    rep_score: float
    frame_count: int


def _load_frames(frames_json: Path) -> list[dict[str, Any]]:
    data = json.loads(frames_json.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit("frames.json 格式不正确")
    return data


def _read_gray(path: Path) -> np.ndarray:
    b = cv2.imdecode(np.frombuffer(path.read_bytes(), np.uint8), cv2.IMREAD_GRAYSCALE)
    if b is None:
        raise SystemExit(f"无法读取图片：{path}")
    return b


def _dhash64(gray: np.ndarray) -> int:
    small = cv2.resize(gray, (9, 8), interpolation=cv2.INTER_AREA)
    diff = small[:, 1:] > small[:, :-1]
    bits = diff.flatten()
    h = 0
    for i, v in enumerate(bits):
        if v:
            h |= 1 << i
    return int(h)


def _hamming(a: int, b: int) -> int:
    return int((a ^ b).bit_count())


def _norm(v: float, lo: float, hi: float) -> float:
    if hi <= lo:
        return 0.5
    x = (v - lo) / (hi - lo)
    if x < 0:
        return 0.0
    if x > 1:
        return 1.0
    return float(x)


def _score(row: dict[str, Any], stats: dict[str, float]) -> float:
    sharp = float(row.get("sharpness") or 0.0)
    bright = float(row.get("brightness") or 0.0)
    contr = float(row.get("contrast") or 0.0)
    sat = float(row.get("saturation") or 0.0)
    motion = row.get("motion")
    mot = float(motion) if motion is not None else stats["motion_med"]

    s1 = _norm(np.log1p(sharp), stats["logsharp_min"], stats["logsharp_max"])
    s2 = 1.0 - abs(bright - stats["bright_med"]) / max(stats["bright_mad"] * 3.0, 30.0)
    if s2 < 0:
        s2 = 0.0
    if s2 > 1:
        s2 = 1.0
    s3 = _norm(contr, stats["contr_p10"], stats["contr_p90"])
    s4 = _norm(sat, stats["sat_p10"], stats["sat_p90"])
    s5 = 1.0 - _norm(mot, stats["motion_p10"], stats["motion_p90"])

    return float(0.45 * s1 + 0.25 * s2 + 0.15 * s3 + 0.05 * s4 + 0.10 * s5)


def _percentile(vals: list[float], p: float) -> float:
    if not vals:
        return 0.0
    a = np.array(vals, dtype=np.float64)
    return float(np.percentile(a, p))


def _median(vals: list[float]) -> float:
    if not vals:
        return 0.0
    return float(np.median(np.array(vals, dtype=np.float64)))


def _mad(vals: list[float], med: float) -> float:
    if not vals:
        return 0.0
    a = np.array(vals, dtype=np.float64)
    return float(np.median(np.abs(a - med)))


def _build_stats(rows: list[dict[str, Any]]) -> dict[str, float]:
    sharp = [float(r.get("sharpness") or 0.0) for r in rows]
    logsharp = [float(np.log1p(x)) for x in sharp]
    bright = [float(r.get("brightness") or 0.0) for r in rows]
    contr = [float(r.get("contrast") or 0.0) for r in rows]
    sat = [float(r.get("saturation") or 0.0) for r in rows]
    mot = [float(r.get("motion") or 0.0) for r in rows if r.get("motion") is not None]

    bright_med = _median(bright)
    motion_med = _median(mot) if mot else 0.0
    return {
        "logsharp_min": min(logsharp) if logsharp else 0.0,
        "logsharp_max": max(logsharp) if logsharp else 1.0,
        "bright_med": bright_med,
        "bright_mad": _mad(bright, bright_med),
        "contr_p10": _percentile(contr, 10.0),
        "contr_p90": _percentile(contr, 90.0),
        "sat_p10": _percentile(sat, 10.0),
        "sat_p90": _percentile(sat, 90.0),
        "motion_p10": _percentile(mot, 10.0) if mot else 0.0,
        "motion_p90": _percentile(mot, 90.0) if mot else 1.0,
        "motion_med": motion_med,
    }


def _copy_bytes(src: Path, dst: Path) -> None:
    dst.write_bytes(src.read_bytes())


def _detect_cuts(
    frames: list[dict[str, Any]],
    cut_thr: int,
    stable_thr: int,
    stable_window: int,
    min_gap_s: float,
) -> list[Cut]:
    n = len(frames)
    if n < (stable_window * 2 + 2):
        return []

    ts = [float(f.get("timestamp_s") or 0.0) for f in frames]
    hs = [int(f.get("__dhash")) for f in frames]

    diffs = [0] * n
    for i in range(1, n):
        diffs[i] = _hamming(hs[i - 1], hs[i])

    cuts: list[Cut] = []
    for i in range(max(1, stable_window), n - stable_window):
        d = diffs[i]
        if d < cut_thr:
            continue
        pre = diffs[i - stable_window : i]
        post = diffs[i + 1 : i + 1 + stable_window]
        if not pre or not post:
            continue
        if max(pre) > stable_thr:
            continue
        if max(post) > stable_thr:
            continue
        t_left = ts[i - 1]
        t_right = ts[i]
        cuts.append(
            Cut(
                index_left=i - 1,
                index_right=i,
                t_left=t_left,
                t_right=t_right,
                cut_t=(t_left + t_right) / 2.0,
                dhash_dist=int(d),
            )
        )

    cuts.sort(key=lambda c: c.cut_t)
    if not cuts:
        return []

    merged: list[Cut] = [cuts[0]]
    for c in cuts[1:]:
        prev = merged[-1]
        if c.cut_t - prev.cut_t < min_gap_s:
            if c.dhash_dist > prev.dhash_dist:
                merged[-1] = c
        else:
            merged.append(c)
    return merged


def _segments_from_cuts(frames: list[dict[str, Any]], cuts: list[Cut]) -> list[Segment]:
    ts = [float(f.get("timestamp_s") or 0.0) for f in frames]
    n = len(frames)
    boundaries = [0] + [c.index_right for c in cuts] + [n]
    segs: list[Segment] = []
    for si in range(len(boundaries) - 1):
        a = boundaries[si]
        b = boundaries[si + 1]
        chunk = frames[a:b]
        if not chunk:
            continue
        rep = max(chunk, key=lambda x: float(x.get("__score") or 0.0))
        segs.append(
            Segment(
                seg_id=si + 1,
                start_t=ts[a],
                end_t=ts[b - 1],
                rep_t=float(rep.get("timestamp_s") or 0.0),
                rep_file=str(rep.get("__abs_file") or ""),
                rep_score=float(rep.get("__score") or 0.0),
                frame_count=len(chunk),
            )
        )
    return segs


def _merge_short_segments(frames: list[dict[str, Any]], cuts: list[Cut], min_len_s: float) -> list[Cut]:
    if min_len_s <= 0:
        return cuts
    ts = [float(f.get("timestamp_s") or 0.0) for f in frames]
    cuts = sorted(list(cuts), key=lambda c: c.cut_t)
    while True:
        boundaries = [0] + [c.index_right for c in cuts] + [len(frames)]
        short_idx = None
        for si in range(len(boundaries) - 1):
            a = boundaries[si]
            b = boundaries[si + 1]
            if b - a <= 0:
                continue
            dur = ts[b - 1] - ts[a]
            if dur < min_len_s:
                short_idx = si
                break
        if short_idx is None:
            return cuts
        left_cut_i = short_idx - 1
        right_cut_i = short_idx
        choices = []
        if 0 <= left_cut_i < len(cuts):
            choices.append(left_cut_i)
        if 0 <= right_cut_i < len(cuts):
            choices.append(right_cut_i)
        if not choices:
            return cuts
        drop_i = min(choices, key=lambda i: cuts[i].dhash_dist)
        cuts.pop(drop_i)


def _write_gallery(out_dir: Path, cands: list[Cand]) -> None:
    rels = [(Path(c.out_file).name, c) for c in cands]
    rows = []
    for fn, c in rels:
        rows.append(
            f"<tr>"
            f"<td>{c.cand_id:03d}</td>"
            f"<td>{c.group_id:03d}</td>"
            f"<td>{c.timestamp_s:.2f}s</td>"
            f"<td>{c.score:.3f}</td>"
            f"<td>{c.description}</td>"
            f"<td><img src=\"{fn}\" style=\"max-width:240px;height:auto\"/></td>"
            f"<td>{fn}</td>"
            f"</tr>"
        )
    html = (
        "<!doctype html><html><head><meta charset=\"utf-8\">"
        "<title>关键帧候选</title>"
        "<style>body{font-family:system-ui,Segoe UI,Arial}table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:6px;vertical-align:top}th{background:#f6f6f6}img{display:block}</style>"
        "</head><body>"
        "<h2>关键帧候选画廊</h2>"
        "<p>建议做法：先在本页挑选要保留的 cand_id（左侧三位数），把编号写到 selected.txt（每行一个编号），再用后续脚本复制为最终关键帧集。</p>"
        "<table><thead><tr><th>cand_id</th><th>group</th><th>t</th><th>score</th><th>desc</th><th>img</th><th>file</th></tr></thead><tbody>"
        + "\n".join(rows)
        + "</tbody></table></body></html>"
    )
    (out_dir / "gallery.html").write_text(html, encoding="utf-8")


def _write_segments_gallery(out_dir: Path, cuts: list[Cut], segs: list[Segment]) -> None:
    cut_line = " / ".join([f"{c.cut_t:.2f}s" for c in cuts]) if cuts else "无"
    rows = []
    for s in segs:
        rep_src = Path(s.rep_file)
        rep_name = f"seg_{s.seg_id:02d}_t{float(s.rep_t):06.2f}_{rep_src.name}"
        rep_dst = out_dir / rep_name
        _copy_bytes(rep_src, rep_dst)
        rows.append(
            f"<tr>"
            f"<td>{s.seg_id:02d}</td>"
            f"<td>{s.start_t:.2f}s - {s.end_t:.2f}s</td>"
            f"<td>{s.frame_count}</td>"
            f"<td>{s.rep_t:.2f}s</td>"
            f"<td>{s.rep_score:.3f}</td>"
            f"<td><img src=\"{rep_name}\" style=\"max-width:320px;height:auto\"/></td>"
            f"<td>{rep_name}</td>"
            f"</tr>"
        )
    html = (
        "<!doctype html><html><head><meta charset=\"utf-8\">"
        "<title>分段结果</title>"
        "<style>body{font-family:system-ui,Segoe UI,Arial}table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:6px;vertical-align:top}th{background:#f6f6f6}img{display:block}</style>"
        "</head><body>"
        "<h2>分段结果（按转场切分）</h2>"
        f"<p>转场点：{cut_line}</p>"
        "<table><thead><tr><th>seg</th><th>range</th><th>frames</th><th>rep_t</th><th>rep_score</th><th>rep_img</th><th>file</th></tr></thead><tbody>"
        + "\n".join(rows)
        + "</tbody></table></body></html>"
    )
    (out_dir / "segments_gallery.html").write_text(html, encoding="utf-8")


def _write_prompt_page(out_dir: Path, cuts: list[Cut], segs: list[Segment], cands: list[Cand]) -> None:
    cut_line = " / ".join([f"{c.cut_t:.2f}s" for c in cuts]) if cuts else "无"

    seg_rows = []
    for s in segs:
        rep_src = Path(s.rep_file)
        rep_name = f"seg_{s.seg_id:02d}_t{float(s.rep_t):06.2f}_{rep_src.name}"
        seg_rows.append(
            f"<tr>"
            f"<td>S{s.seg_id:02d}</td>"
            f"<td>{s.start_t:.2f}s - {s.end_t:.2f}s</td>"
            f"<td><img src=\"{rep_name}\" class=\"img\"/></td>"
            f"<td class=\"mono\">{rep_name}</td>"
            f"</tr>"
        )

    cand_rows = []
    for c in cands:
        fn = Path(c.out_file).name
        cand_rows.append(
            f"<tr data-cand-id=\"{c.cand_id:03d}\">"
            f"<td class=\"mono\">{c.cand_id:03d}</td>"
            f"<td class=\"mono\">{c.group_id:03d}</td>"
            f"<td>{c.timestamp_s:.2f}s</td>"
            f"<td>{c.score:.3f}</td>"
            f"<td class=\"small\">{c.description}</td>"
            f"<td><img src=\"{fn}\" class=\"img\"/></td>"
            f"<td class=\"mono\">{fn}</td>"
            f"</tr>"
        )

    q = [
        ("成片", "平台__；时长__s；分镜数（4-6默认）__；画幅__；风格参考__；禁用元素__"),
        ("内容", "地点/场景__；主体__；动作__；情绪__；时代感/现代元素容忍度__"),
        ("画面", "光线__；时段__；镜头语言（景别/机位/运镜）__；色调__；材质细节__"),
        ("素材", "用户已有照片__张（分别是什么）；可补拍/可找素材的范围__"),
    ]
    q_rows = "".join([f"<tr><td class=\"k\">{a}</td><td>{b}</td></tr>" for a, b in q])

    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>复筛与提示词</title>
  <style>
    :root {{
      --bg: #ffffff;
      --fg: #111111;
      --muted: #666666;
      --card: #f6f6f6;
      --border: #d0d0d0;
      --accent: #2b6cb0;
      --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #0b0f14;
        --fg: #e8eaed;
        --muted: #a0a0a0;
        --card: #111827;
        --border: #243244;
        --accent: #60a5fa;
      }}
    }}
    body {{ margin: 0; background: var(--bg); color: var(--fg); font-family: system-ui, Segoe UI, Arial; }}
    .wrap {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
    h1, h2 {{ margin: 0 0 10px 0; }}
    p {{ margin: 6px 0; color: var(--muted); }}
    .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 14px; margin: 12px 0; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border: 1px solid var(--border); padding: 8px; vertical-align: top; }}
    th {{ background: color-mix(in oklab, var(--card) 80%, var(--bg) 20%); }}
    .mono {{ font-family: var(--mono); }}
    .small {{ color: var(--muted); font-size: 12px; }}
    .img {{ max-width: 260px; height: auto; display: block; border-radius: 8px; border: 1px solid var(--border); }}
    .row {{ display: grid; grid-template-columns: 1fr; gap: 12px; }}
    @media (min-width: 980px) {{ .row {{ grid-template-columns: 1fr 1fr; }} }}
    textarea {{ width: 100%; min-height: 120px; background: var(--bg); color: var(--fg); border: 1px solid var(--border); border-radius: 8px; padding: 10px; font-family: var(--mono); }}
    input[type="text"] {{ width: 100%; background: var(--bg); color: var(--fg); border: 1px solid var(--border); border-radius: 8px; padding: 8px; font-family: var(--mono); }}
    button {{ background: var(--accent); color: white; border: none; border-radius: 8px; padding: 8px 10px; cursor: pointer; }}
    .btn2 {{ background: transparent; color: var(--fg); border: 1px solid var(--border); }}
    .k {{ width: 90px; white-space: nowrap; }}
    .gridimgs {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 10px; }}
    .thumb {{ border: 1px solid var(--border); border-radius: 10px; padding: 8px; background: var(--bg); }}
    .thumb img {{ max-width: 100%; height: auto; display: block; border-radius: 8px; }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>复筛与提示词（本地一键复制页）</h1>
    <p>转场点：{cut_line}</p>

    <div class="card">
      <h2>第一步：让用户上传可用照片</h2>
      <div class="row">
        <div>
          <p>把用户照片拖进这里，仅用于本页预览与对照（不上传到网络）。</p>
          <input id="upload" type="file" accept="image/*" multiple>
          <div id="uploads" class="gridimgs" style="margin-top:10px"></div>
        </div>
        <div>
          <p>要问用户的内容（复制给用户）：</p>
          <table>
            <tbody>
              {q_rows}
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="card">
      <h2>第二步：建议提供的帧（按转场切分的每段代表帧）</h2>
      <p>这些帧来自 segments.json；用于和用户照片对齐“缺什么补什么”。</p>
      <table>
        <thead>
          <tr><th>段</th><th>范围</th><th>代表帧</th><th>文件</th></tr>
        </thead>
        <tbody>
          {"".join(seg_rows)}
        </tbody>
      </table>
    </div>

    <div class="card">
      <h2>第三步：已有关键帧/候选关键帧（复筛池）</h2>
      <p>从下面挑 6-12 张作为最终关键帧（4-6分镜×每分镜1-2张）。把 cand_id 用逗号写进“最终关键帧ID”。</p>
      <div class="row">
        <div>
          <label class="small">最终关键帧ID（cand_id，用逗号分隔，如 002,009,010）</label>
          <input id="picked" type="text" placeholder="例如 002,009,010">
          <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap">
            <button id="btnBuild">生成分镜提示词表</button>
            <button id="btnCopyAll" class="btn2">复制全部提示词</button>
          </div>
          <p class="small">提示：你也可以直接用已有的 selected.txt（每行一个编号），手动复制到这里。</p>
        </div>
        <div>
          <label class="small">迁移提示词（复制到AI，让它根据关键帧与用户照片产出每分镜提示词）</label>
          <textarea id="migratePrompt"></textarea>
        </div>
      </div>
      <table style="margin-top:12px">
        <thead>
          <tr><th>cand_id</th><th>group</th><th>t</th><th>score</th><th>desc</th><th>img</th><th>file</th></tr>
        </thead>
        <tbody>
          {"".join(cand_rows)}
        </tbody>
      </table>
    </div>

    <div class="card">
      <h2>第四步：分镜提示词（可直接复制）</h2>
      <div class="row">
        <div>
          <label class="small">基准prompt（固定画幅/风格/质感/画质/禁用元素）</label>
          <textarea id="basePrompt" placeholder="写你的基准prompt..."></textarea>
        </div>
        <div>
          <label class="small">分镜提示词输出（基准 + 分镜偏移）</label>
          <textarea id="shotPrompts" placeholder="点击“生成分镜提示词表”后自动填充..."></textarea>
        </div>
      </div>
    </div>
  </div>

  <script>
    const upload = document.getElementById('upload');
    const uploads = document.getElementById('uploads');
    upload.addEventListener('change', () => {{
      uploads.innerHTML = '';
      for (const f of upload.files) {{
        const url = URL.createObjectURL(f);
        const div = document.createElement('div');
        div.className = 'thumb';
        div.innerHTML = `<img src="${{url}}"><div class="small">${{f.name}}</div>`;
        uploads.appendChild(div);
      }}
    }});

    const migrate = document.getElementById('migratePrompt');
    migrate.value =
`你是分镜提示词生成器。\n` +
`目标：根据“用户照片”和“关键帧(参考图)”生成4-6个分镜的生图提示词，每分镜至少1张图。\n` +
`要求：\n` +
`1) 先输出你理解的：平台/时长/画幅/风格/禁用元素。\n` +
`2) 再输出分镜表（S01..S0N）：每行包含：地点、主体、动作、镜头语言(景别/机位)、光线/时段、情绪、关键物件、环境细节、负面约束。\n` +
`3) 分镜提示词格式：基准prompt + 分镜偏移；除“主体/动作/镜头/细节/情绪”外不要改动。\n` +
`4) 若用户照片缺关键角度/细节，先给“需要补拍清单”(每条说明拍法)。\n` +
`输入给你：\n` +
`- 用户照片：见本页上传预览\n` +
`- 关键帧：从本页选择的 cand_id 对应图片\n` +
`- 建议提供的帧：segments_gallery 里的每段代表帧\n`;

    const btnBuild = document.getElementById('btnBuild');
    const btnCopyAll = document.getElementById('btnCopyAll');
    const picked = document.getElementById('picked');
    const basePrompt = document.getElementById('basePrompt');
    const shotPrompts = document.getElementById('shotPrompts');

    function parseIds(s) {{
      return s.split(',').map(x => x.trim()).filter(Boolean).map(x => x.padStart(3,'0'));
    }}

    btnBuild.addEventListener('click', () => {{
      const ids = parseIds(picked.value);
      const base = basePrompt.value.trim();
      const lines = [];
      let i = 1;
      for (const id of ids) {{
        lines.push(`S${{String(i).padStart(2,'0')}}：` + (base ? base + '；' : '') + `地点__；主体__；动作__；镜头语言__；关键物件__；情绪__；环境细节__；禁用元素__；参考关键帧=cand_${{id}}`);
        i++;
      }}
      shotPrompts.value = lines.join('\\n');
    }});

    btnCopyAll.addEventListener('click', async () => {{
      const text = shotPrompts.value.trim();
      if (!text) return;
      try {{
        await navigator.clipboard.writeText(text);
      }} catch (e) {{
        shotPrompts.focus();
        shotPrompts.select();
      }}
    }});
  </script>
</body>
</html>
"""
    (out_dir / "prompt_pack.html").write_text(html, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("frames_json", help="extract_frames_and_describe.py 产出的 frames.json 路径")
    parser.add_argument("--out", default=None, help="输出目录，默认在 frames.json 同目录创建 _keyframes_candidates")
    parser.add_argument("--hamming", type=int, default=10, help="dHash 汉明距离阈值（越小去重越强）")
    parser.add_argument("--max-cands", type=int, default=30, help="最多保留多少候选关键帧")
    parser.add_argument("--cut-thr", type=int, default=22, help="转场阈值：前后大量变化（dHash 汉明距离）")
    parser.add_argument("--stable-thr", type=int, default=10, help="稳定阈值：前后相似（窗口内最大距离）")
    parser.add_argument("--stable-window", type=int, default=3, help="稳定窗口：转场前后各看多少个相邻差值")
    parser.add_argument("--min-gap", type=float, default=1.0, help="转场最小间隔（秒）")
    parser.add_argument("--min-seg-len", type=float, default=1.5, help="最短分段长度（秒），过短会合并")
    args = parser.parse_args()

    frames_json = Path(args.frames_json).expanduser().resolve()
    rows = _load_frames(frames_json)
    if not rows:
        raise SystemExit("frames.json 为空")

    frames_dir = frames_json.parent
    out_dir = Path(args.out).expanduser().resolve() if args.out else (frames_dir / "_keyframe_candidates")
    out_dir.mkdir(parents=True, exist_ok=True)

    stats = _build_stats(rows)

    enriched = []
    for r in rows:
        f = Path(str(r.get("file") or "")).expanduser()
        if not f.is_absolute():
            f = (frames_dir / f).resolve()
        r2 = dict(r)
        r2["__abs_file"] = str(f)
        r2["__score"] = _score(r2, stats)
        enriched.append(r2)

    enriched.sort(key=lambda x: float(x.get("timestamp_s") or 0.0))

    groups: list[list[dict[str, Any]]] = []
    cur: list[dict[str, Any]] = []
    last_hash: int | None = None
    for r in enriched:
        p = Path(r["__abs_file"])
        gray = _read_gray(p)
        h = _dhash64(gray)
        r["__dhash"] = h
        if last_hash is None:
            cur = [r]
            last_hash = h
            continue
        if _hamming(last_hash, h) <= int(args.hamming):
            cur.append(r)
        else:
            groups.append(cur)
            cur = [r]
        last_hash = h
    if cur:
        groups.append(cur)

    cuts = _detect_cuts(
        frames=enriched,
        cut_thr=int(args.cut_thr),
        stable_thr=int(args.stable_thr),
        stable_window=int(args.stable_window),
        min_gap_s=float(args.min_gap),
    )
    cuts = _merge_short_segments(enriched, cuts, float(args.min_seg_len))
    segs = _segments_from_cuts(enriched, cuts)
    (out_dir / "cuts.json").write_text(json.dumps([c.__dict__ for c in cuts], ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "segments.json").write_text(
        json.dumps([s.__dict__ for s in segs], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _write_segments_gallery(out_dir, cuts, segs)

    picks: list[dict[str, Any]] = []
    for g in groups:
        best = max(g, key=lambda x: float(x.get("__score") or 0.0))
        picks.append(best)

    picks.sort(key=lambda x: float(x.get("__score") or 0.0), reverse=True)
    picks = picks[: max(1, int(args.max_cands))]
    picks.sort(key=lambda x: float(x.get("timestamp_s") or 0.0))

    cands: list[Cand] = []
    for i, r in enumerate(picks, start=1):
        src = Path(r["__abs_file"])
        group_id = 0
        for gi, g in enumerate(groups, start=1):
            if r in g:
                group_id = gi
                break
        out_name = f"c_{i:03d}_g{group_id:03d}_t{float(r.get('timestamp_s') or 0.0):06.2f}_{src.name}"
        dst = out_dir / out_name
        _copy_bytes(src, dst)
        cands.append(
            Cand(
                group_id=group_id,
                cand_id=i,
                timestamp_s=float(r.get("timestamp_s") or 0.0),
                src_file=str(src),
                out_file=str(dst),
                score=float(r.get("__score") or 0.0),
                sharpness=float(r.get("sharpness") or 0.0),
                brightness=float(r.get("brightness") or 0.0),
                contrast=float(r.get("contrast") or 0.0),
                saturation=float(r.get("saturation") or 0.0),
                motion=float(r.get("motion")) if r.get("motion") is not None else None,
                description=str(r.get("description") or ""),
            )
        )

    (out_dir / "candidates.json").write_text(
        json.dumps([c.__dict__ for c in cands], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    with (out_dir / "candidates.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(Cand.__dataclass_fields__.keys()))
        w.writeheader()
        for c in cands:
            w.writerow(c.__dict__)

    _write_gallery(out_dir, cands)
    _write_prompt_page(out_dir, cuts, segs, cands)
    (out_dir / "selected.txt").write_text("", encoding="utf-8")
    print(str(out_dir))


if __name__ == "__main__":
    main()

