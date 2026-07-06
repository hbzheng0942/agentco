#!/usr/bin/env bash
# install.sh — 幂等部署(Ubuntu 22/24)。重复执行安全。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
LITELLM_VERSION="1.90.3"
echo "== agentco install @ $ROOT =="

# 0. 依赖
command -v python3 >/dev/null || { echo "need python3"; exit 1; }
command -v codex   >/dev/null || { echo "need codex: npm i -g @openai/codex && codex login --device-code"; exit 1; }
command -v sqlite3 >/dev/null || sudo apt-get install -y sqlite3
if [ ! -x "$ROOT/.venv/bin/litellm" ] && ! command -v litellm >/dev/null; then
  python3 -m venv "$ROOT/.venv"
  "$ROOT/.venv/bin/pip" install -U pip "litellm[proxy]==$LITELLM_VERSION"
fi
LITELLM_BIN="$ROOT/.venv/bin/litellm"
[ -x "$LITELLM_BIN" ] || LITELLM_BIN="$(command -v litellm)"

# 0b. codex 沙箱前提:Ubuntu24 kernel.apparmor_restrict_unprivileged_userns=1 会拦 bwrap 的
# userns(症状:worker 内 shell 全灭 "bwrap: loopback: Failed RTM_NEWADDR",agent 读不到文件
# 只能凭先验编造)。定向放行 bwrap,其余程序仍受限。
if [ -f /proc/sys/kernel/apparmor_restrict_unprivileged_userns ] && [ ! -f /etc/apparmor.d/bwrap ]; then
  sudo tee /etc/apparmor.d/bwrap > /dev/null << 'EOF'
abi <abi/4.0>,
include <tunables/global>
profile bwrap /usr/bin/bwrap flags=(unconfined) {
  userns,
}
EOF
  sudo apparmor_parser -r /etc/apparmor.d/bwrap
  echo "apparmor: bwrap userns 已放行"
fi

# 1. env
[ -f "$ROOT/.env" ] || { cp "$ROOT/.env.example" "$ROOT/.env"; echo "!! 编辑 .env 填key后重跑"; exit 1; }
set -a; source "$ROOT/.env"; set +a

# 2. state.db
sqlite3 "$ROOT/state.db" < "$ROOT/config/schema.sql"

# 3. Codex配置注入(幂等:标记块替换) + profile文件安装
CFG="$HOME/.codex/config.toml"; mkdir -p "$HOME/.codex/agents"
python3 - "$CFG" "$ROOT/config/codex-config.toml.snippet" << 'PY'
import sys, pathlib, re
cfg, snip = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]).read_text()
block = f"# >>> agentco >>>\n{snip}\n# <<< agentco <<<\n"
txt = cfg.read_text() if cfg.exists() else ""
txt = re.sub(r"# >>> agentco >>>.*?# <<< agentco <<<\n", "", txt, flags=re.S)
cfg.write_text(txt.rstrip() + "\n\n" + block)
print("config.toml updated")
PY
python3 - "$HOME/.codex" "$ROOT" << 'PY'
import pathlib, sys
codex_home = pathlib.Path(sys.argv[1])
root = pathlib.Path(sys.argv[2])
for src in (root/"config/codex-profiles").glob("*.config.toml"):
    txt = src.read_text().replace("/opt/agentco", str(root))
    dst = codex_home/src.name
    dst.write_text(txt)
    print(f"profile installed: {dst}")
PY
# subagent TOML软链:git仓 = single source of truth
for f in "$ROOT"/.codex/agents/*.toml; do ln -sf "$f" "$HOME/.codex/agents/$(basename "$f")"; done

# 4. litellm systemd服务
sudo tee /etc/systemd/system/litellm.service > /dev/null << EOF
[Unit]
Description=LiteLLM proxy (agentco)
After=network.target
[Service]
EnvironmentFile=$ROOT/.env
ExecStart=$LITELLM_BIN --config $ROOT/config/litellm.yaml --port 4000 --host 127.0.0.1
Restart=always
User=$USER
[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload && sudo systemctl enable --now litellm

# 4b. 飞书网关 systemd
sudo tee /etc/systemd/system/agentco-gateway.service > /dev/null << EOF
[Unit]
Description=agentco feishu gateway
After=network.target
[Service]
EnvironmentFile=$ROOT/.env
ExecStart=$(command -v python3) $ROOT/bin/feishu_gateway.py
WorkingDirectory=$ROOT
Restart=always
User=$USER
[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload && sudo systemctl enable --now agentco-gateway

# 5. git init
[ -d "$ROOT/.git" ] || { cd "$ROOT" && git init -q && cat > .gitignore << 'EOF'
.env
state.db*
logs/
traces/
.dispatch.lock
EOF
git add -A && git commit -qm init; }

echo "== done. 下一步: bash bin/verify.sh =="
echo "== 通过后: crontab -e 粘贴 crontab.txt(路径按实际部署位置改) =="
