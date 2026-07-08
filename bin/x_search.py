#!/usr/bin/env python3
"""x_search.py — L2 深潜层 X(Twitter)分支(社区原声采集)。

产出 `kind: community_raw`(带回复线程=用户原声),对外契约同 reddit_deep.py:
吃 topic 吐 raw 文件,下游(digester)只读离线。deepdive_preprocess 里被调用。

与 reddit_deep 的区别:twitter-cli 直接返回结构化 JSON,**无需 LLM 驱动**——本脚本
确定性调用 CLI 并格式化(零幻觉、零模型成本)。原声在回复里,故 search 出高赞推文后,
对最高互动的几条 `tweet <id>` 抓回复线程。

认证:twitter-cli 读环境变量 TWITTER_AUTH_TOKEN / TWITTER_CT0(最高优先级);
本脚本从 .env 的 X_AUTH_TOKEN / X_CT0 注入。⚠️ 用的是一次性小号(@hbzheng_x),
非浏览器 API 调用有封号风险,故调用量克制(1 search + 少量 thread 抓取)。

CLI:  x_search.py --project <proj> --topic "<话题>" [--posts 8] [--threads 3]
API:  from x_search import run_x_search; path = run_x_search(topic, project)
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import ROOT, load_env

load_env()
TWITTER_BIN = (os.environ.get("TWITTER_BIN")
               or str(Path.home() / ".agent-reach-venv/bin/twitter")
               or shutil.which("twitter"))
TIMEOUT = 60


def _tw(args):
    """调用 twitter-cli(compact JSON),返回解析后的 list;失败抛异常。"""
    if not TWITTER_BIN or not Path(TWITTER_BIN).exists():
        raise RuntimeError(f"twitter-cli 未安装({TWITTER_BIN});装:pip install twitter-cli")
    env = os.environ.copy()
    tok, ct0 = os.environ.get("X_AUTH_TOKEN", ""), os.environ.get("X_CT0", "")
    if not tok or not ct0:
        raise RuntimeError("X_AUTH_TOKEN / X_CT0 未在 .env 配置")
    env.update({"TWITTER_AUTH_TOKEN": tok, "TWITTER_CT0": ct0})
    r = subprocess.run([TWITTER_BIN, "-c", *args], capture_output=True, text=True,
                       timeout=TIMEOUT, env=env)
    if r.returncode != 0:
        raise RuntimeError(f"twitter {args[0]} 失败: {(r.stderr or r.stdout)[:200]}")
    out = r.stdout.strip()
    data = json.loads(out) if out else []
    return data if isinstance(data, list) else [data]


def _handle(author):
    return (author or "").lstrip("@").strip()


def _url(t):
    h = _handle(t.get("author"))
    return f"https://x.com/{h}/status/{t.get('id')}" if h and t.get("id") else ""


def _slug(s):
    s = re.sub(r"[^\w一-鿿]+", "-", s.strip().lower()).strip("-")
    return (s[:40] or "topic").rstrip("-")


def run_x_search(topic, project="default", posts=8, threads=3):
    if not topic or not topic.strip():
        raise ValueError("topic 为空")
    fetch_ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    found = _tw(["search", topic, "-n", str(posts)])
    # 保留 twitter-cli 的原生相关性排序:X 上按赞重排会把病毒式无关推文顶上来
    # (实测 "simulation" 泛匹配到 5k赞的游戏 mod)。相关性优先,按帖 id 去重。
    seen, uniq = set(), []
    for t in found:
        if t.get("id") and t["id"] not in seen:
            seen.add(t["id"]); uniq.append(t)
    urls, sections = [], []
    for t in uniq[:threads]:
        tid, u = t.get("id"), _url(t)
        if not tid:
            continue
        urls.append(u)
        try:
            thread = _tw(["tweet", str(tid)])
        except Exception as e:
            thread = [t]   # 回复抓取失败:至少保留主推,标缺口
            sections.append(f"> 采集缺口:tweet {tid} 回复抓取失败({str(e)[:80]})")
        main = thread[0] if thread else t
        replies = thread[1:] if len(thread) > 1 else []
        replies.sort(key=lambda r: (r.get("likes", 0) or 0), reverse=True)
        sec = [f"## [@{_handle(main.get('author'))}] {(main.get('text') or '')[:120]}",
               f"- url: {u}",
               f"- score: ▲{main.get('likes',0)}赞 · {main.get('rts',0)}转 · time: {main.get('time','?')}",
               f"- 主推原声: {(main.get('text') or '').strip()}",
               "- 回复线程(原声):"]
        if replies:
            for rp in replies[:6]:
                txt = (rp.get("text") or "").strip().replace("\n", " ")
                sec.append(f"  - ▲{rp.get('likes',0)} @{_handle(rp.get('author'))}: \"{txt[:400]}\"")
        else:
            sec.append("  - (无回复或未抓到)")
        sections.append("\n".join(sec))

    if not urls:
        raise RuntimeError(f"x_search 空返:'{topic}' 无结果(query 太窄或 X 风控)")

    urls = sorted(set(u for u in urls if u))
    body = "\n\n".join(sections)
    h = hashlib.sha256()
    for u in urls:
        h.update(u.encode())
    h.update(body.encode())
    content_hash = h.hexdigest()[:16]

    raw_dir = ROOT / "kb/30-projects" / project / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_path = raw_dir / f"community-x-{_slug(topic)}-{datetime.now():%Y%m%d}.md"
    lines = ["---", "kind: community_raw", "platform: x",
             f"topic: {json.dumps(topic, ensure_ascii=False)}",
             f"fetch_ts: {fetch_ts}", f"content_hash: {content_hash}",
             f"project: {project}", "collector: twitter-cli(确定性,无LLM)", "source_urls:"]
    lines += [f"  - {u}" for u in urls]
    lines += ["---", "",
              f"# 社区原声:X / {topic}", "",
              "> twitter-cli 深潜采集(确定性格式化,无模型加工)。**原声在回复线程里**;"
              "digester 蒸馏时逐条痛点回指具体推文/回复(带▲赞),勿把线程综合成一句。"
              "注意 X 噪声高(引流/宗教/空回复),digester 需甄别有效信号。",
              "", body, ""]
    out_path.write_text("\n".join(lines))
    return str(out_path.relative_to(ROOT))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="default")
    ap.add_argument("--topic", required=True)
    ap.add_argument("--posts", type=int, default=8)
    ap.add_argument("--threads", type=int, default=3)
    a = ap.parse_args()
    print(run_x_search(a.topic, a.project, a.posts, a.threads))
