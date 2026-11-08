# SIDE STORIES — Guests 1–6

Source: `story/04-supporting-cast-and-hireables.md` B3. Pregen-derived guests use their new names (B4).
Each guest has **SS1 (recruit)** and **SS2 (secret)**. SS2 upgrades one guest skill (+1 use or a stronger effect).
Format: production style (`production/README.md`).

---

## 1. Akodo Rin — Lion / Akodo + Seppun guard
**Skills:** *Cover* (protect ally, 2) · *The Clouds Part* (first-turn speed buff, 1)
**Banter with:** Shizue, Rensei

### SS1 — "The Escort" (recruit) · offered: Unicorn Ch1 (after the bombing) · Lv 8+
MAP: `buried_leaves_inn` → `pass_road`
(Akodo Rin, armour scorched from the inn fire, packing her gear with mechanical precision.)
AKODO RIN: I was supposed to guard the tribunal. Half of it nearly burned.
AKODO RIN: My grandmaster would say I failed. (beat) He'd be right.
TRAVELER: (any) Then come and guard us instead. We'll burn less.
AKODO RIN: (a short laugh) …Prove it. There's a judge's courier on the pass road. Bandits.
[BATTLE b_ss_rin_bandits] (courier escort; protect the courier NPC)
AKODO RIN: (after) You didn't let him get hit once.
AKODO RIN: (bowing) Akodo Rin. Lion. My sword's yours until the tribunal ends — or longer, if you're interesting.
[GUEST +Akodo Rin]

### SS2 — "The Son Her Father Wanted" (secret) · unlocks: after Unicorn Ch2 · Lv 25+
MAP: `seppun_shrine_capital_road`
(A road shrine with Seppun mon. An old man in faded Imperial guard robes sweeps it: SEPPUN TAKEMORI, Rin's
grandmaster.)
SEPPUN TAKEMORI: Rin-*kun*. Still wearing your brother's armour.
AKODO RIN: (stiffly) It fits, sensei.
(Later, by the shrine fire.)
AKODO RIN: My father wanted a son. My brother died at four. So I became the son. Rin-kun.
AKODO RIN: Sword lessons, armour, a boy's name in the dojo. My grandmother, who was Seppun, made sure of it.
AKODO RIN: (beat) There was someone, once. A girl at the Seppun school. She knew. She didn't mind.
AKODO RIN: My father married her off to a Matsu so it would stop.
TRAVELER: Does your grandmaster know who you are?
AKODO RIN: He's always known. (looking at the old man) He's the only one who never called me "kun" by accident.
### The task
SEPPUN TAKEMORI: A man came asking about you, Rin. About your *blood*. Since that business at Shiro Iuchi.
[BATTLE b_ss_rin_hunters] (two blood-hunters who missed their chance in Unicorn Ch2)
### Payoff
SEPPUN TAKEMORI: (after) You fight as yourself now. Not as your brother.
AKODO RIN: (a long breath) …What's the difference?
SEPPUN TAKEMORI: You stopped *waiting for permission*.
AKODO RIN: (to the traveler, quietly) My name is Rin. Just Rin. (beat) I'd like you to use it.
[UPGRADE *Cover* → *Rin's Guard* (protect ally + counter, 3 uses)]

---

## 2. Bayushi Hideki — Scorpion / Bayushi bushi
**Skills:** *Pincers and Tail* (lower enemy evasion, 2) · *Strike at the Tail* (disarm, 1)
**Banter with:** Mitsue, Tamotsu

### SS1 — "The Duel Nobody Asked For" (recruit) · offered: Unicorn/Scorpion crossroads (Ch2/Ch3) · Lv 22+
MAP: `tribunal_hall` → `lake_ice`
(A Scorpion bushi, sharp and bored, has challenged a Unicorn envoy to a duel on the frozen lake. Nobody knows why.)
BAYUSHI HIDEKI: He insulted my mother.
UNICORN ENVOY: I said she *was* a Unicorn!
BAYUSHI HIDEKI: (pause) …Yes. That's the insult.
> path action
  - **Charm / Etiquette:** talk them both down → HIDEKI: "Fine. Fine. You win. I'm bored anyway."
  - **Duel** (stand in for the envoy) → [BATTLE b_ss_hideki_duel]
BAYUSHI HIDEKI: (after) You're more interesting than this tribunal. I'll follow you. For the entertainment.
[GUEST +Bayushi Hideki]

### SS2 — "Half a Family" (secret, joint with Iuchi Saran) · unlocks: after Unicorn Ch3 · Lv 32+
MAP: `shinjo_estate_ruins`
(A ruined Shinjo estate in the valleys. Hideki stands at a grave. Saran is with him — if recruited.)
BAYUSHI HIDEKI: My father was a Bayushi magistrate. My mother was Unicorn.
BAYUSHI HIDEKI: When my father died, she married a Shinjo. He raised me.
BAYUSHI HIDEKI: (very flat) And then I found out he's the one who killed my father. In this war. Twenty years ago.
[IF saran recruited]
IUCHI SARAN: (quietly) He's my father too. Your stepfather.
BAYUSHI HIDEKI: (not looking at her) I know, little sister. I've known for a year. That's why I'm so *pleasant*.
[END]
### The task
(The stepfather, OLD SHINJO HAKUBA, lives in the ruins, half-blind. Hideki came to kill him.)
> CHOICE (the guest's choice, guided by the traveler)
  - "Ask him why." → SHINJO HAKUBA: "Because your father was about to kill *me*. And then I married his widow and raised his son, and I loved you both. I never asked you to forgive me."
  - "Leave it." → (Hideki stands at the grave and doesn't draw)
BAYUSHI HIDEKI: (after a very long silence; putting his sword away) …The Scorpion would kill him.
BAYUSHI HIDEKI: (to Saran, or to the traveler) I'm finding I'm a terrible Scorpion.
[UPGRADE *Strike at the Tail* → disarm + Silence, 2 uses]

---

## 3. Iuchi Saran — Unicorn / Iuchi shugenja
**Skills:** *Path to Inner Peace* (heal, 3) · *Rolling River* (water AoE, 1)
**Banter with:** Tamotsu, Haruki

### SS1 — "The Child of the War" (recruit) · offered: Unicorn Ch2 · Lv 22+
MAP: `refugee_camps` (night)
(A young Iuchi shugenja treating refugees by lamplight, exhausted, out of herbs: IUCHI SARAN.)
IUCHI SARAN: I'm the only shugenja who'll come to the camps. The others say it's beneath them.
IUCHI SARAN: (beat) I was born in a camp like this. During the *last* war.
### The task — gather ginseng and rhubarb at the camp edge (Hunting prompt, or Sayo's Remedy)
[BATTLE b_ss_saran_scavengers] (scavengers raiding the medicine tent)
IUCHI SARAN: (after) You stayed. People don't usually stay.
[GUEST +Iuchi Saran]

### SS2 — "The Truth of My Birth" (secret; joint with Hideki) · see Hideki SS2 · Lv 32+
(If Hideki isn't recruited, Saran finds Old Shinjo Hakuba alone.)
IUCHI SARAN: My mother never told me who my father was. Only that he was "a good man in a bad war".
SHINJO HAKUBA: (half-blind) …Saran? You have your mother's voice.
SHINJO HAKUBA: I'm your father, girl. And I killed your brother's father. (beat) You have a brother. A Scorpion. He hates me.
IUCHI SARAN: (sitting down hard in the ruins) …I have a *brother*?
[IF hideki recruited] (Hideki in the doorway, arms folded.) BAYUSHI HIDEKI: "Hello, little sister. Surprise." [END]
[UPGRADE *Rolling River* → 2 uses + cleanses the party]

---

## 4. Doji Chiyo — Crane / Doji courtier
**Skills:** *Test of Honor* (cancel an enemy action, 1) · *Whisper from the Soul* (debuff, 2)
**Banter with:** Rensei, Mitsue

### SS1 — "The Swing Vote" (recruit) · offered: Unicorn Ch1 (the tribunal) · Lv 6+
MAP: `buried_leaves_inn`
(The neutral swing judge's clerk: a plain-faced Crane woman in severe grey, devastatingly clever: DOJI CHIYO.)
DOJI CHIYO: Everyone tries to bribe my judge with beauty. Poems. Lovely fans. (with contempt) *Painted boys.*
DOJI CHIYO: Nobody's tried bribing him with the truth. It's very refreshing when you do.
### The task — bring Chiyo three pieces of evidence from the Ch1 case board (any 3 → done)
DOJI CHIYO: (reading them) …Thorough. Ugly. True. My three favourite things.
DOJI CHIYO: I'll come with you. My judge sleeps through the afternoons anyway.
[GUEST +Doji Chiyo]

### SS2 — "The Ugly Crane" (secret: Nashiko's foil) · unlocks: after Crane Ch4 · Lv 42+
MAP: `kyuden_doji_garden`
(The Kyuden Doji gardens. Court ladies gossip behind fans about Chiyo — the "ugly Crane".)
DOJI CHIYO: (sitting by a pond, unbothered) The Crane worship beauty. Did you know there's a Doji ancestor nobody talks about?
DOJI CHIYO: She was so beautiful she thought it made her *owed* things. A throne. A husband. The world.
DOJI CHIYO: (looking at her own plain reflection) I've always been grateful I wasn't pretty. Nobody ever told me I was owed anything.
[IF rensei in party] RENSEI: (very quietly) …You're talking about Nashiko. CHIYO: (a sharp look) "So you've read the play too." [END]
### The task — a beauty contest Chiyo has been entered in, as a court joke
> CHOICE
  - "Help her win with wit." (a debate-UI mini round) → CHIYO wins by making the judges laugh at themselves
  - "Help her refuse to compete." → CHIYO: "I'll judge it instead. Harshly."
DOJI CHIYO: (after) If you meet that ancestor of mine, tell her something from me.
DOJI CHIYO: Tell her that plain women don't need to be *owed*. We just take what's ours.
[UPGRADE *Test of Honor* → 2 uses; in the finale it can cancel one of Nashiko's "Empress" actions]

---

## 5. Mirumoto Daigo — Dragon / Agasha shugenja (prankster scientist)
**Skills:** *Firecracker* (fire, random targets, 2) · *Katana of Fire* (buff, 1)
**Banter with:** Gendo, Haruki

### SS1 — "Things That Go Bang" (recruit) · offered: Unicorn Ch2 (the Dragon peacekeepers) · Lv 22+
MAP: `mirumoto_camp`
(An explosion. A young Dragon shugenja with singed eyebrows climbs out of a smoking tent, delighted: MIRUMOTO DAIGO.)
MIRUMOTO DAIGO: It worked! It worked! (pause) …Mostly.
MIRUMOTO DAIGO: Agasha alchemy. Perfectly legal. *Fireworks*. Not gunpowder. Very different. (beat) Slightly different.
### The task — gather 3 alchemical reagents (sulphur from a hot spring, bat guano from a cave, a lightning-struck stick)
[BATTLE b_ss_daigo_bats] (the cave)
MIRUMOTO DAIGO: (after) You found a lightning stick! Nobody ever finds the lightning stick!
MIRUMOTO DAIGO: I'm coming with you. Things explode near you. I can tell.
[GUEST +Mirumoto Daigo]

### SS2 — "Best Friends, Worst Rivals" (secret; with Shiba Toshiro) · unlocks: after Phoenix Ch3 · Lv 32+
(See Toshiro SS2. The joint story; Daigo's side.)
MIRUMOTO DAIGO: Toshiro and I were students together. We swore we'd be legends.
MIRUMOTO DAIGO: Then I set his family dojo on fire. By accident. Mostly.
MIRUMOTO DAIGO: (quietly, for once) His hands. That was me. My firework. He's never once said so.
[UPGRADE *Firecracker* → hits all enemies, 2 uses]

---

## 6. Shiba Toshiro — Phoenix / Shiba bushi
**Skills:** *Spear Wall* (2) · *One With Nothing* (give an ally an extra action, 1)
**Banter with:** Haruki, Natsuko

### SS1 — "Wherever Daigo Is" (recruit) · offered: with Daigo (Unicorn Ch2) · Lv 22+
(A tall Shiba with gloved hands standing guard outside Daigo's smoking tent, resigned.)
SHIBA TOSHIRO: I follow him around so the explosions are at least *supervised*.
SHIBA TOSHIRO: If he's joining you, so am I. (beat) Please keep him away from lanterns.
[GUEST +Shiba Toshiro]

### SS2 — "The Burned Hands" (secret; joint with Daigo) · unlocks: after Phoenix Ch3 · Lv 32+
MAP: `shiba_dojo_ruins`
(The ruins of a small Shiba dojo, burned years ago. Toshiro takes off his gloves for the first time. His hands are scarred.)
SHIBA TOSHIRO: My family blade was taken from me after the fire. "A man who lets his dojo burn doesn't deserve the sword."
SHIBA TOSHIRO: I've never said whose firework it was. (beat) I never will.
SHIBA TOSHIRO: (glancing at a narrow tunnel into the ruins; going pale) …The blade's in there. In the old vault. It's very small in there.
TRAVELER: You're afraid of small spaces.
SHIBA TOSHIRO: (a thin smile) Since the fire. Yes.
### The task — enter the collapsed vault (a short dungeon); Toshiro must go too
[BATTLE b_ss_toshiro_vault_kami] (a guardian kami of the burned vault)
[IF daigo recruited]
MIRUMOTO DAIGO: (in the tunnel, holding a little firework like a lantern) It was me. Toshiro. The fire. I've never said it.
SHIBA TOSHIRO: (in the dark) I know, idiot. I've always known.
MIRUMOTO DAIGO: …Why didn't you ever say?
SHIBA TOSHIRO: Because you'd have stopped making things go bang. (beat) And the world needs things that go bang.
[END]
(The family blade, in the ash. Toshiro takes it in his scarred hands.)
SHIBA TOSHIRO: …It doesn't care what my hands look like.
[UPGRADE *Spear Wall* → 3 uses + Toshiro's family blade (Yari)]
