# PRODUCTION — Ronin Ch2 · "The Noble and the Ronin"

**Traveler:** Sayo · **Lv** 20–25 · **Outline:** `scripts/ronin-ch2-the-noble-and-the-ronin.md`
**Flags set:** `writ_pilfered`, `retainers_spared`, `crawl_results`, `order_promise`
**Maps:** `river_road_winter`, `rice_barge`, `floating_flowers` (jetties, harbourmaster's house, geisha house, market),
`snake_den_1–2`, `sand_room`, `serpent_mouth`
**Battles:** `b_retainers_road`, `b_storm_jetties`, `b_boss_snake_enforcers`
**Guest:** Jinnai (monk; S02)
**Set-piece:** "Only Snakes May Pass" (the sand room) · **Storyboard:** `storyboards/ronin-ch2.md`
**Night rule:** the first inn rest in Floating Flowers is night 1 (S04, the storm); the next rest is night 2 (S05).

---

## S01 — Apprehend the Criminal!
MAP: `river_road_winter` · TRIGGER: start
NARRATION: Winter on the river road. Lords ride in the middle. Everyone else walks in the ditch.
(A devout ronin pilgrim in grey, JINNAI, steps aside a heartbeat too slowly for a mounted young lord: IKOMA
SADANOBU. The lord's retainers knock the pilgrim into the snow and beat him.)
IKOMA SADANOBU: (spotting Sayo) You! Peasant! Hold that man!
SAYO: (looking at the bleeding pilgrim; then at the lord) Which one of you is the criminal again? I'm new.
IKOMA SADANOBU: (spluttering) How *dare*—! Seize her too!
[BATTLE b_retainers_road] (they flee at half strength)
IKOMA SADANOBU: (galloping off) You'll hang, wave-girl! I'll have your face on every post from here to the sea!
SAYO: (calling after) Make sure they get my good side!
(His travel writ fluttered from his saddle in the fight.)
> CHOICE "The writ"
  - [PA Pilfer] "Pocket it." → [SET writ_pilfered] (Honor −1 if any witness — there's one: a crow)
  - "Leave it." → (nothing)

## S02 — Barge Medicine
MAP: `rice_barge` · TRIGGER: flee downriver
(A rice barge in the dark. Sayo binds the pilgrim's ribs by lantern light. He's calm, wry, and in more pain than he admits.)
JINNAI: You'll be hunted for this.
SAYO: I was born on a barge, monk. I've been "hunted" by every toll-keeper on three rivers.
SAYO: They never catch me at low tide.
JINNAI: (a dry laugh; then he winces) …I'm not a monk. Not exactly. A lay brother. The Order of Osano-Wo.
SAYO: Osano-Wo? The thunder fortune? Your order hits people.
JINNAI: Only when they insist.
### Tutorial — Remedy with two catalysts (story brew)
"Ginseng + Willow bark + Snow-lotus: a heal with a defence buff and regeneration." (Sayo's Medicine rank doesn't
need to be 5 for this story brew.)
(Jinnai's prayer beads click as he settles. On one bead: a tiny carved snake.)
SAYO: Pretty snake.
JINNAI: (closing his hand over it) A family thing.
[GUEST +Jinnai] (skills: Freezing the Lifeblood — paralyze, 2 uses; Chi Protection — heal/cure, 1 use; passive Kharmic counter)

## S03 — Floating Flowers (hub)
MAP: `floating_flowers` · TRIGGER: dock
NARRATION: The Village of Floating Flowers. A river stop between Crab, Scorpion and Sparrow lands, where everyone knows everyone's business and nobody admits it.
(A wanted poster on the dock post: a badly drawn girl with an enormous nose.)
VILLAGE GRANDMOTHER: (comparing the poster to Sayo) No, no. That girl has a nose like a radish. You're much prettier.
VILLAGE GRANDMOTHER: Go away before they notice.
SAYO: (delighted) I love this village already.
### Town NPCs — Floating Flowers (side stories)
| NPC | Default | Info | Path action |
|---|---|---|---|
| Yasuki merchant **Kanemori** | "I'm a respectable man! (sighs) Mostly." | *Discern:* "In love with a branded eta woman. Ashamed of being ashamed." | — |
| The eta woman **Oyuki** | "Sayo? Ume-baa's girl? You set my arm when I was nine!" | — | *Remedy:* her cough (side story: Kanemori & Oyuki) |
| Geisha-house **Madame Hagi** (Ryoko Owari) | "Everyone has a secret, sweetling. Mine are expensive." | *Eavesdrop:* "The harbourmaster has visitors at midnight. Men with snake rings." | *Barter:* information |
| Harbourmaster **Tokubei** | "Beloved by all! Ask anyone!" | *Discern* (Gendo): "His floor mats are newer than his house." | — |
| Fisherman | "Lord Sadanobu's men will come. They always do." | — | *Pilfer:* fish |
| Sparrow ronin | "Fox or Sparrow, everyone wants a sword here." | — | *Duel* (Iaijutsu 3): Glory +1 · Lacquered Yari |
| Boatman | "Storm's coming." | — | *Sumai:* "Lord Sadanobu pays the storm-riders double." |
| Shrine maiden | "The river gives and the river takes." | — | *Bless:* follows ("River Blessing": Water resist, 1 battle) |
| "Pedlar" (Sadanobu's spy) | "Ribbons! Combs!" | *Discern:* "Not a pedlar. Too clean." | *Charm:* gives up the retainer count (−1 enemy on the jetties) |
### Sub-story — "Kanemori and Oyuki"
1. Remedy Oyuki's cough (Willow bark + Honey). 2. Discern or Eavesdrop Kanemori: he wants to ask for her hand in public
and is terrified. 3. Charm or Bless gives him courage; he asks on the jetty. Reward: **Kanemori's Discount** (Floating
Flowers shops −10%) + Herbal Salve ×5.
[SAVE]

## S04 — The Storm on the Jetties
MAP: `floating_flowers` (jetties, storm) · TRIGGER: night 1
(A winter storm. Sadanobu's retainers come down the jetties in force with torches.)
RETAINER CAPTAIN: Give up the wave-girl and the beggar, villagers!
VILLAGE GRANDMOTHER: (from a window) What wave-girl? We only have pretty girls here!
[BATTLE b_storm_jetties]
> CHOICE "The retainers"
  - "Spare them." → [SET retainers_spared] (Honor +1; the village shelters Sayo)
      SAYO: (to the beaten captain) Go home. Tell your lord the radish-nosed girl wasn't here.
  - "Drive them into the river." → (faster; the village is frightened of her)

## S05 — Under the Floor Mats (dungeon)
MAP: `snake_den_1–2` · TRIGGER: night 2 — Jinnai is gone from his bed
(Sayo follows wet footprints to the harbourmaster's house. Under the floor mats: a trapdoor, a stair, a cold den of
carved stone serpents. Candles. Men and women with snake tattoos on their wrists, murmuring.)
SNAKE CULTIST: (unseen; whispering) …the line must stay true… the usurper must be removed…
SAYO: (to herself) A cult. Under a harbourmaster. Of course.
(Far ahead, Jinnai's grey back, walking calmly into the dark.)

## S06 — Only Snakes May Pass (set-piece)
MAP: `sand_room` · TRIGGER: enter
(A long room of white sand under carved serpents. Shadows of snakes slide across the walls.)
CARVED INSCRIPTION (narration): "Only snakes may pass."
### SYSTEM — the sand room
"Each party member chooses: **walk** (shadow-snakes bite: damage + Poison) or **crawl on your belly** (samurai lose
face: **Honor −1** each)."
SAYO: (already on her belly, grinning) Come on. The sand's warm.
[IF rensei_in_party] RENSEI: (standing very straight) I would rather be bitten. (he is; he endures it with dignity) [END]
[IF natsuko_in_party] NATSUKO: (crawling) I've crawled through worse on the Wall. Bigger snakes, too. [END]
[IF shizue_in_party] SHIZUE: (crawling, precise) It's a test. Tests are won by the ones who aren't too proud to take them. [END]
[IF mitsue_in_party] MITSUE: (crawling) Honestly, this is the most dignified thing I've done all week. [END]
[IF tamotsu_in_party] TAMOTSU: (crawling, puffing) The Ide have no shame! It's our great strength! [END]
[IF haruki_in_party] HARUKI: (crawling, counting) …Five snakes. Fire, water, air, earth, void. (beat) Oh. That's
probably not what they mean. [END]
[IF gendo_in_party] GENDO: (crawling, spectacles askew) For the record, I'm only doing this for the evidence. [END]
[SET crawl_results]

## S07 — The Judgement
MAP: `serpent_mouth` · TRIGGER: after the sand room
(A giant stone serpent's open mouth. Beyond it, darkness — and a voice with no body, vast and slow.)
THE VOICE: Who comes to the den of the Order?
SAYO: Sayo. Of nowhere in particular.
THE VOICE: (a long pause, like a tide turning) …No line. No lord. No family name.
THE VOICE: Then you are free to carry what no line can.
SAYO: That sounds heavy.
THE VOICE: It is.
[SAVE] (inside the serpent's mouth, before the way out)

## S08 — The Order's Enforcers (BOSS)
MAP: `snake_den_2` · TRIGGER: leaving the serpent's mouth
(Enforcers with snake tattoos block the way out. Shadows crawl off the walls and become snakes.)
SNAKE ENFORCER: A spy! The Voice spoke to a *spy*!
SAYO: I'm not a spy. Spies are better dressed.
[BATTLE b_boss_snake_enforcers]
### Barks
- Shadow-snake summons (every 2 turns): SNAKE ENFORCER: "Rise, children of the den!"
- Jinnai's paralysis strike: JINNAI: "Forgive me, brother. Lie still a moment."
- First enforcer broken → JINNAI (stepping between): "Enough! She passed the judgement! The Voice spoke to her!" (battle won)
> CHOICE "The Order's secret"
  - "I'll keep it." → [SET order_promise kept]
  - "I won't promise anything." → [SET order_promise refused] (Jinnai trusts her anyway; the Order watches)

## S09 — Ending
MAP: `floating_flowers` (dawn) · TRIGGER: after the boss
(Dawn on the jetty. Jinnai sits heavily, his old wound reopened.)
JINNAI: My family guarded a secret on the Mountain of the White Snow. For three hundred years.
JINNAI: I'm the last of them. And this wound won't let me climb.
JINNAI: The Order isn't mine to give you. (pressing the snake beads into her hand) The mountain is.
JINNAI: Climb it for me, wave-girl. Find out what my family was guarding. Then decide whether it should stay guarded.
SAYO: And you?
JINNAI: (smiling) I'll go back to my shrine. The Osano-Wo monks will want to know why I'm late.
SAYO: Will you be all right?
JINNAI: (standing, with effort) I'm a lay brother of the thunder fortune. We're very hard to kill. It's mostly stubbornness.
[ITEM +Snake Beads (key item)]
[CHAPTER COMPLETE]
### Chapter complete card
**"The Noble and the Ronin" — complete.**
Journal: *Branded a bandit for helping a stranger, Sayo crawled through a snake-cult's sand on her belly and was told
she belongs to no one — which, it turns out, is exactly why the mountain needs her.*
[UNLOCK] Rank 2 (second ronin technique) · *Striking as Void* at the Lv 25 pick

---
## Travel Banter unlocked by Ronin Ch2
### TB-ronin2-a "Radish" (Sayo + Rensei)
RENSEI: Your wanted poster…
SAYO: Don't.
RENSEI: The artist gave you a remarkable nose.
SAYO: Rensei.
RENSEI: (straight-faced) Very noble. Very bold. A nose for the ages.
SAYO: (laughing, shoving him) I liked you better when you were stiff.
### TB-ronin2-b "Stubbornness" (Sayo + Jinnai, guest)
SAYO: Your order fights with fists and thunder.
JINNAI: And patience. Mostly patience. The thunder only comes once the patience runs out.
SAYO: How long does yours last?
JINNAI: (considering) About three insults. Lord Sadanobu used all three in one sentence. Very efficient.
