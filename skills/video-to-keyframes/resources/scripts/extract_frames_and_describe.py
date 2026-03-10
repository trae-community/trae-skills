import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np


@dataclass
class FrameInfo:
    index: int
    timestamp_s: float
    file: str
    width: int
    height: int
    sharpness: float
    brightness: float
    contrast: float
    saturation: float
    motion: float | None
    suggested_keep: bool
    description: str


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _save_image(out_dir: Path, stem: str, frame, jpeg_params: list[int]) -> Path:
    out_file = out_dir / f"{stem}.jpg"
    ok, buf = cv2.imencode(".jpg", frame, jpeg_params)
    if not ok:
        out_file = out_dir / f"{stem}.png"
        ok, buf = cv2.imencode(".png", frame)
    if not ok:
        raise SystemExit("写入图片失败")
    data = np.asarray(buf).tobytes()
    out_file.write_bytes(data)
    return out_file


def _fmt_ts(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    ms = int(round((seconds - int(seconds)) * 1000))
    s = int(seconds) % 60
    m = (int(seconds) // 60) % 60
    h = int(seconds) // 3600
    return f"{h:02d}-{m:02d}-{s:02d}-{ms:03d}"


def _lap_var(gray) -> float:
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def _mean_std(gray) -> tuple[float, float]:
    m, s = cv2.meanStdDev(gray)
    return float(m[0][0]), float(s[0][0])


def _mean_saturation(bgr) -> float:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    s = hsv[:, :, 1]
    return float(s.mean())


def _motion_score(prev_gray, gray) -> float:
    diff = cv2.absdiff(prev_gray, gray)
    return float(diff.mean())


def _desc(brightness: float, contrast: float, sharpness: float, saturation: float, motion: float | None) -> str:
    parts: list[str] = []

    if brightness < 70:
        parts.append("偏暗")
    elif brightness > 180:
        parts.append("偏亮")
    else:
        parts.append("曝光正常")

    if contrast < 25:
        parts.append("对比偏低")
    elif contrast > 70:
        parts.append("对比偏高")
    else:
        parts.append("对比适中")

    if sharpness < 60:
        parts.append("偏糊")
    elif sharpness > 200:
        parts.append("很清晰")
    else:
        parts.append("清晰度正常")

    if saturation < 40:
        parts.append("色彩寡淡")
    elif saturation > 140:
        parts.append("色彩浓烈")
    else:
        parts.append("色彩适中")

    if motion is not None:
        if motion < 2.0:
            parts.append("画面稳定")
        elif motion > 10.0:
            parts.append("运动幅度大")
        else:
            parts.append("有一定运动")

    return "，".join(parts)


def _bool_keep(sharpness: float, brightness: float, contrast: float, min_sharpness: float, bmin: float, bmax: float) -> bool:
    if sharpness < min_sharpness:
        return False
    if brightness < bmin or brightness > bmax:
        return False
    if contrast < 10:
        return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("video", help="视频路径")
    parser.add_argument("--out", default=None, help="输出目录，默认在视频同目录下创建 _frames_<文件名>")
    parser.add_argument("--every-seconds", type=float, default=0.5, help="按时间间隔抽帧")
    parser.add_argument("--max-frames", type=int, default=600, help="最多抽取帧数，防止视频过长")
    parser.add_argument("--start", type=float, default=0.0, help="起始秒")
    parser.add_argument("--end", type=float, default=None, help="结束秒（不含）")
    parser.add_argument("--jpeg-quality", type=int, default=92, help="JPEG质量 0-100")
    parser.add_argument("--min-sharpness", type=float, default=80.0, help="最小清晰度阈值（拉普拉斯方差）")
    parser.add_argument("--brightness-min", type=float, default=60.0, help="亮度下限")
    parser.add_argument("--brightness-max", type=float, default=200.0, help="亮度上限")
    args = parser.parse_args()

    video_path = Path(args.video).expanduser().resolve()
    if not video_path.exists():
        raise SystemExit(f"视频不存在：{video_path}")

    out_dir = Path(args.out).expanduser().resolve() if args.out else (video_path.parent / f"_frames_{video_path.stem}")
    _ensure_dir(out_dir)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise SystemExit("无法打开视频")

    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    duration_s = (frame_count / fps) if fps > 0 else 0.0

    start_s = max(float(args.start), 0.0)
    end_s = float(args.end) if args.end is not None else duration_s
    end_s = min(end_s, duration_s) if duration_s > 0 else end_s
    if end_s <= start_s:
        raise SystemExit("end 必须大于 start")

    step_s = max(float(args.every_seconds), 0.05)
    target_ts = start_s
    extracted = 0
    prev_gray = None
    rows: list[FrameInfo] = []

    jpeg_params = [int(cv2.IMWRITE_JPEG_QUALITY), int(max(0, min(100, args.jpeg_quality)))]

    while extracted < int(args.max_frames) and target_ts < end_s:
        if fps > 0:
            cap.set(cv2.CAP_PROP_POS_MSEC, target_ts * 1000.0)
        ret, frame = cap.read()
        if not ret or frame is None:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        sharpness = _lap_var(gray)
        brightness, contrast = _mean_std(gray)
        saturation = _mean_saturation(frame)
        motion = _motion_score(prev_gray, gray) if prev_gray is not None else None

        keep = _bool_keep(
            sharpness=sharpness,
            brightness=brightness,
            contrast=contrast,
            min_sharpness=float(args.min_sharpness),
            bmin=float(args.brightness_min),
            bmax=float(args.brightness_max),
        )
        description = _desc(brightness, contrast, sharpness, saturation, motion)

        stem = f"f_{extracted:05d}_t{_fmt_ts(target_ts)}"
        out_file = _save_image(out_dir, stem, frame, jpeg_params)

        rows.append(
            FrameInfo(
                index=extracted,
                timestamp_s=float(target_ts),
                file=str(out_file),
                width=width,
                height=height,
                sharpness=sharpness,
                brightness=brightness,
                contrast=contrast,
                saturation=saturation,
                motion=motion,
                suggested_keep=bool(keep),
                description=description,
            )
        )

        prev_gray = gray
        extracted += 1
        target_ts += step_s

    cap.release()

    meta: dict[str, Any] = {
        "video": str(video_path),
        "fps": fps,
        "frame_count": frame_count,
        "width": width,
        "height": height,
        "duration_s": duration_s,
        "start_s": start_s,
        "end_s": end_s,
        "every_seconds": step_s,
        "max_frames": int(args.max_frames),
        "extracted": extracted,
        "out_dir": str(out_dir),
        "columns": [f.name for f in FrameInfo.__dataclass_fields__.values()],
    }

    (out_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "frames.json").write_text(
        json.dumps([asdict(r) for r in rows], ensure_ascii=False, indent=2), encoding="utf-8"
    )

    with (out_dir / "frames.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=meta["columns"])
        w.writeheader()
        for r in rows:
            w.writerow(asdict(r))

    kept = [r for r in rows if r.suggested_keep]
    kept_sorted = sorted(kept, key=lambda r: (r.sharpness, -abs(128 - r.brightness), r.contrast), reverse=True)
    top = kept_sorted[: min(30, len(kept_sorted))]
    (out_dir / "top_keep.json").write_text(json.dumps([asdict(r) for r in top], ensure_ascii=False, indent=2), encoding="utf-8")

    print(str(out_dir))


if __name__ == "__main__":
    main()

