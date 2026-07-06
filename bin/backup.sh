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
fi