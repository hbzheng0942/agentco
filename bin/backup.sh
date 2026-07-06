#!/usr/bin/env bash
# 每夜git备份 + 远程推送
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# 确保 logs 目录存在
mkdir -p logs

# 1. 备份 state.db 到 logs
sqlite3 state.db ".backup 'logs/state.$(date +%F).db'"

# 2. 清理 14 天前的旧备份
find logs -name 'state.*.db' -mtime +14 -delete

# 3. Git 提交本地变更
git add -A
if ! git diff --cached --quiet; then
    git commit -m "auto: $(date +%F)"
    echo "[$(date)] Local commit created" >> logs/backup.log
else
    echo "[$(date)] No changes to commit" >> logs/backup.log
fi

# 4. 推送到 GitHub
if git remote get-url private >/dev/null 2>&1; then
    echo "[$(date)] Pushing to GitHub..." >> logs/backup.log
    if git push private master >> logs/backup.log 2>&1; then
        echo "[$(date)] Push to GitHub SUCCESS" >> logs/backup.log
    else
        echo "[$(date)] Push to GitHub FAILED" >> logs/backup.log
    fi
else
    echo "[$(date)] ERROR: private remote not configured" >> logs/backup.log
    exit 1
fi#!/usr/bin/env bash
# 每夜git备份:state.db 一致性快照(backup/,git跟踪→随push离机)+ kb/handoff 全量 + 日志轮转。
# 注:live state.db 不直接入库(WAL 写入中拷贝可能不一致),用 sq
mkdir -p backup
sqlite3 state.db ".backup 'backup/state.db'"          # 一致性快照,git 跟踪
sqlite3 state.db ".backup 'logs/state.$(date +%F).db'" # 本地留 14 天多代快照(logs 不入git)
find logs -name 'state.*.db' -mtime +14 -delete

# 日志轮转:>10M gzip 归档保 3 代(logs 在 .gitignore,不轮转会无限涨)
for f in logs/*.log; do
  [ -f "$f" ] || continue
  if [ "$(stat -c%s "$f")" -gt 10485760 ]; then
    [ -f "$f.2.gz" ] && mv "$f.2.gz" "$f.3.gz"
    [ -f "$f.1.gz" ] && mv "$f.1.gz" "$f.2.gz"
    gzip -c "$f" > "$f.1.#!/usr/bin/env bash
# 每夜git备份:state.db 一致性快照(backup/,git跟踪→随push离机)+ kb/hand>
# 注:live state.db 不直接入库(WAL 写入中拷贝可能不一致),用 sq     
mkdir -p backup
sqlite3 state.db ".backup 'backup/state.db'"          # 一致性快照,git>
sqlite3 state.db ".backup 'logs/state.$(date +%F).db'" # 本地留 14 天[>
fi #!/usr/bin/env bash
# 每夜git备份 + 远程推送
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# 确保 logs 目录存在
mkdir -p logs

# 1. 备份 state.db 到 logs
sqlite3 state.db ".backup 'logs/state.$(date +%F).db'"

# 2. 清理 14 天前的旧备份
find logs -name 'state.*.db' -mtime +14 -delete

# 3. Git 提交本地变更
git add -A
if ! git diff --cached --quiet; then
    git commit -m "auto: $(date +%F)"
    echo "[$(date)] Local commit created" >> logs/backup.log
else
    echo "[$(date)] No changes to commit" >> logs/backup.log
fi

# 4. 推送到 GitHub（必须有 remote）
if git remote get-url private >/dev/null 2>&1; then
    if git push private master 2>&1 | tee -a logs/backup.log; then
        echo "[$(date)] ✅ Push to GitHub SUCCESS" >> logs/backup.log
    else
        echo "[$(date)] ❌ Push to GitHub FAILED" >> logs/backup.log
    fi
else
    echo "[$(date)] ❌ ERROR: 'private' remote not configured" >> logs/backup.log
    exit 1
find logs -name 'state.*.db' -mtime +14 -delete

# 日志轮转:>10M gzip 归档保 3 代(logs 在 .gitignore,不轮转会无限涨)
for f in logs/*.log; do
  [ -f "$f" ] || continue
  if [ "$(stat -c%s "$f")" -gt 10485760 ]; then
    [ -f "$f.2.gz" ] && mv "$f.2.gz" "$f.3.gz"
    [ -f "$f.1.gz" ] && mv "$f.1.gz" "$f.2.gz"
    gzip -c "$f" > "$f.1.  
if ! git diff --cached --quiet; then
  git commit -m "auto-backup: $(date '+%Y-%m-%d %H:%M:%S')" --quiet
  # 推当前分支(注意:push master 会推到陈旧的本地 master)
  git push private "$(git rev-parse --abbrev-ref HEAD)" --quiet \
    && echo "[$(date)] backup pushed" >> logs/cron.log \
    || bash bin/feishu_push.sh "🛑 夜间备份 push 失败,当前备份仅在本机>
else
  echo "[$(date)] no changes to backup" >> logs/cron.log
fi
if ! git diff --cached --quiet; then
  git commit -m "auto-backup: $(date '+%Y-%m-%d %H:%M:%S')" --quiet
  # 推当前分支(注意:push master 会推到陈旧的本地 master)
  git push private "$(git rev-parse --abbrev-ref HEAD)" --quiet \
    && echo "[$(date)] backup pushed" >> logs/cron.log \
    || bash bin/feishu_push.sh "🛑 夜间备份 push 失败,当前备份仅在本机!"
else
  echo "[$(date)] no changes to backup" >> logs/cron.log
fi
