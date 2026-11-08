# PRODUCTION — Ronin Ch3 · "The Village of the Wounded Lion"

**Traveler:** Sayo · **Lv** 30–35 · **Outline:** `scripts/ronin-ch3-the-village-of-the-wounded-lion.md`
**Flags read:** `order_promise` · **Flags set:** `climbers_told`, `mosuke_knows`, `hikaru_spoke`
**Maps:** `wounded_lion_village`, `cedar_slopes`, `ice_ledges`, `cloud_bridge`, `white_snow_fortress_1–2`,
`basin_hall`
**Battles:** `b_snow_beasts`, `b_frost_spirits`, `b_boss_ghost_guard_basin`
**Guest:** Mirumoto Hikaru (for the boss only)
**Re-scaled secret:** the legendary "rescued prince" was a peasant's newborn, so the Hantei line for 300 years
descends from a peasant.
**Storyboard:** `storyboards/ronin-ch3.md` (adds route `wounded_lion_road` with a Lion checkpoint).
**Also reads:** `writ_pilfered` (the checkpoint).

## S00 — The Checkpoint (route)
MAP: `wounded_lion_road` · TRIGGER: approach
LION SERGEANT: Papers. Wave-folk go round by the goat track.
[IF writ_pilfered]
SAYO: (holding up a travel writ with a very grand seal) Lord Ikoma Sadanobu's business.
LION SERGEANT: (reading; paling) …Lord Sadanobu's? (stepping aside) Pass. Pass!
SAYO: (walking on; aside) He wanted my face on every post. He never said anything about his *writ*.
[ELSE]
[BATTLE b_lion_checkpoint] (Border Patrol ×3 — Barter Coin can bribe them)
[END]

---

## S01 — The Re-enactment
MAP: `wounded_lion_village` · TRIGGER: start
NARRATION: The Village of the Wounded Lion, at the foot of the Mountain of the White Snow. Every fifty years, the
grandchildren of heroes come here to climb it.
(Five young samurai in brilliant clan colours: the descendants of the five legendary champions. Matsu, Hida, Bayushi,
Doji, Mirumoto. Their leader, sharp and proud: MATSU HANAE.)
MATSU HANAE: You. Ronin. You'll carry the ropes.
SAYO: Of course, my lady.
SAYO: (to herself) And I'll be the only one who knows how to tie them.
HIDA CLIMBER (Hida Ren): Our grandfathers' grandfathers climbed this mountain to save a stolen prince from an oni.
DOJI CLIMBER (Doji Aoi): Five champions. Four died gloriously. Bayushi carried the baby down and died telling the tale.
BAYUSHI CLIMBER (Bayushi Kei): (smirking) The Bayushi always get the best lines.
MIRUMOTO CLIMBER (Mirumoto Sen): The Mirumoto ancestor died first. Bravely. It's in every history.
### The snow mounds
(At the village gate: a row of low snow-covered mounds. Villagers leave rice cakes on them and won't say why.)
SAYO: (to an old man leaving an offering) What are these, grandfather?
OLD MOSUKE: (not looking up) My family's. Always have been.
OLD MOSUKE: My grandfather's grandfather said the real prince never came down the mountain.
OLD MOSUKE: (laughing, uneasy) He was a silly old man. Everybody said so.
[SAVE]

## S02 — The Climb (3 stages)
MAP: `cedar_slopes` → `ice_ledges` → `cloud_bridge` · TRIGGER: begin the ascent
### Field — rope points (Athletics/Hunting interaction prompts; Sayo's specialty)
"Tie off here?" — Sayo's knot holds; the samurai's slip (comic lines).
MATSU HANAE: (dangling) Ronin! *Ronin!*
SAYO: (pulling her up one-handed) Sayo. My name's Sayo, my lady. It's quicker to shout.
### Stage 1 — the cedar slopes
(A grave under the cedars: a Crane's grave. A Lion arrow still in the headstone.)
DOJI AOI: (staring) …A Crane grave. With a *Lion* arrow in it.
MATSU HANAE: (sharply) Bandits. Obviously.
[BATTLE b_snow_beasts]
### Stage 2 — the ice ledges
(A great gate in the cliff, its timbers scorched black in a starburst.)
SAYO: (touching the scorch) This isn't fire. It's gunpowder. Somebody blew this gate open.
BAYUSHI KEI: (quietly) …The Bayushi champion was said to be clever with fire.
[BATTLE b_frost_spirits]
### Stage 3 — the cloud bridge
(A suit of ancient Mirumoto armour, half-buried in ice. It's facing *away* from the castle — down the mountain.)
MIRUMOTO SEN: (very pale) …That's facing the wrong way. Our ancestor died charging the castle.
SAYO: (gently) Armour doesn't lie, my lord. People do.
### Mirumoto Hikaru (appears at each stage, then walks ahead)
(A tall, silent man with a Crane tattoo winding over his face and neck, ageless, barefoot in the snow. He looks at
Sayo, then walks on up the mountain without a word.)
SAYO: Who *is* that?
MATSU HANAE: A hermit. They say he's been on this mountain forever. He never speaks.
[SAVE] (the castle gate)

## S03 — The Truth in the Snow (the fortress)
MAP: `white_snow_fortress_1–2` · TRIGGER: enter
NARRATION: The Castle of the White Snow. A winter palace. Three hundred years of frost, and a night that never ended.
(The rebel ghost-guard walks the halls, replaying the night over and over like a play with no audience.)
### Ghost-replay interactions (5 — Discern-style prompts; each reveals one truth)
1. **The kidnapping:** GHOST GUARD: "The Crab lord says take the prince. He'll marry the other heir. Consort to an empty cradle."
   → "There was no oni. A Crab lord had rebel guards kidnap the prince."
2. **The fight:** GHOST (a Lion, a Crane, struggling): "You shot him!" "He was a guard!" "He was *Crane*!"
   → "The champions fought each other. The Lion killed the Crane."
3. **The gate:** GHOST (a Scorpion, with a smoking fuse): "Stand back. This will be loud."
   → "The Bayushi champion blew the gate with gunpowder."
4. **The flight:** GHOST (a Mirumoto, trembling at a baby's cry): "Togashi said — when you hear the cry — run. *Run.*"
   → "The Mirumoto champion fled on Togashi's prophetic order."
5. **The basin:** (a stone basin set with red stones. Empty. Very still.) The ghost-guard turns away from it and won't look.
   → "The child died here." (implied only)
(Matsu Hanae stands in the basin hall, white-faced. The others behind her, silent.)
MATSU HANAE: …The legend is a lie. All of it. Our families' glory is built on —
SAYO: (quietly) — a dead baby and a lot of brave men who did terrible things. (beat) Yes.
(The ghost-guard turns toward them. All of them. At once.)
[SAVE] (the basin-hall door)

## S04 — The Ghost-Guard and the Basin (BOSS)
MAP: `basin_hall` · TRIGGER: after S03
(The ghosts draw ghost-swords. Behind them, the stone basin glows red. Mirumoto Hikaru steps out of the snow and
stands beside Sayo, drawing two swords.)
[GUEST +Mirumoto Hikaru (battle only)] (skill: *Endless Strike* — up to 3 extra hits)
[BATTLE b_boss_ghost_guard_basin]
### GIMMICK — the basin raises the dead
"Every 2 turns, a fallen ghost-guard **rises again**. **Break the bloodstone basin** (it's a target) to end it."
### Barks
- A guard rises: GHOST GUARD: "The prince — the prince must not come down —"
- Hikaru's Endless Strike: (no words; the swords move like a hurricane)
- Basin cracked: (the red stones go grey one by one)
- Basin broken: (the ghost-guards lower their swords and fade, one by one, bowing to the empty basin)
SAYO: (catching her breath) …Thank you, hermit.

## S05 — The Child in Its Bed of Stone
MAP: `basin_hall` · TRIGGER: after the boss
(Hikaru kneels by the empty basin. For the first time in three hundred years, he speaks — a voice like a door that
hasn't been opened since the world was young.)
MIRUMOTO HIKARU: I ran.
MIRUMOTO HIKARU: Togashi told me to run, and I ran, and I have remembered it every day since.
MIRUMOTO HIKARU: He put this tattoo on me so I would live to remember. A living book.
MIRUMOTO HIKARU: (touching the basin) I was forbidden to speak until I saw the child in its bed of stone.
MIRUMOTO HIKARU: (to Sayo) Someone must carry it down now. Not me. I've carried it long enough.
[SET hikaru_spoke]
> CHOICE "The grandchildren"
  - "Tell them everything." → [SET climbers_told]
      MATSU HANAE: (after a long silence) …If this is ever told, the Empire burns. Every clan's legend. Every throne.
      MATSU HANAE: (kneeling to Sayo, astonishing everyone) I'll keep the silence. On my family's name. (beat) Thank you for telling us the truth, Sayo.
  - "Let them keep the legend." → (Sayo carries it alone)
      SAYO: (to the climbers) The ghosts were very confused. Old ghosts. Let's go down.

## S06 — Only One Comes Down
MAP: `cloud_bridge` → `ice_ledges` → `cedar_slopes` (blizzard) · TRIGGER: descend
(A blizzard. The legend says only one champion came down. Sayo ties every rope herself, checks every knot twice, and
makes sure *everyone* comes down.)
HIDA REN: (shouting over the wind) Why are you doing this? We treated you like a porter!
SAYO: You *paid* me like a porter! (yanking a knot tight) Porters get everyone home. That's the job.
(At the castle gate, Hikaru stands in the snow and does not follow.)
SAYO: You're not coming?
MIRUMOTO HIKARU: I'll stay with the child. (a very faint smile) It's the first time I've *chosen* to.
### The village
(Old Mosuke at the snow mounds.)
> CHOICE "Old Mosuke"
  - "Tell him the truth — quietly." → [SET mosuke_knows]
      SAYO: (kneeling beside him) Your grandfather's grandfather wasn't silly. The real prince never came down.
      SAYO: And the one who did — the one who became Emperor — was a baby from *this* village.
      OLD MOSUKE: (a long silence; then he begins to cry, and laugh) …All these years. All these years we left rice for them and didn't know why.
  - "Tell him the legend." → (he nods, satisfied; the offerings continue)
SAYO: (leaving her own rice cake on a mound) You weren't punished for anything. You were just in the way.
SAYO: (beat) I know what that's like.

## S07 — Ending
MAP: `wounded_lion_village` (night) · TRIGGER: auto
(Sayo sits alone by the village fire, turning the snake beads in her fingers.)
SAYO: (to no one) Every emperor for three hundred years. A peasant's grandson's grandson's grandson.
SAYO: Blood means nothing. (beat) Funny.
SAYO: That's the one thing samurai would kill to stop anyone saying.
(Far away, in the dark beyond the firelight, someone with a snake ring on their wrist watches her.)
[IF order_promise kept] (The watcher bows toward her — a deep, odd, respectful bow — and slips away.) [ELSE] (The
watcher writes something on a slip of paper, folds it, and slips away.) [END]
[CHAPTER COMPLETE]
### Chapter complete card
**"The Village of the Wounded Lion" — complete.**
Journal: *A legend climbed by grandchildren in their best colours, a hermit who kept a promise for three hundred
years, and a basin of red stones. Sayo carried the truth down the mountain — and it is heavy enough to topple a
dynasty.*
[UNLOCK] Bloodstone Shard (Void accessory) · Hikaru's kata scroll (post-game, for Gendo) · Rank 3 at 41: third ronin technique

---
## Travel Banter unlocked by Ronin Ch3
### TB-ronin3-a "Porters" (Sayo + Shizue)
SHIZUE: You got five proud samurai down a mountain in a blizzard by tying knots.
SAYO: Somebody had to.
SHIZUE: In go, the stone nobody notices is often the one that saves the corner.
SAYO: (laughing) Is that a compliment?
SHIZUE: It's the highest one I know.
### TB-ronin3-b "Heavy" (Sayo + Mitsue)
MITSUE: You're carrying something. I can tell. You walk like I walk after a very good secret.
SAYO: It's not a good secret.
MITSUE: (gently) Those are the heavy ones. (beat) If you ever want to put it down for an evening, I'll hold it. I'm very good at not looking inside.
SAYO: (pause) …I know you are. That's why I'll say no.
