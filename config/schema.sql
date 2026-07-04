-- agentco state.db schema v1
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS tasks (
  id          TEXT PRIMARY KEY,              -- T-YYYYMMDD-NNN
  agent       TEXT NOT NULL,                 -- owl-intel / exec-ds / ...
  title       TEXT NOT NULL,
  spec_path   TEXT NOT NULL,                 -- handoff/T-xxx.md
  status      TEXT NOT NULL DEFAULT 'queued',-- queued|running|review|done|blocked
  tier        INTEGER NOT NULL DEFAULT 0,    -- 0=cheap 1=escalated
  attempts    INTEGER NOT NULL DEFAULT 0,
  ttl_sec     INTEGER NOT NULL DEFAULT 900,
  notify      INTEGER NOT NULL DEFAULT 1,    -- push result to feishu
  result_path TEXT,
  created_at  TEXT DEFAULT (datetime('now')),
  updated_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS events (          -- audit trail (metrics source)
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id TEXT, agent TEXT, kind TEXT,       -- claim|done|fail|escalate|block|rework
  detail TEXT, ts TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS feedback (        -- implicit signals for weekly critic
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  agent TEXT, task_id TEXT,
  signal TEXT,                               -- adopted|reworked|ignored|corrected
  note TEXT, ts TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_events_agent ON events(agent, ts);
