# Script — Lion Ch2 · "Shadow of a Doubt" (TEMPLATE for the user's approval) — DRAFT v0.1

**Purpose:** a voice-and-format template for all chapter scripts. It covers the whole chapter at scene level, with
sample dialogue. A production script would add every line, branch and barks.
**Source:** *Shadow of a Doubt* (Weepie & Hobart, 1999). Plot facts only; **all dialogue is original**.
**Traveler:** Akodo Shizue · **Rank 2**, recommended Lv 20–25 · **Winter 1122–23**, Shiro Akodo.
**Systems shown:** a calendar hub with festival minigames, the Duel path action (the bokken bracket), Discern and
Eavesdrop clues, an escalation clock (stolen objects), jade prizes that matter later, a charm boss, and an epilogue
branch.

Format key: `NAME:` dialogue · *(stage direction)* · `[CHOICE]` · `[BATTLE]` · `[FLAG name]` · `[SYS]` = systems
note.

---

## Scene 1 — "The Far End of the Hall"
**Where/When:** Shiro Akodo, Hall of Honors · Week 1, Day 1 (opening ceremony)
**Cast:** Shizue, Akodo Hiruto (her uncle), Akodo Toturi, Kaiu Gesshin, Akodo Nishi, Akodo Kafu
**Beat:** Shizue sits at the very end of her uncle's retinue, so far back she can barely see the Champion. The
Crab envoy's speech is famously cool. Nishi, who taught Shizue go one summer, recognises her.

*(Wide shot: ranks of kneeling samurai under ancestor portraits. The camera slides past the great names and stops at
the last cushion: Shizue.)*
NARRATION: Winter Court at Shiro Akodo. Three hundred samurai, and one of them is so junior that the servants pour
her tea last.
KAIU GESSHIN: *(standing, unhurried)* The Crab were asked for their opinion of the Akodo. I have looked. My verdict
is… sufficient.
*(A ripple. Uncle Hiruto doesn't move a muscle. Shizue hides a smile behind her sleeve.)*
SHIZUE: *(aside)* "Sufficient." From a Crab, that's a love poem.
*(After the ceremony, in the corridor. Nishi stops, turns back.)*
AKODO NISHI: You. The girl who sacrificed three stones on the left edge to win the centre. Shizue, wasn't it?
SHIZUE: *(bowing far too low)* Nishi-sama remembers a game from four summers ago?
AKODO NISHI: I remember the moves that surprised me. There have not been many. *(a flicker of something sad)* Come
to the North Dojo some evening. I'd like an opponent who isn't trying to flatter me.
*(Behind Nishi, Akodo Kafu waits. He looks at Nishi a moment too long, then away.)*
`[FLAG met_nishi]` `[SYS]` Rank-1/2 rule: Toturi never addresses Shizue here. NPCs with high Glory have "brief
audience" dialogue only.

## Scene 2 — "The Castle as a Calendar" (hub)
**Where/When:** Shiro Akodo (explorable) · Weeks 1–11
**Beat:** The castle is the town map. A **calendar scroll** on the pause menu shows the court's events. Each event
advances the clock; between events Shizue explores, does side stories and uses path actions.
- **Map areas:** Central Dojo (the bushido paintings in sequence; the Sorrow's Path mural), North Dojo (Nishi), South
  Dojo (Kafu), Central Garden (winter flowers), Hall of Honors, Hall of Akodo (trophies, mostly Crane), library,
  kitchens, baths, guest wing. The upper floor is off-limits (the war-plans chamber).
- **Recurring NPC routines:** Kaiu Yutaka paints in the garden mornings; Kaiu Mami re-fights sieges with origami;
  **Daidoji Atsuko** reads in the library and stops when anyone approaches; **Moto Benjiro** sits alone in the
  stables, mocked by Crab guards.
- `[SYS]` **Escalation clock:** after each festival, one object in the castle is *gone*. Its empty spot stays visible
  on the map (environmental storytelling). The Discern / Eavesdrop / Inquire info on servants changes each week.

## Scene 3 — "Tranquillity" (painting contest)
**Where/When:** Central Garden · W1 D5
**Beat:** Paint something that conveys the garden's *tranquillity*, not the garden itself. A choose-the-theme puzzle
(three right answers, four literal wrong ones).
- Prize: Scroll of Acclaim (+Glory).
- **After:** a blossom is missing from the prize tree. Nobody but Shizue (Perception) notices.

KAIU YUTAKA: *(showing his painting: a Wall battle, and below it a mother bird feeding chicks in a nest)* The Wall is
the noise. The nest is what the noise is for.
SHIZUE: Then your painting isn't of the Wall at all.
KAIU YUTAKA: *(pleased, embarrassed)* Don't tell the judges.

`[SYS]` A minigame result affects only rewards; the story never locks behind a minigame.

## Scene 4 — "The Bracket" (bokken tournament = Duel path action showcase)
**Where/When:** Central Dojo · W2 D3
**Beat:** A ladder of four 1-on-1 **Duel** battles with bokken (non-lethal), each opponent showing one kata.
The final is against **Kaiu Yutaka**, who fights like a wall.
- **Prize: a miniature jade-bladed tanto** (a jade-element Tanto: the first anti-oni weapon).
- **After:** the painting and plaque **"Duty"** is missing from the Central Dojo. Suspicion falls on the Crane guest.

*(Final round. Yutaka hasn't moved his feet once.)*
SHIZUE: *(internal)* He wants me to come to him. Every Crab wants you to come to them.
`[CHOICE]` *Wait him out* (Defend + Read the Field) · *Feint, then strike* (Feint → Heavy Blow) · *Command myself*
(Talent: act twice)
*(Win or lose, Toturi, seated above, says two words to his karo. The karo writes something down.)*
`[FLAG bracket_result]` `[SYS]` Duel = path action rules (`skills.md`); the bracket is the tutorial for Iaijutsu
Focus in duels.

## Scene 5 — "To Know a Man's Ancestors" (history dinner)
**Where/When:** Hall of Honors · W3 D1
**Beat:** Guests tell histories. Kafu tells of an Akodo who betrayed a Matsu woman he loved for his lord's sake:
*his own confession, disguised*. A dialogue-choice minigame.
- Prize: **a jade-headed flesh-cutter arrow** (a Barbed Shot with Jade element).

AKODO KAFU: *(the hall quiet)* …and the story says he never wept, because duty does not weep. The story is wrong.
He wept every night for thirty years. He simply did it where no one could see.
*(Nishi sets her cup down very carefully.)*
`[SYS]` **Discern on Kafu** here reveals: *"Has not slept in days. Something speaks to him at night."* **Eavesdrop
in the kitchens** reveals: *"The South Dojo is cold even with the braziers lit."*

## Scene 6 — "The Bushido Debate" (Hall of Honors → the banner)
**Where/When:** Hall of Honors · W4 D4
**Beat:** A formal debate on the virtues. **This is the dress rehearsal for the finale's debate** (`03-crossroads`):
same UI, low stakes. Shizue argues *Honor*.
- Prize: an illuminated copy of *Akodo's Leadership* (+1 rank to the Battle skill).
- **After:** the **Crane banner of Sorrow's Path**, the Lion's great trophy, is gone from the Hall of Akodo. The
  court erupts; every eye turns to **Daidoji Atsuko**.

SHIZUE: *(rebutting a Matsu speaker)* You say honour is the lord's to define. Then whose honour was it at Sorrow's
Path, when both armies called themselves righteous? Honour isn't a banner someone can steal from a wall.
*(Silence. Then, from the high seats, Toturi, for the first time:)*
AKODO TOTURI: Who is that?
KARO: Akodo Hiruto's niece, my lord. A junior strategist.
AKODO TOTURI: *(that is all he says)*
`[FLAG toturi_knows_name]` `[SYS]` Glory +; from now on Toturi's "brief audience" lines use her name.

## Scene 7 — "The Sword That Isn't Being Rewrapped"
**Where/When:** South Dojo / swordsmith's shed · W6 D1
**Beat:** Kafu no longer wears his ancestral katana; he claims it's being rewrapped. The swordsmith has never seen
it. Servants hear voices in the South Dojo at night. A **night exploration** segment: the South Dojo after dark,
cold, the braziers guttering, a wet trail on the floor that hisses where it touches wood.
- `[BATTLE]` Mid-encounter: *"fear-shades"* (Terror-inflicting minor spirits), the oni's leavings. Teaches that
  **Terror** exists and that jade gear helps.

SWORDSMITH: Rewrapped? Kafu-sama's blade? Lady, if that sword came to my shed I'd have bowed to it for an hour first.
It has not been here.

## Scene 8 — "The Dance" (contest) · "The Seal" (arrest)
**Where/When:** W7 D6 → W8 D7
**Beat (dance):** a timing minigame; partners cover each other's slips. Shizue may partner Kaiu Yutaka, Atsuko or
Benjiro (which gives a different banter line). Nishi dances with her betrothed, smiling the whole way through, and her
smile breaks only once.
- Prize: **jade-inlaid war fans** (a party accessory: +resist Terror).
**Beat (arrest):** Toturi's **seal and mon** are stolen. Atsuko is dragged in; **Shizue has one week to clear her.**
- Clue chain: Atsuko's spartan room (she has studied *only* the anti-Crane war plans, so she *is* a spy, but not this
  thief); the wet hissing trail again; the missing objects form a pattern: a scarf, a flower, *Duty*, the banner, a
  sword, letters, a seal. **"Everything Kafu loves, in order."**

DAIDOJI ATSUKO: *(in the cell, calm)* I will tell you exactly one true thing, Lion, because you came yourself instead
of sending a servant. I did not take the seal. I did read your war plans. Both of those are true, and only one of them
is a crime your Champion can prove.
`[CHOICE]` *Promise her nothing* · *Promise to clear her of the theft only* (honest) · *Promise to free her* (a lie:
Honor −)
`[FLAG atsuko_promise]` → pays off in **Lion Ch4** (Atsuko as the go-between).

## Scene 9 — "Something With No Name Yet"
**Where/When:** Stables · W11 D1
**Beat:** **Moto Benjiro**, white death-mask painted on, preparing to ride into the Shadowlands to die well, asks for
help. He can *feel* the evil but not its name.
- **Guest: Moto Benjiro** joins (*Death Trance*: party Terror immunity, 1 use).

MOTO BENJIRO: The Crab laugh at me because my family rides toward death instead of away. But I know the smell of
it, Lion. It is in this castle. It has been eating someone for weeks, slowly, the way a coward eats.
SHIZUE: Kafu-sama.
MOTO BENJIRO: *(not surprised)* Then we must hurry. A coward, once it is fat enough, becomes brave.

## Scene 10 — "The Coward's Feast" (climax) · BOSS
**Where/When:** South Dojo, the night before the wedding · W11 D6
**Beat:** Shizue and the party find Kafu kneeling in the dark before a thing like a slug the size of a horse, with a
ring of teeth: **Oni no Ianwa**. It has no attacks of its own. It **charms party members into attacking each other**.
- **Talk-down first:** before the fight, `[CHOICE]` reach Kafu.
  - *"Nishi"*: he flinches.
  - *"Duty"*: he laughs bitterly.
  - *"You told the story of the man who wept. Weep now, where I can see."* This one works if `met_nishi` and you
    heard the history dinner.
  - Success → `[FLAG kafu_joins]`: Kafu fights *with* you (guest for this battle only).

`[BATTLE]` **Oni no Ianwa**:
- Resolve 10. Weak: **Jade** (the tanto, the arrow, the fans), Fire.
- Gimmick: each turn it Charms one ally (Terror-Charm). Jade gear cuts the chance, and Benjiro's *Death Trance*
  blocks it for one round.
- **Coward rule:** on its first Suki it **flees through the floor**. Battle won.

ONI NO IANWA: *(voices layered, all of them Kafu's)* He gave me everything. One small thing at a time. You would all
give me everything too, if I asked politely enough.
SHIZUE: Then I'll be rude.

## Scene 11 — Epilogue (branch)
- **`kafu_joins` = true:** at dawn, Kafu asks Toturi's leave for seppuku. It is granted. In his last line he looks
  past Nishi to the mountains: *"You can see all the way to the Spine this morning. I'd forgotten."* Nishi's wedding goes ahead at noon, and she doesn't cry until
  the evening, alone in the North Dojo, where Shizue finds her and says nothing and sets up the go board.
- **`kafu_joins` = false:** Kafu is taken in chains. Toturi orders his name cut from every record: "The Akodo
  have no son called Kafu. Not any more." Nishi's wedding goes ahead. The go board scene still happens, but Nishi doesn't play.
- **Both:** Atsuko is released of the theft (per `atsuko_promise`), but expelled from court for spying. The stolen
  objects turn up in the oni's lair, **except the plaque "Duty"**, which is never found. *(Finale: it hangs in
  Nashiko's glade.)*
- **Toturi** to Shizue, in passing in a corridor, without stopping: "Akodo Shizue. Again." *(→ Ch3: his karo
  chooses her for the message.)*

`[SYS]` **Rewards:**
- 2 jade weapons and the war fans.
- Glory +2, plus Honor + if Kafu was redeemed.
- Battle skill *Read the Field*, if you won the bracket.

**Recruitable after this chapter:** Moto Benjiro as an Allies' Muster guest (`04-cast`).

---

## Format notes (for the user's approval)
1. **One file per chapter**, scene-by-scene, with sample dialogue at the key beats. The full line-by-line pass comes
   at production.
2. **Every scene states its systems** (`[SYS]`) so the engine work can trace story → mechanics.
3. **Branches are flags**, kept few (Octopath-style): they colour epilogues and later chapters, never block progress.
4. **Voice:**
   - Narration is short and wry.
   - Lords speak in few words, which keeps the low-status rule.
   - Each traveler has a verbal habit: Shizue frames things as go moves; Natsuko has gallows humour; Rensei is
     over-formal until he forgets to be.
