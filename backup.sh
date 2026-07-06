cd /opt/agentco || exit 1

# 添加 state.db（如果存在）
[ -f state.db ] && git add state.db -f

# 提交（有变更才提交）
if ! git diff --cached --quiet; then
    git commit -m "Auto-backup: $(date '+%Y-%m-%d %H:%M:%S')"
    git push private master
    echo "[$(date)] Backup pushed to GitHub" >> /var/log/backup.log
else
    echo "[$(date)] No changes to backup" >> /var/log/backup.log
fi
