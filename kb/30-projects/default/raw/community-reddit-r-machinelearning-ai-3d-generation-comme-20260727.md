---
kind: community_raw
platform: reddit
topic: "r/MachineLearning AI 3D generation commercial use 2026"
fetch_ts: 2026-07-27T00:04:39+00:00
content_hash: d20ed7e6b2e18d04
project: default
model: ds-chat
trace: traces/reddit_deep/20260727/r-machinelearning-ai-3d-generation-comme.json
source_urls:
  - https://www.reddit.com/r/MachineLearning/comments/1oe6ywk/r_continuous_latent_interpolation_breaks/
  - https://www.reddit.com/r/StableDiffusion/comments/1puszuc/former_3d_animator_trying_out_ai_is_the/
  - https://www.reddit.com/r/StableDiffusion/comments/1pwlt52/former_3d_animator_here_again_clearing_up_some/
  - https://www.reddit.com/r/StableDiffusion/comments/1r7r9rw/fully_automatic_generating_and_texturing_of_3d/
  - https://www.reddit.com/r/StableDiffusion/comments/1sll638/tencent_hyworld_20_appears_to_be_dropping_on/
  - https://www.reddit.com/r/StableDiffusion/comments/1v4k3je/trellis2_can_now_generate_a_highquality_3d_asset/
---

# 社区原声:reddit / r/MachineLearning AI 3D generation commercial use 2026

> reddit-research-mcp 深潜采集(ds-chat 忠实转录,未分析)。**原声在高赞评论里**;digester 蒸馏时逐条痛点回指具体评论(带▲赞数),交叉验证,勿把评论区综合成一句。

## [r/StableDiffusion] Former 3D Animator trying out AI, Is the consistency getting there?
- url: https://www.reddit.com/r/StableDiffusion/comments/1puszuc/former_3d_animator_trying_out_ai_is_the/
- score: ▲4625 · 492评论 · date: 2025-12-24
- 楼主原声: Attempting to merge 3D models/animation with AI realism. Greetings from my workspace. I come from a background of traditional 3D modeling. Lately, I have been dedicating my time to a new experiment. This video is a complex mix of tools, not only ComfyUI. To achieve this result, I fed my own 3D renders into the system to train a custom LoRA. My goal is to keep the "soul" of the 3D character while giving her the realism of AI. I am trying to bridge the gap between these two worlds. Honest feedback is appreciated. Does she move like a human? Or does the illusion break? (Edit: some like my work, wants to see more, well look im into ai like 3months only, i will post but in moderation, for now i just started posting i have not much social precence but it seems people like the style)
- 高赞评论(原声):
  - ▲916 ">3D animator. >the sweater. >the armpits. Top tier choices. I know what you are."
  - ▲276 "https://preview.redd.it/b3ulgzpg479g1.jpeg?width=842&format=pjpg&auto=webp&s=dd8fc51538208c730e82c7f38853972041ab46f9" (图片回复)
  - ▲239 "haha, i felt that since the posts here were slightly spicy but SFW, i should create something that is appealing like skin, videogames and anime often portray skin a lot so i went with that, but i do have to say there's a certain niche to this fetish. glad u liked it."
  - ▲38 "I see she comes equipped with the virgin slayer sweater. Well played, sir."
  - ▲27 "i have only started posting from today, i have projects but i think i dont want to become a slop, so wanna post in moderation keeping quality over quantity."
  - ▲11 "thanks for this, i mean i still didn't know people would have content to sites for these, in general many hate ai so i myself in moderation to too much exposure as i slightly fear backlash as ai and digital artist using it bit of taboo still and there are sloppy art of ai too which I don't want the label to be placed. i learned today people like this sort of style even tho i feared it."
  - ▲11 "lol now i want my electricity bill to be free at this point, if ai content can bare the cost of electricity+gpu cloud rent, it be enough. i am currently burning a lot of Change for these test run. tho glad this one was worth it, the approx cost of this one and few similar was around $70 to $200 of render cost in testing."

## [r/StableDiffusion] Fully automatic generating and texturing of 3D models in Blender - Coming soon to StableGen thanks to TRELLIS.2
- url: https://www.reddit.com/r/StableDiffusion/comments/1r7r9rw/fully_automatic_generating_and_texturing_of_3d/
- score: ▲662 · 159评论 · date: 2026-02-18
- 楼主原声: EDIT: It is now released. A new feature for StableGen I am currently working on. It will integrate TRELLIS.2 into the workflow, along with the already exsiting, but still new automatic viewpoint placement system. The result is an all-in-one single prompt (or provide custom image) process for generating objects, characters, etc. Will be released in the next update of my free & open-source Blender plugin StableGen.
- 高赞评论(原声):
  - ▲60 "The texturing itself is projection based, using good old SDXL. But Qwen-Image-Edit and FLUX.1 are also available. FLUX.2 Klein support will also be added soon."
  - ▲27 "It's a whole set of different mechanisms. I wrote my bachelor thesis about it - you can find it in the StableGen GitHub if you're interested in the details (it's in English). TL;DR: Some combination of: Inpainting, differential diffusion, IPAdapter & normal angle based blending within shaders."
  - ▲24 "Here's the GitHub link. You can try the plugin as-is or wait for the release of this (kinda big) update: https://github.com/sakalond/StableGen"
  - ▲18 "This looks like voodoo. Amazing work! How do you auto fix the seams?"
  - ▲12 "990k triangles💔"
  - ▲11 "The TRELLIS.2 native textures will be of course also available. They aren't as detailed, but have full PBR (and don't suffer from occlusions). So you may try and choose what suits your use case. (I will also try to bring PBR to my projection based system in the future)"
  - ▲9 "I sure hope you'll prove me wrong, I had a similar project in mind and ditched it. Funny that my comments get downvoted for sharing the info I know. It's called denial I guess."

  > 采集缺口: 商业许可讨论链完整
  - ▲7 "No, it doesn't. It uses some nvidia libs which strictly forbids commercial use. And RMBG, which is also not free for commercial use."
  - ▲6 "So I did a deeper dive into the source code. It seems that the shape only workflow does not utilize those nvidia libraries at all. So it should be clean once I bypass RMBG. (unless you need to use TRELLIS.2 native texturing)"
  - ▲5 "Nice, too bad it can't be used commercially."
  - ▲5 "I can bypass the RMBG step easily with something else. I will look into those libraries. Any idea at which point they are used exactly? Good catch anyway."
  - ▲4 "License allows it (unless you use FLUX)"

## [r/StableDiffusion] TRELLIS.2 can now generate a high-quality 3D asset in under 7 minutes on a 6 GB VRAM CUDA GPU. No ComfyUI Node Nightmare.
- url: https://www.reddit.com/r/StableDiffusion/comments/1v4k3je/trellis2_can_now_generate_a_highquality_3d_asset/
- score: ▲649 · 144评论 · date: 2026-07-23
- 楼主原声: Not Self Promotion: Just sharing an open-source tool I built to democratize image to 3D creations. For OpenAI Build Week Hackathon I built a free, open-source local Image-to-3D Studio that makes TRELLIS.2 easier to run on consumer NVIDIA gpus like 3060 or a laptop 3070ti, without expensive cloud APIs, subscriptions, or complicated ComfyUI workflows. It combines generation, texturing, retopology, rigging, and animation in one interface. I know there are already multiple implementations of running Trellis2 under 8gb GPU. The hard part was to test the best possible combination for mesh/textures that gave 1024 High precision quality but still kept under the VRAM.
- 高赞评论(原声):
  - ▲150 "I'll just throw out there that what people not in 3d mean by 'high-quality 3d asset' is very, very different from what people in 3d mean by that. These are extremely low-quality 3d assets."
  - ▲29 "You are quite right, terrible topology and messed-up UV unwrapping. By High Quality 3D asset, I mostly mean aesthetic quality and depth. But in my refine tab workflow, I tried to fix the topology a bit. There are also works in progress for making it fully game-ready, but that has to wait until they pass judgment on the hackathon, as no more edits are allowed in the meantime."
  - ▲27 "These can be used as background assets"
  - ▲20 "It's more than enough to slice and 3D Print stuff though."
  - ▲10 "Ah yes, you're mostly right, but I just want to add it's also use-case specific. I myself am a 3d/Vfx professional with more than 10+ Years in the Industry. For many of my workflows Trellis2 would've been a blessing. For a government MegaProject back in 2017, we had to build the whole city and it's metro rail system in 3D. Everything was done manually, and most were 'hard surface' models. Trellis2 models would work perfect for that, saving hours of hard work. For another children's animated series in German national channel we used a lot of Artistic meshes too, where trellis could nicely recreate the concept art to just drop into Blender."
  - ▲10 "Soooo AI doesnt generate good 3D Models if I still have to do 80% of the Work"
  - ▲5 "What a troll. Shut up. This is free"
  - ▲3 "Retopo will fix it, dont have to start from the scratch"
  - ▲3 "Nah, it wont. I've checked."

## [r/StableDiffusion] Tencent HY-World 2.0 appears to be dropping on April 15 — open-source multimodal 3D world generation from Tencent Hunyuan
- url: https://www.reddit.com/r/StableDiffusion/comments/1sll638/tencent_hyworld_20_appears_to_be_dropping_on/
- score: ▲554 · 103评论 · date: 2026-04-12
- 楼主原声: Tencent's Hunyuan team is apparently releasing HY-World 2.0 tomorrow, according to a teaser post from Tengfei Wang (Tencent Hunyuan): "Launching tomorrow — Tencent #HYWorld 2.0, an engine-ready World Model". The launch page is already live... HY-World 2.0 is a multimodal world model that can generate persistent, explorable 3D environments from: Text prompts, Single images, Multiple images, Video input. Unlike many world models that only output video, this one generates engine-compatible editable 3D scenes, exportable as: 3D Gaussian Splatting (3DGS), Mesh, Point clouds, Video renders. It also supports: Free navigation with collision physics, Unity / Unreal Engine compatibility, Real-world reconstruction from photos/video, Panorama generation, "Character mode" for playable scene exploration.
- 高赞评论(原声):
  - ▲54 "The fact this will be able to output to major game engines is HUGE. This will make game devs lives a LOT easier."
  - ▲35 "Gamer Karens won't even want AI generated 2D assets. But I can see this would help rapid prototyping."
  - ▲32 "From image generation to video generation, and now 3d generation? Jeez"
  - ▲30 "I'm not making games for them, this is just for me and my boy Claude"
  - ▲17 "This will not be used in any game dev workflows for a while. Not nearly good enough yet."
  - ▲15 "All of it? No. There's a lot of slop if you don't know what you're doing but when you get to an advanced level with these tools you can have amazing results."
  - ▲12 "It was the same with just, for example, speedtree: instead of 10 devs to model and place trees by hand, one dev can do it just by changing parameters. but to put things in perspective, just before the arrival of AI, we'd never had so many active video game developers."
  - ▲11 "That's marketing, there will be zero real world usage of this model in unreal game development. If you've worked with unreal of game development then you will know that generating a world model mesh with no detail and edit ability as it's one massive mega mesh mess is useless."
  - ▲8 "Games in development are heavily using AI for art but not telling you as it's a sensitive subject."
  - ▲7 "And all the people who worked in video stores? ... That's what computers have been doing for 70 years! Nothing new under the sun, and nobody cared before… I'm surprised that we're paying more attention to a few video game developers than to the millions of people working in other sectors…"

## [r/MachineLearning] [R] Continuous latent interpolation breaks geometric constraints in 3D generation
- url: https://www.reddit.com/r/MachineLearning/comments/1oe6ywk/r_continuous_latent_interpolation_breaks/
- score: ▲64 · 21评论 · date: 2025-10-23
- 楼主原声: Working with text-to-3D models and hitting a fundamental issue that's confusing me. Interpolating between different objects in latent space produces geometrically impossible results. Take "wooden chair" to "metal beam". The interpolated mesh has vertices that simultaneously satisfy chair curvature constraints and beam linearity constraints. Mathematically the topology is sound but physically it's nonsense. This suggests something wrong with how these models represent 3D space. We're applying continuous diffusion processes designed for pixel grids to discrete geometric structures with hard constraints. Is this because 3D training data lacks intermediate geometric forms? Or is forcing geometric objects through continuous latent mappings fundamentally flawed?
- 高赞评论(原声):
  - ▲57 "This phenomenon has been studied extensively in computer graphics and medical imaging, where generating realistic shapes is a key requirement. Researchers in these fields like to think that 3D shapes belong to a non-Euclidean 'shape space', whose geodesics correspond to plausible interpolating trajectories. As a recent example, you may check the repulsive shells paper. Machine learning in this setting is a very active research topic."
  - ▲17 "Well, that's right, the latent space isn't built for complex geometric rules. It just mixes things that shouldn't be mixed together."
  - ▲10 "Sort of, yeah. You're solving an underspecified problem with a universal approximator and then giving it inputs for which you've provided no data or constraints. Like, what does it even mean to 'interpolate between a chair and a beam'? I can imagine multiple ways of interpreting that statement."
  - ▲5 "It's been a while since I read anything about it, but I think you may be touching upon the difference between a linear or unstructured latent space where implausible samples can be discovered, and a manifold aligned latent space where plausibility is baked into the latent and as such generally only plausible samples can be discovered."
  - ▲3 "Researchers in these fields like to think that 3D shapes belong to a non-Euclidean 'shape space'... Then, there are papers trying to build better path in the latent space. In particular there are people trying to understand the deformation of the space (e.g. looking at the jacobian of the decoders) to build geodesics in the latent space."
  - ▲1 "Meshy handles this better in my experience."

## [r/StableDiffusion] Former 3D Animator here again – Clearing up some doubts about my workflow
- url: https://www.reddit.com/r/StableDiffusion/comments/1pwlt52/former_3d_animator_here_again_clearing_up_some/
- score: ▲487 · 76评论 · date: 2025-12-26
- 楼主原声: I recently posted a video here that many of you liked. As I mentioned before, I am an introverted person who generally stays silent, and English is not my main language. Being a 3D professional, I also cannot use my real name on social media for future job security reasons. (also again i really am only 3 months in, even tho i got the boost of confidence i do fear i may not deliver right information or quality so sorry in such cases.) What exactly am I doing in my videos? 1. 3D Posing: I start by making 3D models... 2. ComfyUI: I then bring those renders into ComfyUI... 3. The Technique: I use the 3D models for the pose or slight animation, and then overlay a set of custom LoRAs with my customized textures/dataset.
- 高赞评论(原声):
  - ▲49 "Thank you for sharing your knowledge senpai."
  - ▲20 "i hope i delivered rightfully."
  - ▲17 "Very similar to what I do with comics. My WF starts with custom Cinema 4D characters. I work with my custom LoRAs from my own illustration style and ComfyUI or Stable Diffusion. I will then finish the panel in Clip Studio Paint."
  - ▲16 "あなたの作品は本当にクオリティが高すぎます。。"
  - ▲15 "just wanna say thanks for sharing the resources and approach used. 1girl instagram videos are a dime a dozen here but yours in my opinion is very well done, good quality production"
  - ▲10 "This are the kind of post i adore, someone find out something special and tells other about it and teaches them how to do it. Imagine we had this in every sub here."
  - ▲6 "yes i use daz or any free or affordable models, i collected many 3D models over the decade but since my gpu is a titan x maxwell i kept simplicity of tools like blender,daz and web 3D posing... the gist is better the 3D models u use better ai will stick to it like a skin. but u don't need High game ready or metahuman just even basic anatomy i used would do but just keep background colour neutral."
  - ▲6 "thanks, well this takes enormous time the workflow is complicated and riddled with time consuming but the output is good."
  - ▲5 "Perhaps this could be of use for you: https://posemy.art/app/?lang=en"
  - ▲4 "I'm happy to spend the time refining the images to get exactly what I want. It's still easier than my days of drawing comics for a living."
  - ▲2 "I'd like to know more about the process below! >3. The Technique: I use the 3D models for the pose or slight animation, and then overlay a set of custom LoRAs with my customized textures/dataset."
