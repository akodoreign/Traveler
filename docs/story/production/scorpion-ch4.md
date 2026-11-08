# PRODUCTION — Scorpion Ch4 · "The Eve" (Crossroads: Tamori's Furnace)

**Owner:** Shosuro Mitsue · **Partner:** Kitsuki Gendo (else stand-in **Togashi Yosai** — or **Tamori Haku** while
Yosai is lost in the ink: Dragon Ch2 done, Ch4 not) · **Lv** 41–45 · **Storyboard:** `storyboards/scorpion-ch4.md`
**Outline:** `scripts/scorpion-ch4-the-eve.md`
**Flags read:** `iron_box_held`, `mitsue_knows_shoju_war`, `mitsue_wore_giseiki` · **Flags set:**
`courier_heard`, `togashi_heard`, `gendo_keeps_secret`, `box_destroyed`
**Maps:** `dragon_mountain_town`, `mountain_inn`, `togashi_road`, `kyuden_togashi_garden`, `tamori_furnace_1–2`,
`crater_mouth`
**Battles:** `b_furnace_elementals`, `b_ash_ghouls`, `b_boss_stolen_face`
**Paraphrase rule:** Togashi's canon answer is **paraphrased**, never quoted.

---

## S01 — The Box Is Talking Again
MAP: `dragon_mountain_town` (inn room, night) · TRIGGER: start
(The iron box on the floor beside Mitsue's futon. Lid closed. It speaks — in her own voice.)
IRON BOX (Mitsue's voice): Open me. You're so tired of being nobody.
IRON BOX (Mitsue's voice): I could make you everyone.
MITSUE: (sitting up, to the box) Everyone is exactly the problem.
(A letter from Norie, by the lamp.)
SHOSURO NORIE (letter): The only fire hot enough is Tamori's Furnace, in Dragon lands. Destroy it there.
SHOSURO NORIE (letter): And Mitsue — whatever you hear on the road, keep walking.
MITSUE: (folding it) …That's an odd thing to write, sensei.
[SAVE]

## S02 — A Troupe of Pilgrims
MAP: `dragon_mountain_town` · TRIGGER: morning
(Mitsue leads a "pilgrim troupe" through the Dragon mountains: Many Faces, a grey pilgrim's face.)
[IF gendo_in_party]
GENDO: (falling in beside her) I know the path to the Furnace. And the Tamori monks who tend it.
GENDO: I'll want to know what's in the box.
MITSUE: You won't like it.
GENDO: (polishing his spectacles) I'll settle for knowing what it *does*.
[ELSE IF dragon_ch2_not_done OR dragon_ch4_done]
TOGASHI YOSAI: (appearing from behind a shrine, munching a persimmon) A cursed box of a Bloodspeaker's heart! In my mountains!
TOGASHI YOSAI: Wonderful. That's nineteen.
MITSUE: Nineteen what?
TOGASHI YOSAI: Things that might kill me this year. You're very welcome to join the list.
[GUEST +Togashi Yosai (stand-in)]
[ELSE]
(Yosai is lost in the ink — storyboard rule Y-1. A young monk in Tamori heat-wards waits at the shrine instead.)
TAMORI HAKU: The Furnace-keepers sent me down to escort pilgrims. (sniffing) You don't smell like pilgrims.
TAMORI HAKU: You smell like something that wants to be burned. (beat) Come on, then. It's a long climb.
[GUEST +Tamori Haku (stand-in)] (skills: Heat-Ward — party Fire resist, 2 uses; Ember Palm — Fire hit, 2 uses)
[END]

## S03 — A Dying Courier
MAP: `mountain_inn` · TRIGGER: the night stop
(A mountain inn. In the corner, a Bayushi courier in fever, sweating through his messenger's robe. He sees Mitsue's
current mask — a face he knows — and reaches for her.)
BAYUSHI COURIER: (feverish) Hana? Hana, is that you? Tell them — tell the garrisons —
[PA Eavesdrop Courier] (his fever-talk) →
BAYUSHI COURIER: …muster at the Month of the Rooster… every garrison toward the capital… the Champion's orders… sealed…
BAYUSHI COURIER: …the Emperor's guard won't know… until it's done…
[SET courier_heard]
MITSUE: (very still; then, gently, in "Hana's" voice) Rest now. I'll tell them.
(He dies before dawn, smiling, believing he delivered his message.)
[IF gendo_in_party] (Gendo, at the next table, has heard every word. He meets Mitsue's eyes once, and looks away.) [END]

## S04 — The High House of Light
MAP: `togashi_road` → `kyuden_togashi_garden` · TRIGGER: the road
(On the road: the Scorpion Champion's procession. Red lacquer, silent servants, banners. At its centre, masked,
unmistakable: BAYUSHI SHOJU, going to the High House of Light — Kyuden Togashi.)
MITSUE: (internal) My Champion. On his way to see the Dragon Kami.
[IF mitsue_knows_shoju_war] MITSUE: (internal) The Ojatara war was his distraction. Every court looking west. (beat)
Now I know what he was distracting them *from*. [END]
MITSUE: (internal) …Keep walking, she said.
(Many Faces — a cutscene trigger: Mitsue steps into the procession's servant train in a new face, carrying a tray,
eyes down.)
### The garden (cutscene, Eavesdrop — cannot fail)
(A garden of raked sand and old pines at the top of the world. Shoju kneels before a tall tattooed figure who seems
less a man than the mountain itself: the Kami TOGASHI.)
BAYUSHI SHOJU: I've found a prophecy, my lord. That the last of the Hantei will bring ruin. I would ask your guidance.
(Togashi is silent a long time.)
TOGASHI (paraphrase in game): Do this, and a family's line will end. Succeed — and the Empire will be saved.
(Shoju bows low. He hears only the second half. He rises with something like peace on his face.)
(Mitsue, at the edge of the garden with a tray, does not drop it. Her hands don't shake. She waits until the
procession has passed, until she is alone behind a wall, and then they do.)
MITSUE: (barely a whisper) …A family's line will end.
MITSUE: The Emperor's. (beat) He's going to kill the Emperor.
[SET togashi_heard]

## S05 — Duty's Knife (locked choice)
MAP: `togashi_road` (night) · TRIGGER: auto
### SYSTEM — the choice that isn't
> CHOICE "Tell someone?"
  - ~~"Tell the party."~~ (greyed) — "They'd be killed for knowing."
  - ~~"Warn the Emperor."~~ (greyed) — "Who would believe a nobody?"
  - ~~"Tell Norie."~~ (greyed) — "She'd have to report me. She'd do it."
  - **"Keep walking."**
MITSUE: (internal) Duty isn't a leash.
MITSUE: (internal) It's the promise you keep when you know exactly what it will cost.
[IF gendo_in_party]
(By the campfire. Gendo takes a page from his notebook — the one where he wrote the courier's words — and holds it
over the flame until it's ash. He says nothing. Mitsue watches him do it and says nothing either.)
[SET gendo_keeps_secret]
[ELSE IF dragon_ch2_not_done OR dragon_ch4_done]
TOGASHI YOSAI: (by the fire, not looking at her) You look like someone who just swallowed a mountain.
MITSUE: (lightly) It went down easier than you'd think.
TOGASHI YOSAI: Liar. (beat; kindly) That's twenty, by the way. Whatever you're carrying. I'm counting it for you.
[ELSE]
TAMORI HAKU: (feeding the fire) The Furnace takes anything. That's what we tell pilgrims.
TAMORI HAKU: (not looking at her) It doesn't take what you carry in here. (tapping his chest) Sorry. That's yours.
[END]

## S06 — Tamori's Furnace (dungeon)
MAP: `tamori_furnace_1–2` · TRIGGER: climb the volcano
(Lava tubes. Ash-shrines. Tamori monks in heat-wards bow and let them pass.)
TAMORI MONK: The Furnace takes anything. That's why the Tamori guard it.
[BATTLE b_furnace_elementals]
[BATTLE b_ash_ghouls]
(The Iron Box grows hot in Mitsue's hands. It screams in her voice the closer they get.)
IRON BOX (Mitsue's voice): Don't — don't — I'll be good — I'll be *you* —
MITSUE: (through her teeth) You'll be ash.
[SAVE] (the last shrine)

## S07 — The Stolen Face (BOSS)
MAP: `crater_mouth` · TRIGGER: approach the crater
(At the lip of the crater, a figure waits in Mitsue's own face, smiling her smile: a Bloodspeaker who has hunted the
Box since Kudo.)
BLOODSPEAKER (in Mitsue's face): You and I are the same, Shosuro.
BLOODSPEAKER: We wear what we need.
[BATTLE b_boss_stolen_face]
### GIMMICK — the Stolen Face
"At 66% and 33% HP the Bloodspeaker **steals a party member's face** and copies their last skill. Its weaknesses
become **that traveler's weapon types**."
### Barks
- Face stolen (Gendo's): BLOODSPEAKER: "Two swords! How *clerical*." GENDO: "That's a terrible impression."
- Face stolen (Yosai's): BLOODSPEAKER: "Oh, I'm very cheerful." YOSAI: "You're not. You're doing it wrong."
- Face stolen (Haku's): BLOODSPEAKER: "So young. So *warm*." TAMORI HAKU: "Give that back. My mother likes that face."
- [IF mitsue_wore_giseiki] GISEIKI's echo (pale text): "A borrowed face, Shosuro. You know how to take it back." →
  Mitsue's Steal on the stolen face **can't fail**.
- Maho: (Taint) "My blood is a key. Every lock opens."
- The Iron Box's curse is active one last time (−1 VP).
- Final: MITSUE (Many Faces: Steal — she takes her face back): "We're not the same."
- MITSUE: "I always give mine back."

## S08 — Ending
MAP: `crater_mouth` → `togashi_road` · TRIGGER: after the boss
(Mitsue stands at the crater's edge. The box in her hands is red-hot, screaming in her voice — then, as she lets it
fall, in nobody's voice at all. The Furnace swallows it.)
[SET box_destroyed] [ITEM −Iron Box] (the VP curse is gone)
(Mitsue sits down on a warm rock and doesn't move for a while.)
### The road home
(A fork in the mountain road. One way down to the Dragon lowlands. The other toward the long road south — to Otosan Uchi.)
(Mitsue presses something into each party member's hand: a small blood-red jasper scorpion. A "Favor".)
MITSUE: One favour each. From a nobody. They're good for exactly one impossible thing.
MITSUE: (smiling) Don't waste them on dinner.
[IF gendo_in_party]
(Gendo walks with her as far as the fork. Neither speaks. At the fork, he bows — lower than his rank requires, lower
than hers, the bow of a man to a friend he won't see again for a long time.)
GENDO: …Be careful in the capital, Shosuro.
MITSUE: (lightly) I'm always careful. (beat; not lightly) Thank you for burning the page.
[END]
(She takes the south road. Behind her, in Shoju's procession disappearing over a ridge, one servant turns her head
and looks back. Her eyes are very blue. She smiles. Then she's gone.)
MITSUE: (stopping; looking at the ridge; very quietly) …You're in his procession.
MITSUE: (beat) Of course you are.
[CHAPTER COMPLETE]
### Chapter complete card
**"The Eve" — complete.**
Journal: *Mitsue carried a sorcerer's heart into a volcano and heard the Dragon Kami answer her Champion's question.
She knows what is coming in the Month of the Rooster. She can tell no one. She kept walking.*
[UNLOCK] Rank 3 (*The Shadow Has No Form*) · *Blackened Sight* kata at Lv 51 · the Favor pendants · `gendo_keeps_secret`

---
## Travel Banter unlocked by Scorpion Ch4
### TB-scorpion4-a "Favors" (Mitsue + Tamotsu)
TAMOTSU: A Scorpion Favor. One impossible thing. (turning it over) What did *you* keep yours for?
MITSUE: (pause) …Something I can't have.
TAMOTSU: That's a terrible use of a favour.
MITSUE: (smiling) I know. I'm keeping it anyway.
### TB-scorpion4-b "The Fork" (Mitsue + Sayo)
SAYO: You took the south road.
MITSUE: The capital's lovely in autumn.
SAYO: (looking at her a long time) …Mitsue. Whatever it is. Come back after.
MITSUE: (very lightly) I always come back. (beat) Usually.
