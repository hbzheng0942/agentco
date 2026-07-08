---
kind: community_raw
platform: reddit
topic: "r/blender 'Serious discussion: Is AI replacing' 高赞回复分析"
fetch_ts: 2026-07-08T15:23:08+00:00
content_hash: 3ef411e45f0d2364
project: default
model: ds-chat
trace: traces/reddit_deep/20260708/r-blender-serious-discussion-is-ai-repla.json
source_urls:
  []
---

# 社区原声:reddit / r/blender 'Serious discussion: Is AI replacing' 高赞回复分析

> reddit-research-mcp 深潜采集(ds-chat 忠实转录,未分析)。**原声在高赞评论里**;digester 蒸馏时逐条痛点回指具体评论(带▲赞数),交叉验证,勿把评论区综合成一句。

我查看了当前所有可用工具，**没有发现 `dialog-mcp` 或任何 Reddit 研究工具**。我的工具集里没有 Reddit API/MCP 服务器可用。

具体来说，我缺少：
- `discover_operations`
- `discover_subreddits`
- `search_subreddit` / `fetch_posts`
- `fetch_comments`

——即整个 Reddit 采集链路所需要的操作入口都不存在。

**你可以做的事：**

1. **告诉我 dialog-mcp 如何连接**——如果它需要在 settings.json 中配置 MCP 服务器，我可以帮你添加配置（比如设置 `reddit_client_id`/`secret` 等凭据），然后用 `WaitForMcpServers` 等它就绪。

2. **改用 WebSearch + WebFetch 手工采集**——用搜索引擎找 Reddit 帖子 URL，然后拿 URL 去 WebFetch 抓内容。但这不是结构化 API 调用，提取评论的精度会差很多。

3. **如果你在别的会话里有这组工具**，把采集结果直接粘贴过来，我来帮你按你要求的格式整理。

你倾向哪种方式？
