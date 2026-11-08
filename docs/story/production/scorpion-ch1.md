# PRODUCTION — Scorpion Ch1 · "Blood and Iron"

**Traveler:** Shosuro Mitsue · **Lv** 1–8 · **Outline:** `scripts/scorpion-ch1-blood-and-iron.md`
**Flags set:** `rumours_found` (0–3), `governor_fake`, `hana_saved`, `iron_box_held`
**Maps:** `bayushi_gardens`, `willow_teahouse`, `traitors_grove`, `shutai_town`, `kudo_town` (governor's house,
river docks, Suzume hall), `river_crossing`, `west_marsh_1–2`, `heart_clearing`
**Battles:** `b_road_bandits` (Steal tutorial), `b_kommei_brood` (mid-boss: command-swap), `b_marsh_leeches`,
`b_boss_kansen_hana` (ritual counter + disarm-on-Suki)
**Fit conversions:** the eavesdrop minigame is Eavesdrop on 3 marked NPCs; the disguises are Many Faces cutscene
triggers; the ritual counter is the chapter's one gimmick.
**Storyboard:** `storyboards/scorpion-ch1.md` (adds the Kyuden Bayushi castle-town screen; Kudo NPC rows).

### RECRUIT VARIANT (Mitsue is not the starter)
**Join point:** the Kyuden Bayushi castle town, at the servants' gate after S02. A teahouse servant with a tray falls
into step beside the party.
MITSUE: (servant's voice) Don't look at me. Keep walking. (beat; her own voice, lighter) You're going south?
MITSUE: So am I. I'd like to look like I'm with someone. You look like someone.
MITSUE: (setting the tray on a wall) Shosuro Mitsue. Temporary yoriki. Permanently nobody.
> CHOICE "Travel with Mitsue?" → Yes: **Memory** (S01–S02: the memorial, three faces, "Nobody is very easy to be",
  Norie's orders) → resume at S03.
→ No: she sets down the tray and is simply gone; her chapter icon appears at the gate.

---

## S01 — A Memorial in Red
MAP: `bayushi_gardens` (afternoon, incense) · TRIGGER: new game, Mitsue chosen
NARRATION: Kyuden Bayushi. Its gardens are beautiful. Its walls hide three times as many passages as rooms.
(A memorial service. Courtiers in red and black. A lady's maid with downcast eyes carries a tray: MITSUE, in her
first face of the game.)
(An older woman in Emerald Magistrate's green passes, murmuring without moving her lips: SHOSURO NORIE.)
SHOSURO NORIE: Three true rumours before the incense burns down, Mitsue. Begin.
MITSUE: (as the maid, bowing) Yes, my lady. More tea?
### TUTORIAL — Path Action: Eavesdrop
"**Eavesdrop** — listen in on an NPC's private conversation. Your chance depends on your **Stealth** rank.
Failing in town costs **Honor** — it's a dishonourable act if you're caught."
| Target (marked) | Rumour (on success) |
|---|---|
| Two courtiers by the koi pond | R1: "A **Miya caravan** of relics from some ruined capital stopped here last month." |
| A Mantis envoy at dinner | R2: "Bandits on the River of Gold — and *another* band, fighting them. Nobody knows whose." |
| A pale courtier who won't eat | R3: "Two of us had the same dream. Both nights the caravan stayed. Blood. A beating heart." |
(Each success: [SET rumours_found +1]. Failure: the target glares at "the maid"; try another.)
(The incense burns down. Mitsue — now a minor cousin in a different silk — kneels beside Norie.)
SHOSURO NORIE: Three. And you were a maid for two of them. Who were you for the third?
MITSUE: (a stranger's voice, then her own) Nobody, sensei. Nobody is very easy to be.
SHOSURO NORIE: (not smiling) Be careful. Some of us forget how to stop.
[SAVE]

## S02 — The Willow Teahouse
MAP: `willow_teahouse` (a pond peninsula, dusk) · TRIGGER: auto
SHOSURO NORIE: Orders. From the Champion. Who does not know your name, which is why you are useful.
SHOSURO NORIE: Kudo. A farm town on the River of Gold, near the Shinomen. Once Hare land, now no one's.
SHOSURO NORIE: The Fox and the Sparrow govern it together and hate it together.
SHOSURO NORIE: Someone wants it to be the seat of a new Minor Clans Court. Someone else wants it to burn.
SHOSURO NORIE: You'll be a temporary yoriki to the Mantis magistrate there. Find out which someone is winning.
MITSUE: And the caravan? The dreams?
SHOSURO NORIE: (pause) Find out those too. Quietly. Leave by the servants' gate.
[per rumours_found] SHOSURO NORIE: (sliding a parcel across) For your trouble. (1: Antidote ×2 · 2: + Smoke Pellet ×2 ·
3: + Norie's Kozuka — "You'll need a smaller knife than you think.")
### TUTORIAL — Talent: Many Faces (field)
"**Many Faces** — in towns, take an NPC's appearance to pass guards. In battle: **Steal**, or **copy** an enemy's
skill for one turn."
(Mitsue becomes a teahouse servant and walks out past the guards, carrying a tray.)
GUARD: Evening, girl.
MITSUE: (servant's voice) Evening, sir. Mind the step.
(She is gone.)

## S03 — Traitor's Grove (road)
MAP: `traitors_grove` → `shutai_town` · TRIGGER: travel south
NARRATION: The road south. Blighted rice. And a grove where the Scorpion leave their traitors for the crows.
(Old posts among the trees. Rusting chains. Mitsue walks through without slowing, eyes ahead.)
MITSUE: (to herself) Eyes ahead. Never count the posts.
MITSUE: (beat) …Nineteen.
(Bandits block the road at the edge of the grove.)
[BATTLE b_road_bandits] (tutorial: **Steal** with Many Faces)
BANDIT: Hand over the purse, pretty!
MITSUE: (stealing his) This one?
### Town NPCs — `shutai_town` (border town)
| NPC | Default | Info | Path action |
|---|---|---|---|
| Innkeeper | "Two murders this month. Both travellers from Kudo." | *Eavesdrop:* "Both victims were bloodless." | — |
| Ronin drifter | "Kudo pays well for swords. Too well." | — | *Pilfer* (Sayo): Kudo Pass (opens the Suzume hall without Many Faces) |
| Priest | "The river's gone a strange colour upstream." | — | — |

## S04 — Kudo (investigation hub)
MAP: `kudo_town` · TRIGGER: arrive
NARRATION: Kudo. Fox lanterns on one street, Sparrow ribbons on the next, and a bridge between them nobody likes to cross.
(The Mantis magistrate's office. A clerk coughs.)
CLERK: The magistrate is ill. Very ill. All of us — pneumonia. (cough) Come back next season.
MITSUE: (presenting her yoriki papers) I'll wait here, then. Under your desk, if necessary.
### Suspects (Eavesdrop / Discern / Many Faces targets)
| Target | Default line | Path action → info |
|---|---|---|
| **Kitsune governor** | "Kudo is calm. Kudo is very calm." | *Eavesdrop* (night): eats raw river fish alone, whispering to it |
| **Suzume governor's steward** | "My lord barely survived the assassin!" | *Eavesdrop:* "There was no assassin. My lord wanted sympathy." |
| **Kitsune Hana** (Fox aide) | "The governor hasn't been himself since spring." | *Discern* (if Gendo): "Frightened; hiding the governor's change." |
| **Tortoise envoy** | "Just trading. Rice. Ordinary rice." | *Eavesdrop:* smuggling — not your case (red herring) |
| River dock-hand | "The caravan was robbed right here! Everything got dumped in the reeds." | "Everything except a little iron box. Nobody found that." |
| Old woman (east district) | "My neighbours left in the night. All of them." | *Bless:* follows ("Neighbour's Charm", heal, 1 use) |
| Kitsune Hana (again) | — | *Charm:* she shows the Fox charm-box (a hint toward the west) |
| Tortoise envoy (again) | — | *Barter:* Sea Salt, Eel |
| Sparrow ronin | "Fox street or Sparrow street. Pick one." | *Duel:* Glory +1 · *Sumai:* "The Fox governor bought every jar of river salt in town." |
| Fishmonger | "Salt herring, salt herring." | *Pilfer:* Salt Herring ×3 |
### S04b — Many Faces: the governor's rooms
(A Fox household servant, scolded and sent upstairs: Mitsue in her third face.)
MITSUE: (bowing) Your fish, my lord.
"GOVERNOR": (back to her, eating) …Leave it.
MITSUE: My lord, it's raw—
"GOVERNOR": (turning — too many teeth, for one moment) Leave the plate. Leave.
MITSUE: (calm, backing out) Of course, my lord.
(The corridor. Her hands shake once, then stop.)
MITSUE: (to herself) …That isn't a governor. That isn't a *person*.
[SET governor_fake]
[SAVE]

## S05 — The Nudge
MAP: `kudo_town` (night) → `river_crossing` · TRIGGER: governor_fake + 2 suspects
(Night. The sick from the magistrate's office are gone — beds empty, still warm. A great shape blots out the moon,
flying west across the river.)
KITSUNE HANA: (running up, terrified) The governor — he's gone! He walked into the river! He didn't sink!
MITSUE: Which way?
KITSUNE HANA: West! Into the woods — the woods are *changing*!
(At the river crossing the "governor" waits on the water, grinning, its face slipping.)
[BATTLE b_kommei_brood] (mid-boss)
### GIMMICK preview (mid-boss only — the chapter's main gimmick is the boss's)
"The oni **swaps two allies' commands** on its turn." (One-time demonstration; it foreshadows Crab Ch3.)
KOMMEI-BROOD ONI: Which of you is which? Do you even know?
MITSUE: (Many Faces: Copy) I'm whoever I need. You should try it.
(It dissolves into river mud. A Fox charm is left in the mud.)

## S06 — Across the River (dungeon)
MAP: `west_marsh_1–2` · TRIGGER: cross
### Status — Taint (first appearance)
"Marsh tiles add **Taint**: a stacking curse that lowers max HP. Jade items and shrines cleanse it."
(A drifting barge, tangled in reeds. Under a cloth: the Mantis magistrate. And the real Kitsune governor — dead for
weeks. Both bloodless.)
KITSUNE HANA: (falling to her knees) …My lord. It was never you. All spring, it was never you.
MITSUE: (covering them again, gently) Then he didn't fail you. Something wore him.
[BATTLE b_marsh_leeches]
(In the reeds: the Miya caravan's relics, dumped and half-sunk. Interaction → [ITEM +Crystal Shard ×4])
MITSUE: Miya relics. Crystal. (turning a shard in the light) Somebody was carrying these to bind something.
(The trees bleed sap like blood. Animals stream past, fleeing east.)
KITSUNE HANA: (following, shaking) Something is calling. I can hear it. It's — it's calling *me*.
[SAVE] (an emergency shrine before the clearing)

## S07 — The Heart in the Clearing (BOSS)
MAP: `heart_clearing` · TRIGGER: enter
(A clearing that rises and falls like breathing. A pit of blood in the centre. Kitsune Hana walks to its edge as if
in a dream, and lifts a small iron box from the mud. A yellow-green cloud pours into her.)
KANSEN-HANA: (two voices: hers pleading, and another) Take it… take it away from me… (then:) Give it to ME.
MITSUE: (stepping forward) Hana. Look at me. Not at the box.
KANSEN-HANA: The Oracle comes. The blood rises. Iuchiban's heart will beat again.
[BATTLE b_boss_kansen_hana]
### GIMMICK — the ritual counter & disarm
"The **ritual counter** advances each turn. At 10, the Oracle of Blood begins to rise.
Break her (**Suki**) and she **drops the Iron Box** — the counter stops. **Steal** it!"
### Barks
- Counter 5: KANSEN-HANA: "The pit is listening!"
- Counter 7: (phase 2 risk) the pool takes a human shape. MITSUE: "Not today."
- Counter 10: the Oracle of Blood rises fully — *Blood Tide* (heavy party damage each turn) until Hana is broken.
  Still winnable.
- Suki: (the box clatters free) MITSUE: "Mine." (Steal prompt)
- Kansen (physical damage halved): MITSUE: "Crystal hurts it. Everything else just annoys it."
(Victory. The cloud tears out of Hana and dissolves in the air. She collapses, alive.)
[SET hana_saved]

## S08 — What Is in the Box
MAP: `kudo_town` (inn, dawn) · TRIGGER: after the boss
(The box sits on the inn table. Iron. Plain. A finger long. It hums, very faintly, like a heartbeat heard through a
wall.)
KITSUNE HANA: (wrapped in a blanket) Thank you. I don't know your name.
MITSUE: (smiling) Neither does anyone. It's restful.
(That night. Mitsue dreams of a heart beating inside iron. She wakes. The lid is open on her pillow. She closes it.)
(A letter from Norie arrives at dawn.)
SHOSURO NORIE (letter): That box once held the heart of Iuchiban. No tool we own can break it.
SHOSURO NORIE (letter): Keep it. Tell no one. Do not open it again.
MITSUE: (reading, the box beside her) …Again?
[ITEM +Iron Box (cursed key item: −1 VP at the start of every battle)] [SET iron_box_held]
[ITEM +Scorpion "Favor" (jasper pendant; one-time story favour)]
KITSUNE HANA: (at the door, shy) The Fox will remember you. Even if you're nobody.
MITSUE: (after she goes, softly) …Especially if I'm nobody.
[CHAPTER COMPLETE]
### Chapter complete card
**"Blood and Iron" — complete.**
Journal: *Three rumours, three faces, and a town ruled by something wearing a dead governor. Mitsue saved a
frightened Fox — and now carries an iron box that once held a sorcerer's heart.*

---
## Travel Banter unlocked by Scorpion Ch1
### TB-scorpion1-a "The Burn" (Mitsue + Tamotsu)
TAMOTSU: How did you burn your hand?
MITSUE: A lamp at the theatre.
TAMOTSU: Last week you said it was a cooking fire.
MITSUE: (smiling) Was it? Then it was both. I'm very unlucky with fire.
TAMOTSU: (gently) You don't have to tell me.
MITSUE: (pause) …I know. That's why I nearly did.
### TB-scorpion1-b "The Box" (Mitsue + Haruki)
HARUKI: That box. It's… humming. Can you hear it?
MITSUE: Only at night.
HARUKI: It's using your voice. I heard it from the next room.
MITSUE: (lightly) Then it has excellent taste.
HARUKI: (very serious) Mitsue. Please don't open it.
MITSUE: (beat; the smile fades) …I won't. Ask me again tomorrow, though.
