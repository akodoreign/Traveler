# PRODUCTION — Crab Ch1 · "Eggs and Shadows"

**Traveler:** Hiruma Natsuko · **Lv** 1–8 · **Outline:** `scripts/crab-ch1-eggs-and-shadows.md`
**Flags set:** `hidden_ones_cleared`, `talked_satomi`, `ryozo_talked_down`, `oni_named_ryozo`, `nezumi_friends`,
`seppun_tanto_taken`
**Maps:** `wall_watchtower`, `wall_garrison`, `road_coast`, `hoshi_town`, `hoshi_inn`, `quarry_camp`,
`egg_caves_1–3`, `egg_caves_altar`
**Battles:** `b_goblin_raid` (tutorial), `b_hidden_ones_sumai` (Sumai), `b_cave_nezumi_a/b`, `b_cave_beetles`,
`b_boss_grasping_paw` (+Ryozo variant)
**Fit conversions applied (OCTOPATH-FIT §3):** the chase is a cutscene plus a follow-walk; tracking uses interaction
prompts; the Rumble meter is the chapter's one gimmick.

**Storyboard:** `storyboards/crab-ch1.md` (map layouts, chests, and the findings applied below).

### RECRUIT VARIANT (Natsuko is not the starter; storyboards README §3)
**Join point:** `hoshi_town`, the noodle stall. S03 plays when the party first walks past it. Natsuko is the woman
who sits down beside the angry bushi.
After the drop-soup exchange, talk to her:
NATSUKO: You lot aren't from the coast. (beat) Nobody chooses Hoshi-no-Ichi. It chooses you.
NATSUKO: I'm on leave. Apparently. My commander says I have to rest. I don't know how.
NATSUKO: And the town's missing its eggs. I could use someone who doesn't mind getting egg on them.
> CHOICE "Travel with Natsuko?" → Yes: she joins → **Memory** (S01–S02 as a cutscene: the goblin raid in three shots,
  the hat, the map case, Tomoe's leave order; no battle, no tutorial) → resume at S03's "Why are there no eggs?" line.
→ No: she stays at the stall; her chapter icon appears there.

---

## S01 — The Long Grey Line
MAP: `wall_watchtower` (night, rain) · TRIGGER: new game, Natsuko chosen
(Black screen. Rain. A war drum, slow.)
NARRATION: The Kaiu Wall. Three hundred miles of stone between the Emerald Empire and the Shadowlands.
NARRATION: Every night, something tries to climb it. Every night, the Crab push it back down.
(Fade in: torches hissing on the battlements. Natsuko leans on her yari, a rolled map case strapped to her back.)
HIDA SACHIKO: Hiruma! Your little friends are back!
NATSUKO: How many?
HIDA SACHIKO: Twelve. Thirteen. (squinting) One of them has a hat.
NATSUKO: A hat.
HIDA SACHIKO: A straw one. Very fetching.
NATSUKO: Then I'll take the one with the hat. Fashion should be punished.
(Grappling hooks clatter onto the stone. Goblins pour over the crenellations.)
HIRUMA RYOICHI: Natsuko! Left side!
NATSUKO: I see them. Stay behind me, Ryoichi.
HIRUMA RYOICHI: I always do. It's the safest place on the Wall.
[BATTLE b_goblin_raid] (tutorial: see the TUTORIAL block)

### TUTORIAL (popup prompts during b_goblin_raid)
- T1 (turn 1): "Enemies show **weakness icons**. A goblin flinches from **spears** — your Yari."
- T2 (first shield hit): "Each weakness hit chips away **Resolve**. When it reaches zero, the foe is **open —
  Suki!** It loses its turn and takes extra damage."
- T3 (start of turn 2): "You gained a **Void Point**. Spend them to **Boost**: more hits, more power."
- T4 (turn 3, if Natsuko is targeted): "**Razor's Edge** — stand in the gap. Draw their blows. Make them miss."
- T5 (after the hat-goblin breaks): "Strike while it reels."

(After battle. The last goblin topples off the Wall. Its straw hat drifts down after it.)
HIDA SACHIKO: (laughing) You hit it so hard it lost its fashion sense.
NATSUKO: It never had any. (wincing, holding her arm)
HIRUMA RYOICHI: You're bleeding.
NATSUKO: The goblin started it.
(Ryoichi wraps her arm. He glances at the map case.)
HIRUMA RYOICHI: Your father's map got wet.
NATSUKO: (too quickly) It's oiled. It's fine.
NATSUKO: It's been through worse than rain.
HIRUMA RYOICHI: You still look at it every night.
HIRUMA RYOICHI: Thirty years of Hiruma died looking for that road home, Natsuko.
NATSUKO: Then the thirty-first should at least look at the map first.
(Beat. The rain eases.)
NATSUKO: (quietly) Go to sleep, Ryoichi. I've got the watch.
HIRUMA RYOICHI: You always have the watch.
NATSUKO: Someone has to.
[SAVE]

## S02 — Leave, Unwanted
MAP: `wall_garrison` (dawn) · TRIGGER: auto after S01
(A cramped garrison office. A grizzled commander, HIDA TOMOE, reading a report without looking up.)
HIDA TOMOE: Three months on the Wall without a day's leave.
NATSUKO: [neutral] Yes, Tomoe-sama.
HIDA TOMOE: Two broken ribs you didn't report.
NATSUKO: [determined] One and a half, Tomoe-sama.
HIDA TOMOE: (finally looking up) You're going on leave.
NATSUKO: [determined] I'd rather not.
HIDA TOMOE: I'd rather you didn't die of being stubborn on my section of Wall.
HIDA TOMOE: There's a supply cart going up the coast to Hoshi-no-Ichi. You'll escort it.
HIDA TOMOE: Then you'll rest. A week. Eat food a goblin hasn't touched.
NATSUKO: [determined] And if I refuse?
HIDA TOMOE: Then you'll guard the latrines until the Shadowlands fall into the sea.
NATSUKO: [determined] (pause) …I'll take the cart.
HIDA TOMOE: Good. And Hiruma — (beat) — try to enjoy yourself.
NATSUKO: [determined] I'll try, Tomoe-sama. I don't know how.
HIDA TOMOE: Nobody does, on the Wall. Go and find out.
(Map unlocks. Objective: "Escort the cart to Hoshi-no-Ichi.")
[SAVE]

## S03 — The Town With No Eggs
MAP: `hoshi_town` (day) · TRIGGER: arrive with the cart
NARRATION: Hoshi-no-Ichi. A Yasuki market town where salt, fish and gossip change hands every hour.
(The cart pulls in. Merchants mob it.)
CART DRIVER: Rice! Is there rice?
MERCHANT: Is there any *egg*?
CART DRIVER: Eggs? I brought pickled radish.
MERCHANT: (wailing) Radish!
NATSUKO: (aside) …Rest. Right.
(Inside the noodle stall: a big Crab bushi, red-faced, glares at his bowl.)
ANGRY CRAB BUSHI: Egg-drop soup!
KIYO: Y-yes, my lord!
ANGRY CRAB BUSHI: Where. Is. The. EGG.
KIYO: There isn't an egg in the whole town, my lord! I swear it!
ANGRY CRAB BUSHI: Then what am I drinking?!
(Natsuko sits down beside him on the bench.)
NATSUKO: Drop soup.
ANGRY CRAB BUSHI: …What?
NATSUKO: No egg. Just the drop. Very pure. Very Crab.
NATSUKO: Drink it and let the girl go.
(Long pause. He drinks. He starts to laugh, a big helpless laugh.)
ANGRY CRAB BUSHI: Drop soup! Ha! You're from the Wall.
NATSUKO: Is it that obvious?
ANGRY CRAB BUSHI: Nobody else would talk to me like that.
(He leaves coins for the whole table and stomps out, still laughing.)
KIYO: (bowing deeply) Thank you, my lady! He's been shouting for three days!
NATSUKO: I'm not a lady. I'm a scout. Why are there no eggs?
KIYO: Nobody knows! The hens lay, and by morning the eggs are gone.
KIYO: And it isn't just eggs. Fans. Mirrors. Hairpins. Little pretty things.
KIYO: Everyone says it's the Hidden Ones.
NATSUKO: The who?
KIYO: Ronin! A gang camped at the old quarry. Thieves, all of them, the magistrate says.
NATSUKO: (aside) A gang that steals eggs and hairpins. Terrifying.
(Objective: "Look around Hoshi-no-Ichi." Town is free to explore. Path action **Sumai** tutorial pops when first
nearing a blocking NPC.)

### TUTORIAL — Path Action: Sumai
"**Sumai** — wrestle an NPC. Win and they step aside (or tell you what they know). Your chance depends on your
**Jiujutsu** rank versus theirs. Failing costs a little of the town's **Honor** — reputation."

### Town NPCs — `hoshi_town`
| NPC | Default line | Discern-type info (Natsuko has none; others' path actions) | Path action |
|---|---|---|---|
| Kiyo (noodle girl) | "Drop soup! I'm putting it on the menu." | *Eavesdrop:* "Saw a little furry shape on the roof last night." | — |
| Egg merchant Gonbei | "Ruined! Forty hens and not one egg to sell!" | *Discern:* "His hens are fine. Something takes the eggs at night." | *Barter:* buys Fresh Egg ×1 later (sidequest) |
| Yasuki magistrate Kanbe | "The Hidden Ones did it. Case closed. Lunch." | *Discern:* "He hasn't investigated anything." | *Sumai:* refuses ("I'm a magistrate!") |
| **Seppun Satomi** (courtier) | "You're Crab? Have you seen… no. Never mind." | *Discern:* "Looking for a missing relative." | Talk ×2 → `[SET talked_satomi]` |
| Street fishwife | "Salt herring! Two zeni, or one if you smile." | — | *Barter:* Herring (heal item) |
| Wall veteran, drunk | "I was on the Wall forty years. Now I'm on the sake." | — | *Sumai:* win → Old Jade Bead (accessory) |
| Child with kite | "My mirror's gone! I used it to signal my friend!" | — | *Bless:* follows (battle: "Kite Signal", Accuracy up, 2 uses) |
| Kiyo (again) | — | — | *Charm:* follows (battle: "Hot Broth", small Fire hit, 2 uses) |
| Hida bushi Taneo (the angry bushi, after S03) | "Drop soup. Ha!" | — | *Duel* (Iaijutsu 2): win → Oak Tetsubo (fine) · Glory +1 |
| Gonbei / Kanbe (again) | — | — | *Pilfer:* henhouse key (→ Herbal Salve chest) / seized Jade Dust ×2 |

### S03b — Seppun Satomi (optional, sets `talked_satomi`)
MAP: `hoshi_town`, tea house · TRIGGER: talk to Satomi twice
SEPPUN SATOMI: You're a scout. You notice things?
NATSUKO: It's mostly what I do. That, and stab things.
SEPPUN SATOMI: (lowering her voice) My nephew came to this coast a month ago. Seppun Ryozo.
SEPPUN SATOMI: An Imperial guardsman. He… had troubles in the capital. Strange ideas.
SEPPUN SATOMI: His letters stopped. If you hear of him, come to me. Only me.
NATSUKO: Strange ideas like what?
SEPPUN SATOMI: (pause) Ideas a Seppun should not have. Please. Only me.
[SET talked_satomi]

## S04 — The Hidden Ones
MAP: `quarry_camp` · TRIGGER: go to the quarry (objective after talking to 3 town NPCs)
(Ragged tents. Thin ronin around a thin fire. Town guards gather on the ridge behind Natsuko.)
GUARD SERGEANT: Stand aside, scout. We're clearing this nest at noon.
NATSUKO: Give me until noon, then.
GUARD SERGEANT: (shrugging) Your funeral.
(A mountain of a man rises from the fire: GONTA.)
GONTA: Crab dog. Come to watch the Yasuki burn us out?
NATSUKO: Came to see if you're worth burning.
GONTA: I don't talk to Crab dogs.
NATSUKO: Then don't talk. (setting down her yari) Wrestle.
GONTA: (slow grin) …Now you're speaking a language I like.
> CHOICE "Gonta"
  - "Sumai with him." → [PA Sumai Gonta] (forced win if fails twice: Gonta "lets" her win, slightly less Honor)
  - "Look around the camp first." → explore camp (3 hint spots), then Sumai
  - "Leave." → [SET quarry_left] guards raid at noon; return to S05 (no `hidden_ones_cleared`)
[IF Sumai won]
(Gonta lands flat on his back. The camp goes silent. Then he roars with laughter.)
GONTA: All right, scout! All right! You throw like a landslide!
NATSUKO: Now talk.
GONTA: Look around you. Do we look like we're eating anyone's eggs?
GONTA: We're eating *bark*. Someone's robbing the whole coast — us too. My boy's carving got stolen. A wooden fish.
NATSUKO: (looking at the empty pots) …Who steals a wooden fish?
GONTA: Something small. Comes at night. Smells like a rotten egg.
(Natsuko walks back up to the ridge.)
NATSUKO: Sergeant. They don't have anything. Not even soup.
GUARD SERGEANT: (pause) …The magistrate won't like it.
NATSUKO: The magistrate doesn't like anything. Go home.
[SET hidden_ones_cleared]
GONTA: (calling after her) Crab! If you ever need a landslide, ask for Gonta!
[END]
[SAVE]

## S05 — Something in My Pack
MAP: `hoshi_inn` (night) · TRIGGER: the first inn rest **after S04** (earlier rests are normal)
(Dark room. Snoring through the wall. A tiny scratching. A small furred shape rummaging in Natsuko's pack.)
(Natsuko's eyes open.)
NATSUKO: (whisper) …You picked the wrong pack, friend.
(The shape freezes: a young NEZUMI with huge ears. It grabs the map case and bolts out the window.)
NATSUKO: NOT. THE. MAP!
(CUTSCENE — the chase: Natsuko vaults the window, half-dressed, yari in hand, across rooftops, slides down a
drainpipe, crashes through a laundry line. The nezumi is always one roof ahead. At the edge of town it stops,
looks back — and *waits* for her.)
NATSUKO: (panting) …You're waiting for me.
(It runs again, slower now. Prompt: "Follow the nezumi.")
### FOLLOW-WALK (`road_coast`, night) — interaction prompts (random encounters **off** until the cave mouth)
- P1 (muddy prints): "Small clawed prints. Fresh. Heading for the cliffs."
- P2 (a dropped hairpin): "A stolen hairpin, dropped — on purpose?"
- P3 (cave mouth smell): "Rotten eggs. Lots of them."
(At the cave mouth the nezumi sets the map case down carefully and squeaks, pointing inside.)
SQUEAK: Scout-who-fights-at-night! You come! You come!
NATSUKO: You can talk.
SQUEAK: Yes-yes. Talk good-good. Squeak-of-Many-Eggs, me.
NATSUKO: You stole my map.
SQUEAK: (proudly) Yes! Smart-smart. Scout follow map. Scout come here.
NATSUKO: …You stole my father's map to get me to follow you.
SQUEAK: Yes-yes! Big-man-sad. Big-man-*wrong*. Eggs-eggs-eggs, no-good!
SQUEAK: Big-man say eggs make magic. Eggs make nothing! Only stink!
SQUEAK: Tribe say Squeak crazy. Squeak say: get scout. Scout fight bad things at night.
NATSUKO: (picking up the map case, checking it, sighing) Who's the big man?
SQUEAK: Big-man-shiny-armor. He feed us. He love us. (ears drooping) He very wrong.
NATSUKO: (beat) …All right. Show me.
[SAVE]

## S06 — The Egg Caves (dungeon)
MAP: `egg_caves_1–3` · TRIGGER: enter cave
### GIMMICK — Rumble meter (on screen in all cave battles)
"The cave is unstable. **Big attacks** (area skills, Boosted multi-hits) fill the **Rumble** meter.
When it's full — **cave-in!** Everyone takes damage, enemies too."
(Cave 1: nests of straw; stolen fans and mirrors laid out in careful circles.)
NATSUKO: Mirrors. Fans. Kiyo's town has been decorating a cave.
(Interaction: the stolen-thing circles → [ITEM +Kite Mirror] [ITEM +Wooden Fish] [ITEM +Pearl Hairpin]. Return them in
Hoshi-no-Ichi after the chapter: the kite child, Gonta's boy [IF hidden_ones_cleared], Kiyo.)
SQUEAK: Big-man say: shiny things help magic.
NATSUKO: Does it?
SQUEAK: No. But pretty.
[BATTLE b_cave_nezumi_a] (nezumi who distrust Squeak)
NEZUMI WARRIOR: Squeak-traitor! Bring Crab! Crab eat rats!
NATSUKO: I don't eat rats. (beat) Not since that one winter.
SQUEAK: (horrified) …
NATSUKO: Joke. It was a joke.
(Cave 2: baskets of eggs painted with crude symbols.)
NATSUKO: (lifting one) These marks… they look like a child drew a nightmare.
SQUEAK: Big-man paint. Every night. Paint-paint-paint.
[BATTLE b_cave_beetles]
(Cave 3: polished Imperial armour on a driftwood stand.)
NATSUKO: Seppun colours. An Imperial guard's armour… polished every day.
[IF talked_satomi]
NATSUKO: (quietly) Satomi's nephew.
NATSUKO: Ryozo. You're Seppun Ryozo.
[END]
[BATTLE b_cave_nezumi_b]
[SAVE] (before the altar)

## S07 — Seppun Ryozo, Sorcerer of Eggs
MAP: `egg_caves_altar` · TRIGGER: enter altar cave
(A great heap of eggs. Candles. Young nezumi kneel around a thin man in a guard's undershirt, painting an egg with
enormous care: SEPPUN RYOZO.)
SEPPUN RYOZO: (not looking up) Another one, Squeak? Did you bring me the fresh ones?
SQUEAK: (small) Brought scout.
SEPPUN RYOZO: (looking up, radiant) A Crab! Wonderful! Come, come — you'll understand. Your people fight darkness!
NATSUKO: My people fight goblins. What are you doing, Ryozo?
SEPPUN RYOZO: You know my name! Then you know I was a guardsman of the Emperor himself.
SEPPUN RYOZO: And I learned the secret the shugenja hide. (holding up an egg) Magic without blood.
SEPPUN RYOZO: The life inside the shell is the offering. No blood. No sin. A clean sorcery!
SEPPUN RYOZO: They laughed at me in the capital. They threw me out.
NATSUKO: Does it work?
SEPPUN RYOZO: (beaming) Of course it works!
NATSUKO: What happened when you tried it?
SEPPUN RYOZO: (long pause) …The eggs must be fresher.
> CHOICE "Reach Ryozo" (pick until success or 3 tries)
  - [IF talked_satomi] "Your aunt Satomi is in Hoshi-no-Ichi. She's frightened for you." → [SET ryo_a]
      SEPPUN RYOZO: Aunt Satomi? (the brush trembles) She… she's here? She came?
  - "These nezumi will die for you. Is that clean?" → [SET ryo_b]
      (The young nezumi look up at him. He looks at them. For a moment, he sees them.)
      SEPPUN RYOZO: I… I only wanted to give them something. Something that would protect them.
  - "You've been stealing from starving people." → (rage)
      SEPPUN RYOZO: Starving?! I'm saving them from the dark and you talk about FOOD?
[IF ryo_a AND ryo_b]
SEPPUN RYOZO: (setting the egg down very carefully) …It never worked. Not once. I knew.
SEPPUN RYOZO: I just couldn't stop painting. If I stopped, I'd have to go home a failure.
NATSUKO: (kneeling to his level) My whole family's failed to go home for fifteen generations, Ryozo.
NATSUKO: You get up and try again. That's all there is.
SEPPUN RYOZO: (tears) …Will you take me to her?
NATSUKO: Yes.
[SET ryozo_talked_down]
[END]

## S08 — The Grasping Paw (BOSS)
MAP: `egg_caves_altar` · TRIGGER: after S07
(The candles gutter. An old nezumi in bone charms steps out of the shadows: the TRIBE SHAMAN.)
NEZUMI SHAMAN: Shiny-man ours. Eggs ours. Young ones OURS.
NEZUMI SHAMAN: Crab take nothing. Crab go in the dark-hole forever.
[IF ryozo_talked_down]
SQUEAK: Shaman wrong! Squeak fight with scout!
[GUEST +Squeak (battle only): skill "Pocket Sand" — blinds 1 enemy, 2 uses]
[BATTLE b_boss_grasping_paw]
[ELSE]
SEPPUN RYOZO: (rising, wild-eyed) You'll not take my children! The eggs will protect us!
[BATTLE b_boss_grasping_paw_ryozo] (Ryozo heals allies with "Egg Rite" — it works because they believe)
[END]
### Boss barks
- Shaman at 50%: "Name-magic! You forget-forget your own name!" (casts Silence)
- Rumble at 75%: SQUEAK: "Scout! Roof go crack-crack!"
- If a cave-in occurs: NATSUKO: "Well. That's one way to win."
- Shaman defeated: NEZUMI SHAMAN: "…Young ones… choose scout…?"

## S09 — Something Without a Name
MAP: `egg_caves_altar` → `hoshi_town` · TRIGGER: after the boss
[IF ryozo_talked_down]
(Dawn. Natsuko walks Ryozo out of the cave mouth, wrapped in her cloak.)
(Hoshi-no-Ichi, the tea house. Satomi rushes to him and stops herself — then holds him anyway.)
SEPPUN SATOMI: You foolish, foolish boy.
SEPPUN RYOZO: I'm sorry, Aunt. The eggs didn't work.
SEPPUN SATOMI: (laughing and crying) No. No, they wouldn't.
SEPPUN SATOMI: (to Natsuko) The town will be paid for every egg. Every fan. Every hairpin.
SEPPUN SATOMI: And this will never have happened. You understand.
NATSUKO: I understand you're asking. I don't gossip. Ask anyone on the Wall.
SEPPUN SATOMI: (offering a lacquered box) A Seppun blade. A small thank-you.
> CHOICE "Satomi's gift"
  - "Accept." → [ITEM +Seppun Tanto] [SET seppun_tanto_taken]
      NATSUKO: It's beautiful. I'll get goblin on it within the week.
  - "Refuse." → (town Honor +1)
      NATSUKO: Keep it. Buy Kiyo some hens.
[ELSE]
(The party turns to leave. Ryozo, bleeding, crawls into a side tunnel. The camera stays behind.)
(Darkness. Dripping. Something large and wet shifts.)
??? : (a voice like a door creaking) …a name…
??? : …give me… a name…
SEPPUN RYOZO: (delirious) …Seppun… Ryozo… of the Emperor's… guard…
??? : …Ryozo. (pleased, savouring it) …Yes.
(Black.)
[SET oni_named_ryozo]
(Hoshi-no-Ichi, the tea house. Satomi is packing.)
SEPPUN SATOMI: You found him.
NATSUKO: I found where he was. (beat) He ran into the deep tunnels. I couldn't follow.
SEPPUN SATOMI: (very still) …Then I'll tell the family he died bravely. It's what Seppun do.
(She leaves the coast that evening. No gift.)
[END]
(After the boss: the altar cave collapses behind them. Caves 1–3 stay open for revisits.)
(Outside the cave: the young nezumi huddle at the entrance. Squeak looks up at Natsuko.)
SQUEAK: Tribe have no cave now. Roof go crack. Shaman gone.
NATSUKO: (long pause, looking out at the grey sea)
NATSUKO: (aside) Every Crab instinct I have says walk away.
NATSUKO: …There's a dry cave three ri from my Wall post. Nobody uses it. The goblins hate the smell.
SQUEAK: (ears up) Smell like what?
NATSUKO: Crab.
SQUEAK: (delighted) Good-good smell!
[SET nezumi_friends]
[ITEM +Squeak's Charm (accessory: item-find up)]

## S10 — Back to the Wall
MAP: `wall_garrison` · TRIGGER: travel back
(Natsuko returns: bruised, the map case intact. At a distance behind her, a nezumi pretends very hard not to be
following.)
HIDA SACHIKO: You're back early!
NATSUKO: I rested.
HIDA SACHIKO: You've got a black eye.
NATSUKO: I rested hard.
(A RUNNER in Kaiu colours waits at the gate, a sealed letter in his hand.)
RUNNER: Hiruma Natsuko? The karo of Kyuden Hida, Kaiu Takakana, summons you.
HIDA SACHIKO: Kyuden Hida! The Champion's castle! What did you *do*?
NATSUKO: I went on leave.
HIDA SACHIKO: (to the sky) Fortunes help us. Never let her rest again.
NATSUKO: (reading the letter; quietly) He wants a Hiruma nobody at court would notice.
NATSUKO: (folding it away, smiling a little) Well. That's me.
[CHAPTER COMPLETE]

### Chapter complete card
**"Eggs and Shadows" — complete.**
Journal: *Sent on leave against her will, Natsuko found a town's missing eggs, a guardsman's broken dream, and a
tribe of nezumi who chose her. Now Kyuden Hida calls for a scout nobody will notice.*

---

## Travel Banter unlocked by Crab Ch1
### TB-crab1-a "Drop Soup" (Natsuko + Sayo)
SAYO: Is it true you told a samurai to drink egg-drop soup with no egg?
NATSUKO: I told him it was drop soup.
SAYO: (delighted) That's the best thing I've heard all year. Can I use it?
NATSUKO: On a samurai?
SAYO: On *every* samurai.
### TB-crab1-b "The Map" (Natsuko + Haruki)
HARUKI: You check that map case every night. (counting on his fingers) Four times tonight.
NATSUKO: You counted.
HARUKI: I count everything. It's a… habit.
NATSUKO: (pause) My father drew it. A road back to Hiruma Castle. Thirty years of work.
HARUKI: Does it lead there?
NATSUKO: I don't know. (beat) That's why I check it.
### TB-crab1-c "Rats" (Natsuko + Mitsue)
MITSUE: A nezumi has been following you for three days.
NATSUKO: His name's Squeak.
MITSUE: He's very bad at hiding.
NATSUKO: He's very good at stealing maps. Everyone has a talent.
