# PRODUCTION — Crane Ch4 · "The Play No One Performs"

**Traveler:** Kakita Rensei · **Lv** 41–45 · **Outline:** `scripts/crane-ch4-the-play-no-one-performs.md`
**Flags read:** `same_woman_proven`, `tadanobu_letters` · **Flags set:** `play_known_scenes` (0–3),
`rehearsal_quality`, `play_handed_over`, `duel_won`, `sanae_answer`
**Maps:** `kyuden_doji` (court, Sanae's rooms), `doji_archives_1–3`, `rehearsal_hall`, `kakita_dueling_ground`
**Battles:** `b_archive_spirits`, `b_archive_guardian`, `b_boss_masanori` (formal duel)
**Set-piece:** the rehearsal (3 timing prompts + 2 dialogue picks) · **Storyboard:** `storyboards/crane-ch4.md`
(adds the castle-town screen of `kyuden_doji`)

---

## S01 — Bury It
MAP: `kyuden_doji` (Sanae's rooms) · TRIGGER: start
NARRATION: Kyuden Doji. The most beautiful castle in the Empire. Beauty, the Crane say, is what you show. The rest
you keep in boxes.
LADY SANAE: (pouring tea; not drinking it) The woman behind the border crisis, Rensei-san. You saw her face.
RENSEI: Two faces, my lady. One woman.
LADY SANAE: She was a Doji.
RENSEI: (setting down his cup very carefully) …My lady?
LADY SANAE: Doji Nashiko. Four centuries ago. She was jilted by the Emerald Champion, Doji Komatsu.
LADY SANAE: So she destroyed his entire court. With maho.
LADY SANAE: The Crane cannot have a demon in the family tree. (beat) Find everything the archives hold on her.
LADY SANAE: Then we will decide what the archives *held*.
RENSEI: (bowing) …Yes, my lady.
RENSEI: (internal) Bury it. She wants me to help bury it.
[SAVE]

## S02 — The Archives (dungeon)
MAP: `doji_archives_1–3` · TRIGGER: descend
(A library like a maze. Censor-monks with brushes and blades. Wards glowing on certain shelves.)
CENSOR-MONK: The forbidden shelves are forbidden, young lord.
> path actions
  - [PA Charm Censor-monk] → RENSEI: "Lady Sanae of the House Honour sends me. She'd hate to have to come herself."
      CENSOR-MONK: (paling) …Shelf nine. Mind the guardian.
  - *Watchful Falcon* kata (if equipped) → hidden shelves glow on the map
[BATTLE b_archive_spirits] (paper-spirits — weak to Fire, Tanto)
[BATTLE b_archive_guardian] (the forbidden shelf's kami)
(Shelf nine. A box sealed with Imperial wax, four hundred years old. Inside: a noh play.)
RENSEI: (reading the title) *The Empress of Nothing.* (beat) Written by "a survivor of the court of Komatsu".
### Reading the play (each scene read → [play_known_scenes +1])
(The scenes are on three lecterns in the forbidden wing (storyboard): Scene 1 in plain sight · Scene 2 behind a
Calligraphy cipher (Haruki or Gendo at Calligraphy 3, or Rensei with *Watchful Falcon*) · Scene 3 behind the guardian,
with the margin note.)
- **Scene 1 — The Mirror:** "She sees all smooth stone as jade. The colours are lost to her."
  RENSEI: She's colour-blind.
- **Scene 2 — The Blade:** "A cut to her face undoes her. She cannot bear to be marred."
  RENSEI: A terror of disfigurement.
- **Scene 3 — The Title:** "Call her Empress, and her guard falls for a breath. She wants it more than life."
  RENSEI: She wants to be called Empress.
- **Margin note:** "She reads only one heart at a time. Speak two truths at once, and she hears neither."
RENSEI: (very still) She doesn't know this play exists. (beat) Nobody has performed it in four hundred years.
[ITEM +"The Empress of Nothing" (play script — finale key item)]
[SAVE]

## S03 — Will It Work? (set-piece: the rehearsal)
MAP: `rehearsal_hall` (night) · TRIGGER: after S02
(A disused rehearsal hall. Rensei recruits three court actors who owe him favours — and swears them to silence.)
ACTOR: A forbidden play? At night? (delighted) Finally, Kyuden Doji has culture.
[IF mitsue_in_party]
MITSUE: (from the shadows at the back, sitting on a costume trunk) Oh, please let me direct.
RENSEI: You're a Scorpion.
MITSUE: I'm an *actress*. The Scorpion part is a hobby.
[END]
### SYSTEM — the rehearsal
"Stage the play's key scene. **3 timing prompts** (cue the mirror · cue the false jade · speak the title) and
**2 dialogue picks**. A good rehearsal unlocks the finale's **'Empress' bait**."
- Cue the mirror (timing): ACTOR: "The lady gazes — and sees jade where there is only stone!"
- Pick 1 — how to deliver "Empress":
  - "With awe." → (best) [IF mitsue_in_party] MITSUE: "Yes. *Mean* it. She can tell flattery from worship." RENSEI: "How do you know?" MITSUE: "Because I can." [END]
  - "With mockery." → (fail) ACTOR: "She'd tear your throat out for that tone, young lord."
- Cue the false jade (timing)
- Pick 2 — "Two truths at once":
  - "Two actors speak at the same time." → (best) ACTOR: "It sounds like chaos!" RENSEI: "Exactly. She can only follow one."
  - "One speaks, then the other." → (weak)
- Speak the title (timing)
[SET rehearsal_quality good/poor]

## S04 — My Father's Answer
MAP: `kyuden_doji` (court) · TRIGGER: morning
(KAKITA MASANORI, Rensei's father, enters Sanae's rooms unannounced — which no one does.)
KAKITA MASANORI: A forbidden play. Rehearsed at night. By my son.
KAKITA MASANORI: The Kakita name tied to a Doji demon in the archive registers.
KAKITA MASANORI: Burn it. Today.
> CHOICE "The play"
  - "Hand it over." → [SET play_handed_over] (Sanae secretly saves a copy; finale debuffs halved)
      RENSEI: (bowing, holding it out) …Yes, Father.
      (Later, Sanae, alone, drawing a second copy from her sleeve.) LADY SANAE: "Hm."
  - "Refuse." → (the formal duel; recommended)
      RENSEI: No, Father.
      (Silence. Nobody in the room has ever heard a Kakita son say it.)
      KAKITA MASANORI: (very quietly) Then we will settle it the Kakita way. First blood. At dawn.
[SAVE] (Sanae's rooms, the night before)

## S05 — First Blood (BOSS)
MAP: `kakita_dueling_ground` (dawn) · TRIGGER: refuse in S04 (or a "test" duel anyway if handed over — Masanori insists on testing his son)
(White sand. Two men in white. The court watches from the veranda. Sanae among them, expressionless.)
KAKITA MASANORI: Your left foot still hesitates.
RENSEI: (taking his stance) Yes, Father.
[BATTLE b_boss_masanori]
### Structure / barks
- **Phase 1 — duel** (more Focus than Rensei; *One Strike Blade* gives him speed).
  KAKITA MASANORI: "Focus. Again. Again. You'll never be faster than me."
- **Phase 2 — kata** (*Kakita's First Stance*: he duels with his Honor; *Watchful Falcon*).
- **Win:** first blood — break him (Suki) once **and** land a crit.
  RENSEI: (Strike) "Yes, Father. (beat) It's waiting for me to decide." (the cut lands — a thin red line on his father's sleeve)
  [SET duel_won]
  (Masanori looks at the red line on his sleeve for a long time.)
  KAKITA MASANORI: (to no one, or to himself) …The foot didn't hesitate.
- **Loss:** Masanori stops a hair from Rensei's throat. KAKITA MASANORI: "…Adequate."
  [IF NOT play_handed_over] (He holds out his hand. Rensei gives him the play.) [SET play_handed_over] [END]
  (Sanae has the copy; the story continues.)

## S06 — A Very Dull Sword
MAP: `kyuden_doji` (court) · TRIGGER: after the duel
LADY SANAE: One question, Rensei-san. The House's honour, or the Empire?
> CHOICE "Sanae's question" [SET sanae_answer]
  - "The Empire." → LADY SANAE: "Brave. Foolish. Correct."
  - "The House." → LADY SANAE: "Honest. Also correct, in its way."
(Either way: in front of the whole court she burns a scroll in the brazier.)
LADY SANAE: (to the court) There. The play is destroyed.
(Later, alone, she slides the real one out of her sleeve and into Rensei's hands.)
LADY SANAE: That scroll was blank. (beat) I keep a supply of blank scrolls for exactly this reason.
LADY SANAE: A sword that only cuts what it's told to is a very dull sword, Rensei-san.
RENSEI: (holding it) Why help me?
LADY SANAE: Because she's a Doji. (beat) And the House should be the one to finish her.
(That night. Rensei's sword lies on its stand. Someone has rewrapped the hilt in new white silk. There's no note.
There doesn't need to be.)
RENSEI: (touching the wrap) …Father.
[ITEM +Father's Hilt-wrap (accessory: Iaijutsu Strike crit up)]
[CHAPTER COMPLETE]
### Chapter complete card
**"The Play No One Performs" — complete.**
Journal: *A play about a demon, banned for four hundred years. Rensei rehearsed it in secret, refused his father,
and drew first blood — and found a new hilt-wrap on his sword with no note at all.*
[UNLOCK] *One Strike Blade* kata at Lv 51 · the play (finale: `play_known_scenes`, `rehearsal_quality`)

---
## Travel Banter unlocked by Crane Ch4
### TB-crane4-a "Blank Scrolls" (Rensei + Gendo)
GENDO: Lady Sanae keeps a supply of blank scrolls to burn in public.
RENSEI: Yes.
GENDO: (with deep professional respect) …I'd like to meet her.
RENSEI: She'd file you under "useful" in a heartbeat.
GENDO: That's the nicest thing anyone could file me under.
### TB-crane4-b "First Blood" (Rensei + Sayo)
SAYO: You fought your *father*?
RENSEI: Ceremonially. First blood.
SAYO: And you won.
RENSEI: (pause) …He let me see that I'd won. I don't think that's the same.
SAYO: (gently) Maybe it's better.
