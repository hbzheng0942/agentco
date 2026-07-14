---
kind: community_raw
platform: reddit
topic: "r/gamedev AI world model integration practical experience gamedev"
fetch_ts: 2026-07-14T04:19:35+00:00
content_hash: ce7d3bc3c7dcedc6
project: gaming
model: ds-chat
trace: traces/reddit_deep/20260714/r-gamedev-ai-world-model-integration-pra.json
source_urls:
  - https://reddit.com/r/GameDevelopment/comments/1rdpta1/trying_to_make_a_living_world_engine_that/
  - https://reddit.com/r/GameDevelopment/comments/1up0zfz/where_do_you_personally_draw_the_line_when_it/
  - https://reddit.com/r/gamedev/comments/1rlhbz7/anyone_else_using_world_models_to_feel_out_a/
  - https://reddit.com/r/gamedev/comments/1sfa588/i_think_most_ai_npc_projects_are_solving_the/
  - https://reddit.com/r/gamedev/comments/1sty2af/postmortem_i_tried_and_failed_vibe_coding_a/
  - https://reddit.com/r/gamedev/comments/1ugwyjt/as_ai_costs_rise_theres_little_evidence_of_major/
---

# 社区原声:reddit / r/gamedev AI world model integration practical experience gamedev

> reddit-research-mcp 深潜采集(ds-chat 忠实转录,未分析)。**原声在高赞评论里**;digester 蒸馏时逐条痛点回指具体评论(带▲赞数),交叉验证,勿把评论区综合成一句。

## [r/gamedev] Anyone else using world models to "feel out" a level before actually building it?
- url: https://reddit.com/r/gamedev/comments/1rlhbz7/anyone_else_using_world_models_to_feel_out_a/
- score: ▲0 · 11评论 · date: 2026-03-05
- 楼主原声: I've been trying to find a way to stop wasting so much time in the early concept phase. Usually, I spend days throwing basic shapes and lights into a scene just to see if a specific hallway or room idea even looks good. Its a lot of manual work to set up a "mood" only to realize the sightlines are bad or the scale feels weird

Recently I started experimenting with a world model as a kind of pre-vis tool before opening Unreal.

I'll just take a messy sketch or a rough layout and let the AI generate a "walk-through" of that space. Obviously, you cant actually play it, but its been great for seeing if a specific look actually works. I can check how a neon sign glows against a wet floor or how a dark tunnel
- 高赞评论(原声):
  - ▲8 "I prefer to ask my cat. He doesn't usually answer and he's not very helpful when he does, but he's cute, and a good boy"
  - ▲8 "Is this a covert ad? because it seems you ask and answer yourself with a workflow that works for you"
    - ▲5 "Yes"
  - ▲4 "No I make a rough blockout and test it in-game then make the assets and I have complete control on every stage"
  - ▲2 "It looks cool for a mood board, but I'd worry about the scale. A video might look great, but then you get into the engine and realize the hallway is way too narrow for the player camera. Does this actually help you plan the layout, or is it just for the lighting and colors?"
  - ▲1 "Just blockout in game and you can actually play it!"
  - ▲0 "Not world models but definitely AI videos made from in game levels. It helps with referencing the mood and can sometimes give you some extra ideas."

---

## [r/gamedev] I think most AI NPC projects are solving the wrong problem
- url: https://reddit.com/r/gamedev/comments/1sfa588/i_think_most_ai_npc_projects_are_solving_the/
- score: ▲0 · 17评论 · date: 2026-04-08
- 楼主原声: A lot of AI game projects focus on making NPCs talk more naturally. That part is interesting, but I don't think it is the real challenge. The hard part is getting characters to take meaningful actions inside a live game state while staying coherent with plot, quest logic, pacing, and player choice.

**Where things actually break**  
It is not that hard to get an NPC to generate a believable line of dialogue. What is much harder is making sure that character does not reveal information the player should not know yet, react as if a quest step already happened when it did not, or say something that sounds plausible in isolation but creates no usable action for the game itself. The same goes for runtime choices. A model can produce an interesting response, but if it cannot turn that into something structured and consistent with the current world state, the whole thing starts to fall apart.
- 高赞评论(原声):
  - ▲16 "Because anyone doing these AI NPC have no idea what makes games fun. Who cares if the NPC can tell you what it had for dinner, it doesn't make a game."
    - ▲2 "It's a novelty that would wear off in a couple hours. We know this because there's already a Skyrim mods that does this with chatgpt and nobody cares."
    - ▲3 "Players are lazy. They don't want to have a conversation, they want results. Same reason games have options to remove pick up animations."
      - ▲3 "A main selling point of BG3 is how many lines of dialogue that game had though... There are clearly players who enjoy conversation."
  - ▲8 "Wouldn't it be cool if you could just tell the LLM exactly which phrase to use in which situation? Like if the LLM could receive a system prompt saying that it will always say 'Go, slay the dragon' at the first stage of the quest and 'Thank you for slaying the dragon, here is your 100 gold reward' after the player completed the quest? And perhaps we could save a ton of tokens and thus solve the cost problem if we would train the AI model to not parse natural language but instead interpret a formalized short-form language for defining the rules of when to use which phrase."
  - ▲2 "I think *all* AI NPC projects are a solution looking for a problem. Too many people think there's some magic in there, and are blind to the low quality they're getting out of it. You could spend months trying to make your LLM not ruin your game, but you could also use that time to just write some good dialogue."
  - ▲1 "There's no point in this discussion since it's too vague to be useful, and most of the interesting work is being done by researchers not by the common programmer who is hacking together vibe coded stuff."
  - ▲1 "I think right now the best solution is to keep a manually pre-set structure for plot, quests and such but add different hand-made alternative ways to tackle those tasks and mask it behind AI interactions instead of dialoge choices to create the illusion that the players interactions really do alter how the quest progresses."

---

## [r/gamedev] Post-mortem: I tried and failed vibe coding a metroidvania so you (hopefully) won't have to
- url: https://reddit.com/r/gamedev/comments/1sty2af/postmortem_i_tried_and_failed_vibe_coding_a/
- score: ▲303 · 409评论 · date: 2026-04-24
- 楼主原声: TLDR; Last Friday, I gave up on my vibe-coded game because I came to the conclusion that it was never going to work. I spent about 40 hours over a couple of months chasing a dream fueled by AI marketing hype. Vibe-coding full projects is largely a myth and today's models and agents aren't able to build anything more than prototypes. You can't use AI to make up for not knowing GDScript or Godot. The time you spend fumbling around with AI would be better spent learning the technical skills.

If you're a seasoned game developer, you already know this. I'm sharing this story for anyone out there who, like me, felt like learning game dev is an impossibly huge task and that AI might be the answer to that problem. I hope this can serve as a reality check to help stem the tide of "AI Slop" inundating society. (...)
- 高赞评论(原声):
  - ▲824 "Gonna be real with you chief; you spent exactly 1 work-week developing a game. Game development is measured in months and years, not weeks."
    - ▲433 "And in one week he had a broken mess. I think he's come to the right conclusion here, using AI to vibe code a whole-ass game without actually knowing how to code is not going to work, no matter how much time he spends designing prompts or setting up development pipelines."
    - ▲76 "Also I could be wrong but 40 hours spread across 'a couple of months' is not equal to 40 hours in 1 week. Working in that small chunks is gonna mean you're not getting focused for that long."
    - ▲46 "Ok, but any amount of time into a completely vibe coded game is a good time to quit."
    - ▲36 "I could have put 500 hours into this and still gotten nowhere. The point of this post is to save time for the next guy who comes along thinking that vibe coding is a shortcut to success."
      - ▲45 "If you put 500 hours into learning how to make a metroidvania, with something like Pixel Game Maker MV, you would have actually made a game. Or at least made significant progress."
        - ▲45 "That's one of the points I tried to make in this post. Unfortunately I don't have 500 hours. I was hoping a legion of AI agents might be a shortcut. I was hopelessly naive and wrong."
    - ▲5 "It's also measured in thought and creativity, not tokens - which I think is their point"
  - ▲42 "the difference between prompts like 'add a feature like this' and actually being able to guide it competently and review and edit it yourself is kind of insane."
  - ▲9 "In a way this 'AI Revolution' reminds me of the shift towards 'higher level languages' in the past. Everyone thought that programmers would disappear as soon as business users had a language that was simple enough for them to interact with directly rather than needing programmers. What they failed to account for was that the problem was never that the business users couldn't read/interact with the code. The problem was always that they weren't used to thinking in a structured rule-based manner."
  - ▲32 "If you use AI, you never learn anything. You're only as good as the AI, and it won't learn from you."

---

## [r/gamedev] As AI costs rise, there's little evidence of major utility in game development
- url: https://reddit.com/r/gamedev/comments/1ugwyjt/as_ai_costs_rise_theres_little_evidence_of_major/
- score: ▲630 · 508评论 · date: 2026-06-27
- 楼主原声: "Similarly, some artists find that image editor tools based on deep learning models do a solid job of speeding up tedious parts of their workflows. AI tools also do a reasonable job of some managerial slog, like transcribing and summarising team meetings. These things are not nothing – they're solid little gains that free up staff to spend more time applying their skills to more interesting and complex tasks.

Those gains, however, are a long way from the dream that executives were sold. Those developers who have tried to use more complex AI tools in their workflows, often being pushed to do so from senior echelons of their companies, generally seem far less enthused by the experience. Setting agentic AI tools loose on game codebases reportedly runs into hard limits very quickly; the codebases are too big, too complex, and too specialized, and any code produced by the agents needs to be extremely carefully vetted by senior developers – a dull and time-consuming task."
- 高赞评论(原声):
  - ▲243 "I actually like some of the dumber AI stuff. Generating boilerplate code from well known APIs. I remember spending several hours adding gzip handling to a file loader/saver since I was learning the API as I went, and this is something GPT3 can do easily in about a minute. Perhaps the goal should be reducing resource requirements rather than improving the models"
    - ▲114 "I'd argue the time spent learning the API wasn't wasted though. Making games and programming in general is all about problem solving and part of that is taking in the shape and structure of things made before. Even if you never added gzip to anything ever again that exposure to the API will help down the road even if you're not consciously aware of it. With AI you gain some efficiency in the task at hand but lose so much more."
    - ▲57 "I'd argue that this is more useful for APIs that have more levers to pull... I worry about juniors. I have enough experience that reviewing AI code tells me enough about the API to know where to look for changes. The junior is gonna be drowning in a wall of text they just don't understand."
  - ▲202 "AI is clearly overhyped from the very beginning, there is a crazy amount of money flowing around it, so the AI companies are trying to force its use in any field, even when on most use cases it is useless at best and counter productive as worst... as any other bubble it is finding the reality that it is very far to be profitable, so it will burst sooner or later"
    - ▲133 "Honestly, it's not just AI companies, or even mostly them. It's CEOs. The ivy-league trust-fund-baby kleptocracy class have never accepted the fact that technically difficult tasks like programming and design and art require the expense of hiring people with talent, training and experience."
      - ▲34 "I would argue that offshoring has way better results than what AI has produced so far."
    - ▲59 "I don't agree that it will die down in the next few years, these models will continue to improve. Hell agentic AI only really became useable in the last 8 months. That's absolutely nothing in technology terms. People who think this is the peak are either deluding themselves, or they haven't used modern AI agents extensively/effectively. In the hands of a skilled dev they save an insane amount of time."
  - ▲136 "Setting agentic AI tools loose on game codebases — Wrong way to use the tool btw"
    - ▲29 "That's what happens when the order to use it comes from people who know nothing about your job"
    - ▲24 "Its strange how quickly vibe coding went from a silly experiment to the way we're pushed to do things."
  - ▲31 "As someone on the absolute frontline of this, it's entirely correct. Small, incremental gains in removing tedious busywork, and lots of effort wasted down trying to research moonshots"

---

## [r/GameDevelopment] Trying to make a "Living World" engine that actually thinks. Am I onto something here?
- url: https://reddit.com/r/GameDevelopment/comments/1rdpta1/trying_to_make_a_living_world_engine_that/
- score: ▲0 · 21评论 · date: 2026-02-25
- 楼主原声: Hi everyone! Like many of you, I've always been obsessed with the promise of "living worlds" in games. We've heard it for years: "cities will grow, wars will break out, and the world will evolve organically". But let's be real—most of the time, it's just a bunch of scripts and static decision trees that feel hollow once you look under the hood. I decided to try an approach With IA. I'm trying to create an engine that can think for itself about basic things (in a medieval context) using AI, and make it possible to do it offline and at no cost to the players once a new model is trained based on the responses, in this case, from Sonnet, Haiku, and Opus... The core idea: Kings who actually reason. Instead of scripts, These AI kings don't just follow rules; they deliberate twice a year based on a thorough analysis of their resources, population, and rival status.
- 高赞评论(原声):
  - ▲8 "Okay, but current AIs are just based on language models. They aren't actually 'thinking' critically, so why do you think this will create some grand amazing game? And like the other guy asked, what's the difference to the player? Civ games are pretty good, and the AIs aren't just scripted to do the same things, they make decisions based on that Civs goals and what they have vs what they need. ALSO, we have goal oriented programming already (called GOAP). it's not just basic scripts, so you clearly have a fundamental misunderstanding of what we have and what we can do."
    - ▲1 "(OP reply) What surprised me building this is that behaviors I never designed emerged naturally, like refusing to trade with an enemy right before attacking, or adjusting strategy based on the memory i load before. Whether that's 'real thinking' philosophically is a fair debate. but they practically, it produced emergent behavior I didn't author."
  - ▲8 "What's the difference, for the player, between a lightweight built-in LLM that you then translate into game actions, and a traditional game AI (meaning heuristic algorithms with some randomness where appropriate)?"
  - ▲1 "The irony here is that AI tends to converge on similar patterns rather than create unique interactions. You're more likely to get authentic output with generating pseudorandom values and plugging them into a heuristics-based 'traditional' game AI."
  - ▲1 "I mean... what makes this any different from the simple agent-based modeling from the 1970s? Or, any of the more advanced computational models since? Not all games have equally thoughtful AI, but pretty much all of the best simulation/management games already do this in their simulation engine (vs. adding the natural language layer to feed to a giant generative AI model that is really good at putting sensible natural language words back together at a much higher compute and financial cost)"
  - ▲1 "(OP reply) I didn't code 'don't trade with enemies when you're about to attack' the king reasoned to that conclusion from first principles. Whether that's worth the compute cost long-term is exactly why I'm planning to distill it into a smaller trained model. The LLM is the teacher, not the final product."

---

## [r/GameDevelopment] Where do you personally draw the line when it comes to using AI in game development?
- url: https://reddit.com/r/GameDevelopment/comments/1up0zfz/where_do_you_personally_draw_the_line_when_it/
- score: ▲0 · 25评论 · date: 2026-07-06
- 楼主原声: First of all, I'm not looking for people to agree with the use of AI. I'm genuinely interested in hearing opinions from different perspectives, whether you support it or oppose it. I understand that some people believe any use of AI in game development is unacceptable, and I completely respect that viewpoint. At the same time, AI-powered tools are becoming more common, so I'm curious where people personally draw the line. For example, this is how I'm currently learning programming. I describe a feature I want to create to an AI, and it generates example code. Instead of copying and pasting it, I type it out myself. While doing so, I try to understand how it works and modify it to fit my own game.
- 高赞评论(原声):
  - ▲6 "I don't really care about whether it's been used or what tasks it's been used for. What I really care about is whether the person who's using it is taking personal responsibility for the final product. It can be lazy abdication of personal responsibility or it can just be a very good set of new tools for people who care about the craft. The first one offends me, the second one excites me."
  - ▲4 "I draw the line where it impacts the sales of my game negatively which rn is basically using any kind of AI generated asset. I don't mind using agentic AI for writing code or directly interacting with unity and afaik you don't need to disclose that kind of AI usage when you publish on steam. The only problem is, AI agents suck at writing code so you'll most likely endup doing it yourself unless it's a very generic and easy to write piece of code."
  - ▲3 "(Reply to OP) Retyping AI code won't do that. Coding is ultimately about why more than how once you learn the syntax."
  - ▲2 "For most people 'just at the line where however I use it is okay and anyone more than me is too much'."
  - ▲2 "Line is where players can find out about its usage"
  - ▲1 "We just don't use any generative AI in our game. Yes it can generate some decorative imagery but I can say that my works are not solely a product to generate income. Our upcoming game has a very intentional design. And this design is also defined by our own limits."
  - ▲1 "In my opinion, it's not the tool, it's the user. If someone uses it to make a good, fun game that is well made then that's exactly what it's designed for. If someone just lazily makes a weak prototype without much effort and try sell it as a full game is where the problem is."
  - ▲1 "(OP reply from OP) Spend most of the effort on planning. Use reasoning models to discuss the problem, challenge assumptions, explore alternatives, and finalize a detailed implementation plan. Once the plan is solid, hand it off to a fast, inexpensive coding model for implementation. Review every code change—both manually and with AI. Never assume generated code is correct."
