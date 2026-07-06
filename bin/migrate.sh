#!/usr/bin/env bash
# migrate.sh — 幂等落 schema:重放 schema.sql(不损数据)+ 存量表补列。
# 可安全重复执行。install.sh 与手动升级共用。
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DB="$ROOT/state.db"

# 1. 存量 tasks 先补列(schema.sql 的新列索引依赖这些列先存在)。
#    SQLite 无 ADD COLUMN IF NOT EXISTS;表不存在(全新库)或列已存在时忽略报错。
for stmt in \
  "ALTER TABLE tasks ADD COLUMN project TEXT DEFAULT 'default'" \
  "ALTER TABLE tasks ADD COLUMN priority INTEGER DEFAULT 2" \
  "ALTER TABLE tasks ADD COLUMN depends_on TEXT"; do
  sqlite3 "$DB" "$stmt" 2>/dev/null || true
done

# 2. 重放目标 schema(全 IF NOT EXISTS;全新库在此建全部表+列+索引+触发器)
sqlite3 "$DB" < "$ROOT/config/schema.sql"

echo "migrate ok: $(sqlite3 "$DB" "SELECT count(*) FROM sqlite_master WHERE type='table'") tables, "\
"$(sqlite3 "$DB" "SELECT count(*) FROM sqlite_master WHERE type='trigger'") triggers"
