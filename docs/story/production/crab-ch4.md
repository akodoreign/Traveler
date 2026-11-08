# PRODUCTION — Crab Ch4 · "The Fairest One of All"

**Traveler:** Hiruma Natsuko · **Lv** 41–45 · **Outline:** `scripts/crab-ch4-the-fairest-one-of-all.md`
**Flags read:** `guard_rescued`, `blue_flare_held`, `nezumi_friends`, `same_woman_proven` · **Flags set:**
`flare_fired`, `kage_told_truth`, `nashiko_unmasked`, `dread_count`
**Maps:** `kyuden_hida_wedding`, `kyuden_hida_town` (summer), `kyuden_hida_siege`, `cellars`, `dark_castle_1–3`,
`trap_tunnels_deep`, `wall_top` · **Storyboard:** `storyboards/crab-ch4.md`
**Battles:** `b_siege_breach_a/b` (storyboard), `b_boss_tsukakoro`
**Set-piece:** the stalking sequence (no combat: identify Nashiko by her tells; a "dread" counter)

---

## S01 — A Wedding at Speed
MAP: `kyuden_hida_wedding` · TRIGGER: start
NARRATION: Summer at Kyuden Hida. The court needs a Hiruma heir. So the court has arranged a wedding — quickly.
(A hasty, grand ceremony. HIRUMA KAGE, numb, in borrowed finery. Beside him, radiant: ASAKO KUHIME. Natsuko stands at
the very back.)
ASAKO KUHIME: (afterwards, to Natsuko, warmly) You brought him home from the Shadowlands. I'll never forget it.
ASAKO KUHIME: (beat) I never forget anything.
NATSUKO: (bowing) My lady.
(Kuhime glides away. Natsuko watches her lift a cup of scalding sake for a toast, and drink it without a flicker.)
NATSUKO: (to herself) …I've seen someone drink sake like that before.
[IF same_woman_proven] NATSUKO: (very quietly) Garden Under Shadow. Yasuki Yashiki. *Her.* [END]
[SAVE]
(Free roam in the castle town. Prompt on the castle gate: "Night will fall when you return to the castle.")

## S02 — Every Trap Is Wrong
MAP: `kyuden_hida_siege` · TRIGGER: that night
(War drums. The Shadowlands strike the Wall — Oni no Tsume's horde, torches to the horizon.)
KAIU TAKAKANA: (running, naginata in hand) The traps! Every trap inside the castle — tampered! Rollers jammed, pits filled!
KAIU TAKAKANA: Somebody's been busy from the *inside*.
[IF guard_rescued]
(The half-mad old guard from the Shadowlands, wrapped in a blanket, grabs Natsuko's arm.)
BROKEN GUARD: Sector four… sector *six*… the east stair… they're wrong. All wrong. I counted. Nobody listens to me.
NATSUKO: I'm listening, uncle. Which ones are still right?
BROKEN GUARD: (pointing a shaking finger at the old lower tunnels) …Down. The old ones. Nobody remembered to sabotage the old ones.
[END]
KAIU TAKAKANA: Scouts to the Wall! Bodyguards — get the court into the cellars! Hiruma — cellars.
NATSUKO: Takakana-sama, I'm a *scout*—
KAIU TAKAKANA: The Champion's guests must live. Most of them. Go.
(The outer yard: goblins on ladders. Tampered trap tiles hurt — [IF guard_rescued] the old guard calls out each one,
and they're marked [END].)
[BATTLE b_siege_breach_a]
(The cellar stair. An ogre has broken through and goes for the courtiers.)
[BATTLE b_siege_breach_b] (Razor's Edge draws it off the courtiers)

## S03 — The Barrel
MAP: `cellars` · TRIGGER: herding the court below
(Lantern light among the pickle barrels. Frightened courtiers. One barrel sealed with fresh wax, though nobody has
opened the cellar in weeks. A smell.)
NATSUKO: (prising the lid; looking in; her face goes still) …
(She sets the lid back down, very gently.)
NATSUKO: (quietly) Two weeks. She's been dead two weeks.
NATSUKO: The real Asako Kuhime.
NATSUKO: (looking up the stairs) …Then who did my lord just marry?
(Upstairs: laughter. A woman's laughter, from every direction at once. The children's quarters are upstairs.)

## S04 — She Can Be Anyone (set-piece)
MAP: `dark_castle_1–3` · TRIGGER: climb back up
### SYSTEM — the stalking sequence
"**Nashiko** stalks the dark castle. She can wear **anyone's face**. Find her by her **tells**:
she doesn't flinch at scalding sake · she thinks smooth stone is jade (colour-blind) · jade burns her bare skin ·
she can read **only one mind at a time** (split the party to confuse her).
A wrong accusation raises the **Dread** counter. If it fills, she knocks out a party member. Lure her to the **old
tunnels** below."
- Each NPC: pick a test (hot sake / smooth "jade" stone / jade-dust glove), then *Accuse* or *Let pass*. A wrong
  accusation, or one made without a test: Dread +1 (max 3). At 3, one traveler is knocked out until the boss; Dread resets.
- *Split up* (at each junction, once per floor): two travelers go different ways; she can only follow one mind.
  Dread −1.
(Save point among the cellar barrels before the climb: [SAVE])
### Encounters (each a disguised NPC — one is Nashiko)
- **A frightened maid** with a tray of sake. (Test: "Your hand's shaking. Drink something hot." — she flinches → real.)
- **A Crab guard** at the stair. (Test: hand him a smooth river stone as "jade for luck" — he says "it's a pebble" → real.)
- **Isawa Akiko**, 13, running. (Test: jade-dust glove — nothing happens → real.)
  ISAWA AKIKO: (crying) Natsuko-san! Lady Kuhime said to come to the roof! She said it was safe!
  NATSUKO: (kneeling) Akiko. Go to the cellars. Squeak — [IF nezumi_friends] SQUEAK: (from a vent) "Squeak take little one! Rat-ways!" [END]
- **A servant with a lantern**: (the lantern gives no warmth)
  NASHIKO (servant's face): Lost, scout? Let me light your way.
  NATSUKO: (handing her a smooth river stone) Here. Jade. For luck.
  NASHIKO: (taking it, pleased — then the jade dust on Natsuko's glove brushes her wrist and *smokes*) …You little *Crab*.
  [SET nashiko_unmasked]
NASHIKO: (her face sliding, laughing) Chase me, then! I love a chase!
(She flees down the stairs — toward the tunnels. Exactly where Natsuko wants her.)
[SAVE]

## S05 — Through the Teeth
MAP: `trap_tunnels_deep` · TRIGGER: pursue
(The old trap tunnels. Natsuko runs them like she was born in them, springing the traps the saboteurs missed behind
her. Nashiko pursues, laughing — and screaming, as rollers hit her, as jade dust rises, as the spiked pit opens.)
NASHIKO: (from the dark, delighted and furious) You're *herding* me! Like a goat!
NATSUKO: (running) Like a goblin. Goats are smarter.
### The blue flare
[IF blue_flare_held]
(The tunnel's exit. Natsuko stops at the mouth, the blue flare in her hand.)
NATSUKO: (to herself) "Something none of us has seen before."
> CHOICE "The blue flare"
  - "Fire it." → [SET flare_fired] (the whole Crab army rings the tunnel exit; +1 turn of army support in the boss)
      (A blue star climbs over the Wall. Every Crab on the Wall turns and stares. Then, everywhere, horns.)
      KAIU TAKAKANA (distant, roaring): BLUE! *BLUE!* Every man to the east tunnel!
  - "Keep it." → (it stays for the finale)
[END]

## S06 — Oni no Tsukakoro at the Wall (BOSS)
MAP: `wall_top` · TRIGGER: the tunnel exit
(The top of the Wall at the tunnel's mouth. Nashiko floats above the battlements, smoke streaming from her burned
wrist, and calls up a bone-cage that bounces like a monstrous ball: ONI NO TSUKAKORO.)
NASHIKO: Play with my pet, Crab. I'm late for a carriage.
[BATTLE b_boss_tsukakoro]
### Barks
- Bounce chain: "It's bouncing — it's going to bounce off all of us!"
- NATSUKO (Razor's Edge): "Bounce off *me*, then!" (redirects the chain)
- [IF flare_fired] Crab archers: CRAB SERGEANT: "Volley! For the scout who fired the blue!"
- Fire and Shadow (+damage vs Shadowlands): NATSUKO: "I know your kind. I know where you *break*."
- Defeat: (the cage collapses into bones that roll off the Wall into the dark)

## S07 — Smoke and Laughter
MAP: `wall_top` · TRIGGER: after the boss
(The whole Crab army has the Wall. Nashiko hangs in the air above them, untouchable, laughing.)
NASHIKO: Tell Kage I enjoyed the wedding! Such a *sad* little man.
NASHIKO: I'll wear someone he loves next time. (to Natsuko, sweetly) Maybe *you*.
NATSUKO: (yari raised) Try it. My face doesn't fit anyone else.
(Nashiko becomes smoke, and the smoke flies north on the wind.)
### Kage
(Dawn. The castle quiet. Kage sits alone on the Wall steps, looking at the smoke still drifting north.)
> CHOICE "What do you tell him?"
  - "The whole truth." → [SET kage_told_truth]
      NATSUKO: My lord. The woman you married wasn't Kuhime. Kuhime died two weeks ago. You married a demon.
      HIRUMA KAGE: (a very long silence) …Twice now. Twice I've loved someone in this castle and lost her to the dark.
      HIRUMA KAGE: (standing, slowly) I'll keep the Hiruma alive, Natsuko. I swear it. Not by marrying. Not by dying.
  - "A kinder version." → (Honor −1)
      NATSUKO: She fled with the Shadowlands, my lord. She was… never what she seemed.
      HIRUMA KAGE: (nodding, not understanding) …I'll keep the Hiruma alive. I swear it.
(Kage presses his father's tanto into her hands.)
HIRUMA KAGE: Someday we'll walk your father's road.
HIRUMA KAGE: Not by dying.
NATSUKO: (bowing) Not by dying, my lord.
(She looks north, where the smoke went.)
NATSUKO: (to herself) …North. You keep running north.
[ITEM +Kage's Father's Tanto (Jade-element Tanto)]
[CHAPTER COMPLETE]
### Chapter complete card
**"The Fairest One of All" — complete.**
Journal: *A wedding at speed, a barrel in the cellar, and a demon in a bride's face. Natsuko hunted her through a
dark castle using pebbles and jade dust, and herded her out onto the Wall. She escaped north on smoke — and Natsuko
is following.*
[UNLOCK] *Shards of Earth* kata at Lv 51 · `nashiko_unmasked` (finale debuff)

---
## Travel Banter unlocked by Crab Ch4
### TB-crab4-a "Pebbles" (Natsuko + Rensei)
RENSEI: You defeated the most terrifying creature in the Empire with a pebble.
NATSUKO: A smooth pebble. Smoothness matters.
RENSEI: (very seriously) The Kakita Academy has nothing on this.
### TB-crab4-b "North" (Natsuko + all, at the inn)
NATSUKO: She ran north. From Kyuden Hida. From the Crane border. Everywhere.
GENDO: (unrolling a map) North-east, if you draw the lines.
SHIZUE: (placing go stones on the map, one for each sighting) …They converge.
NATSUKO: Where?
SHIZUE: (one stone, very deliberately) Shinomen Mori.
