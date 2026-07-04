#!/usr/bin/env python3
"""feishu_gateway — 常驻HTTP服务(systemd),三个端点:
  GET  /review?tid&action&note&token  手机点卡片按钮直达验收(无需飞书应用回调)
  POST /feishu                        飞书应用事件订阅入站:想法→90-inbox;"派 <agent> <任务>"→入队
  GET  /health
安全:绑127.0.0.1,经Cloudflare Tunnel暴露;/review 需 GATEWAY_TOKEN;/feishu 校验 Verification Token(明文模式,飞书后台不配Encrypt Key)。
"""
import json, os, subprocess, sys, urllib.parse
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import ROOT, load_env, apply_review, enqueue

load_env()
TOKEN  = os.environ.get("GATEWAY_TOKEN", "")
VERIFY = os.environ.get("FEISHU_VERIFY_TOKEN", "")
BIND   = os.environ.get("GATEWAY_BIND", "127.0.0.1:9000")
VALID_AGENTS = {"owl-intel", "exec-ds", "critic"}

def push(text):
    subprocess.run([str(ROOT/"bin/feishu_push.sh"), text], check=False)

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

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
            if not TOKEN or q.get("token") != TOKEN:
                return self._send(403, "forbidden")
            ok, msg = apply_review(q.get("tid", ""), q.get("action", ""), q.get("note", ""))
            return self._send(200 if ok else 400,
                f"<html><body style='font-size:22px;padding:40px'>{'✅' if ok else '⚠️'} {msg}</body></html>")
        self._send(404, "404")

    def do_POST(self):
        if self.path != "/feishu":
            return self._send(404, "404")
        raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        try:
            data = json.loads(raw)
        except Exception:
            return self._send(400, "bad json")
        # 首次配置回调URL的验证握手
        if data.get("type") == "url_verification":
            return self._send(200, json.dumps({"challenge": data.get("challenge", "")}), "application/json")
        if "encrypt" in data:
            return self._send(400, "请在飞书后台关闭Encrypt Key(本网关使用明文模式+Token校验)")
        hdr = data.get("header", {})
        if VERIFY and hdr.get("token") != VERIFY and data.get("token") != VERIFY:
            return self._send(403, "forbidden")
        if hdr.get("event_type") == "im.message.receive_v1":
            try:
                text = json.loads(data["event"]["message"].get("content", "{}")).get("text", "").strip()
            except Exception:
                text = ""
            if text:
                self.handle_text(text)
        return self._send(200, json.dumps({"code": 0}), "application/json")

    def handle_text(self, text):
        # "派 owl-intel 调研xxx" → 入队;其余一切 → 90-inbox 异步信箱
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
