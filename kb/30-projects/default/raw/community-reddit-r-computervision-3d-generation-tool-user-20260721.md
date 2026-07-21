---
kind: community_raw
platform: reddit
topic: "r/computervision 3D generation tool user sentiment 2026"
fetch_ts: 2026-07-21T00:04:04+00:00
content_hash: ee056e097dd06831
project: default
model: ds-chat
trace: traces/reddit_deep/20260721/r-computervision-3d-generation-tool-user.json
source_urls:
  - https://reddit.com/r/StableDiffusion/comments/1oxn70h/how_do_you_think_ai_will_integrate_into_3d/
  - https://reddit.com/r/StableDiffusion/comments/1q3ijwo/trellis_2_is_already_getting_dethroned_by_other/
  - https://reddit.com/r/StableDiffusion/comments/1qxjdz5/best_ai_tools_currently_for_generative_3d/
  - https://reddit.com/r/StableDiffusion/comments/1r7r9rw/fully_automatic_generating_and_texturing_of_3d/
  - https://reddit.com/r/computervision/comments/1q4sza0/implemented_3d_gaussian_splatting_fully_in/
  - https://reddit.com/r/computervision/comments/1rcjirq/is_it_worth_implementing_3d_gaussian_splatting/
  - https://www.reddit.com/r/comfyui/comments/1q4aii4/ultrashape_deep_dive/?show=original
---

# 社区原声:reddit / r/computervision 3D generation tool user sentiment 2026

> reddit-research-mcp 深潜采集(ds-chat 忠实转录,未分析)。**原声在高赞评论里**;digester 蒸馏时逐条痛点回指具体评论(带▲赞数),交叉验证,勿把评论区综合成一句。

## [r/StableDiffusion] Trellis 2 is already getting dethroned by other open source 3D generators in 2026
- url: https://reddit.com/r/StableDiffusion/comments/1q3ijwo/trellis_2_is_already_getting_dethroned_by_other/
- score: ▲195 · 75评论 · date: 2026-01-04
- 楼主原声: Update: link for Ultrashape ComfyUI integration:

[https://www.reddit.com/r/comfyui/comments/1q4aii4/ultrashape_deep_dive/?show=original](https://www.reddit.com/r/comfyui/comments/1q4aii4/ultrashape_deep_dive/?show=original)

[https://github.com/jtydhr88/ComfyUI-UltraShape1](https://github.com/jtydhr88/ComfyUI-UltraShape1)

——-

So I  made some errors and now am rewriting this post to clarify what those models do, since I overlooked, that those models are for refinement, after the initial 3D model geometry creation only.

Still I think we will see large strides in the 3D generation space in 2026
- 高赞评论(原声):
  - ▲41 "Of this list hunyuan motion has been the biggest W for me. Finding cleanish mocap animations of everyday things is honestly a bitch. Being able to type the motion I want in and get a rigged rig performing that motion in seconds is huge and I don't know why more people are screaming about it."
  - ▲17 "So Ultrasharo can't do textures at all making it not very usable for much and the others aren't out yet? So….huh?"
  - ▲7 "Not sure what you mean about 'dethroned'. You're comparing apple vs orange. Many of these are not exactly image to 3D generator like Trellis or Hunyuan. Lattice and Ultrashape are 3D to 3D."
  - ▲5 "UniRig very bad. Is like a automatic rig in any Maya or blender"
  - ▲4 "I deeply researched trellis2 even if ultrasharp looks a like bit better, trellis 2 has much more potential. And it's mit licensed. Tenant license is not for commercial use at all."
  - ▲3 "Problem with these is they are on the border of my gpu vram and I have not seen them get quantized like other models."
  - ▲2 "I personally am only in the geometry created, to use that as a base mesh for manual sculpting and modeling. I don't think many of the available 3D generators seem to create usable PBR textures without baked in shadows. I see most textures generated just as a toy, unusable for most 3D scenes."

## [r/StableDiffusion] How do you think AI will integrate into 3D modeling pipelines over the next 5 years? (Sharing some models I generated)
- url: https://reddit.com/r/StableDiffusion/comments/1oxn70h/how_do_you_think_ai_will_integrate_into_3d/
- score: ▲342 · 205评论 · date: 2025-11-15
- 楼主原声: I'm experimenting with AI-assisted 3D workflows and wanted to share a few of the models I generated using recent tools
- 高赞评论(原声):
  - ▲79 "Those look nice. I think it's going to be massive, it's already working into a lot of pipelines and we're going to see the fruits of that in the next couple of years as the games and films which were not started or early enough into production when 3D generated models started to become good enough reach completion. Right now, it's really only suitable for base sculpts and statics but a lot of meshes are static so that's already doing a lot of work. Topology is the big thing left to resolve if we want clean deformations and fully-generated characters but bipedal character topology doesn't seem like that daunting of a task to solve to me."
  - ▲41 "care to share the wireframes?"
  - ▲36 "Ouch. Well, hopefully they will integrate with topology tools. It's a good first step, though."
  - ▲14 "I'm no 3d modeller but, can't meshes like this be 'shrink wrapped' to some degree. you could then project the uv/surface normals into the shrink wrap?"
  - ▲10 "Retopology is boring and time-consuming, i hope AI can solve this problem soon."
  - ▲9 "So you do remesh it and then what do you do with a new UV and broken texture? Once people figure out the way to generate correct topology with AI and correct UV islands then it will be amazing. But right now since AI generates bonkers UV and ridiculous topology I see no use for it except for props in background."
  - ▲7 "Came here to ask the same. How much of this can be auto-optimized to reduce the overly detailed vertex mesh without loosing too much fidelity? Or that would be essentially a second pass with a different AI which can decimate this mesh?"
  - ▲6 "lol perfect. I'm sure you can have at least 3 of these in a game engine before the fps drops"
  - ▲4 "The better choice is to retopo, either way that is where the majority of your time is spent, so if you are already wrapping mesh or retopoing then you might as well do manual editing, the genAI basically functions as a starting point, or reference object. Too much bleed in the textures and too much inaccuracies in the mesh to justify a lot of time spent retopoing or transfer textures to new UV."

## [r/StableDiffusion] Fully automatic generating and texturing of 3D models in Blender - Coming soon to StableGen thanks to TRELLIS.2
- url: https://reddit.com/r/StableDiffusion/comments/1r7r9rw/fully_automatic_generating_and_texturing_of_3d/
- score: ▲668 · 159评论 · date: 2026-02-18
- 楼主原声: EDIT: It is now released

A new feature for StableGen I am currently working on. It will integrate TRELLIS.2 into the workflow, along with the already exsiting, but still new automatic viewpoint placement system. The result is an all-in-one single prompt (or provide custom image) process for generating objects, characters, etc.

Will be released in the next update of my free & open-source Blender plugin StableGen.
- 高赞评论(原声):
  - ▲57 "The texturing itself is projection based, using good old SDXL. But Qwen-Image-Edit and FLUX.1 are also available. FLUX.2 Klein support will also be added soon." — sakalond
  - ▲25 "It's a whole set of different mechanisms. I wrote my bachelor thesis about it — you can find it in the StableGen GitHub if you're interested in the details (it's in English). TL;DR: Some combination of: Inpainting, differential diffusion, IPAdapter & normal angle based blending within shaders." — sakalond
  - ▲24 "Here's the GitHub link. You can try the plugin as-is or wait for the release of this (kinda big) update: https://github.com/sakalond/StableGen" — sakalond
  - ▲18 "This looks like voodoo. Amazing work! How do you auto fix the seams?"
  - ▲11 "990k triangles💔"
  - ▲11 "The TRELLIS.2 native textures will be of course also available. They aren't as detailed, but have full PBR (and don't suffer from occlusions). So you may try and choose what suits your use case." — sakalond
  - ▲8 "looking for updates and good news :)"
  - ▲7 "I looked into it too. Is not for rendering only, but for adjustments based on rendering. Also uses nvdiffrec and kaolin, both from NVIDIA, under the same license."
  - ▲5 "Nice. I bet FLUX.2 Klein will be amazing. So far I love what FLUX.2 Klein can do in Photoshop, but now Blender?! I use Blender for my designing over Photoshop daily... what you've done here will speed up my work 100x."
  - ▲5 "Nice, too bad it can't be used commercially."

## [r/StableDiffusion] Best AI tools currently for Generative 3D? (Image/Text to 3D)
- url: https://reddit.com/r/StableDiffusion/comments/1qxjdz5/best_ai_tools_currently_for_generative_3d/
- score: ▲4 · 18评论 · date: 2026-02-06
- 楼主原声: Hey everyone, I'm currently exploring the landscape of AI tools for 3D content creation and I'm looking to expand my toolkit beyond the standard options. I'm already familiar with the mainstream platforms (like Luma, Tripo, Spline, etc.), but I'm interested to hear what software or workflows you guys are recommending right now for: Text-to-3D; Image-to-3D; Reconstruction (NeRFs or GS); Texture Generation. I'm looking for tools that export standard formats (OBJ, GLB, FBX) and ideally produce geometry that isn't too difficult to clean up.
- 高赞评论(原声):
  - ▲2 "This is the best resource I know of to compare the latest models. It has a leaderboard, but comparing the models yourself side by side is very useful: https://www.top3d.ai/arena"
  - ▲1 "That would probably be trellis 2. It's still kind of messy compared to closed source though. 3D doesn't get the love it deserves."
  - ▲1 "I'd say Rodin is worth trying, especially if you care about clean geometry and fast iteration. Rodin Gen-2.5 feels much stronger in both geometry and textures, with more faithful surface details and better PBR materials."

## [r/computervision] Implemented 3D Gaussian Splatting fully in PyTorch — useful for fast research iteration?
- url: https://reddit.com/r/computervision/comments/1q4sza0/implemented_3d_gaussian_splatting_fully_in/
- score: ▲276 · 11评论 · date: 2026-01-05
- 楼主原声: I've been working with 3D Gaussian Splatting and put together a version where the entire pipeline runs in pure PyTorch, without any custom CUDA or C++ extensions. The motivation was research velocity, not peak performance: everything is fully programmable in Python; intermediate states are straightforward to inspect. The obvious downside is speed: On an RTX A5000, ~1.6 s/frame @ 1560×1040 (inference), ~9 hours for ~7k training iterations per scene. [Code is public]
- 高赞评论(原声):
  - ▲3 "That seems awesome, congrats!"
  - ▲2 "My guess is that the main bottleneck is kernel launch overhead from processing each tile in a Python-level loop. The workload seems fragmented into many small kernels, so launch latency and poor GPU utilization likely dominate. I'd expect kernel fusion or using Triton to give a significant speedup."
  - ▲1 "Curious, what is the main cause for the slow-down? What ops are inefficiënt in pytorch? Awesome work!"

## [r/computervision] Is it worth implementing 3D Gaussian Splatting from scratch to break into 3D reconstruction?
- url: https://reddit.com/r/computervision/comments/1rcjirq/is_it_worth_implementing_3d_gaussian_splatting/
- score: ▲30 · 11评论 · date: 2026-02-23
- 楼主原声: I'm trying to get into the 3D reconstruction/neural rendering space. I have a DL background and have implemented NeRF and a few related papers before, but I'm new to this specific subfield. My plan is to implement the core pipeline in pure PyTorch (projection, differentiable rasterization, SH, densification, training loop) on small synthetic scenes, skipping the CUDA rasterizer entirely. It'll be slow but should be correct (?). For anyone working in this space: is this a reasonable way to build up the knowledge needed for 3D reconstruction roles?
- 高赞评论(原声):
  - ▲8 [removed]
  - ▲5 "If you have DL background I would suggest to look into basics of 3d classical pipelines and try to implement things that does colmap for example, as mini projects. Explore also things like use depth model and try to align them as point clouds, learn about ICP, BA, camera calibrations etc. Also look into graphics renderings basics. I recommend that route because you will gain better understanding and rarer skillsets to expand and build with your DL skills."
  - ▲2 "If you do break into it, what do you imagine you'll be doing? If you intend to work in some field, why wouldn't you get as familiar as possible with its fundamentals as soon as possible?"
  - ▲1 "I'm not sure splatting is going to help you much working towards 'neural rendering'. But it is the 'state-of-the-art' right now so it surely can't hurt to learn. But I wouldn't skip the CUDA. Do it all otherwise you'll have a significant knowledge and performance lag/gap."
  - ▲1 "Yes—I actually did this myself (in PyTorch, no custom CUDA), and I'd definitely recommend it. You don't need to reproduce all the optimized parts. Even just implementing the splatting (i.e. no training) already teaches you a lot about how the method works."
