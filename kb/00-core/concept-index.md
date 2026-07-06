# 全局概念索引(single source of truth)

> **查表顺序**:本表(全局)→ 各项目 `kb/30-projects/<proj>/_index.md`,**查到即停,全局优先**。
> 通用概念入本表;项目特有概念入项目 `_index.md`。
> **产出前强制**:产出新概念前必查此表。已有→更新其"权威文件"禁止另建重复;
> 新概念→追加一行并声明相邻概念(scope=global 入本表,scope=proj 入对应项目表)。

格式:`概念 | 权威文件路径 | scope | 相邻概念`

| 概念 | 权威文件路径 | scope | 相邻概念 |
|------|-------------|-------|---------|
| envelope(产出溯源信封) | kb/00-core/constitution.md#envelope | global | content_hash, source_urls, depends_on |
| content_hash(结果集哈希) | bin/search.py, kb/00-core/constitution.md#envelope | global | envelope, source_urls |
| source_urls(来源链) | bin/search.py | global | content_hash, raw |
| 工具域(域=工具边界) | kb/00-core/constitution.md#工具域切分 | global | worker, profile |
| worker(=profile 变体) | config/codex-profiles/ | global | 工具域, tier |
| tier(0廉价/1升级) | bin/dispatch.py | global | worker, escalate |
| 依赖边(depends_on) | bin/dispatch.py | global | dep_triggered, dep_failed, waiting_dep |
| skill 心跳(use_count) | kb/00-core/constitution.md#skill心跳 | global | skill_hit |
| 搜索层(dispatcher 非模型工具) | bin/search.py | global | raw, retriever |
| raw(搜索原料) | kb/30-projects/*/raw/ | global | source_urls, retriever, cache_gc |
| 三审分离 | kb/00-core/roles.md | global | Strategist, Architect, Auditor |
| 共享组件传播 | kb/00-core/shared/ | global | breaking, dependents |
| events 不可变 | config/schema.sql | global | 审计流 |
