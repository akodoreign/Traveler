# PRODUCTION — Phoenix Ch3 · "The Darkfever"

**Traveler:** Isawa Haruki · **Lv** 30–35 · **Outline:** `scripts/phoenix-ch3-the-darkfever.md`
**Flags read:** `consumer_scroll_kept`, `told_keiki`, `mieko_midnight_seen` · **Flags set:** `sick_treated` (0–8),
`stayed_extra_day`, `showed_scroll`
**Maps:** `kyuden_isawa` (city, Council hall), `fever_village_1–3`, `temple_hospital`, `isawa_mori_1–2`,
`mieko_estate`, `sealed_library`
**Battles:** `b_forest_fever_spirits`, `b_mieko_dark_mid`, `b_boss_oni_no_kuzushi` ("Off-Balance" gimmick)
**Fit conversion:** triage is path actions (Bless / Remedy / Path to Inner Peace on sick NPCs).
**Storyboard:** `storyboards/phoenix-ch3.md` (route `fever_road` links the villages and the temple hospital).
**Triage rule:** while the fever rages, the villages have **no inn**. The temple hospital allows one rest (the "stay
one more day" choice). SP comes from items and Haruki's VP-paid Void spells.

---

## S01 — The Sun Goes Out
MAP: `kyuden_isawa` · TRIGGER: start
NARRATION: Kyuden Isawa. The heart of Phoenix magic. On the first day of the Month of the Serpent, at noon, the sun went out.
(A solar eclipse. The city stops. Then every kami in Kyuden Isawa shrieks at once — a sound like a thousand bells cracking.)
HARUKI: (hands over his ears, falling to his knees) They're screaming — they're all screaming —
(Silence. Light returns. Townsfolk stare at the sky.)
(Days later. A messenger, gasping.)
MESSENGER: Fever, in the forest villages! People burning up in a night — dark veins — dying by morning!
MESSENGER: The Council says it's peasant dirt. It isn't dirt, Isawa-sama. It's *walking*.
(Mieko has left the city. Two envoys are still dead. The Council's investigators hunt for her in the wrong places.)
[SAVE]

## S02 — Fever Roads (path-action hub)
MAP: `fever_village_1–3`, `temple_hospital` · TRIGGER: travel to the villages
NARRATION: The forest villages. The Darkfever came with the eclipse. It came fast.
### The sick (8 NPCs; treating 5 opens the forest road) — each sets [sick_treated +1]
| NPC | Line | Treatment |
|---|---|---|
| Farmer Goemon | "My wife… can't see her own hands…" | Path to Inner Peace / Remedy (Ginseng + Moxa) |
| Child Hana | "Mama says the dark goes away if I'm good. I've been very good." | [PA Bless] → temple-hospital |
| Old charcoal-burner | "Leave me. Treat the young ones." | Remedy (Rhubarb purge) or Bless |
| Village priestess | "My prayers bounce off it. Like rain off stone." | Path to Inner Peace (VP 3: whole family) |
| A Lion deserter, hiding | "Don't tell anyone a Lion is here." | any treatment; *Discern*: "deserted from the Ch1 raid" |
| Twin boys | "We share everything. Even this." | mass Path to Inner Peace |
| Ferryman | "I carried the fever across the river. It's my fault." | Remedy |
| Ronin bodyguard | "My lord died last night. I'm meant to die with him." | [PA Bless] (he follows Haruki instead) |
### The dying healer (temple-hospital)
DYING HEALER: (pressing a scroll into Haruki's hands) It won't cure this. Nothing cures this.
DYING HEALER: But it'll teach you what "cure" means. (beat) Go and find the thing that started it.
[SPELL +Hand of Jurojin (story grant, ML4)]
> CHOICE (when leaving, once 5 are treated)
  - "Stay one more day." → [SET stayed_extra_day] (+2 villagers saved; the boss gains +1 Resolve)
      VILLAGE ELDER: (bowing to the ground) Bless you. Bless you.
  - "Go now." → HARUKI: (internal) Every hour I stay, it spreads further. I'm sorry. I'm so sorry.

## S03 — The Council's Hubris
MAP: `kyuden_isawa` (Council hall) · TRIGGER: return to report
(The Council of Elemental Masters. Masks of the five elements. The Master of Earth, ISAWA RUJO, waves a dismissive
sleeve.)
ISAWA RUJO: Peasant uncleanliness. They'll wash, or they'll die. Either way, it ends.
HARUKI: (very quietly) It spreads in a circle, Master. Dirt doesn't spread in a circle.
ISAWA RUJO: (not looking at him) Who is this?
COUNCIL CLERK: An acolyte, Master. Hoju's.
ISAWA RUJO: Hoju's. (sniffing) Hoju always kept strays.
(Outside the hall, on the steps: a tired Crane in an Emerald Magistrate's yoriki sash, eating a rice ball: DOJI HAYATO.)
DOJI HAYATO: The Masters say it's dirt.
HARUKI: Dirt doesn't spread in a circle.
DOJI HAYATO: (stopping mid-bite) …Show me the circle.

## S04 — The Circle
MAP: `kyuden_isawa` (Hayato's lodging, maps on the floor) · TRIGGER: auto
(Hayato's maps. Haruki casts Reflective Pool over a bowl of water. Village after village lights up, a ring spreading
outward from one point deep in the Isawa Mori.)
DOJI HAYATO: There. Your centre.
HARUKI: (staring; very still)
DOJI HAYATO: You know it.
HARUKI: …It's a house. A family's forest house. I was there once. When I was eight.
HARUKI: (barely audible) It's where I broke her.
DOJI HAYATO: Broke whom?
HARUKI: (closing his eyes) Isawa Mieko.
(Flashback flicker: a child's go board; a jealous little girl knocking the stones away; a boy's scream; light like
black glass tearing the room in half.)
HARUKI: My Void lashed out. It split her soul. (beat) And it cracked something under that house. Something that was sleeping.
HARUKI: The eclipse finished what I started.
DOJI HAYATO: (long pause) …Then you'd better finish it properly.
[SAVE]

## S05 — The Forest Estate
MAP: `isawa_mori_1–2` → `mieko_estate` · TRIGGER: go
(The Isawa Mori, the forest. Fever spirits drift between the trees like bruised smoke.)
[BATTLE b_forest_fever_spirits]
(The estate. Rotting gardens. A child's go board on the veranda, the game abandoned mid-move twelve years ago.)
### Flashback interactions (3 points; non-interactive replays)
- The go board: "Two children. A dispute over a captured stone."
- The broken screen: "A little girl laughing; a little boy, red-faced, shouting."
- The courtyard: "Light like black glass. A scream. Then two shadows where one girl stood."
(At the house's heart, sitting where the screen was broken, humming: Mieko's dark half. Black-glass eyes.)
MIEKO (DARK): Little Void. You came back to where you broke me.
HARUKI: Mieko—
MIEKO (DARK): You broke *more* than me, you know. (laughing) Can you hear it? Under the floor? It's been so grateful.
[BATTLE b_mieko_dark_mid] (she flees at 50%)
[IF consumer_scroll_kept]
> CHOICE "The Consumer scroll"
  - "Show it to her." → [SET showed_scroll]
      HARUKI: (holding it out) You wrote this. Your other half. A warning — about *you*.
      MIEKO (DARK): (staring at her own handwriting; she falters) …I don't remember writing this.
      HARUKI: She remembers you. She was afraid for you.
      (Mieko hesitates — one turn too long. Then she vanishes into the trees.)
  - "Don't." → (she escapes at once)
[END]
MIEKO (DARK): (leaving, her voice everywhere) It's waking up, little Void! Say hello for me!
[SAVE]

## S06 — Oni no Kuzushi (BOSS)
MAP: `mieko_estate` (the cellar beneath the house) · TRIGGER: descend
(A cellar older than the house. A seal of cracked jade in the floor, broken outward. A shape fills the dark like a body
falling down stairs forever: ONI NO KUZUSHI.)
ONI NO KUZUSHI: (a sound of something tumbling, endlessly) You opened my door, little Void.
ONI NO KUZUSHI: Twelve years ago. I waited so *politely*.
HARUKI: (Drawing the Void) Then I'll close it.
HARUKI: (beat) Politely.
[BATTLE b_boss_oni_no_kuzushi]
### GIMMICK — Unbalancing Breath
"Every 2 turns the oni breathes on one traveler: they are **Off-Balance** and **lose their next turn**, and the oni
**regains 2 Resolve**. Counter with *The Mountain's Feet*, Defend, a guest call, or turn-order tricks."
### Barks
- Breath: ONI NO KUZUSHI: "Fall down. Everyone falls down eventually."
- Off-Balance traveler: (stumbling) "My legs — I can't —"
- Darkfever aura (poison each turn): HARUKI: "Water heals clear it — stay close to me!"
- [IF stayed_extra_day] ONI NO KUZUSHI: "You stayed to save them. I grew while you were kind."
- At 25%: ONI NO KUZUSHI: "You'll do this again, little Void. You'll break something else. You always will."
- HARUKI: (mass Path to Inner Peace, VP 3) "Maybe. (beat) But not today."
(The oni collapses inward, tumbling down into nothing. The cellar seal glows, then goes dark and whole.)

## S07 — The Sealed Library (reward)
MAP: `sealed_library` · TRIGGER: return to Kyuden Isawa
(The fever ends in a week. The Council, grudging, opens the sealed library to "the acolyte who assisted the
magistrate". Haruki walks between shelves no one has touched in a century.)
HARUKI: (reading) "On the splitting and joining of souls." (beat) "Joining requires one of the halves to *want* it. And a giver."
HARUKI: (very quiet) …A giver.
(Another scroll: the destruction of the Snake Clan, by a Shuten Doji.)
HARUKI: (reading) "Obsidian against Fear. Jade against Regret. Crystal against Desire." (beat) "Obsidian corrupts the hand that holds it."
HARUKI: (to himself) Someone in the Ojatara valleys should read this. (He copies it.)
(The Master of Air, ISAWA UONA, a young woman newly raised to the Council, finds him there.)
ISAWA UONA: You're Hoju's boy. The one who counted the circle.
ISAWA UONA: The Council won't thank you. (holding out a scroll) So I will. Quietly.
ISAWA UONA: *Dreamwalker*. A secret of Air. (beat) I think you'll need to walk in someone's dreams soon.
[SPELL +Dreamwalker (First Tier)]
(Hayato's report to the Emerald Magistrates credits "the Isawa". Haruki's name isn't in it. Haruki reads it and smiles.)
HARUKI: (to Hayato) Thank you for leaving me out.
DOJI HAYATO: (puzzled) Most people want their names *in* reports.
HARUKI: I've been in one report already. (touching his sleeve, where the old note lies) It took twelve years to read.
[CHAPTER COMPLETE]
### Chapter complete card
**"The Darkfever" — complete.**
Journal: *An eclipse, a plague, and a circle drawn from a house where a boy once broke a girl. Haruki closed the door
he'd opened at eight — and learned that joining a soul needs a giver.*
[UNLOCK] *Hand of Jurojin*, *Dreamwalker* · Rank 3 at 41 (Mastery 4 spells; Void costs −1 VP while Attuned to Void)

---
## Travel Banter unlocked by Phoenix Ch3
### TB-phoenix3-a "The Circle" (Haruki + Gendo)
GENDO: You found the source by mapping where the dying were.
HARUKI: Doji Hayato did most of it.
GENDO: You saw it in a bowl of water. (beat) That's the most elegant piece of evidence I've ever heard of.
HARUKI: (pause) …It was a terrible thing to see.
GENDO: The best evidence usually is.
### TB-phoenix3-b "A Giver" (Haruki + Sayo)
SAYO: You read "joining needs a giver" and went white.
HARUKI: Did I?
SAYO: Like rice paper. (gently) You're going to give something, aren't you.
HARUKI: (after a long time) …Some of me. It seems fair. I took some of her.
SAYO: (nodding slowly) Then eat something first. Givers faint.
