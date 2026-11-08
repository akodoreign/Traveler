# PRODUCTION — Dragon Ch3 · "Past Mistakes"

**Traveler:** Kitsuki Gendo · **Lv** 30–35 · **Outline:** `scripts/dragon-ch3-past-mistakes.md`
**Flags read:** `ushimo_lead`, `history` · **Flags set:** `dinner` (bayushi / doji / shiba), `tsuhime_helped`,
`mirrors_recovered`
**Maps:** `otosan_uchi_400` (palace, streets, south gate), `bayushi_mansion`, `doji_mansion`, `shiba_mansion`,
`ushimo_house`, `miyoshi_studio`, `shiro_izumida_1–2`, `war_council`, `parley_ship`
**Battles:** `b_izumida_musketeers`, `b_boss_parley` (win when the vanguard captain falls; Akuro can't be beaten)
**Set-piece:** the History meter (anachronisms lower it; at 0, a bad-future cutscene, then retry)

---

## S01 — A Man With No Family
MAP: `otosan_uchi_400` (palace garden) · TRIGGER: start
NARRATION: Otosan Uchi, in the year 400. The Forbidden City is younger here, and somehow more dangerous.
(The boy-Emperor HANTEI KUSADA, fourteen, curious, polite, tugs Gendo's sleeve in the garden.)
HANTEI KUSADA: Can you see the future through them? The glass?
GENDO: (History: careful) Only very small print, Majesty.
HANTEI KUSADA: (giggling) You're the only person at court who makes jokes to me. Everyone else makes *requests*.
GENDO: (internal) He's fourteen, he suspects he's a puppet, and he's right. (aloud) Majesty, may I ask a request of my own?
HANTEI KUSADA: (delighted) Of course!
GENDO: When people tell you what you want, ask them what *they* want first.
HANTEI KUSADA: (pause) …That's a very strange request.
GENDO: It's a very strange court.
### History meter reminders (on screen while in the past)
"Don't say **Kitsuki · Unicorn · Emerald Magistrate · Kaiu Wall · Asahina**. Don't wear spectacles before nobles.
Don't draw a katana openly — **most samurai here carry straight tachi**."
- At each noble's door, prompt: *"Remove your spectacles?"* — Yes: Discern −10% inside. No: History −2.
**Storyboard:** `storyboards/dragon-ch3.md` (adds route `izumida_road`).

## S02 — Three Dinners, One Hour
MAP: `bayushi_mansion` / `doji_mansion` / `shiba_mansion` · TRIGGER: the invitations
GENDO: (holding up three lacquered cards) One hour. Three lords. If I go to one, I insult two.
GENDO: (polishing his spectacles, then hiding them) Every historian says these three ruled the Empire through a boy.
GENDO: Nobody says what they served at dinner.
> CHOICE "Which dinner?" [SET dinner]
### A — Bayushi Atsuki (corpulent, imperial, bribes rather than blackmails)
BAYUSHI ATSUKI: (enormous, beaming, surrounded by food) The no-family man! Eat! Eat!
BAYUSHI ATSUKI: I have a niece. Lovely girl. The Emperor is fourteen. A little… access, between young people.
GENDO: (internal) A Bayushi girl in the boy's bed changes who sits on the throne in twenty years. Changes the first Empress.
> CHOICE "Atsuki's request"
  - "Refuse — gently." → (History +5) GENDO: "My lord, I'm a man with no family. I have no way to introduce anyone."
  - "Agree." → (History −25; a portrait flickers) GENDO: (aside, sick) "…What have I done."
### B — Doji Tomeko (young, newly inherited, sheltered) & Doji Seikidera (her Champion)
DOJI TOMEKO: (barely nineteen) Sit, sit. Seikidera says you fought like a brush.
DOJI SEIKIDERA: (a beautiful, haunted man; his sword *Shukujo* chimes faintly when he touches it) I said two brushes, my lady.
DOJI TOMEKO: I want trade with the gaijin. Small trade. Silk for glass. Seikidera thinks it's dangerous.
DOJI SEIKIDERA: (quietly) I carried out the last purge. I know what happens when we let them in, and when we drive them out.
GENDO: (internal) He'll be dead within the month. History says so. (beat) History doesn't say how.
### C — Shiba Katsutoshi ("the boss you have always hated") & his page, Isawa Sanro
SHIBA KATSUTOSHI: (cold, logic-proof) You are not who you say you are.
GENDO: (very steady) Nobody at this court is, my lord.
SHIBA KATSUTOSHI: (a thin smile) …Good answer. Sanro! More tea for the no-family man.
(A bright boy of twelve with ink on his fingers: ISAWA SANRO, the future Isawa Asahina.)
ISAWA SANRO: (whispering, pouring) Do you think spirits could live inside *things*? Cups? Fans?
GENDO: (History: careful; a smile) …I think you should write that idea down, and never stop.
(History +5) [this nudges the founding of the Asahina]
[SAVE]

## S03 — Why Ushimo Struck
MAP: `ushimo_house` · TRIGGER: [IF ushimo_lead] or a guard's tip
(A small house. A woman in a sickbed, thin, grey, breathing badly: TSUHIME. Ushimo kneels beside her, unarmed.)
SEPPUN USHIMO: Her "doctor" gave me the sake. A kind old man. Gaijin medicine for her pain.
SEPPUN USHIMO: He said one sentence to me as he left. I've heard it ever since.
GENDO: (Deduce on the medicine jar) …Real gaijin medicine. Real comfort. Wrapped around one poisoned suggestion.
GENDO: (internal) Akuro. The Chameleon tattoo. He wore a doctor's face.
> CHOICE "Tsuhime"
  - "Help her." → [SET tsuhime_helped] (History +10; Ushimo becomes a Ch4 ally)
      [IF haruki_in_party] HARUKI: (Path to Inner Peace) "It won't cure her. But it'll let her sleep without the medicine." [END]
      [IF sayo_in_party] SAYO: (a Remedy) "Willow bark and honey. Old peasant trick. Nobody ever writes it down." [END]
      SEPPUN USHIMO: (weeping) …She's asleep. She hasn't slept in a month.
  - "Leave the past alone." → (no change; Ushimo is a broken man in Ch4)
### The portrait and the mirrors
(The Ink Door — the duplicate portal painting by the palace's south entrance — was painted by an elderly artisan,
KAKITA MIYOSHI, and paid for in glass mirrors.)
KAKITA MIYOSHI: (in her studio, delighted) Mirrors! Real silvered glass! A man in a bear mask paid me in mirrors.
GENDO: (internal; History −) Mirrors that won't exist here for two hundred years.
[PA Barter Miyoshi] **or** [PA Pilfer Miyoshi] (Low Skill) **or** pay full price (3,000 zeni) → the mirrors →
[SET mirrors_recovered] (History +10)
KAKITA MIYOSHI: (handing them over, sulking) Fine! But I'm keeping one. I like my face in it.
GENDO: (beat) …Keep it in a drawer, sensei. Please.

## S04 — Shiro Izumida (dungeon)
MAP: `shiro_izumida_1–2` · TRIGGER: rumours of a massacre at the winter palace
NARRATION: Shiro Izumida. A small winter palace ten miles south of the capital. Its groundskeepers are gone.
(Empty halls. Braziers overturned. Musket balls in the plaster.)
GENDO: (prising one out) Lead. Gaijin. (very quietly) They're already here.
[BATTLE b_izumida_musketeers]
### History note
"Muskets drop from fallen gaijin. **Using one** — History −15."
(The great hall. The floor is scorched in perfect lines — an exact map of the coast, with arrows. Spirits wail out of
the cracks.)
TORTURED SPIRITS: IT WROTE US! IT WROTE US! MAKE IT UN-BE! MAKE IT UN-BE!
GENDO: (kneeling at the scorched map) An invasion plan. Landing points. Dates. (beat) Burned into the floor by spirits that saw it written.
(From the ridge outside: a gaijin army, banners and pikes, marching north.)

## S05 — The Missing Champion
MAP: `war_council` · TRIGGER: report
(A war council. Bayushi Atsuki and Shiba Katsutoshi argue for closing the gates. Doji Tomeko tries to speak and is
drowned out.)
SHIBA KATSUTOSHI: We hold the city. Let the gaijin break on the walls.
DOJI TOMEKO: (standing, white-faced) Where is Seikidera? Has anyone seen my Champion?
(Silence. A messenger, breathless.)
MESSENGER: The Crane Champion rode to the Mantis shipyard at dawn, my lady. Alone. To talk peace — with the gaijin.
DOJI TOMEKO: (barely audible) …He went to stop it himself.
GENDO: (already moving) Then someone has to reach him first.
[SAVE]

## S06 — The Parley (BOSS)
MAP: `parley_ship` · TRIGGER: race to the shipyard
(A trading ship at anchor. Seikidera on deck with the Mantis trader GUSAI IAMI and gaijin envoys. A stableboy holds
the horses at the rail.)
(Gendo's boat bumps alongside. He climbs the rail just as the stableboy straightens, raises a gaijin pistol, and
shoots Seikidera in the back of the head.)
GENDO: NO—
(The "stableboy's" face ripples. TOGASHI AKURO, old and calm and unhurried, lowers the pistol.)
TOGASHI AKURO: Little clerk. You're late. History usually is.
(Gaijin and pirates swarm the deck.)
[BATTLE b_boss_parley]
### Rules / barks
- "**Akuro can't be beaten.** His tattoos (Crab: absorbs wounds; Wasp: extra actions) make him untouchable.
  **Defeat the vanguard captain** to win."
- Hitting Akuro: TOGASHI AKURO: "You can't hurt the past, little clerk. I've tried."
- Mid-fight, AKURO (on the rail, unhurried): "I saw how your world ends. The son becomes the dark brother. The jade
  clan goes black. The dead rule."
- TOGASHI AKURO: "I'm saving you from it. You should thank me."
- GENDO: "You're writing a history no one will ever read. (beat) I've filed a thousand of those."
- [IF any ally uses a gunpowder barrel] (History −10) GENDO: "Not the barrels! They don't *belong* here!"
- Vanguard captain falls → (the powder room explodes; when the smoke clears, Akuro is gone)

## S07 — Ending
MAP: `war_council` (night) · TRIGGER: return with Seikidera's body
(Seikidera lies in state. The merchant fleets will follow only the Crane Champion. Tomeko stares at nothing.)
DOJI TOMEKO: They'll follow only him. Only Seikidera.
(Gendo stands. Takes off his spectacles. Folds them. Puts them away.)
GENDO: Then they'll follow him, my lady.
GENDO: (quietly) I've studied every recorded habit of the Crane Champion. (beat) I filed them.
DOJI TOMEKO: (understanding, horrified, hopeful) …You'd wear his face.
GENDO: For one battle. Then I'll give it back. (beat) History can have it.
[CHAPTER COMPLETE]
### Chapter complete card
**"Past Mistakes" — complete.**
Journal: *Three dinners, a sick woman's sleep, mirrors bought back from a painter, and a map of an invasion burned
into a floor. Gendo was one breath too late for the Crane Champion. Now he must become him.*
[UNLOCK] *My Brother's Soul* kata at the Lv 41 pick (Mirumoto 2)

---
## Travel Banter (past)
### TB-dragon3-a "Glass" (Gendo + any ally, in the past)
ALLY: You took your spectacles off.
GENDO: I'll need to see the battle. (beat) I'll have to remember it instead.
ALLY: Can you?
GENDO: I was an archive clerk for nine years. (tapping his temple) I can remember anything. That's the trouble.
### TB-dragon3-b "Sanro" (Gendo, solo, at the palace window)
GENDO: (to himself) A boy with ink on his fingers who wonders if cups have souls.
GENDO: Before he's old, they'll name a whole family after him. (smiling) I told him to write it down. That's allowed. Probably.
