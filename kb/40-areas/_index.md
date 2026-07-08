---
kind: index
scope: area
tier: canonical
---
# Areas — 无终点的持续职责(周期性监测)

PARA 的 Areas:不属于任何有终点项目的常规性任务流。每个 area 是时间序列(raw/digest 按日期,rollup 按周/月)。

- **xhs-hot/** — 小红书每日热点追踪(AI/非AI两线,近7天发布口径)。采集 bin/xhs_hot.py,日更 bin/xhs_daily.sh(cron 07:00)。
- (arxiv-monitor/ — 论文监测,储备中,bin/arxiv_monitor.py)
- (intel-daily/ — 每日情报,现落 30-projects/default,后续可迁入)
