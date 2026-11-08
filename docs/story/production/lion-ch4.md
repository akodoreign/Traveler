# PRODUCTION — Lion Ch4 · "Sorrow's Path"

**Traveler:** Akodo Shizue · **Lv** 41–45 · **Outline:** `scripts/lion-ch4-sorrows-path.md`
**Flags read:** `shogen_joined`, `atsuko_promise`, `yachiko_letters`, `tadanobu_letters`, `rensei recruited`,
`toturi_knows_name`, `phoenix_supply_proof` ·
**Flags set:** `go_between` (rensei / atsuko / shizue), `gusai_held`, `obsidian_blade_taken`, `report_truth`, `three_clan_truce`
**Maps:** `lion_camp_ford`, `camp_night`, `riverbank`, `the_ford`, `courtier_tent`, route `sorrows_path_road`
**Storyboard:** `storyboards/lion-ch4.md` (camp shops Lion T4; NPC path-action table)
**Battles:** `b_gusai_duel` (Duel), `b_ford_waves_1–5`, `b_boss_rokuro_demon`
**Set-piece:** hold the ford (5 defence waves)

---

## S01 — The Same Ground
MAP: `lion_camp_ford` · TRIGGER: start
NARRATION: Kanashimi no Komichi. Sorrow's Path. Centuries ago a Lion general won here, and the Crane never forgave the river.
(A Lion camp on the east bank. Across the water, Crane banners. Uncle AKODO HIRUTO, calm. Cousin AKODO GUSAI,
pacing. The Matsu vanguard under MATSU ROKURO — a huge, gentle-faced champion — sharpening a blade.)
AKODO HIRUTO: The same ground. Both armies. Again.
SHIZUE: The same banner, too, uncle. The one the oni stole at Shiro Akodo — it was taken *here*, centuries ago.
AKODO HIRUTO: (dryly) Then the river has a long memory.
[IF shogen_joined]
AKODO SHOGEN: (muddy, grinning, in the command tent) Every Lion general who died here thought he was winning.
AKODO SHOGEN: (beat) Think the other thing, girl.
[BUFF "Old Lion's Counsel" (+10% party damage this chapter)]
[END]
(An "Imperial observer" in muted silk takes a seat by the command tent, smiling: MIYA YACHIKO.)
MIYA YACHIKO: Akodo Shizue. We meet again. The Emperor so values peace.
SHIZUE: (bowing exactly as deep as courtesy requires) So I've read, magistrate. In your letters.
MIYA YACHIKO: (the smile doesn't move) …How diligent of you.
[SAVE]

## S02 — The Forged Apology
MAP: `camp_night` · TRIGGER: night
(A Crane envoy's apology letter, delivered to Hiruto at dusk, has become a vile insult by the time Hiruto reads it.)
AKODO HIRUTO: (reading; handing it to Shizue) The Crane general calls my late wife a fishwife.
SHIZUE: (examining the seal) The wax was lifted and pressed again. Someone swapped the letter on the road.
### Path actions (camp)
- Talk to the courier (any party) → "A lovely courtier met me at the ford. She offered tea." · [PA Discern] or
  [PA Eavesdrop] adds: "Blue eyes. He can't stop thinking about them."
- Sentry → "A woman with very blue eyes. She went into the Crane camp too. Yesterday."
- Yachiko's tent → [Eavesdrop] YACHIKO (to her servant): "Two letters. Two insults. Two armies. Elegant." (she's *pleased*, not the author)
SHIZUE: (laying the letters out by lantern-light — Yachiko's, and [IF tadanobu_letters] Matsu Tadanobu's [END])
SHIZUE: The Imperial magistrate feeds both armies lies. A Lion pays Mantis pirates to bleed the Crane.
SHIZUE: And now a blue-eyed woman swaps their letters. (beat) Three hands. All pushing toward this river.
### "Same method twice"
SHIZUE: (very still) …She swapped the Crane's apology. She uses the same method twice.
SHIZUE: Then she swapped *our* letter too. Uncle — you sent the Crane a peace letter yesterday.
AKODO HIRUTO: (slowly) I did.
SHIZUE: They've read it by now. And it didn't say peace.
SHIZUE: Someone has to cross the river before dawn and tell them what it really said.

## S03 — Across the River
MAP: `riverbank` · TRIGGER: choose the go-between
> CHOICE "Who crosses?"
  - [IF rensei recruited] "Rensei." → [SET go_between rensei] (a crossroads beat)
      RENSEI: I'm on my way to Kyuden Doji anyway. (smiling) I'll take the scenic route. Through the enemy camp.
      SHIZUE: If they shoot you—
      RENSEI: I'll bow first. Crane hate shooting someone mid-bow. It's rude.
  - [IF atsuko_promise honest] "Daidoji Atsuko." → [SET go_between atsuko]
      DAIDOJI ATSUKO: (appearing out of the reeds) You told me one true thing in my cell, Lion. Here's mine: I'd have crossed anyway.
      DAIDOJI ATSUKO: (beat) But I like that you asked.
  - "I'll go myself." → [SET go_between shizue] (the hardest: Gusai or Hiruto holds the ford with weaker buffs)
      AKODO HIRUTO: (handing her his own white truce-fan) Then go. And Shizue — come back.

## S04 — Gusai
MAP: `camp_night` (Gusai's tent) · TRIGGER: after S03
(The Matsu champion Rokuro walks the camp at night, eyes glassy, murmuring. His voice is wrong.)
MATSU ROKURO: (to the river) …charge at dawn… charge… they'll all be afraid… so afraid…
SHIZUE: (internal) He's ridden. Something in him. It'll charge at dawn whatever the letters say.
(Gusai's tent. Gusai, armoured, eager.)
AKODO GUSAI: Rokuro charges at dawn. I'm going with him.
AKODO GUSAI: I started this war in one night, cousin. Let me end it in one morning.
SHIZUE: You can't end a war by starting a battle.
SHIZUE: (drawing) I'll prove it on you if I have to.
> path actions
  - [PA Duel Gusai] [BATTLE b_gusai_duel] (non-lethal) → [SET gusai_held]
      AKODO GUSAI: (on his knees in the mud, laughing bitterly) …You were always the better player.
  - [IF Rank ≥ 3 AND toturi_knows_name] Command dialogue (Toturi knows her name: she can invoke his authority) → [SET gusai_held]
      SHIZUE: Akodo Gusai. Your lord, your father, and your cousin order you to hold.
      AKODO GUSAI: (a long breath) …Holding.
### The obsidian blade
(On Gusai's weapon rack: a black, glassy blade.)
AKODO GUSAI: A Crane deserter sold it to me. Obsidian. He said it kills fear-demons.
SHIZUE: (not touching it) Obsidian is a corrupt man's tool, cousin. It eats the hand that holds it.
> CHOICE "The obsidian blade"
  - "Take it. Just in case." → [SET obsidian_blade_taken] [ITEM +Obsidian Blade (each use: Taint +1 to user)]
  - "Leave it." → (nothing)
[SAVE]

## S05 — Hold the Ford (set-piece)
MAP: `the_ford` (dawn) · TRIGGER: dawn
### SYSTEM — the defence waves
"**Hold the ford** for 5 waves until the go-between reaches the Crane general. **Knock down** and **subdue** Lion
berserkers — don't kill your own."
(Dawn. Mist on the water. Rokuro roars — and the Matsu vanguard charges, Crane horns answering.)
SHIZUE: (Command) Lion! Lock shields across the ford! NO ONE CROSSES!
- [BATTLE b_ford_waves_1] Matsu berserkers charging by mistake — SHIZUE: "Knock them down! They're ours!"
- [BATTLE b_ford_waves_2] Crane counter-charge — SHIZUE: "Hold! Don't pursue! Don't give them a reason!"
- [BATTLE b_ford_waves_3] Archers on the far bank — SHIZUE: "Formation! Shields high!" (Akodo Formation)
- [BATTLE b_ford_waves_4] The burning bridge (fire tiles) — "The bridge is burning — fall back to the stones!"
- [BATTLE b_ford_waves_5] The demon's terror wave (party Terror) — SHIZUE (Battle Cry): "Fear is a rumour! Hold!"
[IF go_between rensei] (Mid-wave, across the water, a white-clad figure walks through the Crane lines, bowing to
every spear.) [END]
[IF go_between atsuko] (A Crane scout's whistle across the water — three notes. "She's through.") [END]
- Between waves: a "Hold" pause (items, kata, guest swap; no save). The wave battles are normal battles.
(After wave 5 the mist lifts. [SAVE])

## S06 — The Possessed Champion (BOSS)
MAP: `the_ford` · TRIGGER: after wave 5
(Rokuro wades into the middle of the ford alone, roaring, and the thing inside him shows in his eyes — black, wide,
hungry. Both armies cower.)
THE DEMON (in Rokuro's voice): You're afraid, little strategist. I can *taste* it.
SHIZUE: Of course I'm afraid. (Command: "Now!") Only fools and Matsu aren't.
SHIZUE: (beat) Sorry, Rokuro-san.
[BATTLE b_boss_rokuro_demon]
### Barks
- Terror aura: THE DEMON: "Run. Everyone runs from Sorrow's Path eventually."
- Jade hit: THE DEMON: "Burns — it burns —"
- [IF obsidian_blade_taken] obsidian strike: (big Suki damage; a black vein crawls up the user's arm) "…That felt *wrong*."
- Possession broken (victory): (Rokuro collapses into the shallows, himself again, weeping like a child)
MATSU ROKURO: …I was so frightened. All night. I was so frightened, and I couldn't stop walking.
SHIZUE: (helping him up) I know. You're out of the river now.

## S07 — One Battle
MAP: `the_ford` → `courtier_tent` · TRIGGER: after the boss
(In the middle of the ford, Hiruto and the Crane general meet, holding the *real* letters. The armies stand down.
Nobody cheers.)
CRANE GENERAL: (reading Hiruto's real letter) …This says peace.
AKODO HIRUTO: It always did.
[IF phoenix_supply_proof AND haruki_in_party]
HARUKI: (setting a charred, stamped crate lid on the truce table) General — the Phoenix have been supplying your army. In secret.
CRANE GENERAL: (stiffly) …That is not a matter for the Lion.
HARUKI: It is if the Phoenix want this war to last. (beat) I don't think they do. I think they're just afraid.
AKODO HIRUTO: (looking at the lid a long time) Then we have three clans at this table who'd rather not die here. That's a start.
[SET three_clan_truce] (finale Act 1: +1 Resolve damage in the shrine defence)
[END]
### Shizue's report to Toturi (by messenger)
> CHOICE "The report"
  - "The truth: the Lion charged first." → [SET report_truth] (Honor +1, Glory −1; recommended)
      SHIZUE: (dictating) "The Matsu vanguard charged first. Possessed, but ours. My own cousin's men were ready to follow."
      SHIZUE: "The Lion started this battle. The Lion should say so."
  - "Blame the demon alone." → (Glory +1, Honor −1)
(Yachiko, her letters exposed, is "recalled to the capital for consultation". She passes Shizue on her way to her
palanquin and smiles.)
MIYA YACHIKO: This won't be the last time, Akodo.
SHIZUE: No, magistrate. (beat) But it's the first time you lost.
### The courtier's tent
(A tent at the edge of the Crane lines, abandoned in the night. Inside: a Crane court mask. A pot of white hair-dye. A
smooth grey stone carved into the shape of a jade amulet.)
SHIZUE: (holding the stone up to the light) …It isn't jade. It's river stone. She couldn't tell the difference.
SHIZUE: (placing it on a map with the go stones she carries) North. And east. (beat) Shinomen.
(Hiruto, beside her, looking at the ford.)
SHIZUE: I couldn't stop the war, uncle. Only one battle.
AKODO HIRUTO: (rattling the go stones in his sleeve) One is enough today.
[CHAPTER COMPLETE]
### Chapter complete card
**"Sorrow's Path" — complete.**
Journal: *The same ford, the same banner, the same blue-eyed hand pushing both armies into the river. Shizue held the
ford through five waves, freed a frightened champion, and told her Champion the Lion charged first.*
[UNLOCK] *Gentle Blade of Winter* kata at Lv 51 · Atsuko in the finale callback · [IF obsidian_blade_taken] the Obsidian Blade

---
## Travel Banter unlocked by Lion Ch4
### TB-lion4-a "Fools and Matsu" (Shizue + Natsuko)
NATSUKO: "Only fools and Matsu aren't afraid." You said that to a possessed Matsu champion.
SHIZUE: He apologised afterwards. He agreed with me.
NATSUKO: (laughing) The Crab would agree too. We're just fools in better armour.
### TB-lion4-b "The Stone" (Shizue + Rensei; requires go_between rensei)
RENSEI: You put a river stone on your map like a go stone.
SHIZUE: Every place she's been. They're starting to make a shape.
RENSEI: What shape?
SHIZUE: (quietly) A noose. (beat) Around Shinomen Mori.
