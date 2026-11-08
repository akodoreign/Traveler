# PRODUCTION — Dragon Ch1 · "Under the Skin"

**Traveler:** Kitsuki Gendo · **Lv** 1–8 · **Outline:** `scripts/dragon-ch1-under-the-skin.md`
**Flags set:** `oharu_poisoned`, `kumpei_watched` / `kumpei_accused`, `riichi_trusts`, `momo_joined`
**Maps:** `mantis_ship`, `silk_docks`, `yoritomo_hall`, `guest_house`, `silk_dump`, `rakusho_school`,
`gusai_ruins_1–3`, `silk_boathouse`, `tortoise_beach`
**Battles:** `b_dock_tutorial`, `b_gusai_thugs_a/b`, `b_boss_tide` (tide-timer gimmick)
**Guests:** Togashi Yosai (S03), Kitsuki Momo (S04, optional)
**Fit conversions:** Riichi's code is a Discern plus one dialogue choice; the stair code is the dungeon's layout,
not a puzzle UI; the tide timer is the chapter's one gimmick.
**Storyboard:** `storyboards/dragon-ch1.md` (adds route `silk_hill_path`). **Guests (G-1):** Yosai is story-locked
as the active guest. If Momo joins, she waits on the roster and becomes active in Dragon Ch2.

### RECRUIT VARIANT (Gendo is not the starter)
**Join point:** `silk_docks`, the ferry pier, on the morning after S02. Gendo is questioning the ferry crew, with a
seal much too big for him on his belt.
GENDO: (not looking up from his notebook) You came on the morning ferry. Three of you were seasick. One pretended not to be.
GENDO: (looking up; polishing his spectacles) Forgive me. Kitsuki Gendo, junior yoriki. My superior has been poisoned.
GENDO: I have her seal, no authority, and a body with no tattoos. (beat) Would you like to be useful to the law?
> CHOICE "Travel with Gendo?" → Yes: **Memory** (S01–S02: the ship, the waterline, the dock brawl (no battle), the hall,
  the poisoned tea, the seal, "a hat on a fish") → resume at S03.
→ No: he stays on the pier.

---

## S01 — The Junior Yoriki
MAP: `mantis_ship` (deck, morning, choppy) · TRIGGER: new game, Gendo chosen
NARRATION: The Mantis Isles. Where the Empire's laws arrive late, wet, and slightly bribed.
(A trading ship. Gendo leans on the rail polishing round gaijin spectacles. Beside him, gripping the rail very hard:
KITSUKI OHARU, sharp-eyed, grey-haired, kind.)
KITSUKI OHARU: Tell me what you see, Gendo.
GENDO: A trading ship. Forty crew. Silk in the manifest.
KITSUKI OHARU: And?
GENDO: The captain's lying about the cargo. The ship sits too low for silk. Lead, perhaps. Or rice.
KITSUKI OHARU: Good. And?
GENDO: (beat) And you're seasick, Oharu-sama, and pretending you're not.
KITSUKI OHARU: (laughing, then groaning) Better. Never tell anyone that second one.
GENDO: I'll file it under "classified".
### TUTORIAL — Path Action: Discern
"**Discern** — study an NPC to learn what they hide. Some secrets need a higher **Investigation** rank."
(Prompt: Discern the CAPTAIN.)
→ CAPTAIN info: "Smuggling Mantis rice past a Crane tariff. Nervous. Not dangerous."
GENDO: (to the captain, mildly) Rice is heavier than silk, captain. Your waterline says hello.
CAPTAIN: (sweating) …Please don't tell the Yoritomo.
GENDO: I'm a junior yoriki. Nobody tells me anything, and I tell nobody anything. It's very restful.
(Docking. A drunken sailor swings a gaff at Gendo for "staring".)
[BATTLE b_dock_tutorial] (teaches Deduce: "**Deduce** — your Talent. Reveal an enemy's weaknesses and its next action.")
GENDO: (after) I wasn't staring. I was deducing. It looks the same from outside.
[SAVE]

## S02 — Hospitality
MAP: `yoritomo_hall` → `guest_house` · TRIGGER: auto
(A hall hung with nets and trophies. YORITOMO, the Mantis lord: big, blunt, bluffing. Beside him a shaven-headed man
in armour at court — TADAYASU, captain of the Storm Legion — with kama-carrying thugs.)
YORITOMO: The Dragon send a magistrate about a body on a dump. Good. Take it away.
KITSUKI OHARU: A Togashi body, my lord. The Dragon take an interest.
YORITOMO: The Dragon take an interest in everything and pay for nothing. Tadayasu — give them a minder.
TADAYASU: (smiling with too many teeth) Kosai. Show the magistrate whatever she likes. And the boy.
(A young thug, KOSAI, bows sloppily. Gendo stands three paces behind Oharu. No one addresses him.)
(Night. The guest house. Oharu sips her tea. Coughs. Coughs again. Drops the cup.)
GENDO: Oharu-sama!
(Quick cuts: Gendo shouting for a healer; Kosai "can't find one"; Gendo's hands steady as he sniffs the tea.)
GENDO: (internal) Bitter almond… no. Mantis mushroom. She'll live if she doesn't move. If.
KITSUKI OHARU: (whispering, feverish) Gendo. My seal. Take my seal.
GENDO: Oharu-sama, I'm a clerk with spectacles.
KITSUKI OHARU: They won't respect it in your hands. (pressing it into his palm) Use it anyway.
[SET oharu_poisoned] [ITEM +Oharu's Seal]
(Morning. Tadayasu leans in the doorway.)
TADAYASU: Terrible luck. The magistrate is sick. The case must wait for a real magistrate.
GENDO: (holding up the seal) The case has one.
TADAYASU: (laughing) A seal on a clerk is a hat on a fish, little Dragon. Go home.
GENDO: (after he leaves; to himself) Fish wear hats on some islands. I've read about it.
[SAVE]

## S03 — Blood! Fire! Pain!
MAP: `silk_dump` · TRIGGER: go to the dump
(A reeking garbage heap above the sea. A cheerful little eta in a stained apron waves: MUIKA, the mortician.)
MUIKA: You're the clerk! The fish-hat clerk! Everyone's talking about you.
GENDO: Everyone is very well informed.
MUIKA: The body's under the tarp. Skinned — well, not *skinned*. That's the strange thing.
GENDO: (lifting the tarp; a pause) …His tattoos are gone. The skin is blank.
MUIKA: Like someone poured them out of him. Thirty years I've washed the dead. Never seen that.
(The earth under the dump trembles. Faint voices rise out of the ground.)
EARTH KAMI (many voices): BLOOD! FIRE! PAIN! BLOOD! FIRE! PAIN!
GENDO: (stepping back) …Earth kami. Driven mad.
(On top of the heap, eating a persimmon, sits a tattooed monk with a shaved head and a cheerful face: TOGASHI YOSAI.)
TOGASHI YOSAI: That's Togashi blood in the ground. It makes the spirits hysterical. Like sugar for children.
GENDO: And you are?
TOGASHI YOSAI: Yosai. Togashi. (pointing the persimmon at the body) That's Nobue. He owed me three strings of coin and a poem.
TOGASHI YOSAI: I suppose I'll never get the poem.
GENDO: You knew him.
TOGASHI YOSAI: We were brothers in the Order. (brightly) He's the third brother to die like this this year.
TOGASHI YOSAI: If the pattern holds, I'm next! So I thought I'd come and see who's doing it before it's my turn.
TOGASHI YOSAI: Saves time.
MUIKA: (delighted) Oh, I *like* him.
GENDO: (polishing his spectacles very slowly) …Would you like to help a junior yoriki with no authority?
TOGASHI YOSAI: Would I! I've never been useful to the law before. It'll be a new way to nearly die.
[GUEST +Togashi Yosai] (skills: Dragon's Breath — Fire AoE, burns him too, 2 uses; Arrowroot — heal ally, he takes
half, 2 uses; passive Crow: Taint-immune, Shadowlands foes target him)
TOGASHI YOSAI: (counting on his fingers) That's seventeen.
GENDO: Seventeen what?
TOGASHI YOSAI: Times the Fortunes have tried to kill me. I keep count. It's only polite.
### Town NPCs — `silk_docks` / `silk_dump`
| NPC | Default line | Discern info | Path action |
|---|---|---|---|
| Muika | "The dead tell the truth. The living tell me about the weather." | "Washed all three monks. All three had their tattoos taken." | — |
| Kosai (minder) | "Captain says don't go anywhere. Go anywhere you like." | "Paid by Tadayasu to report everything. Badly." | — |
| Net-mender | "Monks? One came to the Rakusho school a lot." | "Saw a 'Crane gentleman' with Nobue." | — |
| Storm Legion thug | "Move, fish-hat." | "Carries a Tortoise Island ferry token." | *Sumai* (if Natsuko): token |
| Fishwife | "Two monks bought my eels. One never came back for change." | — | *Barter:* eel (heal) |
| Kosai (again) | — | *Eavesdrop:* "He reports at the boathouse at dusk." | — |
| Storm Legion thug (again) | — | — | *Pilfer:* Storm Legion Token (sell) |
| Mantis bushi (docks) | "Clerks don't carry swords." | — | *Duel* (Iaijutsu 1): Fisherman's Kama · Glory +1 |
| Rakusho teacher | "Riichi! Again!" | — | *Charm:* follows ("Recitation": Confuse 1 enemy, 2 uses) |
| Muika (again) | — | — | *Bless:* follows ("Mortician's Calm": cures Terror, 2 uses) |

## S04 — The Boy Who Remembers Wrongly
MAP: `rakusho_school` · TRIGGER: follow the net-mender's lead
(A temple school. Children recite Tao verses. One boy, slightly older, recites louder and wrong: RIICHI.)
TEACHER: Riichi! Again! You've said it wrong again!
RIICHI: (calmly) No, sensei. I said it exactly wrong.
(The teacher throws up his hands. Gendo kneels beside the boy.)
GENDO: Who taught you to say it exactly wrong, Riichi?
RIICHI: The monk. Three monks. One after the other. "Say it exactly wrong, Riichi. Exactly."
RIICHI: People laugh at me. I don't mind. I remember everything. They forget.
[PA Discern Riichi] → "Each monk changed different words in the same verses. The changed words form directions."
> CHOICE "How do you ask him?"
  - "Recite it slowly, for me." → [SET riichi_trusts] RIICHI: (smiling) Nobody ever asks slowly.
  - "Write it down." → RIICHI: (frowning) I don't write. I *remember*. (he recites it anyway, but sulks; banter changes)
(Riichi recites. Gendo's lips move along with him. His pen flies.)
GENDO: (muttering) "The fourth step"… "three stones, thirty-three paces"… "twenty up the wall"…
GENDO: It isn't scripture. It's a map. Up the stairs of the ruin. Kyuden Gusai.
RIICHI: Did I say it perfectly?
GENDO: (very gently) You said it perfectly wrong, Riichi. That's the hardest kind.
### Optional — Kitsuki Momo
(A young woman in Kitsuki colours with farmer's hands, investigating a stolen-plum case: KITSUKI MOMO.)
KITSUKI MOMO: You're the fish-hat clerk!
GENDO: The reputation precedes me like a smell.
KITSUKI MOMO: I was a plum farmer's daughter until I saved my lord from a snake. Now I'm a magistrate who investigates plums.
KITSUKI MOMO: Let me help with something that isn't plums. Please.
[GUEST +Kitsuki Momo (optional)] [SET momo_joined] (skill "Perfect Recall": reveal weakness, 2 uses)
[SAVE]

## S05 — The Stairs of Kyuden Gusai (dungeon)
MAP: `gusai_ruins_1–3` · TRIGGER: travel to the ruin
NARRATION: Kyuden Gusai. Torn down after its lord's hostage plot. Its stairs still climb to nothing.
### Dungeon layout = the code (no puzzle UI)
- Ruins 1: the **fourth step** has a loose stone → a hidden footpath opens (cutscene on interaction).
- Ruins 2: **three stones, thirty-three paces apart**, each with a carved arrow → follow them (arrows appear as
  marked interaction points).
- Ruins 3: **twenty stones up a wall** → a hollow behind the twentieth → the monks' notes.
[BATTLE b_gusai_thugs_a] (Tadayasu's kama thugs — they've been following)
TADAYASU'S THUG: Captain says the fish goes back in the water!
TOGASHI YOSAI: (cheerfully) Eighteen?
GENDO: Not yet. Stand behind me.
TOGASHI YOSAI: You're a clerk.
GENDO: I'm a clerk with a Mirumoto sword I rarely draw. (drawing it) This is rarely.
[BATTLE b_gusai_thugs_b]
(The hollow. A bundle of oiled paper. Gendo reads by lamplight.)
GENDO: "Ayaru. Then Jotaro. Then Nobue. Each of us has followed the old man. Each of us will die."
GENDO: "Togashi Akuro. An ise zumi of our order. His last tattoo showed him a vision he could not bear."
GENDO: "He can change his face. Where he walks, there is no Taint. Only absence."
(Yosai has gone quiet. For the first time, he isn't smiling.)
TOGASHI YOSAI: …Akuro taught me to sit still. When I was nine. Six hours on a cold stone. I cried the whole time.
TOGASHI YOSAI: He brought me rice afterwards and said crying was just stillness leaking.
TOGASHI YOSAI: (a long breath; then, brightly, too brightly) Well! That's ruined that memory.
[SAVE]

## S06 — The Terrified Artist
MAP: `silk_boathouse` · TRIGGER: the notes mention "the Crane who helps us"
(A boathouse. A thin, elegant Crane artisan cowers among nets: KAKITA KUMPEI.)
KAKITA KUMPEI: Don't hurt me! I only helped the monk with his paintings! I'm an artist! I'm harmless!
GENDO: Of course. (Deduce prompt)
[PA Discern Kumpei] → "Rare blue pigment on his fingernails — the same blue as the stolen tattoos' ink."
→ second layer (Investigation 2): "Says he left the island the night Nobue died. The tide tables say no boat could."
GENDO: (internal) Evidence: paint, tide, a lie about tide tables. Testimony against it: a Crane with beautiful manners.
GENDO: (internal) Every court in the Empire believes the manners.
> CHOICE "Kumpei"
  - "Accuse him now." → [SET kumpei_accused]
      GENDO: You were there when Nobue died.
      KAKITA KUMPEI: (tears, instantly) How dare you! A Crane! Accused by a — a *clerk*!
      (Tadayasu, at the door, laughing:) TADAYASU: The fish-hat accuses a Crane artist! Off the island, clerk!
      (Glory −1; Gendo was right, and nobody cares.)
  - "Thank him. Watch him." → [SET kumpei_watched]
      GENDO: Thank you, Kumpei-san. You've been very helpful. (bowing) Please don't leave the island.
      (Outside.) TOGASHI YOSAI: He did it. GENDO: Yes. TOGASHI YOSAI: You let him go. GENDO: I let him *run*.
      GENDO: Men who run go somewhere. I'd like to know where.
(Either way: that evening Kumpei slips away by boat toward Tortoise Island.)

## S07 — The Tide (BOSS)
MAP: `tortoise_beach` (dusk) · TRIGGER: go after Kumpei
(The departure beach. A borrowed fishing boat. Figures waiting on the sand with dull eyes: ronin shugenja, and
Mantis thugs — all murmuring the same phrase.)
HYPNOTISED SHUGENJA: (together, flat) …you're at the end of your rope… the end of your rope…
GENDO: (Deduce) Someone planted that sentence in them. They aren't choosing this.
TOGASHI YOSAI: Akuro used to do a trick like that with a sake cup and a whisper. I thought it was a party trick.
[BATTLE b_boss_tide]
### GIMMICK — the tide
"Every 3 turns, **the tide comes in**. The front row becomes **Waist-deep** (Speed and Evasion down), then
**Drowning** (damage each turn). Defeat the shugenja first — or swap your formation."
### Battle barks
- Tide rising, GENDO: "The water won't wait for evidence. Neither should we."
- Interrogate (or Haruki's Know the Mind) on a shugenja: HYPNOTISED SHUGENJA: "…rope… what rope…?" (he stops fighting)
- Yosai hit: TOGASHI YOSAI: "Ow! Eighteen and a half!"
(Victory. The tide covers the sand. The shugenja wake, shivering, remembering nothing. Yosai fetches a blanket for
each one from the wrecked boat.)
TOGASHI YOSAI: There. Now you're only cold and confused, like the rest of us.
(The boat is wrecked. Kumpei's sail is a white speck heading for Tortoise Island.)

## S08 — No Authority, All the Same
MAP: `guest_house` · TRIGGER: after the boss
(Oharu, propped on cushions, still grey, listens to everything.)
KITSUKI OHARU: You let a Crane walk free because you couldn't prove it yet.
GENDO: Yes, Oharu-sama.
KITSUKI OHARU: You followed a code a child remembered wrongly.
GENDO: Perfectly wrong, Oharu-sama.
KITSUKI OHARU: (smiling, closing her eyes) I name you to continue the case under my seal.
KITSUKI OHARU: They won't respect you, Gendo.
GENDO: No, Oharu-sama. (polishing his spectacles) But they'll remember being wrong about me.
GENDO: That will have to do.
(The next morning. Gendo pays a fisherman out of his own purse. Tadayasu watches from the docks, laughing.)
TADAYASU: Off to fish, clerk?
GENDO: (stepping into the boat) Off to catch something.
[CHAPTER COMPLETE]
### Chapter complete card
**"Under the Skin" — complete.**
Journal: *A senior magistrate poisoned, a seal in a clerk's hand, three monks emptied of their ink — and a cheerful
tattooed man counting the ways he might be next. Gendo goes to Tortoise Island with no authority at all.*

---
## Travel Banter unlocked by Dragon Ch1
### TB-dragon1-a "Seventeen" (Gendo + Yosai, guest banter)
GENDO: You keep a count of attempts on your life.
TOGASHI YOSAI: Eighteen and a half now.
GENDO: What's the half?
TOGASHI YOSAI: The poison was meant for Oharu-sama. But I tasted the cup to check. I'll allow it as half.
GENDO: …You tasted poisoned tea to *check*?
TOGASHI YOSAI: How else do you find out?
### TB-dragon1-b "Spectacles" (Gendo + Rensei)
RENSEI: Your spectacles are gaijin glass. That's… scandalous.
GENDO: My eyes are Rokugani and they don't work. My spectacles are gaijin and they do. Which should I be loyal to?
RENSEI: (long pause) …I'll need to think about that.
GENDO: Good. Thinking is also scandalous.
### TB-dragon1-c "Clerk" (Gendo + Tamotsu)
TAMOTSU: Nine years as an archive clerk? I'd have died of boredom.
GENDO: I read every lie the Dragon ever filed. It was the least boring job in the Empire.
TAMOTSU: (laughing) Then you'll love court. It's the same lies, but they serve snacks.
