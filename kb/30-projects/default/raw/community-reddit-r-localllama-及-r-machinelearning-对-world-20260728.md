---
kind: community_raw
platform: reddit
topic: "r/LocalLLaMA 及 r/MachineLearning 对 World Labs 空间智能的技术评价"
fetch_ts: 2026-07-28T00:03:46+00:00
content_hash: 7a3aa335fab732fd
project: default
model: ds-chat
trace: traces/reddit_deep/20260728/r-localllama-及-r-machinelearning-对-world.json
source_urls:
  - https://reddit.com/r/LocalLLaMA/comments/1poy0lb/apple_introduces_sharp_a_model_that_generates_a/
  - https://reddit.com/r/LocalLLaMA/comments/1qjjrmq/fei_fei_li_dropped_a_nonjepa_world_model_and_the/
  - https://reddit.com/r/MachineLearning/comments/1i74pni/d_a_little_late_but_interesting_talk_by_feifei_li/
  - https://reddit.com/r/MachineLearning/comments/1tgn3bz/subjepa_a_simple_fix_to_lecun_groups_leworldmodel/
  - https://reddit.com/r/MachineLearning/comments/1ttei2r/whats_the_actual_focus_in_world_models_right_now_r/
  - https://reddit.com/r/MachineLearning/comments/1v1i26p/i_just_read_lecuns_recent_thoughts_on_world/
---

# 社区原声:reddit / r/LocalLLaMA 及 r/MachineLearning 对 World Labs 空间智能的技术评价

> reddit-research-mcp 深潜采集(ds-chat 忠实转录,未分析)。**原声在高赞评论里**;digester 蒸馏时逐条痛点回指具体评论(带▲赞数),交叉验证,勿把评论区综合成一句。

## [r/LocalLLaMA] Fei Fei Li dropped a non-JEPA world model, and the spatial intelligence is insane

- url: https://reddit.com/r/LocalLLaMA/comments/1qjjrmq/fei_fei_li_dropped_a_nonjepa_world_model_and_the/
- score: ▲195 · 88评论 · date: 2026-01-22

- 楼主原声: Fei-Fei Li, the "godmother of modern AI" and a pioneer in computer vision, founded World Labs a few years ago with a small team and $230 million in funding. Last month, they launched https://marble.worldlabs.ai/, a generative world model that's not JEPA, but instead built on Neural Radiance Fields (NeRF) and Gaussian splatting. It's insanely fast for what it does, generating explorable 3D worlds in minutes...

- 高赞评论(原声):
  - ▲88 "Not open source. Not interested."
  - ▲76 "230 millions of funding and 3d scene generator based on image generation and splats? This is not a world model."
  - ▲48 (reply) "I think you're really overselling this. There's no geometric intelligence here."
  - ▲37 "It would have been great if you actually looked around in the final generation"
  - ▲25 "Honestly, meh considering all the money and hype of her startup."
  - ▲15 ""Godmother of AI" 🙄"
  - ▲12 (reply) "2023 paper: https://arxiv.org/abs/2305.11588 \n\nThis isn't that revolutionary. Genie by Google is much more revolutionary."
  - ▲11 "this isn't what people mean by 'world model'. A world model understands physics (how matter interacts, how fluids work, how light works, how gravity works, etc). It understands cause and consequence. There is none of that in this."
  - ▲8 "Can someone please explain the attraction of this in its current state? To me the 'worlds' look super janky, and the 'exploration' is limited to about five or ten seconds at most."
  - ▲5 (reply) "you can make edits deterministically"
  - ▲4 "Very impressive! Thank you for sharing this! Can you elaborate on the use case for an Ai researcher here? ... Can you run this locally? Is it open sourced?"
  - ▲1 (reply) "'Humanoid Robot Simulation in Generated 3D Scenes' is right there. We generate 3D Gaussians from text and import them into NVIDIA Isaac Sim... I don't see how Marble would be better at this."

## [r/LocalLLaMA] Apple introduces SHARP, a model that generates a photorealistic 3D Gaussian representation from a single image in seconds.

- url: https://reddit.com/r/LocalLLaMA/comments/1poy0lb/apple_introduces_sharp_a_model_that_generates_a/
- score: ▲1250 · 135评论 · date: 2025-12-17

- 楼主原声: GitHub: https://github.com/apple/ml-sharp \n\nPaper: https://arxiv.org/abs/2512.10685

- 高赞评论(原声):
  - ▲228 "Rendering trajectories (CUDA GPU only)\n\nFor real, Tim Apple?"
  - ▲105 "Does it work for adult content?.... I'm asking for a friend."
  - ▲74 [removed]
  - ▲43 "This is the future"
  - ▲40 (reply) "Just so future quick readers don't get confused, you can run this model on a Mac. The examples shown in the videos were generated on an M1 Max and took about 5–10 seconds. But for that other mode you need CUDA."
  - ▲39 (reply) "r/gaussiansplatting"
  - ▲39 (reply) "The examples shown in the video are rendered in real time on Apple Vision Pro and the scenes were generated in 5–10 seconds on a MacBook Pro M1 Max."
  - ▲33 (reply) "Also Black Mirror. Stepping into photos is a plot in one of the episodes."
  - ▲26 "this is some bladerunner shit"
  - ▲23 "This is the closest thing to a Cyberpunk Braindance I've ever seen IRL."
  - ▲21 "I had a go and yeah it kind of works."
  - ▲12 "Amazing something with 3d these days, either HY-world 1.5, microsoft trellis and that apple crazy thing. The future is here"
  - ▲7 "Would be interesting to see how well these stitch together, taking a 360 image and getting a 360 Gaussian would be quite nice for lots of uses"
  - ▲6 "Apple's bad because they like having proprietary standards. Why can't everyone just be sensible and use NVIDIA's proprietary standard instead?"
  - ▲4 "The 2D nature of the clip is hiding a lot of sins... I wish they'd focus more on reconstruction of 3D, and less on faking it."
  - ▲2 "A nice toy for a week, I guess. I am already exhausted seeing the video."

## [r/MachineLearning] I just read LeCun's recent thoughts on world models. Thoughts on JEPA as a path forward? [D]

- url: https://reddit.com/r/MachineLearning/comments/1v1i26p/i_just_read_lecuns_recent_thoughts_on_world/
- score: ▲85 · 61评论 · date: 2026-07-20

- 楼主原声: So, I just read LeCun's interview with Nebius Science. I feel he had some cool points about LLMs being able to answer things, but not literally understand the physics of the physical world. (Like, being able to explain a task and actually performing it are two completely different things.) But I wanted to get opinions on what others thought of his solution to the problem. He thinks JEPA could be the solution...

- 高赞评论(原声):
  - ▲191 "Well, If I developed/developing a new technology, I would definitely say that the technology that Im currently developing is the solution for a actual limitation of todays problem too."
  - ▲47 "As always in ML, ideas are cheap, implementation matters."
  - ▲33 "JEPA is less principled than generative approaches IMO... I don't see any way in which JEPA would be a better fit for world models."
  - ▲31 "Well, he's put some great research forward. Undeniable... Having said that, I think he's drinking way too much of his own kool-aid. 'World Models' by JEPA architecture which honestly largely relies on: Latent structure, autoregressive modeling and Contrastive Learning? Come on..."
  - ▲21 "JEPA itself already has limitations. + It doesn't really address partial observability in a thorough manner... + JEPA is still a form of traditional 'learning'. It does not have a directed response to address adaptation at deploy time (or 'test time'). So even JEPA will fail catastrophically when the agent encounters a situation that did not occur during training."
  - ▲11 (reply) "Meanwhile the technology he's claiming has 'fundamental limitations' is solving famous math problems that have been open since the 19th century over dinner. Unless LLMs run into a wall very soon, any alternative is going to be a tough sell."
  - ▲8 (reply) "LeCun routinely makes claims that aren't falsifiable. He may have put an argument out into the world, but he's given himself giant loopholes. Real theory deliberately exposes its soft underbelly. It announces what would prove it wrong. That's basic science."
  - ▲7 "Efficient world models seem supremely useful for synthetic data / RL training workflows, which are all the rage for agentic LLMs and increasingly self-driving cars. JEPA promises world modeling from tons of unlabeled data without the quadratic shenanigans of contrastive methods..."
  - ▲6 "Extremely bearish on JEPA"
  - ▲6 "we humans 'understand' the physical world exactly the same way LLMs 'understand' language. it's pattern matching and heuristics all the way down. our cognition is not special."

## [r/MachineLearning] Sub-JEPA: a simple fix to LeCun group's LeWorldModel that consistently improves performance [P]

- url: https://reddit.com/r/MachineLearning/comments/1tgn3bz/subjepa_a_simple_fix_to_lecun_groups_leworldmodel/
- score: ▲102 · 28评论 · date: 2026-05-18

- 楼主原声: World models learn compact latent representations for planning without pixel reconstruction. LeWorldModel (LeWM), from LeCun's group at NYU, achieves stable end-to-end JEPA training by enforcing an isotropic Gaussian prior over the full latent space. The flaw: real environment dynamics live on low-dimensional manifolds, so a global high-dimensional Gaussian is an overly rigid prior — mismatched to the task geometry. Our fix (Sub-JEPA): apply the Gaussian regularization inside multiple frozen random orthogonal subspaces instead. Consistently outperforms LeWM, up to +10.7 pp on Two-Room.

- 高赞评论(原声):
  - ▲42 "Isn't this already what LeJEPA does? Isn't the paper already about subsampling dimensions and applying SigReg only on a subset? The difference here is only keeping the subset fixed? Furthermore, isn't this just a sign that most dimensions are either garbage or another pathway for obscure regularizations?"
  - ▲22 (reply) "And if you look into the LeJEPA github repo, it's even less rigid, they actually apply the regulizer only to a MLP projection of the representation, not to the representation itself. There's even an issue about it, where someone from the team claims it just works better this way."
  - ▲16 "As someone using lejepa/sigreg myself, what are you doing differently? What's the trick?"
  - ▲12 "lol. This is one of the reasons I love ML. 'We proved this thing works optimally. But actually if we change it to this other thing it actually works better.'"
  - ▲9 (author reply) "LeJEPA/LeWM's SIGReg projects onto thousands of 1D directions precisely to constrain the entire ambient space to be isotropic Gaussian... Our point is that constraining the full ambient space is too strong a prior when the true dynamics live on a low-dimensional manifold."
  - ▲4 "With my new paper I propose the novel concept: 'just add another layer'"
  - ▲2 "How do you guys prevent z_pred from collapsing in JEPA training? ... the predicted latents collapse to a 0 norm and MSE of 1 (predicting the mean). How do you guys deal with this?"

## [r/MachineLearning] What's the actual focus in World Models right now? [R]

- url: https://reddit.com/r/MachineLearning/comments/1ttei2r/whats_the_actual_focus_in_world_models_right_now_r/
- score: ▲82 · 28评论 · date: 2026-05-26

- 楼主原声: Hey everyone, I'm trying to get back into the loop on world models. The last time I followed SSL closely, the buzz was all about Barlow Twins and DINO, but now everything just looks like scaled-up video generation from big industry labs. What is the actual academic research community stressing over right now?

- 高赞评论(原声):
  - ▲44 "Maybe reconstruction-free/JEPA"
  - ▲27 "'World model' is kind of an overloaded term because I see people referring to world models as both the generative models that create coherent 4D worlds and the things inside of them, and I see people referring to world models as the AI models that interact with the 4D worlds. The videos aren't just regular videos, they're closer to simulations... The general direction is: use a fixed encoder that acts as ground truth for reality, the encoder's output is the model's input, and have the model either predict the next encoder output, or fill in the blanks from masked encoder output."
  - ▲14 "Pixel reconstruction is really hard for learning useful representations from videos, so people are turning to latent-space reconstruction methods. Yann Le Cun is now pushing JEPA architectures, and they have a new paper showing a teacher/EMA-free method that scales well (LeJEPA)... We are also discovering that these methods (latent space reconstruction) are also amazing for other modalities, like audio, images etc."
  - ▲9 "are you asking about SSL/UL in general? to me, 'world model' usually means something like 'unconditional video model', unless it's contextualized more."
  - ▲8 "A lot depends on which camp you mean by 'world models.' The visible frontier right now is definitely video generation, but personally I think the more interesting research questions are underneath that: What representation makes physical state compact and learnable? What update operator lets that state evolve stably over long horizons? ... My impression is that the field still hasn't had its 'transformer moment' for physical systems."
  - ▲3 "The academic community is mostly focused on learning dynamics prediction without explicit 3D reconstruction. The video generation labs are solving a different problem. The real research frontier is whether you can learn a compressed world state that supports planning, not just next-frame prediction."
  - ▲1 "I think the current world model is moving into a pitfall because lack of causal relationships"

## [r/MachineLearning] [D] A little late but interesting talk by Fei-Fei Li at NeurIPS 2024

- url: https://reddit.com/r/MachineLearning/comments/1i74pni/d_a_little_late_but_interesting_talk_by_feifei_li/
- score: ▲45 · 4评论 · date: 2025-01-22

- 楼主原声: Great talk by Fei-Fei Li on Visual Intelligence and what the future holds for AI. Wanted to share it here in case anyone wants to check it out on their website. TL;DR: At NeurIPS 2024, Fei-Fei Li delivered a talk titled "From Seeing to Doing: Ascending the Ladder of Visual Intelligence," where she emphasized the progression from visual perception to actionable intelligence in AI systems. She highlighted the limitations of current AI, particularly its reliance on two-dimensional data, and advocated for the development of "spatial intelligence" to enable machines to comprehend and interact with the three-dimensional physical world. Li discussed her work at World Labs, focusing on creating AI models that understand 3D environments, which is crucial for applications in robotics, autonomous vehicles, and augmented reality.

- 高赞评论(原声):
  - ▲4 "Thanks for sharing"
  - ▲3 (reply) "Updated!"
  - ▲2 "Amazing, thanks!"
  - ▲1 "Can anyone give us a TLDR of the talk?"

---

> 采集缺口: r/LocalLLaMA 搜索 "world labs spatial intelligence" 直接命中仅1帖（即上述首帖），World Labs 话题在该社区讨论密度低。r/MachineLearning 无直接讨论 World Labs Marble 产品的帖子，最相关的为 Fei-Fei Li NeurIPS 2024 演讲帖及世界模型/ JEPA 架构讨论。上述输出全部来自工具返回数据，无先验编造。
