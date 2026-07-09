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
p.add_argument("--query", action="append", help="可重复:多聚焦子query")
p.add_argument("--sources", help="逗号分隔:github,reddit,hn,x,xiaohongshu,wechat")
p.add_argument("--difficulty", choices=["light", "medium", "heavy"],
               help="难度档→模型路由;缺省 executor=medium(GPT),其余 light")
p.add_argument("--body")
a = p.parse_args()
if a.spec:
    # spec 模式下 body 不进投递链路(worker 只见 spec+title)。曾静默丢弃 --body
    # 致任务缺参数被 blocked(2026-07-09 T-002~006 实锤)→ 改为响亮拒绝。
    if a.body is not None:
        sys.exit("enqueue: --spec 与 --body 不能并用(worker 只读 spec 内容,title/body 都不进 prompt)。"
                 "参数化任务用 --body:body 会落成该任务专属 spec,在 body 里引用共享规约文件即可。")
    body = a.title
elif a.body is not None:
    body = a.body
else:
    body = sys.stdin.read().strip() or a.title
print(enqueue(a.agent, a.title, body, a.ttl, 0 if a.silent else 1, a.spec,
              project=a.project, priority=a.priority, depends_on=a.depends_on, query=a.query,
              difficulty=a.difficulty,
              sources=[s.strip() for s in a.sources.split(",") if s.strip()] if a.sources else None))
