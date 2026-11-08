# PRODUCTION — Lion Ch1 · "The Blood of Family"

**Traveler:** Akodo Shizue · **Lv** 1–8 · **Outline:** `scripts/lion-ch1-the-blood-of-family.md`
**Shared climax** with Phoenix Ch1 (S07–S08 here = Phoenix S08). When both travelers are in the party, merged lines
are marked `[IF haruki_in_party]`.
**Flags set:** `shrine_broken`, `clues_found` (0–5), `hojiki_custody` (lion/phoenix), `climax_route` (A/B/C),
`yachiko_suspected`
**Maps:** `magonojo_river`, `hiruto_castle` (courtyard, chapel, bathhouse, barracks, guest wing, west tower),
`shrine_roads`, `shiro_kamatori`
**Battles:** `b_warehouse_raid` (tutorial), `b_nagai_possessed`, `b_duel_ashimita` (Duel), `b_boss_otamai`
**Guests:** Akodo Ijako (S03), Shiba Ashimita (S04 Duel → S06)
**Fit conversions:** the clue board is Octopath town questioning with a 5-clue gate; the shrine search is a
colder/warmer prompt at 4 spots; the 3 climax routes are one choice with the same boss.
**Storyboard:** `storyboards/lion-ch1.md` (adds the castle-town screen; `shrine_roads` = `road_west_phoenix`).

### PAIR RULE with Phoenix Ch1 (storyboard P-1)
- **Played first:** as written. If Haruki isn't recruited, he appears as a silent NPC in the embassy ("a young Isawa
  carrying too many scrolls").
- **Played second** (Phoenix Ch1 already done): a playable flashback. Title card: *"That week at Lord Hiruto's
  castle."* Shizue tells the party her side. `climax_route` is **locked** to the first playthrough's value (Phoenix
  first = A). The boss is fought "in memory" (same battle). Merged `[IF haruki_in_party]` lines play if he's active.
- **Guests (G-1):** Ijako (S03) and Ashimita (S04): one active, the other waits. Stand-ins acting in cutscenes don't
  use the guest slot.

### RECRUIT VARIANT (Shizue is not the starter)
**Join point:** `hiruto_castle` courtyard, as the Phoenix embassy arrives (S02).
SHIZUE: (watching the Phoenix banners, not the party) Three clans' maps overlap here. You've wandered into the one
place none of them agree on.
SHIZUE: (turning) Akodo Shizue. My cousin burned a granary and broke a shrine, and now the Phoenix say we murdered
their historian. (beat) I'd like to find out if we did.
> CHOICE "Travel with Shizue?" → Yes: **Memory** (S01: the raid, Gusai's torch, Hojiki and the skull in the fog — no
  battle) → resume at S02 ("You will investigate. All of you.").
→ No: she waits in the courtyard.

---

## S01 — Smoke on the Magonojo
MAP: `magonojo_river` (night) · TRIGGER: new game, Shizue chosen
NARRATION: The Lion-Phoenix-Crane border. Where three clans' maps overlap, and none of them agree.
(River fog. Lion riders on the bank. AKODO GUSAI, soot-smeared and grinning, raises a torch.)
AKODO GUSAI: Phoenix warehouses! Full of rice for the Crane army! Burn them!
SHIZUE: Cousin, we came to *scout* the warehouses.
AKODO GUSAI: I've scouted them. They're flammable.
SHIZUE: Gusai—
AKODO GUSAI: Hold the horses, Shizue! You're good at standing still.
(He charges. Phoenix guards rush out.)
[BATTLE b_warehouse_raid]
### TUTORIAL
- T1: "**Command** — your Talent. Give an ally an extra action, or move them up the turn order."
- T2 (on a Lion rider): "Lions break shields fastest when they strike in order. Command a rider to act now."
- T3: "Weaknesses and **Suki** work the same for everyone. Think three moves ahead."
(The warehouses burn. Across the water, smaller flames: a roadside shrine being smashed by Gusai's men.)
SHIZUE: Gusai! The shrine is not a warehouse!
AKODO GUSAI: Then it shouldn't stand next to one!
(Inside the broken shrine, a samurai, AKODO HOJIKI, lifts a lacquered box. It splits open: a skull bound in jade
chain. The chain is in pieces. He cuts his palm on a jade shard and wraps the cut with a small green stone.)
AKODO HOJIKI: (to himself, uneasy) …For luck.
(Hojiki looks up and sees Shizue watching. He bows, embarrassed. The fog swallows the shrine.)
[SET shrine_broken]
[SAVE]

## S02 — The Phoenix Arrive
MAP: `hiruto_castle` (courtyard, a week later) · TRIGGER: auto
(A small castle. LORD AKODO HIRUTO stands at the gate, calm as a stone. Phoenix banners approach: the arrogant
heir ISAWA KAMASARI, his yojimbo SHIBA ASHIMITA, and an Imperial magistrate in muted silk, MIYA YACHIKO.)
ISAWA KAMASARI: Lord Hiruto. My uncle, Isawa Hoju, is dead. By blood magic.
ISAWA KAMASARI: We followed the stink of maho west. It ends at your gate.
AKODO HIRUTO: Then you'll want to come in.
MIYA YACHIKO: (pleasantly) The Emperor's interest is in peace, my lord. And the truth, of course.
AKODO HIRUTO: Of course.
(Later. Hiruto, alone with his family in the hall: his eldest HOJATO (monk-like), the sullen GUSAI, and Shizue.)
AKODO HIRUTO: You will investigate. All of you.
AKODO HOJATO: Father, bushido and honour are all we—
AKODO HIRUTO: Bushido and honour have never once found a murderer, Hojato.
AKODO HIRUTO: Find the truth. If it's a Lion's truth, it is still the truth.
SHIZUE: And if the truth starts a war, uncle?
AKODO HIRUTO: (a long look) Then we will at least know what we are fighting about.
AKODO HIRUTO: That will be rare.
(Objective: "Investigate the castle. Find 5 clues.")
[SAVE]

## S03 — Where the Kami Went (investigation hub)
MAP: `hiruto_castle` · TRIGGER: explore
### Map-wide status — Spirit Wasteland
"The kami here have fled or been devoured. **Spells are weaker** in the castle (−1 tier)."
### S03a — Ijako (chapel)
(A young woman in a mask of reeds and dried mud kneels before the ancestor shrine: AKODO IJAKO, Shizue's cousin.)
SHIZUE: Ijako? You're home.
AKODO IJAKO: (lifting the mask) I came back from the Kitsu a stranger. Nobody here knows what to say to a girl who
talks to the dead.
SHIZUE: I'll say what I always say. "Good morning, Ijako."
AKODO IJAKO: (a small smile) …Good morning, Shizue.
AKODO IJAKO: The dead in this house are frightened. The dead are never frightened. Something is eating them.
[GUEST +Akodo Ijako] (skills: Call the Dead — ancestor strike, 1 use; Mask Rite — reveal a spirit's true form, 2 uses)
### Clues (any 5 of 6 → `clues_found` ≥ 5)
| # | Where | How | Clue |
|---|---|---|---|
| C1 | chapel | Ijako's Mask Rite | **Hoju's ghost:** "the one who bound him has returned… it wears a sleeping man" |
| C2 | courtyard | talk to a peasant's ghost at night | It accuses Hojiki of murder. **Mask Rite** → it casts no reflection in the water barrel: **a lie** |
| C3 | bathhouse | search | A small green stone on the floor: **real jade**. Hojiki's wound-stone is an illusioned pebble |
| C4 | Ozaki's room | [PA Duel] cousin **Akodo Ozaki** for entry, or wait until he's at dinner | A looted statue of Isawa from the shrine. **Ozaki ordered the shrine smashed** |
| C5 | barracks | talk to **Ryuzoji** | He hides an arm wound: he should have been on the raid and wasn't |
| C6 | guest wing | [PA Eavesdrop / Discern] on Yachiko — or, with neither available, Ijako notices the cipher ink on her sleeve once C1–C3 are found | She writes daily to "the capital" in cipher |
### Key lines
- C1, HOJU'S GHOST: "Gentle child. Tell my apprentice… the chains. The chains are in my chest. He'll know."
- C2, PEASANT GHOST: "Hojiki! Hojiki killed me! The Lion killed me!" / IJAKO (Mask Rite): "Look in the water, Shizue.
  No face." / SHIZUE: "A ghost that lies. Then it isn't a peasant."
- C4, AKODO OZAKI (if dueled): "A war makes heirs, cousin. Peace makes clerks." / SHIZUE: "Then I'll be a clerk."
- C6, YACHIKO (Eavesdrop, to her servant): "…inconclusive, tell them. It must stay inconclusive."
### Town NPCs — `hiruto_castle`
| NPC | Default | Info | Path action |
|---|---|---|---|
| Akodo Hojato | "Bushido is enough." | *Discern:* "Secretly terrified his father is right." | — |
| Akodo Gusai | "The Phoenix are lying!" | *Discern:* "Can't sleep since the raid." | *Duel:* he yields → "I didn't order the shrine. Ozaki did." |
| Kitsu Togawa (priest) | "The ancestors won't answer me." | — | — |
| Matsu Nagai (visiting sensei) | "Bah. Ghosts. Train harder." | *Discern:* "Has nightmares of red shadows." | — |
| Akodo Ukita (cavalry) | "I won't lie for anyone. Ask me anything." | *Discern:* "A fox-spirit ancestor; he sees oddly well at night." | gives C2 timing |
| Servant girl | "The bath is always cold now." | — | — |
| Farmer (castle town) | "The fields won't grow. The kami left." | — | *Bless:* follows ("Field Prayer", small heal, 1 use) |
| Crane trader (castle town) | "Just passing. Buying. Selling." | *Eavesdrop:* "Crane scouts pay him for news." | *Barter:* Herbal Salve |
| Kitsu child (castle town) | "My grandfather won't talk to me any more." | — | *Charm:* follows ("Ancestor Whisper", reveal 1 weakness) |
| Ronin guard (castle town) | "I guard the gate. Nobody asked which side." | — | *Sumai:* Old Whetstone · *Pilfer:* Patrol Writ |

## S04 — Escalation
MAP: `hiruto_castle` · TRIGGER: clues_found reaches 2, then 3, then 4
- **At 2:** scouts report Crane troops on the border. (AKODO UKITA: "Crane banners. Three ri. Watching, not moving.")
- **At 3:** KITSU TOGAWA is found choked in the chapel, from the inside. (IJAKO: "Not a hand. Something inside him.")
- **At 4:** MATSU NAGAI, possessed, attacks the Phoenix guest wing.
[BATTLE b_nagai_possessed]
(mid-boss — weak to Jade (Hojiki's real stone, C3, usable as an item) and Water)
MATSU NAGAI (possessed, many voices): Phoenix! You killed my children! (no — not his voice) You *bound* me!
(Victory: Nagai collapses, himself again, weeping. Isawa Kamasari is furious.)
ISAWA KAMASARI: Enough! Hojiki was named by the dead! I will have him in chains!
SHIZUE: Give me one more day, Isawa-sama.
ISAWA KAMASARI: For what? Lion honour?
SHIZUE: For the truth. You said you followed it here. Let me follow it a little further.
SHIBA ASHIMITA: (stepping forward, wincing at a sound no one else hears) My lord. Let me test her.
SHIBA ASHIMITA: If she can stand against me, she's earned her day.
[PA Duel Ashimita] [BATTLE b_duel_ashimita]
(win OR lose honourably → the day is granted)
SHIBA ASHIMITA: (after) You fight like someone listening for the next move.
SHIZUE: You fight like someone listening for something else entirely.
SHIBA ASHIMITA: (a thin smile) My grandfather. He screams. He has since I was born.
SHIBA ASHIMITA: You get used to it. (beat) No. You don't.
[SAVE]

## S05 — A Good Man, Technically Guilty
MAP: `hiruto_castle` (barracks) · TRIGGER: clues_found ≥ 5
(Hojiki sits on his bunk, the illusioned pebble in his hand. His brother RYUZOJI hovers, guilty.)
AKODO HOJIKI: I dream every night of killing an old man I've never met. Then I wake, and the dream is true.
AKODO HOJIKI: If my hands did it, then I did it. Let the Phoenix have me.
SHIZUE: No.
SHIZUE: If your hands did it, then someone is wearing your hands. I want the someone.
AKODO RYUZOJI: (bursting out) It should have been me on that raid! I hid a wound to stay home! He went in my place!
SHIZUE: (gently) Then you'll help me bring him back.
> CHOICE "Hojiki's custody"
  - "Hand him to the Phoenix." → [SET hojiki_custody phoenix] (Kamasari is satisfied; the climax is harder: no host
    ready)
  - "Keep him under Lion guard." → [SET hojiki_custody lion] (Kamasari is furious; Yachiko smiles a little too much)

## S06 — The Fire-Coloured Castle
MAP: `shiro_kamatori` · TRIGGER: ride east under truce (with Ashimita as guide)
NARRATION: Shiro no Kamatori. In the sunset its copper-edged walls blaze as though the castle were built of fire.
[IF haruki_in_party]
HARUKI: (at the gate, very quietly) This was my teacher's home.
SHIZUE: Then you'll know where he kept his secrets.
HARUKI: In a chest under his desk. With his tea. (beat) He always said history and tea should be kept together.
[ELSE]
(A nervous young Isawa acolyte meets them: the castle's last scholar, who reads them Hoju's history.)
[END]
(Hoju's study. His unfinished family history, read aloud.)
READER: "A Bloodspeaker, O-Tamai, who called himself the beloved of Iuchiban, wore the body of the young shugenja
Kaiki for two years."
READER: "We could not cast him out. So we killed the boy, and bound the spirit to its skull in jade."
READER: "I forged the chains myself. I have never forgiven myself for the boy."
(In the chest: the jade chains. The lock grows cold when it faces west.)
[ITEM +Jade Chains (key item — compass)]
### Colder/warmer search (fit conversion) — `shrine_roads`, 4 despoiled shrines
- S1: "The lock is cool." · S2: "Colder." · S3: "Cold. Frost on the lacquer." · S4 (Hiruto's castle, facing the west
  tower): "**Ice.** The spirit is here."
[SAVE]

## S07 — Three Ways to End It (shared with Phoenix Ch1 S08)
MAP: `hiruto_castle` (hall, night) · TRIGGER: return with the chains
(Everyone gathers: Hiruto, Kamasari, Ashimita, Yachiko, Ijako, Hojiki under guard. The chains hang in Shizue's hands,
freezing.)
AKODO IJAKO: He's impatient now. He'll do something tonight.
> CHOICE "How do we end it?"
  - "A · Bind him into a body." → [SET climax_route A] (recommended)
      AKODO HOJIKI: Use me. It's my body he's been borrowing. Let him have it one last time — in chains.
      [IF hojiki_custody phoenix] KAMASARI: (reluctantly) …Bring the Lion back from my guard. [END]
  - "B · Settle it by duel." → [SET climax_route B]
      (A Crane duellist arrives under truce: KAKITA MIZOCHI, to settle the border by iaijutsu.)
      O-TAMAI (whispering in Shizue's ear): Let me lend you Hojiki's hands, Lion. You'll win. The Crane will die.
      SHIZUE: (aloud) No. (to Mizochi) I'll face you clean, Kakita-san.
      (Refused, O-Tamai lashes out.)
  - "C · Protect my uncle." → [SET climax_route C]
      (A red shadow crawls across the courtyard wall toward Lord Hiruto's chamber. A short chase — a cutscene and
      2 interaction points — ends in his doorway.)
      SHIZUE: Uncle! Don't move!
      AKODO HIRUTO: (not moving at all) I wasn't going to.

## S08 — O-Tamai (BOSS, shared)
MAP: `hiruto_castle` (hall / yard / Hiruto's chamber, by route) · TRIGGER: after S07
(The air goes red. O-Tamai rises in a borrowed body; a shadow-oni crawls up behind it.)
O-TAMAI: Lions! You broke my prison to burn a granary!
O-TAMAI: I owe you a war. Let me pay my debt!
SHIZUE: (Command: "Now!") We'll take it in jade.
[IF haruki_in_party]
O-TAMAI: And a Phoenix! The Phoenix killed a child to bind me! Tell them, little Isawa!
HARUKI: (very still) Yes. We did. And I know exactly what that costs.
HARUKI: (lifting the chain) That's why I won't let you make anyone pay it again.
[END]
[BATTLE b_boss_otamai]
### Boss mechanics (barks)
- "Soul damage": the red-shadow oni drains SP/VP. AKODO IJAKO: "It's eating our breath, not our blood!"
- Each Suki on O-Tamai → command **[Jade Chain]** appears: "Bind a chain around him!" (3 chains = victory)
- Chain 1, O-TAMAI: "Cold! Cold!" · Chain 2: "Not again — not AGAIN—" · Chain 3: (a scream that becomes silence)
(The spirit-wasteland status clears. Somewhere, very faintly, a kami in the garden starts humming again.)

## S09 — The Weight of a Raid
MAP: `hiruto_castle` · TRIGGER: after the boss
(Morning. The skull, wrapped in new jade, goes east with the Phoenix.)
ISAWA KAMASARI: (stiffly, to Shizue) The Phoenix… acknowledge your diligence.
SHIZUE: (bowing) The Lion acknowledge your patience.
SHIBA ASHIMITA: (aside, with a ghost of a smile) That's the nicest thing he's ever said to anyone.
MIYA YACHIKO: (writing, to her servant) Inconclusive. Write "inconclusive".
(Shizue sees Yachiko smile at the word.)
[SET yachiko_suspected]
(Later. Hiruto's private garden.)
AKODO HIRUTO: My son started a war for a granary. My nephew wanted one for glory.
AKODO HIRUTO: You stopped one for the truth.
AKODO HIRUTO: I can't reward you for it. It would shame them.
(He gives her his own go stones, worn smooth.)
AKODO HIRUTO: The black stones. You always play black.
SHIZUE: (holding them) …You noticed.
AKODO HIRUTO: I notice everything, Shizue. I just don't say so. It's a Lion habit. Break it, if you can.
(A messenger: Shizue is to join the Lion retinue at the Champion's Winter Court.)
AKODO HIRUTO: The most junior seat. The far end of the hall.
SHIZUE: (smiling) Good. You see the whole board from the far end.
[ITEM +Hiruto's Go Stones (accessory: +1 Command use per battle)]
[CHAPTER COMPLETE]
### Chapter complete card
**"The Blood of Family" — complete.**
Journal: *A raid broke a shrine and freed a Bloodspeaker. Shizue followed the truth into her own family, and bound
the spirit in jade. Now Toturi's Winter Court awaits — and an Imperial magistrate who prefers things inconclusive.*

---
## Travel Banter unlocked by Lion Ch1
### TB-lion1-a "Black Stones" (Shizue + Gendo)
GENDO: You play go in your head when people talk to you.
SHIZUE: Only when they're boring.
GENDO: Am I boring?
SHIZUE: You're a very interesting opening. I haven't decided where you go.
### TB-lion1-b "Ijako" (Shizue + Haruki, if Ijako has been met)
HARUKI: Your cousin talks to the dead. Do they… say anything nice?
SHIZUE: Mostly they complain about their descendants.
HARUKI: (relieved, oddly) Oh good. Mine would too.
