#!/usr/bin/env python3
"""agentco dispatcher (Wave④) — 队列在引擎外,claude -p 只当 worker(2026-07-07 由 codex exec 切换)。
cron 每 5 分钟;四域独立文件锁并行消费(域内串行),慢任务只阻塞本域。

Wave④ 变更(引擎迁移+出站重构):
- worker: codex exec -p → claude -p(经 litellm /v1/messages,ANTHROPIC_BASE_URL 注入);
  profile 定义移至 config/claude-profiles/profiles.json(model=litellm别名/max_turns/instructions)。
- envelope 2.0:产出须含 ```report 块(tldr/highlights/action_needed/confidence),
  Stop hook(bin/report_stop_hook.py)协议级强制;缺块记 report_missing 事件进周治理。
- 出站:notifier.py 一任务一卡原地更新(running/done/review/blocked),模型独白永不上卡;
  应用凭据/chat_id 缺失时降级 webhook 文本,信号永不丢。

Wave③ 变更:
- 工具域 4:retriever / executor-{code,data,3d} / digester / auditor(worker=profile 变体)。
- 路由:retriever/digester/auditor 产出→inbox&done;executor→review(机器验收)。
- retriever 预处理:codex 前先跑 search.py(query 取自 spec frontmatter)→ raw 注入上下文,模型不联网。
- 取任务:status='queued' 且依赖已 done,ORDER BY priority,created_at;依赖未 done 的任务是 waiting_dep,不占 worker。
- 依赖边:任务 done→扫 waiting_dep(depends_on==该 tid)→queued+dep_triggered;任务 blocked→下游标 dep_failed 进日报。
- 3D:executor-3d 入队即 waiting_gpu,不进主循环(bin/gpu_worker.sh 本地拉取)。
- skill_hit:spec 引用 skill 路径时记 event 并 bump use_count。
- 难度路由(Wave③后修订):tier=难度档(0=light 1=medium 2=heavy),派单时定;
  失败同档重试 2 次即 blocked,不再自动升档换厂商。
"""
import fcntl, json, multiprocessing, os, re, sqlite3, subprocess, sys, threading
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from agentlib import claude_bin, load_env, enqueue
load_env()  # cron 环境无 .env 变量;claude/notifier 子进程靠继承 os.environ 拿 LITELLM_MASTER_KEY 等

ROOT = Path(__file__).resolve().parent.parent
DB, TRACES, LOG = ROOT/"state.db", ROOT/"traces", ROOT/"logs/dispatch.log"
MAX_ATTEMPTS = 2
RECRAWL_MAX_DEPTH = 2       # gaps 自动补抓硬上限:原始→d1→d2 后强制收敛(审计收口)
GAPS_MAX_ITEMS = 3         # 单次补抓/深潜最多取的缺口条目数,防 retriever 一次甩一堆
DEEPDIVE_SCRIPT = {        # 社区深潜采集脚本(文件存在=该路上线;未就位只记事件,不造死任务)
    "reddit": "bin/reddit_deep.py",       # ✅ ds-chat worker 驱动 reddit-research-mcp
    "x": "bin/x_search.py",               # ✅ twitter-cli 确定性采集
    "xiaohongshu": "bin/xhs_search.py",   # ⏳ 待建(需 HB 扫码登录);文件不存在→gate 保持 pending
}
_RECRAWL_TAG = re.compile(r"\[auto-recrawl d(\d+)\]")

# 难度路由:tier=难度档(0=light 1=medium 2=heavy),入队时定,失败不自动升档。
# 多模态仅 GPT 通道(-hi profile)可用;auditor 刻意不给 GPT(审 executor 产出须异厂商)。
DIFF = {0: "light", 1: "medium", 2: "heavy"}
PROFILES = json.loads((ROOT/"config/claude-profiles/profiles.json").read_text())
PROFILE = {  # (agent, tier) -> claude profile(见 config/claude-profiles/profiles.json)
    # executor 两档制(2026-07-08):light=executor-ds(ds-chat 杂活),medium/heavy=executor(gpt-5.5 代码开发)
    ("retriever", 0): "retriever",         ("retriever", 1): "retriever",         ("retriever", 2): "retriever-long",
    ("executor-code", 0): "executor-ds",   ("executor-code", 1): "executor",      ("executor-code", 2): "executor",
    ("executor-data", 0): "executor-ds",   ("executor-data", 1): "executor",      ("executor-data", 2): "executor",
    ("executor-3d", 0): "executor-3d",     ("executor-3d", 1): "executor-3d",     ("executor-3d", 2): "executor-3d",
    ("digester", 0): "digester",           ("digester", 1): "digester",           ("digester", 2): "digester-hi",
    ("auditor", 0): "auditor",             ("auditor", 1): "auditor",             ("auditor", 2): "auditor",
}
VALID_AGENTS = {"retriever", "executor-code", "executor-data", "executor-3d", "digester", "auditor"}
INBOX_AGENTS = {"retriever", "digester", "auditor"}   # 产出→inbox&done;其余(executor)→review

def log(msg):
    line = f"{datetime.now().isoformat(timespec='seconds')} {msg}"
    print(line); LOG.parent.mkdir(exist_ok=True); LOG.open("a").write(line+"\n")

def feishu(text):
    subprocess.run([str(ROOT/"bin/feishu_push.sh"), text], check=False)

def feishu_archive(path, name):
    """md 产物存档到飞书云文档 agentco 目录,返回链接;未配凭据/失败返回 None(降级本地路径)。"""
    try:
        r = subprocess.run([sys.executable, str(ROOT/"bin/feishu_archive.py"), str(path), name],
                           capture_output=True, text=True, timeout=30)
        return r.stdout.strip() if r.returncode == 0 and r.stdout.strip().startswith("http") else None
    except Exception:
        return None

def ev(db, task_id, agent, kind, detail=""):
    db.execute("INSERT INTO events(task_id,agent,kind,detail) VALUES(?,?,?,?)",
               (task_id, agent, kind, detail)); db.commit()

# ---- skill 心跳:spec 引用 skill 路径 → skill_hit + bump use_count ----
_SKILL_RE = re.compile(r"skills/([A-Za-z0-9_\-]+)")

def record_skill_hits(db, tid, agent, spec):
    for sid in sorted(set(_SKILL_RE.findall(spec))):
        ev(db, tid, agent, "skill_hit", sid)
        for f in ROOT.glob(f"**/skills/{sid}/SKILL.md"):
            txt = f.read_text()
            m = re.search(r"^use_count:\s*(\d+)\s*$", txt, re.M)
            if m:
                f.write_text(txt[:m.start(1)] + str(int(m.group(1)) + 1) + txt[m.end(1):])

# ---- envelope 规范化:溯源字段(source_urls/content_hash)信模型,身份字段(model/tier/…)信 dispatcher ----
# 背景:envelope 由模型手写时格式漂移(yaml 围栏包裹/tier 错/model 自报不可信,T-20260706-003 审计实锤)。
_ENV_LINE = re.compile(r"^(?:[\w_]+:.*|-\s.*|---|```(?:yaml)?|#\s*envelope.*|\s*)$")

def split_envelope(final):
    """从产出末尾剥离模型手写 envelope(容忍 ``` 围栏/---/# envelope 标头),
    返回 (正文, source_urls行, content_hash)。无 envelope 返回 (原文, None, None)。"""
    lines = final.rstrip().splitlines()
    i = len(lines)
    while i > 0 and _ENV_LINE.match(lines[i-1]):
        i -= 1
    tail = "\n".join(lines[i:])
    if "task_id:" not in tail and "content_hash:" not in tail:
        return final.rstrip(), None, None
    m_urls = re.search(r"^source_urls:\s*(.+)$", tail, re.M)
    urls = m_urls.group(1).strip() if m_urls else None
    if urls is None and re.search(r"^source_urls:\s*$", tail, re.M):  # yaml 多行列表
        block = re.search(r"^source_urls:\s*\n((?:\s*-\s.*\n?)+)", tail, re.M)
        if block:
            urls = "[" + ", ".join(x.strip("- ").strip() for x in block.group(1).splitlines()) + "]"
    m_hash = re.search(r"^content_hash:\s*(\S+)", tail, re.M)
    return "\n".join(lines[:i]).rstrip(), urls, (m_hash.group(1) if m_hash else None)

def profile_model(profile):
    return PROFILES.get(profile, {}).get("model", "unknown")


# ---- claude -p worker 调用 ----
WORKER_TOOLS_ALLOW = "Read,Glob,Grep"           # 与 codex read-only 沙箱等价:只读,产出经最终消息落盘
WORKER_TOOLS_DENY = "Bash,Write,Edit,NotebookEdit,WebSearch,WebFetch,Task,TodoWrite"

def worker_cmd_env(profile, max_turns_override=None):
    """构造 claude -p 命令与环境。spec 经 stdin 注入(防长 spec 撑爆 argv/与变长 flag 冲突)。"""
    prof = PROFILES[profile]
    instr = (ROOT/"config/profile-instructions"/prof["instructions"]).read_text()
    instr += (ROOT/"config/profile-instructions/_report.md").read_text()
    cmd = [claude_bin(), "-p", "--model", prof["model"],
           "--max-turns", str(max_turns_override or prof["max_turns"]),
           "--output-format", "json", "--strict-mcp-config", "--setting-sources", "",
           "--settings", str(ROOT/"config/claude-profiles/worker-settings.json"),
           "--allowedTools", WORKER_TOOLS_ALLOW, "--disallowedTools", WORKER_TOOLS_DENY,
           "--append-system-prompt", instr]
    env = os.environ.copy()
    if prof.get("max_thinking_tokens"):   # effort 档位(profile 级);spec 里写 ultrathink 等关键词是任务级
        env["MAX_THINKING_TOKENS"] = str(prof["max_thinking_tokens"])
    env.update({
        "CLAUDE_CONFIG_DIR": str(ROOT/".claude-worker"),   # 与主会话配置隔离
        "ANTHROPIC_BASE_URL": "http://127.0.0.1:4000",     # litellm /v1/messages
        "ANTHROPIC_AUTH_TOKEN": os.environ.get("LITELLM_MASTER_KEY", ""),
        "ANTHROPIC_SMALL_FAST_MODEL": "ds-chat",           # harness 后台小调用也走廉价档
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    })
    return cmd, env

def canonical_envelope(t, profile, urls, chash, artifacts):
    return ("---\n"
            f"task_id: {t['id']}\nagent: {t['agent']}\nmodel: {profile_model(profile)}\n"
            f"tier: {t['tier']}\nproject: {t['project'] or 'default'}\n"
            f"depends_on: {t['depends_on'] or 'null'}\n"
            f"source_urls: {urls if urls else '[]'}\ncontent_hash: {chash or ''}\n"
            f"artifacts: [{', '.join(artifacts)}]\n---")

# ---- retriever 预处理:跑 search.py,把 raw 路径注入上下文 ----
def search_preprocess(db, t, spec):
    # query 行可多条(query: / query_en: / query_zh: / query_2: 都认,鼓励多聚焦子query)
    queries = [q.strip().strip('"').strip("'")
               for q in re.findall(r"^query(?:_[a-z0-9]+)?:\s*(.+?)\s*$", spec, re.M) if q.strip()]
    if not queries:
        log(f"{t['id']} retriever 无 query 字段,跳过搜索预处理")
        return spec
    m = re.search(r"^sources:\s*(.+)$", spec, re.M)   # 垂直/站内路由(github,reddit,hn,x,xiaohongshu,wechat)
    srcs = [s.strip() for s in m.group(1).split(",") if s.strip()] if m else None
    try:
        from search import run_search
        raw = run_search(queries, project=t["project"] or "default", sources=srcs)
        ev(db, t["id"], t["agent"], "search", raw)
        log(f"{t['id']} search.py → {raw}")
        return (f"# 已抓取搜索原料(只读它分析,禁止联网)\n路径:{raw}\n"
                f"内容见该文件;其 frontmatter 的 content_hash/source_urls 必须继承进你的 envelope。\n\n" + spec)
    except Exception as e:
        ev(db, t["id"], t["agent"], "search_fail", str(e)[:200])
        log(f"{t['id']} search.py 失败:{e}")
        return spec

# ---- digester 深潜预处理:跑 reddit_deep/x_search 抓 community_raw,把路径注入上下文 ----
# 与 search_preprocess 同构:采集(可能带 MCP/cookie)封在独立脚本里,digester 只读离线 community_raw。
def deepdive_preprocess(db, t, spec):
    plat = (re.search(r"^deepdive_platform:\s*(.+?)\s*$", spec, re.M) or [None, ""])
    plat = plat.group(1).strip().lower() if hasattr(plat, "group") else ""
    topic = re.search(r"^deepdive_topic:\s*(.+?)\s*$", spec, re.M)
    if not plat or not topic:
        return spec   # 非深潜 digester 任务(常规蒸馏),原样放行
    topic = topic.group(1).strip()
    script = DEEPDIVE_SCRIPT.get(plat)
    if not (script and (ROOT/script).exists()):
        ev(db, t["id"], t["agent"], "deepdive_script_missing", f"{plat}")
        return spec + f"\n\n# ⚠️ 深潜采集脚本未就位({plat}):无 community_raw 可读,如实输出 BLOCKED,勿凭先验编造原声。"
    entry = {"reddit": ("reddit_deep", "run_reddit_deep"),
             "x": ("x_search", "run_x_search"),
             "xiaohongshu": ("xhs_search", "run_xhs_search")}.get(plat)
    if not entry:
        ev(db, t["id"], t["agent"], "deepdive_unknown_platform", plat)
        return spec + f"\n\n# ⚠️ 未知深潜平台({plat}):无 community_raw,如实输出 BLOCKED。"
    try:
        mod = __import__(entry[0])
        fn = getattr(mod, entry[1])
        raw = fn(topic, project=t["project"] or "default")
        ev(db, t["id"], t["agent"], "deepdive", f"{plat} → {raw}")
        log(f"{t['id']} deepdive({plat}) → {raw}")
        return (f"# 已抓取社区原声(只读它分析,禁止联网/MCP)\n路径:{raw}\n"
                f"kind=community_raw,原声在高赞评论里;其 frontmatter 的 content_hash/source_urls 继承进 envelope。\n\n" + spec)
    except Exception as e:
        ev(db, t["id"], t["agent"], "deepdive_fail", f"{plat}: {str(e)[:180]}")
        log(f"{t['id']} deepdive({plat}) 失败:{e}")
        return spec + f"\n\n# ⚠️ 深潜采集失败({plat}):{str(e)[:120]}。无 community_raw,如实输出 BLOCKED。"


# ---- 依赖注入:上游产出路径显式给下游(协作只认带 hash 的 artifact,不让 worker 自己找) ----
def dep_preprocess(db, t, spec):
    dep = t["depends_on"]
    if not dep:
        return spec
    r = db.execute("SELECT result_path FROM tasks WHERE id=?", (dep,)).fetchone()
    if r and r["result_path"] and (ROOT/r["result_path"]).exists():
        return (f"# 上游产出(depends_on={dep})\n路径:{r['result_path']}\n"
                f"它是你的输入源:先读它;其 envelope 的 content_hash/source_urls 必须继承进你的 envelope。\n\n" + spec)
    ev(db, t["id"], t["agent"], "dep_artifact_missing", str(dep))
    return spec


# ---- gaps 补抓闭环:retriever 产出机读 gaps 块 → dispatcher 自动补抓/派深潜 ----
# 审计收口:每轮补抓都是一条真实入队任务(DB 可见/可预算控),深度用 title 标记承载,
# RECRAWL_MAX_DEPTH 硬上限后强制收敛,禁止无限刷 ds-chat。
def parse_gaps(text):
    """提取产出里的 ```gaps 围栏块 → dict。解析失败/无块返回 {}。"""
    import yaml
    m = re.search(r"```gaps\s*\n(.*?)```", text, re.S)
    if not m:
        return {}
    try:
        d = yaml.safe_load(m.group(1))
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}

def _clean_list(v):
    return [x for x in (v or []) if x][:GAPS_MAX_ITEMS] if isinstance(v, list) else []

def handle_gaps(db, t, final):
    """retriever 任务 done 后调用:读 gaps 块,派补抓(need_recrawl)/深潜(need_deepdive)。"""
    if t["agent"] != "retriever":
        return
    gaps = parse_gaps(final)
    if not gaps:
        return
    title0 = t["title"] or "intel"
    m = _RECRAWL_TAG.search(title0)
    depth = int(m.group(1)) if m else 0
    base_title = _RECRAWL_TAG.sub("", title0).strip()
    proj, pri = t["project"] or "default", (t["priority"] if t["priority"] is not None else 2)
    recrawl = _clean_list(gaps.get("need_recrawl"))
    if recrawl and depth < RECRAWL_MAX_DEPTH:
        nid = enqueue("retriever", f"{base_title} [auto-recrawl d{depth+1}]",
                      "gaps 自动补抓:就下列精炼 query 重抓,聚焦上一轮的检索盲区。",
                      ttl=t["ttl_sec"], notify=0, project=proj, priority=pri, query=recrawl)
        ev(db, t["id"], t["agent"], "gaps_recrawl", f"{nid} d{depth+1} n={len(recrawl)}")
        log(f"{t['id']} gaps→补抓 {nid} (d{depth+1}) queries={recrawl}")
    elif recrawl:
        ev(db, t["id"], t["agent"], "gaps_recrawl_capped", f"depth={depth} 已达上限{RECRAWL_MAX_DEPTH}")
    for dd in _clean_list(gaps.get("need_deepdive")):
        plat = ((dd.get("platform") if isinstance(dd, dict) else "") or "").strip().lower()
        target = (dd.get("target") if isinstance(dd, dict) else str(dd)) or ""
        script = DEEPDIVE_SCRIPT.get(plat)
        if script and (ROOT/script).exists() and target.strip():
            # 派 digester 任务;实际社区采集由 deepdive_preprocess 跑 reddit_deep/x_search 落 community_raw 后注入
            body = ("社区原声深潜:dispatcher 已用采集脚本抓好 community_raw 注入你的上下文,"
                    "你只读它做痛点/需求/机会蒸馏(原声在高赞评论里,逐条回指)。\n"
                    f"deepdive_platform: {plat}\ndeepdive_topic: {target}")
            nid = enqueue("digester", f"社区深潜:{plat} {target[:40]}", body,
                          notify=0, project=proj, priority=pri)
            ev(db, t["id"], t["agent"], "gaps_deepdive", f"{nid} {plat} {target[:60]}")
            log(f"{t['id']} gaps→深潜 {nid} ({plat}):{target[:60]}")
        else:   # 采集脚本未就位/话题空:记事件,不造依赖不存在工具的死任务
            ev(db, t["id"], t["agent"], "gaps_deepdive_pending", f"{plat} {target[:60]}")
            log(f"{t['id']} gaps→深潜挂起(脚本未就位 {plat}):{target[:60]}")


def run_task(db, t):
    tid, agent, tier = t["id"], t["agent"], t["tier"]
    profile = PROFILE.get((agent, tier))
    if not profile:
        ev(db, tid, agent, "block", f"no profile for ({agent},{tier})")
        db.execute("UPDATE tasks SET status='blocked',updated_at=datetime('now') WHERE id=?", (tid,)); db.commit()
        propagate_block(db, t); return
    spec_file = ROOT/t["spec_path"]
    if not spec_file.exists():   # spec 丢失(如项目目录被清理):blocked 进日报,绝不让单任务崩掉整个调度器
        ev(db, tid, agent, "block", f"spec missing: {t['spec_path']}")
        db.execute("UPDATE tasks SET status='blocked',updated_at=datetime('now') WHERE id=?", (tid,)); db.commit()
        feishu(f"🛑 {tid} {t['title']} BLOCKED:spec 文件丢失 {t['spec_path']},需人工裁决")
        propagate_block(db, t); return
    spec = spec_file.read_text()
    record_skill_hits(db, tid, agent, spec)
    if agent == "retriever":
        spec = search_preprocess(db, t, spec)
    elif agent == "digester":
        spec = deepdive_preprocess(db, t, spec)
    spec = dep_preprocess(db, t, spec)
    trace_dir = TRACES/agent/datetime.now().strftime("%Y%m%d"); trace_dir.mkdir(parents=True, exist_ok=True)
    trace = trace_dir/f"{tid}.a{t['attempts']}.jsonl"
    log(f"{tid} -> {profile} (attempt {t['attempts']+1})")
    from notifier import notify, parse_report
    hb = None
    if t["notify"]:   # 长任务心跳:ttl 70% 仍未完 → 卡片原地更新(降级:文本出站),免得静默到超时
        notify(tid, "running")
        hb_sec = max(60, int(t["ttl_sec"]*0.7))
        def _heartbeat():
            if not notify(tid, "running", extra={"elapsed_min": hb_sec//60}):
                feishu(f"⏳ {tid} {t['title']} 仍在运行(已 {hb_sec//60} 分钟,上限 {t['ttl_sec']//60} 分钟)agent={agent}")
        hb = threading.Timer(hb_sec, _heartbeat)
        hb.daemon = True; hb.start()
    # start_new_session:claude(node)与 codex 同为多级进程树,超时必须整组杀,
    # 否则孙进程成孤儿继续烧上游 token(2026-07-07 T-003 codex 实锤,同坑防复发)
    cmd, wenv = worker_cmd_env(profile)
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, start_new_session=True, cwd=str(ROOT), env=wenv)
    final, cost, dur_s = None, 0.0, 0
    try:
        out, err = p.communicate(input=spec, timeout=t["ttl_sec"])
        trace.write_text(out + (f"\n\n# stderr\n{err}" if err else ""))
        ok = p.returncode == 0
        if ok:
            try:   # --output-format json:最后一行 JSON,result=最终消息
                res = json.loads(out.strip().splitlines()[-1])
                ok = not res.get("is_error") and bool(res.get("result", "").strip())
                final = res.get("result", "")
                cost = res.get("total_cost_usd") or 0.0
                dur_s = int((res.get("duration_ms") or 0)/1000)
            except Exception as e:
                ok = False
                ev(db, tid, agent, "fail", f"claude 输出不可解析: {str(e)[:120]}")
    except subprocess.TimeoutExpired:
        import signal as _sig
        try:
            os.killpg(p.pid, _sig.SIGKILL)
        except ProcessLookupError:
            pass
        p.communicate()
        ok = False
        ev(db, tid, agent, "fail", "timeout(进程组已整组杀)")
    finally:
        if hb:
            hb.cancel()

    if ok:
        body, urls, chash = split_envelope(final)
        if urls is None and chash is None:
            ev(db, tid, agent, "envelope_missing", profile)   # 模型没写 envelope,进周治理统计
        report = parse_report(body)
        if not report.get("tldr"):
            ev(db, tid, agent, "report_missing", profile)     # Stop hook 漏网,进周治理统计
        proj = t["project"] or "default"
        out = ROOT/"handoff"/proj/f"{tid}.result.md"          # 与 spec 同项目目录,禁扁平落 handoff/
        out.parent.mkdir(parents=True, exist_ok=True)
        artifacts = [str(out.relative_to(ROOT))]
        inbox = None
        if agent in INBOX_AGENTS:
            inbox = ROOT/"kb/90-inbox"/f"{tid}-{agent}.md"
            artifacts.append(str(inbox.relative_to(ROOT)))
        envelope = canonical_envelope(t, profile, urls, chash, artifacts)
        out.write_text(f"# {tid} result ({agent}/{profile})\n\n{body}\n\n{envelope}\n")
        if inbox is not None:       # retriever/digester/auditor 直接闭环落 inbox
            inbox.write_text(f"---\nsource: {agent}\ntask: {tid}\nproject: {proj}\n"
                             f"date: {datetime.now():%Y-%m-%d}\nstatus: raw\n---\n\n{body}\n\n{envelope}\n")
            new_status = "done"
        else:                       # executor → review(机器验收)
            new_status = "review"
        db.execute("UPDATE tasks SET status=?,result_path=?,updated_at=datetime('now') WHERE id=?",
                   (new_status, str(out.relative_to(ROOT)), tid))
        ev(db, tid, agent, "done", profile)
        if new_status == "done":
            trigger_dependents(db, tid)
            try:
                handle_gaps(db, t, final)   # 补抓闭环:不因 gaps 处理异常连累主任务落盘
            except Exception as e:
                ev(db, tid, agent, "gaps_error", str(e)[:160])
        if t["notify"]:
            link = feishu_archive(inbox or out, f"{tid}-{agent}.md")
            extra = {"artifacts": artifacts, "doc_url": link, "cost": cost, "dur_s": dur_s}
            if not report.get("tldr"):   # report 缺失兜底:首段截断,好过独白但记账督促
                report = {"tldr": body.strip().splitlines()[0][:60] if body.strip() else "(空产出)"}
            notify(tid, "review" if new_status == "review" else "done", report, extra)
    else:
        attempts = t["attempts"]+1
        # 失败不换厂商:难度是入队时已知的任务属性,失败是给人看的信号(裁决后可改难度重派)
        if attempts >= MAX_ATTEMPTS:
            db.execute("UPDATE tasks SET status='blocked',attempts=?,updated_at=datetime('now') WHERE id=?", (attempts, tid))
            ev(db, tid, agent, "block", f"max attempts at difficulty={DIFF.get(tier, tier)}")
            notify(tid, "blocked", {"tldr": f"连续 {attempts} 次失败,需人工裁决(可改难度重派)"},
                   {"reason": f"max attempts at difficulty={DIFF.get(tier, tier)}",
                    "trace": str(trace.relative_to(ROOT))})
            propagate_block(db, t)
        else:
            db.execute("UPDATE tasks SET attempts=?,status='queued',updated_at=datetime('now') WHERE id=?", (attempts, tid))
            ev(db, tid, agent, "fail", f"attempt {attempts}")
    db.commit()

# ---- 依赖边 ----
def trigger_dependents(db, done_tid):
    """上游 done → 依赖它的 waiting_dep 任务转 queued(幂等:仅动 waiting_dep)。"""
    for r in db.execute("SELECT id,agent FROM tasks WHERE depends_on=? AND status='waiting_dep'", (done_tid,)).fetchall():
        db.execute("UPDATE tasks SET status='queued',updated_at=datetime('now') WHERE id=?", (r["id"],))
        ev(db, r["id"], r["agent"], "dep_triggered", f"upstream {done_tid} done")
        log(f"{r['id']} dep_triggered by {done_tid}")
    db.commit()

def propagate_block(db, t):
    """上游 blocked → 下游(waiting_dep/queued 依赖它的)标 dep_failed,不静默挂起,进日报。"""
    for r in db.execute("SELECT id,agent FROM tasks WHERE depends_on=? AND status IN ('waiting_dep','queued')",
                        (t["id"],)).fetchall():
        db.execute("UPDATE tasks SET status='dep_failed',updated_at=datetime('now') WHERE id=?", (r["id"],))
        ev(db, r["id"], r["agent"], "dep_failed", f"upstream {t['id']} blocked")
        log(f"{r['id']} dep_failed <- {t['id']} blocked")
    db.commit()

# ---- 域级并发:四域各持独立锁并行消费,慢任务只阻塞本域,不再队头阻塞全队 ----
DOMAINS = ("retriever", "executor", "digester", "auditor")

def connect():
    db = sqlite3.connect(DB, timeout=30); db.row_factory = sqlite3.Row
    db.execute("PRAGMA busy_timeout=30000")   # WAL + busy_timeout:多域写者共存
    return db

def domain_loop(domain):
    lock = open(ROOT/f".dispatch.{domain}.lock", "w")
    try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError: return            # 该域上一轮还在跑,跳过(其余域不受影响)
    sys.path.insert(0, str(ROOT/"bin"))       # for `import search`
    db = connect()
    like = domain + "-%"
    # 僵尸回收(本域):running 超 2×ttl → 重排
    for s in db.execute("""SELECT id,agent FROM tasks WHERE status='running'
        AND (agent=? OR agent LIKE ?)
        AND (strftime('%s','now')-strftime('%s',updated_at)) > 2*ttl_sec""", (domain, like)).fetchall():
        db.execute("UPDATE tasks SET status='queued',attempts=attempts+1,updated_at=datetime('now') WHERE id=?", (s["id"],))
        ev(db, s["id"], s["agent"], "fail", "stale-running recovered")
    while True:
        # 只取本域 queued 且依赖已满足(NULL 或指向的任务 done);按优先级、创建时间
        row = db.execute("""SELECT * FROM tasks WHERE status='queued'
            AND (agent=? OR agent LIKE ?)
            AND (depends_on IS NULL OR depends_on='' OR
                 depends_on IN (SELECT id FROM tasks WHERE status='done'))
            ORDER BY priority, created_at LIMIT 1""", (domain, like)).fetchone()
        if not row: break
        db.execute("UPDATE tasks SET status='running',updated_at=datetime('now') WHERE id=?", (row["id"],)); db.commit()
        ev(db, row["id"], row["agent"], "claim", f"domain={domain}")
        run_task(db, dict(row))

def _ready_count(db):
    return db.execute("""SELECT count(*) FROM tasks WHERE status='queued'
        AND (depends_on IS NULL OR depends_on='' OR
             depends_on IN (SELECT id FROM tasks WHERE status='done'))""").fetchone()[0]

def main():
    # 最多 3 轮:上游 done 触发的跨域下游任务(dep_triggered)同一次 cron 内接力消费,不等下轮
    for _ in range(3):
        procs = [multiprocessing.Process(target=domain_loop, args=(d,)) for d in DOMAINS]
        for p in procs: p.start()
        for p in procs: p.join()
        if _ready_count(connect()) == 0:
            break

if __name__ == "__main__":
    main()
