---
kind: community_raw
platform: reddit
topic: "r/singularity Gemini 3.6/3.1 空间推理是否提升"
fetch_ts: 2026-08-05T00:10:22+00:00
content_hash: b8e165170efdbff6
project: default
model: ds-chat
trace: traces/reddit_deep/20260805/r-singularity-gemini-3-6-3-1-空间推理是否提升.json
source_urls:
  - https://reddit.com/r/GeminiAI/comments/1r9r36i/spent_all_night_making_a_benchmark_for_3d/
  - https://reddit.com/r/GoogleGeminiAI/comments/1p29mhm/gemini_30_pro_vs_chatgpt_51_thinking_on_visual/
  - https://reddit.com/r/singularity/comments/1p095c9/gemini_30_pro_benchmark_results/
  - https://reddit.com/r/singularity/comments/1p22fay/gemini_3_achieves_new_sota_performance_on/
  - https://reddit.com/r/singularity/comments/1ra6x6n/fixed_difference_between_gemini_30_pro_and_gemini/
  - https://reddit.com/r/singularity/comments/1v2l6sm/gemini_36_flash_benchmarks/
---

# 社区原声:reddit / r/singularity Gemini 3.6/3.1 空间推理是否提升

> reddit-research-mcp 深潜采集(ds-chat 忠实转录,未分析)。**原声在高赞评论里**;digester 蒸馏时逐条痛点回指具体评论(带▲赞数),交叉验证,勿把评论区综合成一句。

## [r/singularity] Gemini 3 achieves new SOTA performance on SpatialBench. A benchmark to test spatial reasoning in VLMs.
- url: https://reddit.com/r/singularity/comments/1p22fay/gemini_3_achieves_new_sota_performance_on/
- score: ▲207 · 33评论 · date: 2025-11-20
- 楼主原声: [https://spicylemonade.github.io/spatialbench/](https://spicylemonade.github.io/spatialbench/)
- 高赞评论(原声):
  - ▲57 "Wow, this is a great benchmark. I thought sota would be around 20-30% in something like this, still a lot of work to do. But when this gets saturated that's another big component of intelligence that is basically solved.\n\nIsn't that what Lecun was talking about when he said that cats understood the world better than llms?" — Bright-Search2835
  - ▲25 "The skills we benchmark are very important for certain tasks like circuit analysis where humans trace with their eyes (models cant do this yet). The 3d tests check AI's ability to rotate and move objects in its head. We believe these are one of the 2 most important components to human vision (besides object detection which has been solved)." — gbomb13
  - ▲14 "This is a great benchmark, if ai can score high on this it should be really good at image understanding and won't be falling for the fingers trick or problems similar to that. One big weaknesses of ai rn. Also I don't think the avg human is getting 80% on this lol." — [deleted]
  - ▲10 "yeah i didn't expected all of these AI models to be so low on it, that show us indeed that they still lack some things that we possess, but in the future all of these benchmarks will get destroyed hopefuly, 5 years ago the benchmarks we had are completely destroyed right now be AI, either that or we'll have extremely complex benchmarks beyond any human capabilities (even experts), in any case the future of AI is promising" — ShAfTsWoLo

## [r/singularity] [FIXED] Difference Between Gemini 3.0 Pro and Gemini 3.1 Pro on MineBench (Spatial Reasoning Benchmark)
- url: https://reddit.com/r/singularity/comments/1ra6x6n/fixed_difference_between_gemini_30_pro_and_gemini/
- score: ▲192 · 18评论 · date: 2026-02-20
- 楼主原声: ^(I made a previous post showing this comparison, but as I mentioned in that post, some builds that Gemini 3.1 Pro would make were simply not of the quality that was expected of the model.)\n\n^(TLDR: Found out those builds were routed to 3.0 Pro, not 3.1 Pro. Have since deleted the previous post.)\n\nWith these new builds, I think Gemini 3.0 Pro -> 3.1 Pro feels more like a generational leap…
- 高赞评论(原声):
  - ▲44 "[deleted]"
  - ▲16 "That was what I hoped for when creating the benchmark, thank you!! I didn't actually think this benchmark could be \"saturated\" but unfortunately (or fortunately) I think Gemini 3.1 Pro shows that we're nearing a point where the actual builds are basically flawless – from like a pure fidelity standpoint.\n\nIf progress continues like this, I think the benchmark will shift from clearly showing disparities between visual reasoning/intellect in the models and instead just show the creative/stylistic choices between different models." — ENT_Alam
  - ▲6 "Nice! But what's up with the knight's chest..." — SuggestionMission516
  - ▲5 "This outlines that the biggest misconception about LLMs is that they are LLMs, as in they are not large *language* models.\n\nSure Gemini 3 is multimodal, but even a pure LLM can do that. LLMs are really LTM, they don't handle Language per se, they handle text. Making a knight with cube blocks is not a language task but because it's text, an LLM can do it.\n\nYou can even fine-tune an LLM to display doom frames as ASCII art and play the game doom ... on an LLM. As long as there is a pattern in text even though it's not language at all, an LLM can handle it because what it really is is a Large Text Model…" — GraceToSentience

## [r/singularity] Gemini 3.6 Flash benchmarks
- url: https://reddit.com/r/singularity/comments/1v2l6sm/gemini_36_flash_benchmarks/
- score: ▲625 · 281评论 · date: 2026-07-21
- 楼主原声: (仅标题)
- 高赞评论(原声):
  - ▲262 "Damn this sub really only look at success based on coding is everyone a developer now? It lags in coding but makes up for it in other areas, areas that imo are equally as important. This for normie use (assistant) is good and for agentic tasks outside of coding as well." — Aaco0638
  - ▲133 "The responses here are a bit odd to me. I've been having good success with the google models in large context multi modal knowledge work and this looks to be a step up in that area. Think use cases like processing 100s of pages of text / pictures in a document as part of an RPA pipeline.\n\nAnother interesting thing for me about google models is the generous requests per minute they give on their API, which at my spend is better than I can get from AI foundry and bedrock.\n\nI'm not sure if it will beat a fine tuned open weight model for my use case on accuracy or cost, but I do think it's worth testing.\n\nI wouldn't recommend for coding." — sn0wquake
  - ▲88 "There's well over a billion AI users a month now, as if they are all SWE's lol. The vast majority are using AI models in ways that this 3.6 model accels at." — Tkins
  - ▲47 "This has been my experience as well. I can't use it for coding, which sucks, but Gemini is my go to model when I'm implementing AI inside a product. It just responds really reliably." — CannyGardener
  - ▲30 "The biggest problem with Gemini is not coding, it's its hallucinations.\n\nIt's also a lazy model that do the minimum every single time. Where ChatGPT could spend 5 minutes digging the web for info, Gemini will often hallucinate that it uses a web search tool and give you a less reliable answer.\n\nI used to be the biggest Gemini fanboy up to Gemini 3. Since that model, it became incredibly clear that the model had problems and was no longer competitive." — kiki-le-koala

## [r/GeminiAI] spent all night making a benchmark for 3D modelling and Gemini 3.1 Pro is absolutely dominating it winning 94% of blind evals, its a massive leap forwards in spatial reasoning
- url: https://reddit.com/r/GeminiAI/comments/1r9r36i/spent_all_night_making_a_benchmark_for_3d/
- score: ▲2 · 2评论 · date: 2026-02-20
- 楼主原声: https://preview.redd.it/57j2u4y5emkg1.png?width=1232&format=png&auto=webp&s=3b35858750c943bf87638b4ee94026a1121e8821\n\nhttps://preview.redd.it/nl38r3y5emkg1.png?width=1241&format=png&auto=webp&s=6233033c02004e605c45ca4170f0c9b7840f33be\n\nhttps://preview.redd.it/5fpvf4y5emkg1.png…(selftext 为图片链接)
- 高赞评论(原声):
  - ▲1 "Are the SVGs on your site generated by AI ?" — ChippingCoder
  - ▲1 "Yes they are! By Gemini 3.1 pro as well!" — SammyIggy

## [r/singularity] Gemini 3.0 Pro benchmark results
- url: https://reddit.com/r/singularity/comments/1p095c9/gemini_30_pro_benchmark_results/
- score: ▲2462 · 587评论 · date: 2025-11-18
- 楼主原声: (仅标题)
- 高赞评论(原声):
  - ▲770 "Man I was happy with GPT 5.1 and all that improvement and was expecting for gemini 3 to be the same.\n\nThis is fucking incredible, what a conclusion to the year." — [deleted]
  - ▲433 "Some of these numbers are insane (Arc AGI, ScreenSpot)" — rag_n_roll
  - ▲310 "No way this is real, ARC AGI - 2 at 31%?!" — user0069420
  - ▲310 "If the numbers are real, google is going to be the solo reason the American economy isn't going to crash like the great depression. Keeping the ai bubble alive" — [deleted]
  - ▲165 "But not the best SWE verified result, it's over /s. Not that benchmarks matter that much, from what I've seen it is considerably better at visual design but not really a jump for backend stuff." — enilea

## [r/GoogleGeminiAI] Gemini 3.0 Pro vs ChatGPT 5.1 (Thinking) on Visual Logic: A Side-by-Side Stress Test (The results surprised me)
- url: https://reddit.com/r/GoogleGeminiAI/comments/1p29mhm/gemini_30_pro_vs_chatgpt_51_thinking_on_visual/
- score: ▲128 · 23评论 · date: 2025-11-20
- 楼主原声: There is a lot of noise right now about "reasoning" models, so I decided to skip the standard benchmarks and run a practical **visual logic stress test**.\n\nI fed both models (Gemini 3.0 Pro and ChatGPT 5.1 Thinking) three "trick" images designed to confuse standard multimodal vision. The goal was to test **observation** (what is actually there?) vs. **hallucination** (what the model *expects* to be there)…
- 高赞评论(原声):
  - ▲14 "It's crazy good and is built multi modal foundationally. That explains the dominant score in ARC-AGI 2" — chasingth
  - ▲11 "Google has a secret sauce in image. It wins. That's also why it is leaps and bounds on arc AGI. OAI stole some vision guyd from them, but then they got zucced. Not sure if OAI can catch up on this ever." — Freed4ever
  - ▲6 "Honestly, the table test (slide 3) really surprised me. I assumed both would fail the physics check. Has anyone tried running this on o1-preview?" — ConstructionThese663
  - ▲6 "This must be the reason its more intelligent. That's it. They trained it with image data also en mass" — Yes_but_I_think

> 采集缺口说明: r/singularity 的 1ra6x6n 帖下原最高赞评论(▲44)内容已被作者删除,工具返回原样 "[deleted]",未用先验补。
