"""代理层临门一脚洗报文 —— 无论 Codex 怎么裁剪上下文,都在调用上游前修补成 DeepSeek 需要的标准格式。

三件事(都在 async_pre_call_hook 里):
  1. 剥离内置非 function 工具定义:Codex 0.142+ responses 载荷带 type=namespace/web_search 等,
     DeepSeek/Moonshot 反序列化直接 400(codex 已移除 wire_api="chat",只能代理层过滤)。
  2. 补 reasoning_content:DeepSeek V4 推理档(ds-reasoner=deepseek-v4-pro)要求带 tool_calls 的
     assistant 消息回传 reasoning_content,否则 400 "reasoning_content must be passed back"。
     Codex 的 responses→chat 变换会丢它,这里对缺失者补占位(空串即被接受,已 VERIFY)。
  3. 补齐孤立 tool_calls:assistant.tool_calls 的每个 id 必须紧跟对应 tool 消息,否则 400
     "tool_calls must be followed by tool messages"。变换偶发丢配对,这里为缺失 id 合成占位 tool 回复。

外加一件(log 钩子):router 发生 fallback 换模型(如 qwen-max→ds-chat)或连兜底全挂时,
飞书出站通知为何失败、切成了什么(宪法要求;10 分钟冷却防刷屏)。
"""
import json
import os
import subprocess
import time
from datetime import datetime

from litellm.integrations.custom_logger import CustomLogger

_DEBUG = os.environ.get("LITELLM_HOOK_DEBUG", "") == "1"
_LOG = os.path.join(os.path.dirname(__file__), "..", "logs", "litellm_hook.log")


def _dbg(msg):
    if not _DEBUG:
        return
    try:
        with open(_LOG, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} {msg}\n")
    except Exception:
        pass


def _strip_tools(data):
    tools = data.get("tools")
    if isinstance(tools, list):
        kept = [
            t for t in tools
            if not isinstance(t, dict) or t.get("type") in (None, "function")
        ]
        if kept:
            data["tools"] = kept
        else:
            # 全被过滤时连 tool_choice 一起清掉,防上游报 "tool_choice 但无 tools"
            data.pop("tools", None)
            data.pop("tool_choice", None)


def _sanitize_messages(messages):
    patched_reasoning = 0
    stubbed_tools = 0

    # 1) 带 tool_calls 的 assistant 补 reasoning_content(reasoner 强制,chat 无害)
    for m in messages:
        if (isinstance(m, dict) and m.get("role") == "assistant"
                and m.get("tool_calls") and not m.get("reasoning_content")):
            m["reasoning_content"] = ""
            patched_reasoning += 1

    # 2) 每个 assistant.tool_calls 的 id 都要紧跟一条 tool 消息;缺失者合成占位
    out = []
    i, n = 0, len(messages)
    while i < n:
        m = messages[i]
        out.append(m)
        if (isinstance(m, dict) and m.get("role") == "assistant"
                and isinstance(m.get("tool_calls"), list)):
            ids = [tc.get("id") for tc in m["tool_calls"]
                   if isinstance(tc, dict) and tc.get("id")]
            j = i + 1
            seen = set()
            while j < n and isinstance(messages[j], dict) and messages[j].get("role") == "tool":
                out.append(messages[j])
                seen.add(messages[j].get("tool_call_id"))
                j += 1
            for cid in ids:
                if cid not in seen:
                    out.append({"role": "tool", "tool_call_id": cid,
                                "content": "(tool output unavailable)"})
                    stubbed_tools += 1
            i = j
            continue
        i += 1

    return out, patched_reasoning, stubbed_tools


def _sanitize_input(items):
    """Responses 载荷(data["input"])重排:确保每组 function_call 后紧跟其 function_call_output,
    中间不夹 assistant message。Codex 会把 assistant 叙述文本插在 tool_call 与其 output 之间,
    litellm 转 chat 后就变成 [assistant.tool_calls][assistant.text][tool...],DeepSeek 因
    "tool_calls 后未紧跟 tool 消息" 400。这里把夹在中间的 assistant message 提到 tool_call 组之前。
    """
    out = []
    reordered = 0
    i, n = 0, len(items)
    while i < n:
        it = items[i]
        if isinstance(it, dict) and it.get("type") == "function_call":
            fcs, fcos, strays = [], [], []
            j = i
            while j < n:
                x = items[j]
                xt = x.get("type") if isinstance(x, dict) else None
                if xt == "function_call":
                    if fcos:
                        break                   # 已开始收 output 又见 function_call = 下一回合,切断
                    fcs.append(x); j += 1
                elif xt == "function_call_output":
                    fcos.append(x); j += 1
                elif xt == "message" and x.get("role") == "assistant" and not fcos:
                    strays.append(x); j += 1   # tool_call 之前的叙述,提前
                else:
                    break                       # user 消息或 output 之后的 assistant = 新回合,不动
            if strays:
                reordered += len(strays)
            out.extend(strays); out.extend(fcs); out.extend(fcos)
            i = j
            continue
        out.append(it); i += 1
    return out, reordered


# ---- 故障切换出站通知(宪法:任何失败切模型都必须说明为何失败、切成了什么)----
_NOTIFY_COOLDOWN = 600          # 同一切换路径 10 分钟内只报一次,防 codex 多轮调用刷屏
_last_notify = {}


def _feishu(text):
    try:
        script = os.path.join(os.path.dirname(__file__), "..", "bin", "feishu_push.sh")
        subprocess.Popen([script, text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        _dbg(f"feishu push failed: {e}")


def _fallback_info(kwargs):
    """router 发生过 fallback/重试换模型时,metadata.previous_models 记录失败尝试。
    返回 (失败模型列表文本, 原因文本, 当前模型组) 或 None。条目格式随 litellm 版本浮动,防御式取值。"""
    meta = (kwargs.get("litellm_params") or {}).get("metadata") or kwargs.get("metadata") or {}
    prev = meta.get("previous_models") or []
    if not prev:
        return None
    failed, reasons = [], []
    for p in prev:
        if isinstance(p, dict):
            f = str(p.get("model") or p.get("model_group") or "?")
            r = str(p.get("exception_string") or p.get("exception_type") or "")[:200]
            if r and r not in reasons:
                reasons.append(r)
        else:
            f = str(p)[:80]
        if f not in failed:                # 同模型重试 N 次只列一次
            failed.append(f)
    cur = meta.get("model_group") or kwargs.get("model") or "?"
    return " → ".join(failed), ("; ".join(reasons) or "unknown"), str(cur)


def _maybe_notify_fallback(kwargs, final_error=None):
    # failure 事件按"每次尝试"触发;只有 previous_models 非空(=前面已换过模型)才是兜底也挂,
    # 首次尝试失败不报——router 随后要么 fallback 成功(success 事件报切换),要么最终失败再报。
    info = _fallback_info(kwargs)
    if not info:
        return
    failed, why, cur = info
    if final_error is not None:
        head = f"🛑 litellm 连同兜底全部失败:{failed} → {cur}"
        fe = str(final_error)[:200]
        if fe not in why:
            why = (why + " | final: " + fe).strip(" |")
    else:
        head = f"⚠️ litellm 故障切换:{failed} → 已切至 {cur}"
    key = (head.split(":")[0], failed, cur)
    now = time.time()
    if now - _last_notify.get(key, 0) < _NOTIFY_COOLDOWN:
        return
    _last_notify[key] = now
    _dbg(f"fallback notify: {head} why={why}")
    _feishu(f"{head}\n原因:{why}")


class ToolSanitizer(CustomLogger):
    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        _strip_tools(data)
        msgs = data.get("messages")
        if isinstance(msgs, list) and msgs:
            data["messages"], pr, st = _sanitize_messages(msgs)
            if _DEBUG:
                _dbg(f"[chat] model={data.get('model')} msgs={len(msgs)} "
                     f"reasoning_patched={pr} tool_stubs={st}")
        elif isinstance(data.get("input"), list) and data["input"]:
            if _DEBUG:
                try:
                    with open(os.path.join(os.path.dirname(_LOG), "hook_inputs.jsonl"), "a") as f:
                        f.write(json.dumps({"n": len(data["input"]), "input": data["input"]},
                                           ensure_ascii=False, default=str) + "\n")
                except Exception:
                    pass
            data["input"], ro = _sanitize_input(data["input"])
            if _DEBUG:
                _dbg(f"[resp] model={data.get('model')} input_items={len(data['input'])} reordered={ro}")
        return data

    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        # 成功但走过 fallback(previous_models 非空)→ 出站说明
        _maybe_notify_fallback(kwargs)

    async def async_log_failure_event(self, kwargs, response_obj, start_time, end_time):
        # 连兜底也失败 → 出站说明(dispatcher 只报任务 blocked,不报模型层原因)
        _maybe_notify_fallback(kwargs, final_error=kwargs.get("exception") or response_obj)


proxy_handler_instance = ToolSanitizer()
