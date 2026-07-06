#!/usr/bin/env bash
# verify.sh — Wave③ 验收门探针,全绿才算部署完成。
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
set -a; source .env 2>/dev/null || true; set +a  # set -a:.env无export前缀,不加则codex等子进程拿不到LITELLM_MASTER_KEY
pass=0; fail=0; skip=0
ck(){ if eval "$2" >/dev/null 2>&1; then echo "✅ $1"; pass=$((pass+1)); else echo "❌ $1"; fail=$((fail+1)); fi }
sk(){ echo "⏭  SKIP $1"; skip=$((skip+1)); }

# 0. 地基:schema 重放 + tasks 新列 + events 触发器 + append-only
bash bin/migrate.sh >/dev/null 2>&1
ck "schema: tasks 有 project/priority/depends_on" "sqlite3 state.db 'SELECT project,priority,depends_on FROM tasks LIMIT 1' >/dev/null; sqlite3 state.db \"PRAGMA table_info(tasks)\" | grep -q depends_on"
ck "schema: events 双触发器存在" "[ \$(sqlite3 state.db \"SELECT count(*) FROM sqlite_master WHERE type='trigger' AND name LIKE 'events_no_%'\") -eq 2 ]"
# append-only 的行为验证在 selftest(临时 DB)跑,不向生产 events 写测试行(append-only 不可删)

# 1. Wave③ 逻辑自测(临时 DB,不碰生产):search 四路含 news/依赖边/优先级/3D/skill_hit/cache_gc豁免/shared/brief五段
ck "selftest: Wave③ 全逻辑" "python3 bin/selftest.py"

# 2. LiteLLM 健康 + 两厂商真实调用
ck "litellm /health" "curl -sf -m 10 http://127.0.0.1:4000/health -H \"Authorization: Bearer \$LITELLM_MASTER_KEY\""
for m in ds-chat kimi-long qwen-max; do
  ck "litellm chat [$m]" "curl -sf -m 60 http://127.0.0.1:4000/v1/chat/completions -H \"Authorization: Bearer \$LITELLM_MASTER_KEY\" -H 'Content-Type: application/json' -d '{\"model\":\"$m\",\"messages\":[{\"role\":\"user\",\"content\":\"reply OK\"}]}' | grep -qi ok"
done

# 3. Codex headless auth + 经 LiteLLM 跑国产模型(新 profile)
# bwrap 沙箱可用性:Ubuntu24 apparmor_restrict_unprivileged_userns=1 会让 codex 内 shell 全灭,
# agent 读不到文件只能靠先验编造(2026-07-06 实锤)。需 /etc/apparmor.d/bwrap 放行 userns。
ck "bwrap 沙箱可用(codex worker shell 前提)" "bwrap --unshare-all --ro-bind / / /bin/true"
ck "codex headless auth" "codex exec 'reply exactly: AUTH_OK' 2>/dev/null | grep -q AUTH_OK"
ck "codex -p auditor via litellm" "codex exec -p auditor --skip-git-repo-check 'reply exactly: LITELLM_OK' 2>/dev/null | grep -q LITELLM_OK"
ck "难度路由 profile 已装(executor-data-hi/retriever-long)" "test -f ~/.codex/executor-data-hi.config.toml && test -f ~/.codex/retriever-long.config.toml"
echo "→ 手动:codex exec -p retriever '报告cwd和可见目录' 确认沙箱边界;确认 retriever 无联网(trace 无 web_search)"

# 4. tool-call 压测
for m in ds-chat kimi-long; do ck "toolcall stress [$m]" "python3 bin/verify_toolcall.py 20 $m"; done
ck "toolcall stress [qwen-max]" "python3 bin/verify_toolcall.py 5 qwen-max"   # qwen按token计费,5轮抽检

# 5. search.py 端到端活探针(执行注意点①:真跑带 news 的 query,确认两家 news endpoint 都通)
if [ -n "${BRAVE_API_KEY:-}" ] || [ -n "${SERPER_API_KEY:-}" ]; then
  RAW=$(python3 bin/search.py --project _verify --query "AI spatial intelligence latest news" 2>/dev/null)
  if [ -n "$RAW" ] && [ -f "$ROOT/$RAW" ]; then
    ck "search.py: raw 落盘带 content_hash" "grep -q '^content_hash: ' \"$ROOT/$RAW\""
    ck "search.py: Brave news endpoint 通(/res/v1/news/search 独立于 web)" "grep -q 'brave_news: ok(' \"$ROOT/$RAW\""
    ck "search.py: Serper news endpoint 通(/news 独立于 /search)" "grep -q 'serper_news: ok(' \"$ROOT/$RAW\""
    ck "search.py: 四路加权去重后 top≤12" "[ \$(grep -c '^## ' \"$ROOT/$RAW\") -le 12 ]"
    echo "   ↳ routes 实况: $(grep -A5 '^routes:' "$ROOT/$RAW" | grep ': ' | tr '\n' ' ')"
    rm -rf "$ROOT/kb/30-projects/_verify"
  else
    ck "search.py: 活探针产出 raw" "false"
  fi
else
  sk "search.py 活探针:BRAVE_API_KEY / SERPER_API_KEY 均未配(执行注意点①要求配 key 后必跑,确认两家 news 都通)"
fi

# 6. SQLite + 飞书 + 网关(/health + /enqueue 鉴权)
ck "feishu push" "bin/feishu_push.sh 'agentco verify ping'"
ck "gateway /health" "curl -sf -m 5 http://\${GATEWAY_BIND:-127.0.0.1:9000}/health"
ck "gateway /enqueue 拒绝无 token" "[ \$(curl -s -o /dev/null -w '%{http_code}' -m5 \"http://\${GATEWAY_BIND:-127.0.0.1:9000}/enqueue?agent=retriever&title=x\") = 403 ]"
ck "gateway /api/stats 鉴权+可用" "[ \$(curl -s -o /dev/null -w '%{http_code}' -m5 \"http://\${GATEWAY_BIND:-127.0.0.1:9000}/api/stats\") = 403 ] && curl -sf -m5 \"http://\${GATEWAY_BIND:-127.0.0.1:9000}/api/stats?token=\$GATEWAY_TOKEN\" | grep -q '\"status\"'"
ck "kb_lint 可运行(死链/冗余体检)" "python3 bin/kb_lint.py"
ck "proposals 表就位(进化闭环)" "sqlite3 state.db 'SELECT count(*) FROM proposals'"

echo "---- pass=$pass fail=$fail skip=$skip ----"
[ $fail -eq 0 ]
