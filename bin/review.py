#!/usr/bin/env python3
"""review.py — 验收CLI(与飞书卡片按钮同一逻辑,见agentlib.apply_review)
  review.py                     列出待验收
  review.py T-xxx adopt|rework|reject [备注]"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from agentlib import db, apply_review

if len(sys.argv) < 2:
    for r in db().execute("SELECT id,agent,title,result_path FROM tasks WHERE status='review' ORDER BY created_at"):
        print(f"{r['id']}  [{r['agent']}]  {r['title']}  -> {r['result_path']}")
    sys.exit(0)
ok, msg = apply_review(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "",
                       " ".join(sys.argv[3:]))
print(msg); sys.exit(0 if ok else 1)
