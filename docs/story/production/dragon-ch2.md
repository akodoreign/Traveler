# PRODUCTION — Dragon Ch2 · "The Painting"

**Traveler:** Kitsuki Gendo · **Lv** 20–25 · **Outline:** `scripts/dragon-ch2-the-painting.md`
**Flags read:** `kumpei_watched`, `momo_joined` · **Flags set:** `mirumoto_school`, `jumped_first`, `ushimo_lead`,
`history` (meter starts at 100)
**Maps:** `tortoise_village`, `tortoise_house`, `ridge_dojo`, `cove_cave_1–3`, `ink_limbo`, `orchard_400`
**Battles:** `b_cove_crabs`, `b_cove_guards`, `b_boss_ushimo` (don't-kill gimmick)
**Party note:** only Gendo + up to 3 go through the portal. Yosai is "lost in the ink" until Ch4.
**Storyboard:** `storyboards/dragon-ch2.md`. **The Ink Door** (S06 end) links the year-400 south gate and the
Tortoise cove, so the party can come and go between Dragon chapters. Party swaps happen in the present (Tortoise
village inn). The door closes at the end of Dragon Ch4.

---

## S01 — Tortoise Island
MAP: `tortoise_village` → `tortoise_house` · TRIGGER: arrive by fishing boat
NARRATION: Tortoise Island. A fishing village, a shrine, and a new wooden house nobody remembers being built.
(A grey fishing village. A villager points up the hill without being asked.)
[IF kumpei_watched] GENDO: (watching the hill) He ran exactly where I hoped. Men who run go somewhere. [END]
VILLAGER: The new house? An old man and a Crane gentleman. They paid in glass. Who pays in glass?
(The house: clean, empty, smelling of alchemy. Dragon instruments on the shelves: an alembic, a brass star-chart.)
GENDO: (lifting an alembic) Dragon work. Tamori-style. Our own clan's tools, in a murderer's kitchen.
TOGASHI YOSAI: (from the cellar stairs; no joke in his voice) …Gendo.
(The cellar. Two shapes under cloth. Yosai lifts a corner, then lowers it again, gently.)
TOGASHI YOSAI: Two more brothers. Their tattoos are gone. Not cut. *Lifted*.
TOGASHI YOSAI: The ink lived in them, and he took it.
GENDO: Akuro.
TOGASHI YOSAI: He always said ink was just patience made visible. (beat) I suppose he wanted the patience back.
(The floor lurches. Plaster rains down. An unnatural earthquake — the house folds like paper.)
(CUTSCENE: they escape through the window as the roof comes down. Below, round the headland, a white sail: Kumpei's
boat entering a sea-cave.)
[SAVE]

## S02 — A Sword You Rarely Draw (Rank 2 unlock)
MAP: `ridge_dojo` · TRIGGER: optional before the cove (required for the Rank 2 school)
(A one-room dojo on the ridge. An old Mirumoto in exile sharpens two blades.)
OLD MIRUMOTO (KOSHI): A Kitsuki who carries a Mirumoto sword and never draws it. I've heard of you, fish-hat.
GENDO: Everyone has. It's my only fame.
OLD MIRUMOTO: You hold the katana like a clerk holds a brush.
GENDO: I was a clerk.
OLD MIRUMOTO: Good. (tossing him a wakizashi) Clerks know the second stroke corrects the first. Take the wakizashi too.
OLD MIRUMOTO: Two swords. Two truths. One hand states. The other hand checks.
GENDO: (holding both, awkwardly) It feels like writing with two brushes.
OLD MIRUMOTO: It is. Now — write.
[SET mirumoto_school] [UNLOCK Mirumoto secondary school (Rank 1: Daisho Technique)]
(Training montage. Gendo drops the wakizashi twice. The third time, he doesn't.)
OLD MIRUMOTO: Adequate.
GENDO: (polishing his spectacles, almost smiling) That's the second time someone's said that to me in a way that sounded like praise.

## S03 — The Cove Cave (dungeon)
MAP: `cove_cave_1–3` · TRIGGER: enter the sea-cave
(The cave widens. On the floor: a miniature city of clay and wood, laid out with obsessive care. Otosan Uchi —
the capital — growing older toward its centre: tile roofs, then thatch; stone walls, then wood.)
GENDO: (kneeling) The capital. Built backwards in time. The middle is… four, five hundred years old.
TOGASHI YOSAI: Someone made a map of *when*.
[BATTLE b_cove_crabs]
[BATTLE b_cove_guards] (Akuro's hypnotised guards — they murmur the same sentence)
HYPNOTISED GUARD: …the end of your rope… the end of your rope…
(The centre. A frame of two posts, silk stretched between them, painted with living ink — tattoos flowing like water.
A portal. Through it: a cherry orchard in winter.)
(KAKITA KUMPEI and an old fisherman — who straightens, and is not a fisherman — step through. TOGASHI AKURO glances
back once. He looks at Yosai. Something passes over his face. Then he's gone.)
(The silk's edges begin to blacken and curl.)
TOGASHI YOSAI: (very quietly) He looked at me.
GENDO: Yosai—
> CHOICE "The portal"
  - "Jump in after them." → [SET jumped_first]
  - "Wait — think first." → (the portal pulls at them anyway)
TOGASHI YOSAI: (already running) Twenty!
(He leaps. Gendo leaps. Up to two more party members leap after them. Everyone else stays on the sand.)
[IF momo_joined] KITSUKI MOMO: (hitching up her sleeves) I've investigated plums. I can investigate *time*. (she
jumps; she is the active guest from here) [END]
(The silk burns away behind them.)
### Party note (system)
"Only Gendo and up to 3 allies cross. The rest wait in the present. **Togashi Yosai is lost in the ink.**"

## S04 — Outside Time
MAP: `ink_limbo` → `orchard_400` · TRIGGER: auto
(A breathless dark full of stars made of ink. No sound. Gendo's spectacles reflect a thousand flowing tattoos.
Somewhere, Yosai's voice, laughing, getting further away: "…still twenty— that doesn't count— still twenty—")
GENDO: Yosai!
(Silence. Then — a fall. Snow. Cherry petals. A winter orchard under a pale sun.)
NARRATION: The year 400. The reign of the sixth Hantei. Three great lords rule the Empire through a boy.
### SYSTEM — History meter (appears on screen)
"**History: 100%.** You are in the past. **Anachronisms** — words, objects, deeds that don't belong — lower History.
At 0, the future you came from is lost."
GENDO: (brushing snow from his spectacles; muttering) Year four hundred. No Kitsuki family yet.
GENDO: No magistrates. Spectacles are probably witchcraft.
GENDO: (beat) Wonderful.
### Tutorial prompt
"Don't say **'Kitsuki'**. Don't mention the **Unicorn**, the **Kaiu Wall**, or **Emerald Magistrates**. Keep your
**spectacles** hidden around nobles."
[SAVE]

## S05 — Seppun Ushimo (BOSS)
MAP: `orchard_400` · TRIGGER: walk toward the voices
(A boy of fourteen in Imperial white walks under the trees with two guards: HANTEI KUSADA. One guard — SEPPUN
USHIMO — draws and cuts his partner down without a word, and turns toward the boy.)
HANTEI KUSADA: (not running; very polite) …Ushimo?
(Gendo is closest. He steps between them — both swords out, badly.)
GENDO: (internal) Do not change history. Do not change history. (aloud) Majesty, behind me.
[BATTLE b_boss_ushimo]
### Structure
- **Phase 1 — duel:** Ushimo's iaijutsu is perfect. Gendo's *Daisho Technique* lets him answer with Kenjutsu.
- **Phase 2 — skirmish.** Weak: **Bo**, **Yari**, **Water**.
- **GIMMICK — don't kill him:** "Ushimo **wants to die**. Below 25% HP he drops his guard. **A killing blow is
  refused** — *History shudders* (History −10) and he's left at 1 HP. **Break him (Suki) or use a non-lethal skill**
  (Subdue, Knockdown) to win."
### Barks
- Below 25%, SEPPUN USHIMO: (kneeling, sword lowered, throat bared) "Please. Finish it. I'm at the end of my rope."
- A killing blow attempted: (the screen ripples; a sound like a page tearing) "History shudders."
- GENDO (Subdue: a Bo strike to the wrist): "That's not your sentence, Ushimo. Someone put it in your mouth."
- Win: (Ushimo collapses, sobbing; the boy-Emperor kneels beside him, puzzled and kind)
> CHOICE "Ushimo"
  - "Ask him why." → [SET ushimo_lead]
      SEPPUN USHIMO: My wife. Tsuhime. She's dying. Only the gaijin medicine eases her.
      SEPPUN USHIMO: Her new doctor gave me sake last night. He said I was at the end of my rope.
      SEPPUN USHIMO: (staring at his hands) I've been at the end of my rope for a year. I never wanted to cut it.
  - "Give him to the guards." → (the lead comes later via the guards)

## S06 — The Court's Sensation
MAP: `orchard_400` → palace gate · TRIGGER: after the boss
(Guards come running. The boy-Emperor stands, brushes snow from his sleeves, and studies Gendo with frank fascination.)
HANTEI KUSADA: You fought like a brush, sir. Two brushes. (pointing) What are those on your face?
GENDO: (History meter twitches) …An affliction, Majesty. Of the eyes.
HANTEI KUSADA: They're *glass*. How marvellous. What is your name?
GENDO: (careful) …Gendo, Majesty. Just Gendo.
HANTEI KUSADA: (delighted) A man with no family! How *mysterious*.
(That evening: three lacquered invitations arrive at the guest house where the palace lodges them. Three gozoku
lords. Three dinners. All at the same hour.)
GENDO: (holding them up) Every history scroll I ever filed has these three names in it.
GENDO: (beat) None of them got the seating right.
### The Ink Door
MAP: `otosan_uchi_400` (south entrance) · TRIGGER: leave the guest house
(Passing the palace's south entrance, Gendo stops. A painting on silk: a grey sea-cave, a tide pool, a clay city.)
GENDO: …That's the cove. Our cove. Tortoise Island.
(He touches it. His hand goes *in*, to the wrist. It's warm. The ink moves around his fingers like water.)
GENDO: (pulling his hand back; very quietly) Akuro kept a spare.
[IF any_ally] ALLY: "So we can go home?" GENDO: "We can go home. (beat) And we can come back. Which is worse." [END]
[UNLOCK] **The Ink Door** — travel between the year-400 south gate and the Tortoise Island cove (active party only;
swap in the present). It closes at the end of Dragon Ch4.
[CHAPTER COMPLETE]
### Chapter complete card
**"The Painting" — complete.**
Journal: *A city built backwards in time, a portal painted in stolen ink, and a fall into the year 400. Gendo saved
a boy-Emperor without killing the man who tried to kill him — and lost a friend somewhere in the ink.*

---
## Travel Banter (past chapters; party in the past only)
### TB-dragon2-a "No Family" (Gendo + any)
ALLY: "Just Gendo"? Doesn't that sting?
GENDO: I've been "the clerk", "the fish-hat", and "boy" for twenty years.
GENDO: "Just Gendo" is the first name anyone's given me that's entirely mine.
### TB-dragon2-b "Yosai" (Gendo alone, at the guest-house window — a solo scene)
GENDO: (to the snow) Twenty-two, you'd say. The Fortunes tried again.
GENDO: (beat) Don't let them win, Yosai. I still need you to explain the half.
