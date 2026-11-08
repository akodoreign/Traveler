# PRODUCTION — Phoenix Ch4 · "Howl"

**Traveler:** Isawa Haruki · **Lv** 41–45 · **Outline:** `scripts/phoenix-ch4-howl.md`
**Flags read:** `consumer_scroll_kept`, `showed_scroll`, `apology_note_found`, `mieko_midnight_seen`, `told_keiki`
· **Flags set:** `echoes_blessed` (0–3), `dream_keys` (0–3), `mieko_answer`, `whole`
**Maps:** `coast_temple_town`, `cliff_path_1–2`, `last_shrine`, `dream_estate` (dream), `red_torii_cliff`
**Battles:** `b_mieko_shadows_a/b`, `b_boss_mieko_dark` (Void duel; final phase is a choice)
**Set-piece:** Dreamwalker. **Rules payoff:** Void −1 and the passive "Whole". · **Storyboard:** `storyboards/phoenix-ch4.md`

---

## S01 — The Book
MAP: `coast_temple_town` · TRIGGER: start
NARRATION: The Phoenix coast. A storm coming in off the sea. And in the temple, a book that took a hundred years to write.
(A temple scriptorium. Monks copy a fat old book: *Against the Bloodspeakers*.)
ASAKO KEIKI: Every ward against the Bloodspeakers, in one book. The Council finally agreed to share it with every clan.
ASAKO KEIKI: (beat) Last night it was stolen.
HARUKI: (very quiet) Mieko.
ASAKO KEIKI: Her other half. She went toward the red torii on the cliffs.
ASAKO KEIKI: She'll burn it there. Or read it, and then there's no ward left that can hold her.
HARUKI: She'll do neither. (beat) She'll wait for me. She's been waiting twelve years.
[IF told_keiki] ASAKO KEIKI: (gripping his sleeve) I watched her, as you asked. Every midnight. I'm sorry I wasn't enough. [END]
[IF mieko_midnight_seen AND NOT told_keiki] ASAKO KEIKI: (quietly) You saw her at midnight, didn't you. In Treaty City. You knew before any of us. [END]
[SAVE]

### Town NPCs — `coast_temple_town` (storyboard pass)
| NPC | Info | Path action |
|---|---|---|
| Copy-monk | *Discern:* "The thief wore white and hummed." | — |
| Fisherwife | — | *Barter:* Eel ×3, Sea Salt |
| Ronin guard | — | *Sumai:* the cliff shortcut ledge |
| Shiba sentry | — | *Duel* (Iaijutsu 7): Glory +1 · Fine Katana Fragment |
| Storm-watcher | *Eavesdrop:* "Two wolves on the cliff, every night. One white, one black." | — |
| Child with a kite | — | *Charm:* follows ("Kite Line": party Speed up, 1 use) |
| Outfitter | — | *Pilfer:* Kansen Mist ×2 |
| Drowned sailor's ghost (jetty) | — | *Bless:* leads to a sunken box → Orochi Scale |

## S02 — The Cliff Path
MAP: `cliff_path_1–2` · TRIGGER: climb toward the torii
(Rain. Wind. A path of little shrines along the cliff edge.)
[BATTLE b_mieko_shadows_a] (fragments of the dark half — they copy Haruki's own spells)
HARUKI: (as a shadow casts his own Path to Inner Peace on itself) …She's learned everything I can do.
### Echoes of the gentle Mieko (3 Bless interactions → [echoes_blessed +1])
- An echo tending wet camellias: "They'll drown if I don't cover them…" → HARUKI: "Let me help." (they cover them together; she fades, smiling)
- An echo singing a children's counting song: "…fire, water, air, earth, void…" → HARUKI: (counting along on his fingers) "…void."
- An echo writing the Consumer scroll by candlelight, weeping: → HARUKI: "You were so brave. To write a warning about yourself."
[BATTLE b_mieko_shadows_b]
[SAVE] (the last shrine)

## S03 — Inside the Dream (set-piece)
MAP: `last_shrine` → `dream_estate` · TRIGGER: enter the last shrine
(Mieko's body lies asleep on the shrine floor, breathing slowly. The book beside her.)
HARUKI: (kneeling) She's here. But she isn't.
HARUKI: (raising his hands) *Dreamwalker*.
### SYSTEM — the dream
"You are walking in Mieko's dream: the night you were both eight. Find **three dream keys**."
(The forest estate, twelve years ago. Daylight that's too bright. The go board. Two children's voices.)
CHILD-MIEKO (echo): That's my stone! You can't take it!
CHILD-HARUKI (echo): I captured it fairly!
(A crack runs across the dream, splitting it: on one side, a garden in sunlight; on the other, ash.)
(In the garden: the gentle Mieko, arranging flowers, humming. In the ash: the dark Mieko, sitting on the broken go board.)
### Dream keys
- **Key 1** (gentle side): [IF consumer_scroll_kept OR showed_scroll] show her the warning she wrote.
  GENTLE MIEKO: (reading it) …I wrote this? I don't — (beat) I was afraid of her. Of *me*.
  [dream_keys +1]
- **Key 2** (dark side): [IF apology_note_found] show her the note.
  DARK MIEKO: (reading the child's handwriting, *I'm sorry Mieko I didn't mean to please wake up*) …You wrote this.
  DARK MIEKO: (very quiet, for once not laughing) …You were eight.
  [dream_keys +1]
- **Key 3** (the crack itself): stand where it began. A frozen child-Haruki, mid-scream, Void pouring from his hands.
  CHILD-HARUKI (frozen echo): I'm sorry I'm sorry I'm sorry I didn't mean to—
  HARUKI: (kneeling beside him; putting a hand on the frozen child's shoulder) I know.
  HARUKI: You don't have to say it anymore. I'll say it for both of us.
  [dream_keys +1]
(The dream shudders. Haruki wakes.)

## S04 — Mieko's Dark Half (BOSS)
MAP: `red_torii_cliff` · TRIGGER: wake
(The red torii on the sea-cliff, in the storm. The dark Mieko stands at the edge with the book, black-glass eyes,
Void crackling around her like broken lightning.)
MIEKO (DARK): You walked in my dream. (laughing, but strained) Rude.
MIEKO (DARK): You broke me in half, little Void. Now you'll finish the job?
MIEKO (DARK): Do it. (spreading her arms) It's what Void does.
[BATTLE b_boss_mieko_dark]
### Mechanics / barks
- "Mieko casts **Void spells that cost her VP** — a duel of two Void economies. She **drains your VP**."
- Drain: MIEKO (DARK): "Your Void tastes like mine. Did you know that? We're made of the same night."
- *Void Strike* steals her charge: HARUKI: "Give that back. It isn't yours. (beat) It isn't mine either."
- *Kharmic Intent* (sharing VP with an ally): HARUKI: "I don't have to hold it alone. I never did."
- [per dream_keys] her Resolve starts 2 lower per key.
- [per echoes_blessed] each blessed echo **cancels one VP drain**: "The gentle echo stands between you."
- At 0 HP she drops to her knees in the rain. **The fight ends.**

## S05 — The Choice (fake choice)
MAP: `red_torii_cliff` · TRIGGER: after the battle
MIEKO (DARK): (on her knees, the book in the mud) Well? Finish it.
> CHOICE "Mieko"
  - "Strike the final blow." → (Haruki raises his staff. Stops. Lowers it.)
      HARUKI: (barely audible) …No. Not again. I won't break you again.
      (→ continues as Join)
  - "Join the halves." →
HARUKI: (kneeling in front of her in the mud) The library said joining needs one half to want it. And a giver.
MIEKO (DARK): (bitter) And who would give anything for *me*?
HARUKI: (holding out his hands, Void gathering in them — gentle, this time) I would. I took some of you. It's fair.
(Light. Not black glass — something like dawn through water. The crack between two Miekos closes, slowly, and Haruki
cries out once and falls to his knees.)
### SYSTEM
"**Haruki gives part of his Void.** Void −1 (permanent). Gained passive **Whole**: Water heals also cleanse 1
debuff; *Drawing the Void* can be used **twice** per battle."
[SET whole]
(One Mieko kneels in the rain. Fragile. Remembering everything. She looks at her hands as though she's never seen them.)
MIEKO: (one voice now, very quiet) …Who am I?
HARUKI: (exhausted, smiling) I don't know. I think you get to decide.
HARUKI: I'm sorry it took me twelve years to give it back.
> CHOICE "Her answer" [SET mieko_answer "yet" / "eight"]
  - (Mieko) "Someone who doesn't forgive you yet." → (honest)
      MIEKO: Someone who doesn't forgive you. (beat) Yet.
      HARUKI: (laughing weakly, rain in his face) "Yet" is more than I ever hoped for.
  - (Mieko) "Someone who remembers you were eight." → (gentler)
      MIEKO: Someone who remembers you were eight. (beat) And that I was cruel first. I took your stone.
      HARUKI: …You did take my stone.

## S06 — Ending
MAP: `coast_temple_town` (dawn) · TRIGGER: auto
(Dawn. The storm gone. Mieko, wrapped in a temple blanket, gives the book back to Haruki. One page is marked with a
dried camellia petal.)
MIEKO: (pointing to the page) My other half was investigating something. Before. Read that.
HARUKI: (reading) "On the Bride of Fu Leng, who wears the faces of the beloved…"
HARUKI: (looking up) …You were hunting her. Even then.
MIEKO: The gentle half was. (beat) The other half thinks she'd like to help finish it.
MIEKO: Bring the book back afterwards. Then we'll talk.
HARUKI: About forgiveness?
MIEKO: (almost smiling) About camellias. They're very difficult to grow.
(At the red torii, as the sun rises over the sea: two wolves on the cliff, one white and one black, howl once together.
Then there is only one, the colour of dawn, and it trots away into the trees.)
[ITEM +"Against the Bloodspeakers" (finale key item)]
[CHAPTER COMPLETE]
### Chapter complete card
**"Howl" — complete.**
Journal: *Haruki walked through the night he broke Mieko, met both halves of her, and gave up part of his own Void to
make her whole. She doesn't forgive him — yet. She does want to help hunt the Bride of Fu Leng.*
[UNLOCK] Passive **Whole** · Void −1 · the Bloodspeaker book (finale: Blood Shouting broken)

---
## Travel Banter unlocked by Phoenix Ch4
### TB-phoenix4-a "Lighter" (Haruki + Sayo)
SAYO: You're walking differently.
HARUKI: Am I?
SAYO: Like someone who put down a basket he'd carried for twelve years.
HARUKI: (thinking about it) …I gave part of myself away. I thought I'd feel emptier.
SAYO: (grinning) Medicine's funny like that. Sometimes you get better by losing something.
### TB-phoenix4-b "Five" (Haruki + Natsuko)
NATSUKO: You stopped counting on your fingers.
HARUKI: (looking at his hand) …I did.
NATSUKO: What happened?
HARUKI: I think I finally got to the end of the number.
