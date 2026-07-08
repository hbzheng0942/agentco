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


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("json3", type=Path)
    p.add_argument("--anchor-sec", type=int, default=20)
    p.add_argument("--out", type=Path)
    a = p.parse_args()
    txt = convert(a.json3, a.anchor_sec)
    (a.out.write_text(txt) if a.out else sys.stdout.write(txt))
