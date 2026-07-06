#!/usr/bin/env python3
"""feishu_gateway — 常驻HTTP服务(systemd),三个端点:
  GET  /review?tid&action&note&token  手机点卡片按钮直达验收(无需飞书应用回调)
  POST /feishu                        飞书应用事件订阅入站:想法→90-inbox;"派 <agent> <任务>"→入队
  GET  /health
安全:绑127.0.0.1,经Cloudflare Tunnel暴露;/review 需 GATEWAY_TOKEN;/feishu 校验 Verification Token(明文模式,飞书后台不配Encrypt Key)。
"""
import json, os, subprocess, sys, urllib.parse
import traceback
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import ROOT, db, load_env, apply_review, enqueue, verify_sig

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
                text = json.loads(data["event"]["message"].get("content", "{}")).get("text", "").strip()
            except Exception:
                text = ""
            audit(f"message_text={text[:200]!r}")
            if text:
                self.handle_text(text)
        return self._send(200, json.dumps({"code": 0}), "application/json")

    def handle_text(self, text):
        # "派 owl-intel 调研xxx" → 入队;其余一切 → 90-inbox 异步信箱
        if "检测" in text and "入站" in text:
            push("已入站")
            return
        if text.startswith("派 ") or text.startswith("派"):
            parts = text.lstrip("派").strip().split(maxsplit=1)
            if len(parts) == 2 and parts[0] in VALID_AGENTS:
                tid = enqueue(parts[0], parts[1][:40], parts[1])
                push(f"📥 已入队 {tid} → {parts[0]}\n{parts[1][:100]}")
                return
            push(f"⚠️ 格式:派 <{'|'.join(sorted(VALID_AGENTS))}> <任务描述>")
            return
        f = ROOT/"kb/90-inbox"/f"idea-{datetime.now():%Y%m%d-%H%M%S}.md"
        f.write_text(f"---\nsource: feishu\ndate: {datetime.now():%Y-%m-%d %H:%M}\nstatus: raw\n---\n\n{text}\n")
        push(f"📝 已收进 inbox:{text[:60]}")

if __name__ == "__main__":
    host, port = BIND.rsplit(":", 1)
    HTTPServer((host, int(port)), H).serve_forever()
