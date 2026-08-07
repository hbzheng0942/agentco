---
kind: community_raw
platform: reddit
topic: "r/GaussianSplatting LingBot-Map 单手机实时3D重建 真伪与上手体验"
fetch_ts: 2026-08-07T00:04:22+00:00
content_hash: 3e74b9a66d9154d7
project: default
model: ds-chat
trace: traces/reddit_deep/20260807/r-gaussiansplatting-lingbot-map-单手机实时3d重.json
source_urls:
  - https://reddit.com/r/GaussianSplatting/comments/1rwi7h7/splatcam_free_gaussian_splatting_with_iphone_lidar/
  - https://reddit.com/r/GaussianSplatting/comments/1sn8o0l/lingbotmap_streaming_3d_reconstruction_with/
  - https://reddit.com/r/GaussianSplatting/comments/1szy7bm/iphone_app_with_guided_capture_for_high_quality/
  - https://reddit.com/r/GaussianSplatting/comments/1tmo22x/lidar_camera/
  - https://reddit.com/r/GaussianSplatting/comments/1tqo3hb/can_the_lidar_on_an_iphone_achieve_realtime_4dgs/
  - https://reddit.com/r/GaussianSplatting/comments/1uvusjg/built_an_ondevice_3dgs_scanner_for_iphone_with/
---

# 社区原声:reddit / r/GaussianSplatting LingBot-Map 单手机实时3D重建 真伪与上手体验

> reddit-research-mcp 深潜采集(ds-chat 忠实转录,未分析)。**原声在高赞评论里**;digester 蒸馏时逐条痛点回指具体评论(带▲赞数),交叉验证,勿把评论区综合成一句。

## [r/GaussianSplatting] LingBot-Map: Streaming 3D Reconstruction with Geometric Context Transformer
- url: https://reddit.com/r/GaussianSplatting/comments/1sn8o0l/lingbotmap_streaming_3d_reconstruction_with/
- score: ▲3 · 4评论 · date: 2026-04-16
- 楼主原声: (仅标题,外链 https://technology.robbyant.com/lingbot-map)
- 高赞评论(原声):
  - ▲3 "Read the paper."
  - ▲1 "Reddit is for linking to things. That's how it's generally been used and what it was designed to do. If the link itself is informative then there's no need to add text. If people don't like the content - that's what the voting buttons are for."
  - ▲-1 "Hi there — thanks for your submission! Could you please edit your post to include more context or additional details? Posts with minimal information or just a link tend to receive less engagement, as most users are less likely to click through without some explanation."

## [r/GaussianSplatting] Can the LiDAR on an iPhone achieve real-time 4DGS?
- url: https://reddit.com/r/GaussianSplatting/comments/1tqo3hb/can_the_lidar_on_an_iphone_achieve_realtime_4dgs/
- score: ▲13 · 23评论 · date: 2026-05-29
- 楼主原声: (仅标题,视频帖)
- 高赞评论(原声):
  - ▲11 "I don't know if you can really call this 4DGS, it looks more like just a point cloud / voxelated depth-displaced video. Neat, though!"
  - ▲6 "So what is the gaussian splat part in this? It looks like a video with z depth applied to it to stretch it in 3d."
  - ▲5 "This is not gaussian splatting whatsoever. Its just a video with depthmap. "
  - ▲3 "SHARP somehow convinced people that monocular view synthesis is actually 4DGS, when it's not even 3DGS - you can do this exact same thing with depth maps and triangles."
  - ▲3 "Are you actually capturing from multiple viewpoints or just adding the LiDAR depth to the video?"

## [r/GaussianSplatting] Built an on-device 3DGS scanner for iPhone with msplat
- url: https://reddit.com/r/GaussianSplatting/comments/1uvusjg/built_an_ondevice_3dgs_scanner_for_iphone_with/
- score: ▲28 · 39评论 · date: 2026-07-14
- 楼主原声: "I saw the recent post about training 3D Gaussian Splats directly on an iPhone and realized we've been building something similar in **Voxelio**, using almost the same stack:\n\n* SwiftUI and ARKit for capture\n* msplat for on-device 3DGS training\n* MetalSplatter for real-time rendering\n* XcodeGen for the iOS project\n\nThe entire pipeline runs locally on the iPhone and already works surprisingly well for smaller scenes…"
- 高赞评论(原声):
  - ▲3 "Looks cool  but no lifetime option? How does this compare with Scaniverse?"
  - ▲3 "Please can I request a feature?\n\nA wigglegram mode, where the scene just moves left and right!"
  - ▲2 "Isn't this the app called \"memo\" with some UI / text edits? Same capture UX :)  \nhttps://github.com/frs0n/memo-app  \n\nI'm also working on a very similar app and have recently switched to implementing msplat in it."
  - ▲2 "Any plans for android?"
  - ▲2 "Hey! Rayan here, the developper of msplat. Really pumped to see people are using my library and building apps on top of it."

## [r/GaussianSplatting] Splatcam: (Free) Gaussian Splatting with iPhone LiDAR
- url: https://reddit.com/r/GaussianSplatting/comments/1rwi7h7/splatcam_free_gaussian_splatting_with_iphone_lidar/
- score: ▲141 · 36评论 · date: 2026-03-17
- 楼主原声: "My initial foray into Gaussian Splatting tools, [Gauss Cannon](https://github.com/keshmirian/gauss-cannon), was about making it easy to get synthetic Blender scenes into 3DGS. SplatCam is the other half, doing the same thing for the real world. Point your iPhone at a scene, walk around it, and get a nerfstudio-format package (transforms.json + images + PLY) with no COLMAP step. So, it fits right into LichtFeld Studio, Postshot, and other tools!\n\nSplatcam uses the iPhone's ARKit LiDAR-backed depth maps to build the seed point cloud directly at capture time — confidence-filtered, RGB-colored, no feature matching or triangulation…"
- 高赞评论(原声):
  - ▲12 "Meta out. Indie devs in! Congratulations!!"
  - ▲8 "Yeah! That's the whole idea. Since the iPhone already knows roughly where it is (thanks to ARKit) we can use this to know where each picture is taken. With the LiDAR depth sensor we can generate a nice point cloud too, so with those together we already have all we need to start splatting! COLMAP doesn't have any of this information, only the images, so the process to determine it from only those is a lot more involved."
  - ▲8 "Thanks! Yes, Scaniverse is definitely in this space too. My goal is to allow users to use desktop programs like LichtFeld Studio to be able to customize and optimize the way the splat is processed, trim the point cloud, etc, and also to be able to use new techniques that are likely to show up more quickly in open-source projects (eg: IGS+ and PPISP are already in LichtFeld). Scaniverse is absolutely a fantastic product if you just want to scan-and-share, though!"
  - ▲3 "Great integration! My only thought is the similarity to the existing Scaniverse app. Whats the difference here? Scaniverse is designed for user friendliness and map based uploads. Does this give greater power user control maybe? Im all for more ways to splat, just didnt see any mention of Scaniverse in your post and I think comparison should be addressed."
  - ▲3 "How is it possible that we can scip the Colmap process ? Normally this step took 30 minutes or more on my MacBook "

## [r/GaussianSplatting] iPhone app with guided capture for high quality splats
- url: https://reddit.com/r/GaussianSplatting/comments/1szy7bm/iphone_app_with_guided_capture_for_high_quality/
- score: ▲245 · 51评论 · date: 2026-04-30
- 楼主原声: "Hey everyone,\n\nI've been working on a companion app to Spatial Studio called Spatial Lens. The idea was to make the capture process for high-quality 3D spaces as simple as taking a video on your phone.\n\nI built this to be a \"one-tap\" experience for anyone who wants to skip the technical setup and just get a clean result. Spatial Lens is built specifically for the iPhone Pro, using the LiDAR sensor to handle the heavy lifting. It automates the entire journey from \"scanning a room\" to \"exploring a splat tour\" so the process is completely seamless…"
- 高赞评论(原声):
  - ▲18 "Spatial Lens (capture app):  \nhttps://apps.apple.com/in/app/spatial-lens-real-horizons/id6762635917\n\nSpatial Studio (processing + tour creation):  \nhttps://realhorizons.ai/\n\nJust a heads up,.,the app is part of a full pipeline. Capture happens on Spatial Lens, but splat generation + tour building runs through Spatial Studio.\n\nIf you give it a try, I'd really appreciate any feedback. Thank youu"
  - ▲9 "Nice - is there a link to try it ?"
  - ▲5 "I can tell this is vibe coded from a mile away, the icons give it away. I downloaded it crashed then asked me to pay. Why would i pay for AI slop?"
  - ▲5 "First scan the app crashed on an iphone pro max 15, second scan it asks for credits, it doesn't have enough credits to process... first time user"
  - ▲5 "I'm trying to access it from Euriope but it says \"This app is currently not available in your country or region.\" :("

## [r/GaussianSplatting] LiDAR + camera ?
- url: https://reddit.com/r/GaussianSplatting/comments/1tmo22x/lidar_camera/
- score: ▲9 · 15评论 · date: 2026-05-24
- 楼主原声: "It's been about 2/3 months since I discovered Gaussian Splatting.  \nSince then, I've been able to experiment a lot on my own thanks to YouTube and Reddit. I've gotten some incredible results… but I've also had some major disappointments. I know I'm just getting started and that I still have a lot to learn.\n\nStill, what frustrates me the most right now is the inconsistency of the results.  \nPart of the problem surely comes from the software I'm using and the settings, but I feel like, most of the time, the real issue stems mainly from the inputs.\n\nFor now, I'm working exclusively with cameras (iPhone and Insta360 X5), and certain scenes are really complicated: uniform walls, floors with little detail, dark  dimly lit environments…"
- 高赞评论(原声):
  - ▲9 "I don't have this hardware but this looks doable: https://github.com/hku-mars/LIV_handhold_2"
  - ▲5 "iPhone LiDAR its about an order of magnitude lower precision and resolution than you'd need for it to be helpful. It suffers from a lot of sensor drift. A few of the splat apps take LiDAR snapshots to help ballpark the scene scale within 5% accuracy, but in many cases like when doing reflective surfaces it can actually negatively impact the results so its not directly used for reconstruction. Higher end systems like Xgrids are another league in terms of hardware and you can't replicate that with iPhone."
  - ▲3 "Waste of time. the Iphone depth sensor (it's not actually a LiDAR) isn't up for this task."
  - ▲2 "Do you have a pro model iPhone? There's a few apps that use the lidar."

> 采集缺口:discover_subreddits 全 peripheral(0.28–0.69),r/GaussianSplatting 未出现在发现结果里,系直接按话题点名定位;photogrammetry 子版搜索返回结果与话题相关性低,未选入。
