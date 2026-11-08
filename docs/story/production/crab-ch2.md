# PRODUCTION — Crab Ch2 · "Winter Court at Kyuden Hida"

**Traveler:** Hiruma Natsuko · **Lv** 18–25 · **Outline:** `scripts/crab-ch2-winter-court-at-kyuden-hida.md`
**Flags read:** `nezumi_friends`, `hidden_ones_cleared` · **Flags set:** `wall_crab_trust`, `wall_mud_clue`,
`accusation` (mutsuye / shigeru / onenight), `puppet_spared`, `blue_flare_held`
**Maps:** `kyuden_hida_6f` (audience), `kyuden_hida_court` (floors 1–4), `kyuden_hida_barracks`, `womens_shrine`,
`kyuden_hida_donjon_1–2`, `trap_catacombs`, `kyuden_hida_town` (castle town: inn, shops, dojo), route `hida_wall_road`
**Storyboard:** `storyboards/crab-ch2.md`
**Battles:** `b_duel_noboru` (route only), `b_donjon_goblins`, `b_boss_puppet_troll`
**Fit conversions:** the archery contest is one dialogue choice; the gimmick is the troll as a boss-arena hazard.

---

## S01 — One Glance from the Bear
MAP: `kyuden_hida_6f` · TRIGGER: arrive at Kyuden Hida
NARRATION: Kyuden Hida. Seven floors of black stone. The Great Bear lives at the top, and nobody climbs there twice
by choice.
(The audience hall. HIDA KISADA in the Armor of the Shadow Warrior, unmoving as the castle. Natsuko kneels far
below. The karo, KAIU TAKAKANA — scarred, broad, a naginata over his shoulder even here — presents her.)
KAIU TAKAKANA: Hiruma Natsuko, my lord. Scout of the Wall.
(Kisada looks at her. One glance. Then at the next petitioner.)
(That is all.)
(The corridor outside. Takakana walks fast. Natsuko keeps up.)
KAIU TAKAKANA: Your daimyo, Hiruma Kage, is going to marry.
NATSUKO: My lord Kage? Marry? He's never looked at anyone but a map.
KAIU TAKAKANA: He's looked now. A Phoenix girl. Isawa Mutsuye.
KAIU TAKAKANA: The betrothal is announced at the end of court. Before that, I want her vetted.
KAIU TAKAKANA: If she's Tainted, a Scorpion, or a fool, I want to know before the Champion does.
NATSUKO: Why me? I'm a scout. I can't tell a fan from a fork.
KAIU TAKAKANA: Exactly. Nobody at this court will notice a junior Hiruma. You'll see everything.
NATSUKO: And if she's none of those things?
KAIU TAKAKANA: Then you've wasted my time. (beat) And I'll thank you for it.
(He stops at a window overlooking the Wall and hands her three small cylinders.)
KAIU TAKAKANA: Red flare, we attack. Green, we fall back.
KAIU TAKAKANA: (holding up the third) Blue. Nobody has fired a blue in my lifetime.
NATSUKO: What does blue mean?
KAIU TAKAKANA: Something none of us has seen before. (pressing it into her hand) Keep it.
[ITEM +Blue Flare (key item)] [SET blue_flare_held]
[SAVE]

## S02 — Court Is a Siege (hub)
MAP: `kyuden_hida_court` · TRIGGER: explore
NARRATION: Winter Court. The most dangerous battlefield in the Empire. Nobody bleeds. Everybody loses.
### Key NPC scenes (any order)
**Isawa Mutsuye** (garden, 2nd floor)
ISAWA MUTSUYE: (fumbling a fan) Oh! Are you — you're Hiruma! You're from his family!
NATSUKO: From his family's ruins, my lady. We're mostly ruins.
ISAWA MUTSUYE: (laughing despite herself) He says that too. Exactly that. (softly) Is he always so sad?
NATSUKO: (beat) He wasn't, this week.
**Asako Kuhime** (always near Mutsuye; lovely, attentive, eyes very blue)
ASAKO KUHIME: You're the scout Takakana sent. (smiling) Don't worry. She's exactly what she seems. I've known her for years.
NATSUKO: How many years?
ASAKO KUHIME: (lightly) Long enough to know everything about her.
**Isawa Akiko** (13, talkative)
ISAWA AKIKO: Are you a real Hiruma? From the Wall? Have you killed an oni? I almost drowned in a carp pond. Twice.
ISAWA AKIKO: Except the second time was on purpose. Don't ask about the exploding Togashi. Nobody's allowed to ask about the exploding Togashi.
NATSUKO: …I wasn't going to.
**Ide Keiyomi** (16, a Unicorn girl practising a gaijin dance alone)
IDE KEIYOMI: It's called the Tunnel of Quiescent Flame. My grandmother learned it in the Burning Sands.
IDE KEIYOMI: Everyone here thinks it's barbaric. (spinning) I think it's the only honest thing at court.
**Shosuro Shiko** (drunk, disgraced, venomous)
SHOSURO SHIKO: A Hiruma at court! How refreshing. You look at the exits like they owe you money.
NATSUKO: They do. Nobody here knows where they are.
SHOSURO SHIKO: (delighted) Oh, I like you. A free rumour: the Phoenix bride's friend never sleeps. I've watched.
**Yogo Shigeru & Kuni Taira** (basement stair; whispering over notes)
YOGO SHIGERU: The troll's regeneration is remarkable. We'd need another week.
KUNI TAIRA: (Tainted pallor, cheerful) Another troll, you mean. That one's nearly worn out.
**Yasuki Kurako** (the flustered hostess)
YASUKI KURAKO: (clutching her chest) The dance contest, the archery, the dinner — oh, my heart, my heart —
### Archery contest (fit conversion: one dialogue choice)
(The court gathers to shoot at painted targets — "dogs" in the old days, the hostess says, flustered; "now we use
straw goblins, much nicer.")
YASUKI KURAKO: Hiruma-san! You'll shoot, of course. All the Crab shoot.
> CHOICE "Archery"
  - "Shoot to win." → (wins; Glory +1; Kuhime claps a beat too late)
  - "Shoot to lose politely." → (Etiquette +; Mutsuye smiles at her: "You're kind.")
  - "Shoot the straw goblin's hat off." → (the court gasps; Kisada, on his balcony, almost smiles)
### Barracks — Sumai with the Wall Crabs
(HIDA SACHIKO and three Wall veterans, bored, wrestling for sake.)
HIDA SACHIKO: Hiruma! Court got you yet?
NATSUKO: Court's trying. It hasn't found anything to grip.
[PA Sumai Wall Veteran] → win:
WALL VETERAN: (on his back, laughing) Fine! You want a secret? The troll in the basement — its chains were filed.
WALL VETERAN: Not broken. *Filed*. Somebody's been visiting it with a rasp.
[SET wall_crab_trust]
### Guest side-story hooks offered here (`04-cast` B3)
Hiruma Goro (bodyguard), Ide Fujio (letter-writer), Daidoji Sakura, Kitsu Takeo, Yogo Mai, Isawa Michio.
[SAVE]

### Town NPCs — `kyuden_hida_court` (storyboard pass)
| NPC (floor) | Default line | Info (Discern / Eavesdrop) | Other path action |
|---|---|---|---|
| Isawa Mutsuye (2F) | "Is he always so sad?" | — | *Bless* (after S03): "Every evening Kuhime touches my sleeve." |
| Asako Kuhime (2F) | "She's exactly what she seems." | **Blank:** Discern → "Nothing. Absolutely nothing. That's what's wrong." Eavesdrop → "She stops talking whenever you get close. Every time." | — |
| Shosuro Shiko (3F) | "You look at the exits like they owe you money." | *Eavesdrop:* "Kuhime's room is always empty at night." | *Pilfer:* Fine Sake |
| Ide Keiyomi (2F) | "The only honest thing at court." | — | *Barter:* Unicorn Dance Ribbon (lore; give it to O-Shito after S03 → Honor +1) |
| Isawa Akiko (2F) | "Don't ask about the exploding Togashi." | — | *Charm:* follows ("Carp-Pond Splash", Water hit, 2 uses) |
| Yasuki Kurako (4F) | "Oh, my heart, my heart —" | — | *Barter:* Incense Stick ×3 at cost |
| Shinjo O-Shito (2F) | "Mother of six. I've seen worse than court." | — | *Duel* (Iaijutsu 3): Lacquered Do-maru |
| Kitchen servant (4F) | "Sake for the 6th floor, sake for the 6th floor…" | — | *Pilfer:* Herbal Salve ×2 |
| Yogo Shigeru (1F stair) | "Another week." | *Discern:* "He forges — love letters. Badly." | — |
| Kuni Taira (1F stair) | "That one's nearly worn out." | *Discern:* "Tainted, and delighted by the filed chains. Curious, not guilty." | — |
| Hiruma Kage (3F) | (studying maps) "Court is a map with no roads, Natsuko." | — | — |
**Rule (all chapters):** Nashiko in any disguise **blanks** Discern and Eavesdrop with a line like the ones above.

## S02b — The Dance (evening)
MAP: `kyuden_hida_court` 4F, great hall · TRIGGER: Mutsuye, Kuhime, Keiyomi and the archery scene all done
(The dance contest. Courtiers in pairs, careful as chess. Then Ide Keiyomi steps out alone and dances the Tunnel of
Quiescent Flame: fast, fierce, barefoot. The court titters behind its fans.)
NATSUKO: (internal) They're laughing at her. She knows. She doesn't stop.
(Across the hall, Asako Kuhime watches the girl's face the whole time, and never once blinks.)
(Fade. The barracks. Prompt: "Rest until morning.")

## S03 — The Girl Who Danced
MAP: `womens_shrine` (mountainside, dawn) · TRIGGER: the morning after the dance contest
(A scream from the women's shrine. Natsuko runs. Courtiers in a frozen ring around a veiled shape on the shrine
steps. Ide Keiyomi. Her face hidden under a cloth someone laid over it.)
SHINJO O-SHITO (Unicorn liaison, blunt, mother of six): Don't lift it. Don't anyone lift it. Her face — it's *gone*.
(Natsuko kneels. She doesn't lift the cloth.)
NATSUKO: (quietly, to the body) Tunnel of Quiescent Flame. You were the only honest thing here.
### Evidence (all appear within the scene; extra lines with party members)
- **Mutsuye has fresh Taint.** [IF haruki_in_party] HARUKI (Speak to the Soul): "It's laid *on* her, not grown in
  her. Like a stain thrown at a wall." [END]
- **Forged scrolls** in Yogo Shigeru's room point to him.
- [IF gendo_in_party] GENDO (Discern, the knife): "Held by a small hand. A woman's. A careful one." [END]
- **Only a scout notices:** ASAKO KUHIME, who "found" the body, has wet mud on her hem.
NATSUKO: (looking at the hem, then at the path) Shrine-path mud is red clay. That's grey. That's *Wall* mud.
NATSUKO: (internal) Why would a Phoenix lady walk the Wall path at dawn?
[SET wall_mud_clue]
(A runner: the Champion demands a culprit by nightfall.)
KAIU TAKAKANA: (grim) By nightfall, Hiruma. He won't wait. He never waits.

## S04 — The Accusation
MAP: `kyuden_hida_6f` (dusk) · TRIGGER: report to Kisada
(The audience hall. The court lines the walls. Kisada waits.)
KAIU TAKAKANA: The scout's findings, my lord.
> CHOICE "Accuse"
  - "Isawa Mutsuye." → [SET accusation mutsuye]
      SHIBA NOBORU (her humble yojimbo, stepping forward): Then I demand the right to defend my lady's name.
      [BATTLE b_duel_noboru] (non-lethal; win or lose, she is confined)
  - "Yogo Shigeru." → [SET accusation shigeru]
      (Shigeru is dragged out protesting. He is executed before morning.)
      NATSUKO: (internal, afterwards) He was a creep. He wasn't a killer. I just killed a creep.
  - [IF wall_mud_clue AND wall_crab_trust] "No one yet. One more night." → [SET accusation onenight] (recommended)
      NATSUKO: My lord. I don't have a culprit. I have mud.
      (A ripple through the court. Takakana goes very still.)
      NATSUKO: Give me one night, and I'll give you the hand that held the knife.
      HIDA KISADA: (the only words he speaks to her in the entire chapter) One night. Then I choose for you.

## S05 — The Donjon (dungeon)
MAP: `kyuden_hida_donjon_1–2`, `trap_catacombs` · TRIGGER: night (any route continues here)
(Following the grey mud: down past the sake barrels, a secret door, the donjon. The troll's cell door hangs open.
Its chains lie in pieces, the cuts clean and bright.)
[IF accusation mutsuye OR accusation shigeru] NATSUKO: (internal) The Champion has his culprit. The mud doesn't care. [END]
NATSUKO: Filed. Just like the Crab said.
[IF nezumi_friends] (A familiar squeak in the dark.) SQUEAK: Scout! Rat-ways go down-down! Squeak show! (opens the
rat-way shortcut through donjon_1) [END]
[BATTLE b_donjon_goblins] (escaped experiments)
### Trap catacombs (Natsuko knows them — interaction shortcut)
- "A roller trap. Natsuko steps on the third stone — the safe one."
- "A jade-dust trip line, *fresh*. Someone came this way who didn't want to touch it."
NATSUKO: (crouching at the jade dust) Every Crab walks through jade dust without thinking. Somebody stepped *over* it.
[SAVE]

## S06 — The Puppet and the Troll (BOSS)
MAP: `kyuden_hida_donjon_2` (deepest cell) · TRIGGER: enter
(A servant, dull-eyed, holding a strip of veil, rocking. Behind him the troll, unchained, wakes.)
MAHO PUPPET: (in a sweet woman's cadence that isn't his) Such a pretty dancer. Such a pretty face. I only borrowed it.
NATSUKO: Who's holding your strings?
MAHO PUPPET: (giggling) Someone *beautiful*.
[BATTLE b_boss_puppet_troll]
### GIMMICK — the troll is a hazard
"The **troll** isn't your target. Each turn it smashes whoever draws the most attention.
**Razor's Edge** can draw it to Natsuko. **Break the puppet** and the troll turns on *it*."
### Barks
- Troll targets an ally: NATSUKO: "Over here, you ugly heap of moss!"
- Puppet casts *No Pure Breaths*: (silence + damage) "Hush now. Hush."
- Puppet broken: (the troll turns, roaring, and swats the puppet) NATSUKO: "That's right. He's the one you want."
(Victory. The troll, sated and confused, lets Natsuko re-chain it. The puppet lies in the straw, himself again —
dying, and frightened.)
SERVANT (no longer a puppet): I don't remember… I don't remember anything…
> CHOICE "The servant"
  - "Spare him. Tell his family he was innocent." → [SET puppet_spared]
  - "End it quickly." → (he dies; nothing else changes)

## S07 — Testimony, Not Truth
MAP: `kyuden_hida_6f` (morning) · TRIGGER: after the boss
(The puppet's "confession" — magically extracted, word-perfect — is read to the court. Kisada accepts it with a nod.
The case is closed.)
(But Mutsuye stands at the edge of the hall in plain robes, the Taint dark at her collar. It can't be undone in
time. She bows to Kage, who can't look at her, and leaves the court.)
(The window above the Wall. Natsuko and Takakana.)
NATSUKO: The puppet didn't do it alone. Someone held its strings.
KAIU TAKAKANA: I know.
NATSUKO: Then why—
KAIU TAKAKANA: So does the Champion. A culprit is not the same as the truth, Hiruma.
KAIU TAKAKANA: The Wall only needs a culprit. (beat) You and I need the truth. Keep looking.
(Last shot: the court below. Asako Kuhime comforting a weeping Kage, her hand on his shoulder. She looks up at the
window, straight at Natsuko, and smiles. Her eyes are very blue in the lantern light.)
[CHAPTER COMPLETE]
### Chapter complete card
**"Winter Court at Kyuden Hida" — complete.**
Journal: *A dancer without a face, a bride with a stain thrown on her, and a puppet's word-perfect confession. The
Champion has his culprit. Natsuko has grey mud, and a friend of the bride's who never seems to sleep.*
[UNLOCK] Hida secondary school (Kyuden Hida dojo, Rank 2) · Crossroads: Crane Ch2 (with Rensei)

---
## Travel Banter unlocked by Crab Ch2
### TB-crab2-a "Fans and Forks" (Natsuko + Rensei)
RENSEI: You held your fan upside down for an entire dinner.
NATSUKO: It works the same either way.
RENSEI: It does *not*. Upside down, it means "I am in mourning for a very small pet."
NATSUKO: (pause) …Well. I was, a little. A goblin ate my favourite boot.
### TB-crab2-b "Blue" (Natsuko + Gendo)
GENDO: A blue flare. What does it signal?
NATSUKO: "Something none of us has seen before."
GENDO: How would anyone know when to use it?
NATSUKO: (turning it in her fingers) I think you know when you see it.
