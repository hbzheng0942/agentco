#!/usr/bin/env python3
"""verify_toolcall.py [N=20] [model=ds-chat] — LiteLLM tool-call压测
每轮要求模型调用get_file工具;统计 未调用/参数非法JSON/工具名错误 为malformed。
malformed率>2% 退出码1(换模型ID或升级LiteLLM后的30秒回归测试)。"""
import json, os, sys, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import load_env
load_env()

N = int(sys.argv[1]) if len(sys.argv) > 1 else 20
MODEL = sys.argv[2] if len(sys.argv) > 2 else "ds-chat"
KEY = os.environ.get("LITELLM_MASTER_KEY", "")
URL = "http://127.0.0.1:4000/v1/chat/completions"

TOOL = {"type": "function", "function": {
    "name": "get_file",
    "description": "读取指定路径的文件内容",
    "parameters": {"type": "object",
                   "properties": {"path": {"type": "string"}},
                   "required": ["path"]}}}

bad = 0
for i in range(N):
    req = {"model": MODEL, "tools": [TOOL], "tool_choice": "auto",
           "messages": [{"role": "user",
                         "content": f"调用get_file工具读取文件 kb/test-{i}.md,不要直接回答。"}]}
    try:
        r = urllib.request.Request(URL, json.dumps(req).encode(),
            {"Content-Type": "application/json", "Authorization": f"Bearer {KEY}"})
        resp = json.loads(urllib.request.urlopen(r, timeout=60).read())
        calls = resp["choices"][0]["message"].get("tool_calls") or []
        ok = bool(calls) and calls[0]["function"]["name"] == "get_file" \
             and "path" in json.loads(calls[0]["function"]["arguments"])
    except Exception as e:
        ok = False
        print(f"  round {i+1}: EXC {e}", file=sys.stderr)
    bad += 0 if ok else 1
    print(f"  round {i+1}/{N}: {'ok' if ok else 'MALFORMED'}")

rate = bad / N * 100
print(f"---- model={MODEL} malformed={bad}/{N} ({rate:.1f}%) 阈值2% ----")
sys.exit(1 if rate > 2 else 0)
