---
kind: community_raw
platform: reddit
topic: "世界模型融资泡沫(真预训练仅3-5家)从业者验证与争议"
fetch_ts: 2026-08-09T00:14:21+00:00
content_hash: a5f4b9a7630c1208
project: default
model: ds-chat
trace: traces/reddit_deep/20260809/世界模型融资泡沫-真预训练仅3-5家-从业者验证与争议.json
source_urls:
  - https://reddit.com/r/MachineLearning/comments/1swa26o/why_do_only_big_ml_labs_dominate_widelyused/
  - https://reddit.com/r/MachineLearning/comments/1ttei2r/whats_the_actual_focus_in_world_models_right_now_r/
  - https://reddit.com/r/MachineLearning/comments/1uxcryc/looking_for_jepa_devil_advocates_r/
  - https://reddit.com/r/MachineLearning/comments/1v1i26p/i_just_read_lecuns_recent_thoughts_on_world/
  - https://reddit.com/r/aiwars/comments/1qsaim7/genie_3_the_socalled_world_model_based_on_video/
  - https://reddit.com/r/aiwars/comments/1qtix8s/games_industry_stocks_crash_as_investors_panic/
  - https://www.reddit.com/r/MachineLearning/comments/1uxcryc/looking_for_jepa_devil_advocates_r/
---

# 社区原声:reddit / 世界模型融资泡沫(真预训练仅3-5家)从业者验证与争议

> reddit-research-mcp 深潜采集(ds-chat 忠实转录,未分析)。**原声在高赞评论里**;digester 蒸馏时逐条痛点回指具体评论(带▲赞数),交叉验证,勿把评论区综合成一句。

## [r/MachineLearning] I just read LeCun's recent thoughts on world models. Thoughts on JEPA as a path forward? [D]
- url: https://reddit.com/r/MachineLearning/comments/1v1i26p/i_just_read_lecuns_recent_thoughts_on_world/
- score: ▲88 · 60评论 · date: 2026-07-20
- 楼主原声: So, I just read LeCun's interview with Nebius Science. I feel he had some cool points about LLMs being able to answer things, but not literally understand the physics of the physical world. (Like, being able to explain a task and actually performing it are two completely different things.) But I wanted to get opinions on what others thought of his solution to the problem. He thinks JEPA could be the solution. But it made me think about whether JEPA is genuinely the architectural solution to this, or if we're just looking for a "magic bullet" that doesn't exist yet in our toolbox
- 高赞评论(原声):
  - ▲192 "Well, If I developed/developing a new technology, I would definitely say that the technology that Im currently developing is the solution for a actual limitation of todays problem too."
  - ▲51 "As always in ML, ideas are cheap, implementation matters."
  - ▲35 "JEPA is less principled than generative approaches IMO. We discussed JEPA in this thread https://www.reddit.com/r/MachineLearning/comments/1uxcryc/looking_for_jepa_devil_advocates_r/ I don't see any way in which JEPA would be a better fit for world models."
  - ▲33 "Well, he's put some great research forward. Undeniable. Hell, the solution of a problem I'm having right now came directly of a paper he put together recently. So, I have to refrain myself from bashing him too much. Having said that, I think he's drinking way too much of his own kool-aid. "World Models" by JEPA architecture which honestly largely relies on: Latent structure, autoregressive modeling and Contrastive Learning? Come on... The only reason why I think this flies with ML research is because hypothesis testing is almost inexistent in the field."

## [r/MachineLearning] Looking for JEPA devil advocates [R]
- url: https://reddit.com/r/MachineLearning/comments/1uxcryc/looking_for_jepa_devil_advocates_r/
- score: ▲112 · 93评论 · date: 2026-07-15
- 楼主原声: I am currently doing research on world models, specially in tje field of robot learning, and, as probably most of you alredy know, JEPA-like models are mentioned over and over. I read the main recent papers from lecun as well as other research groups, and I personally think the whole approach is very promising and can really go somewhere. But after listening a bunch of the recent Y Lecun conferences his ideas looks even too cool compared to "literally everything else" (as he's dissing LLM, RL, etc and pitching his ideas are the "only next big things"...). So I am asking myself if there are red flags about his approaches that I do not see yet...
- 高赞评论(原声):
  - ▲83 "My pet peeve with JEPA is that there is an emphasis on the abstraction at the same time as they want to compete with general models. Predicting abstract representations is more efficient. However, the abstraction necessary is completely dependent on your target task. You might predict a car driving path great but when you try to predict detailed information you fail. LLMs are kind of able to L2-smear out everything into something that makes sense regardless of the task. In my head the solution to this are hierarchical abstractions, but this is not something that is JEPA-specific and its really unclear how to train such networks. Also, JEPA does nothing to address fat-tailed distributions..."
  - ▲80 "Dissing LLMs and RL is more political than anything for Yann. You just have to follow him on Twitter/Threads to realize his dislike for LLMs is less about the technical capabilities of those models and more about how they've completely overtaken a massive swathe of research and funding and basically collapsed most of the field into one technique and one paradigm, meaning other promising avenues that might be miles better than LLMs simply don't get explored enough because everyone wants to fund/work on LLMs only. I wouldn't take it as a reason to avoid JEPA thinking Yann's just trying to hype up an obsolete idea or something."
  - ▲22 "The issue I have with JEPA is that it is less principled than generative models. By that I mean that JEPA produces a representation, but the information the representation contains is basically "up to chance". There is no mechanism that forces the representation to keep useful information, beside the inductive biases from the neural architecture itself and the choice of data augmentation transforms..."
  - ▲13 "JEPA assumes that learning happens from observation which is fundamentally untrue. learning happens from play and interaction. It's been mathematically proven that causal attribution cannot be concluded from observation alone. That assumption is fatal, as modeling the world requires relationships between things more than a frequentist perspective. What is a spoon? It's a form, a function, its material, its relations with its surroundings. To really understand the world, the agent must perturb, observe, deduce..."

## [r/MachineLearning] What's the actual focus in World Models right now? [R]
- url: https://reddit.com/r/MachineLearning/comments/1ttei2r/whats_the_actual_focus_in_world_models_right_now_r/
- score: ▲80 · 28评论 · date: 2026-05-31
- 楼主原声: Hey everyone, I'm trying to get back into the loop on world models. The last time I followed SSL closely, the buzz was all about Barlow Twins and DINO, but now everything just looks like scaled-up video generation from big industry labs. What is the actual academic research community stressing over right now?
- 高赞评论(原声):
  - ▲41 "Maybe reconstruction-free/JEPA"
  - ▲26 "It looks like scaled-up video generation, because video generation is part of it, and the most visible parts of the training. "World model" is it kind of an overloaded term because is see people referring to work models as both the generative models that create coherent 4D worlds and the things inside of them, and I see people referring to world models as the AI models that interact with the 4D worlds. The videos aren't just regular videos, they're closer to simulations..."
  - ▲14 "World models are more about teaching neural networks the physics of the real world, and semantics from next-frame predictions in a video, and then using them to act and plan. The idea comes from predictive decoding and internal world models from computational neuroscience. People would like to do this in a self-supervised manner, as there are millions of hours of video available on the internet for free use. Pixel reconstruction is really hard for learning useful representations from videos, so people are turning to latent-space reconstruction methods. Yann Le Cun is now pushing JEPA architectures, and they have a new paper showing a teacher/EMA-free method that scales well (LeJEPA)..."

## [r/MachineLearning] Why do only big ML labs dominate widely-used models despite many open-source pretrained models smaller labs could do RL on? [D]
- url: https://reddit.com/r/MachineLearning/comments/1swa26o/why_do_only_big_ml_labs_dominate_widelyused/
- score: ▲62 · 29评论 · date: 2026-04-25
- 楼主原声: I'm trying to understand why models from major labs (GPT, Claude, etc.) dominate real-world usage? You might say it's due to the expensive pretraining compute budge, but there already exists many pretrained open-source models at the same scale (e.g., Kimi). Of course Kimi isn't as good as Claude, but it's the RL on top of the pretraining that makes Claude what it is right? Given Kimi, DeepSeek etc all have the expensive pretraining done, the RLHF on top is what makes Claude what it is right? And that should be much more accessible in terms of cost to smaller labs no?
- 高赞评论(原声):
  - ▲63 "[deleted]"
  - ▲43 "the rlhf framing misses the main thing. alignment quality compounds with usage data. you need millions of real-world interactions to learn what matters for actual users vs what you capture in synthetic preferences or curated datasets. deepseek and kimi have the compute and pretraining budget, but they do not have the implicit feedback loop from deploying at openai/anthropic scale. it is less "rlhf is magic" and more "the production feedback loop is the moat". that is why labs iterating on real deployment failures can move faster on the hard alignment cases even when the base models are comparable."
  - ▲39 "At the risk of sounding pedantic, RLHF isn't really the RL post-training step that's making Claude and GPT better than Kimi, Qwen, etc, anymore. It's the RLVR, which admittedly they do all use at this point I think (including OSMs), but I'm guessing the major US labs just keep finding new ways to improve the reward signal for things like prompt adherence because they have the compute budget to do so. And the OSM labs (likely) figured out they can generally keep up by generating new, higher quality post-training datasets from every new wave of proprietary models and doing SFT on that instead, which is much cheaper, and then focus their research efforts into less computationally intensive breakthroughs (like quant aware training)."
  - ▲20 "The model has to fit the VRAM. RL is still training and at frontier scale its expensive as hell, $2.68/hr+ for one h100, plus testing if it works then "oh shoot its still not able to understand some special token" or some other weird edge case from the run that changed something. And RLHF you need the actor model, the reference model, the reward model, the critic model ALL loaded and its prone to reward hacking. Truly its a nightmare..."

## [r/aiwars] Genie 3 (the so-called world model based on video gen by Google) basically shows that it is interesting, but pointless.
- url: https://reddit.com/r/aiwars/comments/1qsaim7/genie_3_the_socalled_world_model_based_on_video/
- score: ▲2 · 136评论 · date: 2026-01-31
- 楼主原声: Source: https://x.com/fofrAI/status/2017543881735172525 As a game, it's clearly useless because where is the actual gameplay? What's the goal? None of that. As a world model, the physics are so-so. It looks interesting, and it's basically fun to play as a 3D map you explore, but that's about it. It costs $250 a month. If this was all advertised as just 3D map research, it would be cool in principle. Unfortunately, it's being pushed as a world model, New Era Of Game Industry.
- 高赞评论(原声):
  - ▲46 ""Ai will never be able to accurately generate hands.""
  - ▲42 "This tech is incredible and if you fail to see how this can be used, you already had zero creativity to begin with."
  - ▲15 "You're kidding? For 3D games, models, lighting and physics is like 80% of work. It would take much more time and money to make something like this manually. Many independent developers struggle with 3D assets, modelling is very labour-intensive and arguably harder than programming."
  - ▲10 ">It's literally just a video All games are just videos if you want to be that reductionist. When playing a game, the end result of all the graphical computations your PC makes results in... images, in sequence, being presented on a screen. A video."

## [r/aiwars] Games Industry Stocks Crash As Investors Panic Over Google's Genie 3 World Model AI...
- url: https://reddit.com/r/aiwars/comments/1qtix8s/games_industry_stocks_crash_as_investors_panic/
- score: ▲5 · 4评论 · date: 2026-02-01
- 楼主原声: (仅标题)
- 高赞评论(原声):
  - ▲1 "Shouldn't the prospects of an entirely new medium for game development cause the game industry to skyrocket?"
  - ▲1 "No because the "industry" being referred to are the current powerhouse studios and publishers. If a tool makes it much easier for indie teams and individuals to produce quality games, those giants will lose money. The biggest companies have already been struggling because they've doubled down on greedy microtransaction schemes and making stupid ass games with political propaganda in them."

---

> 采集缺口:r/venturecapital 对 "World Labs" / "world model" 均返回空;`fetch_posts` 未使用(搜索已覆盖所需)。话题词两轮 discover_subreddits 全部为 peripheral 层级,无 core 层级子版可用。
