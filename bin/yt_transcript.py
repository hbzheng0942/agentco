#!/usr/bin/env python3
"""yt_transcript.py — json3 字幕 → 带时间戳的干净转写文本(L1 蒸馏输入)

- 合并碎片 caption 为段落,每 ~N 秒落一个 [mm:ss] 时间锚(默认 20s)
- 输出到 stdout 或 --out;供 digester 蒸馏 workflow card 用
用法: yt_transcript.py <file.json3> [--anchor-sec 20] [--out FILE]
"""
import argparse, json, re, sys
from pathlib import Path


def convert(path: Path, anchor_sec: int = 20) -> str:
    d = json.loads(path.read_text())
    words = []  # (start_sec, text)
    for e in d.get("events", []):
        for s in e.get("segs") or []:
            t = s.get("utf8", "")
            if t.strip():
                start = (e["tStartMs"] + s.get("tOffsetMs", 0)) / 1000
                words.append((start, t))
    out, last_anchor = [], -1e9
    for start, t in words:
        if start - last_anchor >= anchor_sec:
            m, sec = divmod(int(start), 60)
            out.append(f"\n[{m:02d}:{sec:02d}] ")
            last_anchor = start
        out.append(t if not t.startswith("\n") else " ")
    text = "".join(out)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip() + "\n"


def batch(subs_dir: Path, tx_dir: Path, anchor_sec: int) -> None:
    """subs/*.json3 → transcripts/<vid>.txt 增量转换;同视频 en-orig 优先于 en。"""
    tx_dir.mkdir(parents=True, exist_ok=True)
    picked = {}
    for p in sorted(subs_dir.glob("*.json3")):
        vid = p.name.split(".")[0]
        if vid not in picked or ".en-orig." in p.name:
            picked[vid] = p
    n = 0
    for vid, p in picked.items():
        out = tx_dir / f"{vid}.txt"
        if out.exists():
            continue
        out.write_text(convert(p, anchor_sec))
        n += 1
    print(f"converted {n} new, total {len(list(tx_dir.glob('*.txt')))} transcripts")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("json3", type=Path, nargs="?")
    p.add_argument("--anchor-sec", type=int, default=20)
    p.add_argument("--out", type=Path)
    p.add_argument("--batch", action="store_true",
                   help="增量转换整个频道: subs/*.json3 → transcripts/,en-orig 优先")
    p.add_argument("--slug", default="stefan-3d-ai")
    a = p.parse_args()
    if a.batch:
        base = Path(__file__).resolve().parent.parent / "data/inspiration" / a.slug
        batch(base / "subs", base / "transcripts", a.anchor_sec)
    elif a.json3:
        txt = convert(a.json3, a.anchor_sec)
        (a.out.write_text(txt) if a.out else sys.stdout.write(txt))
    else:
        p.error("需要 json3 文件参数,或 --batch")
