#!/usr/bin/env bash
# gpu_worker.sh — 本地 M4 开机手动跑。3D 异步:拉服务器 waiting_gpu 任务 → 本地 Blender 执行 → scp 回写。
# 云端 Blender 未装,故 3D 走此本地通道(见 agents/executor/AGENT.md §3D)。GPU 失败直接 blocked,不升级。
#
# 用法(在 mac M4 上):AGENTCO_SSH=user@server bash gpu_worker.sh
# 依赖:ssh/scp 可达服务器;本地 blender 在 PATH。
set -uo pipefail
: "${AGENTCO_SSH:?需设 AGENTCO_SSH=user@server}"
REMOTE_ROOT="${AGENTCO_REMOTE_ROOT:-/opt/agentco}"
RDB="$REMOTE_ROOT/state.db"
SQL() { ssh "$AGENTCO_SSH" "sqlite3 '$RDB' \"$1\""; }

# 取一个 waiting_gpu 任务(优先级序)
TID=$(SQL "SELECT id FROM tasks WHERE status='waiting_gpu' ORDER BY priority,created_at LIMIT 1")
[ -z "$TID" ] && { echo "无 waiting_gpu 任务"; exit 0; }
echo "认领 $TID"
SPEC=$(SQL "SELECT spec_path FROM tasks WHERE id='$TID'")
PROJ=$(SQL "SELECT COALESCE(NULLIF(project,''),'default') FROM tasks WHERE id='$TID'")
SQL "UPDATE tasks SET status='running',updated_at=datetime('now') WHERE id='$TID'"
SQL "INSERT INTO events(task_id,agent,kind,detail) VALUES('$TID','executor-3d','claim','gpu_worker')"

WORK=$(mktemp -d)
scp "$AGENTCO_SSH:$REMOTE_ROOT/$SPEC" "$WORK/spec.md" || { echo "scp spec 失败"; exit 1; }

# —— 本地 Blender 执行(占位:按 spec 组织实际渲染/建模命令)——
OUT="$WORK/${TID}.result.md"
if command -v blender >/dev/null && bash "$WORK/run_blender.sh" 2>"$WORK/err.log"; then
  ssh "$AGENTCO_SSH" "mkdir -p '$REMOTE_ROOT/handoff/$PROJ'"
  scp "$OUT" "$AGENTCO_SSH:$REMOTE_ROOT/handoff/$PROJ/${TID}.result.md"
  SQL "UPDATE tasks SET status='review',result_path='handoff/$PROJ/${TID}.result.md',updated_at=datetime('now') WHERE id='$TID'"
  SQL "INSERT INTO events(task_id,agent,kind,detail) VALUES('$TID','executor-3d','done','gpu_worker')"
  echo "$TID → review"
else
  # GPU 失败:直接 blocked,不升级(见 3.5)
  SQL "UPDATE tasks SET status='blocked',updated_at=datetime('now') WHERE id='$TID'"
  SQL "INSERT INTO events(task_id,agent,kind,detail) VALUES('$TID','executor-3d','block','gpu failed / blender missing')"
  echo "$TID → blocked (GPU 失败,不升级)"
fi
rm -rf "$WORK"
