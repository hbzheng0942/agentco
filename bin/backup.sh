#!/usr/bin/env bash
# 每夜git备份(kb/agents/handoff/traces索引;state.db快照)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
sqlite3 state.db ".backup 'logs/state.$(date +%F).db'"
find logs -name 'state.*.db' -mtime +14 -delete
git add -A && git commit -m "auto: $(date +%F)" --quiet || true
git push --quiet 2>/dev/null || echo "no remote configured"
