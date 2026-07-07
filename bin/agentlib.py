#!/usr/bin/env python3
"""agentlib — 共享库:.env加载 / DB / 验收 / 入队(review.py、feishu_gateway.py、enqueue.py共用)"""
import hashlib, hmac, os, sqlite3, time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---- 短时效签名令牌:卡片按钮链接不再携带完整 GATEWAY_TOKEN(URL 会进 CF 日志) ----
def sign(*fields, exp=None):
    """对若干字段签短令牌,默认 7 天有效。格式 <exp>.<hmac16>。"""
    secret = os.environ.get("GATEWAY_TOKEN", "")
    exp = exp or int(time.time()) + 7*86400
    msg = "|".join(map(str, fields)) + f"|{exp}"
    return f"{exp}.{hmac.new(secret.encode(), msg.encode(), hashlib.sha256).hexdigest()[:16]}"

def verify_sig(sig, *fields):
    try:
        exp, _ = sig.split(".", 1)
        if int(exp) < time.time():
            return False
        return hmac.compare_digest(sig, sign(*fields, exp=int(exp)))
    except Exception:
        return False

def load_env():
    f = ROOT/".env"
    if f.exists():
        for line in f.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

def claude_bin():
    """claude CLI 绝对路径:nvm 安装不在 systemd/cron 最小 PATH 里(2026-07-07 gateway 实锤)。"""
    import glob, shutil
    p = shutil.which("claude")
    if p:
        return p
    cands = sorted(glob.glob(str(Path.home()/".nvm/versions/node/*/bin/claude")))
    return cands[-1] if cands else "claude"

def db():
    c = sqlite3.connect(ROOT/"state.db", timeout=30); c.row_factory = sqlite3.Row
    c.execute("PRAGMA busy_timeout=30000")   # 域级并发派工后多写者共存,等锁不炸
    return c

def ev(c, task_id, agent, kind, detail=""):
    c.execute("INSERT INTO events(task_id,agent,kind,detail) VALUES(?,?,?,?)",
              (task_id, agent, kind, detail)); c.commit()

def _dep_met(c, depends_on):
    if not depends_on:
        return True
    r = c.execute("SELECT status FROM tasks WHERE id=?", (depends_on,)).fetchone()
    return bool(r) and r["status"] == "done"

DIFFICULTY = {"light": 0, "medium": 1, "heavy": 2}

def default_difficulty(agent):
    # executor 默认 medium(走 GPT,HB 拍板"中等及以上难度走 GPT");杂活需显式标 light 省 Plus 配额
    return "medium" if agent in ("executor-code", "executor-data") else "light"

def enqueue(agent, title, body, ttl=900, notify=1, spec_path=None,
            project="default", priority=2, depends_on=None, query=None,
            difficulty=None):
    difficulty = difficulty or default_difficulty(agent)
    if difficulty not in DIFFICULTY:
        raise ValueError(f"difficulty 须为 {'/'.join(DIFFICULTY)},得到 {difficulty!r}")
    tier = DIFFICULTY[difficulty]
    if difficulty == "heavy" and ttl == 900:
        ttl = 1800   # heavy=超长上下文蒸馏,缺省 ttl 放宽一倍(显式传 ttl 则尊重)
    c = db()
    # 日期一律用本地时间:SQL 'now' 是 UTC,本地 00:00-08:00 会与 datetime.now() 差一天,
    # LIKE 模式与生成的 id 日期不一致 → 序号从 0 重数 → 主键冲突(2026-07-07 selftest 实锤)
    today = f"{datetime.now():%Y%m%d}"
    last = c.execute("SELECT MAX(CAST(substr(id,-3) AS INTEGER)) FROM tasks WHERE id LIKE ?",
                     (f"T-{today}-%",)).fetchone()[0] or 0
    tid = f"T-{today}-{last+1:03d}"
    # 初始状态:3D→waiting_gpu(不进主循环,待本地 gpu_worker);依赖未 done→waiting_dep;否则 queued
    if agent == "executor-3d":
        status = "waiting_gpu"
    elif depends_on and not _dep_met(c, depends_on):
        status = "waiting_dep"
    else:
        status = "queued"
    if not spec_path:
        sp = ROOT/"handoff"/project/f"{tid}.md"
        sp.parent.mkdir(parents=True, exist_ok=True)
        qs = ([query] if isinstance(query, str) else list(query)) if query else []
        qline = "".join(f"query: {q}\n" for q in qs if q and str(q).strip())
        sp.write_text(f"""---
id: {tid}
agent: {agent}
title: {title}
project: {project}
priority: {priority}
difficulty: {difficulty}
depends_on: {depends_on or ''}
{qline}---
# 任务
{body}

# 验收
- 按 AGENT.md 规定格式输出
- 末尾必附 envelope(task_id/agent/model/tier/project/source_urls/content_hash/depends_on/artifacts)
""")
        spec_path = str(sp.relative_to(ROOT))
    c.execute("INSERT INTO tasks(id,agent,title,spec_path,ttl_sec,notify,status,project,priority,depends_on,tier) "
              "VALUES(?,?,?,?,?,?,?,?,?,?,?)",
              (tid, agent, title, spec_path, ttl, notify, status, project, priority, depends_on, tier))
    ev(c, tid, agent, "enqueue", f"status={status} project={project} pri={priority} diff={difficulty}"
       + (f" dep={depends_on}" if depends_on else ""))
    c.commit()
    return tid

def mark_seen(c, tag):
    """幂等标记:首次返回 True 并记录;已存在返回 False。"""
    try:
        c.execute("INSERT INTO seen_events(tag) VALUES(?)", (tag,)); c.commit()
        return True
    except sqlite3.IntegrityError:
        return False

REVIEW_MAP = {"adopt": ("done", "adopted"), "rework": ("queued", "reworked"), "reject": ("blocked", "corrected")}

def apply_review(tid, action, note=""):
    if action not in REVIEW_MAP:
        return False, f"未知动作 {action}(adopt|rework|reject)"
    c = db()
    t = c.execute("SELECT * FROM tasks WHERE id=?", (tid,)).fetchone()
    if not t:
        return False, f"任务不存在 {tid}"
    if t["status"] not in ("review", "blocked"):
        return False, f"{tid} 当前状态 {t['status']},不可验收(防重复点击)"
    status, signal = REVIEW_MAP[action]
    if action == "rework":
        sp = ROOT/t["spec_path"]
        sp.write_text(sp.read_text() + f"\n\n# 返工意见({datetime.now():%m-%d %H:%M})\n{note or '(未注明)'}\n")
        c.execute("UPDATE tasks SET status='queued',attempts=0,updated_at=datetime('now') WHERE id=?", (tid,))
        ev(c, tid, t["agent"], "rework", note)
    else:
        c.execute("UPDATE tasks SET status=?,updated_at=datetime('now') WHERE id=?", (status, tid))
    if action == "adopt":   # 进化闭环:apply 任务被采纳 → 对应提议 adopted→applied(等 auditor 周复检)
        c.execute("UPDATE proposals SET status='applied',updated_at=datetime('now') "
                  "WHERE apply_task=? AND status='adopted'", (tid,))
    c.execute("INSERT INTO feedback(agent,task_id,signal,note) VALUES(?,?,?,?)",
              (t["agent"], tid, signal, note))
    c.commit()
    return True, f"{tid} → {status}(feedback: {signal})"
