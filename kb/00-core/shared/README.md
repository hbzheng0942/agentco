---
scope: core
tier: canonical
---

# 共享组件(结构预留,按需生长)

每个共享组件一个目录:`kb/00-core/shared/<comp>/`,含:
- `spec.md` — 组件规格。其中 `## API契约` 段是传播判定的锚点。
- `dependents.md` — 依赖本组件的项目清单(每行一个项目名,如 `assembly`)。

## 传播判定(bin/shared_watch.py)
- `## API契约` 段 hash 变化 = **breaking** → 实时给每个 dependent 项目生成 review 任务(auditor,高优先级)。
- spec 其他部分变化(API契约段不变) = **non-breaking** → 仅记 event,攒入每日简报。

> 尚无共享组件时本目录仅有此 README;第一个组件落地时按上述结构新建。
