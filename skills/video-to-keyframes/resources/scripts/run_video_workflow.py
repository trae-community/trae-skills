import argparse
import json
import subprocess
import sys
from pathlib import Path


def _fmt_ts(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    ms = int(round((seconds - int(seconds)) * 1000))
    s = int(seconds) % 60
    m = (int(seconds) // 60) % 60
    h = int(seconds) // 3600
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def _tag_seconds(v: float) -> str:
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return s.replace(".", "p") + "s"


def _run(args: list[str]) -> None:
    p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise SystemExit(p.stdout.strip() or "运行失败")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("video", help="视频路径")
    parser.add_argument("--day-folder", default=None, help="当天文件夹（YYYY-MM-DD），默认用视频所在目录")
    parser.add_argument("--every-seconds", type=float, default=0.5, help="抽帧间隔秒")
    parser.add_argument("--max-frames", type=int, default=600, help="最多抽帧数")
    parser.add_argument("--jpeg-quality", type=int, default=92, help="JPEG质量")
    parser.add_argument("--hamming", type=int, default=10, help="去重阈值（dHash汉明距离）")
    parser.add_argument("--max-cands", type=int, default=30, help="候选关键帧数量上限")
    parser.add_argument("--cut-thr", type=int, default=30, help="转场阈值：前后大量变化（dHash距离）")
    parser.add_argument("--stable-thr", type=int, default=31, help="稳定阈值：前后相似（窗口内最大距离）")
    parser.add_argument("--stable-window", type=int, default=1, help="稳定窗口：转场前后各看多少个相邻差值")
    parser.add_argument("--min-gap", type=float, default=1.0, help="转场最小间隔（秒）")
    parser.add_argument("--min-seg-len", type=float, default=2.0, help="最短分段长度（秒），过短会合并")
    args = parser.parse_args()

    video_path = Path(args.video).expanduser().resolve()
    if not video_path.exists():
        raise SystemExit("视频不存在")

    day_folder = Path(args.day_folder).expanduser().resolve() if args.day_folder else video_path.parent
    day_folder.mkdir(parents=True, exist_ok=True)

    frames_dir = day_folder / f"_frames_{video_path.stem}_{_tag_seconds(float(args.every_seconds))}"
    frames_dir.mkdir(parents=True, exist_ok=True)

    root = Path(__file__).resolve().parent
    extract_py = root / "extract_frames_and_describe.py"
    select_py = root / "select_keyframes.py"
    if not extract_py.exists() or not select_py.exists():
        raise SystemExit("缺少脚本文件")

    _run(
        [
            sys.executable,
            str(extract_py),
            str(video_path),
            "--every-seconds",
            str(float(args.every_seconds)),
            "--max-frames",
            str(int(args.max_frames)),
            "--jpeg-quality",
            str(int(args.jpeg_quality)),
            "--out",
            str(frames_dir),
        ]
    )

    _run(
        [
            sys.executable,
            str(select_py),
            str(frames_dir / "frames.json"),
            "--hamming",
            str(int(args.hamming)),
            "--max-cands",
            str(int(args.max_cands)),
            "--cut-thr",
            str(int(args.cut_thr)),
            "--stable-thr",
            str(int(args.stable_thr)),
            "--stable-window",
            str(int(args.stable_window)),
            "--min-gap",
            str(float(args.min_gap)),
            "--min-seg-len",
            str(float(args.min_seg_len)),
        ]
    )

    meta = json.loads((frames_dir / "meta.json").read_text(encoding="utf-8"))
    cuts = json.loads((frames_dir / "_keyframe_candidates" / "cuts.json").read_text(encoding="utf-8"))
    segs = json.loads((frames_dir / "_keyframe_candidates" / "segments.json").read_text(encoding="utf-8"))

    cut_ts = [float(c["cut_t"]) for c in cuts]
    cut_line = " / ".join([_fmt_ts(t) for t in cut_ts]) if cut_ts else "无"

    lines: list[str] = []
    lines.append(f"视频：{video_path.name}")
    lines.append(
        f"参数：{meta.get('fps')}fps，约{meta.get('frame_count')}帧，时长约{float(meta.get('duration_s') or 0.0):.2f}秒"
    )
    lines.append("拆分依据：转场=前后相似且中间大量变化（基于dHash相似度，抽帧后检测）")
    lines.append(
        f"判定规则：cut_thr={int(args.cut_thr)}，stable_thr={int(args.stable_thr)}，stable_window={int(args.stable_window)}，min_seg_len={float(args.min_seg_len)}s"
    )
    lines.append("")
    lines.append(f"转场点：{cut_line}")
    lines.append("")
    lines.append("分段：")
    for s in segs:
        start_t = float(s["start_t"])
        end_t = float(s["end_t"])
        rep_t = float(s["rep_t"])
        rep_file = Path(str(s["rep_file"])).name
        lines.append(f"- 分段{s['seg_id']}：{_fmt_ts(start_t)} - {_fmt_ts(end_t)}（代表帧 t={rep_t:.2f}s，{rep_file}）")

    out_txt = day_folder / f"{video_path.stem}_拆分.txt"
    out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(str(out_txt))


if __name__ == "__main__":
    main()

