---
kind: community_raw
platform: reddit
topic: "r/GaussianSplatting 开源实时3D重建讨论与痛点"
fetch_ts: 2026-08-06T00:02:36+00:00
content_hash: 69d1fa3d5e64052e
project: default
model: ds-chat
trace: traces/reddit_deep/20260806/r-gaussiansplatting-开源实时3d重建讨论与痛点.json
source_urls:
  - https://reddit.com/r/GaussianSplatting/comments/1q430m5/gsplat_allinone_gui_for_mac_silicon/
  - https://reddit.com/r/GaussianSplatting/comments/1qha7ae/freeopen_source_alternatives_to_postshot/
  - https://reddit.com/r/GaussianSplatting/comments/1rv03sb/blunt_opensource_tool_to_turn_any_photo_into_a/
  - https://reddit.com/r/GaussianSplatting/comments/1snq9do/built_a_colmap_3dgs_pipeline_for_home_interiors/
  - https://reddit.com/r/GaussianSplatting/comments/1tvptue/supersplat_moves_to_webgpu_for_huge_performance/
  - https://reddit.com/r/photogrammetry/comments/1t7bg15/are_gaussian_splats_actually_useful_yet/
---

# 社区原声:reddit / r/GaussianSplatting 开源实时3D重建讨论与痛点

> reddit-research-mcp 深潜采集(ds-chat 忠实转录,未分析)。**原声在高赞评论里**;digester 蒸馏时逐条痛点回指具体评论(带▲赞数),交叉验证,勿把评论区综合成一句。

## [r/GaussianSplatting] BLUNT — open-source tool to turn any photo into a Gaussian Splat (MIT licensed, runs locally)
- url: https://reddit.com/r/GaussianSplatting/comments/1rv03sb/blunt_opensource_tool_to_turn_any_photo_into_a/
- score: ▲193 · 39评论 · date: 2026-03-16
- 楼主原声: Hey everyone - I recently shipped image to splat in StorySplat and then realized I could not use SHARP commercially, so over the past two days, I created and open-sourced alternative called BLUNT (Basic Lifting and UNprojection Tool) — a single Python script that converts a photo into a 3DGS PLY file in a few seconds.
- 高赞评论(原声):
  - ▲12 "The Depth Anything v2 is very outdated. You might wanna check out DA360 from the Insta360 Team: https://github.com/Insta360-Research-Team/DA360"
  - ▲8 "I will add some more examples including 360 generations tomorrow"
  - ▲7 "I have a PR up with DA3 and 360 integrated. Will do testing today and update with a new post and examples"
  - ▲6 "Nice work! Now you can technically get google street view to gaussian 😊"
  - ▲4 "Amazing work. Are you able to use this to produce splat sequences from a video but retain depth consistency frame to frame?"
  - ▲3 "Great project, I will test it further with AMD (ROCm) but since you use Pytorch it should run fine. I might also try to push a PR to support 360 panorama and not only 360 output from a spherical camera. Thanks :)"

## [r/photogrammetry] Are Gaussian splats actually useful yet?
- url: https://reddit.com/r/photogrammetry/comments/1t7bg15/are_gaussian_splats_actually_useful_yet/
- score: ▲19 · 34评论 · date: 2026-05-08
- 楼主原声: I might just be cranky this morning, but is this sub basically just /r/gaussiansplats now? Is it just me? Gaussian splats look like ass and don't produce useful geometry still, right? (Also they're not photogrammetry, but that's nitpicking)
- 高赞评论(原声):
  - ▲33 "I use them for professional surveying, mapping, and inspection work from drones and phones. I have given a few presentations on how they are useful in Engineering, Construction, and Surveying. They can be fully georeferenced and scaled now."
  - ▲16 "If you look at the cutting edge research yes they're useful. Product wise, not really."
  - ▲11 "They used them at the winter Olympics recently for virtual camera moves during replays. I'd say that's a pretty real-world use case. Sure, for small object reproduction or surveying, they aren't the go-to tool (yet) - although I don't really do surveying, so maybe people are using them more for that now. But I think they produce pretty incredible results when used in areas that photogrammetry falls flat: capturing real world scenes with lots of transparency or reflective surfaces, historical preservation of locations using non-ideal (or just overly sparse) capture methods, real-time playback with photorealistic lighting without the weight of a rendering engine, etc."
  - ▲8 "It's not that challenging to make ones that don't look like ass and yes, they're useful. Not as useful as I'd like them to be admittedly, largely due to the current limitations of which software packages have put the effort in so far, but that's growing at a reasonable pace."
  - ▲8 "Completely depends on what you consider useful. Raw geometry is not always needed"
  - ▲8 "I'm an architectural historian and we have been using basic iPhone scanning (Scaniverse as it's free) to show preservation officers in small, low-budget towns how they can use phone photogrammetry to crowdsource documentation of buildings that otherwise wouldn't be documented (such as a rural Black farmstead in danger of demolition, or someone's personal historic home)... at least for iPhone scanning, gaussian splats are usually the way to go for the exteriors of buildings or anything that would trip up a mesh (fine ironwork with lots of holes, very reflective objects, objects being hit by sun outdoors, etc). I sometimes prefer to use a 3d mesh on interior spaces if i'm just doing it for the measurements."

## [r/GaussianSplatting] Free/open source alternatives to PostShot
- url: https://reddit.com/r/GaussianSplatting/comments/1qha7ae/freeopen_source_alternatives_to_postshot/
- score: ▲12 · 33评论 · date: 2026-01-19
- 楼主原声: Hi! I want to know if there is an alternative to PostShot in order to create Gaussian Splats locally? I'm planning on creating some splats using a 360 camera with some students for a VFX assignments and I'd rather not having to use PostShot as it's a paid app now. Using Colmap maybe? I've used PostShot before and I understand it's the easier option, but is there any alternative? Thanks.
- 高赞评论(原声):
  - ▲15 "It's 34 quid a month. That's quite a lot for hobby use."
  - ▲12 "The best workflow is colmap, then Brush !"
  - ▲11 "Lichtfeld Studio and Brush are great alternatives."
  - ▲7 "It's a school project. I'd rather have the students generate their own splats rather than me doing it for them. And the school won't pay for a dozen licences, and students won't pay for it either. I just wanted to know if there was alternatives."
  - ▲7 "It's a subscription though, if it was a yearly release or one time purchase it'd be a different story"
  - ▲6 "COLMAP or GLOMAP and then Brush or Lichtfeld Studio. This might help: https://packet39.com/blog/a-primer-on-gaussian-splats/"
  - ▲3 "I find it quite hard to pay like 50usd pm for something i just use for fun projects and make no money, personally (yes im aware of the indie subscription but its missing important things i need)"
  - ▲2 "Fuck the camera controls and UI are terrible in Postshot. Can't even change the hotkeysi."

## [r/GaussianSplatting] Gsplat all-in-one GUI for Mac Silicon
- url: https://reddit.com/r/GaussianSplatting/comments/1q430m5/gsplat_allinone_gui_for_mac_silicon/
- score: ▲87 · 70评论 · date: 2026-01-04
- 楼主原声: Hey everyone, I wanted to share a tool I built to scratch my own itch (vibe coding). I wasn't really planning on sharing this, but I figured it might interest others. I'm a filmmaker working on a documentary and I needed a reliable way to process Gaussian Splats locally on my Mac without juggling ten terminal windows. I'm not a professional developer, so i used Gemini pro 3 to make a clear and quick GUI for all the tools i was using. It is a simplified, all-in-one GUI designed specifically for Apple Silicon. It automates the messy parts of the pipeline.
- 高赞评论(原声):
  - ▲6 "I think we'll be exceeding PostShot quality and ease soon with just open source projects stacked together like legos and tied together with interfaces like this. The amount of research and new breakthroughs in this segment are wild."
  - ▲5 "Great job, thanks a lot for sharing that ! I will give it a try soon ! It is very appreciated 🙌"
  - ▲4 "This is great. I did my own little vibe coding session to get Facebook's VGGT working on my PC with a 5090 (basically a stupidly fast version of Colmap) and it made the entire process so much easier. They kind of abandoned that project and getting it working was a nightmare. Offloaded the task to Opencode and GLM 4.7 and it went through a hilariously complex troubleshooting and editing workflow that would have taken me a month in like an hour. Colmap on large datasets was taking an insane amount of time, with VGGT it was giving me a densely mapped 3d model on the same data in like 4 minutes."
  - ▲3 "This is amazing man! In a same boat here and have been dreading the terminals workflow as it seems so inefficient. Is m4 out of the question or did you just forget to add it in the brackets?"
  - ▲3 "Thanks so much for this integrator! I just tried running this Gaussian Splattering training on a 4K video with my M4 Max Macbook Pro, and it's working perfectly. I'm not sure how this speed compares to others, but it's up and running! Really amazed by how it can run on Apple's GPU!"
  - ▲2 "Ffmpeg, colmap, & brush is the same workflow I use, with colmap being the problem child. Slow and often bad results which confuse brush."
  - ▲2 "Hey, im getting the following error during install: CMake Error ... ld: library 'omp' not found ... ❌ Auto-install failed for glomap: Command ... returned non-zero exit status 1. And then it still starts, but I get an error message when trying to run it: Échec extraction features. Any Advice?"

## [r/GaussianSplatting] Built a COLMAP → 3DGS pipeline for home interiors — looking for faster alternatives at both stages
- url: https://reddit.com/r/GaussianSplatting/comments/1snq9do/built_a_colmap_3dgs_pipeline_for_home_interiors/
- score: ▲6 · 20评论 · date: 2026-04-17
- 楼主原声: I've been putting together a full pipeline for capturing home interiors and turning them into 3D Gaussian Splats. The current setup is: 1. Extract frames from video 2. Run COLMAP for camera tracking / SfM 3. Feed the sparse reconstruction into a 3DGS training model. I've tested nerfstudio's splatfacto and a few others. The pipeline works, but both stages are painfully slow for a real world use case. Even on a cheaper dedicated server.
- 高赞评论(原声):
  - ▲8 "Nothing beats the quality of a successful colmap alignment. The second best alignment is realityscan. But colmap has so many hidden things that you can dial in to make perfect for your setup. Almost nobody talks about their lens variations. I.e. pinhole, opencv, etc."
  - ▲3 "RealityScan. I like it better than COLMAP, etc."
  - ▲2 "Newest versions of colmap have glomap built in which has GPU support for faster reconstruction and matching. Depending on the card you have it might be annoying to get working. Took all day to get it working on my 5080. I use a program called Sharp Frames to extract video frames. Colmap for SfM. Litchfield studio for splat training"
  - ▲2 "It all depends on the number of images and the resolution you are processing them on. Generally a 4K image is more than enough to produce good splats; JPG compressed images perform decently at nearly 1/4 size of PNG. Smaller sizes tend to be much faster and more stable in the training. GLOMAP is significantly faster than COLMAP when the image count increases (500+images)... For COLMAP, limit your sift features and use the vocab tree matcher to speed up feature matching."
  - ▲2 "Colmap > Brush. What's your next question?"
  - ▲1 "You could try VGGT or FastVGGT or a variation thereof as an alternative to colmap that can run quite fast. Ive been working on using Fast VGGT into GSplat to do splatting on an Nvidia Thor. I've gotten good results on benchmark datasets in about 15 minutes from beginning to end."
  - ▲1 "Use something like pano2room. Equirectangular panorama to 3d gaussian splat. Works great for interiors. Alt you could try Mast3r or Smas3r."

## [r/GaussianSplatting] SuperSplat moves to WebGPU for huge performance gains
- url: https://reddit.com/r/GaussianSplatting/comments/1tvptue/supersplat_moves_to_webgpu_for_huge_performance/
- score: ▲667 · 43评论 · date: 2026-06-03
- 楼主原声: We just shipped two big upgrades to SuperSplat, your free and open-source platform for 3DGS. Sharing the technical details here since I think this crowd cares about the *how*, not just the *what*. 1. A compute-based WebGPU renderer. Instead of sorting splats on a CPU worker thread, the new renderer moves the heavy lifting onto compute shaders: cull invisible splats, project the rest, sort them with a fast GPU radix sort.
- 高赞评论(原声):
  - ▲9 "I still have to write XR version of this new renderer .. starting now."
  - ▲8 "Thanks 😊💪🏼"
  - ▲8 "How does it perform in VisionPro? I'm hoping for a feewww more frames."
  - ▲3 "Amazing work! Can't believe how performant these are on low end / old devices."
  - ▲3 "Just curious how much of the performance gain is due to webgpu and how much due to LOD"
  - ▲3 "Man, the world of gaussian splatting has been popping off like crazy lately. Very cool stuff"
  - ▲3 "Thank you as always!! WebGpu has already been integrated into StorySplat a few weeks ago and auto lod generation from a ply will have to be next on the list! You guys rock!"
  - ▲2 "How are you handling the transition between well-observed and poorly-observed regions? That's usually where I see the most artifacts in my own captures."

> 采集缺口: discover_subreddits 对"Gaussian Splatting / 3DGS / 3D重建"多次检索均只返回 peripheral 低置信结果(未见 r/GaussianSplatting 本体),已按规则改用更专业词重试仍无效后,改为对话题点名的 r/GaussianSplatting 与置信度最高的 r/photogrammetry 直接 search_subreddit。所引 url 全部为工具返回的真实 permalink。
