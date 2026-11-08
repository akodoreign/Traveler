# PRODUCTION — Ronin Ch4 · "The Oracle's Choice"

**Traveler:** Sayo · **Lv** 41–45 · **Outline:** `scripts/ronin-ch4-the-oracles-choice.md`
**Flags read:** `climbers_told`, `mosuke_knows`, `order_promise` · **Flags set:** `well_cleansed`, `race_route`
(road / cliff), `naga_talked_down`, `sayo_saw_nashiko`
**Maps:** `oracle_town`, `eta_quarter_oracle`, `poisoned_well`, `oracle_rooftops`, `switchback_stair`, `crater_shrine`
**Battles:** `b_well_agents`, `b_race_assassins_1–3` (+2 on the cliff route), `b_boss_naga_champion`
**Guest:** Hiro
**User rule:** Sayo gains **no Oracle powers**. Keepsake: the ember charm.
**Storyboard:** `storyboards/ronin-ch4.md` (adds route `oracle_road`)

---

## S01 — The Fire Talks to Me
MAP: `oracle_town` · TRIGGER: start
NARRATION: The shrine town of the Oracle of Fire, on the flank of a living volcano. The old Oracle is leaving his
body. The whole Empire is watching to see who he chooses.
(Thousands of pilgrims. Prayer flags. Heat-shimmer. A young eta woman in grey, hiding in a doorway: AKARI. She sees
Sayo and runs to her.)
AKARI: Sayo! You came!
SAYO: (hugging her) You sent for me. I came. That's how it works.
AKARI: The fire talks to me, Sayo. Since the spring. It says my name.
AKARI: It says it like a *lord* would. (shaking) I'm scared.
SAYO: Fire's like that. Loud and full of itself. (gently) Let's find out what it wants.
[SAVE]

## S02 — Three Hands Reaching (hub)
MAP: `oracle_town` · TRIGGER: explore
### The factions
- **Scorpion agents** (in plain pilgrim robes, too well-shod): "The Oracle will choose properly. A samurai. We'll *help* him choose."
- **Order of the Snake** scouts (snake rings): "Ronin girl. You carry something from the White Snow. Give it to us, and the Order will topple a usurper."
  SAYO: Which usurper?
  SNAKE SCOUT: (smiling) The biggest one there is.
- **Temple priests**: "An *eta*? Choosing an eta would be an obscenity. She should go away. Quietly. Tonight."
### Path actions
| Target | Path action | Result |
|---|---|---|
| Scorpion agent | *Pilfer* (Sayo) | a cipher letter: "poison the eta well before the ascension" |
| Scorpion agent | *Eavesdrop* (Mitsue) | "Two dozen of us. Rooftops by midnight." |
| Snake scout | *Discern* (Gendo) | "They don't care about Akari. They want the White Snow secret." |
| Frightened pilgrims | *Bless* (Haruki) | the crowd parts on the pilgrim road later (route bonus) |
| Old priest | *Barter* (Tamotsu) | the crater shrine's back-gate key (skips the last switchback battle in S06) |

## S03 — The Eta Quarter
MAP: `eta_quarter_oracle` · TRIGGER: hide Akari
[IF samurai in party] (The samurai stop at the quarter's edge, as before. This time Rensei steps forward one pace,
hesitates — and steps back.) RENSEI: "…Next time." SAYO: "Next time." [END]
(The eta quarter. HIRO, enormous, toothless, at the gate with his no-dachi. And a tiny old woman in grey smoking a
long pipe: UME-BAA.)
UME-BAA: There's my girl. Thinner. Taller. Same stupid hat.
SAYO: (crying and laughing at once) Ume-baa!
UME-BAA: (to Akari, kindly) You're the one the fire's shouting at. Come in, child. Fire can't shout through mud walls.
### Anatomy (Ume-baa's low knowledge)
UME-BAA: Samurai doctors heal from across the room so they don't have to touch you.
UME-BAA: (taking Sayo's hands) We heal from *here*. Let me teach you the bit they won't.
[SKILL +Anatomy (Low) → *Diagnosis*: the next Remedy on a target gets +1 tier]
(Hiro's arm. The three claw marks, red and swollen.) SAYO: (a jade Remedy) "Hold still, Hiro." HIRO: "…It's quieter.
The tiger. It's quieter." SAYO: (not fooled) "For now." → [UNLOCK] Hiro SS2 "The Tiger in the Blood" (after this chapter)
[GUEST +Hiro]

## S04 — The Poisoned Well
MAP: `poisoned_well` · TRIGGER: the cipher letter
(Night. The eta quarter's well. Figures in pilgrim robes pouring something into it.)
SAYO: (low) Poison the well, and the priests say the eta are unclean, and the fire's choice is "a curse".
[BATTLE b_well_agents]
(The well water already darkening.)
### Remedy (story brew)
"**Rhubarb + Moxa** — a purge that spreads. Pour it in." (Poison skill rank shows the counter-recipe.)
SAYO: (pouring the brew into the well) Rhubarb. Moxa. And a pinch of spite.
[SET well_cleansed]
### The blue-eyed woman
(In the pilgrim crowd at the well's edge, a lovely woman in Scorpion grey, whispering to an agent. Later, in a priest's
robe, whispering to a priest. Later still, with a snake ring, whispering to a scout. The same smile each time.)
SAYO: (watching) …Same smile. Three faces. (beat) Nobody hides from a ronin girl. We're not worth hiding from.
[SET sayo_saw_nashiko]
[SAVE]

## S05 — "Somebody" (fake choice)
MAP: `oracle_town` (a quiet teahouse) · TRIGGER: the Order makes its offer
(A snake-ringed elder pours tea for Sayo with exquisite courtesy.)
SNAKE ELDER: A name. A house. A place. Lands, if you want them. A *family*.
SNAKE ELDER: All for one secret from the White Snow. You'll be *somebody*, Sayo.
> CHOICE "The offer"
  - "Accept." → (Sayo opens her mouth to accept — and laughs.)
  - "Refuse." →
SAYO: A name? (beat) I've had lots of names. "Wave-girl." "Ronin's brat." "You there."
SAYO: (standing, grinning) Sayo's the only one I picked. I'll keep it.
SNAKE ELDER: (a long look) …The Voice said you'd say that.
[IF order_promise kept] SNAKE ELDER: "And that you'd keep the secret even from us. The Voice was pleased." [END]

## S06 — The Night Race (set-piece)
MAP: `oracle_rooftops` → `switchback_stair` · TRIGGER: midnight; the ascension is at dawn
### SYSTEM — the chase
"Get **Akari** to the crater shrine before dawn. **Three battles in a row**, **no full heal** between them — items
and Remedy only. Choose your route."
> CHOICE "The route" [SET race_route]
  - "The pilgrim road." → (fewer fights; [IF Bless used on the pilgrims] the crowd parts for them)
      PILGRIM (shouting, making way): The eta girl! Let the fire's girl through!
  - "The cliff path." → (faster; +2 battles)
[BATTLE b_race_assassins_1] (rooftops) SAYO: "Akari, hold my basket! Don't drop the ginseng!"
[BATTLE b_race_assassins_2] (the alley) HIRO: "Go! I'll hold the alley!" (Hiro stays behind, holding the line)
[IF climbers_told AND race_route road] (On the switchback, five young samurai in bright clan colours push through
the pilgrims.) MATSU HANAE: "Ronin! *Sayo!* Go — we'll hold this one!" (replaces battle 3) [ELSE]
[BATTLE b_race_assassins_3] (the first switchback) [END]
[IF race_route cliff] [BATTLE b_race_assassins_4] [BATTLE b_race_assassins_5] [END]
(With the back-gate key, the last switchback battle is skipped.)
[SAVE] (a crater lantern at the top of the stair)
AKARI: (gasping, climbing) Sayo — I can't — the fire's so loud —
SAYO: (pulling her up) Then shout back! Tell it to wait for us!
AKARI: (a cracked, astonished shout up at the mountain) WAIT FOR US!
(The mountain rumbles. It sounds, almost, like it's laughing.)

## S07 — The Naga's Champion (BOSS)
MAP: `switchback_stair` (the top) · TRIGGER: near the crater
(At the top of the stair, blocking the way: a great serpent-bodied warrior in pearl-and-bronze armour, spear lowered.
The Great Naga's champion — the Order's guardian.)
NAGA CHAMPION: The Order guards the true lines. The choice must be the *right* one.
SAYO: It is. (pointing at Akari) There's a true line. It goes from her to the fire.
SAYO: (drawing) Guard *that*.
[BATTLE b_boss_naga_champion]
### Barks / talk-down
- "Weak to **Air**, **Yari**, **Fire**. Resists Water."
- NAGA CHAMPION (at half): "You fight like one with no line. No one taught you."
- SAYO: "Everyone taught me. Eta, barge-folk, a monk, a tiger. I just didn't have a dojo."
- **On Suki:** (the champion's spear dips) → talk-down prompt:
  SAYO: The Voice in the den judged me. "Of no line. Free to carry what no line can."
  SAYO: Well. I'm carrying *her*.
  NAGA CHAMPION: (a long, slow breath, like a tide going out) …So the Voice said.
  (It lowers its spear and coils aside.) [SET naga_talked_down] (Honor +1)

## S08 — The Ascension
MAP: `crater_shrine` (dawn) · TRIGGER: the stair cleared
(The crater shrine, at the lip of the fire. The old ORACLE OF FIRE stands at the edge, ancient, half-made of flame.
Dawn breaks.)
OLD ORACLE: (turning; a voice like a bonfire) You brought her. Good. I was getting impatient. Fire always is.
(He holds out a burning hand. Akari, shaking, takes it. The old Oracle becomes light and rises into the dawn like a
spark from a bonfire, and is gone.)
(Akari stands at the crater's edge. The flames in the pit bow toward her. The priests who climbed behind them fall to
their knees. Some weep. Some look furious.)
AKARI (the new Oracle; her voice carries like a bonfire now): Sayo.
AKARI: (beat; almost herself again) …It still says my name like a lord.
AKARI: (smiling) But it says yours like a friend.
(She holds out something small and warm: an ember, caught in a twist of iron.)
AKARI: For you. It won't make you anything. It'll just keep you warm. And light, if you need it.
[ITEM +Ember Charm (once per battle: a small Fire hit OR a revive)]
SAYO: (taking it; no powers, no glow, just an ember) …That's all I ever wanted from fire, honestly.
### Ending beat
(The descent. Sayo turns the snake beads in one hand and the ember in the other.)
SAYO: (to herself) Three hundred years of emperors, descended from a peasant.
SAYO: I could start a war with one sentence. (beat) I'll keep it. For the villagers who'd die in it.
[IF mosuke_knows] SAYO: (beat) For Old Mosuke's rice cakes. [END]
SAYO: (looking at her friends ahead on the path) …And for my family.
[CHAPTER COMPLETE]
### Chapter complete card
**"The Oracle's Choice" — complete.**
Journal: *An eta woman the fire called by name, a poisoned well, a race up a burning mountain, and a serpent that
lowered its spear. Sayo didn't become the Oracle. She got her friend there alive — and finally chose a family.*
[UNLOCK] Ember Charm · Anatomy · Rank 4 at 51: fourth ronin technique · `sayo_saw_nashiko` (finale clue)

---
## Travel Banter unlocked by Ronin Ch4
### TB-ronin4-a "Family" (Sayo + all, at the inn)
SAYO: (setting down a pot of something that smells like dirt and is delicious) I made dinner.
NATSUKO: What is it?
SAYO: Medicine. It just happens to be soup.
TAMOTSU: (tasting) Sayo, this is magnificent.
SAYO: (sitting down among them; quietly) …Good. Eat it all. That's an order from your family.
### TB-ronin4-b "Ember" (Sayo + Haruki)
HARUKI: The Oracle gave you an ember. Not power.
SAYO: Just warmth.
HARUKI: (looking at it) …I think that's the rarer gift.
SAYO: (grinning) Don't tell the Phoenix Council. They'll want to study it.
