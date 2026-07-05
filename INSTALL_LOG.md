# INSTALL_LOG

## 2026-07-04

- 本机预检: python3 3.13.12, sqlite3 3.51.0, codex-cli 0.142.5。
- Codex 官方手册确认: Codex >=0.134 不再读取 `~/.codex/config.toml` 中的 `[profiles.*]`; `codex exec -p <name>` 改为加载 `$CODEX_HOME/<name>.config.toml`。
- 最小适配: `config/codex-config.toml.snippet` 仅保留 LiteLLM provider 和 `[agents]` 全局设置;新增 `config/codex-profiles/*.config.toml` 作为独立 profile 模板。
- 最小适配: `web_search = "live"` 替代旧的 `tools.web_search = true`, 只放在 `owl-intel`/`owl-intel-hi` profile 中,满足 Owl 联网检索要求。
- 最小适配: 为 `owl-intel` 和 `critic` profile 增加 `model_instructions_file`,确保 headless `codex exec -p` 也会读取对应 playbook 入口。
- 已创建 `.env` 并设置权限为 `600`;仍需填写真实 `DEEPSEEK_API_KEY`、`MOONSHOT_API_KEY`、`LITELLM_MASTER_KEY`、`FEISHU_WEBHOOK`、`GATEWAY_TOKEN`。
- 已在本地初始化 `state.db`;表为 `tasks`、`events`、`feedback`,journal mode 为 WAL。
- 腾讯云 Ubuntu 24.04 适配: LiteLLM 安装到项目 `.venv`;`install.sh` 优先使用 `$ROOT/.venv/bin/litellm` 生成 systemd 服务,避免系统 Python `--break-system-packages`。
- Codex 0.142.5 远端实测: `wire_api = "chat"` 已被拒绝;LiteLLM provider 改为 `wire_api = "responses"`。
- LiteLLM 已在腾讯云服务器以 systemd 方式部署,实际版本 `1.90.3`;`install.sh` 已 pin 到 `litellm[proxy]==1.90.3`,避免重跑安装时版本漂移。
- 2026-07-05 远端健康检查: LiteLLM 服务 active,但 `DEEPSEEK_API_KEY`、`MOONSHOT_API_KEY`、`FEISHU_WEBHOOK` 仍为占位值,模型调用返回 401。
