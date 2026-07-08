#!/usr/bin/env python3
"""yt_harvest.py — YouTube 频道资产采集器(inspiration 项目起,通用可复用)

三层采集,逐层变重,均可断点续跑(已存在即跳过):
  inventory  频道全量元数据(flat,免登录也能跑)
  subs       全量字幕(auto-subs, json3)+ info.json(description 含章节/工具链接)
  videos     精选视频 720p 下载(供关键帧/视觉层分析)

依赖 cookies(云机 IP 被 YouTube 封锁):默认 ~/.config/yt-dlp/youtube-cookies.txt
⚠️ 用小号导出 cookies——被这样使用的账号最终可能被 YouTube 封禁。

用法:
  yt_harvest.py inventory --channel https://www.youtube.com/@stefan_3d_ai
  yt_harvest.py subs      [--limit N]     # 按清单逐个取字幕,随机 sleep 防风控
  yt_harvest.py videos --ids id1,id2,...  # 或 --ids-file 一行一个
产物: data/inspiration/<slug>/{inventory.json, info/, subs/, video/}
"""
import argparse, json, random, subprocess, sys, time
from pathlib import Path

YTDLP = str(Path.home() / ".local/bin/yt-dlp")
COOKIES = Path.home() / ".config/yt-dlp/youtube-cookies.txt"
BASE = Path(__file__).resolve().parent.parent / "data/inspiration"


def run(args, **kw):
    return subprocess.run([YTDLP, "--js-runtimes", "node", *args], **kw)


def cookie_args():
    if not COOKIES.exists():
        sys.exit(f"缺 cookies: {COOKIES}\n浏览器导出 youtube.com cookies(Netscape 格式)后 scp 到该路径")
    return ["--cookies", str(COOKIES)]


def cmd_inventory(a):
    out = BASE / a.slug / "inventory.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    r = run(["--flat-playlist", "-J", f"{a.channel.rstrip('/')}/videos"],
            capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-800:])
    out.write_text(r.stdout)
    n = len(json.loads(r.stdout).get("entries", []))
    print(f"{n} videos -> {out}")


def load_ids(a):
    inv = BASE / a.slug / "inventory.json"
    entries = json.loads(inv.read_text()).get("entries", [])
    return [(v["id"], v.get("title", "")) for v in entries]


def cmd_subs(a):
    root = BASE / a.slug
    subs, info = root / "subs", root / "info"
    subs.mkdir(parents=True, exist_ok=True); info.mkdir(exist_ok=True)
    ids = load_ids(a)[: a.limit or None]
    done = fail = backoff = 0
    i = 0
    while i < len(ids):
        vid, title = ids[i]
        if list(subs.glob(f"{vid}.*")):
            i += 1; continue  # 断点续跑
        r = run([*cookie_args(), "--skip-download", "--ignore-no-formats-error",
                 "--write-auto-subs", "--write-subs", "--sub-langs", "en-orig,en",
                 "--sub-format", "json3", "--write-info-json",
                 "-o", f"infojson:{info}/{vid}", "-o", f"subtitle:{subs}/{vid}",
                 f"https://www.youtube.com/watch?v={vid}"],
                capture_output=True, text=True)
        ok = bool(list(subs.glob(f"{vid}.*")))
        out = (r.stderr or "") + (r.stdout or "")
        if not ok and ("not a bot" in out or "429" in out):
            # 风控:指数退避自愈,不弃跑
            backoff += 1
            if backoff > 6:
                sys.exit("退避6轮仍被风控,放弃。稍后手动续跑(已存在的会跳过)。")
            wait = 600 * backoff + random.uniform(0, 120)
            print(f"[{i+1}/{len(ids)}] 风控 {vid} → 退避 {wait/60:.0f}min (第{backoff}轮)", flush=True)
            time.sleep(wait)
            continue  # 重试同一个视频
        backoff = 0
        done += ok; fail += (not ok)
        note = "" if ok else " | " + (out.strip().splitlines()[-1] if out.strip() else "?")
        print(f"[{i+1}/{len(ids)}] {'ok ' if ok else 'FAIL'} {vid} {title[:60]}{note}", flush=True)
        i += 1
        time.sleep(random.uniform(a.sleep_min, a.sleep_max))
    print(f"done={done} fail={fail} (已存在的未计入)")


def cmd_videos(a):
    root = BASE / a.slug / "video"
    root.mkdir(parents=True, exist_ok=True)
    ids = a.ids.split(",") if a.ids else Path(a.ids_file).read_text().split()
    for i, vid in enumerate(ids):
        if list(root.glob(f"{vid}.*")):
            continue
        print(f"[{i+1}/{len(ids)}] {vid}")
        run([*cookie_args(), "-f", "bv*[height<=720]+ba/b[height<=720]",
             "-o", f"{root}/{vid}.%(ext)s",
             f"https://www.youtube.com/watch?v={vid}"])
        time.sleep(random.uniform(8, 15))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--slug", default="stefan-3d-ai")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("inventory"); s.add_argument("--channel", required=True)
    s = sub.add_parser("subs"); s.add_argument("--limit", type=int)
    # 实测:15-30s 节奏在账号被标记后仍会连续触发;夜间用 60-120s
    s.add_argument("--sleep-min", type=float, default=15)
    s.add_argument("--sleep-max", type=float, default=30)
    s = sub.add_parser("videos")
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--ids"); g.add_argument("--ids-file")
    a = p.parse_args()
    {"inventory": cmd_inventory, "subs": cmd_subs, "videos": cmd_videos}[a.cmd](a)
