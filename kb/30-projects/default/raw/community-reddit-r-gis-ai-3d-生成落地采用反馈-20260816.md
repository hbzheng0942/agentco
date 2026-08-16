---
kind: community_raw
platform: reddit
topic: "r/gis AI 3D 生成落地采用反馈"
fetch_ts: 2026-08-16T00:05:01+00:00
content_hash: ec556ffa5518e516
project: default
model: ds-chat
trace: traces/reddit_deep/20260816/r-gis-ai-3d-生成落地采用反馈.json
source_urls:
  - https://reddit.com/r/LiDAR/comments/11mwsym/making_3d_point_cloud_using_generative_ai_and/
  - https://reddit.com/r/gis/comments/1l1olbw/esri_using_ai_art_ugh/
  - https://reddit.com/r/gis/comments/1o9t2r7/is_anyone_doing_anything_interesting_with_ai/
  - https://reddit.com/r/gis/comments/1td62b4/ai_edit_models_seems_to_works_pretty_well_with/
  - https://reddit.com/r/photogrammetry/comments/1arq85p/openais_sora_video_generation_ai_produces_videos/
  - https://reddit.com/r/photogrammetry/comments/1vb1boz/ai_powered_photogrammetry_delighting/
---

# 社区原声:reddit / r/gis AI 3D 生成落地采用反馈

> reddit-research-mcp 深潜采集(ds-chat 忠实转录,未分析)。**原声在高赞评论里**;digester 蒸馏时逐条痛点回指具体评论(带▲赞数),交叉验证,勿把评论区综合成一句。

## [r/gis] Is anyone doing anything interesting with AI?
- url: https://reddit.com/r/gis/comments/1o9t2r7/is_anyone_doing_anything_interesting_with_ai/
- score: ▲35 · 72评论 · date: 2025-10-18
- 楼主原声: AI is being used in a lot of industries, but I can't imagine it being used much for GIS. Correct me if I'm wrong; has anyone found any interesting use for AI in any form? I.e. A large language model like GPT, a visual model, etc. I did see one interesting thing where you can draw an arrow on a map and it'll generate a street view image from that position and direction (https://x.com/tokumin/status/1960583251460022626)… One thing I wish existed: I often have to take a map screenshot / photo / scan with a boundary on it and create a GeoJSON polygon from it…
- 高赞评论(原声):
  - ▲77 "I've been using AI in GIS/remote sensing for many years in the Agricultural sector. I started working in 2002, and then we used AI to do crop recognition on specific area's where images could be obtained. With sentinel 1 and 2 becoming available in 2017 this was expanded to nation-wide recognition as well as some other topics, some of them using AI. Since 2018 I started using deep neural networks to segment different types of orthoreferenced maps (aerial images, historic maps, DHM's) to create vector maps of trees, sealed surfaces, ditches, water courses, fruit trees,... So yes, AI has been a great tool in GIS/remote sensing for a long time already..."
  - ▲39 "Same. We were using "AI" in 1994 to determine deforested areas."
  - ▲27 "Well at a recent ESRI conference they banged on about AI in literally every presentation. They're going to be rolling out AI assistants to help with coding and advising what you should be doing at each step sorta thing, kinda like copilot. Then they're going to be launching AI agents, which will eventually just replace us, and allow non GIS people to do our jobs ... I use AI a lot on my work tbh. Ive recently been using AI to scan a large text field on a datast and extract information into a load of different fields."
  - ▲27 "Knowing ESRI will do AI half ass baked like anything else they do and kill further development in 2 Years. Dont worry about GIS jobs."
  - ▲23 "It'll continue to be a stalemate between an unstoppable object vs immovable force. AI allowing "non-GIS people to do our jobs" versus employers requiring/preferring literally every GIS-related skill/certification to even be considered to be considered to be considered to be considered to get a call back for the next round of interviews for a 56k/yr position that depends on a grant that depends on who's in office."
  - ▲22 "I use Claude almost every day to help me with sql querries in postgis. (Creation, correction, optimisation)"

## [r/gis] ESRI Using AI Art - ugh
- url: https://reddit.com/r/gis/comments/1l1olbw/esri_using_ai_art_ugh/
- score: ▲493 · 86评论 · date: 2025-06-02
- 楼主原声: ESRI ArcGIS Online Team sends me a regular email and today I got one highlighting how now you can easily add commercial satellite imagery to projects on AGOL. When you click on that link you get to the article where it's obvious that ESRI used AI to generate an image. As a user, and a human, this doesn't sit right with me. Maybe it sits less right because I just listened to a lecture by Rick Roderick on the postmodern world we now find ourselves in. In my opinion, the core mission of GIS is to show the closest approximation to the truth as possible and ESRI should lead by example on this…
- 高赞评论(原声):
  - ▲347 "why the hell would they get an AI to create a fake version of the service they're trying to promote. Is it so difficult to just take a photo of someone at a computer??"
  - ▲65 "In the spirit of what you're saying here, I feel I should point out that AI is tremendously power-hungry—to the extent that Microsoft is planning a revival of the Three Mile Island nuclear plant, and Musk's AI data center in Memphis (powered by natural gas) is spewing so much pollution into black communities there that the NAACP has filed an emergency suit to shut it down. AI truly is an incredible tool, and we should take full advantages of its utility in applications like GIS…"
  - ▲58 "I mean, technically a lot more expensive to do the real photo. It's like the difference between an unpaid marketing intern typing a prompt into ChatGPT free version for the image, and getting legal to provide a release form, hiring a model, getting UI cleared, setting up the scene, bringing in lighting, makeup and wardrobe, a pro photographer plus assists, then having someone do post to color correct, Greek, and generally crop/edit for print."
  - ▲43 "Looks like they pulled that keyboard out of a fire"
  - ▲30 "They have or had a full time photographer on staff and an amazing graphics group who can make beautiful images from those photos. 🤷🏻‍♀️"
  - ▲16 "As our society drifts further and further away from the truth, and as it becomes more and more difficult to discern reality from fantasy it will become paramount that tools will need to be available to help us identify fact from fiction. GIS is but one of those tools. AI certainly has its place in GIS and society however, ESRI will be overlooking an opportunity if it doesn't do what it can to reassure it's users of its reality based information…"

## [r/gis] AI Edit models seems to works pretty well with aerial imagery. Here's an example with the "AI edit" plugin in QGIS to do a quick map from an orthophoto
- url: https://reddit.com/r/gis/comments/1td62b4/ai_edit_models_seems_to_works_pretty_well_with/
- score: ▲64 · 57评论 · date: 2026-05-14
- 楼主原声: (仅标题)
- 高赞评论(原声):
  - ▲179 "the problem is that as long as it isn't perfect, you'll be spending ungodly amounts of time identifying mistakes and fixing them. Which in my experience is the biggest problem with AI outputs in general."
  - ▲68 "What's the difference of this and traditional machine learning based imagery interpretation"
  - ▲49 "A pseudo-meaningful map that impresses your boss and is a headache for you."
  - ▲40 "You made this plugin and I assume are using AI to post it to all the subreddits too?"
  - ▲35 "Are these supposed to be buildings?"
  - ▲30 "Yeah, but that's GIS in a nutshell. At least there's the potential with more freedoms for product creation."
  - ▲26 "Yeah it might be useful for rough analysis, but the problem with that is that it isn't reproducible, which is another problem with AI. Someone using the exact same method will get slightly different results."

## [r/photogrammetry] OpenAI's Sora Video Generation AI produces videos so good that you can make 3D models from them
- url: https://reddit.com/r/photogrammetry/comments/1arq85p/openais_sora_video_generation_ai_produces_videos/
- score: ▲138 · 33评论 · date: 2024-02-15
- 楼主原声: (仅标题)
- 高赞评论(原声):
  - ▲28 "Note that this is just an example video from their page and it is NOT even meant to be used for photogrammetry. High quality AI 3D model generation can't be far away."
  - ▲19 "I used an online converter tool and paid no attention to optimizing the process. I just threw everything into metashape and it worked. To me that is VERY surprising. Yesterday there was no AI remotely capable of this."
  - ▲14 "The city video showcased another angle of this matter. The spatial integrity was non existent even for naked eye."
  - ▲3 "The ability to generate consistent 360 panoramic shots, if present with Sora, is a killer combo with gaussian splatting."
  - ▲2 "Very interesting indeed. Looks like this would be a great way to simulate data sets for large terrain scans. As someone who can't afford a drone to scan large objects and landscapes, this isn't a bad alternative if the footage is consistent enough as displayed here."

## [r/photogrammetry] AI powered photogrammetry De-lighting
- url: https://reddit.com/r/photogrammetry/comments/1vb1boz/ai_powered_photogrammetry_delighting/
- score: ▲210 · 43评论 · date: 2026-07-30
- 楼主原声: I always had trouble with removing environmental lighting, and because I can't afford cross-polarization I had to stay with the digital tools. I didn't like any of the De-lighting tools on the market, so I built one from scratch using a Neural Network. I got a lot of cross-polarized scans online and baked back environmental lighting, then gave it to the network with some geometry maps like object space normal and ambient occlusion… It generates outputs in seconds. Though not every type of 3D model works, I still have to understand it. Its not perfect, but for 5 days and a limited dataset, and the fact that I never trained a neural net its promising…
- 高赞评论(原声):
  - ▲25 "There are shitloads of amazing uses of AI. They're just completely overwhelmed by slop."
  - ▲24 "Sure. I got like 36 different models from an online site. Because they use cross-polarization for scanning, which is ground-truth albedo they were the perfect targets. Then i created 27 different environmental light variations for each model and assigned geometry maps that anybody can bake beside their input albedo. The network was trained to process 2048x2048 textures in 1024x1024 tiles. It's a dual-encoder U-Net architecture trained in PyTorch…"
  - ▲12 "Neato"
  - ▲11 "Could you share more infos? This is really interesting"
  - ▲11 "A rare good use of AI"
  - ▲4 "From that single example your results looks like they're about as good as the best de-lighting solutions out there. The bar wasn't very high to begin with considering they all kinda suck but still a very impressive one to clear…"

## [r/LiDAR] Making 3D Point Cloud using Generative AI and Blender
- url: https://reddit.com/r/LiDAR/comments/11mwsym/making_3d_point_cloud_using_generative_ai_and/
- score: ▲5 · 4评论 · date: 2023-03-09
- 楼主原声: https://youtu.be/kVT5G7e-n-o
- 高赞评论(原声):
  - ▲2 "You can just send prompts from a web ui or terminal to stability ai, run the colab notebook (linked in the video) and schedule a blender run"
  - ▲1 "Interesting! Any way to automate this?"
  - ▲1 "Yeah. That would be a really cool thing to have as it can then possibly used in ML scenarios as well."
