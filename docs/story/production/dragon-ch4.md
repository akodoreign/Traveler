# PRODUCTION — Dragon Ch4 · "The Battle of the White Stag"

**Traveler:** Kitsuki Gendo · **Lv** 41–45 · **Outline:** `scripts/dragon-ch4-the-battle-of-the-white-stag.md`
**Flags read:** `history`, `tsuhime_helped`, `mirrors_recovered` · **Flags set:** `fronts_won` (0–3),
`kumpei_spared`, `glory_refused`, `vial_saved`, `history_final`
**Maps:** `war_camp_400`, `land_front`, `mantis_council`, `lighthouse_peninsula`, `harbour_tunnels`, `gaijin_flagship`,
`palace_400`, `cove_cave_return`, `kitsuki_yasu_hall`
**Battles:** `b_front_land` (defend N turns), `b_front_mantis` (duel or talk), `b_front_lighthouse` (escort Sanro),
`b_harbour_musketeers`, `b_boss_kumpei_flagship`
**Set-piece:** the three-front battle chain. **Yosai returns.** · **Storyboard:** `storyboards/dragon-ch4.md`
**On entering through the Ink Door:** prompt — *"When this chapter ends, the door will close forever. The past's
shops and chests will be gone."* (G-1: when Yosai rejoins he is story-locked; Momo returns to the roster.)

---

## S01 — Wearing a Dead Man's Face
MAP: `war_camp_400` · TRIGGER: start
NARRATION: The year 400. A gaijin army marches on the capital. The Crane Champion is dead. And a clerk from 1122 is
about to become him.
(A tent. Seikidera's armour on a stand. Doji Tomeko holds out the sword *Shukujo*. It does not ring when Gendo takes it.)
DOJI TOMEKO: It only rings for its true wielder.
GENDO: Then we'll hope nobody listens closely.
[IF mitsue_in_party]
MITSUE: (painting his face with a fine brush) Seikidera had a scar here. Faint. And he held his chin a little higher.
GENDO: How do you know?
MITSUE: You told me. (beat) You've told me every detail about him four times since dinner.
[ELSE]
(A Crane make-up artist, terrified, works by lamplight.)
[END]
GENDO: (internal, checking the bronze mirror) He tilted his head left when he lied.
GENDO: (internal) I'll keep mine very straight.
### Yosai returns
(The tent flap bursts open. A shaved head, singed eyebrows, a grin.)
TOGASHI YOSAI: Twenty-one!
GENDO: (spinning) Yosai!
TOGASHI YOSAI: The ink tried to eat me. It didn't like the taste. (beat) It spat me out three days ago, in a fish market. I've been looking for you ever since.
TOGASHI YOSAI: (looking at Gendo in the Champion's armour) …Gendo. Why are you a dead Crane?
GENDO: It's a long story.
TOGASHI YOSAI: (sitting down cheerfully) Good. I love long stories. They're the ones you survive.
[GUEST +Togashi Yosai (rejoins)]
[SAVE]

## S02 — Three Fronts (set-piece)
MAP: `land_front`, `mantis_council`, `lighthouse_peninsula` · TRIGGER: the battle begins
### SYSTEM — the battle chain
"Win **three fronts**, in any order. Each won front gives the final battle a **buff**. A lost front costs
**History**."
- Losing a front battle is **not** a game over: the front is lost (History −10, no buff). GENDO (internal): "I filed
  this battle as a victory. I was wrong."
### Front 1 — The Land (defend)
"Hold the line for **6 turns** until the Dragon and Centipede relief arrives."
GENDO (as Seikidera, to the Crane line): Hold! The Dragon are coming!
CRANE SOLDIER: The Champion's voice is… different.
GENDO: (very steady) I've been shouting all morning. Hold!
[BATTLE b_front_land] → win: artillery buff (the flagship's cannons fire half as often)
(The Dragon and Centipede banners over the hill. A roar.)
[IF tsuhime_helped] (At the head of the relief, Seppun Ushimo, alive, sword high.) SEPPUN USHIMO: "For the boy-Emperor! And for the man with glass eyes!" [END]
### Front 2 — The Mantis Council (talk or duel)
(The Mantis trader GUSAI IAMI in a ship's cabin, sweating, surrounded by gaijin gifts.)
GUSAI IAMI: The gaijin pay well, Champion. Better than the throne.
> CHOICE "Gusai Iami"
  - [PA Discern Iami] → "Owes the gaijin a fortune. If they win, they own him."
      GENDO: You don't take gaijin money, Iami-san. *They* take *you*. Ask your ledgers.
      GUSAI IAMI: (pale) …How do you know about my ledgers?
      GENDO: (straight-faced, as Seikidera) Champions know everything.
  - Duel his champion → [BATTLE b_front_mantis]
→ win: Mantis ships buff (they sail against the gaijin)
### Front 3 — The Lighthouse (escort)
"Keep the **Isawa wards** lit on the peninsula. Protect the boy **Isawa Sanro**. If he falls, **History −30%**."
ISAWA SANRO: (feeding the ward-fire) Champion! Do you think the fire has a spirit? It feels like it's *helping*!
GENDO: I think it likes you very much, Sanro. Keep feeding it.
[BATTLE b_front_lighthouse] → win: ward buff (party E.Def + in the final battle)
[SET fronts_won]
[SAVE]

## S03 — The Harbour Choked With Wrecks
MAP: `harbour_tunnels` · TRIGGER: after the fronts
(Cannon fire. Burning wrecks. Sharks in the red water. Gaijin musketeers in the old sea-tunnels under the harbour.)
[BATTLE b_harbour_musketeers]
### History rule
"**Gunpowder barrels** line the tunnels. **Using one — History −5%.**"
TOGASHI YOSAI: (eyeing a barrel) This would solve everything.
GENDO: That's exactly what Akuro thought.
TOGASHI YOSAI: (sighing, walking past it) …You're no fun at all, Gendo.
[SAVE] (the flagship gangway)

## S04 — Kakita Kumpei and the Flagship (BOSS)
MAP: `gaijin_flagship` · TRIGGER: board
(The gaijin flagship's deck. Cannons. And at the rail, painting frantically on a stretched silk, KAKITA KUMPEI —
the last vial of kami-ichor at his hip. Akuro is not here.)
KAKITA KUMPEI: Akuro's gone ahead. Into the ink. Toward *your* year.
KAKITA KUMPEI: I was going to save the Empire. (laughing, tears in his eyes) Nobody ever asked me to paint anything else.
GENDO: Then paint me the year 1122, Kumpei. Exactly as it is.
GENDO: (beat) Nobody else can.
[BATTLE b_boss_kumpei_flagship]
### Barks / mechanics
- Cannons (timer; halved if the land front was won): "CANNONS! Down!"
- Kumpei's living-ink sigil copies one party buff per turn: KAKITA KUMPEI: "Your courage, painted. Mine now."
- **The vial:** "Break him before turn 8, or he hurls the vial overboard."
  - [IF turn ≥ 8] (Kumpei throws it. Yosai dives over the rail.) TOGASHI YOSAI: "TWENTY-TWO!" (he surfaces with it; no reward)
  - else [SET vial_saved]
- Defeat: KAKITA KUMPEI: (sinking to his knees, brush in hand) "…It's a very beautiful year, 1122. I saw it in your eyes when you arrived."
> CHOICE "Kumpei"
  - "Spare him. Let him paint us home." → [SET kumpei_spared]
      KAKITA KUMPEI: (weeping, painting) …I'll get the light right. I promise. I'll get the light *exactly* right.
  - "Give him to the Emperor's guards." → (he paints the way home under guard)

## S05 — The Emperor's Offer
MAP: `palace_400` · TRIGGER: the battle won
(The palace. The court bows. The boy-Emperor HANTEI KUSADA stands before "Seikidera" — then, privately, before Gendo, the paint washed off.)
HANTEI KUSADA: I know you're not Seikidera.
GENDO: (bowing low) …Yes, Majesty.
HANTEI KUSADA: You saved my city wearing a dead man's face. I could give you a clan. Lands. A name in every history.
HANTEI KUSADA: "Gendo the Saviour." They'd paint your glass eyes on temple walls.
> CHOICE "The offer"
  - "Accept." → (History −50%; an epilogue vision of a darker 1123)
      GENDO: (after a long silence) …I accept, Majesty.
      (The scene shimmers. Somewhere in the future, something shifts.)
  - "Refuse. Erase me." → [SET glory_refused] (recommended; Honor +5, told to no one)
      HANTEI KUSADA: You'd give up being remembered?
      GENDO: Majesty, I was an archive clerk for nine years.
      GENDO: (smiling) I know exactly how little being remembered is worth. It's the remembering that matters.
      GENDO: Let them remember *him*. Seikidera. He earned it. He rode out alone to stop a war.
      HANTEI KUSADA: (a long look, very old for fourteen) …I'll burn the records myself.
      HANTEI KUSADA: (beat) But I'll remember. Is that allowed?
      GENDO: (bowing) That's the only kind that matters, Majesty.
[SET history_final = "erased" if glory_refused, else "saviour"] (finale: the "saviour" route plays the darker-1123 vision in Gendo's coda)

## S06 — Home
MAP: `cove_cave_return` → `kitsuki_yasu_hall` · TRIGGER: Kumpei's portal
(Kumpei's painted portal: a cherry orchard dissolving into a grey sea-cave. Tortoise Island. Summer 1123.)
TOGASHI YOSAI: (stepping out, sniffing the air) Fish! Rain! *Our* century! (beat) Twenty-three — no, that was the landing. That doesn't count.
(Behind them, the Ink Door's painted cave goes still. Just paint now. The year 400 is sealed.)
(The hall of Lord KITSUKI YASU. Gendo reports. Everything.)
KITSUKI YASU: Time travel.
GENDO: Yes, my lord.
KITSUKI YASU: The year four hundred. A boy-Emperor who liked your *spectacles*.
GENDO: Yes, my lord.
KITSUKI YASU: (long pause) …You'd make a fine jester, Gendo.
GENDO: (polishing his spectacles) Thank you, my lord. I'll consider it.
(Outside, Yosai is waiting with two persimmons.)
TOGASHI YOSAI: Well?
GENDO: He thinks I should be a jester.
TOGASHI YOSAI: (handing him one) You'd be terrible. You never laugh at your own jokes.
### Akuro's prophecy (a solo beat)
GENDO: (alone, writing in his notebook) "The son will become the dark brother. The jade clan goes black. The dead rule."
GENDO: "…and out of all hope, seven mortals will rise."
GENDO: (stopping; tapping the pen) Seven. (beat) There are eight of us.
[CHAPTER COMPLETE]
### Chapter complete card
**"The Battle of the White Stag" — complete.**
Journal: *Gendo wore a dead Champion's face to win a battle four hundred years in the past — and then refused to be
remembered for it. Home again, his lord suggests a career as a jester. Akuro is already somewhere in 1123.*
[UNLOCK] *Time Between Breaths* kata at Lv 51 (Mirumoto 3) · `glory_refused` (Honor +5) · pressed cherry blossom (accessory)

---
## Travel Banter unlocked by Dragon Ch4
### TB-dragon4-a "Remembered" (Gendo + Haruki)
HARUKI: You gave up being in every history.
GENDO: I've read every history. Being in them isn't as nice as you'd think.
HARUKI: (quietly) …I've been left out of a report too. It was the kindest thing anyone did for me all year.
GENDO: Then we're both very well-hidden men.
### TB-dragon4-b "Twenty-three" (Gendo + Yosai, guest)
GENDO: The landing doesn't count?
TOGASHI YOSAI: Falling out of a portal isn't the Fortunes trying to kill me. That's just *physics*.
GENDO: You know about physics?
TOGASHI YOSAI: I've fallen off a great many things, Gendo.
