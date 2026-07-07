---
date: 2026-07-07
scope: 系统级(全域)
status: applied
decider: HB(飞书拍板"一次性切了吧") + CC 执行
---

# Wave④ 决策:worker 引擎 codex→Claude Code + 出入站体验重构

## 决策内容(已全部落地并 E2E 验证)

| # | 决策 | 裁决 |
|---|------|------|
| D1 | worker 引擎 codex exec → claude -p(经 litellm /v1/messages) | ✅ 一次性全切,不留双引擎 |
| D2 | GPT 通道:ChatGPT Plus 经 CLIProxyAPI(vendor/cliproxyapi,systemd)转 API 入 litellm(`gpt-plus`) | ✅ 接受 ToS 灰区风险;未登录期 fallback ds-reasoner+出站说明 |
| D3 | envelope 2.0:产出强制 ```report 块(tldr/highlights/action_needed/confidence),Stop hook 协议级打回 | ✅ 模型独白从此不上卡 |
| D4 | 出站:群 webhook 文本 → 应用机器人一任务一卡原地更新(bin/notifier.py);降级链 webhook 保留 | ✅ |
| D5 | 入站:双速。快车道规则直通;慢车道 concierge(haiku,订阅额度,多轮 --resume);bridge 降为兜底 | ✅ concierge 无工具,动作 JSON 过 bridge.validate_plan 白名单 |
| D6 | 飞书生态:吃管道(消息API/卡片/docx),不进大脑(Aily 不接);lark-mcp 二期再议 | ✅ |
| D7 | auditor 暂留 qwen-max(半价活动期沉淀经验),活动结束评估切 gpt-plus | ✅ 改 litellm.yaml 一行即切 |

## 关键实现事实

- profile 定义:`config/claude-profiles/profiles.json`(model=litellm别名/max_turns/instructions);工具统一只读 Read,Glob,Grep,产出经最终消息由 dispatcher 落盘(与 codex read-only 沙箱等价)。
- worker 环境注入:ANTHROPIC_BASE_URL=127.0.0.1:4000 + LITELLM_MASTER_KEY;CLAUDE_CONFIG_DIR=.claude-worker 与主会话隔离;concierge 刻意**不**注入 base_url(走本机 Claude 订阅,预算与 litellm 隔离)。
- claude CLI 在 nvm 路径,systemd/cron 最小 PATH 找不到 → agentlib.claude_bin() 统一解析(2026-07-07 实锤)。
- Stop hook 打回时**必须要求正文+report+envelope 同一条消息重发**:系统只落盘最后一条消息,只补块会丢正文(T-20260707-005 实锤,已修)。
- 收件 chat_id:网关入站捕获写 logs/feishu_notify_chat;首次冷启动可经 im/v1/chats 拉取。
- 验证基线:verify.sh 27/27 全绿;三通路(ds/kimi/qwen)工具循环 0 malformed;retriever/digester 双域 E2E(含 cron 最小环境);卡片发送+PATCH 原地更新实测。

## 风险与遗留

1. **CLIProxyAPI 未登录**:需 HB 手动 `vendor/cliproxyapi/cli-proxy-api --codex-device-login`;登录后 `curl :8317/v1/models` 校准 litellm.yaml 里 gpt-plus 的 model 名(现为占位 gpt-5.5)。在此之前 -hi 档实际由 ds-reasoner 承接(litellm fallback,有出站说明)。
2. **ToS 风险**:CLIProxyAPI 属 OpenAI ToS 灰区,有封号可能;codex CLI 未卸载,作为 GPT 通道逃生舱。
3. **成本水位**:Claude harness 每轮固定开销高于 codex exec(万 token 级);ds 有缓存折扣,qwen-max(auditor)固定开销上涨,月度预算 200 USD 水位周治理盯一周。
4. 旧 T-20260707-005 inbox 正文不全(hook 修复前产物),原文在 traces/retriever/20260707/。
5. feishu_card.py 保留(daily_brief 等仍引用),dispatch 已不再调用;二期统一并入 notifier。
