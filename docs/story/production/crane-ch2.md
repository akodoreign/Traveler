# PRODUCTION — Crane Ch2 · "The Iron Cranes" (Crossroads: Two Faces of the Border)

**Owner:** Kakita Rensei · **Partner:** Hiruma Natsuko (else stand-in **Hiruma Goro**) · **Lv** 20–25
**Outline:** `scripts/crane-ch2-the-iron-cranes.md`
**Flags read:** `depura_seen` · **Flags set:** `tadaka_lie_heard`, `eriko_close`, `camp_split`, `uji_won_by`,
`same_woman_proven`
**Maps:** `garden_under_shadow` (lantern garden, castle), `land_bridge`, `yasuki_yashiki` (hall), `border_camp_1–2`,
`miyako_chamber` (+ the port-town screen of `garden_under_shadow`; tidal `land_bridge`: low tide only)
**Storyboard:** `storyboards/crane-ch2.md`
**Battles:** `b_camp_sentries_a/b`, `b_boss_iron_cranes` (charmed-generals gimmick)
**Partner lines** are marked `[IF natsuko_in_party]`. In the `[ELSE]` blocks, HIRUMA GORO speaks the stand-in line.

---

## S01 — Garden Under Shadow
MAP: `garden_under_shadow` (lantern garden, night) · TRIGGER: arrive
NARRATION: Garden Under Shadow City. A Daidoji port where the tide comes in twice a day, and the land-bridge to the
Crab vanishes under it.
(A dinner in a garden of a thousand lanterns. Daidoji generals in iron-grey. And at the centre of every gaze, a
white-haired Crane courtier who laughs like silver: DOJI MIYAKO.)
LADY SANAE: (aside) The border is a hair from war, Rensei-san. Those men are the hair.
RENSEI: They're all looking at her.
LADY SANAE: Yes. (beat) Count how many, and tell me later.
(A jealous painter with ink-stained sleeves glares at Miyako from behind a screen: KAKITA YUMI.)
### Charm targets
- **Kakita Yumi** — [PA Charm] →
  KAKITA YUMI: Her? She arrived three months ago. Now every general paints her into his dreams.
  KAKITA YUMI: (bitterly) She told me she loved my work. She's never once looked at it.
- **Daidoji Eriko** (wife of General Daidoji Shinro) — [PA Charm] → [SET eriko_close]
  RENSEI: Your husband looks… distracted tonight, my lady. Perhaps he'd like you nearer.
  DAIDOJI ERIKO: (a sharp glance at Miyako, then a smile at Rensei) …Perhaps he would. Thank you, young man.
(A Lion envoy at a side table, IKOMA TADAKA, raises his cup to Miyako.)
IKOMA TADAKA: Lady Miyako, you mentioned your late uncle, Doji Moteuchi. He died on the *northern* border, you said?
DOJI MIYAKO: Defending it, yes. So bravely.
IKOMA TADAKA: (pleasantly) How strange. I served with Moteuchi. He died in the *south*. Of a fever.
(A tiny silence. Miyako's smile doesn't move at all.)
[SET tadaka_lie_heard]
(Minutes later: a cry from the dark end of the garden. Miyako, dishevelled, weeping, clutching a torn sleeve.)
DOJI MIYAKO: The Lion! He — he tried to —
(A Daidoji general's sword is out before anyone can speak. One cut. Tadaka falls among the lanterns.)
(Rensei is at the far end of the garden. Rank 1. He takes three steps. It's already over.)
RENSEI: (to Sanae, shaking) He was right. She lied. I *heard* her.
LADY SANAE: So did I. And a man is dead for hearing it.
LADY SANAE: Say nothing yet, Rensei-san. Remember everything.
[SAVE]

## S02 — Scalding Sake (partner side)
MAP: `land_bridge` → `yasuki_yashiki` · TRIGGER: next day
[IF natsuko_in_party]
(The land-bridge at low tide. Natsuko, in borrowed court clothes she clearly hates, crosses to the Crab side with
Rensei's letter of introduction.)
NATSUKO: (tugging at her collar) If anyone asks, I'm your… what am I?
RENSEI: My "esteemed Crab colleague".
NATSUKO: Nobody's ever esteemed me. It itches.
[ELSE]
[IF goro recruited] (Lady Sanae sends HIRUMA GORO — already travelling with the party — across the land-bridge with a letter.)
[ELSE] (Lady Sanae sends HIRUMA GORO, a big Crab bodyguard on loan from the Yasuki, across the land-bridge with a letter.)
[END]
HIRUMA GORO: (cracking his knuckles) Crab dinner. I know how those go. Somebody always ends up in the fish pond.
[END]
(The Crab hall at Yasuki Yashiki. Hida generals. And beside them, a lovely black-ponytailed Kuni apprentice with a
gentle smile: KUNI MIYUBI.)
(A Crab custom: sake served scalding hot, as a dare. Generals wince and swear. Miyubi drains her cup without a
flicker.)
[IF natsuko_in_party]
NATSUKO: (watching) Nobody drinks Crab sake like that. Not even Crab.
[ELSE]
HIRUMA GORO: (watching) I've seen a troll flinch at that sake.
[END]
(Two Hida generals start shoving over a remark. A sumai ring is cleared.)
[IF natsuko_in_party]
[PA Sumai Hida General Masakazu]
NATSUKO: (pinning him) Why are you angry, general? Really?
HIDA GENERAL MASAKAZU: (red-faced, ashamed) Because — because we raided an Asahina estate. Last month. On *her* word.
HIDA GENERAL MASAKAZU: She found maho masks there. She said they were planning to — (he stops) Gods. Did anyone else see the masks?
[ELSE]
(Goro wins the bout; the loser, Masakazu, confesses the same thing.)
[END]
(A one-handed Kuni with a burned face, KUNI AKUJA, holds up "relics" Miyubi found. He looks at her with naked
jealousy.)
KUNI AKUJA: She found in one night what I've hunted for ten years. Isn't that *remarkable*.

## S03 — Same Method Twice
MAP: `garden_under_shadow` (Sanae's rooms) · TRIGGER: partner's report arrives
(Sanae, Rensei, Seigen (if present) — and Natsuko, or Goro's letter read aloud.)
RENSEI: The Crane generals hang on Miyako. The Crab generals hang on Miyubi.
RENSEI: Miyako lied about a dead uncle. Miyubi drank sake hot enough to strip paint.
[IF natsuko_in_party]
NATSUKO: Two women. Same trick. Seduce the generals, plant a reason for war, wait.
[ELSE]
LADY SANAE: (reading Goro's letter) "Same trick both sides. Soft hands. Hard eyes. Ask the boy."
[END]
LADY SANAE: A Crane courtier and a Kuni apprentice. Never seen together.
RENSEI: (slowly) …Because they can't be.
[IF gendo_in_party] GENDO: Two crimes, one fingerprint. Courts call it coincidence. I call it a signature. [END]
> CHOICE "The border conference — how do we split?"
  - "I'll take Uji's camp. My colleague takes Yakamo's." → [SET camp_split split] (Natsuko/Goro leaves the active
    party for the night camp and takes the Crab camp off-screen; Yakamo's scene is her report; she rejoins for S05)
  - "We go together." → [SET camp_split together] (full party; Yakamo is met live at the meadow edge; banter
    "Two Faces, One Woman" unlocks)
[SAVE]

## S04 — A Night of Tents (dungeon)
MAP: `border_camp_1–2` (night) · TRIGGER: the conference
NARRATION: The border conference. Two armies, one meadow, and a lot of very sharp politeness.
(Night. Shadows move between the tents. A figure in white silk slips into one Crane general's tent — then another —
then a third. Later, a black ponytail ducks into a Crab tent.)
[BATTLE b_camp_sentries_a] (seduced sentries — they wake confused when broken)
SEDUCED SENTRY: The lady said — the lady said the Crab come at dawn—
RENSEI: The lady says a lot of things.
### Path actions in the camp
- Rensei [PA Charm] a Crane sentry: "The general wants to see me. Urgently. About the lady."
- [IF natsuko_in_party] Natsuko [PA Sumai] a Crab sentry: "Shh. Nap time." [END]
[BATTLE b_camp_sentries_b]
### Daidoji Uji's tent
(Young, swarthy, coiled like a spring: DAIDOJI UJI, half-dressed, already buckling armour.)
DAIDOJI UJI: The Crab are coming at dawn. I've been told. We strike first.
> CHOICE "Uji"
  - "Wake him with argument." (Etiquette) → [SET uji_won_by argument]
      RENSEI: Who told you, my lord? (beat) A woman? At night? In your tent?
      DAIDOJI UJI: (slowing) …How do you—
  - [IF tadaka_lie_heard] "Tell him about Tadaka." → [SET uji_won_by tadaka] (stronger)
      RENSEI: The Lion your general cut down. He caught her in a lie about a dead uncle. Minutes later he was dead.
      DAIDOJI UJI: (very still) …Moteuchi died in the south. Of fever. I was at his funeral.
(Across the meadow, HIDA YAKAMO — young, blunt, impatient — is already half-persuaded.)
[IF natsuko_in_party]
HIDA YAKAMO: An outside hand? On both sides? (spits) Fine. If you're wrong, scout, you're cleaning latrines.
NATSUKO: I've been threatened with latrines before. I'm still here.
[ELSE]
HIDA YAKAMO: (reading Goro's note) An outside hand. Hm. (grimly) Somebody playing us like a drum.
[END]

[SAVE] (the foot of the ridge, before dawn)

## S05 — The Iron Cranes (BOSS)
MAP: `border_camp_2` (dawn, the Crane lines) · TRIGGER: after S04
(Dawn. Three Daidoji generals ride out ahead of their lines, eyes glassy, swords drawn. Behind them on the ridge,
in white: Miyako, watching.)
DAIDOJI GENERAL (charmed): She said the Crab would come at dawn. She said only I could save her.
RENSEI: (Iaijutsu: Focus) She says that to everyone, general. I heard her say it twice last night.
[BATTLE b_boss_iron_cranes]
### GIMMICK — charmed generals
"Each general is held by **her charm**. Damage *feeds* her hold — she heals them between turns.
**Break them (Suki) to free them** instead."
### Barks
- A general heals: DOJI MIYAKO (from the ridge): "Don't let them hurt you, my love."
- Freed general 1: DAIDOJI GENERAL: "…Why am I holding my sword? Who — who was I fighting?"
- Freed general 2: "Gods. My wife. Where's my wife?" [IF eriko_close] DAIDOJI ERIKO: "Right here, you fool." [END]
- Freed general 3 → victory.
- (Sayo present, cold-water Remedy): SAYO: "Wakey wakey, general!"

## S06 — Six Doors
MAP: `miyako_chamber` · TRIGGER: after the boss
(Miyako's chamber in the port castle. Empty — then not. She sits in the window, radiant, unhurried. Six floating
doorways of light open around the room. In each, a sleeping child.)
(In Rensei's: his little cousins at the Kakita estate. [IF natsuko_in_party AND nezumi_friends] In Natsuko's: Squeak
and the young nezumi in their dry cave. [ELSE IF natsuko_in_party] In Natsuko's: Sachiko and Ryoichi, asleep in the
Wall barracks. [END])
DOJI MIYAKO: Serve, and they live. Refuse, and — well. Doors open both ways.
DOJI MIYAKO: I bargain honestly, you know. Ask anyone I've owned.
[IF natsuko_in_party]
NATSUKO and RENSEI: (together) No.
DOJI MIYAKO: (delighted) Two of you in one night! I *do* love a pair.
[ELSE]
RENSEI: (hand on his sword; his left foot does not hesitate) No.
DOJI MIYAKO: (amused) A Crane who says no to me. How *novel*.
[END]
(She laughs. The doors close. The children are gone — only images. She stands, and the window fills with smoke, and
she is a white bird, and then nothing.)
[SET same_woman_proven]
RENSEI: (at the empty window) …Not two women. One.

## S07 — Ending
MAP: `garden_under_shadow` · TRIGGER: auto
(Confessions. The most compromised Crane general kneels for seppuku at dawn. On the Crab side, the old wrestler
general HIDA CHUTO walks off into the Shadowlands "to look for Hida".)
LADY SANAE: (dictating to a clerk) "A Scorpion provocateur, operating on both sides of the border, has been exposed."
RENSEI: (low) …There *was* a Scorpion. At Goroso's castle. Bayushi Depura.
LADY SANAE: Then my report is accurate. (beat) Merely incomplete.
[IF natsuko_in_party]
(The land-bridge at low tide. Natsuko and Rensei, both exhausted.)
NATSUKO: (handing him a scrap of map) My father's. A copy of one corner. For luck.
RENSEI: (handing her a small sake cup, Kakita-made) For the scalding sake. So you never have to drink from a Crab cup again.
NATSUKO: (holding it, almost smiling) You're very strange for a Crane.
RENSEI: You're very polite for a Crab.
NATSUKO: Don't tell anyone.
RENSEI: (bowing) I never gossip. Ask anyone at the Academy.
[ELSE]
HIRUMA GORO: (on the land-bridge) Next time, Crane, you wrestle the generals. I'll drink the tea.
[IF NOT goro recruited] [GUEST +Hiruma Goro (joins the roster)] [END]
[END]
[CHAPTER COMPLETE]
### Chapter complete card
**"The Iron Cranes" — complete.**
Journal: *Two women seduced two armies — and they were never two women. Rensei freed three generals, refused a
bargain of open doors, and learned that the woman behind it all is a Doji.*
[UNLOCK] Rank 2 for Rensei (*The Sudden Strike*) if not already reached.

---
## Travel Banter unlocked
### TB-crossroads1 "Two Faces, One Woman" (Rensei + Natsuko; requires camp_split together)
NATSUKO: She looked right at me in the Crab hall. Smiled.
RENSEI: She looked right at me in the garden.
NATSUKO: Same smile?
RENSEI: (pause) …Exactly the same. To the hair.
NATSUKO: That's what gets me. She didn't even bother to change the smile.
RENSEI: Because she doesn't think we're worth the effort.
NATSUKO: (grim) Good. Let her keep thinking that.
