# PRODUCTION — Lion Ch3 · "The Deadly Message"

**Traveler:** Akodo Shizue · **Lv** 30–35 · **Outline:** `scripts/lion-ch3-the-deadly-message.md`
**Flags read:** `yachiko_suspected` · **Flags set:** `message_route` (A deliver / B return), `shogen_joined`,
`duelist_spared`, `yachiko_letters`
**Maps:** `shiro_akodo_karo`, `burned_bridge_village`, `sleet_waystation`, `ancestor_shrine`, `mountain_pass_1–2`,
`kaze_no_tani_hermitage`, route `lion_west_road` · **Storyboard:** `storyboards/lion-ch3.md`
**Battles:** `b_bridge_bandit` (Duel), `b_pass_ronin`, `b_shogen_test` (Duel, route A only), `b_boss_miya_killers`
**Guest:** Akodo Ijako

---

## S01 — Three Lines
MAP: `shiro_akodo_karo` · TRIGGER: start
NARRATION: Spring thaw at Shiro Akodo. The snow lets go of the roads, and the war lets go of its patience.
(A small dim office. Toturi's karo, AKODO KAGEHISA — precise, unreadable — holds out a lacquered tube sealed with the Champion's mon.)
AKODO KAGEHISA: For the old man of Kaze-no-Tani. Speak to no one. Go now.
SHIZUE: Yes, Kagehisa-sama.
(That's the whole audience. The screen slides shut.)
(The corridor. Shizue looks at the tube.)
SHIZUE: (to herself) A Rank 1 messenger. Nobody would miss one.
SHIZUE: (beat) …That's why it's me.
[SAVE]

## S02 — The Burned Bridge
MAP: `burned_bridge_village` · TRIGGER: the road west
(A Lion village full of refugees from Crane border raids. A burned bridge; a ford; a bandit chief collecting a toll
from people who have nothing.)
BANDIT CHIEF: A zeni a head to cross, or wade home.
SHIZUE: I'll cross for free. (setting her travel case down) You'll want to challenge me first.
BANDIT CHIEF: (laughing) A Lion girl? Fine!
[PA Duel Bandit Chief] [BATTLE b_bridge_bandit]
BANDIT CHIEF: (after, sitting in the river) …The toll is waived.
(AKODO IJAKO, in her reed-and-mud mask, waits on the far bank as if she'd always been there.)
AKODO IJAKO: The ancestors said you'd come this way.
SHIZUE: The ancestors say a lot of things.
AKODO IJAKO: They said you'd say that too. (falling in beside her) I'm coming.
[GUEST +Akodo Ijako]
### The "courier inspector"
(A neat man in Imperial Miya colours, with papers, blocks the road.)
INSPECTOR: Imperial courier inspection. All sealed messages must be examined. For the Emperor's safety.
> CHOICE "The inspector"
  - "Refuse politely." → SHIZUE: "Forgive me. My orders are my lord's, and my lord's are his." (no penalty)
  - "Refuse rudely." → (Glory −1) SHIZUE: "Get out of my way." INSPECTOR: (noting it down) "…Of course."
(He lets her pass. He watches her go for a long time.)

## S03 — Kill These Messengers
MAP: `sleet_waystation` (night, sleet) · TRIGGER: rest
(A rough waystation. Frozen rain. The lacquer tube, set too near the brazier, cracks with a sound like a twig. The
seal splits. A slip of paper slides half out.)
SHIZUE: (not touching it; then, slowly, touching it) …It's broken. I didn't break it. It's already broken.
(She reads it. Three words in Toturi's own hand.)
SHIZUE: (reading aloud, very quietly) *"Kill these messengers."*
### Party reactions (if present)
- GENDO: "Evidence is testimony. Whose hand? Whose seal? When was it sealed, and by whom?"
- MITSUE: "Burn it. Go home. Say it was lost in the river. Nobody ever checks rivers."
- RENSEI: "Deliver it. That's the point. A messenger who reads the message isn't a messenger anymore."
- NATSUKO: "So someone wants you dead. Welcome to my whole life."
- SAYO: "Is your lord always this rude in letters?"
(Ijako, at the waystation's roadside shrine, lifts her mask and kneels.)
ANCESTOR (through Ijako, an old man's voice): A message is a blade, child. Who holds the hilt?
> CHOICE "The message"
  - "Deliver it anyway." → [SET message_route A]
      SHIZUE: If my lord wants me dead, I'll hear him say it to my face. Or to the old man's.
  - "Turn back. Ask the karo." → [SET message_route B]
      SHIZUE: I'll ask Kagehisa what this means. To his face.
[SAVE]

## S04 — The Pass (dungeon)
MAP: `mountain_pass_1–2` · TRIGGER: either route
(A snowy pass. "Bandits" in good boots.)
RONIN: Hand over the tube, girl, and walk away.
SHIZUE: (Command) Bandits don't usually know about tubes.
[BATTLE b_pass_ronin]
### The defeated (the ronin surrender at low HP — bestiary A2)
- Search their packs (any party) → "A **Miya travel writ**. And a letter to a *Crane* general."
- [PA Discern] or [PA Eavesdrop] adds: "…in the same hand as the writ." (Interrogate is a battle skill, not a path action.)
SHIZUE: (reading the second letter) "…the Lion will attack at the river by the next moon. Prepare."
SHIZUE: (very still) The Lion have no such plan. Someone is telling the Crane we do.
[ITEM +Miya Letters] [SET yachiko_letters]

## S05A — The Old Man of Kaze-no-Tani (route A)
MAP: `kaze_no_tani_hermitage` · TRIGGER: message_route A
(A hermitage clinging to the mountain. A wiry old man splitting firewood in a thin robe, despite the cold:
AKODO SHOGEN.)
AKODO SHOGEN: A Lion girl with a broken seal. (holding out his hand) Give it here.
(He reads. He laughs — a great barking laugh that echoes off the peaks.)
AKODO SHOGEN: Toturi remembers! Ha!
AKODO SHOGEN: It's an old Akodo test, girl. The message says "kill these messengers."
AKODO SHOGEN: I only teach the ones who deliver it *knowing* what it says.
AKODO SHOGEN: (picking up a bokken) But first, show me why I should bother.
[PA Duel Shogen] [BATTLE b_shogen_test]
### Barks
- AKODO SHOGEN (Fury Without End stance): "Pain is a rumour. Ignore it."
- Win or lose honourably:
AKODO SHOGEN: You read it. You came anyway. Why?
SHIZUE: Because if my lord wanted me dead, I wanted to hear him say it to my face.
SHIZUE: And if he didn't, someone else did, and I wanted to know who.
AKODO SHOGEN: (delighted) Ha! He's sent me a strategist. (beat) Finally.
AKODO SHOGEN: I'll come down the mountain. Don't tell anyone I enjoyed it.
[SET shogen_joined]

## S05B — The Karo's Answer (route B)
MAP: `shiro_akodo_karo` · TRIGGER: message_route B
AKODO KAGEHISA: (reading the cracked tube; no expression) You read it.
SHIZUE: It broke. I read it.
AKODO KAGEHISA: You failed the test. (beat) And you came back to ask instead of running. That's loyalty.
AKODO KAGEHISA: The old man stays on his mountain. (handing her a sealed reply-request) Fetch his answer. And take care on the pass.
SHIZUE: (internal) He knows something's waiting on the pass. He's sending me anyway.
[SET shogen_joined false]

## S06 — The Miya Killers (BOSS, both routes)
MAP: `kaze_no_tani_hermitage` gate (A) / `mountain_pass_2` (B) · TRIGGER: after S05
(A tall man in a Seppun-cut kimono with a long, perfect blade, and two archers on the rocks above.)
SEPPUN-TRAINED DUELIST: Our orders are simple, Akodo. The message never arrives.
SHIZUE: It already has.
SEPPUN-TRAINED DUELIST: Then the messenger never returns.
[BATTLE b_boss_miya_killers]
### Barks
- Command on the archers: SHIZUE: "Ijako — the left rock! Now!"
- Akodo Formation vs. arrows: SHIZUE: "Close up. Shields high. Make them waste arrows."
- At 25%, SEPPUN-TRAINED DUELIST: "You don't know who you're fighting."
- SHIZUE: "I'm starting to."
> CHOICE "The duelist"
  - "Spare him." → [SET duelist_spared]
      SEPPUN-TRAINED DUELIST: (kneeling in the snow) …Miya Yachiko. Imperial magistrate. She pays both sides. (bitterly) She pays everyone.
  - "Finish him." → (the letters still name her, with less weight)
[IF message_route B]
(Over the last ridge: the hermitage. The old man reads the karo's request and laughs.)
AKODO SHOGEN: Tell Toturi he still owes me a jar of plum wine.
AKODO SHOGEN: (beat) And tell him his messenger is too polite. She *asked*.
[END]

## S07 — Ending
MAP: `shiro_akodo` (Toturi's study) · TRIGGER: return
(For once, Shizue is admitted past the karo. Toturi reads the Miya letters, the writ, the Crane general's letter. He reads them twice.)
AKODO TOTURI: An Imperial magistrate. Feeding both armies false reports.
SHIZUE: To keep the clans bleeding, my lord. So none of us can challenge the throne.
(A very long silence.)
AKODO TOTURI: Again.
SHIZUE: …My lord?
AKODO TOTURI: (looking up at her, finally) You did it again. Found the hand behind the hand.
[IF shogen_joined] (At the door, old Shogen, muddy and grinning, bows to Toturi like an uncle to a nephew.) AKODO SHOGEN: "Your strategist is rude, Toturi. I like her." [END]
(Elsewhere: Yachiko, recalled "for consultation", rides for the capital under Imperial protection, untouchable.
She'll be at Sorrow's Path.)
[CHAPTER COMPLETE]
### Chapter complete card
**"The Deadly Message" — complete.**
Journal: *Three words in her lord's own hand: "Kill these messengers." Shizue delivered them anyway — or asked why —
and found an Imperial magistrate who pays everyone to keep the Empire at war.*
[UNLOCK] (route A) *Strategist's Eye*; *Read the Field* early · *Fury Without End* kata at R3

---
## Travel Banter unlocked by Lion Ch3
### TB-lion3-a "Rivers" (Shizue + Mitsue)
MITSUE: You should have thrown it in the river.
SHIZUE: Then I'd never have known who wanted me dead.
MITSUE: Knowing is overrated.
SHIZUE: (a small smile) Says the woman who eavesdrops for a living.
MITSUE: (beat) …That's different. I *enjoy* it.
### TB-lion3-b "Shogen" (Shizue + Natsuko; requires shogen_joined)
NATSUKO: Your old sensei splits firewood barefoot in the snow.
SHIZUE: He says the cold is a rumour.
NATSUKO: (approving) The Crab would adopt him in a heartbeat.
