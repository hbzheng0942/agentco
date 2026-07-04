# AGENTCO 安装手册(Wave ①)— 供 Codex 执行

> 规则:**只做安装动作,不得重写本包内任何文件的逻辑**。环境不符处(模型ID、config字段名、路径)做最小修改,逐条记入 INSTALL_LOG.md。

## 步骤(按序,每步过了再走下一步)

1. **前置**:python3≥3.10 / sqlite3 / git / codex CLI 就绪;`codex --version` 记入日志。包解压路径即部署根(示例 /opt/agentco;crontab.txt 内路径按实际改)。
2. **密钥**:`cp .env.example .env` → 提示用户填 DEEPSEEK_API_KEY / MOONSHOT_API_KEY / LITELLM_MASTER_KEY(自生成随机串)/ FEISHU_WEBHOOK(+可选FEISHU_SECRET);`chmod 600 .env`。
3. **校准模型ID**:调厂商 /models 端点,更新 config/litellm.yaml 中标注 TODO 的 model 字段;记录改动。
4. **执行 `bash install.sh`**(幂等:依赖、state.db、config.toml标记块合并、agent软链、litellm systemd、git init)。
5. **校准 codex 字段**:若 ~/.codex/config.toml 合并块中 model_providers/profiles/tools.web_search 字段与当前 codex 版本 schema 不符,按官方文档等价改写;**owl-intel 必须具备联网检索能力**(web_search 工具或搜索MCP,二选一),记录方案。
6. **验收 `bash bin/verify.sh`**:全绿后,手动执行脚本内提示的两项探针(沙箱cwd确认、20轮tool-call压测,malformed率>2%即停止上报)。
7. **cron**:`crontab -e` 粘贴 crontab.txt(路径改为实际部署根)。
8. **网关暴露**(验收按钮+入站信箱必需):安装 cloudflared,建 Tunnel 指向 `http://127.0.0.1:9000`;把 Tunnel 域名填入 .env 的 PUBLIC_BASE_URL;`systemctl restart agentco-gateway`;`curl <PUBLIC_BASE_URL>/health` 通过。
9. **飞书应用(入站信箱,可选)**:企业自建应用 → 事件订阅 URL 填 `<PUBLIC_BASE_URL>/feishu`(明文模式,**不配** Encrypt Key,Verification Token 填入 .env)→ 订阅 im.message.receive_v1 → 权限仅 im:message 单聊。
10. **首跑闭环**:`bash bin/intel_daily.sh` → kb/90-inbox/ 出现信号卡、飞书收到推送;`echo 测试 | python3 bin/enqueue.py exec-ds 卡片测试` 跑完后手机应收到带三按钮的验收卡片,点"采纳"应见 ✅。
11. 提示用户配置私有 git remote → `git push -u origin main`。

## 日常使用(装完告知用户)
- 手机派任务:飞书发 `派 owl-intel 调研xxx`;任意其他消息 → 自动进 90-inbox 异步信箱
- 验收:手机点卡片按钮(采纳/返工/废弃);或服务器 `python3 bin/review.py [T-xxx adopt|rework|reject 备注]`
- 周治理:周日 20:00 自动跑(异模型审计+watchlist进化+inbox策展),周一早 15 分钟裁决报告中的 diff,采纳即应用并 git commit
- 看板:`sqlite3 state.db "SELECT id,agent,status,title FROM tasks ORDER BY created_at DESC LIMIT 10"`

## 硬边界
- 不改 bin/*.py 逻辑(路径/常量除外);不提权沙箱;主会话永不 --yolo;不装本手册外的服务。
