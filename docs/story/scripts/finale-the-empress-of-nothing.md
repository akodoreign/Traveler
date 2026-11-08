# Script — Finale · "The Empress of Nothing" — DRAFT v0.1

**Sources:**
- *Of Family and Honor* Round Two: the shrine defence, Shinomen Mori, Nashiko's attack on bushido
- *Mirror, Mirror*: Nashiko's facts and her death
- story/03

Plot facts only; **all dialogue is original**; Nashiko's arguments are **paraphrased** (story/03 table).
**Unlock:** all eight Chapter 4s cleared (OT1 hidden-ending model). **Recommended Lv 55–60** (Rank 4).
**Time:** the end of the Month of the Monkey, 1123, weeks before the Coup (14th of the Rooster ≈ October).
**Octopath shape:** four acts, each with one centrepiece:
- Act 1: a defence-wave battle (set-piece)
- Act 2: a journey dungeon (the Kumo courtesy test)
- Act 3: the **debate** (set-piece)
- Act 4: a multi-phase final boss, fought by **two parties of four** (OT1's final-boss model)

**Finale debuffs earned in the chapters** (each reveals or removes one Nashiko shield at the start of Act 4):
| Flag / item | From | Effect |
|---|---|---|
| `nashiko_unmasked` | Crab Ch4 | Phase 1: she can't turn invisible on turn 1 |
| the play (`play_known_scenes` 1–3) | Crane Ch4 | Up to 3 shields revealed; "Empress" bait (drops her guard for 1 turn) |
| the Bloodspeaker-hunting book | Phoenix Ch4 | Blood Shouting broken: damage no longer transfers to her champions |
| `same_woman_proven` | Crane Ch2 | Her disguise phase is skipped |
| `sayo_saw_nashiko`, `mitsue` glimpse | Ronin Ch4, Scorpion Ch4 | Her mind-reading is limited to one target from the start (per canon: one mind at a time) |
| crystal shard / jade gear | Scorpion Ch2, Unicorn Ch3, Lion Ch2 | Crystal and Jade attack items in the inventory |
| Kage's blue flare (if kept) | Crab Ch4 | Act 1: the Crab arrive one wave early |

---

## ACT 1 — "The Shrine of Osano-Wo" (set-piece: defence waves)
**Where:** the Plains of Thunder. The Shrine of Osano-Wo: a stockade, a hundred monks, peasants, stores of powdered
jade. **Jinnai**'s order (Ronin Ch2).
**Beat:** A Shadowlands host marches out of the Shinomen Mori. All eight travelers arrive from eight roads; their
first scene together. **Travel Banter: "Eight Roads"** (each traveler names who sent them, and nobody did: they came
on their own).
`[SYS]` **Defence-wave battle**, adapted from *Of Family and Honor* R2:
1. Goblin swarm.
2. Hold the breach (Natsuko's Razor's Edge shines).
3. Burning goblin fanatics.
4. Ogre battering ram.
5. Save the abbot (escort).
6. Close the breach.
7. A spidery horror (wave boss).
- **Two parties of four alternate waves** (swap at the stockade gate).
- **"Ryozo"** (the nameless oni from Crab Ch1/Ch3, wearing the guardsman's armour) leads wave 4.
  `oni_named_ryozo` = false: an ordinary ogre captain instead. If true, Natsuko gets a closing line:
  NATSUKO: You took a good man's name. *(Razor's Edge)* Give it back.
**After:** a herald with blue eyes walks out of the smoke, unharmed.
HERALD: The Empress congratulates you. She awaits you in Shinomen. Four days. *(beat)* Or this shrine burns, and
everyone in it.

## ACT 2 — "Shinomen Mori" (journey dungeon)
**Beat:** A long forest dungeon with save shrines.
- **Stich'Kik**, a one-handed, tortured nezumi slave, guides them, and begs to be killed when it's over. If
  `nezumi_friends`, Squeak recognises his tribe-marks. The party can **free** him instead (canonical); he joins the
  nezumi of Crab Ch1.
  STICH'KIK: Kill-kill after, yes? Stich'Kik good-good guide. Then kill.
  SQUEAK: *(furious, tiny)* No-kill! Come-come live in dry-cave. Is nice. Has eggs.
- **The Naga are waking:** drag-marks of enormous serpents (canon 1122–23; the Naga champion from Ronin Ch4 may nod
  from the trees).
- **A carved mock-seppuku scene** in a clearing, with a sneering inscription *(paraphrased)*: "this is your bushido,
  in truth." Each traveler reacts in one line.
- **Mamoru the Kumo:** an old hermit by a fire. **The courtesy test:** treat him with respect (Etiquette and
  dialogue), and he lets you pass and warns you of her one weakness. Be rude, and a spider fight follows.
  *(Rensei and Tamotsu lead this naturally.)*
- **The glade:** corrupted, beautiful, wrong. On a tree hangs the **plaque "Duty"** stolen from Shiro Akodo (Lion
  Ch2). Shizue takes it down.

## ACT 3 — "The Debate" (set-piece)
**Where:** the glade. **Doji Nashiko** in her loveliest form, on a mat of leathery hide, receiving them like a court.
**Beat:** She attacks bushido tenet by tenet (story/03 table, paraphrased). The **debate UI** is the one rehearsed in
Lion Ch2 and Phoenix Ch2.
- **Doubt beat (the design twist):** she first strikes each traveler through their clan's *least-valued* tenet. For
  example she tells Natsuko she was never courteous, and Rensei that he was never brave. The traveler stumbles.
- **Rebuttal:** then each answers with their clan's paramount tenet, drawn from their own story.
| Tenet | Traveler | Line (from 02-travelers, final form) |
|---|---|---|
| Courage | Natsuko | "Courage is walking back into the dark every morning because someone has to." |
| Courtesy | Rensei | "Etiquette can be a mask for knives. It's also the only thing that keeps two enemies at one table long enough to stop a war." |
| Sincerity | Gendo | "Sincerity is knowing exactly what the lie costs, and paying it yourself." |
| Honor | Shizue | "Honour is what I answer for when no one is watching." *(she sets the "Duty" plaque down between them)* |
| Righteousness | Haruki | "No court ever judged me. So I judged myself, and I spent my life setting it right." |
| Duty & Loyalty | Mitsue | "Duty isn't a leash. It's the promise I keep when I know what it will cost — and I know better than anyone here." |
| Compassion | Tamotsu | "Compassion is the rice you hand over anyway, especially when there's no profit in it." |
| *"Bushido is a child's dream."* | **Sayo** | "Maybe. Nobody ever made me swear to it. No lord, no clan. I picked it up anyway. That's what makes it real." |
- `[SYS]` Each strong answer (the right evidence chosen from the traveler's story flags) **breaks one of her eight
  shields** for Act 4. A weak answer leaves it up: harder, never unwinnable.
NASHIKO: *(after Sayo, very still)* …A peasant's daughter, lecturing an Empress.
SAYO: Ronin's daughter. *(beat)* And you're not an Empress. You never were. That's the whole play.

## ACT 4 — "The Empress of Nothing" (final boss, two parties)
`[BATTLE]` **Doji Nashiko**, in 3 phases. Party A (4) fights phase 1; Party B fights phase 2; the **best 4 of all
eight** fight phase 3 (OT1-style swap screen between phases).
- **Phase 1, "The Bride":** she flies and turns invisible. **Crystal or thin jade** reveals her (items). Her seduced
  champions shield her with **Blood Shouting** (damage transfers to them) unless the Phoenix book broke it.
  Resolve 20.
- **Phase 2, "Body of Damned Time":** an inky starfield. A **turn timer ages the party** (stacking stat drain).
  Kill her quickly or cleanse (Water heals cleanse it thanks to Haruki's "Whole" passive). Resolve 24.
- **Phase 3, "True Form":** a black-edged wound in her throat pulsing with Fu Leng's glowing blood; empty sockets
  glowing blue. Weak: **jade, crystal, obsidian** (obsidian Taints its user: still a temptation to the very end).
  Exploits:
  - A **smooth stone decoy** (colour-blind: she wastes a turn on it).
  - A **disfiguring strike** (any crit to the face staggers her: her phobia).
  - **"Empress" bait** (the play: she drops her guard for 1 turn).
  - Tamotsu's **The Immovable Hand of Peace** (R5, if reached) locks her for one turn.
  Resolve 28 minus the shields broken in the debate.
- **Flight:** at the end she tries to flee, and every path is blocked by the allies the travelers made. A callback
  montage, with each one appearing only if its chapter flag is set:
  - Kage's Crab, Toturi's Lion, the Mirumoto army
  - Phoenix shugenja, Naohida's guerrillas, the eta of Cakon with Hiro, the Kitsune of Kudo, Atsuko's Crane scouts
NASHIKO: *(cornered, faces flickering through every disguise from the eight stories)* I was going to be *Empress*.
GENDO: *(quietly)* You were going to be a footnote. *(beat)* I've filed a thousand of those.
- **Death:** her body fades into an inky void. A **white jewelled porcelain mask** cracks and breaks into motes of
  light: the souls she drank go free. Deep under the Shadowlands, something bellows in grief.

## EPILOGUE — "The Eve"
**Beat:** Each traveler's short coda in their home region (eight brief scenes; flags colour each):
- **Natsuko** walks beside Kage on the first mile of her father's road, then turns back: "Someday. Not by dying."
- **Rensei** performs his kata. His left foot doesn't hesitate. His father watches from a doorway and says nothing.
  It is enough.
- **Gendo** murmurs Akuro's prophecy over his evidence case: "The son will become the dark brother… seven mortals
  will rise." He stops and counts: seven, plus one. He frowns.
- **Shizue** plays go with her uncle. She lets him win once, and he knows.
- **Haruki** brings the book back to Mieko. They don't talk about forgiveness. They talk about camellias.
- **Tamotsu** reaches the valleys with the refugee caravan. Persimmon bites the daimyo.
- **Sayo** sits with seven people who chose her back.
- **Mitsue**, alone, on the road to **Otosan Uchi**, knowing. She touches the Scorpion Favor pendant she kept for
  herself, then keeps walking.
**Final image:** a lantern festival in the capital; a masked figure in red on a rooftop; the first beat of a war drum.
Title card: ***The year is 1123.*** (Before the 14th of the Rooster.)
`[SYS]` **Post-game:**
- R5 content (Lv 61+); the Orochi superboss (Crane Ch3 sighting).
- The Hiruma Castle side story (the canon Hare sword).
- Mirumoto Hikaru's Endless Strike (Gendo).
- Purity of Shinsei (Haruki at Fire 5).
