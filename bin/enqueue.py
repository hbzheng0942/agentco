#!/usr/bin/env python3
"""enqueue.py <agent> <title> [--spec file.md] [--ttl 900] [--silent]
无--spec则从stdin读任务描述。逻辑在agentlib.enqueue(与飞书"派"命令共用)。"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from agentlib import enqueue

p = argparse.ArgumentParser()
p.add_argument("agent"); p.add_argument("title")
p.add_argument("--spec"); p.add_argument("--ttl", type=int, default=900)
p.add_argument("--silent", action="store_true")
a = p.parse_args()
body = a.title if a.spec else (sys.stdin.read().strip() or a.title)
print(enqueue(a.agent, a.title, body, a.ttl, 0 if a.silent else 1, a.spec))
