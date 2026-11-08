# PRODUCTION — Crab Ch3 · "Beyond the Wall"

**Traveler:** Hiruma Natsuko · **Lv** 30–35 · **Outline:** `scripts/crab-ch3-beyond-the-wall.md`
**Flags read:** `nezumi_friends`, `hidden_ones_cleared`, `oni_named_ryozo`, `blue_flare_held` · **Flags set:**
`guard_rescued`, `kage_fought`
**Maps:** `wall_gate_dawn`, `trap_tunnels_wall`, `sl_tar_chasm`, `sl_lava_trees`, `sl_poppy_fields`, `sl_watchpost`,
`toshi_no_kijo`, `sl_plain`, `sl_road_home` · **Storyboard:** `storyboards/crab-ch3.md`
**Battles:** `b_sl_goblins`, `b_sl_onikage`, `b_sl_akutsukai` (on a failed hide), `b_boss_kommei`
**Gimmick:** Oni no Kommei swaps two travelers' commands. Taint is a standard status.

---

## S01 — Told, Not Shown
MAP: `wall_gate_dawn` · TRIGGER: start
(Grey dawn at the Wall gate. HIDA SACHIKO waits, for once not smiling.)
HIDA SACHIKO: Hiruma. The Phoenix girl. Mutsuye.
HIDA SACHIKO: She went up to the women's shrine last night. She didn't come down.
NATSUKO: (very still) …She was Tainted. She couldn't bear it.
HIDA SACHIKO: And Kage-sama — he walked out through the Wall at first light. Alone. No armour.
HIDA SACHIKO: The sentries let him. He's their daimyo. What could they do?
(KAIU TAKAKANA arrives at a run, naginata over his shoulder.)
KAIU TAKAKANA: He's a daimyo, Hiruma. If he dies out there, the Hiruma line dies with him.
NATSUKO: Then I'll bring him back.
KAIU TAKAKANA: (beat) I didn't hear you volunteer.
KAIU TAKAKANA: Because I didn't order it. Because nobody would be fool enough.
(He presses a pouch of jade into her hands.)
KAIU TAKAKANA: Go.
[ITEM +Jade Pouch ×5 (cleanse Taint)]
[SAVE]

## S02 — The Trap Tunnels
MAP: `trap_tunnels_wall` · TRIGGER: descend
(Rollers, spikes, jade-dust lines. Natsuko steps through them like a dance.)
NATSUKO: Third stone. Skip the fourth. Never trust the fifth.
[IF nezumi_friends]
(At the tunnel's far mouth: a cluster of small glowing eyes.)
SQUEAK: Scout-who-fights-at-night! We know dark-ways! Rats always know dark-ways!
SQUEAK: (unrolling a hand-drawn map on bark) Squeak draw! Is good-good map!
NATSUKO: (looking at it, then at her father's) …It matches. The first leg. Your map and my father's.
SQUEAK: (proudly) Squeak smart-smart.
[GUEST +Squeak] (skills: Pocket Sand — Blind 1 enemy, 2 uses; field: *Dark-ways* — chests show on the map)
[ELSE IF hidden_ones_cleared]
(GONTA and two of the Hidden Ones, at the tunnel mouth with packs.)
GONTA: You said if you ever needed a landslide. (grinning) I've been bored for a month.
[GUEST +Gonta] (skill: Landslide — Earth damage to all enemies, 1 use)
[END]
(Prompt at the tunnel's far mouth: "Beyond the Wall there is no turning back until you reach home. Prepare.")

## S03 — The Upside-Down Forest (dungeon, part 1)
MAP: `sl_tar_chasm` → `sl_lava_trees` → `sl_poppy_fields` · TRIGGER: enter the Shadowlands
NARRATION: The Shadowlands. The land itself is the enemy here. Every breath costs a little of who you are.
### Status — Taint (Shadowlands tiles)
"Every step on corrupted ground can add **Taint**. Jade and shrine-stones cleanse it."
(A tar chasm and a rope bridge. Then the Lava Trees — a forest growing roots-up, branches buried, dripping fire.)
NATSUKO: (checking her father's map, landmark by landmark) "Tar chasm. Rope bridge. The forest that hangs." (beat) …It's here.
NATSUKO: It's all here. Every mark.
[BATTLE b_sl_goblins]
(The poppy fields: red flowers with teeth, turning to follow them.)
[BATTLE b_sl_onikage] (demon horses)
(A ridge. Natsuko stops, kneels, and marks the map with charcoal, her hand shaking.)
NATSUKO: (very quietly) He wasn't a fool. He was *right*.
NATSUKO: Thirty years, and he was right. There's a road.
[IF any_ally] ALLY: "…Natsuko?" NATSUKO: (wiping her eyes with a filthy sleeve) "Shadowlands dust. Very irritating." [END]
[SAVE] (a Hiruma waystone — shrine)

## S04 — The Broken Guard
MAP: `sl_watchpost` · TRIGGER: on the route
(A ruined Hiruma watchpost. A guard huddles in the corner, half-Tainted, muttering a patrol report from years ago.)
BROKEN GUARD: …all quiet in sector four… all quiet… all quiet…
NATSUKO: (kneeling) Brother. What's your name?
BROKEN GUARD: …Hiruma… Hiruma something. (laughing, wrong) I forgot it on purpose. Things can't call you if you've forgotten your name.
> CHOICE "The guard"
  - "Give him mercy." (the Crab way)
      NATSUKO: (gently) You've kept the watch long enough. I'll take it from here.
      (A clean stroke, off-screen. She leaves his patrol report under a stone.)
  - "Carry him home." → [SET guard_rescued] (slower; he survives, half-mad)
      NATSUKO: Up you get. You're coming off watch.
      BROKEN GUARD: (as she lifts him) …Off watch? Nobody comes off watch.
      NATSUKO: Today somebody does.

## S05 — Toshi no Kijo
MAP: `toshi_no_kijo` · TRIGGER: arrive
(A troll-ruin coliseum. Broken pottery everywhere. HIRUMA KAGE — a warrior-poet, haggard, armourless — hurls a jar against a pillar.)
HIRUMA KAGE: (not turning) Go home, scout.
NATSUKO: You first, my lord.
HIRUMA KAGE: Fifteen generations of Hiruma without a home. One woman made me forget it for a month.
(Another jar, shattering.)
HIRUMA KAGE: I'm done remembering.
NATSUKO: (holding out her father's map) Then remember this.
NATSUKO: There's a road back, my lord. My father found it. I walked the first leg this morning. It's real.
HIRUMA KAGE: (laughing, terribly) A road. To a castle full of oni.
NATSUKO: A road. To *home*. (beat) If you die here, who walks it?
(Long silence. Kage takes the map. He unrolls it in the dust and looks at it for a long time. Then he sits down, and
for the first time since the court, he weeps.)
NATSUKO: (sitting beside him, not touching him; looking at the sky) …I'll keep watch.
HIRUMA KAGE: (through tears) You always keep watch.
NATSUKO: Someone has to.
(Kage walks with the party from here as a follower. He doesn't fight random battles.)
[SAVE] (a second Hiruma waystone, half-buried in the coliseum sand)

## S06 — Riders Without Faces
MAP: `sl_plain` · TRIGGER: the way home
(Winged undead riders sweep the plain — Moto akutsukai, skeletal wings over rotting horses.)
NATSUKO: Down. Flat. Don't breathe.
### Hide prompt (one Stealth check, using the party's best Stealth; [IF guard_rescued] −2 rank: you're carrying him)
- Success → they pass overhead.
- Failure → [BATTLE b_sl_akutsukai] (hard)
[IF oni_named_ryozo]
(One rider lingers. It wears polished Imperial armour — Seppun colours — over something that isn't a man. It turns
its head toward their hiding place.)
"RYOZO": (a door-creak voice) …I have a name now, scout.
"RYOZO": A good one. Imperial. (pleased) Thank you for leaving it for me.
NATSUKO: (frozen) …Ryozo.
"RYOZO": (savouring it) Ryozo. (it rides off into the dark, laughing)
NATSUKO: (to herself, sick) I left him in that tunnel. I left a name in the dark, and something picked it up.
[END]

## S07 — The Patrol That Isn't (BOSS)
MAP: `sl_road_home` · TRIGGER: near the Wall
(A Crab patrol on the road ahead — Hida mon, torches. The relief is enormous. Then the patrol leader turns, and on the
back of his head is a second face, smiling.)
NATSUKO: That's not a patrol. That's a costume.
ONI NO KOMMEI: (both faces speaking) Hiruma! We've come to bring you home!
> CHOICE "Kage"
  - "Fight beside me, my lord." → [SET kage_fought] (Kage joins this battle: strong, takes huge damage)
      HIRUMA KAGE: (rising, taking up a fallen tetsubo) Finally. Something I'm allowed to break.
  - "Stay back. That's an order." → (harder; Kage obeys a Hiruma scout for once)
      HIRUMA KAGE: (a long look, then a nod) …Yes, scout.
[BATTLE b_boss_kommei]
### GIMMICK — body-swap
"Every third turn the Kommei **swaps two travelers' commands** for 2 turns. Break **the face on the back of its
head** to stop the swaps."
### Barks
- Swap: ONI NO KOMMEI: "Which of you is which? Do you even know?" NATSUKO: "I'm the one hitting you."
- [IF swap gives Natsuko a healer's command] NATSUKO: "I don't know how to *heal*! …Oh. Oh, that's nice."
- Back-face broken: ONI NO KOMMEI: (one face screaming) "My other self! You've blinded my other self!"
- Defeat: (it unravels into two shadows, which fight each other as they fade)

## S08 — Ending
MAP: `wall_gate_dawn` (dusk) · TRIGGER: reach the Wall
(Dusk. The Wall gate. Sentries cheer when they see Kage. Takakana stands at the top of the steps and says nothing,
which from Takakana is a parade.)
[IF guard_rescued] (Behind them the broken guard, wrapped in Natsuko's cloak, steps through the gate. A sentry
recognises him and drops his spear.) SENTRY: "…Uncle?" [END]
HIRUMA KAGE: (giving Natsuko back the map) Keep it.
HIRUMA KAGE: (taking it back) No. I'll keep it. Someone of rank should carry it.
HIRUMA KAGE: (beat) You'll walk beside me when we use it.
NATSUKO: (bowing, so he won't see her face) Yes, my lord.
(A messenger meets them inside: the court has already arranged Kage's next marriage. To the late bride's dearest
friend. Asako Kuhime.)
NATSUKO: (to herself, very quietly) …The one with grey mud on her hem.
[CHAPTER COMPLETE]
### Chapter complete card
**"Beyond the Wall" — complete.**
Journal: *Natsuko followed her grieving lord into the Shadowlands and found her father's road was real. She brought
Kage home — and learned that a name left in the dark doesn't stay lost.*
[UNLOCK] Map of the Road Home (key item, held by Kage) · *Stance of the Wall* kata at the first pick after Lv 41

---
## Travel Banter unlocked by Crab Ch3
### TB-crab3-a "The Road" (Natsuko + Tamotsu)
TAMOTSU: Your father's map. Was the road real?
NATSUKO: The first leg was.
TAMOTSU: Then it's real. (smiling) Merchants know: if the first leg of a trade route exists, the rest is just walking.
NATSUKO: Through oni.
TAMOTSU: Every trade route has oni. Mine just wear silk.
### TB-crab3-b "Names" (Natsuko + Haruki)
NATSUKO: Something took a man's name in the dark. Because I left him there.
HARUKI: (quietly) I took half a girl's soul because I was eight and angry.
NATSUKO: …That's not the same.
HARUKI: No. But we both keep looking back at the dark. (beat) Maybe it helps to look back at it together.
