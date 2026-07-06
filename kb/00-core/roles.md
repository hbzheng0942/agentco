# 判断层角色澄清(仅文档,不进 codex 队列)

> 本文件界定 CC(判断层)与 codex worker(执行层)的分工,以及三审分离。
> **PRD / battle 只留在 CC 会话 + KB,仅可执行 spec 才入 codex 队列**(见 §9.3)。

## 三审分离(不同时点、不同 stance、不同产物)

| 审 | 谁 | stance | 时点 | 产物 |
|----|----|--------|------|------|
| **红蓝队** | Strategist(CC 双 stance) | 双立场对抗,审**方向** | 立项**前** | battle 记录 → PRD 取舍。信息不对称是方法,非人设扮演。 |
| **Review** | Architect(CC) | 审**交付** | build **后** | 交付验收意见(采纳/返工/废弃) |
| **Auditor** | auditor 域(codex,异厂商) | 审**系统** | cron(周) | 治理候选包 → inbox,HB 裁决 |

三者不可互相代替:方向没审清不进 build;交付没 review 不算完;系统不定期 audit 会漂移。

## CC 档位(判断层用哪个模型)

- **Architect**:日常 Sonnet;重决策手动切 Opus。审交付、拆 spec、写 PRD。
- **Strategist battle**:Sonnet 跑量(多轮对抗产生信息量)+ Opus 裁决轮(收敛结论)。
  - **battle ≤ 5 轮硬上限**,超轮即强制收敛,避免空转。
- **Fable 排除**:API-only,不用于判断层交互会话。

## 分工边界(§9.3)

- 判断/探索(PRD、红蓝队 battle、方向取舍)→ 留 **CC 会话 + KB**,不入队。
- 可执行、可验收的 **spec** → 才写入 codex 队列(handoff/<project>/)。
- 三入口按认知模式:判断→CC;执行→飞书或 codex;探索→codex 桌面。

## Warden 会话

系统级巡检由 CC 开 **Warden 会话**,喂入 `kb/00-core/warden-checklist.md`(4 维)。
Warden 不是 codex worker,是 CC 的一个巡检 stance。
