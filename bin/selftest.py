#!/usr/bin/env python3
"""selftest.py — Wave③ 逻辑自测(全在临时 DB/ROOT,不碰生产 state.db)。
覆盖:schema/触发器、search.py 四路加权去重(含 news,mock 网络)、依赖边/优先级/3D/skill_hit、
cache_gc 豁免路径、shared_watch breaking/non、daily_brief 五段。verify.sh 调用它。
真网络(litellm/search news 活探针/gateway)由 verify.sh 另跑。"""
import os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCHEMA = REPO / "config/schema.sql"
sys.path.insert(0, str(REPO / "bin"))
FAILS = []


def check(name, cond):
    print(("✅ " if cond else "❌ ") + name)
    if not cond:
        FAILS.append(name)


def fresh_root():
    d = Path(tempfile.mkdtemp(prefix="agentco-selftest-"))
    (d / "handoff").mkdir(); (d / "kb/90-inbox").mkdir(parents=True); (d / "logs").mkdir()
    subprocess.run(["sqlite3", str(d / "state.db")], stdin=open(SCHEMA), check=True,
                   stdout=subprocess.DEVNULL)
    return d


def with_root(root):
    """把 agentlib/其他模块的 ROOT 重指向临时 root,返回重载后的模块。"""
    import importlib, agentlib
    agentlib.ROOT = root
    return agentlib


def t_schema():
    r = fresh_root()
    tabs = subprocess.run(["sqlite3", str(r/"state.db"), "SELECT name FROM sqlite_master WHERE type='table'"],
                          capture_output=True, text=True).stdout.split()
    check("schema: tasks/events/feedback/seen_events 齐全",
          all(x in tabs for x in ("tasks", "events", "feedback", "seen_events")))
    trg = subprocess.run(["sqlite3", str(r/"state.db"), "SELECT name FROM sqlite_master WHERE type='trigger'"],
                         capture_output=True, text=True).stdout
    check("schema: events 双触发器", "events_no_update" in trg and "events_no_delete" in trg)
    subprocess.run(["sqlite3", str(r/"state.db"), "INSERT INTO events(kind) VALUES('x')"], check=True)
    up = subprocess.run(["sqlite3", str(r/"state.db"), "UPDATE events SET kind='y'"],
                        capture_output=True, text=True)
    check("schema: UPDATE events 报 append-only", "append-only" in (up.stderr + up.stdout))
    shutil.rmtree(r, ignore_errors=True)


def t_search():
    os.environ["BRAVE_API_KEY"] = "x"; os.environ["SERPER_API_KEY"] = "y"
    import search
    def fake(method, url, headers, body=None):
        if "brave.com/res/v1/web" in url:
            return {"web": {"results": [{"url": "https://a.com/x?utm_source=g#f", "title": "Aw", "description": "s"},
                                        {"url": "https://b.com/y/", "title": "B", "description": "s"}]}}
        if "brave.com/res/v1/news" in url:
            return {"results": [{"url": "https://a.com/x", "title": "An", "description": "s"},
                                {"url": "https://n1.com/z", "title": "N1", "description": "s"}]}
        if url.endswith("/search"):
            return {"organic": [{"link": "https://a.com/x/", "title": "As", "snippet": "s"},
                                 {"link": "https://c.com/q", "title": "C", "snippet": "s"}]}
        if url.endswith("/news"):
            return {"news": [{"link": "https://n1.com/z?utm_medium=x", "title": "N1s", "snippet": "s"},
                             {"link": "https://d.com/w", "title": "D", "snippet": "s"}]}
        raise AssertionError(url)
    search._http = fake
    r = fresh_root(); search.ROOT = r
    with_root(r); import agentlib; agentlib.ROOT = r; search.load_env = lambda: None
    path = search.run_search("news 测试", project="p")
    txt = (r / path).read_text()
    check("search: 四路含两 news endpoint 都 ok",
          all(f"{x}: ok(2)" in txt for x in ("brave_web", "brave_news", "serper_web", "serper_news")))
    check("search: 跨路加权去重(a.com 聚合 3 源 score 3.0)", "sources: brave_news, brave_web, serper_web" in txt)
    check("search: news 跨源去重(n1 = brave_news+serper_news)", "brave_news, serper_news" in txt)
    check("search: frontmatter 带 content_hash + source_urls",
          re.search(r"content_hash: \w+", txt) and "source_urls:" in txt)
    shutil.rmtree(r, ignore_errors=True)


def t_dispatch():
    r = fresh_root()
    import agentlib, dispatch
    agentlib.ROOT = r; dispatch.ROOT = r; dispatch.DB = r/"state.db"; dispatch.LOG = r/"logs/d.log"
    import sqlite3
    a = agentlib.enqueue("retriever", "A", "x", project="assembly", priority=1, query="q")
    b = agentlib.enqueue("executor-code", "B", "x", project="assembly", priority=1, depends_on=a)
    g = agentlib.enqueue("executor-3d", "3D", "x", project="vibe-modelling")
    c = agentlib.db()
    st = lambda tid: c.execute("SELECT status FROM tasks WHERE id=?", (tid,)).fetchone()[0]
    check("dispatch: 依赖未 done → waiting_dep", st(b) == "waiting_dep")
    check("dispatch: executor-3d → waiting_gpu(不进主循环)", st(g) == "waiting_gpu")
    db = sqlite3.connect(r/"state.db"); db.row_factory = sqlite3.Row
    row = db.execute("""SELECT id FROM tasks WHERE status='queued' AND (depends_on IS NULL OR depends_on=''
        OR depends_on IN (SELECT id FROM tasks WHERE status='done')) ORDER BY priority,created_at LIMIT 1""").fetchone()
    check("dispatch: 优先级取任务只选就绪的 A", row["id"] == a)
    db.execute("UPDATE tasks SET status='done' WHERE id=?", (a,)); db.commit()
    dispatch.trigger_dependents(db, a)
    check("dispatch: A done → B dep_triggered→queued", st(b) == "queued")
    d = agentlib.enqueue("executor-code", "D", "x", project="assembly")
    e = agentlib.enqueue("executor-code", "E", "x", project="assembly", depends_on=d)
    dispatch.propagate_block(db, {"id": d})   # db 已 row_factory=Row(生产由 main() 保证)
    check("dispatch: D blocked → E dep_failed(不静默挂起)", st(e) == "dep_failed")
    sk = r/"agents/digester/skills/scribe"; sk.mkdir(parents=True)
    (sk/"SKILL.md").write_text("---\nuse_count: 0\n---\n")
    dispatch.record_skill_hits(db, "T-x", "digester", "用 agents/digester/skills/scribe/SKILL.md")
    hit = db.execute("SELECT count(*) FROM events WHERE kind='skill_hit' AND detail='scribe'").fetchone()[0]
    check("dispatch: skill_hit 计数 + use_count bump", hit == 1 and "use_count: 1" in (sk/"SKILL.md").read_text())
    # 难度路由:executor 缺省 medium(GPT),其余缺省 light;显式 heavy 可用;失败不升档(escalate 分支已移除)
    tier = lambda tid: c.execute("SELECT tier FROM tasks WHERE id=?", (tid,)).fetchone()[0]
    check("routing: executor 缺省 medium(tier=1→GPT)", tier(d) == 1
          and dispatch.PROFILE[("executor-code", 1)] == "executor-code-hi")
    h = agentlib.enqueue("retriever", "H", "x", project="assembly", difficulty="heavy")
    check("routing: retriever heavy → kimi-long(tier=2)", tier(h) == 2
          and dispatch.PROFILE[("retriever", 2)] == "retriever-long")
    check("routing: auditor 全档异厂商(恒 ds-reasoner,无 GPT 档)",
          len({dispatch.PROFILE[("auditor", i)] for i in (0, 1, 2)}) == 1)
    check("routing: 失败自动升档已移除", not hasattr(dispatch, "MAX_TIER"))
    shutil.rmtree(r, ignore_errors=True)


def t_cache_gc():
    r = fresh_root()
    (r/"kb/30-projects/assembly/raw").mkdir(parents=True); (r/"kb/30-projects/assembly/decisions").mkdir(parents=True)
    import agentlib, cache_gc
    agentlib.ROOT = r; cache_gc.ROOT = r
    raw = r/"kb/30-projects/assembly/raw"; OLD = time.time()-20*86400
    for n, ch in [("a", "H1"), ("c", "UNREF")]:
        (raw/f"s-{n}.md").write_text(f"---\ncontent_hash: {ch}\n---\n"); os.utime(raw/f"s-{n}.md", (OLD, OLD))
    (r/"kb/30-projects/assembly/decisions/D.md").write_text("依据 content_hash=H1 的信号")
    dele, exe = cache_gc.gc(days=14)
    check("cache_gc: 被决策引用的 raw 豁免保留", any(f.name == "s-a.md" for f in exe) and (raw/"s-a.md").exists())
    check("cache_gc: 未引用旧 raw 删除", any(f.name == "s-c.md" for f in dele) and not (raw/"s-c.md").exists())
    c = agentlib.db()
    d = c.execute("SELECT detail FROM events WHERE kind='cache_gc' ORDER BY id DESC LIMIT 1").fetchone()[0]
    check("cache_gc: 删前记 event 计数正确", "deleted=1" in d and "exempt=1" in d)
    shutil.rmtree(r, ignore_errors=True)


def t_shared():
    r = fresh_root(); comp = r/"kb/00-core/shared/authlib"; comp.mkdir(parents=True)
    subprocess.run(["git", "-C", str(r), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(r), "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "-C", str(r), "config", "user.name", "t"], check=True)
    comp.joinpath("spec.md").write_text("# a\n\n## API契约\n- f(x)\n\n## 说明\nv1\n")
    comp.joinpath("dependents.md").write_text("- assembly\n- video-shorts\n")
    subprocess.run(["git", "-C", str(r), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(r), "commit", "-qm", "i"], check=True)
    import agentlib, shared_watch
    agentlib.ROOT = r; shared_watch.ROOT = r
    comp.joinpath("spec.md").write_text("# a\n\n## API契约\n- f(x)\n\n## 说明\nv2改说明\n")
    check("shared: 非 API 段变 = non-breaking", shared_watch.watch("HEAD") == [("authlib", "non-breaking", [])])
    comp.joinpath("spec.md").write_text("# a\n\n## API契约\n- f(x,y) BREAK\n\n## 说明\nv2改说明\n")
    res = shared_watch.watch("HEAD")
    check("shared: API契约段变 = breaking + 2 dependents review 任务", res[0][1] == "breaking" and len(res[0][2]) == 2)
    shutil.rmtree(r, ignore_errors=True)


def t_brief():
    r = fresh_root()
    import agentlib, daily_brief
    agentlib.ROOT = r; daily_brief.ROOT = r
    c = agentlib.db()
    txt, dec = daily_brief.build_brief(c)
    check("brief: 空 DB 仅健康度段", "📊" in txt and "⚡" not in txt and dec == [])
    c.execute("INSERT INTO tasks(id,agent,title,spec_path,status,project) VALUES('T1','executor-code','X','h','review','assembly')")
    c.execute("INSERT INTO tasks(id,agent,title,spec_path,status,project,updated_at) VALUES('T2','retriever','Y','h','done','assembly',datetime('now'))")
    c.execute("INSERT INTO tasks(id,agent,title,spec_path,status,project) VALUES('T3','executor-code','Z','h','blocked','vs')")
    c.execute("INSERT INTO events(kind,detail) VALUES('shared_breaking','authlib')"); c.commit()
    txt, dec = daily_brief.build_brief(c)
    check("brief: 五段齐全 + 决策项=review 任务", all(m in txt for m in ("⚡", "📦", "🔧", "⏳", "📊")) and dec and dec[0]["id"] == "T1")
    shutil.rmtree(r, ignore_errors=True)


if __name__ == "__main__":
    for fn in (t_schema, t_search, t_dispatch, t_cache_gc, t_shared, t_brief):
        try:
            fn()
        except Exception as e:
            check(f"{fn.__name__} 抛异常: {e}", False)
    print(f"\n---- selftest {'PASS' if not FAILS else 'FAIL: ' + ', '.join(FAILS)} ----")
    sys.exit(1 if FAILS else 0)
