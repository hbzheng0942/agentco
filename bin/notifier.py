#!/usr/bin/env python3
"""notifier — 出站呈现层(envelope 2.0 配套):一任务一卡片,应用机器人原地更新全生命周期。

设计:
- 卡片经自建应用 im/v1/messages 发送(可 PATCH 原地更新),message_id 存 tasks.card_msg_id。
- 收件会话 chat_id:入站网关捕获后写 logs/feishu_notify_chat(单用户系统,取最近私聊)。
- 降级链(信号永不丢):应用凭据缺/chat_id 未捕获/API 失败 → feishu_push.sh 文本 webhook。
- 渲染是确定性模板:内容字段来自 report 块(tldr/highlights/action_needed/confidence)与
  dispatcher 数据(agent/难度/耗时/成本),模型独白永不上卡。

phases: running / heartbeat / done / review / blocked / adopted / rework / reject
"""
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import ROOT, db, load_env, sign

load_env()
OPEN_BASE = "https://open.feishu.cn/open-apis"
CHAT_FILE = ROOT/"logs/feishu_notify_chat"
_TOKEN_CACHE = ROOT/"logs/.feishu_tenant_token.json"

DIFF_NAME = {0: "light", 1: "medium", 2: "heavy"}
COLOR = {"running": "wathet", "done": "green", "review": "blue", "blocked": "red",
         "adopted": "green", "rework": "orange", "reject": "grey"}
ICON = {"running": "▶️", "done": "✅", "review": "🔎", "blocked": "🛑",
        "adopted": "✅", "rework": "🔁", "reject": "🗑"}
PHASE_NAME = {"running": "运行中", "done": "已完成", "review": "待验收", "blocked": "受阻",
              "adopted": "已采纳", "rework": "已打回返工", "reject": "已废弃"}


def _push_text(text):
    subprocess.run([str(ROOT/"bin/feishu_push.sh"), text], check=False)


def _tenant_token():
    app_id = os.environ.get("FEISHU_APP_ID", "")
    secret = os.environ.get("FEISHU_APP_SECRET", "")
    if not app_id or not secret:
        return None
    try:  # 2h 有效,提前 5min 过期
        c = json.loads(_TOKEN_CACHE.read_text())
        if c["exp"] > time.time() + 300:
            return c["token"]
    except Exception:
        pass
    try:
        req = urllib.request.Request(f"{OPEN_BASE}/auth/v3/tenant_access_token/internal",
            json.dumps({"app_id": app_id, "app_secret": secret}).encode(),
            {"Content-Type": "application/json"})
        r = json.loads(urllib.request.urlopen(req, timeout=10).read())
        tok = r.get("tenant_access_token")
        if tok:
            _TOKEN_CACHE.write_text(json.dumps({"token": tok, "exp": time.time() + r.get("expire", 7200)}))
        return tok
    except Exception:
        return None


def _api(method, path, payload, token):
    req = urllib.request.Request(f"{OPEN_BASE}{path}", json.dumps(payload).encode(),
        {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}, method=method)
    return json.loads(urllib.request.urlopen(req, timeout=10).read())


def _chat_id():
    v = os.environ.get("FEISHU_NOTIFY_CHAT_ID", "")
    if v:
        return v
    try:
        return CHAT_FILE.read_text().strip() or None
    except Exception:
        return None


def _ensure_column():
    c = db()
    try:
        c.execute("ALTER TABLE tasks ADD COLUMN card_msg_id TEXT")
        c.commit()
    except Exception:
        pass  # 已存在
    return c


# ---- 卡片模板(确定性渲染) ----
def _md(s):
    return {"tag": "markdown", "content": s}


def _build_card(t, phase, report=None, extra=None):
    tid, title = t["id"], t["title"]
    diff = DIFF_NAME.get(t["tier"], t["tier"])
    report, extra = report or {}, extra or {}
    els = []
    if phase == "running":
        els.append(_md(f"⏱ 已运行 {extra.get('elapsed_min', 0)} 分钟(上限 {t['ttl_sec']//60} 分钟)"
                       if extra.get("elapsed_min") else "任务执行中…"))
    if report.get("tldr"):
        els.append(_md(f"**{report['tldr']}**"))
    hl = report.get("highlights") or []
    if hl:
        els.append(_md("\n".join(f"· {h}" for h in hl[:3])))
    if report.get("action_needed") and str(report["action_needed"]).lower() != "null":
        els.append(_md(f"⚠️ **需裁决**:{report['action_needed']}"))
    if phase == "blocked":
        els.append(_md(f"原因:{extra.get('reason', '连续失败达上限')}\ntrace:`{extra.get('trace', '')}`"))
    if extra.get("verdict_note"):
        els.append(_md(f"📝 {extra['verdict_note']}"))
    if extra.get("doc_url"):
        els.append(_md(f"☁️ [飞书文档]({extra['doc_url']})"))
    if extra.get("artifacts"):
        els.append({"tag": "note", "elements": [{"tag": "plain_text",
                    "content": "📄 " + " ; ".join(extra["artifacts"])}]})
    conf = f" · 置信 {report['confidence']}" if report.get("confidence") else ""
    cost = f" · ${extra['cost']:.3f}" if extra.get("cost") else ""
    dur = f" · {extra['dur_s']}s" if extra.get("dur_s") else ""
    els.append({"tag": "note", "elements": [{"tag": "plain_text",
                "content": f"{t['agent']} · {diff}{conf}{dur}{cost}"}]})
    if phase in ("review", "blocked"):   # 验收/裁决按钮(签名短链,原有 /review 流)
        base = os.environ.get("PUBLIC_BASE_URL", "").rstrip("/")
        if base:
            btn = lambda lbl, act, typ: {"tag": "button", "text": {"tag": "plain_text", "content": lbl},
                "type": typ, "url": f"{base}/review?tid={tid}&action={act}&s={sign(tid, act)}"}
            els.append({"tag": "action", "actions": [btn("✅ 采纳", "adopt", "primary"),
                        btn("🔁 返工", "rework", "default"), btn("🗑 废弃", "reject", "danger")]})
    return {"header": {"title": {"tag": "plain_text",
            "content": f"{ICON.get(phase,'·')} {tid} · {title[:30]} · {PHASE_NAME.get(phase, phase)}"},
            "template": COLOR.get(phase, "blue")}, "elements": els}


def _fallback_text(t, phase, report, extra):
    r = report or {}
    lines = [f"{ICON.get(phase,'·')} {t['id']} {t['title']}{PHASE_NAME.get(phase, phase)}"]
    if r.get("tldr"):
        lines.append(r["tldr"])
    lines += [f"· {h}" for h in (r.get("highlights") or [])[:3]]
    if (extra or {}).get("doc_url"):
        lines.append(f"☁️ {extra['doc_url']}")
    if (extra or {}).get("trace"):
        lines.append(f"trace: {extra['trace']}")
    return "\n".join(lines)


def notify(tid, phase, report=None, extra=None):
    """主入口:发/更新任务卡。任何失败降级 webhook 文本,绝不抛异常。"""
    try:
        c = _ensure_column()
        t = c.execute("SELECT * FROM tasks WHERE id=?", (tid,)).fetchone()
        if not t:
            return False
        card = _build_card(t, phase, report, extra)
        token, chat = _tenant_token(), _chat_id()
        if token and chat:
            try:
                if t["card_msg_id"]:
                    _api("PATCH", f"/im/v1/messages/{t['card_msg_id']}",
                         {"content": json.dumps(card, ensure_ascii=False)}, token)
                    return True
                r = _api("POST", "/im/v1/messages?receive_id_type=chat_id",
                         {"receive_id": chat, "msg_type": "interactive",
                          "content": json.dumps(card, ensure_ascii=False)}, token)
                mid = (r.get("data") or {}).get("message_id")
                if mid:
                    c.execute("UPDATE tasks SET card_msg_id=? WHERE id=?", (mid, tid))
                    c.commit()
                    return True
            except Exception:
                pass  # 落降级链
        if phase != "heartbeat":   # 降级为文本;心跳降级时沿用原文案由调用方处理
            _push_text(_fallback_text(dict(t), phase, report, extra))
        return False
    except Exception:
        return False


def parse_report(text):
    """从产出中提取 ```report 围栏块 → dict(tldr/highlights/action_needed/confidence)。
    容忍缩进/引号;解析失败返回 {}。不依赖 yaml 库(块结构受契约约束,手解更抗漂移)。"""
    import re
    m = re.search(r"```report\s*\n(.*?)```", text, re.S)
    if not m:
        return {}
    out, cur_list = {}, None
    for line in m.group(1).splitlines():
        s = line.strip()
        if s.startswith("- ") and cur_list is not None:
            cur_list.append(s[2:].strip().strip('"'))
            continue
        mm = re.match(r"^(tldr|highlights|action_needed|confidence):\s*(.*)$", s)
        if mm:
            k, v = mm.group(1), mm.group(2).strip().strip('"')
            if k == "highlights":
                cur_list = out.setdefault("highlights", [])
                if v and v not in ("", "[]"):
                    cur_list += [x.strip().strip('"') for x in v.strip("[]").split(",") if x.strip()]
            else:
                cur_list = None
                out[k] = v if v else None
    if out.get("action_needed") in ("null", "无", "None", ""):
        out["action_needed"] = None
    return out


if __name__ == "__main__":   # CLI: notifier.py <tid> <phase> ['{"tldr":...}'] ['{"cost":...}']
    rep = json.loads(sys.argv[3]) if len(sys.argv) > 3 else None
    ext = json.loads(sys.argv[4]) if len(sys.argv) > 4 else None
    print("sent" if notify(sys.argv[1], sys.argv[2], rep, ext) else "fallback")
