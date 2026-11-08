# PRODUCTION — Finale · "The Empress of Nothing"

**Party:** all eight travelers (two parties of four; swap at gates and between phases) · **Lv** 55–60
**Outline:** `scripts/finale-the-empress-of-nothing.md`
**Unlock:** all eight Ch4s complete. · **Storyboard:** `storyboards/finale.md`
**Approach:** route `thunder_plain_road` (Danger 50–56) bridges the Ch4 → finale level gap.
**Post-game:** after the credits, the clear save returns the party to the Shrine of Osano-Wo the day before the
finale. The Shadowlands reopen, the Shinomen stays open, and the post-game regions (Lv 61–80) unlock.
**Flags read (all chapters):**
- Crab: `nashiko_unmasked`, `oni_named_ryozo`, `nezumi_friends`, `blue_flare_held` / `flare_fired`
- Crane: `same_woman_proven`, `play_known_scenes`, `rehearsal_quality`
- Phoenix: `whole`, the Bloodspeaker book
- Dragon: `glory_refused`, `history_final`
- Lion: `report_truth`, `atsuko_promise`
- Scorpion: `box_destroyed`
- Unicorn: `settlement`
- Ronin: `sayo_saw_nashiko`, `naga_talked_down`
- Act 1 extra: `three_clan_truce` (Lion Ch4 + Phoenix Ch1 crate lid)
- Debate extras: `courier_heard` (Mitsue), `box_destroyed` (Mitsue); F09: `play_handed_over` (halved play debuffs)
- Montage (F10): `nezumi_friends`, `hidden_ones_cleared`, `guard_rescued`, `play_handed_over`, `forest_village_spared`,
  `depura_seen`, `mirumoto_terms`, `glory_refused`, `momo_joined`, `toturi_knows_name`, `atsuko_promise`, `shogen_joined`,
  `whole`, `torii_saved`, `hana_saved`, `city_freed`, `settlement`, `karasu_joined`, `camps_fed`, `loot_returned`,
  `naga_talked_down`, `inquisitors_hunt_done` (SS-TEAM), `benjiro_father_home` (Benjiro SS2)
- Codas (E01): `kage_told_truth`, `nezumi_friends`, `duel_won`, `history_final`, `gendo_keeps_secret`, `kumpei_spared`,
  `report_truth`, `mieko_answer`, `settlement`, `sayo_saw_nashiko`, `mosuke_knows`, `togashi_heard`, `hana_saved`
**Maps:** `plains_of_thunder`, `osano_wo_shrine`, `shinomen_edge`, `shinomen_1–4`, `kumo_fire`, `corrupted_glade`,
`starfield` (phase 2), and 8 epilogue maps
**Battles:**
- Act 1: `b_shrine_wave_1–7` (defence)
- Act 2: `b_shinomen_a/b`, `b_kumo_spiders` (rudeness only)
- Act 4: `b_final_nashiko_p1/p2/p3`

---

## ACT 1 — The Shrine of Osano-Wo

### F01 — Eight Roads
MAP: `plains_of_thunder` (dusk) · TRIGGER: start the finale
NARRATION: The Plains of Thunder, at the end of the Month of the Monkey, 1123.
NARRATION: A Shadowlands host marches out of the Shinomen Mori toward a shrine full of monks, peasants, and jade.
NARRATION: And eight people, on eight roads, who were not sent by anyone.
(Eight figures converge on the shrine's stockade from different directions. They stop, and look at each other.)
NATSUKO: Nobody sent me. I followed smoke.
RENSEI: Nobody sent me either. (beat) Lady Sanae *suggested* it. Strongly.
GENDO: I followed a map of everywhere she's been. (spreading it; the lines converge) It points here.
SHIZUE: (placing a go stone on his map) And here.
HARUKI: Mieko's book said she'd come from the forest.
MITSUE: (arriving last, from the south road, lightly) I was in the area.
TAMOTSU: (with a cart of jade and Persimmon) I was *delivering*. Somebody has to bring the jade.
SAYO: (with an ember in a twist of iron) I came because you'd all be here. (grinning) Obviously.
### TB-finale "Eight Roads" (forced banter; plays once)
NATSUKO: Eight of us.
GENDO: (very quietly) "Seven mortals will rise." That's what the prophecy said.
SAYO: (cheerfully) Then one of us is extra. Hope it's me. I've never been extra before.
(The monk-abbot of Osano-Wo opens the gate. Behind him, in a lay brother's grey, his ribs still bandaged: JINNAI.)
JINNAI: Wave-girl. (bowing) You brought friends.
SAYO: You said the thunder monks were hard to kill.
JINNAI: (looking toward the forest, where the drums are starting) We're about to find out.
[SAVE]

### F02 — Hold the Shrine (set-piece: defence waves)
MAP: `osano_wo_shrine` · TRIGGER: the horde arrives
### SYSTEM
"**Seven waves.** **Two parties** alternate — swap at the stockade gate between waves.
Protect the **jade stores** and the **abbot**."
- [BATTLE b_shrine_wave_1] Goblin swarm. NATSUKO: "Goblins! The first wave's always goblins. It's tradition."
- [BATTLE b_shrine_wave_2] Hold the breach. (Razor's Edge, Stance of the Wall) NATSUKO: "Stand behind me. Everyone. That's what I'm for."
- [BATTLE b_shrine_wave_3] Burning goblin fanatics. SAYO: "Water! Rhubarb! Anything wet!"
- [BATTLE b_shrine_wave_4] Ogre battering ram —
  [IF oni_named_ryozo]
  (Leading the ogres: a rider in polished Seppun armour over something that isn't a man.)
  "RYOZO": Hiruma! I have a name now! Isn't it *good*?
  NATSUKO: You took a good man's name. (Razor's Edge) Give it back.
  (On its defeat:) "RYOZO": (a door-creak, fading) …Ryozo… I liked being Ryozo… (and there is nothing left in the armour)
  NATSUKO: (quietly) Rest, guardsman. Your name's yours again.
  [ELSE] (An ogre captain leads the ram.) [END]
  [IF flare_fired OR blue_flare_held] (A blue star over the plains. Crab horns — Kage's Hiruma, a wave early.) HIRUMA KAGE: "Scout! You'll walk beside me — so I came to walk beside *you*!" [END]
- [BATTLE b_shrine_wave_5] Save the abbot (escort). JINNAI: "Abbot! Down!" (Jinnai's Freezing the Lifeblood stops a goblin mid-leap)
- [BATTLE b_shrine_wave_6] Close the breach. SHIZUE: (Akodo Formation) "Close it! Shields! *Now!*"
  [IF three_clan_truce] (Lion spears and Crane bows hold the breach together, under a Phoenix ward. +1 Resolve damage
  for all seven waves.) HARUKI: "The crate lid. It was worth keeping." [END]
- [BATTLE b_shrine_wave_7] A spidery horror (wave boss). HARUKI: "Mass Path to Inner Peace — everyone, stay close!"
### F03 — The Herald
(Smoke. Silence. The horde breaks and flees into the forest. Out of the smoke walks a lovely herald in red silk,
untouched by soot. Her eyes are very blue.)
HERALD: The Empress congratulates you.
HERALD: She awaits you in Shinomen. Four days.
HERALD: (sweetly) Or this shrine burns, and everyone in it.
MITSUE: (stepping forward) You're not even bothering to change the smile anymore.
HERALD: (the smile widening) Why would she? You'll all be dead soon. (she becomes smoke)
[SAVE]

---
## ACT 2 — Shinomen Mori

### F04 — The Guide
MAP: `shinomen_edge` · TRIGGER: next morning
(At the forest's edge, tied to a stake: a one-handed nezumi, scarred, trembling. STICH'KIK.)
STICH'KIK: Guide! Stich'Kik good-good guide! Knows forest!
STICH'KIK: Take you to the glade. (beat; very small) Then kill. After. Yes? Kill-kill after.
NATSUKO: (kneeling) Why?
STICH'KIK: (looking at his stump) Because she find me again. If you don't.
[IF nezumi_friends]
(A small furred shape pushes past Natsuko's legs: Squeak, who has followed her all the way from the Wall.)
SQUEAK: (furious, tiny) No-kill! (to Stich'Kik) Come-come live in dry-cave! Is nice! Has *eggs*!
STICH'KIK: (staring) …Eggs?
SQUEAK: (proudly) Scout-who-fights-at-night bring eggs. Every week.
[END]
> CHOICE "Stich'Kik"
  - "We'll free you, not kill you." → (recommended; [IF nezumi_friends] he joins the nezumi of Crab Ch1 afterward
    [ELSE] NATSUKO: "There's a dry cave near my Wall post. Nobody uses it. You can have it." [END])
  - "Agree to his terms." → (fake choice) NATSUKO: "…No. I'm not doing it. You're coming home with the rats."

### F05 — Shinomen (journey dungeon)
MAP: `shinomen_1–4` · TRIGGER: enter the forest
- **Naga drag-marks:** enormous serpent trails in the moss.
  SAYO: The Naga are waking. (beat) [IF naga_talked_down] I met one. On a mountain. It lowered its spear for me. [END]
  (From the trees, a pearl-and-bronze shape watches, and inclines its head.)
- **The carved scene:** a clearing where a mock-seppuku has been carved from living wood, with a sneering inscription.
  NARRATION (the inscription, paraphrased): "Here is your bushido. Honestly."
  Party reactions (one line each):
  - NATSUKO: "Somebody's very proud of their carving."
  - RENSEI: "It's badly proportioned."
  - GENDO: "Evidence of an extremely insecure author."
  - SHIZUE: "Trying to make us doubt before we arrive. An old move."
  - HARUKI: "It's sad. Someone carved all this, all alone, out of anger."
  - MITSUE: "I've seen better propaganda in the Scorpion nursery."
  - TAMOTSU: "Shall we leave a rice cake? It looks hungry."
  - SAYO: "Nobody made me swear to it. So it can't mock me." (she walks past)
- [BATTLE b_shinomen_a] [BATTLE b_shinomen_b]
[SAVE] (a mossy shrine)

### F06 — Mamoru the Kumo
MAP: `kumo_fire` · TRIGGER: a campfire in the forest
(An old hermit by a fire, roasting something on a stick. His shadow on the trees has far too many legs: MAMORU THE KUMO.)
MAMORU: Visitors. In my forest. (looking up) Sit, or don't.
> CHOICE "The hermit" (courtesy test — Rensei or Tamotsu lead naturally)
  - [Rensei / Tamotsu / Etiquette] "May we share your fire, grandfather? We brought tea." → (pass)
      TAMOTSU: (pouring) Jasmine. From the Unicorn trade. The good kind.
      MAMORU: (sniffing; pleased) …Polite. Very rare, in this forest.
  - "Out of our way, old man." → [BATTLE b_kumo_spiders] (then he leaves, unimpressed)
[IF passed]
MAMORU: You go to the glade. To *her*.
MAMORU: A word, for the tea. (leaning close; his eyes are many) She can only hold one mind at a time.
MAMORU: Speak with two voices, and she hears neither.
MAMORU: (settling back) That's all. Mind the roots. They bite.
[END]

### F07 — The Glade
MAP: `corrupted_glade` (approach) · TRIGGER: the forest's heart
(A glade of terrible beauty — flowers made of something that isn't petal, a pool that reflects the sky wrong.)
(Nailed to the largest tree: a plaque. Old, Lion-made. "DUTY.")
SHIZUE: (stopping) …The plaque from Shiro Akodo. The one that was never found.
(She takes it down, very carefully, and holds it.)
SHIZUE: (quietly) I'll carry it the rest of the way.
[ITEM +"Duty" Plaque]
[SAVE] (the last save before the debate)
(Prompt: "Beyond this, the Empress waits. You will not return until it's over.")

---
## ACT 3 — The Debate (set-piece)

### F08 — The Empress Receives
MAP: `corrupted_glade` · TRIGGER: enter
(On a mat of something leathery, in the loveliest form any of them has seen, a woman receives them as if at court:
DOJI NASHIKO.)
DOJI NASHIKO: My guests. At last.
DOJI NASHIKO: You've been chasing me through eight little stories. Aren't you tired?
DOJI NASHIKO: Sit. Let's talk about your *code*.
### SYSTEM — the debate
"Nashiko attacks the virtues of bushido one by one. First she strikes each traveler through their clan's **weakest**
virtue — then they answer with their clan's **strongest**, from their own story.
Each **strong** answer **breaks one of her eight shields** for the battle to come."
### Courage — Natsuko
DOJI NASHIKO (doubt — Courtesy, the Crab's weakest): You've never once been courteous, scout. You blunder through every court.
NATSUKO: (stung) …No. I haven't.
DOJI NASHIKO (attack — Courage): And your courage? Following the path every Crab follows — onto the Wall to die — that's not courage. That's habit.
> REBUTTAL (from her story)
  - (strong) NATSUKO: "Courage isn't following the path everyone walks. It's walking back into the dark every morning because someone has to." [+ her father's road, Kage, the nezumi]
  - (weak) "The Crab are brave." 
### Courtesy — Rensei
DOJI NASHIKO (doubt — Courage, the Crane's weakest): A Crane boy who shook at his father's voice. Brave?
RENSEI: (pale) …I shook.
DOJI NASHIKO (attack): And courtesy — a mask for knives. Ask *me*. I was the most courteous woman at Komatsu's court.
> REBUTTAL
  - (strong) RENSEI: "Etiquette can be a mask for knives. It's also the only thing that keeps two enemies at one table long enough to stop a war."
    [IF play_known_scenes ≥ 1] RENSEI: "And I've read your play, my lady. Every scene." (she flinches — "My *what*?") [END]
### Sincerity — Gendo
DOJI NASHIKO (doubt — Duty): A clerk who abandoned his post to play in the past.
GENDO: (polishing his spectacles, unbothered) I filed for leave.
DOJI NASHIKO (attack): Every clan asks its samurai to lie. Sincerity is just lying *well*.
> REBUTTAL
  - (strong) GENDO: "Every clan asks its samurai to lie. I've lied too — to protect a truth bigger than me. Sincerity isn't never lying. It's knowing exactly what the lie costs, and paying it yourself."
    [IF glory_refused] GENDO: "I gave up being remembered rather than lie about who saved that city." [END]
### Honor — Shizue
DOJI NASHIKO (doubt — Compassion): Cold little strategist. Do you feel anything, or only count?
SHIZUE: (beat) …Sometimes I only count.
DOJI NASHIKO (attack): Honour is a word lords use to keep you in line. Your cousin started a war in its name.
> REBUTTAL
  - (strong) SHIZUE: (setting the "Duty" plaque on the mat between them) "I've seen my cousin start a war in its name. Honour isn't what my lord calls it. It's what I answer for when no one is watching."
    [IF report_truth] SHIZUE: "I told my Champion the Lion charged first. Nobody would ever have known." [END]
### Righteousness — Haruki
DOJI NASHIKO (doubt — Sincerity): You hid your crime for twelve years, little Void. Sincere?
HARUKI: (very quietly) …No. I wasn't.
DOJI NASHIKO (attack): And where is justice? The guilty walk free while their retainers die for them.
> REBUTTAL
  - (strong) HARUKI: "No court ever judged me for what I did at eight. So I judged myself. And I spent my life setting it right. That is righteousness: not waiting for someone else to do what's just."
    [IF whole] HARUKI: "I gave her back what I took. It cost me. It was supposed to." [END]
### Duty & Loyalty — Mitsue
DOJI NASHIKO (doubt — Honor): A Scorpion with no honour at all. Nobody knows your name.
MITSUE: (lightly) That's rather the point.
DOJI NASHIKO (attack): Lords never pay for their failures. *You* pay. And your Champion — oh, I know what he's planning. Do you?
MITSUE: (the smile stays; the eyes don't) …
[IF courier_heard] MITSUE: (internal) *Every garrison. Toward the capital. The Month of the Rooster.* (aloud, lightly) "I'm sure I've no idea, my lady." [END]
> REBUTTAL
  - (strong) MITSUE: "Lords never pay for their failures? Mine will. And I'll be there. Because duty isn't a leash. It's the promise I keep even when I know exactly what it will cost — and I know better than anyone here."
    [IF box_destroyed] DOJI NASHIKO: "You threw the Iron Box into a volcano? It would have made you *anyone*." MITSUE: "I'd rather be someone." [END]
### Compassion — Tamotsu
DOJI NASHIKO (doubt — Courtesy): The Ide's famous manners. Bought, like everything Unicorn.
TAMOTSU: (cheerfully) Some of them were on sale.
DOJI NASHIKO (attack): Lords starve villages and sell daughters and call it order.
> REBUTTAL
  - (strong) TAMOTSU: "Lords sell daughters and starve villages, and call it order. I've stood in the camps, lady. Compassion isn't pretending the world is kind. It's the rice you hand over anyway, even when there's no profit in it — *especially* then."
    [IF settlement heir] TAMOTSU: "I made a nameless boy a bridge between two houses that tried to kill each other. Profit: zero." [END]
### The last word — Sayo
DOJI NASHIKO: (turning to the ronin girl, almost bored) And you. No lord. No clan. No virtue to defend.
DOJI NASHIKO: Bushido is a child's dream. You of all people know it.
SAYO: Maybe.
SAYO: Nobody ever made me swear to it. No lord. No clan.
SAYO: I picked it up anyway. (beat) That's what makes it real.
DOJI NASHIKO: (very still, for the first time) …A peasant's daughter. Lecturing an Empress.
SAYO: Ronin's daughter. (beat) And you're not an Empress. You never were.
SAYO: (smiling) That's the whole play.
[IF play_known_scenes ≥ 1] RENSEI: "Act three. Scene two." DOJI NASHIKO: (rising; her beauty cracking like glaze) "WHAT PLAY?" [END]
[SAVE — "The Empress rises." (auto-save before the battle)]

---
## ACT 4 — The Empress of Nothing

### F09 — Final Battle
MAP: `corrupted_glade` → `starfield` → `corrupted_glade` · TRIGGER: after the debate
### SYSTEM
"**Party A** fights phase 1. **Party B** fights phase 2. Choose **your best four** for phase 3.
Shields broken in the debate are already gone."
#### Phase 1 — The Bride  [BATTLE b_final_nashiko_p1]
DOJI NASHIKO: (rising into the air, wings of smoke) You'll be my court. All of you. On your knees, forever.
- She flies and turns **invisible**. **Crystal / thin jade** reveals her.
  - [IF nashiko_unmasked] → "She can't turn invisible on turn 1 — Natsuko knows her tells."
- Her seduced champions shield her (**Blood Shouting**: damage transfers to them).
  - [IF the Bloodspeaker book] HARUKI: "Mieko's book — the ward on the third page! — It's broken!"
- [IF same_woman_proven] → her disguise phase is skipped: RENSEI: "We know your face. All of them."
#### Phase 2 — Body of Damned Time  [BATTLE b_final_nashiko_p2]
(The glade dissolves into an inky starfield. Each traveler sees, for a moment, their own death — and their hair begins
to whiten.)
DOJI NASHIKO: Look. Look how you end. All of you, old and alone, in the dark.
- **Timer:** each turn the party **ages** (stacking stat drain).
  - [IF whole] HARUKI: "Water heals cleanse it — stay with me!"
- NATSUKO: (looking at her own death, unbothered) "Huh. Old. On the Wall." (beat) "I'll take it."
#### Phase 3 — True Form  [BATTLE b_final_nashiko_p3]
(Her loveliness peels away. A black-edged wound in her throat pulses with Fu Leng's glowing blood. Her eye-sockets are
empty and glow blue.)
DOJI NASHIKO: (a voice like a court of the dead) I was going to be *EMPRESS*!
- Weak: **jade, crystal, obsidian** (obsidian Taints its user).
- **Exploits (commands appear when available):**
  - *Smooth Stone Decoy* (colour-blind) — SAYO: "Here, Empress. A present." (she snatches the pebble; loses a turn)
  - *Disfiguring Strike* (any crit to the face) — she staggers, shrieking, hands over her face
  - *"Empress" Bait* [IF rehearsal_quality good] — RENSEI: (with awe, as rehearsed) "…Empress." (her guard drops for 1 turn)
  - [IF play_handed_over] The play-based debuffs (*Empress Bait*, the "WHAT PLAY?" shield break) are **halved** —
    Rensei only knows Sanae's copy second-hand. RENSEI: (internal) "I should have kept it, Father."
  - *Two Voices* (Mamoru's word) — two travelers speak at once; her next action is wasted
  - *The Immovable Hand of Peace* [IF Tamotsu R5] — TAMOTSU: "I won't strike you. And so you won't strike me." (she's locked 1 turn)
- Resolve 28 minus the shields broken in the debate.

### F10 — Flight
(At 10% she breaks, and flees through the forest — and every path is blocked. A callback montage; each shot plays only
if its flag is set:)
- [Crab] Kage's Hiruma, torches high. [IF nezumi_friends] Squeak on a sergeant's shoulder. [END]
  [IF hidden_ones_cleared] Gonta and the Hidden Ones with a landslide of boulders. [END]
  [IF guard_rescued] The old guard, off watch, holding a lantern. [END]
- [Crane] [IF play_handed_over] Lady Sanae, on a palanquin, a blank scroll burning in a brazier. [ELSE] Lady Sanae and Kakita Masanori side by side. [END]
  [IF sanae_answer "The Empire"] LADY SANAE: "Brave. Foolish. Correct. (beat) Again." [ELSE] LADY SANAE: "For the House, then. It's the same road tonight." [END]
  [IF forest_village_spared] Imuro and the forest "bandits" with paper lanterns. [END]
  [IF depura_seen] (A cloaked Scorpion merchant slips away from the scene, unnoticed by everyone but Rensei.) [END]
- [Dragon] [IF mirumoto_terms] The Mirumoto army, wax in its ears, swords out. [END]
  [IF glory_refused] Togashi Yosai at the front: "Twenty-four!" [END]
  [IF momo_joined] Kitsuki Momo with her plum-farm cousins and pitchforks. [END]
- [Lion] [IF toturi_knows_name] Toturi's Lion, who know Shizue's name now. [END]
  [IF atsuko_promise honest] Atsuko's Crane scouts beside them. [END]
  [IF shogen_joined] Old Shogen, barefoot, grinning. [END]
- [Phoenix] [IF whole] Mieko, one person, raising a ward. [END]
  [IF torii_saved] Keiki's monks with temple bells. [END]
- [Scorpion] [IF hana_saved] Kitsune Hana and the Fox of Kudo. [END]
  [IF city_freed] (A drift of light shaped like a city wall — Osuko's freed souls — bars one path.) [END]
- [Unicorn] [IF settlement heir] Naohida's guerrillas, under two family banners. [END]
  [IF karasu_joined] Karasu's glowing eyes. [END]
  [IF camps_fed] The refugees of the Ojatara, carrying rice-sack shields. [END]
- [Ronin] [IF loot_returned] The eta of Cakon, Hiro with his no-dachi. [END]
  [IF naga_talked_down] A Naga in pearl-and-bronze, spear lowered across the path. [END]
  Akari's fire in the trees (always).
- (Side stories) [IF inquisitors_hunt_done] The Phoenix Inquisitors, blocking a path. [END] [IF benjiro_father_home] Moto Benjiro, face unpainted, at the head of the Crab. [END]
DOJI NASHIKO: (cornered, her face flickering through every disguise from eight stories) I was going to be *Empress*…
GENDO: (quietly) You were going to be a footnote.
GENDO: (beat) I've filed a thousand of those.
### F11 — Death
(Her body becomes an inky void. A white jewelled porcelain mask falls from it and cracks. It breaks into a thousand
motes of light — the souls she drank, rising free. The glade is just a glade.)
(Far away, deep under the Shadowlands, something bellows in grief.)
(The eight stand in an ordinary forest, in ordinary morning light.)
SAYO: (after a long silence) …Is anyone hungry?
NATSUKO: (sitting down on a root) Starving.
[SAVE]

---
## EPILOGUE — The Eve

### E01 — Eight Codas (8 short scenes)
- **Natsuko** — `wall_road`: She walks beside Kage on the first mile of her father's road. At the first marker, she stops.
  [IF kage_told_truth] HIRUMA KAGE: "You told me the truth about the wedding. Nobody else would have." [ELSE] HIRUMA KAGE: "I never thanked you properly. For the Shadowlands." [END]
  NATSUKO: Someday. (beat) Not by dying.
  (She turns back toward the Wall. [IF nezumi_friends] Squeak and Stich'Kik trot behind her, arguing about eggs. [END])
- **Rensei** — `kakita_academy`: He performs his kata on the white sand. The left foot does not hesitate. In a doorway, his father watches.
  [IF duel_won] KAKITA MASANORI: (the smallest nod) "…Better." [ELSE] (He says nothing. It is enough.) [END]
- **Gendo** — `kitsuki_office`: At his desk, over his evidence case. He murmurs:
  GENDO: "The son will become the dark brother… the jade clan goes black… seven mortals will rise." (beat; counting on his fingers, like Haruki) …Seven. Plus one.
  GENDO: (frowning, then smiling) Akuro never could count.
  [IF history_final saviour] (On the wall, a temple painting that wasn't there before: "Gendo the Saviour", glass eyes and all. For a moment the
  painted city behind him is burning. He blinks, and it isn't. He turns the painting to the wall.) [END]
  [IF gendo_keeps_secret] (He opens his notebook to the page he burned at the Furnace. It's blank. He leaves it blank, and looks toward the capital for a long time.) [END]
  [IF kumpei_spared] (On the wall above his desk: a small painting of the year 1122, with the light exactly right.) [END]
- **Shizue** — `hiruto_garden`: Go with her uncle. She lets him win once. He knows.
  AKODO HIRUTO: You let me win.
  SHIZUE: You noticed.
  AKODO HIRUTO: I notice everything. (beat) Thank you.
  [IF report_truth] AKODO HIRUTO: "And the Champion read your report. The whole court knows the Lion charged first. (beat) I've never been prouder of a disgrace." [END]
- **Haruki** — `phoenix_garden`: He brings the book back to Mieko. They don't talk about forgiveness. They talk about camellias.
  MIEKO: The white ones need more shade.
  HARUKI: (writing it down carefully) …More shade.
  [IF mieko_answer "yet"] MIEKO: (not looking up) "…Still not yet." HARUKI: (smiling) "Still more than I hoped." [END]
- **Tamotsu** — `ojatara_valley`: The refugee caravan crests the last hill into the valleys. Persimmon bites the daimyo. Everyone laughs, even the daimyo.
  [IF settlement heir] (Naohida eats first at the welcome feast, looking miserable. Tamotsu passes him a rice cake under the table.) [END]
- **Sayo** — `inn_table`: A long inn table. Seven people talking over each other. A pot of soup that smells like dirt and is delicious. Sayo sits in the middle and says nothing at all, and smiles.
  [IF sayo_saw_nashiko] SAYO: (to herself) "She looked right at me in the shrine town. A ronin girl. (beat) Biggest mistake she ever made." [END]
  [IF mosuke_knows] (A letter on the table from old Mosuke at the Village of the Wounded Lion: "The rice cakes are for us now. Thank you.") [END]
- **Mitsue** — `south_road`: Alone, on the long road to Otosan Uchi, in the evening. She touches the Scorpion Favor she kept for herself.
  [IF togashi_heard] MITSUE: (very quietly) "A family's line will end." (beat) "Not if I can help it. Not all of it." [END]
  [IF hana_saved] (A Fox charm on her sash, a gift from Kudo, swings as she walks.) [END]
  She keeps walking.
### E02 — Final Image
MAP: `otosan_uchi_night`
(The capital at night. A lantern festival: thousands of lights on the river. On a rooftop, a masked figure in red
watches the festival. Far off, the first beat of a war drum.)
TITLE CARD: *The year is 1123.*
TITLE CARD: *The fourteenth day of the Rooster is coming.*
[THE END]
### Post-game unlocks
- Rank 5 content (Lv 61+).
- The Orochi superboss (Crane coast).
- The Hiruma Castle side story (the Hare sword).
- Mirumoto Hikaru's Endless Strike (Gendo).
- Purity of Shinsei (Haruki, Fire 5).
