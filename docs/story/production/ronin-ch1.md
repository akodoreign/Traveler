# PRODUCTION — Ronin Ch1 · "What's Eating the Eta"

**Traveler:** Sayo · **Lv** 1–8 · **Outline:** `scripts/ronin-ch1-whats-eating-the-eta.md`
**Flags set:** `ronin_school_first` (warrior/duelist/yojimbo), `sono_link`, `monk_riddle`, `loot_returned`,
`hut_burned`
**Maps:** `river_barge`, `cakon_docks`, `cakon_market`, `cakon_alley`, `cakon_gate`, `eta_village`, `canal_bridge`,
`paddy_edge`, `tomie_hut`
**Battles:** `b_dock_thugs` (tutorial), `b_alley_ambush`, `b_tengu_bridge` (knock-off mini-boss), `b_bakemono`,
`b_boss_tomie_cho` (3 forms)
**Guest:** Hiro (S04)
**Fit conversions:** the caste gate is a solo cutscene walk; the tengu knock-off is a mini-boss gimmick; the
weretiger's 3 forms are standard boss phases.
**Storyboard:** `storyboards/ronin-ch1.md` (Cakon is a Mantis-ferry port).

### RECRUIT VARIANT (Sayo is not the starter)
**Join point:** `cakon_market`, during Kagemaro's call for "bold and honourable citizens". Sayo answers (S02 as
written); afterwards, talk to her.
SAYO: (chewing a rice ball) You lot look bold. Are you honourable? (beat) Doesn't matter. I'm not either.
SAYO: Sayo. Ronin's daughter. Herbalist. Something's eating people in the village outside the walls, and nobody here
will go and look.
SAYO: I'm going to look. You can come. You probably can't come all the way. (cheerfully) I'll explain at the bridge.
> CHOICE "Travel with Sayo?" → Yes: **Memory** (S01: the barge, Ume-baa, the ginseng, jumping onto the docks; **the
  first-school choice is still asked**; the dock fight shown without battle) → resume at S03.
→ No: she shrugs and heads for the river gate; her chapter icon appears in the market.

---

## S01 — Born on the Water
MAP: `river_barge` (memory, sepia) → `cakon_docks` · TRIGGER: new game, Sayo chosen
NARRATION: Some people are born under a lord's banner. Some are born under a roof.
NARRATION: Sayo was born on a rice barge, under nobody at all.
(Sepia memory: a riverbank, nine-year-old Sayo with a basket, following an old woman in eta grey — UME-BAA — picking
herbs.)
YOUNG SAYO: Why won't the town doctor teach me?
UME-BAA: Because you're a ronin's daughter, child. And because he's a fool. Here — this one. Smell it.
YOUNG SAYO: (sniffing) Ugh!
UME-BAA: That's ginseng. It smells like dirt because it remembers the dirt. Good medicine always remembers where it came from.
YOUNG SAYO: The samurai say you're unclean. Because you touch the dead.
UME-BAA: (laughing) Child. Everybody touches the dead eventually. We just do it with clean hands.
(The memory fades into the present. Sayo — eighteen, straw hat, basket of herbs, a plain katana — jumps from the
barge onto the docks of a big Crane river city before it's tied up.)
BARGEMAN: Oi! Wait till we dock!
SAYO: (landing, grinning) I did. It just wasn't your dock yet.
> CHOICE "Who taught you to fight?" (first ronin school)
  - "My mother. She never let anyone hit first." → Warrior (*The Wolf's Technique*) [SET ronin_school_first warrior]
  - "The river. You learn to be faster than the current." → Duelist (*The Wind Technique*) [SET ronin_school_first duelist]
  - "Nobody. I just stood in front of people who needed it." → Yojimbo (*The Way of Sacrifice*) [SET ronin_school_first yojimbo]
(Dockside: two thugs shove a fish-seller into the water.)
[BATTLE b_dock_thugs]
### TUTORIAL
- T1: "**Remedy** — Sayo's Talent. Mix a **base** herb with a **catalyst** to make a remedy."
- T2: "Try **Ginseng + Rice wine**: a strong heal."
- T3: "**Katana** attacks gain extra damage for every VP you spend."
(The fish-seller climbs out, dripping.)
FISH-SELLER: Thank you, miss! Who are you?
SAYO: Nobody in particular. (handing her a herb) Chew this. You swallowed half the river.
[SAVE]

## S02 — Silver for the Musicians
MAP: `cakon_market` · TRIGGER: walk into the market
NARRATION: Cakon. A Crane river city. Very clean on top. Very busy underneath.
(Street musicians. A young noble with a fresh black eye throws a fistful of silver at them — too much — then steps
behind a stall, embarrassed: MIBU KAGEMARO.)
MIBU KAGEMARO: (to the crowd, too loudly) I seek bold and honourable citizens! For a… delicate task!
(Nobody moves. Sayo walks up, chewing a rice ball.)
SAYO: I'm a citizen. Mostly bold.
MIBU KAGEMARO: You are… a ronin?
SAYO: Ronin's daughter. Even worse, my lord. I don't even have a lord to have lost.
MIBU KAGEMARO: (lowering his voice) A murderer — a mercenary named Daigoro — killed my cousin, Mibu Ieko, in a brawl.
MIBU KAGEMARO: Over a poet. O-Sode, of the House of Tranquillity. (wincing) It was a very stupid brawl.
MIBU KAGEMARO: The judge — Sono Kentanaga, of a rival family — added a clause.
MIBU KAGEMARO: If Daigoro isn't executed in three days, he walks free.
SAYO: So execute him.
MIBU KAGEMARO: No eta will do it. Something has been eating them. In their village. At night.
MIBU KAGEMARO: They believe it's a punishment for their unclean souls. They won't do any work until it stops.
SAYO: Couldn't you do the execution yourself?
MIBU KAGEMARO: (recoiling) I would become *eta*!
SAYO: (cheerfully) There. Now you know what you're paying me for.
MIBU KAGEMARO: (beat; then, almost smiling) …Yes. I suppose I do.
MIBU KAGEMARO: I can't be seen to be involved. If anyone asks, you've never met me.
SAYO: My lord, nobody ever asks a ronin girl anything.
### Town NPCs — `cakon_market`
| NPC | Default | Info | Path action |
|---|---|---|---|
| Musician | "He threw silver! Then he hid behind the radishes!" | — | — |
| House of Tranquillity doorman | "O-Sode sees no one. No one." | *Eavesdrop:* "O-Sode cries every night. She liked Ieko." | — |
| Sono servant | "My master is a very fair judge. Very fair." | *Discern:* "Nervous; carries a purse heavier than his wages." | **Pilfer:** the purse → a chit "for Daigoro's men" |
| Herb seller | "Ginseng! Rhubarb! Mystery root!" | — | *Barter:* Remedy ingredients |
| Guard | "Ronin? Move along." | — | *Bless:* he prays for his sick daughter → no toll at the river gate later |
| Street kid | "Got any rice balls? Got any *more* rice balls?" | — | *Charm:* follows ("Pickpocket's Eye": drops +, 1 battle) |
| Crane duellist (docks) | "A ronin with a katana. How quaint." | — | *Duel* (Iaijutsu 1): Glory +1 |
| Bargeman | "Wait till we dock, I said!" | — | *Sumai:* "The Sono's barge goes upriver every night. Empty." |

## S03 — Alley, Gate, Beggar
MAP: `cakon_alley`, `cakon_gate` · TRIGGER: head for the river gate
### S03a — the ambush
(A narrow alley. A ronin with a scarred lip, TETSUO, and a "merchant" with a Lion's posture block both ends.)
TETSUO: You're the girl Mibu's paying. Go home, ronin. This isn't your fight.
SAYO: It's nobody's fight. That's why I'm here.
[BATTLE b_alley_ambush]
(After: Tetsuo runs. The "merchant" drops his disguise — a Lion samurai — and flees too.)
### TUTORIAL — Path Action: Pilfer
"**Pilfer** — take an item an NPC carries. Your chance depends on **Sleight of Hand**.
It's a **Low Skill**: get caught in town and you lose Honor. (Sayo has very little to lose.)"
(If the Sono servant's purse was pilfered:) SAYO: (reading the chit) "Payment, Daigoro's band." From the Sono house.
SAYO: The judge's family is paying the murderer's friends. (pocketing it) Interesting.
[SET sono_link]
### S03b — the beggar-monk (optional)
(At the river gate a stray dog snaps at an old beggar-monk.)
SAYO: (shooing it with a rice ball) Here, here. Go eat this instead.
BEGGAR-MONK: (gap-toothed) Kind child. A riddle for you, in thanks.
BEGGAR-MONK: "Under the right arm of the strong is the gift. Between two red stones, under the old cedar."
SAYO: Strong what?
BEGGAR-MONK: (wandering off) Strong cedar, child. What else is strong?
[SET monk_riddle] → side quest: buried treasure (cedar between two red stones, `paddy_edge`)

## S04 — The Village Outside the Walls (caste gate)
MAP: `eta_village` · TRIGGER: cross the river gate
[IF samurai in party]
(At the bridge to the eta village, the samurai stop.)
(Each one gets a line: RENSEI: "I… cannot. My family—" / SHIZUE: "My uncle would never—" / NATSUKO: "I'll wait.
I'll be watching the bridge.")
SAYO: (patting a shoulder) It's fine. Hold my hat. (beat) No, hold the bridge. I'll be back.
[END]
### Solo walk (fit conversion: cutscene + a short solo walk)
(The village: low houses, an all-faiths shrine built from salvaged lumber, frightened faces in doorways.)
ETA WOMAN: (gasping) Sayo? Little Sayo? Ume-baa's girl?
SAYO: Auntie Fumi! (hugging her) You're thinner.
ETA WOMAN: We're all thinner. It comes at night. Took the Koyama boy last week. Took the old ferryman.
(A huge, toothless man with a rusty no-dachi sits by the shrine, grinding the blade on a stone: HIRO.)
HIRO: (not looking up) Ume's girl. You came.
SAYO: Hiro! You're still alive!
HIRO: It took my brother from his bed. I fought it. It went away. (showing three scars on his arm) It'll come back.
HIRO: (quietly) He didn't scream, my brother. Good men don't scream when they're being punished.
SAYO: (furious, quiet) Then it's not punishment. It's dinner.
SAYO: And I'm going to spoil its appetite.
HIRO: (a long look; then he stands, and he is enormous) …I'll carry the sword.
[GUEST +Hiro] (skill "No-dachi Sweep": hits all enemies, 2 uses)
(By the shrine fire sits a quiet young woman. SAYO: "Akari? You're better!" AKARI: (very quietly, not looking away
from the flames) "The fire talks when it's quiet. Don't tell anyone." — a seed for Ronin Ch4.)
[SAVE]

## S05 — The Tengu Bridge (mini-boss)
MAP: `canal_bridge` · TRIGGER: follow the blood-trail out of the village
[IF samurai in party] (The samurai come round by the paddy road and rejoin here.) ALLY: "We went round. It's a long
way round." (beat) "That's sort of the point, isn't it." [END]
(A single log over an irrigation canal. On it, two crow-headed tengu fence with sticks, cawing with laughter.)
CROW-TENGU A: Cross, wave-girl! Cross with *dignity*!
CROW-TENGU B: And be laughed at! Caw!
SAYO: (already on her hands and knees, crawling along the log) I've been laughed at by better birds.
CROW-TENGU A: (outraged) She's *crawling*!
CROW-TENGU B: That's cheating!
[BATTLE b_tengu_bridge]
### GIMMICK — knock-off
"Heavy hits and Knockdowns **knock a fighter off the log**: they're out for 2 turns, soaked."
### Barks
- **Compliment** command (Etiquette): SAYO: "Your feathers are *very* glossy." → CROW-TENGU: "…They are, aren't
  they." (loses its turn preening)
- Sayo knocked off: SAYO: (spluttering in the canal) "Fine! I'm wet now! I'm *angrier*!"
- Hiro knocked off: (a huge splash; both tengu are soaked too)
(The tengu flap off, sulking. One drops a black feather.)
[ITEM +Tengu Feather (accessory: +Speed)]

## S06 — Goblins With Baskets
MAP: `paddy_edge` · TRIGGER: on the trail
(Six goblins with baskets of stolen pilgrim offerings: coins, charms, paper prayers.)
BAKEMONO: Shinies! Ours! Go away, meat!
[BATTLE b_bakemono]
(Pilfer works mid-battle on the baskets.)
> CHOICE "The pilgrims' loot"
  - "Return it to the shrine." → [SET loot_returned] (Honor +1; the eta village shrine gets new charms)
  - "Keep it." → (+money; Honor −1)
[IF monk_riddle] (Near here: an old cedar between two red stones. Dig → **Grandmother Cedar's Gift**: Jade-handled
knife.) [END]
[SAVE] (a wayside Jizo at the paddy edge)

## S07 — Tomie Cho (BOSS)
MAP: `tomie_hut` (dusk) · TRIGGER: the trail ends at a mud hut
(A mud hut at the edge of the paddies. Smoke from the chimney. An old woman at the door, smiling, a teapot in her hands: TOMIE CHO.)
TOMIE CHO: Visitors! Come in, come in. You smell of herbs, child.
TOMIE CHO: Ume's girl, aren't you? She always smelled of herbs too.
SAYO: (not moving from the threshold) You knew Ume-baa.
TOMIE CHO: I knew everyone in that village. (pouring tea) I've been *visiting* them.
(Her smile widens. And widens. Her teeth are not an old woman's teeth.)
HIRO: (raising the no-dachi) …It's her.
TOMIE CHO: (the voice deepening into a purr) My family drank from the wrong well, child. Three hundred years ago.
TOMIE CHO: And now I'm too old to catch rabbits. The eta don't run very fast. They think they deserve it.
SAYO: (drawing) They don't. Nobody does. Least of all from *you*.
[BATTLE b_boss_tomie_cho]
### Phases
- **Form 1 — the old woman** (inside the hut: cover = high evasion). Prompt: "**Fire** will flush her out."
  - Using Hanabi Remedy, or the "Torch the Hut" command: [SET hut_burned] → phase 2 starts at once.
  - TOMIE CHO: "My house! You little — !"
- **Form 2 — the hybrid**: claw combos; a Terror roar. TOMIE CHO: "RUN, wave-girl! Run like the eta run!"
  - SAYO: "I was born on a river. I don't run. I *drift*."
- **Form 3 — the tiger**: fast; Resolve 9. Weak: Fire, Yari, Yumi.
  - **Hiro**'s No-dachi Sweep does double damage. HIRO: "For my brother."
(Victory. The tiger falls. For a moment it is an old woman again, very small in the ash.)
TOMIE CHO: (fading) …It was such a long time to be hungry.
SAYO: (kneeling, closing her eyes, quietly) I know. (beat) It still wasn't theirs to pay for.

## S08 — Clean Hands
MAP: `eta_village` → `cakon_market` · TRIGGER: after the boss
(The eta return to work. On the third day, at the very edge of the judge's clause, Hiro walks to the execution
ground. His no-dachi has been cleaned and sharpened all night. Sayo watches from the crowd, hat down.)
(The execution happens off-screen: a single sound. The crowd exhales. The law is satisfied.)
(The market. Kagemaro, at a careful distance, does not quite look at her.)
MIBU KAGEMARO: I can't thank you in public.
SAYO: I know.
MIBU KAGEMARO: I owe you giri. A debt. I'll never be able to be seen paying it.
SAYO: (grinning) Throw some silver to the musicians. I'll know what it means.
[IF sono_link]
SAYO: (handing him the chit, low) One more thing. Your judge's family paid Daigoro's friends to slow the hunt.
MIBU KAGEMARO: (reading; his face hardens) …The Sono. (beat) Thank you. That debt I *can* repay. Quietly.
[END]
(Kagemaro walks away and throws a fistful of silver at the musicians. They play a very cheerful song.)
(Epilogue: the eta village at night. Hiro sits by the shrine, rubbing the three claw marks on his arm when he thinks
no one is watching. They are a little redder than they were.)
[CHAPTER COMPLETE]
### Chapter complete card
**"What's Eating the Eta" — complete.**
Journal: *A noble with a black eye, a clause, and a village that believed it deserved to be eaten. Sayo walked where
no samurai would, and an old tiger went hungry at last.*

---
## Travel Banter unlocked by Ronin Ch1
### TB-ronin1-a "Hold My Hat" (Sayo + Rensei)
RENSEI: I'm sorry I didn't cross the bridge.
SAYO: You held it. That's something.
RENSEI: It's… not very much.
SAYO: It's more than most samurai would've done. Most would've walked away and told the story differently later.
RENSEI: (pause) …I'll tell it exactly as it happened.
SAYO: (smiling) Then you're already braver than the story.
### TB-ronin1-b "Clean Hands" (Sayo + Haruki)
HARUKI: Ume-baa said you touch the dead with clean hands.
SAYO: She said *everyone* touches the dead eventually. The eta just admit it.
HARUKI: (looking at his own hands) …I think I'd like to meet her.
SAYO: She'd make you eat something that smells like dirt.
HARUKI: (quietly) That sounds like being looked after.
