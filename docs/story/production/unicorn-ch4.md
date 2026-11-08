# PRODUCTION — Unicorn Ch4 · "Regret"

**Traveler:** Ide Tamotsu · **Lv** 41–45 · **Outline:** `scripts/unicorn-ch4-regret.md`
**Flags read:** `naohida_named`, `nihime_told`, `shahai_trusts`, `daiyu_state`, `karasu_joined`, `mirumoto_terms` ·
**Flags set:** `truce_bought`, `shahai_kept_close`, `settlement` (heir / treaty)
**Maps:** `siege_camp`, `wind_tunnel_1–2`, `shiro_iuchi_stairs`, `storm_room`, `valley_road_home`
**Battles:** `b_tunnel_legion`, `b_boss_kurosho_regret` (the Wail gimmick)
**Guest:** Naohida (S01) · **Storyboard:** `storyboards/unicorn-ch4.md` (siege-camp hub; gale tiles in the tunnel)

---

## S01 — Three Thousand Deaf Dragons
MAP: `siege_camp` · TRIGGER: start
NARRATION: Shiro Iuchi. A triangular castle built into a wind tunnel. Today the wind is screaming, and so is something inside.
(The Mirumoto army, wax in its ears, surrounds the castle. Iuchi survivors with them. A young man walks into camp
under a white flag, a gaijin blade on his back: NAOHIDA.)
[IF naohida_named]
IUCHI SOLDIER: The bomber! Arrest him!
TAMOTSU: (stepping in front of him) One day, Hiroichi-sama. Give me one day's truce. (opening his purse) I'll pay for it.
[PA Barter Hiroichi] → [SET truce_bought]
IUCHI HIROICHI: (taking nothing) …Keep your money, Ide. One day.
[ELSE]
NAOHIDA: (to Tamotsu, quietly) You didn't name me. At the tribunal.
TAMOTSU: You still owe me a copper.
NAOHIDA: (almost laughing) …I'll pay you in pebbles.
[END]
NAOHIDA: He's my father. Kurosho. (beat) I made gunpowder to hurt him.
NAOHIDA: I'll walk in there to save him. I don't understand myself either.
TAMOTSU: Good. Understanding yourself is overrated. (handing him a jade knife) Bring this.
[GUEST +Naohida] (skill "Powder Charge": Fire AoE, 1 use)
[IF nihime_told] (Soshi Nihime arrives at the camp on a borrowed horse, veiled, determined.) SOSHI NIHIME: "I'm coming in. He'll listen to me, once. For one breath." [END]
[SAVE]

## S02 — The Wind Tunnel
MAP: `wind_tunnel_1–2` · TRIGGER: approach, ears covered
[IF mirumoto_terms honour] MIRUMOTO TSUKARU: (at the tunnel mouth, pulling one plug) We came for the children. We hold
the door. (b_tunnel_legion: enemies start at −1 Resolve) [END]
### Covered Ears (on)
(Karasu is a story companion here — NOTE lines, no battle slot. Naohida is the guest.)
NOTE (Tamotsu): WIND TOO LOUD TO HEAR ANYWAY. SMALL MERCIES.
NOTE (Karasu): I CAN HEAR IT. IT'S SINGING MY NAME. BADLY.
(Pigeons in the cliffs, carrying whispers. Possessed Emerald Legion soldiers march in a circle, chanting.)
[BATTLE b_tunnel_legion]
### Battle note
"With ears covered you **can't use voice skills** (Command shouts, Charm-type, Settle the Account). Uncover to use
them — but the Wail can reach you."

## S03 — The Stairs
MAP: `shiro_iuchi_stairs` · TRIGGER: inside the castle
(The great stair. Possessed servants kneel frozen on every step, humming. The party edges around them through the
servants' passages.)
NOTE (Karasu): DON'T STEP ON THEM. THEY'LL REMEMBER IT WHEN THEY WAKE.
NOTE (Tamotsu): THEY'LL WAKE?
NOTE (Karasu): IF WE WIN. (beat) I'M ALWAYS OPTIMISTIC IN WRITING.
(Iuchi Shahai, with them since the tower, hums the same tune as the servants, faintly, without noticing.)
> CHOICE "Shahai"
  - "Send her back with Daiyu." → (safe; the mark worsens offscreen)
      NOTE (Tamotsu, to Shahai): GO WITH YOUR FATHER. I'LL BRING YOU A RICE CAKE AFTER.
      NOTE (Shahai): PROMISE
      NOTE (Tamotsu): PROMISE.
  - [IF shahai_trusts] "Keep her close." → [SET shahai_kept_close] (her voice can be used against the demon — risky)
      NOTE (Karasu): THE DEMON MARKED HER. SHE SINGS ITS SONG. (beat) WE CAN SING IT *BACKWARDS*.
      NOTE (Tamotsu): …THAT'S EITHER GENIUS OR TERRIBLE.
      NOTE (Karasu): WHY NOT BOTH.
[SAVE] (before the storm room)

## S04 — Kurosho and Regret (BOSS)
MAP: `storm_room` · TRIGGER: enter
(The top of the castle. A room where the wind never stops. In its centre, IUCHI KUROSHO — eighty, a monk's robe, the
kanji for Void burned into his skull. Behind him, filling the wind: the SHUTEN DOJI OF REGRET, a shape made of every
apology no one ever made.)
(Ears covered — the party speaks in notes; then Tamotsu pulls out one plug. He needs his voice.)
TAMOTSU: (aloud, into the wind) Kurosho-sama!
IUCHI KUROSHO: (turning, eyes empty) …The Ide boy. Come to haggle?
TAMOTSU: Come to buy you back, my lord.
[BATTLE b_boss_kurosho_regret]
### GIMMICK — the Wail
"Every 3 turns, Regret **wails**. Any traveler **without Covered Ears** must resist or be **possessed** for 2 turns.
Covered Ears blocks it, but also blocks **voice skills**. Choose who listens."
### Mechanics / barks
- Wail: THE SHUTEN DOJI: "SAY IT AGAIN. SAY YOU'RE SORRY. AGAIN. AGAIN."
- Possessed ally: (attacking a friend, weeping) "I'm sorry — I'm sorry — I'm sorry —"
- **Nihime's curse** (once, at half HP): [IF nihime_told] SOSHI NIHIME (in the doorway, unveiled): "Kurosho. Look at me." [ELSE] (a letter, read aloud by Naohida: "Look at me, Kurosho.") [END]
  → Kurosho's Resolve drops to 0 for one breath (a free Suki)
  - IUCHI KUROSHO (awake, for one breath): "Nihime? (beat) I'm sorry. I'm so sorry. I should have —"
  - THE SHUTEN DOJI (through him): "Yes. Say it again. *Again.*"
- [IF shahai_kept_close] Karasu's tuning fork + Shahai's reversed song → the Doji is stunned for a turn
  - IUCHI SHAHAI: (singing it backwards, small and brave) "…dlrow eht fo dne eht ta…"
  - THE SHUTEN DOJI: (shrieking) "STOP THAT!"
- **Tamotsu's signature line** (Barter Coin: Settle the Account, aimed at the Doji):
  TAMOTSU: (throwing a fistful of gold into the storm) He's paid enough! Here — take mine instead —
  TAMOTSU: — and *get out*.
- Regret banished → (the wind stops, all at once; the silence is enormous)

## S05 — Brokered
MAP: `storm_room` → `valley_road_home` · TRIGGER: after the boss
(The servants on the stairs wake, dazed, freed. Kurosho lies in the centre of the still room.)
[IF nihime_told]
(Nihime kneels and takes his head in her lap.)
IUCHI KUROSHO: (fading, himself again) …Twenty years. I should have come for you.
SOSHI NIHIME: (dry-eyed) Yes. You should have. (beat) Hush now. Your son is here.
IUCHI KUROSHO: (finding Naohida's face) …Mine?
NAOHIDA: (kneeling, shaking) …Yours.
(Kurosho dies, at peace.)
[ELSE]
(Kurosho dies alone in the still room, murmuring a name nobody there knows.)
NAOHIDA: (standing over him, very quiet) …I wanted to hate you properly. You didn't even let me do that.
[END]
[IF daiyu_state comforted] IUCHI DAIYU: (stepping forward, a woodchuck at his heel) I'll speak for the boy. I've listened long enough. [END]
[IF daiyu_state shattered] IUCHI DAIYU: (very straight) My father did this. The Iuchi will say so, in court. (Honor +1) [END]
> CHOICE "Tamotsu's settlement"
  - "Acknowledge Naohida as heir of both houses." → [SET settlement heir] (recommended; Compassion)
      TAMOTSU: (to Daiyu and the Soshi envoys) He's Iuchi by his father. Soshi by his mother. Peasant by upbringing.
      TAMOTSU: If you want a bridge between your houses, my lords — here he is. Already built.
      NAOHIDA: (horrified) Tamotsu—
      TAMOTSU: (aside) You always asked why the lord eats first. Now you'll find out. It's mostly indigestion.
  - "A plain treaty." → (safer; Naohida stays nameless)
(The valley road. Tamotsu walks a refugee caravan home through the Ojatara valleys, leading Persimmon, who bites every
person who tries to help carry anything.)
IUCHI DAIYU: (at the roadside, to a woodchuck) He fixed it. The fat merchant fixed it.
IUCHI KARASU: (deadpan) Emissary.
IUCHI DAIYU: The fat *emissary* fixed it.
TAMOTSU: (calling back, cheerfully) *Round*, my lord!
[IF mirumoto_terms jade] MIRUMOTO TABEZU: (riding past, cheerfully) The jade, Ide. (the **Jade Toll**: Jade-variant
prices +25% in the valley shops from now on) [END]
[IF shahai_kept_close OR shahai_trusts] (A small hand tugs Tamotsu's sleeve. Shahai, holding out her palm.) IUCHI SHAHAI: "You promised a rice cake." TAMOTSU: (producing one from his sleeve with a flourish) "I always keep rice-cake promises." [END]
[CHAPTER COMPLETE]
### Chapter complete card
**"Regret" — complete.**
Journal: *In a castle where the wind never stopped, Tamotsu paid a demon to leave, and it went. An old man died
saying sorry at last. A nameless peasant became the bridge between two broken houses — whether he likes it or not.*
[UNLOCK] Naohida (finale callback) · Karasu's tuning fork · *The Immovable Hand of Peace* foreshadowed (R5)

---
## Travel Banter unlocked by Unicorn Ch4
### TB-unicorn4-a "Paid" (Tamotsu + Mitsue)
MITSUE: You tried to *pay* a Shuten Doji to leave.
TAMOTSU: Everything has a price.
MITSUE: And it worked?
TAMOTSU: (pause) …I think it was so offended that it lost its concentration. That's a kind of price.
MITSUE: (laughing) That's the most Unicorn thing I've ever heard.
### TB-unicorn4-b "Indigestion" (Tamotsu + Naohida, guest)
NAOHIDA: You made me an heir. I didn't ask to be an heir.
TAMOTSU: Nobody asks. That's how you know it's real.
NAOHIDA: (sighing) …Do I really have to eat first at every meal now?
TAMOTSU: (grinning) Every single one. And smile while you do it.
