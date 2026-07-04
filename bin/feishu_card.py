#!/usr/bin/env python3
"""feishu_card.py <tid> <title> [preview] — 发送验收卡片(采纳/返工/废弃为link按钮,直达gateway)
PUBLIC_BASE_URL 未配置时降级为纯文本推送。"""
import base64, hashlib, hmac, json, os, sys, time, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import load_env

load_env()
tid, title = sys.argv[1], sys.argv[2]
preview = sys.argv[3][:600] if len(sys.argv) > 3 else ""
hook = os.environ.get("FEISHU_WEBHOOK", "")
base = os.environ.get("PUBLIC_BASE_URL", "").rstrip("/")
tok  = os.environ.get("GATEWAY_TOKEN", "")
if not hook:
    sys.exit(0)

def payload():
    if not base or not tok:   # 降级:纯文本
        return {"msg_type": "text", "content":
                {"text": f"🔎 待验收 {tid} {title}\n{preview}\n(服务器: bin/review.py {tid} adopt|rework|reject)"}}
    btn = lambda lbl, act, typ: {"tag": "button", "text": {"tag": "plain_text", "content": lbl},
        "type": typ, "url": f"{base}/review?tid={tid}&action={act}&token={tok}"}
    return {"msg_type": "interactive", "card": {
        "header": {"title": {"tag": "plain_text", "content": f"🔎 待验收 {tid} · {title}"}, "template": "blue"},
        "elements": [
            {"tag": "markdown", "content": preview or "(无预览)"},
            {"tag": "action", "actions": [btn("✅ 采纳", "adopt", "primary"),
                                          btn("🔁 返工", "rework", "default"),
                                          btn("🗑 废弃", "reject", "danger")]}]}}

body = payload()
secret = os.environ.get("FEISHU_SECRET", "")
if secret:
    ts = str(int(time.time()))
    key = f"{ts}\n{secret}".encode()
    body["timestamp"] = ts
    body["sign"] = base64.b64encode(hmac.new(key, b"", hashlib.sha256).digest()).decode()

req = urllib.request.Request(hook, json.dumps(body).encode(),
                             {"Content-Type": "application/json"})
try:
    urllib.request.urlopen(req, timeout=10)
except Exception as e:
    print(f"feishu_card failed: {e}", file=sys.stderr)
