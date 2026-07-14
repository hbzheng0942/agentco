---
kind: community_raw
platform: reddit
topic: "r/gamedev AI agent NPC 实践帖 2026"
fetch_ts: 2026-07-14T04:27:11+00:00
content_hash: 035970547eb5b7d9
project: gaming
model: ds-chat
trace: traces/reddit_deep/20260714/r-gamedev-ai-agent-npc-实践帖-2026.json
source_urls:
  - https://reddit.com/r/GameDevelopment/comments/1uapia1/npc_behavior_modeled_as_a_dynamical_system/
  - https://reddit.com/r/gamedev/comments/1ng0vnd/on_llms_and_gameplay/
  - https://reddit.com/r/gamedev/comments/1pe0ks3/a_second_attempt_at_explaining_collapse_aware_ai/
  - https://reddit.com/r/gamedev/comments/1qox8dp/the_use_of_ai_in_npcs_interactions/
  - https://reddit.com/r/gamedev/comments/1s1b852/dealing_with_llm_amnesia_in_rpgs_how_we_stopped/
  - https://reddit.com/r/gamedev/comments/1sggknd/how_do_you_prototype_npctonpc_behavior_before/
---

# 社区原声:reddit / r/gamedev AI agent NPC 实践帖 2026

> reddit-research-mcp 深潜采集(ds-chat 忠实转录,未分析)。**原声在高赞评论里**;digester 蒸馏时逐条痛点回指具体评论(带▲赞数),交叉验证,勿把评论区综合成一句。

## [r/gamedev] Dealing with LLM amnesia in RPGs: How we stopped our AI from forgetting the game state after 5 turns.

- url: https://reddit.com/r/gamedev/comments/1s1b852/dealing_with_llm_amnesia_in_rpgs_how_we_stopped/
- score: ▲0 · 20评论 · date: 2026-03-23
- 楼主原声: For the past few months, my friend and I have been building a text-based life sim, and we quickly ran into the biggest wall in AI gaming: context windows. If you just wrap a game around a chatbot, the AI eventually forgets the player's inventory, hallucinates dead NPCs back to life, and just in general completely loses the plot. We realized that for this to work, the narrative text could not be the source of truth. We needed an engine where actions made and developed always happen according to a timeline and are remembered so that past decisions can influence the future. Our solution was to completely decouple the simulation from the LLM...
- 高赞评论(原声):
  - ▲21 "Why are you putting game state in an LLM lol"
  - ▲9 "Bro just learn to code a state machine, it ain't that hard. Dude over here using an entire logging company to trim a bonsai."
  - ▲8 "Ditch the LLM. AI is not a way forward in gamedev."
  - ▲7 "I mean, it's an interesting experiment. But from what you are saying the conclusion seems to be that LLM isn't suitable to be used as a game engine. Which doesn't come as a surprise to be honest."
  - ▲7 "that doesn't seem optimized or even thought of game wise in any single way I can think of..."
  - ▲6 "AI is ruining our environment / AI data centers are creating medical issues for people / AI is can only steal from actual working folks / AI is being used by corpos to replace actual jobs / AI is a bubble that, when it pops is predicted to create a recession worse than x2 of the 2008 housing crisis / AI data centers are causing economic issues for towns/cities / Does none of this matter to you? Is your game more important than these issues?"

## [r/gamedev] A second attempt at explaining Collapse Aware AI (CAAI) NPC middleware, now with actual search-engine verification

- url: https://reddit.com/r/gamedev/comments/1pe0ks3/a_second_attempt_at_explaining_collapse_aware_ai/
- score: ▲0 · 21评论 · date: 2025-12-04
- 楼主原声: My first post about Collapse Aware AI (CAAI) months ago was removed shortly after i posted it... At the time i guess that was to be expected, the tech had zero public footprint, and it probably looked like AI slop or vaporware. Since then, things have changed... If you search "Collapse Aware AI NPCs" or "What does CAAI do for gaming?" on Bing or Google, you'll now get proper feature cards describing the middleware and its use cases in game development. (Not linking anything here to avoid self-promo flags, just telling you what appears.) This post is simply a follow-up with a clear explanation of what the system actually *does*, without hype or marketing language...
- 高赞评论(原声):
  - ▲7 "Something about this sounds a lot more difficult then just adding a fair variety of interactions yourself"
  - ▲6 "Still sounds as vaporware, search engine indexing is irrelevant. Show us research papers if it is applicable in reputable journals and conferences (sigraph etc). Personally that 'npc learns from history' sounds thick as bull crap."
  - ▲4 "Ah alright. I'm no AI expert so I just assume LLM is a base for most of it. But either way, were kinda circling back to my original comment. Why would I need all this stuff when it sounds like a few extra if-else statements would have the same result?"
  - ▲3 "> lots of interaction variants scales linearly / This also confuses me which make me believe I am talking to a bot. Linerly increase is a good thing actually but it is boring, complex interactions goes exponentially."
  - ▲3 "Okay, I would suggest to add this example to your original post, — it greatly showcase where/how system can be used. Thank you for sticking with me."
  - ▲1 "Randomizing between equally viable options has been a thing in NPC behavior for decades. What does this actually do thats new?"

## [r/gamedev] How do you prototype NPC-to-NPC behavior before implementing it?

- url: https://reddit.com/r/gamedev/comments/1sggknd/how_do_you_prototype_npctonpc_behavior_before/
- score: ▲0 · 13评论 · date: 2026-04-09
- 楼主原声: Working on a simulation game where NPCs have schedules, motivations, relationships. The hardest part isn't coding the behavior — it's knowing if the behavior will produce interesting emergent situations before you've written a line of it. Curious how others handle this. Do you just implement and iterate? Use spreadsheets? Write it out narratively? I've been experimenting with running AI agents with hidden agendas and asymmetric information — each agent only knows what they personally witnessed — and letting them simulate interactions. Helps me see failure points in character design before touching the codebase...
- 高赞评论(原声):
  - ▲2 "I've completely implemented it, multiple times over and the project failed. So I suggest not fully implementing the system. I mean, we implement it with graphics and models, so this wasn't really prototyped at all. I think if we would've sticked to capsules moving around, dragging boxes to build boxes with name labels on top of them and with no thoughts about performance or extendable code, this could've worked. Maybe."
  - ▲1 "Implement the core prototype, no visuals, no text, just some tags or keywords for designed actions/reactions... Make something like a logger which allows you to quickly see the outcomes and how they were reached. Run the simulation with the randomized scenarios for tons of iterations. Check the outcomes and whether they meet your 'interesting' criterias. Don't use AI for that, build a determenistic system - unless you're going to incorporate AI for the NPCs behavior normally."
  - ▲0 "LLMs talking to LLMs. How perverse."
  - ▲0 (comment by DehabAsmara) "We hit this wall on a faction-based sim. We focused on Utility AI for emergence, but realized that simulating only intent leads to chaos. The breakthrough came when we shifted from the NPC's 'brain' to the 'Social Physics' of the room. Try a 'Low-Fidelity Social Logic' layer. The Prom Week team used the 'Comme il Faut' (CiF) engine to manage 5,000+ 'social rules' that governed how interactions changed the state based on witnesses and norms."

## [r/gamedev] The use of AI in NPC's interactions.

- url: https://reddit.com/r/gamedev/comments/1qox8dp/the_use_of_ai_in_npcs_interactions/
- score: ▲0 · 19评论 · date: 2026-01-28
- 楼主原声: The other day I was watching the movie Her, with Joaquin Phoenix, and there's a scene where Theodore (Joaquin) and his AI partner are playing a video game and they interact with an NPC. The character is an AI that closely mimics a conscious being; it has a personality, mannerisms, and to progress in the game, you need to talk to it in a specific way. I've always liked imagining how this topic of NPC interaction in games would work in the future. Like, in terms of gameplay and game design, this specific aspect, in contrast to gameplay involving physical actions like fighting, has always been very interesting to me. A sort of 'Social Gameplay'...
- 高赞评论(原声):
  - ▲8 "I'm generally against AI in the current landscape for the various ethical reasons I'm sure you've heard before, mainly environmental but also for its socio-economic impact, which has been fairly severe. Ignoring that though, I still don't really like it. The problem is that LLMs are just unreliable. You can try as hard as you want to get them to say what you want, but it's impossible to lock them down to only interact in the way you want. Sure, you can have them act like the NPC in your game 90 or 96% of the time, but why would I want my NPCs to just go off the rails or say something completely incorrect or unrelated 5+% of the time?"
  - ▲8 "I refuse to believe that giving an AI free roam to say whatever it wants with just a little guidance will ever be better than a finely crafted narrative written by the very people who designed the world that character exists in. I think you'd have to be pretty clueless to think anyone really truly wants that"
  - ▲6 "There are already games exploring this idea. Here's an example https://store.steampowered.com/app/3730100/Whispers_from_the_Star/"
  - ▲4 "I watched a streamer play a similar mod that works in Skyrim and while it responded to player talking to them, the AI found it very difficult to avoid creeping outside the scope of the character being addressed. For e.g. the streamer was in a city where a murder had been discovered, the streamer then accused a random passer-by (NPC) of the murder, and the NPC admitted to the crime, then stated they were innocent."
  - ▲2 "I am against it for a very simple reason: LLMs are inherently unstable in a rules-based environment. NPC AI is an outcome of, and tightly integrated with, game mechanics. You want NPCs to react in predictably unpredictable ways emergeant from the game context. If a player explores the game space and discovers an interesting NPC interaction mechanic, they want this discovery to be special (i.e. they want to be able to exploit it or repeat it later)."
  - ▲2 "Over 20 years ago, there was a kind of interactive fiction game called 'Façade': https://en.wikipedia.org/wiki/Fa%C3%A7ade_(video_game)"

## [r/gamedev] On LLMs and gameplay

- url: https://reddit.com/r/gamedev/comments/1ng0vnd/on_llms_and_gameplay/
- score: ▲0 · 21评论 · date: 2025-09-13
- 楼主原声: Hi all! I have been working for some time on a project that explores ways to have LLMs interact with gameplay. And found some fascinating things. We all have seen videos of AI generated games that are more like interactive videos. Amazing, but ... meh, for the moment at least. We have also seen many examples of videogame characters turned into advanced chatbots for a much more immersive dialogue in game. Well, i am here to write a little bit about how we can instead integrate current LLMs, even tiny ones that perform great on crappy hardware, into our games... (附大量技术示例:用 qwen3-1.7b 做叙事终点检测、JSON 输出驱动的动态合成系统等)
- 高赞评论(原声):
  - ▲10 "But what's the actual in game usage? If I know the player needs to have an item to trigger something, that's something that can already easily be solved. It's a problem we can even solve trivially at scale... As thought exercises this stuff is all well and good, but its yet to be demonstrated to be practical, let alone more efficient than existing techniques."
  - ▲9 "One major problem is with people trying to find problems for a solution, instead of finding the right solution for a problem. Perhaps, if great effort needs to be taken to think of places where generative AI could be used, it doesn't really have a use. I have yet to see a situation in games where an LLM would be an appropriate way of implementing literally anything."
  - ▲7 "Gamers don't want something with infinite possibilities. They want to find that experience with a correct answer. Determinism and proper game design will outdo llms everyday."
  - ▲6 "If you already have the ability for players to take game actions, and an event system to know what players are doing, and you can pipe all that into an LLM having some kind of node or scripting system to tell when someone has won should be pretty trivial. Not to mention you know it's deterministic. LLMs are not. Even with some prompt engineering, you cannot guarantee a consistent experience at scale."
  - ▲5 "I think you're missing the point about determinism. You can have randomness with determinism, but that randomness always operates within set parameters... Take the example crafting that you had. If I add ten more items in my inventory to the list, is the dragon slayer staff something that always gets returned?"
  - ▲4 "That's everywhere in generative ai field. Literally 'You don't use llms yet, but you NEED to come up with a 'problem' that was 'fixed with ai', so we can sell it to moneypigs(clueless investors)'"

## [r/GameDevelopment] NPC behavior modeled as a dynamical system instead of scripts? Do you think it is promising direction?

- url: https://reddit.com/r/GameDevelopment/comments/1uapia1/npc_behavior_modeled_as_a_dynamical_system/
- score: ▲1 · 12评论 · date: 2026-06-20
- 楼主原声: Recently, I've been working on an RPG persona behavior engine. The idea is to use control systems theory to model a persona's mood, feelings, and needs. So instead of just adding stress or anger based on an NPC's discussion with a player, all characters have an embedded emotional/state space. I wanted to ask for a technical opinion on how manageable you think this would be to deploy in a game, and how it looks from a game developer's perspective. The project is open source, but I'm mainly looking for technical discussion of the approach rather than promotion. (附 whitepaper/github/YouTube 链接)
- 高赞评论(原声):
  - ▲5 "Yeah I could be wrong, but I think a vibe coder found utility ai"
  - ▲3 "That title doesn't make any sense, and this is clearly vibe coded. It's always funny the AI will generate big sounding words but clearly miss the big context of clue that the concept it's trying to explain already exists extensively and is really not complicated. This is just utility AI."
  - ▲3 "Yup, this whole thing reads a bit like chatbot psychosis AI-generated white paper and all."
  - ▲2 "Needs and motivations as an auto decaying integer? Is that really the core of it?"
  - ▲2 "Do you mean for npcs to have artificial life? Sounds like a fun project. Just remember that the most memorable games have scripted characters for a good reason, they are there to drive the story onwards. Recently played god of war and the ragnarok sequel, and is the selected scripted main npcs that makes that game so awesome, not the randoms of filler npcs..."
  - ▲1 (OP reply) "Fair point on the title — I may need to make it clearer. I do know what Utility AI is, and I agree that part of this can be mapped to Utility AI, especially at the action-selection layer. But the thing I'm exploring is not just 'score actions and pick the best one'. The focus is on the dynamic internal state that feeds those scores: fatigue, boredom, anger, recovery, relationships, world inputs, different time constants, saturation, feedback, and traceability over time."
