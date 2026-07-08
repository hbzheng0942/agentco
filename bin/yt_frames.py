#!/usr/bin/env python3
"""yt_frames.py — 真值视频 → L1 派生层:镜头边界 + 靶向抽帧(带 manifest 留痕)

  scenes  <vid>   全片镜头边界检测 → scenes/<vid>.json
  targets <vid>   按靶点清单抽帧 → frames/<vid>/t<秒>_<偏移>.jpg + manifest.json
                  靶点清单: frames_targets/<vid>.json  [{"ts":"mm:ss","why":"..."},...]

留痕纪律:manifest 记录 脚本版本/参数/源文件md5/时间;改抽帧策略→重跑并 bump VERSION,
源视频(L0)永不动。
"""
import argparse, hashlib, json, subprocess, sys, time
from pathlib import Path

VERSION = "0.1"
BASE = Path(__file__).resolve().parent.parent / "data/inspiration"


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def find_video(root: Path, vid: str) -> Path:
    hits = list((root / "video").glob(f"{vid}.*"))
    if not hits:
        sys.exit(f"视频不存在: {root}/video/{vid}.*")
    return hits[0]


def md5_head(p: Path, mb=8):  # 头部8MB足够指纹用,全量太慢
    h = hashlib.md5()
    with open(p, "rb") as f:
        h.update(f.read(mb * 1024 * 1024))
    return h.hexdigest()


def parse_ts(ts: str) -> float:
    parts = [float(x) for x in ts.split(":")]
    return parts[0] * 60 + parts[1] if len(parts) == 2 else parts[0] * 3600 + parts[1] * 60 + parts[2]


def cmd_scenes(a):
    from scenedetect import detect, ContentDetector
    root = BASE / a.slug
    vid_file = find_video(root, a.vid)
    scenes = detect(str(vid_file), ContentDetector())
    out = root / "scenes"; out.mkdir(exist_ok=True)
    data = {"version": VERSION, "source_md5_8mb": md5_head(vid_file), "detector": "ContentDetector/default",
            "generated": time.strftime("%F %T"),
            "scenes": [{"start": s.get_seconds(), "end": e.get_seconds()} for s, e in scenes]}
    (out / f"{a.vid}.json").write_text(json.dumps(data, indent=1))
    print(f"{len(scenes)} scenes -> {out}/{a.vid}.json")


def cmd_targets(a):
    root = BASE / a.slug
    vid_file = find_video(root, a.vid)
    targets = json.loads((root / "frames_targets" / f"{a.vid}.json").read_text())
    outdir = root / "frames" / a.vid; outdir.mkdir(parents=True, exist_ok=True)
    offsets = [float(x) for x in a.offsets.split(",")]
    shots = []
    for t in targets:
        base = parse_ts(t["ts"])
        for off in offsets:
            ts = max(0, base + off)
            name = f"t{int(base):04d}_{'+' if off >= 0 else ''}{off:g}.jpg"
            subprocess.run([ffmpeg(), "-ss", str(ts), "-i", str(vid_file), "-frames:v", "1",
                            "-q:v", "2", "-y", str(outdir / name)],
                           capture_output=True)
            shots.append({"file": name, "ts_sec": ts, "target": t["ts"], "why": t.get("why", "")})
    manifest = {"version": VERSION, "source_md5_8mb": md5_head(vid_file),
                "offsets": offsets, "quality": "q2/full-res", "generated": time.strftime("%F %T"),
                "shots": shots}
    (outdir / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False))
    print(f"{len(shots)} frames -> {outdir}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--slug", default="stefan-3d-ai")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scenes"); s.add_argument("vid")
    s = sub.add_parser("targets"); s.add_argument("vid")
    s.add_argument("--offsets", default="-2,0,2", help="相对靶点的秒偏移,逗号分隔")
    a = p.parse_args()
    {"scenes": cmd_scenes, "targets": cmd_targets}[a.cmd](a)
