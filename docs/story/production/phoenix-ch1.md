# PRODUCTION — Phoenix Ch1 · "The Silent Kami"

**Traveler:** Isawa Haruki · **Lv** 1–8 · **Outline:** `scripts/phoenix-ch1-the-silent-kami.md`
**Shared climax:** S08 = `production/lion-ch1.md` S07–S08 (Phoenix version below). If Shizue is absent, **Akodo
Ijako** stands in.
**Flags set:** `phoenix_supply_proof`, `shrine_spirit_blessed`, `apology_note_found`
**Maps:** `shiro_kamatori` (study, garden), `road_west_phoenix`, `magonojo_ruins`, `despoiled_shrine`,
`hiruto_castle_west_tower` (+ the shared maps)
**Battles:** `b_shrine_guardian_shards`, `b_ashimoshi` (mid-boss), `b_boss_otamai` (shared)
**Guest:** Shiba Ashimita (S03)
**Fit conversions:** none needed. The spirit wasteland is a map-wide passive.
**Storyboard:** `storyboards/phoenix-ch1.md` (adds the Kamatori castle-town screen; `hiruto_castle_west_tower` is a
3-floor tower with a save on 2F).
**Pair rule (P-1):** see `production/lion-ch1.md`. Played second, this is the flashback "That week…", with
`climax_route` locked. Played first, Shizue is a silent NPC at Hiruto's side if she isn't recruited.

### RECRUIT VARIANT (Haruki is not the starter)
**Join point:** `shiro_kamatori` courtyard, as the embassy musters (S03). Haruki is the young Isawa with too many
scrolls.
HARUKI: (dropping a scroll; picking it up; dropping another) Sorry — sorry. I'm carrying my teacher's papers. All of them.
HARUKI: (counting on his fingers without noticing) He died two nights ago. Maho. The kami won't speak to me since.
HARUKI: We're riding west, to the Lion. (beat) I'd feel braver with people who aren't Kamasari-sama.
> CHOICE "Travel with Haruki?" → Yes: **Memory** (S01–S02: the dictation, the salt, the scream, the silent garden) →
  resume at S03's Ashimita scene.
→ No: he waits in the courtyard.

---

## S01 — Counting on Fingers
MAP: `shiro_kamatori` (Hoju's study, evening) · TRIGGER: new game, Haruki chosen
NARRATION: Shiro no Kamatori. A Phoenix castle of five towers, where an old man is writing the history of a family
that doesn't want one.
(Lamplight. Scrolls everywhere. ISAWA HOJU, white-bearded, ink on his nose, dictates. HARUKI copies. His left hand
taps his fingers one by one on the desk: fire, water, air, earth, void.)
ISAWA HOJU: "…and in the third year, the family's shugenja bound a great evil in the west." No — "a grave evil." Grave.
HARUKI: Grave, sensei. (writing) …Sensei, what evil?
ISAWA HOJU: The kind one writes about only once. (beat) You're counting on your fingers again.
HARUKI: (hiding his hand) Sorry.
ISAWA HOJU: Five fingers, five elements. And when you run out of fingers?
HARUKI: Then I start again on the other hand, sensei.
ISAWA HOJU: (laughing) Ten elements! The Council will be thrilled. They'll make you a Master.
ISAWA HOJU: Go to bed, Haruki. History has waited four hundred years. It can wait until morning.
HARUKI: Yes, sensei. (at the door) Sensei — you'll go to bed too?
ISAWA HOJU: (already writing) In a moment.
### TUTORIAL — Field spells (garden, before bed)
- **Commune** (garden shrine): GARDEN KAMI: "The cook is putting too much salt in the soup again. Tell him. He never listens to us."
  HARUKI: (smiling) I'll tell him.
- **Summon** (a toppled candle in the hall): summon a little water → the flame hisses out.
- **Sense** (Hoju's lost brush): "Something wooden and well-loved, under the reading stand."
[SAVE]

## S02 — The Kami Fall Silent
MAP: `shiro_kamatori` (night) · TRIGGER: sleep
(A scream from the study. Haruki runs in. Hoju is slumped at his desk, his eyes bleeding — still holding the brush.)
HARUKI: Sensei! Sensei!
(Haruki casts Path to Inner Peace with shaking hands. Nothing. Hoju is already gone.)
(The garden. Haruki stumbles to the shrine. Commune.)
HARUKI: Please. Please answer. You always answer.
(Silence. Only wind in the pines.)
HARUKI: (whisper) …The cook. The salt. You always talk about the salt.
(Nothing. He counts his fingers — fire, water, air, earth, void. He counts them again.)
### Map-wide status — Spirit Wasteland
"The kami are afraid. **Spells are weaker here** (−1 tier)."

## S03 — The Lowest Member of the Embassy
MAP: `shiro_kamatori` (courtyard, morning) · TRIGGER: auto
(Phoenix riders muster. ISAWA KAMASARI, Hoju's nephew — sleek, furious, grief-proud — addresses them. Beside him: the
Imperial magistrate MIYA YACHIKO.)
ISAWA KAMASARI: Maho. In our own house. The trail leads west, to the Lion.
MIYA YACHIKO: The Emperor's interest is in the truth, Isawa-sama. I'll ride with you.
ISAWA KAMASARI: (seeing Haruki) You. You were his favourite.
ISAWA KAMASARI: You'll carry his papers. Try not to weep on them.
HARUKI: (bowing very low) Yes, Kamasari-sama.
ISAWA KAMASARI: (to his yojimbo) Ashimita. Keep the boy from falling off his horse.
(SHIBA ASHIMITA — lean, controlled, wincing at nothing — falls in beside Haruki on the road.)
SHIBA ASHIMITA: Ignore him. He's grieving, and he does it loudly.
HARUKI: You… you're in pain.
SHIBA ASHIMITA: My grandfather has been screaming in my ear since the day I was born.
SHIBA ASHIMITA: Kamasari is much quieter.
HARUKI: (hesitant) Could I try to… calm him? Your grandfather? I'm a shugenja.
SHIBA ASHIMITA: (a thin smile) Many have tried.
(Haruki raises his hands. Murmurs a prayer. Ashimita's face twists.)
SHIBA ASHIMITA: …He's louder.
HARUKI: Oh no. I'm so sorry—
SHIBA ASHIMITA: (and, unexpectedly, he laughs) No. No, that's the first time anyone's made it *worse*. He's furious.
SHIBA ASHIMITA: Thank you. That was almost refreshing.
(Haruki laughs too — the first time since Hoju died.)
[GUEST +Shiba Ashimita] (skills: Guardian — protect an ally, 2 uses; Grandfather's Storm — sense hidden spirits, 1 use)

## S04 — The Jade Chains (required before leaving; the note is optional)
MAP: `shiro_kamatori` (Hoju's study) · TRIGGER: examine the chest under the desk
(If the player heads for the gate first: SHIBA ASHIMITA: "Kamasari said carry *all* his papers. Even the heavy ones.")
(Under the tea things: a coil of jade chain, broken links, a lock. The lock is warm in his hand — and cold when he
turns toward the west window.)
HARUKI: (reading Hoju's notes) "Kaiki. Fifteen. We had no other way." (beat) "I forged the chains. I have never
forgiven myself for the boy."
[ITEM +Jade Chains (key item — compass)]
(Beneath the chains, a small folded paper in a child's handwriting. Interaction (optional): "Take the folded paper?")
(Haruki recognises the handwriting. He doesn't unfold it. He puts it in his sleeve.)
[SET apology_note_found]

### Town NPCs — `shiro_kamatori` (castle town, storyboard pass)
| NPC | Default line | Info | Path action |
|---|---|---|---|
| The cook | (after S02) "Nobody's complained about the salt since…" | — | — |
| Shiba guard | "The towers have never fallen. Not once." | — | *Duel* (Iaijutsu 1): Glory +1 · Oak Bo |
| Scroll-copier | "Hoju-sama's hand was the best in the castle." | *Eavesdrop:* "Kamasari owes the Crane money." | *Charm:* follows ("Ink Ward", a small shield, 1 use) |
| Old nun | "The shrine won't take my prayers." | — | *Bless:* Rejuvenating Tea ×2 |
| Pilgrim | "I came for the five towers. They're very tall." | — | *Barter:* Incense ×2 · *Pilfer:* Pilgrim's Token |
| Stable boy | "Horses don't like it here any more." | — | *Sumai:* "The magistrate's servant left at night, westward, before the embassy." |

## S05 — What the Phoenix Burned For
MAP: `magonojo_ruins` · TRIGGER: travel west
(Blackened warehouses on the Magonojo river. Kamasari's men pick through the ash.)
HARUKI: (Reflections of Pan Ku on a charred crate) …Crane army supply marks. Rice. Arrows.
HARUKI: The Phoenix were supplying the Crane army. Secretly.
ISAWA KAMASARI: (sharply) Throw those crates in the river.
SHIBA ASHIMITA: (quietly, to Haruki) Sensei never told you.
HARUKI: No.
SHIBA ASHIMITA: Sensei was a historian. Historians know which things not to write down *yet*.
> CHOICE "The crate lid"
  - "Keep a stamped lid." → [ITEM +Stamped Crate Lid] [SET phoenix_supply_proof]
  - "Let it go." → (nothing)

## S06 — The Broken Shrine
MAP: `despoiled_shrine` · TRIGGER: on the road
(A smashed roadside shrine. The jade-chain lock is freezing here. An old shrine-keeper's ghost wanders the rubble,
straightening stones that won't stay straight.)
SHRINE-KEEPER'S GHOST: They broke it. Lions. Soldiers. They broke it and *it* got out. I must fix it. I must fix it.
### TUTORIAL — Path Action: Bless
"**Bless** — guide an NPC (living or dead) to follow you. Who will follow depends on your **Theology** rank."
[PA Bless Shrine-Keeper's Ghost] →
HARUKI: You've kept it long enough, grandfather. Let me carry it now.
SHRINE-KEEPER'S GHOST: (pause) …You'll fix it?
HARUKI: I'll find what got out. That's the fixing.
(The ghost bows and fades into a calm light.) [SET shrine_spirit_blessed]
(The shrine's broken guardian-stones lurch upright.)
[BATTLE b_shrine_guardian_shards]
### TUTORIAL — Void & mass healing
- T1: "Haruki's Affinity is **Water and Void**. **Void spells cost VP**, not SP — and grow stronger the more VP you hold."
- T2: "**Drawing the Void** — gain VP right now (free, once per battle)."
- T3: "Boost **Path to Inner Peace** with 3 VP to heal the **whole party**."
HARUKI: (after) Sensei always said Void was the element that holds the others together.
SHIBA ASHIMITA: And?
HARUKI: (looking at his hands) …I've never been very good at holding things together.
[SAVE]

## S07 — The Silent Hurricane (mid-boss)
MAP: `hiruto_castle_west_tower` · TRIGGER: arrive at Lord Hiruto's castle (or, if Lion Ch1 is done, the Lion family
greets them)
(The west tower. Wind howls — and makes no sound. A samurai's ghost spins in the centre of a silent storm:
ASHIMOSHI.)
SHIBA ASHIMITA: (doubling over) He's screaming. Can't you hear him?
HARUKI: No. (beat) Yes. In the wind. He's screaming in the wind.
[BATTLE b_ashimoshi]
### Barks
- ASHIMOSHI (in silent-storm text, shaking on screen): ……………!
- Every other turn: "The silent wind smothers your voice — **spells sealed**."
- HARUKI (when seal lifts): "Now — while he breathes!"
(Victory. The storm settles. Ashimoshi's ghost stands calm for the first time in years.)
ASHIMOSHI: (a voice like a held breath let go) …Thank you.
ASHIMOSHI: The one in the sleeping man. Across the yard. (pointing west, toward the barracks)
ASHIMOSHI: He has been eating us.

## S08 — Crossroads: O-Tamai
→ **Play `production/lion-ch1.md` S07–S08.**
- If Shizue is in the party, the full shared version plays, and Haruki's lines are marked `[IF haruki_in_party]`.
- If Shizue is absent, **Akodo Ijako** takes Shizue's role. Route **A (Binding)** is used automatically. Line
  swaps:
  - IJAKO replaces SHIZUE's "We'll take it in jade." with: "The dead want their house back, spirit."
  - Haruki's binding line plays as written in lion-ch1 S08.

## S09 — The Note
MAP: `shiro_kamatori` (Hoju's study, night) · TRIGGER: return home
(The study is cleaned. Hoju's desk is bare. The Council has thanked Kamasari. No one mentioned Haruki.)
(He sits at the empty desk and takes the folded paper from his sleeve. Unfolds it.)
(A child's brushwork, wobbly, pressed hard into the paper:)
NOTE: "I'm sorry, Mieko. I didn't mean to. Please wake up."
HARUKI: (very quietly) …You kept this. Twelve years.
HARUKI: You knew, sensei. You knew all along. And you never said a word.
(He counts on his fingers. Fire. Water. Air. Earth. He stops at five. He doesn't start again.)
(A knock: a messenger. The Phoenix will hold a Silent Court in Hoju's memory. Every clan will send envoys.)
MESSENGER: The ceremony masters have been named. The second is a priest from the north. Isawa Mieko.
(Haruki's hand closes over the note.)
[CHAPTER COMPLETE]
### Chapter complete card
**"The Silent Kami" — complete.**
Journal: *His teacher murdered by maho, Haruki followed the silence west, bound a Bloodspeaker in jade — and found,
in his teacher's chest, a note he wrote at eight years old. Now the girl he wrote it to is coming to Hoju's court.*

---
## Travel Banter unlocked by Phoenix Ch1
### TB-phoenix1-a "Salt" (Haruki + Sayo)
SAYO: You told the cook he uses too much salt? The cook here?
HARUKI: The kami told me. The kami at home. They always complained about the salt.
SAYO: (tasting the inn's soup, grimacing) …Your kami have good taste. Want to tell this cook too?
HARUKI: (laughing) I'd need a much braver kami.
### TB-phoenix1-b "Grandfather" (Haruki + Ashimita, guest)
SHIBA ASHIMITA: He's quieter when you're near.
HARUKI: Really? I made him louder before.
SHIBA ASHIMITA: You made him angry. Now he's curious. I think he's trying to work out what you are.
HARUKI: (pause) …So am I.
