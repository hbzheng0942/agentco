---
kind: governance
tier: canonical
topics: [知识治理, 文件生命周期, 存储规则]
updated: 2026-07-08
---
# AGENTCO 知识库治理规则(scope × tier × kind × 图谱底座)

> 目的:解决"过程文件一股脑塞进 kb/飞书"导致的长期维护困难,并为未来
> **cross-topic 知识图谱 + 启发性思考**铺底座。核心方法:每个文件按
> **归属(scope)× 生命周期(tier)× 类型(kind)** 三轴治理。
> scope 回答"归谁"、tier 回答"留多久/上不上飞书"、kind 回答"是什么"。

## 零、归属(scope)—— 借鉴 PARA + Johnny.Decimal

现状痛点:不是所有文件都挂项目下——**周期性监测(每日情报/小红书热点/论文监测)是
"无终点的持续职责",不属于任何有终点的项目**。用 PKM 事实标准 PARA 解决:

| scope | 含义 | 目录(延续现有 Johnny.Decimal 数字前缀) | 例子 |
|-------|------|------|------|
| **core** | 治理/原则/角色(元) | `kb/00-core/` | constitution、本规则、concept-index |
| **resource** | 按主题的参考知识 | `kb/10-domain/` | 领域知识沉淀 |
| **area** ⭐ | **无终点的持续职责(周期性任务)** | `kb/40-areas/<area>/` | xhs-hot、arxiv-monitor、intel-daily |
| **project** | 有终点的目标 | `kb/30-projects/<proj>/` | assembly、video-shorts |
| **archive** | 归档(完结项目/过期料) | `kb/99-archive/` | 完结项目整体移入 |
| (inbox) | 分诊着陆区,非归属 | `kb/90-inbox/` | 待落位 |

- **周期性监测归 area**,且是**时间序列**:`kb/40-areas/xhs-hot/{raw,digest}/YYYY-MM-DD.md`,
  支持周/月 rollup 综述(`kb/40-areas/xhs-hot/rollup/2026-W28.md`),旧日报按 tier=ephemeral/working GC。
- 项目完结 → 整个 `30-projects/<proj>/` 移入 `99-archive/`,不留在活跃区干扰。

## 一、生命周期(tier)——决定留存与去向
每个文件按 **类型(kind)× 生命周期分级(tier)** 治理,tier 决定存哪、留多久、是否上飞书。

## 一、三级生命周期(tier)——决定留存与去向

| tier | 含义 | 判据 | 留存 | 飞书镜像 |
|------|------|------|------|----------|
| **ephemeral** | 采集原料,可再生 | 只要蒸馏产物在,原料可丢 | GC 保留 21 天,过期删(留 manifest 溯源) | ❌ 不镜像(高量低值) |
| **working** | 蒸馏/加工产物,策展中 | 被人读、会被上层引用 | 留到被取代/月度 rollup | ✅ 镜像到项目蒸馏区 |
| **canonical** | 决策/知识/永久资产 | 结论性、需长期回指 | 永久(git 版本化) | ✅ 镜像到项目决策/知识区 |

## 二、类型(kind)→ tier → 存储位置 权威表

| kind | tier | 服务器位置 | 飞书 |
|------|------|-----------|------|
| `search_raw` / `community_raw` / `paper_raw` | ephemeral | `kb/30-projects/<proj>/raw/` | ❌ |
| `digest`(蒸馏产物/信号卡) | working | `kb/30-projects/<proj>/digest/` | ✅ 蒸馏区 |
| `research_report`(深研报告) | working→canonical | `kb/30-projects/<proj>/digest/`(重要的晋级 decisions/) | ✅ |
| `paper_digest`(论文日报) | working | `kb/30-projects/<proj>/digest/` | ✅ |
| `decision` / `battle`(决策/取舍) | canonical | `kb/30-projects/<proj>/decisions/` | ✅ 决策区 |
| `spec` / `prd`(任务书/PRD) | canonical | `kb/30-projects/<proj>/specs/` | ✅ |
| `retro`(复盘) | canonical | `kb/30-projects/<proj>/retro/` | ✅ |
| `domain`(领域知识) | canonical | `kb/10-domain/` | ✅ 知识区 |
| `intel`(情报存档) | working | `kb/20-intel/` | 视重要性 |
| `concept`(概念权威定义) | canonical | 登记入 `kb/00-core/concept-index.md` | — |
| `governance` / `principle`(治理/原则) | canonical | `kb/00-core/` | — |
| 任务 spec+result | 操作态 | `handoff/<proj>/` | 结果视 notify |

## 三、inbox 是分诊区,不是仓库

`kb/90-inbox/` 只是**着陆区**:worker 产出先落这里,由 `inbox_digest`(日更 cron)分诊——
每条 → 判定 kind/tier → 移入上表的归属位置 + 打 topics 标签。**inbox 里不该有超过 N 天未分诊的存量**;
未分诊超期由 warden 巡检告警。idea-* 类灵感同理:分诊到项目或 10-domain,不长期躺 inbox。

## 三点五、发布日期 item 级强制(所有采集器)

**教训(2026-07-08 小红书热点 bug)**:按存量热度排序会把两个半月前的老帖当"热点"。
根因是没存发布日期。**铁律:任何采集器抓的每个条目必须带 `发布日期/date`**(文件级 frontmatter
不够,要 item 级)。热度/趋势类任务须按**发布时间窗过滤 + 时间速度(赞/发布天数)**排序,
禁止用绝对存量排序冒充新增趋势。
- 各源日期来源:search.py=page_age/date;x=推文time;reddit=created_utc;arxiv=published;
  xhs=get_feed_detail 的 note.time(⚠️search 不返回,只 detail 有,故须逐笔 detail 才拿得到)。

## 四、图谱底座:frontmatter 元数据标准(working/canonical 强制)

为支撑未来 cross-topic 图谱与启发性检索,每个 working/canonical 文件 frontmatter 须带:
```yaml
kind: <见上表>
tier: ephemeral|working|canonical
project: <proj 或 global>
topics: [主题标签, ...]        # 图谱的节点归属;从 concept-index 取词,新词登记
entities: [具体实体, ...]       # 公司/产品/论文/人 等可连边的实体(可选)
links: [[其它文件name]]         # 跨文件引用=图谱的边;链相关决策/digest/concept
updated: YYYY-MM-DD
```
- `topics`/`entities` 让"跨主题"可聚合(同一 topic 的 digest 跨项目串联)。
- `links` 是显式边;`concept-index.md` 是主题词的权威登记表(节点字典)。
- 未来图谱构建器(`bin/kb_graph.py`,待建)只读这些字段生成 节点/边,做 cross-topic 归纳与启发。

## 五、飞书结构化镜像(替代当前单一 flat 文件夹)

现状:所有产物塞进一个 `FEISHU_ARCHIVE_FOLDER_TOKEN`。改为按 **项目 / 分级区** 建子文件夹:
```
/AGENTCO
  /<project>
    /蒸馏(working:digest/report)
    /决策(canonical:decision/prd/retro)
  /知识库(10-domain)
```
- 只镜像 working/canonical;ephemeral 原料**只在服务器**(飞书不堆原料)。
- feishu_archive 按文件 frontmatter 的 project/tier 路由到对应子文件夹(缺失则落 /_未分类 待人工归位)。

## 六、强制机制(谁来执行)

| 机制 | 载体 | 频率 |
|------|------|------|
| ephemeral 原料 GC(过期删+manifest 溯源) | `bin/kb_gc.py` | 日更 cron |
| inbox 分诊(落位+打标签) | `bin/inbox_digest.py`(扩展) | 日更 cron |
| 飞书结构化路由 | `bin/feishu_archive.py`(扩展:按 tier/project 选子文件夹) | 产出时 |
| 落位/frontmatter 合规巡检 | warden checklist 增维度 | 周巡检 |
| 图谱构建 | `bin/kb_graph.py`(待建) | 按需/周 |

## 七、原则

1. **原料可丢,结论永存**:ephemeral 只是达到 digest 的中间态,靠 content_hash 溯源,不永久占地。
2. **一处权威**:同一概念/决策只有一个 canonical 文件(concept-index 去重),其余用 `links` 指向,不复制。
3. **落位即分类**:文件产出时就带对 tier/kind/project/topics,不靠事后清理;dispatcher/采集器落盘时写全 frontmatter。
4. **飞书是镜像不是主库**:主库在服务器 git;飞书只镜像 working/canonical 供人读,可重建。
