-- agentco state.db schema v2 (Wave③)
-- 全 IF NOT EXISTS,可重放不损数据。新增列由 install.sh / migrate 段用 ALTER 幂等补(见文件尾注)。
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS tasks (
  id          TEXT PRIMARY KEY,              -- T-YYYYMMDD-NNN
  agent       TEXT NOT NULL,                 -- retriever / executor / digester / auditor
  title       TEXT NOT NULL,
  spec_path   TEXT NOT NULL,                 -- handoff/<project>/T-xxx.md
  status      TEXT NOT NULL DEFAULT 'queued',
  -- status: queued|running|review|done|blocked|waiting_dep|waiting_gpu|dep_failed
  tier        INTEGER NOT NULL DEFAULT 0,    -- 0=cheap 1=escalated
  attempts    INTEGER NOT NULL DEFAULT 0,
  ttl_sec     INTEGER NOT NULL DEFAULT 900,
  notify      INTEGER NOT NULL DEFAULT 1,    -- push result to feishu
  project     TEXT DEFAULT 'default',        -- 项目隔离 (Wave③)
  priority    INTEGER DEFAULT 2,             -- 1=高 2=常规 3=低 (Wave③)
  depends_on  TEXT,                          -- 上游 task_id;NULL=无依赖 (Wave③)
  result_path TEXT,
  created_at  TEXT DEFAULT (datetime('now')),
  updated_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS events (          -- 不可变审计流 (metrics source)
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id TEXT, agent TEXT, kind TEXT,       -- claim|done|fail|escalate|block|rework|dep_triggered|dep_failed|cache_gc|skill_hit|...
  detail TEXT, ts TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS feedback (        -- 人工验收信号 (weekly critic 权重最高)
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  agent TEXT, task_id TEXT,
  signal TEXT,                               -- adopted|reworked|ignored|corrected
  note TEXT, ts TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS seen_events (     -- 幂等标记:依赖触发/一次性动作去重
  tag TEXT PRIMARY KEY,                       -- e.g. 'dep_triggered:T-xxx' / 'dep_failed:T-xxx'
  ts  TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_tasks_status   ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_depends  ON tasks(depends_on);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority, created_at);
CREATE INDEX IF NOT EXISTS idx_events_agent   ON events(agent, ts);

-- events 追加即封:UPDATE / DELETE 一律拒绝 (溯源链不可篡改)
CREATE TRIGGER IF NOT EXISTS events_no_update BEFORE UPDATE ON events
BEGIN SELECT RAISE(ABORT, 'events is append-only'); END;
CREATE TRIGGER IF NOT EXISTS events_no_delete BEFORE DELETE ON events
BEGIN SELECT RAISE(ABORT, 'events is append-only'); END;

-- 存量库补列(SQLite 无 IF NOT EXISTS for ADD COLUMN):由 migrate.sh / install.sh 以 `|| true` 幂等执行:
--   ALTER TABLE tasks ADD COLUMN project TEXT DEFAULT 'default';
--   ALTER TABLE tasks ADD COLUMN priority INTEGER DEFAULT 2;
--   ALTER TABLE tasks ADD COLUMN depends_on TEXT;
