# PRODUCTION — Lion Ch2 · "Shadow of a Doubt"

**Traveler:** Akodo Shizue · **Lv** 20–25 · **Outline:** `scripts/lion-ch2-shadow-of-a-doubt.md` (the template)
**Fit conversions applied:**
- The **11-week calendar** is **4 fixed beats**, each followed by an empty spot in the castle (the escalation
  clock):
  - Beat 1: painting + bracket → the "Duty" plaque goes missing
  - Beat 2: history dinner → the Sorrow's Path banner goes missing
  - Beat 3: debate + the sword → Kafu's sword goes missing
  - Beat 4: dance + arrest → the seal goes missing
- Painting and dance are dialogue choices; the bracket is 3 Duel battles.

**Flags set:** `met_nishi`, `painting_answer`, `bracket_result`, `heard_history`, `toturi_knows_name`,
`atsuko_promise` (none / honest / lie), `kafu_joins`
**Maps:** `shiro_akodo` (Hall of Honors, Central/North/South Dojo, Central Garden, Hall of Akodo, library, kitchens,
stables, cells; + a castle-town screen with the swordsmith's shed), `south_dojo_night`, `south_dojo_under` (crawlspace
dungeon, later the oni's lair), route `lion_winter_road` · **Storyboard:** `storyboards/lion-ch2.md`
**Beat trigger:** a beat begins when the player talks to the hostess in the Hall of Honors, or rests at the guest
quarters once its prerequisites are met. Beat 4 also requires S06. A bracket loss is non-fatal (README §3c): the
bracket ends, and Yutaka still presents the Jade Tanto "for spirit".
**Battles:** `b_bracket_1/2/3` (Duel), `b_fear_shades`, `b_boss_ianwa`
**Guest:** Moto Benjiro (S09)

---

## S01 — The Far End of the Hall
MAP: `shiro_akodo` (Hall of Honors) · TRIGGER: arrive
NARRATION: Shiro Akodo. Winter Court. Three hundred samurai, and one of them so junior the servants pour her tea last.
(Ranks of kneeling samurai under ancestor portraits. Far up the hall: AKODO TOTURI, quiet, watchful. The camera
slides past the great names and stops at the last cushion: Shizue.)
KAIU GESSHIN: (rising, a magnificent cold orator) The Crab were asked for their opinion of the Akodo.
KAIU GESSHIN: I have looked. My verdict is… sufficient.
(A ripple through the hall. Uncle Hiruto doesn't move a muscle.)
SHIZUE: (aside) "Sufficient." From a Crab, that's a love poem.
(The corridor afterwards. A woman passes, stops, turns back: AKODO NISHI, bright-eyed, warm, with a strategist's
ink-stained fingers.)
AKODO NISHI: You. The girl who sacrificed three stones on the left edge to win the centre. Shizue, wasn't it?
SHIZUE: (bowing far too low) Nishi-sama remembers a game from four summers ago?
AKODO NISHI: I remember the moves that surprised me. There haven't been many.
AKODO NISHI: (a flicker of sadness) Come to the North Dojo some evening. I'd like an opponent who isn't trying to flatter me.
(Behind Nishi, a man waits for her: AKODO KAFU, Toturi's trusted advisor. He looks at Nishi a moment too long, then
away.)
[SET met_nishi]
[SAVE]

## S02 — The Castle (hub)
MAP: `shiro_akodo` · TRIGGER: explore between beats
### Town NPCs — Shiro Akodo
| NPC | Default line | Info | Path action |
|---|---|---|---|
| Akodo Nishi | "My wedding is in eleven weeks. Everyone keeps telling me." | *Discern:* "Loves someone she can't marry." | **Duel** (go game, North Dojo) → "Kafu taught me to play." |
| Akodo Kafu | "Court is a battlefield with better tea." | *Discern* (Beat 2+): "Hasn't slept in days. Something speaks to him at night." | — |
| Kaiu Yutaka (the groom) | "I paint the Wall. With birds in it." | *Discern:* "Knows Nishi doesn't love him. Kind about it." | — |
| Kaiu Mami (siege mistress) | "Watch — this paper crane is the Kaiu Wall. This one is your castle. Now it's on fire." | — | — |
| **Daidoji Atsuko** (Crane guest) | "I'm only reading. Is that a crime here?" | *Discern:* "Perfect memory. Has read only the anti-Crane war plans." | **Charm** (Rensei): she admits she's a spy, "but not a thief" |
| **Moto Benjiro** (stables) | "The Crab laugh at me. Let them." | *Discern:* "Can feel a Taint in the castle. Can't find it." | — |
| Kitchen girl | "The South Dojo is cold even with the braziers lit." | — | **Eavesdrop:** "Voices from the South Dojo at night. Two voices. One is Kafu-sama's." |
| Matsu bushi (castle town) | "Lions don't read. Lions *win*." | — | **Sumai:** "The Crane girl reads only the war shelf." |
| Widow (shrine) | "My husband's portrait hangs in the Hall. He looks bored." | — | **Bless:** follows ("Ancestor's Vigil": Terror resist, 1 battle) |
| Ikoma bard (castle town) | "Every song is true, if you sing it loudly." | — | **Barter:** "The Ballad of Matsu Joruri" (a second strong line for the Beat 2 history) |
| Stable girl | "Benjiro-sama paints his face every morning." | — | **Pilfer:** spare white paint (return it to Benjiro after S08 → Death Trance +1 use) |

## S03 — Beat 1: "Tranquillity" and "The Bracket"
MAP: `shiro_akodo` (Central Garden → Central Dojo) · TRIGGER: Beat 1
### Painting contest (dialogue choice)
HOSTESS: The theme is *tranquillity*. Not the garden — what the garden *makes you feel*.
> CHOICE "What will you paint?" [SET painting_answer]
  - "A single snowflake on a sword blade." → (best) the judges murmur; **Scroll of Acclaim** (+Glory)
  - "A sleeping lion." → (good) polite approval
  - "The garden, very accurately." → (literal; a judge sighs)
  - "Nishi-sama's go stones, mid-game." → (good) NISHI: (quietly) "…That's not tranquil at all. It's lovely."
(Kaiu Yutaka shows his painting: a Wall battle; below it a mother bird feeding chicks in a nest.)
KAIU YUTAKA: The Wall is the noise. The nest is what the noise is for.
SHIZUE: Then your painting isn't of the Wall at all.
KAIU YUTAKA: (pleased, embarrassed) Don't tell the judges.
### The bracket (3 Duel battles)
HOSTESS: The bokken tournament! Every samurai of the court may enter.
[BATTLE b_bracket_1] (an Ikoma bard — talks too much) IKOMA: "Did you know my grandfather—" (he's down)
[BATTLE b_bracket_2] (a Matsu — all fury) MATSU: "RAAH!" SHIZUE: "…Ah." (she steps aside; the Matsu flies past)
[BATTLE b_bracket_3] — final vs **Kaiu Yutaka**, who hasn't moved his feet once
SHIZUE: (internal) He wants me to come to him. Every Crab wants you to come to them.
> CHOICE (battle tactic hint, shown before the final)
  - "Wait him out." (Defend + Read the Field)
  - "Feint, then strike." (Feint → Heavy Blow)
  - "Command myself." (Talent: act twice)
[SET bracket_result win/lose]
[IF win] (Prize: a **miniature jade-bladed tanto**.) KAIU YUTAKA: "You moved me. Nobody moves me." [END]
[IF lose] (Prize: still awarded — "for spirit" — the jade tanto.) KAIU YUTAKA: "You made me move my left foot. Take it." [END]
(Up in the high seats, Toturi says two words to his karo. The karo writes something down.)
### Escalation — after Beat 1
(The Central Dojo. A pale rectangle on the wall where a painting hung. Servants whisper.)
SERVANT: The "Duty" plaque. Gone. In the night. Who would steal *Duty*?
COURTIER: The Crane, of course. (looking at Atsuko)
[ITEM +Jade Tanto]
[SAVE]

## S04 — Beat 2: "To Know a Man's Ancestors"
MAP: `shiro_akodo` (Hall of Honors, night) · TRIGGER: Beat 2
HOSTESS: Tonight, histories. To know a man's ancestors is to know the man.
(Guests rise in turn. Then Kafu.)
AKODO KAFU: I'll tell of an Akodo who loved a Matsu woman, long ago.
AKODO KAFU: His lord commanded him to betray her, for the clan's sake. He obeyed.
AKODO KAFU: The story says he never wept, because duty does not weep.
AKODO KAFU: (very quiet; the hall silent) The story is wrong. He wept every night for thirty years.
AKODO KAFU: He simply did it where no one could see.
(Nishi sets her cup down very carefully.)
[SET heard_history]
> CHOICE "Your history" (Shizue tells one)
  - "Matsu Joruri at Sorrow's Path." → (Glory +1; Toturi glances up)
  - "My uncle's quietest victory." → NISHI smiles
  - "The day my cousin started a war." → (a hush; honest; Honor +1)
(Prize: **a jade-headed flesh-cutter arrow**.)
### Escalation — after Beat 2
(The Hall of Akodo. Gasps. The great trophy of the Lion — the Crane banner of Sorrow's Path — is gone from its wall.)
LION GENERAL: The Crane spy! Arrest her!
TOTURI: (from the doorway, softly) Not without proof.
[ITEM +Jade Flesh-Cutter Arrow]

## S05 — Beat 3: "The Bushido Debate" and the Sword
MAP: `shiro_akodo` (Hall of Honors) · TRIGGER: Beat 3
### SET-PIECE PREVIEW — the debate UI (low stakes; the finale's system)
HOSTESS: The debate. Each speaker defends a tenet.
MATSU SPEAKER: Honour is what our lord says it is. The lord defines it. We obey.
> DEBATE "Honor" — choose your rebuttal (evidence from Ch1 flags)
  - "Whose honour was it at Sorrow's Path, when both armies called themselves righteous?" → **strong**
  - [IF climax_route A/B/C from Ch1] "My uncle told me to find the truth, even a Lion's truth." → **strong**
  - "Honour is following orders well." → weak
SHIZUE: (strong) Honour isn't a banner someone can steal from a wall.
(Silence. Then, from the high seats, for the first time:)
AKODO TOTURI: Who is that?
KARO: Akodo Hiruto's niece, my lord. A junior strategist.
AKODO TOTURI: (that is all he says)
[SET toturi_knows_name] (Prize: an illuminated *Akodo's Leadership*: Battle skill +1)
### The sword
(Days later. Kafu no longer wears his ancestral katana.)
AKODO KAFU: (to a courtier) Rewrapping. The hilt was worn.
(The swordsmith's shed.)
SWORDSMITH: Rewrapped? Kafu-sama's blade? Lady, if that sword came into my shed, I'd bow to it for an hour first.
SWORDSMITH: It hasn't been here.

## S06 — The South Dojo at Night
MAP: `south_dojo_night` · TRIGGER: after Beat 3 (optional night visit; required before Beat 4)
(Cold. Braziers guttering. A wet trail across the floorboards that hisses where it touches the wood.)
SHIZUE: (crouching) Something crawled here. Something heavy. And frightened.
[BATTLE b_fear_shades]
(The trail goes under the floor. A loose board → `south_dojo_under`: a 2-screen crawlspace and old drain, with Fear
Shade encounters. At the far end, a floor-hatch comes up behind the inner screen.)
### Tutorial — Terror
"**Terror** may make an ally lose their turn and stop them Boosting. **Jade gear** and courage skills resist it."
(After: a voice, very faint, from behind the dojo's inner screen — Kafu's, and another, many voices layered.)
AKODO KAFU: (pleading) …I've given you everything. Everything. Please.
OTHER VOICE: …Not everything. Not yet.
[SAVE]

## S07 — Beat 4: The Dance and the Seal
MAP: `shiro_akodo` (Hall of Honors) · TRIGGER: Beat 4
### Dance (dialogue choice)
> CHOICE "Who will you partner?"
  - Kaiu Yutaka → YUTAKA: "I dance like a wall." SHIZUE: "Then I'll dance like a siege."
  - Daidoji Atsuko → ATSUKO: "A Lion asking a Crane spy to dance. They'll talk." SHIZUE: "Let them."
  - Moto Benjiro → BENJIRO: "No one ever asks me." (he dances surprisingly well)
(Prize either way: **jade-inlaid war fans** — party accessory, +resist Terror.)
(Nishi dances with her betrothed, smiling the whole way through. Her smile breaks only once — when she passes Kafu.)
### Escalation — the seal
(The next morning. Toturi strides into the hall, his karo behind him, dragging Daidoji Atsuko.)
AKODO TOTURI: My seal. My mon. Taken from my own chamber.
KARO: The Crane was seen in the corridor, my lord.
AKODO TOTURI: (to Shizue, surprisingly) Akodo Shizue. You have a week. Clear her or confirm her.
### Clue chain — the missing objects (Shizue lays them out in her room: a scarf, a flower, *Duty*, the banner, the sword, letters, the seal)
SHIZUE: (slowly) A scarf from a friend. A flower from the garden. Duty. The banner. His sword. The seal.
SHIZUE: …They're all Kafu's. Everything Kafu loves, in order. Someone is taking his life apart one piece at a time.
### Atsuko in the cells
DAIDOJI ATSUKO: (calm) I'll tell you exactly one true thing, Lion, because you came yourself instead of sending a servant.
DAIDOJI ATSUKO: I didn't take the seal. I did read your war plans.
DAIDOJI ATSUKO: Both are true. Only one is a crime your Champion can prove.
> CHOICE "Atsuko"
  - "I promise nothing." → [SET atsuko_promise none]
  - "I'll clear you of the theft. Only the theft." → [SET atsuko_promise honest] (Ch4 payoff)
  - "I'll get you free." → [SET atsuko_promise lie] (Honor −1)
[SAVE]

## S08 — Something With No Name Yet
MAP: `shiro_akodo` (stables) · TRIGGER: after S07
(MOTO BENJIRO, a white death-mask painted on his face, saddling a horse to ride into the Shadowlands to die well.)
MOTO BENJIRO: The Crab laugh at me because my family rides toward death instead of away.
MOTO BENJIRO: But I know the smell of it, Lion. It's in this castle.
MOTO BENJIRO: It's been eating someone for weeks. Slowly. The way a coward eats.
SHIZUE: Kafu-sama.
MOTO BENJIRO: (not surprised) Then we must hurry.
MOTO BENJIRO: A coward, once it is fat enough, becomes brave.
[GUEST +Moto Benjiro] (skills: Death Trance — party immune to Terror, 1 use; Oni-Bane — big damage vs oni, 2 uses)

## S09 — The Coward's Feast (BOSS)
MAP: `south_dojo_night` (the night before the wedding) · TRIGGER: go
(Kafu kneels in the dark. Before him: a slug-like thing the size of a horse, a ring of teeth, dripping —
ONI NO IANWA. It has his letters. It's reading them aloud in his own voice.)
ONI NO IANWA: (in Kafu's voice) "My dearest Nishi. If duty were a river, I would drown in it gladly—"
SHIZUE: Stop.
### Talk-down (before the fight)
> CHOICE "Reach Kafu" (one chance each; the right one sets kafu_joins)
  - "Think of Nishi." → AKODO KAFU: (flinching) "I think of nothing else. That's how it eats me."
  - "Remember your duty." → AKODO KAFU: (a bitter laugh) "My duty brought me here."
  - [IF met_nishi AND heard_history] "You told the story of the man who wept. Weep now, where I can see." → [SET kafu_joins]
      AKODO KAFU: (a long breath; then he weeps, openly) …Thirty years. (rising, drawing his short sword) No more.
[BATTLE b_boss_ianwa] (Kafu fights beside the party if kafu_joins)
### GIMMICK — Ianwa's charm (the chapter's one battle gimmick)
"Ianwa has no attacks of its own. Each turn it **charms** one ally into attacking another.
**Jade** cuts the chance. Benjiro's **Death Trance** blocks it for a round."
### Barks
- Charm: ONI NO IANWA: "You would all give me everything, if I asked politely enough."
- SHIZUE: "Then I'll be rude." (Command)
- **Coward rule:** on its first Suki — ONI NO IANWA: "I will return! I will devour your souls!" (it flees through
  the floor — battle won)
- MOTO BENJIRO: (watching the hole in the floor) "…It's lying. It won't come back. Cowards never do."

## S10 — Epilogue
MAP: `shiro_akodo` · TRIGGER: dawn
[IF kafu_joins]
(Dawn. Kafu asks Toturi's leave for seppuku. Toturi grants it. In the garden, Kafu kneels. He looks past Nishi, who
stands at the edge of the snow, to the mountains.)
AKODO KAFU: You can see all the way to the Spine this morning. (beat) I'd forgotten.
(The screen cuts to white before the blade.)
(The wedding goes ahead at noon. Nishi doesn't cry until evening, alone in the North Dojo — where Shizue finds her,
says nothing, and sets up the go board. They play until morning.)
[ELSE]
(Kafu is taken in chains. Toturi orders his name cut from every record.)
AKODO TOTURI: The Akodo have no son called Kafu. Not any more.
(The wedding goes ahead. In the North Dojo, Shizue sets up the go board. Nishi looks at it, and doesn't play.)
[END]
(The stolen objects are found in the oni's lair beneath the floor — all but one. The plaque "Duty" is never found.)
[IF atsuko_promise honest] DAIDOJI ATSUKO: (released, expelled from court) "You kept your one true thing, Lion. I'll remember." [END]
(A corridor. Toturi passes Shizue without stopping.)
AKODO TOTURI: Akodo Shizue. (a half-step) Again.
[CHAPTER COMPLETE]
### Chapter complete card
**"Shadow of a Doubt" — complete.**
Journal: *A cowardly oni ate a good man one treasure at a time. Shizue found the pattern, armed herself in jade
without knowing why, and made the Lion Champion learn her name.*

---
## Travel Banter unlocked by Lion Ch2
### TB-lion2-a "Go" (Shizue + Haruki)
HARUKI: You played go with her all night?
SHIZUE: Until the candles went out.
HARUKI: Who won?
SHIZUE: Nobody. We stopped counting. (beat) Some games you play so that someone isn't alone.
### TB-lion2-b "Benjiro" (Shizue + Tamotsu)
TAMOTSU: Moto Benjiro rides to the Shadowlands to die well. I've tried three times to talk him out of it.
SHIZUE: And?
TAMOTSU: He bought me sake each time and thanked me for caring. (sighing) It's very hard to argue with a polite man who's already decided.
