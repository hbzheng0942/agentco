---
kind: community_raw
platform: reddit
topic: "r/robotics spatial intelligence robot training"
fetch_ts: 2026-07-24T00:04:57+00:00
content_hash: 0ad196678885eb98
project: default
model: ds-chat
trace: traces/reddit_deep/20260724/r-robotics-spatial-intelligence-robot-tr.json
source_urls:
  - https://reddit.com/r/computervision/comments/1t9tomn/odyseus_spatial_vlm_projecting_2d_reasoning_into/
  - https://reddit.com/r/reinforcementlearning/comments/1ro7xen/people_training_rl_policies_for_real_robots_whats/
  - https://reddit.com/r/robotics/comments/1nf90ku/roboticists_im_stuck_anyone_else_battling_the/
  - https://reddit.com/r/robotics/comments/1oi0lil/researchers_at_beijing_academy_of_artificial/
  - https://reddit.com/r/robotics/comments/1sgou6e/simtoreal_with_spiking_neurons_on_a_100_quadruped/
  - https://reddit.com/r/robotics/comments/1szufp9/sim_perfect_backflip_real_perfect_faceplant/
---

# 社区原声:reddit / r/robotics spatial intelligence robot training

> reddit-research-mcp 深潜采集(ds-chat 忠实转录,未分析)。**原声在高赞评论里**;digester 蒸馏时逐条痛点回指具体评论(带▲赞数),交叉验证,勿把评论区综合成一句。

## [r/robotics] Researchers at Beijing Academy of Artificial Intelligence (BAAI) trained a Unitree G1 to pull a 1,400 kg car
- url: https://reddit.com/r/robotics/comments/1oi0lil/researchers_at_beijing_academy_of_artificial/
- score: ▲650 · 41评论 · date: 2025-10-28
- 楼主原声: From BAAI (Beijing Academy of Artificial Intelligence) on 𝕏: [link]
- 高赞评论(原声):
  - ▲130 "Isn’t this leaked footage of teslas new Autopilot?"
    - ▲7 "I mean if cars are the evolution of horse drawn carriages, maybe self driving cars will be the evolution of robot drawn carriages. Maybe they release a model thats just 4 large Boston dynamics type dogs that pull a cart."
  - ▲44 "Poor little guy looks like he's about to 💩 himself"
  - ▲36 "Probably doesn't know how to brake the car, that's why they have a driver there."
  - ▲27 "I mean, tbh it's not that hard to get a car rolling. It's not like you're vertically lifting 1400kg."
    - ▲9 "It's so easy! On a smooth flat surface like that a 7 yo child could push it"
      - ▲9 "Yep! But the real cool thing here is getting it to do the proper motions without falling. This is one of those things which is really damn easy for humans to do without even thinking, but which requires surprisingly complex control algorithms to do robotically."
  - ▲24 "Yeah, I wanna see the video prior to this where there was no driver and the robot got run over"
  - ▲15 "Yeah I'm sure they built the whole parking garage out of level.."
  - ▲14 "This video isn't from Unitree"
  - ▲6 "The best way you can look at it, is to go on youtube and watch youtubers who actually bought one, and see what they are using them for, that will give you an real idea what they can do, and not those animated superhero movies you see from unitree."
    - ▲5 "Anyways, they can do this, but not with unitree software that you see youtubers using. To do this you need to write your own software and train your own models, which is why you only see these kinds of videos from universities."

## [r/robotics] sim: perfect backflip. real: perfect faceplant
- url: https://reddit.com/r/robotics/comments/1szufp9/sim_perfect_backflip_real_perfect_faceplant/
- score: ▲193 · 8评论 · date: 2026-04-29
- 楼主原声: the flip itself actually goes through, full rotation. but the landing... face meets floor every time lol. dug into it for a while. found that the damping in our sim was too high, so the joints in simulation were way smoother than the real ones. the policy just never had to deal with that kind of impact force on landing. working on dialing it down to match actual hardware now. also been getting a ton of questions lately about how we do RL training, sim2real workflow, domain randomization, all that. finally put together a longer writeup covering what we've tried and where we messed up.
- 高赞评论(原声):
  - ▲18 "Pretty good if you ask me 😄"
  - ▲15 "Your robot is doing a standing flip, while the sim starts moving backwards imparting momentum. Beyond this the carpet you are on might be a lot more friction than you expect."
  - ▲2 "[removed]"
  - ▲2 "Do you mind sharing what motors you're using for the drive and arms?"
    - ▲1 "we disign the motor by ourselves!"

## [r/robotics] Roboticists, I'm stuck. Anyone else battling the chaos around robot training?
- url: https://reddit.com/r/robotics/comments/1nf90ku/roboticists_im_stuck_anyone_else_battling_the/
- score: ▲43 · 7评论 · date: 2025-09-12
- 楼主原声: Hey folks, I've been training VLAs for robotic arms and perception tasks. Lately, I'm spending more time on issues around the robot than the robot itself. Policies perform well in simulation but fail in the real world, data pipelines lack consistency, and edge cases reduce reliability. Sim to Real Gap: Policies are solid after domain randomization in simulation. On real hardware, success rates drop due to factors like vibrations, lighting variations, or calibration issues. How do you address this without repeated hardware testing? Data and Replay Sprawl: TFDS datasets vary wildly by modality, and there's zero consistency. It's like herding cats—any tips for standardizing this mess? Long-Tail Failures: Most demos run smooth, but those edge cases wreck reliability. What's your go-to for hunting these down systematically? Edge Deployment Reality: For Jetson-class hardware, there are challenges with model size, memory, and latency. Evaluation That Predicts Real: Benchmarking policies is difficult.
- 高赞评论(原声):
  - ▲37 "[removed]"
    - ▲3 "On the second point about determinism, it is actually rare to meet a roboticist that understands that without it they will hit a wall. If it doesn't work in theory, it won't work in practice: You loose reproducibility so forget about edge cases, then tackling the long tail then safety."
    - ▲3 "Reproducibility is definitely a major problem. Even with a temp=0, rounding errors make it impossible to reproduce the actions."
    - ▲2 "I work with classic programmed robots myself. I am curious about deterministic control though. We currently use RT optimised models for segmentation, detection, etc and then use their results to perform some action by the robot. We make sure that these models run at a frequency that the worst case scenario is still faster than the control loop of the robot hardware."
  - ▲2 "Sim to real is extremely difficult. Typically I think the pipeline goes 1. Try in simulation to make sure the model/architecture works in general on a task of the same complexity. 2. Completely retrain on real robot. Unless you have a hyper-realistic simulator (which some companies are trying to build, e.g. Nvidia, Waab), you really can't replicate all the real-world visual noise."
  - ▲1 "How much have you trained the robot in tasks in the real world? I think that the best way to handle the gap between the real world and the sim is to train it on small interactions in the real world"

## [r/robotics] Sim-to-Real with spiking neurons on a €100 quadruped — on-device learning at 50Hz on Raspberry Pi 4
- url: https://reddit.com/r/robotics/comments/1sgou6e/simtoreal_with_spiking_neurons_on_a_100_quadruped/
- score: ▲41 · 18评论 · date: 2026-04-08
- 楼主原声: I've been working on biologically grounded locomotion control using spiking neural networks instead of conventional RL. The system runs on a Freenove Robot Dog Kit (FNK0050) with a Raspberry Pi 4. The approach: train an Izhikevich SNN in MuJoCo simulation using a custom MJCF model of the robot, then transfer the brain to real hardware where it continues learning with IMU feedback (MPU6050). A central pattern generator provides innate gait, and a competence gate gradually hands control to the SNN as it proves stable. Key result: brain persistence works — stop the robot, restart it days later, synaptic weights reload and it walks immediately without relearning. Honest limitation: spectral analysis shows the SNN learns conservative dampening rather than faster/better gaits. It makes movements smaller and more regular.
- 高赞评论(原声):
  - ▲4 "This is super cool. I'll have a deeper look soon. Question: the Izhikevich model can reproduce lots of different types of neuron firings (bursting, resonators, etc) - did you choose just one?"
    - ▲3 "Currently I'm using tonic spiking for all neurons — the simplest Izhikevich mode (a=0.02, b=0.2, c=-65, d=8). The architecture supports different firing types per neuron since each has its own (a,b,c,d) parameters, but I haven't explored mixing types yet. Chattering or phasic bursting in the motor output layer could produce more dynamic gait patterns — that's an interesting direction."
  - ▲3 "I'd love to hear a bit more about how the training works. Your description mentions no backprop, but I'm not familiar enough with spiking neurons to know what you'd replace that with."
    - ▲2 "Instead of backprop, the system uses R-STDP (reward-modulated spike-timing-dependent plasticity). It works like this: when a presynaptic neuron fires shortly before a postsynaptic neuron, that connection is marked as 'potentially useful.' But the weight only actually changes if a reward signal (dopamine) arrives. So the learning rule is: fire together + good outcome = stronger connection. Fire together + bad outcome = weaker connection. It's local in space and time — no global loss function, no gradient computation, no backward pass through the network. The practical difference: backprop needs to store activations, compute gradients, and update all weights globally. R-STDP updates weights locally at each synapse based only on the timing of the two connected neurons plus a scalar reward signal. That's why it runs on a Raspberry Pi at 50Hz — the computational cost is tiny compared to backprop."
  - ▲3 "This is so fucking cool. Thanks for sharing this."
  - ▲2 "What are the chances I worked on CPG many many years ago it was called the RunBot, I am now working on a quadruped called Sesame and I want to use the same approach but without sim2real only real. I like to see more people using bio-inspired principles instead of just RL the shit out of everything...."
    - ▲-1 "Why? It's clear that traditional transformer models work significantly better on the hardware that we have. A CPU or GPU isn't the same as a brain and I don't see any evidence that biologically inspired models offer any advantage (with the huge downside of being significantly less efficient)"
    - ▲2 "No-one will ever see any evidence if they stop trying things because they don't see any evidence. Sometimes investigations down unpromising looking avenues are the ones that turn out the real breakthroughs."
    - ▲2 "Have you even read the RunBot original publication we got that to work before we had GPUs, it was amazing work at the time, GPUs are still quite power hungry and so we should pursue alternative methods, you can implement CPGs on ASIC/FPA and will be extremely power efficient."
    - ▲2 "...The SNN isn't there for the label though. The cerebellar forward model actively corrects motor output during walking — climbing fiber error from real IMU, PF→PkC weights change on-device. The CPG does the walking, the SNN learns corrections on top. The 10-seed ablation shows it: SNN+Cerebellum does 45.15±0.67m vs CPG-only 40.73±6.14m — not just further but 9x lower variance."

## [r/reinforcementlearning] People training RL policies for real robots — what's the most painful part of your pipeline?
- url: https://reddit.com/r/reinforcementlearning/comments/1ro7xen/people_training_rl_policies_for_real_robots_whats/
- score: ▲32 · 8评论 · date: 2026-03-08
- 楼主原声: Hey, I've been going down the rabbit hole of sim-to-real RL and I'm trying to understand where the ACTUAL bottlenecks are for people doing this in practice (not just in papers). From what I've read, domain randomization and system identification help close the gap, but it seems like there's still a lot of pain around rare/adversarial scenarios that you can't really plan for in sim. For those of you actually deploying RL policies on physical robots: 1. What part of your workflow takes the most time or money? Is it data collection, sim setup, reward shaping, or something else entirely? 2. How do you handle edge cases before deployment? Do you just hope domain randomization covers it, or do you have a more systematic approach? 3. What's the biggest limitation of whatever sim stack you're using right now (Isaac, MuJoCo, etc.)?
- 高赞评论(原声):
  - ▲19 "You will probably not like the answer, though. The most painful part where most time is consumed with robots in practice is always the hardware, and the embedded software stack maintainability. Training and deploying RL policies is easy. Maintaining hardware, diagnosing hardware issues, repairing hardware, and maintaining the embedded software stack of companies like NVIDIA (jetson...), Google (coral...) and Intel (realsense...) who create useful embedded tool stacks and leave them to die the next year... is what is really annoying."
    - ▲2 "Ha honestly I kind of expected someone to say this. So the RL/training side is basically the 'easy' part and the real nightmare is everything around it? That's kind of humbling to hear as someone looking at this from the research side."
    - ▲2 "I am also a researcher, I have been doing RL/ML in a robotics and embedded systems lab for something like 7 years now. I have seen many newcomers in robot learning research complain that maintaining hardware 'should not be their job' as soon as they started touching real robots... Those companies stop updating and maintaining their SDKs soon after they release them. They also leave you stuck with outdated Linux-based OS's that they release and stop maintaining almost instantly (Jetpack for NVIDIA Jetson, Mendel OS for Google Coral...). The notable exception is Raspbian for Raspberry Pis."
  - ▲4 "Camera calibration. All of it. Eye in hand. Eye to hand. Distortion… etc"
    - ▲1 "Depends basically your whole system is a chain of errors… how static any element is determines if you tend towards continuous recalibration. E.g the limb lengths in your robot hardly change but I wasted a month trying to fix camera calibrations on a robot where the wrong calibration had been loaded for the robot. Did you know they think babies putting their foot on their mouths is a self calibration process… with RL there is so many areas that do not have calibration.. e.g how much does my grip slip on this surface or material…"
  - ▲1 "training time, it takes a lot of time to have meaningful result"

## [r/computervision] Odyseus - Spatial VLM : Projecting 2D reasoning into 3D outputs (open source repo)
- url: https://reddit.com/r/computervision/comments/1t9tomn/odyseus_spatial_vlm_projecting_2d_reasoning_into/
- score: ▲244 · 19评论 · date: 2026-05-11
- 楼主原声: So I've always argued that Physical AI for robotics need actionable outputs like 3D coordinates, not bullet points or nice paragraphs. So decided to experiment by combining a VLM with Monocular Depth Estimation, essentially projecting 2D reasoning into 3D, I called it Odyseus - Spatial VLM. Tech Stack: VLM: Qwen 3.6, Depth Estimation: Depth Anything 3 - Metric Large. Worked pretty well, figured to share.
- 高赞评论(原声):
  - ▲7 "Wtf is this black magic fuckery"
  - ▲8 "This is from my server logs running on an NVIDIA L4 with 46GiB Vram: [INFO] Processed Images Done taking 0.006s. [INFO] Model Forward Pass Done. Time: 12.35 seconds. Someone got Depth Anything 3 to run on a Jetson AGX Orin."
  - ▲3 "cool... so you can make lidar projection? based on image... how fast it run? can i run it in low spec hardware?"
  - ▲2 "This is actually a pretty interesting direction. One thing I've always felt is missing from current VLM systems for robotics is that they mostly output 'language about the world' rather than actionable spatial representations of the world."
  - ▲2 "Yep DA3-Metric-Large"
  - ▲2 "maybe use segment anything or yolo and project the results onto the depth frame. Alternatively depth frame to point cloud first, then use segmentation in PCL."
  - ▲1 "Yes you are correct is projecting the point, but your point is interesting about the possibility of fine tunning it to specific tasks"
  - ▲1 "Oh I see, you're perhaps using the VLM to place a dot point and then projecting that onto the scene created by the depth model."
  - ▲1 "Is its quality (for robotics) only as good as the depth model? You need very high precession I imagine for robotics to work in the real world."
    - ▲1 "Yep DA3 Metric is pretty good tho"
