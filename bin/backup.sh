#!/usr/bin/env bash
# 每夜git备份 + 远程推送(cron 03:30)。
# state.db 用 sqlite .backup 出一致性快照:backup/state.db 被 git 跟踪→随 push 离机;
# live state.db 不直接入库(WAL 写入中拷贝可能不一致)。logs/ 留 14 天多代快照(不入 git)。
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p logs backup

# 1. state.db 快照(git 跟踪的离机副本 + 本地多代)
sqlite3 state.db ".backup 'backup/state.db'"
sqlite3 state.db ".backup 'logs/state.$(date +%F).db'"
find logs -name 'state.*.db' -mtime +14 -delete

# 2. 日志轮转:>10M gzip 归档保 3 代(logs 在 .gitignore,不轮转会无限涨)
for f in logs/*.log; do
  [ -f "$f" ] || continue
  if [ "$(stat -c%s "$f")" -gt 10485760 ]; then
    [ -f "$f.2.gz" ] && mv "$f.2.gz" "$f.3.gz"
    [ -f "$f.1.gz" ] && mv "$f.1.gz" "$f.2.gz"
    gzip -c "$f" > "$f.1.gz"; : > "$f"
  fi
done

# 3. git 提交 + 推送(推当前分支;固定推 master 会推到陈旧的本地 master)
git add -A
if ! git diff --cached --quiet; then
  git commit -m "auto-backup: $(date '+%Y-%m-%d %H:%M:%S')" --quiet
  echo "[$(date)] local commit created" >> logs/backup.log
else
  echo "[$(date)] no changes to commit" >> logs/backup.log
fi
if git remote get-url private >/dev/null 2>&1; then
  if git push private "$(git rev-parse --abbrev-ref HEAD)" --quiet 2>>logs/backup.log; then
    echo "[$(date)] ✅ push success" >> logs/backup.log
  else
    echo "[$(date)] ❌ push FAILED" >> logs/backup.log
    bash bin/feishu_push.sh "🛑 夜间备份 push 失败,当前备份仅在本机!详见 logs/backup.log"
  fi
else
  echo "[$(date)] ❌ 'private' remote 未配置,备份仅本地!" >> logs/backup.log
  bash bin/feishu_push.sh "🛑 夜间备份:git remote 'private' 未配置,备份仅在本机!"
fi
