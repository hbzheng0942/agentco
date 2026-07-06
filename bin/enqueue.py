#!/usr/bin/env python3
"""enqueue.py <agent> <title> [--spec f] [--ttl N] [--silent] [--project P]
   [--priority N] [--depends-on TID] [--query Q] [--body B] [--difficulty light|medium|heavy]
无 --spec 且无 --body 时从 stdin 读任务描述。逻辑在 agentlib.enqueue(与飞书"派"/网关 /enqueue 共用)。"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from agentlib import enqueue

p = argparse.ArgumentParser()
p.add_argument("agent"); p.add_argument("title")
p.add_argument("--spec"); p.add_argument("--ttl", type=int, default=900)
p.add_argument("--silent", action="store_true")
p.add_argument("--project", default="default")
p.add_argument("--priority", type=int, default=2)
p.add_argument("--depends-on", dest="depends_on")
p.add_argument("--query")
p.add_argument("--difficulty", choices=["light", "medium", "heavy"],
               help="难度档→模型路由;缺省 executor=medium(GPT),其余 light")
p.add_argument("--body")
a = p.parse_args()
if a.spec:
    body = a.title
elif a.body is not None:
    body = a.body
else:
    body = sys.stdin.read().strip() or a.title
print(enqueue(a.agent, a.title, body, a.ttl, 0 if a.silent else 1, a.spec,
              project=a.project, priority=a.priority, depends_on=a.depends_on, query=a.query,
              difficulty=a.difficulty))
