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
    path = search.run_search("news 测试", project="p", sources=[])
    txt = (r / path).read_text()
    check("search: 四路含两 news endpoint 都 ok",
          all(f"{x}: ok(2)" in txt for x in ("brave_web", "brave_news", "serper_web", "serper_news")))
    check("search: 跨路加权去重(a.com 聚合 3 源 score 3.0)", "sources: brave_news, brave_web, serper_web" in txt)
    check("search: news 跨源去重(n1 = brave_news+serper_news)", "brave_news, serper_news" in txt)
    check("search: frontmatter 带 content_hash + source_urls",
          re.search(r"content_hash: \w+", txt) and "source_urls:" in txt)
    # 双语多 query:8 路记账带语言标签,sources 仍纯路由名(跨语聚合去重)
    p2 = search.run_search(["news 测试", "news test"], project="p", sources=[])
    t2 = (r / p2).read_text()
    check("search: 双语8路记账+跨语聚合",
          "brave_web[zh0]: ok(2)" in t2 and "brave_web[en1]: ok(2)" in t2
          and "sources: brave_news, brave_web, serper_web" in t2)
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
    # envelope 规范化:剥围栏手写 envelope,溯源字段继承,身份字段由 dispatcher 注入
    raw_final = ("分析正文...\n\n```yaml\ntask_id: T-x\nagent: auditor\nmodel: claude-sonnet-4\n"
                 "tier: 2\nstatus: ok\nsource_urls: [https://a.com]\ncontent_hash: abc123\n```")
    body2, urls2, ch2 = dispatch.split_envelope(raw_final)
    check("envelope: 剥离围栏手写块+继承溯源", body2 == "分析正文..." and urls2 == "[https://a.com]" and ch2 == "abc123")
    envt = {"id": "T-y", "agent": "auditor", "tier": 0, "project": "assembly", "depends_on": None}
    env = dispatch.canonical_envelope(envt, "auditor", urls2, ch2, ["handoff/assembly/T-y.result.md"])
    check("envelope: dispatcher 注入身份字段(model 非自报/tier 正确/无契约外字段)",
          "model: qwen-max" in env and "tier: 0" in env and "status:" not in env and "content_hash: abc123" in env)
    b3, u3, c3 = dispatch.split_envelope("纯正文无envelope")
    check("envelope: 无手写块时原文保留", b3 == "纯正文无envelope" and u3 is None and c3 is None)
    # spec 丢失 → blocked(单任务坏文件不许崩掉调度器主循环)
    f = agentlib.enqueue("retriever", "F", "x", project="assembly")
    frow = dict(db.execute("SELECT * FROM tasks WHERE id=?", (f,)).fetchone())
    (r/frow["spec_path"]).unlink()
    dispatch.feishu = lambda *a: None   # 测试不真推飞书
    dispatch.run_task(db, frow)
    check("dispatch: spec 丢失 → blocked 不崩", st(f) == "blocked")
    sk = r/"agents/digester/skills/scribe"; sk.mkdir(parents=True)
    (sk/"SKILL.md").write_text("---\nuse_count: 0\n---\n")
    dispatch.record_skill_hits(db, "T-x", "digester", "用 agents/digester/skills/scribe/SKILL.md")
    hit = db.execute("SELECT count(*) FROM events WHERE kind='skill_hit' AND detail='scribe'").fetchone()[0]
    check("dispatch: skill_hit 计数 + use_count bump", hit == 1 and "use_count: 1" in (sk/"SKILL.md").read_text())
    # 难度路由:executor 缺省 medium(GPT),其余缺省 light;显式 heavy 可用;失败不升档(escalate 分支已移除)
    tier = lambda tid: c.execute("SELECT tier FROM tasks WHERE id=?", (tid,)).fetchone()[0]
    check("routing: executor 缺省 medium(tier=1→GPT)", tier(d) == 1
          and dispatch.PROFILE[("executor-code", 1)] == "executor"
          and dispatch.PROFILES["executor"]["model"].startswith("gpt-")
          and dispatch.PROFILE[("executor-code", 0)] == "executor-ds")
    h = agentlib.enqueue("retriever", "H", "x", project="assembly", difficulty="heavy")
    check("routing: retriever heavy → kimi-long(tier=2)", tier(h) == 2
          and dispatch.PROFILE[("retriever", 2)] == "retriever-long")
    check("routing: heavy 缺省 ttl 放宽 1800s",
          c.execute("SELECT ttl_sec FROM tasks WHERE id=?", (h,)).fetchone()[0] == 1800)
    check("routing: auditor 全档异厂商(恒 qwen-max,无 GPT 档)",
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


def t_sign():
    import agentlib, time as _t
    os.environ["GATEWAY_TOKEN"] = "test-secret"
    s = agentlib.sign("T-1", "adopt")
    check("sign: 正签验证通过", agentlib.verify_sig(s, "T-1", "adopt"))
    check("sign: 字段被篡改拒绝", not agentlib.verify_sig(s, "T-1", "reject"))
    expired = agentlib.sign("T-1", "adopt", exp=int(_t.time())-10)
    check("sign: 过期令牌拒绝", not agentlib.verify_sig(expired, "T-1", "adopt"))


def t_proposals():
    r = fresh_root(); (r/"handoff").exists()
    import agentlib, proposals
    agentlib.ROOT = r
    proposals.push = lambda *a: None
    doc = ("周报...\n### PROPOSAL: 收紧 retriever turn 上限\ntarget: agents/retriever/AGENT.md\n"
           "```\nturn 上限 5 → 4\n```\n中间叙述\n### VERIFY P-2026W01-01: ok event#12 显示已生效\n")
    f = r/"weekly.md"; f.write_text(doc)
    c = agentlib.db()
    c.execute("INSERT INTO proposals(id,week,title,status,apply_task) VALUES('P-2026W01-01','2026W01','旧提议','applied','T-old')")
    c.commit()
    proposals.ingest(str(f), "T-wr")
    row = c.execute("SELECT * FROM proposals WHERE title LIKE '收紧%'").fetchone()
    check("proposals: PROPOSAL 区块解析入库(title/target/diff)",
          row and row["target"] == "agents/retriever/AGENT.md" and "turn 上限" in row["diff"])
    check("proposals: VERIFY ok → applied 转 verified",
          c.execute("SELECT status FROM proposals WHERE id='P-2026W01-01'").fetchone()[0] == "verified")
    proposals.set_status(row["id"], "adopt")
    p2 = c.execute("SELECT status,apply_task FROM proposals WHERE id=?", (row["id"],)).fetchone()
    check("proposals: adopt → 自动入队 apply 任务", p2["status"] == "adopted" and (p2["apply_task"] or "").startswith("T-"))
    agentlib.apply_review(p2["apply_task"], "adopt")   # apply 任务尚在 queued,不可验收 → 状态不变
    c2 = agentlib.db()
    c2.execute("UPDATE tasks SET status='review' WHERE id=?", (p2["apply_task"],)); c2.commit()
    agentlib.apply_review(p2["apply_task"], "adopt")
    check("proposals: apply 任务人工采纳 → applied(等周复检)",
          c2.execute("SELECT status FROM proposals WHERE id=?", (row["id"],)).fetchone()[0] == "applied")
    shutil.rmtree(r, ignore_errors=True)


def t_gateway_parse():
    import feishu_gateway as g
    t = g.strip_mentions("@_user_1 请retriever执行一个信息搜集任务,全球层面因果推理进展")
    p = g.parse_dispatch(t)
    check("gateway: @机器人+自然语言'请retriever执行'解析为派单",
          p and p[0] == "retriever" and p[1].startswith("一个信息搜集任务"))
    check("gateway: '派 digester xx' 兼容", g.parse_dispatch("派 digester 总结本周") == ("digester", "总结本周"))
    check("gateway: 裸 executor 别名到 executor-code",
          g.parse_dispatch("让executor 跑数据清洗")[0] == "executor-code")
    check("gateway: 非派单句('请注意…')不误入队", g.parse_dispatch("请注意明天的评审") is None)
    check("gateway: 未知 agent 不入队", g.parse_dispatch("派 foo 干活") is None)


def t_bridge():
    import bridge
    ok = bridge.validate_plan({"intent": "dispatch", "note": "n", "tasks": [
        {"agent": "retriever", "title": "全球因果推理调研", "body": "目标...验收...",
         "difficulty": "light", "query_zh": "因果推理 3D建模", "query_en": "causal reasoning 3D generation"},
        {"agent": "executor", "title": "整理", "body": "把上面产出归档", "depends_idx": 0}]})
    check("bridge: 合法方案通过+en优先+别名规整",
          ok and ok["tasks"][0]["queries"][0].startswith("causal") and
          ok["tasks"][1]["agent"] == "executor-code" and ok["tasks"][1]["depends_idx"] == 0)
    check("bridge: 未知agent整方案拒绝",
          bridge.validate_plan({"intent": "dispatch", "tasks": [{"agent": "root", "body": "rm -rf"}]}) is None)
    check("bridge: 非法intent拒绝", bridge.validate_plan({"intent": "shell", "tasks": []}) is None)
    check("bridge: 伪造task_ref格式丢弃",
          bridge.validate_plan({"intent": "status", "task_ref": "../../etc/passwd"})["task_ref"] is None)
    check("bridge: depends_idx 前向引用置空",
          bridge.validate_plan({"intent": "dispatch", "tasks": [
              {"agent": "digester", "body": "x", "depends_idx": 3}]})["tasks"][0]["depends_idx"] is None)
    check("bridge: retriever 无query时回退标题",
          bridge.validate_plan({"intent": "dispatch", "tasks": [
              {"agent": "retriever", "title": "查A", "body": "b"}]})["tasks"][0]["queries"] == ["查A"])


def t_kb_lint():
    r = Path(tempfile.mkdtemp(prefix="agentco-kblint-"))
    import kb_lint
    kb_lint.ROOT = r; kb_lint.KB = r/"kb"
    (r/"kb/00-core").mkdir(parents=True); (r/"kb/30-projects/p1").mkdir(parents=True)
    (r/"kb/00-core/concept-index.md").write_text("- [关节](joints.md) | 权威\n- [装配](asm.md) | 权威\n")
    (r/"kb/00-core/joints.md").write_text("ok 见 [缺](nope.md)")
    (r/"kb/30-projects/p1/_index.md").write_text("- [关节](x.md) | 项目内\n")
    issues = kb_lint.lint()
    check("kb_lint: 死链检出", any("nope.md" in i for i in issues))
    check("kb_lint: 全局/项目概念冗余检出", any("关节" in i and "冗余" in i for i in issues))
    shutil.rmtree(r, ignore_errors=True)


if __name__ == "__main__":
    for fn in (t_schema, t_search, t_dispatch, t_cache_gc, t_shared, t_brief, t_sign, t_proposals,
               t_gateway_parse, t_bridge, t_kb_lint):
        try:
            fn()
        except Exception as e:
            check(f"{fn.__name__} 抛异常: {e}", False)
    print(f"\n---- selftest {'PASS' if not FAILS else 'FAIL: ' + ', '.join(FAILS)} ----")
    sys.exit(1 if FAILS else 0)
