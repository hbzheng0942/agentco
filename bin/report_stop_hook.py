#!/usr/bin/env python3
"""Stop hook:强制 envelope 2.0 report 块(claude -p worker 专用)。
最终 assistant 消息缺 ```report 块(或块内无 tldr:)→ block 一次打回重写;
stop_hook_active=True 时放行(防死循环:补写后二次 Stop 不再拦)。
任何解析异常一律放行——hook 只能锦上添花,绝不能把任务卡死。
"""
import json
import sys
from pathlib import Path


def last_assistant_text(transcript_path):
    text = ""
    try:
        for line in Path(transcript_path).read_text().splitlines():
            try:
                d = json.loads(line)
            except Exception:
                continue
            if d.get("type") != "assistant":
                continue
            content = (d.get("message") or {}).get("content") or []
            chunk = "".join(c.get("text", "") for c in content
                            if isinstance(c, dict) and c.get("type") == "text")
            if chunk.strip():
                text = chunk
    except Exception:
        return None
    return text


def main():
    try:
        inp = json.load(sys.stdin)
    except Exception:
        return
    if inp.get("stop_hook_active"):
        return  # 已经打回过一次,放行,不死循环
    text = last_assistant_text(inp.get("transcript_path", ""))
    if text is None:
        return  # transcript 读不到:放行
    if "```report" in text and "tldr:" in text:
        return
    print(json.dumps({
        "decision": "block",
        "reason": ("产出缺 report 块。在回复结尾补上(必须原样使用 ```report 围栏):\n"
                   "```report\ntldr: 一句话结论(≤40字)\nhighlights:\n  - 要点1\n  - 要点2\n"
                   "action_needed: null 或 需人裁决事项\nconfidence: high|medium|low\n```\n"
                   "⚠️ 系统只落盘你的最后一条消息:必须把完整正文+report块+envelope 在同一条消息里"
                   "重新输出(正文原样照抄你上一条消息,不要缩写),然后按原规范附 envelope。")
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
