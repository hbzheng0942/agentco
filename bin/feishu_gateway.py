#!/usr/bin/env python3
"""feishu_gateway — 常驻HTTP服务(systemd),三个端点:
  GET  /review?tid&action&note&token  手机点卡片按钮直达验收(无需飞书应用回调)
  POST /feishu                        飞书应用事件订阅入站:想法→90-inbox;"派 <agent> <任务>"→入队
  GET  /health
安全:绑127.0.0.1,经Cloudflare Tunnel暴露;/review 需 GATEWAY_TOKEN;/feishu 校验 Verification Token(明文模式,飞书后台不配Encrypt Key)。
"""
import json, os, re, subprocess, sys, threading, urllib.parse
import traceback
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import ROOT, db, load_env, apply_review, enqueue, verify_sig
import bridge

load_env()
TOKEN  = os.environ.get("GATEWAY_TOKEN", "")
VERIFY = os.environ.get("FEISHU_VERIFY_TOKEN", "")
BIND   = os.environ.get("GATEWAY_BIND", "127.0.0.1:9000")
VALID_AGENTS = {"retriever", "executor-code", "executor-data", "executor-3d", "digester", "auditor"}
LOG = ROOT / "logs" / "feishu_gateway.log"

def audit(msg):
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} {msg}\n")
    except Exception:
        pass

def push(text):
    subprocess.run([str(ROOT/"bin/feishu_push.sh"), text], check=False)

# ---- 入站文本解析(模块级,selftest 可测) ----
_AGENT_ALIAS = {"executor": "executor-code"}   # 裸 executor 缺省代码域

def strip_mentions(text):
    """群里 @机器人 时 content.text 携带 @_user_N 占位符,剥掉。"""
    return re.sub(r"@_user_\d+\s*", "", text).strip()

def parse_dispatch(text):
    """识别派单意图:'派/请/让 <agent> [执行/跑/做] <任务>'(agent 名精确匹配,大小写不敏感)。
    返回 (agent, task) 或 None(None=不是派单,进 inbox)。"""
    m = re.match(r"^(?:派|请|让)\s*([A-Za-z0-9\-]+)\s*(?:执行|跑|做)?\s*[,,::]?\s*(.+)$", text, re.S)
    if not m:
        return None
    name = m.group(1).lower()
    agent = name if name in VALID_AGENTS else _AGENT_ALIAS.get(name)
    if not agent or not m.group(2).strip():
        return None
    return agent, m.group(2).strip()

def _spend():
    import glob
    f = sorted(glob.glob(str(ROOT/"logs/spend-*.json")))
    try:
        return json.loads(Path(f[-1]).read_text())["spend"] if f else 0.0
    except Exception:
        return 0.0

def stats():
    c = db()
    q = lambda sql, *a: [dict(r) for r in c.execute(sql, a).fetchall()]
    return {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "status": {r["status"]: r["c"] for r in c.execute("SELECT status,count(*) c FROM tasks GROUP BY status")},
        "running": q("SELECT id,agent,title,ttl_sec,"
                     "(strftime('%s','now')-strftime('%s',updated_at)) age FROM tasks WHERE status='running'"),
        "attention": q("SELECT id,agent,status,title FROM tasks WHERE status IN ('blocked','dep_failed','review') "
                       "ORDER BY updated_at DESC LIMIT 10"),
        "agents7d": q("SELECT agent,kind,count(*) c FROM events WHERE ts>datetime('now','-7 day') "
                      "AND kind IN ('done','fail','block') GROUP BY agent,kind"),
        "done24h": c.execute("SELECT count(*) FROM events WHERE kind='done' AND ts>datetime('now','-1 day')").fetchone()[0],
        "events": q("SELECT task_id,agent,kind,substr(detail,1,60) detail,ts FROM events ORDER BY id DESC LIMIT 25"),
        "proposals": q("SELECT id,status,title FROM proposals WHERE status IN ('proposed','adopted','applied') "
                       "ORDER BY ts DESC LIMIT 10"),
        "spend": round(_spend(), 2),
        "budget": float(os.environ.get("LITELLM_BUDGET_USD", "200")),
    }

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _dash_auth(self, q):
        return (q.get("s") and verify_sig(q["s"], "dashboard")) or (TOKEN and q.get("token") == TOKEN)

    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        b = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = dict(urllib.parse.parse_qsl(u.query))
        if u.path == "/health":
            return self._send(200, "ok", "text/plain")
        if u.path == "/review":
            # 短时效签名链接(卡片按钮,不带完整token防CF日志泄露);legacy 完整token仍兼容
            authed = (q.get("s") and verify_sig(q["s"], q.get("tid", ""), q.get("action", ""))) or \
                     (TOKEN and q.get("token") == TOKEN)
            if not authed:
                return self._send(403, "forbidden")
            ok, msg = apply_review(q.get("tid", ""), q.get("action", ""), q.get("note", ""))
            if ok:   # 卡片原地翻状态(adopted/rework/reject);降级无害
                try:
                    import notifier
                    notifier.notify(q["tid"], {"adopt": "adopted", "rework": "rework", "reject": "reject"}[q["action"]],
                                    extra={"verdict_note": q.get("note", "")} if q.get("note") else None)
                except Exception:
                    pass
            return self._send(200 if ok else 400,
                f"<html><body style='font-size:22px;padding:40px'>{'✅' if ok else '⚠️'} {msg}</body></html>")
        if u.path == "/proposal":   # 进化提议裁决(签名链接;adopt 自动入队 apply 任务)
            pid, action = q.get("id", ""), q.get("action", "")
            if not (q.get("s") and verify_sig(q["s"], pid, action)) and (not TOKEN or q.get("token") != TOKEN):
                return self._send(403, "forbidden")
            r = subprocess.run([sys.executable, str(ROOT/"bin/proposals.py"), "set", pid, action],
                               capture_output=True, text=True)
            msg = (r.stdout or r.stderr).strip()
            push(f"🧬 {msg}")
            return self._send(200 if r.returncode == 0 else 400,
                f"<html><body style='font-size:22px;padding:40px'>{'✅' if r.returncode == 0 else '⚠️'} {msg}</body></html>")
        if u.path == "/bridge":   # bridge confirm 流:确认入队暂存的拆解方案
            pid = q.get("id", "")
            if not (q.get("s") and verify_sig(q["s"], pid, "confirm")):
                return self._send(403, "forbidden")
            plan = bridge.pop_plan(pid)
            if not plan:
                return self._send(400, "<html><body style='font-size:22px;padding:40px'>⚠️ 方案不存在或已过期</body></html>")
            reply = bridge.execute_plan(plan)
            push(reply)
            return self._send(200, f"<html><body style='font-size:22px;padding:40px'>✅ 已入队,详情见飞书回执</body></html>")
        if u.path == "/api/stats":
            if not self._dash_auth(q):
                return self._send(403, "{}", "application/json")
            return self._send(200, json.dumps(stats(), ensure_ascii=False), "application/json")
        if u.path == "/dashboard":
            if not self._dash_auth(q):
                return self._send(403, "forbidden")
            page = (ROOT/"bin/dashboard.html").read_text().replace("__AUTH__", urllib.parse.urlencode(
                {k: q[k] for k in ("s", "token") if k in q}))
            return self._send(200, page)
        if u.path == "/enqueue":   # 日报/TODO 卡片按钮点击直接入队(GATEWAY_TOKEN 鉴权)
            if not TOKEN or q.get("token") != TOKEN:
                return self._send(403, "forbidden")
            agent = q.get("agent", "")
            if agent not in VALID_AGENTS:
                return self._send(400, f"<html><body style='font-size:22px;padding:40px'>⚠️ 未知 agent {agent}(须 {'/'.join(sorted(VALID_AGENTS))})</body></html>")
            title = (q.get("title") or q.get("body") or "")[:40] or "(无标题)"
            tid = enqueue(agent, title, q.get("body", title),
                          project=q.get("project", "default"),
                          priority=int(q.get("priority", 2) or 2),
                          depends_on=q.get("depends_on") or None,
                          query=q.get("query") or None)
            push(f"📥 已入队 {tid} → {agent}({q.get('project','default')})\n{title}")
            return self._send(200, f"<html><body style='font-size:22px;padding:40px'>✅ 已入队 {tid} → {agent}</body></html>")
        self._send(404, "404")

    def do_POST(self):
        if self.path != "/feishu":
            audit(f"POST unexpected_path path={self.path}")
            return self._send(404, "404")
        raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        ua = self.headers.get("User-Agent", "")
        audit(f"POST /feishu len={len(raw)} ua={ua}")
        try:
            data = json.loads(raw)
        except Exception:
            audit(f"bad_json raw={raw[:500]!r}")
            return self._send(400, "bad json")
        # 首次配置回调URL的验证握手
        if data.get("type") == "url_verification":
            return self._send(200, json.dumps({"challenge": data.get("challenge", "")}), "application/json")
        if "encrypt" in data:
            audit("encrypted_event_rejected")
            return self._send(400, "请在飞书后台关闭Encrypt Key(本网关使用明文模式+Token校验)")
        hdr = data.get("header", {})
        event_type = hdr.get("event_type")
        token_match = not VERIFY or hdr.get("token") == VERIFY or data.get("token") == VERIFY
        audit(f"event_type={event_type} token_match={token_match}")
        if VERIFY and hdr.get("token") != VERIFY and data.get("token") != VERIFY:
            header_has_token = bool(hdr.get("token"))
            root_has_token = bool(data.get("token"))
            audit(f"forbidden header_token={header_has_token} root_token={root_has_token}")
            return self._send(403, "forbidden")
        if event_type == "im.message.receive_v1":
            try:
                msg = data["event"]["message"]
                text = json.loads(msg.get("content", "{}")).get("text", "").strip()
            except Exception:
                msg, text = {}, ""
            if msg.get("chat_id"):   # 捕获收件会话:notifier 卡片出站用(单用户系统,最近私聊即收件箱)
                try:
                    (Path(__file__).resolve().parent.parent/"logs/feishu_notify_chat").write_text(msg["chat_id"])
                except Exception:
                    pass
            audit(f"message_text={text[:200]!r}")
            if text:
                self.handle_text(text)
        return self._send(200, json.dumps({"code": 0}), "application/json")

    def handle_text(self, text):
        # 双速入站(Wave④):规则快路径("派 <agent> <任务>"精确格式,零延迟)→
        # 慢车道 concierge(haiku 多轮会话,后台线程,不阻塞单线程HTTP服务)→
        # concierge 失败降级 bridge(ds-chat 单轮分诊)→ 规则宽松解析 → inbox。消息永不丢。
        text = strip_mentions(text)
        if "检测" in text and "入站" in text:
            push("已入站")
            return
        m = re.match(r"^派\s+(\S+)\s+(.+)$", text, re.S)
        if m and m.group(1) in VALID_AGENTS:   # 快路径:精确格式直通,不花 LLM
            agent, task = m.group(1), m.group(2).strip()
            tid = enqueue(agent, task[:40], task, query=(task[:100] if agent == "retriever" else None))
            push(f"📥 已入队 {tid} → {agent}\n{task[:100]}")
            return
        threading.Thread(target=self.slow_lane, args=(text,), daemon=True).start()

    def slow_lane(self, text):
        try:
            import concierge
            reply, actions = concierge.chat(text)
        except Exception as e:
            audit(f"concierge_error {e}")
            reply, actions = None, None
        if reply is None:                      # concierge 不可用 → 原 bridge 链
            audit("concierge_unavailable -> bridge")
            return self.bridge_lane(text)
        if actions:
            plan = bridge.validate_plan(actions)   # 白名单校验:agent/难度/意图全枚举,不信任模型输出
            if plan and plan["intent"] == "dispatch":
                if bridge.needs_confirm(plan):     # 大批量/heavy:先确认再入队
                    pid, url = bridge.stash_plan(plan)
                    reply += (f"\n\n🧾 拆解出 {len(plan['tasks'])} 个任务,含大活,请确认:\n"
                              f"{bridge.plan_summary(plan)}\n✅ 确认入队 {url}\n(不点=不执行,24h 过期)")
                else:
                    reply += "\n\n" + bridge.execute_plan(plan)
            elif plan and plan["intent"] == "cancel" and plan["task_ref"]:
                reply += "\n\n" + bridge.cancel_task(plan["task_ref"])
            elif (actions.get("intent") == "idea") if isinstance(actions, dict) else False:
                f = ROOT/"kb/90-inbox"/f"idea-{datetime.now():%Y%m%d-%H%M%S}.md"
                f.write_text(f"---\nsource: feishu-concierge\ndate: {datetime.now():%Y-%m-%d %H:%M}\nstatus: raw\n---\n\n{text}\n")
                reply += "\n\n📝 已收进 inbox"
        push(reply[:2000])

    def bridge_lane(self, text):
        plan = bridge.classify(text)
        if plan:
            audit(f"bridge intent={plan['intent']} tasks={len(plan['tasks'])}")
            if plan["intent"] == "status":
                push(bridge.answer_status(plan["task_ref"]))
                return
            if plan["intent"] == "cancel":
                push(bridge.cancel_task(plan["task_ref"]))
                return
            if plan["intent"] == "dispatch":
                if bridge.needs_confirm(plan):   # 大批量/heavy:先确认再入队
                    pid, url = bridge.stash_plan(plan)
                    push(f"🧾 拆解出 {len(plan['tasks'])} 个任务,含大活,请确认:\n"
                         f"{bridge.plan_summary(plan)}\n✅ 确认入队 {url}\n(不点=不执行,24h 过期)")
                else:
                    push(bridge.execute_plan(plan))
                return
            # intent=idea → 落 inbox(带上 bridge 的理解)
        parsed = parse_dispatch(text)   # bridge 不可用时的规则兜底
        if parsed:
            agent, task = parsed
            tid = enqueue(agent, task[:40], task, query=(task[:100] if agent == "retriever" else None))
            push(f"📥 已入队 {tid} → {agent}(bridge不可用,规则解析)\n{task[:100]}")
            return
        f = ROOT/"kb/90-inbox"/f"idea-{datetime.now():%Y%m%d-%H%M%S}.md"
        note = f"\nbridge_note: {plan['note']}" if plan and plan.get("note") else ""
        f.write_text(f"---\nsource: feishu\ndate: {datetime.now():%Y-%m-%d %H:%M}\nstatus: raw{note}\n---\n\n{text}\n")
        push(f"📝 已收进 inbox:{text[:60]}")

if __name__ == "__main__":
    host, port = BIND.rsplit(":", 1)
    HTTPServer((host, int(port)), H).serve_forever()
