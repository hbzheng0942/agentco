#!/usr/bin/env bash
# verify.sh — ①波验收门探针,全绿才算部署完成
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
source .env 2>/dev/null || true
pass=0; fail=0
ck(){ if eval "$2" >/dev/null 2>&1; then echo "✅ $1"; pass=$((pass+1)); else echo "❌ $1"; fail=$((fail+1)); fi }

# 1. LiteLLM健康 + 两厂商真实调用
ck "litellm /health" "curl -sf -m 10 http://127.0.0.1:4000/health -H \"Authorization: Bearer \$LITELLM_MASTER_KEY\""
for m in ds-chat kimi-long; do
  ck "litellm chat [$m]" "curl -sf -m 60 http://127.0.0.1:4000/v1/chat/completions -H \"Authorization: Bearer \$LITELLM_MASTER_KEY\" -H 'Content-Type: application/json' -d '{\"model\":\"$m\",\"messages\":[{\"role\":\"user\",\"content\":\"reply OK\"}]}' | grep -qi ok"
done

# 2. Codex headless订阅认证(无浏览器环境OAuth是否存活)
ck "codex headless auth" "codex exec 'reply exactly: AUTH_OK' 2>/dev/null | grep -q AUTH_OK"

# 3. Codex经LiteLLM跑国产模型 + subagent cwd探针(沙箱语义确认)
ck "codex -p owl-intel via litellm" "codex exec -p owl-intel 'reply exactly: LITELLM_OK' 2>/dev/null | grep -q LITELLM_OK"
echo "→ 手动跑一次: codex exec -p owl-intel '报告你的cwd和你能看到的目录清单' 确认沙箱边界"

# 4. tool-call自动压测:20轮×两模型,malformed率>2%即FAIL
for m in ds-chat kimi-long; do
  ck "toolcall stress [$m]" "python3 bin/verify_toolcall.py 20 $m"
done

# 5. SQLite + 飞书 + 网关
ck "state.db schema" "sqlite3 state.db 'SELECT COUNT(*) FROM tasks'"
ck "feishu push" "bin/feishu_push.sh 'agentco verify ping'"
ck "gateway /health" "curl -sf -m 5 http://${GATEWAY_BIND:-127.0.0.1:9000}/health"

echo "---- pass=$pass fail=$fail ----"
[ $fail -eq 0 ]
