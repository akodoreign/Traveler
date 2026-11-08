# PRODUCTION — Crane Ch1 · "Heaven's Glory"

**Traveler:** Kakita Rensei · **Lv** 1–8 · **Outline:** `scripts/crane-ch1-heavens-glory.md`
**Flags set:** `ebisu_saved_how` (charm / steel / coin), `forest_village_spared`, `depura_seen`, `seoko_charmed`,
`dawn_route` (1 hidden / 2 public / 3 rescue / 4 duel)
**Maps:** `kakita_academy`, `road_west`, `pleasant_eaves`, `mountains_cloak_forest_1–2`, `bandit_village`,
`goroso_castle_hall`, `goroso_castle_corridor`, `goroso_cells`, `castle_yard`
**Battles:** `b_bokken_bout` (tutorial), `b_forest_bandits_a/b`, `b_boss_yasurugi` (duel + skirmish)
**Guests:** Matsu Kiku (S03), Kitsuki Seigen (S02)
**Fit conversions:** the lantern puzzle is 3 rope-cut interaction points; the four dawn routes are one choice, and
every route ends at the Yasurugi boss.
**Storyboard:** `storyboards/crane-ch1.md`
**Guest rule (G-1):** when Kiku joins in S03, the player picks Kiku or Seigen as the active guest; the other waits
at the inn. Each guest's barks play only if that guest is present.

### RECRUIT VARIANT (Rensei is not the starter)
**Join point:** `pleasant_eaves`, the muddy street. S03's beating plays as the party first enters. Rensei, in new
yojimbo armour beside a plain palanquin, makes the Ebisu choice. Then talk to him:
RENSEI: (bowing exactly as deep as protocol requires) Kakita Rensei, yojimbo to the Lady Sanae. Forgive the scene.
RENSEI: My lady's business is in that forest. I am told it is… dangerous. (beat) I am told I am adequate.
LADY SANAE: (from the palanquin) He means he would be grateful for company. He hasn't learned to say so yet.
> CHOICE "Travel with Rensei?" → Yes: **Memory** (S01–S02: the graduation bout without the battle, "Adequate", the
  road with Sanae, Seigen riding up; Seigen joins as guest) → resume at S03's "Heaven's Glory" reveal.
→ No: he waits by the palanquin.

---

## S01 — The Over-Sharpened Sword
MAP: `kakita_academy` (morning, graduation) · TRIGGER: new game, Rensei chosen
NARRATION: The Kakita Dueling Academy. Where the Crane teach that a single cut, perfectly made, ends any war.
(A courtyard of white sand. Rensei kneels, then rises into the graduation kata: slow, flawless, his white-dyed hair
tied high.)
SENSEI: Kakita Rensei. Final bout. Bokken.
SENIOR STUDENT: Try not to cry when you lose, little brother.
RENSEI: (bowing exactly as deep as protocol requires, no deeper) I'll try not to make you, senpai.
[BATTLE b_bokken_bout]
### TUTORIAL (b_bokken_bout)
- T1: "**Iaijutsu** — your Talent. **Focus** skips your action and builds a stack."
- T2: "At full stacks, **Strike**: one perfect cut. A full-Focus Strike always lands a critical."
- T3 (if the player Strikes too early): "Patience. The Kakita say the sword is drawn only once."
(The senior student's bokken spins out of his hands. Silence. Then polite, approving murmurs.)
(On the veranda, KAKITA MASANORI — Rensei's father — watches with no expression at all.)
KAKITA MASANORI: Your left foot hesitated.
RENSEI: (very still) Yes, Father.
KAKITA MASANORI: On the third step. A quarter-breath.
RENSEI: Yes, Father.
KAKITA MASANORI: Adequate.
(He walks away. The courtyard empties. Rensei stays.)
(Montage: dusk. Rensei performs the kata again. Again. Again. The left foot does not hesitate.)
(Night. He performs it again anyway.)
RENSEI: (alone, to the empty sand) …Adequate.
[SAVE]

## S02 — The Keeper of the House Honour
MAP: `road_west` (palanquin) · TRIGGER: auto
(A plain palanquin on a mountain road. Rensei walks beside it in his new yojimbo's armour, rigidly correct.)
LADY SANAE: (from inside, without opening the screen) Kakita Rensei.
RENSEI: My lady.
LADY SANAE: You may stop walking as though your spine were a spear. We have four days of road.
RENSEI: Yes, my lady. (He does not stop.)
LADY SANAE: (the screen slides open: a calm, tired, observant woman in her forties) Do you know what I do, Rensei-san?
RENSEI: You are Doji Sanae, Keeper of the House Honour, my lady.
LADY SANAE: And what does the Keeper of the House Honour do?
RENSEI: (pause) …Keep it, my lady?
LADY SANAE: (a faint smile) I see to it that certain things never happened.
LADY SANAE: A Kakita prodigy named Kakita Morishu shamed his house a year ago and vanished.
LADY SANAE: Now a Lion lord near Beiden Pass complains of a "Crane bandit" in his forest.
LADY SANAE: We are going to make the problem disappear. Quietly.
RENSEI: And my part?
LADY SANAE: You keep me alive while I arrange it.
(A man rides up alongside on a tired horse: grey-bearded, reading a battered notebook in the saddle — KITSUKI SEIGEN.)
KITSUKI SEIGEN: The boy looks terrified, Sanae.
LADY SANAE: The boy is terrified, Seigen. It's his first assignment.
KITSUKI SEIGEN: (not looking up) Good. Terrified men notice things.
RENSEI: You are… Dragon, sir?
KITSUKI SEIGEN: Retired magistrate. Kitsuki. I solve the Crane's embarrassments for money and bad tea.
RENSEI: The Academy taught us that the Kitsuki method—
KITSUKI SEIGEN: They teach nothing useful at the Academy. That's why it's so expensive.
[GUEST +Kitsuki Seigen] (skill "Evidence": reveal weakness and next move, 2 uses)
RENSEI: (internal) …What if what "never happened" did happen?
LADY SANAE: (as if she heard) Then you will learn something they don't teach at the Academy.
[SAVE]

## S03 — Pleasant Eaves (village hub, dusk)
MAP: `pleasant_eaves` · TRIGGER: arrive at dusk
NARRATION: Pleasant Eaves of Mountains' Cloak Forest Village. A long name for a short street.
(Shouting. Village youths kick a thin man curled in the mud: EBISU, an eta firewood-gatherer, clutching a cloth bundle.)
VILLAGE YOUTH: Eta filth! Where'd you steal a sword?
EBISU: (whimpering) Found! Found it! By the water! Wanted… wanted sake…
> CHOICE "Stop them"
  - [PA Charm] "Would you strike a man before a Kakita blade?" (Etiquette)
      RENSEI: (stepping between, very formal) Would you shame yourselves before a Kakita blade, gentlemen?
      VILLAGE YOUTH: (seeing his mon, backing off) A Crane… Sorry, my lord. Sorry.
      [SET ebisu_saved_how charm]
  - "Draw your sword." → (the youths flee; Honor −1)
      [SET ebisu_saved_how steel]
  - "Pay them to stop." → (−50 zeni)
      RENSEI: (offering coins, crimson with embarrassment) Please. Buy yourselves… dinner. Elsewhere.
      [SET ebisu_saved_how coin]
(Ebisu unwraps the bundle with shaking hands. A wakizashi in a plain scabbard. Rensei draws it a finger's width.)
(The steel catches the dusk. For a moment the whole street seems to reflect in it — and Rensei sees himself,
measured against something perfect, and falling short.)
RENSEI: (barely breathing) …*Heaven's Glory Reflected in the Soul's Steel.*
KITSUKI SEIGEN: (lowering his notebook) You know it?
RENSEI: Every Kakita student knows the name. It was made by the first Kakita's own student. It belongs to…
RENSEI: (quiet) To Kakita Morihoshi's house. To his son.
LADY SANAE: (very calm) To the boy we came to make disappear.
[ITEM +Heaven's Glory (key item — cannot be equipped)]
(The village headman, TORISHIGAWA, an unremarkable old man, watches from his doorway — very attentively.)
(Across the street, a young woman in Matsu colours sets down a pilgrim's staff: MATSU KIKU.)
MATSU KIKU: That eta will be beaten again the moment you leave. I'm Matsu Kiku. I'm going your way.
RENSEI: You don't know our way.
MATSU KIKU: Into that forest. Everyone who looks at that sword goes into that forest. (beat) Please let me come.
MATSU KIKU: (quieter) I'm on pilgrimage. I'm trying not to hit anyone. It would help to have someone to stand behind.
[GUEST +Matsu Kiku] (skill "Battle-Joy": big damage, then she's debuffed, 1 use)

### Town NPCs — `pleasant_eaves`
| NPC | Default line | Info (path actions) | Path action |
|---|---|---|---|
| Ebisu | "Found it by the waterfall. Shiny. Want sake…" | *Discern:* "Found the sword in a glade by a waterfall, a day ago." | *Charm:* leads you to the glade marker |
| Torishigawa (headman) | "The forest is dangerous, my lord. Bandits." | *Discern:* "He knows exactly where the bandits are." | *Charm:* fails ("I'm only a simple headman.") |
| Innkeeper | "One room. One futon. Crane eat last, Lions first." | — | *Barter:* rice balls |
| Old woman | "The Green Ronin? He gives back what the Lion take." | — | — |
| Youth (bruised) | "We didn't mean anything by it." | — | *Sumai:* win → he apologises to Ebisu (Honor +1) |
| Torishigawa (again) | — | *Eavesdrop:* "Let the Crane through if they come gently." (at the back door, to a runner) | — |
| Old woman (again) | — | — | *Bless:* follows ("Green Ronin's Blessing", small party heal, 1 use) |
| Innkeeper (again) | — | — | *Pilfer:* Fine Sake |
| Lion tax-collector (gate) | "Taxes are Heaven's order, Crane." | — | *Duel* (Iaijutsu 1): Glory +1 |
| Peddler | "Lion goods, Lion prices." | — | shop: Lion T1 |

## S04 — The Ghost Maiden (forest dungeon, night)
MAP: `mountains_cloak_forest_1` · TRIGGER: enter forest
NARRATION: Mountains' Cloak Forest. At night, the lanterns come out.
(Paper lanterns drift between the trees, glowing, swaying — too evenly. A weeping voice from deep in the woods.)
GHOST MAIDEN (offscreen): Help me… I've lost my way… help me…
MATSU KIKU: (gripping her staff) That's a ghost.
KITSUKI SEIGEN: That's a girl with a good voice and a rope.
RENSEI: How can you tell?
KITSUKI SEIGEN: Ghosts don't cough. Listen.
GHOST MAIDEN (offscreen): Help me… (tiny cough) …help me…
### INTERACTION POINTS (fit conversion of the lantern puzzle)
- R1 (a rope tied to a tree): "A pulley line. The lanterns ride on it. **Cut it?**" → cut: one lantern drops; a
  bandit swears in the dark.
- R2 (a second line, near a fresh-dug patch): "Another line — and the ground ahead is too soft. **Cut it and go
  around?**" → reveals the **pit trap**.
- R3 (the "ghost" lantern): "The last lantern. Behind it, a girl on a branch with a rope." → cut → she falls into a
  bush, unharmed; her twin sister rushes out.
[BATTLE b_forest_bandits_a] (bandits; they surrender at low HP → [SET forest_village_spared] if no bandit is killed)
### Battle barks
- BANDIT (surrendering): "Mercy! We're farmers! We're just farmers with sticks!"
- RENSEI: "…Then put the sticks down."
MAP: `mountains_cloak_forest_2`
(A clearing. Two Crane samurai stripped to their underclothes, tied to a tree: KAKITA ADORU, furious, and KAKITA
YASURUGI, utterly silent.)
KAKITA ADORU: You! Crane! Untie us at once! We are on our lord's business!
RENSEI: What business?
KAKITA ADORU: Our lord's! Untie us!
KITSUKI SEIGEN: (picking a letter up from the leaves) Their lord's business, it seems, involves this.
(He reads. His face goes still.)
KITSUKI SEIGEN: It's from Kakita Morihoshi to his son. Very polite. Exquisite brushwork.
KITSUKI SEIGEN: It invites him to cut his own belly.
(Silence. Rensei looks at Yasurugi. Yasurugi looks back: the calmest look Rensei has ever received, and the coldest.)
LADY SANAE: (arriving, reading the letter over Seigen's shoulder) …Untie them. Gently. Return their swords.
RENSEI: My lady—
LADY SANAE: Return their swords, Rensei-san. They are Kakita. We do not leave Kakita tied to trees.
(Yasurugi takes his sword and walks into the dark without a word.)
[SAVE]

## S05 — The Green Ronin's Village
MAP: `bandit_village` · TRIGGER: follow the bandits' trail (or be led, if `forest_village_spared`)
(Not a bandit camp: a hidden village. Children. Rice paddies cut into a hillside. Forty people who don't belong to
anyone.)
[IF forest_village_spared]
BANDIT (from S04): It's them — the Crane who cut the ropes instead of throats. Let them through!
[ELSE]
(Spears level at the gate.)
[BATTLE b_forest_bandits_b] (they surrender by turn 3)
(A big jovial man pushes through: IMURO, a Bo across his shoulders.)
[END]
IMURO: Crane! In the Green Ronin's village! Have you come to arrest us or to have tea?
RENSEI: Is… tea an option?
IMURO: (laughing enormously) It is now! Sit!
(A tea mat. A pregnant young woman serves it with shaking hands: SARIKO.)
IMURO: I am the Green Ronin!
KITSUKI SEIGEN: No, you aren't.
IMURO: …No, I'm not.
IMURO: (lowering his voice) He's my friend. Kakita Morishu. When he came here he couldn't hold a cup without spilling it.
IMURO: Then two Lions came to beat our headman for a late tax. He killed both with two cuts. Two. Like breathing.
IMURO: Then he sat down in the mud and shook for an hour.
RENSEI: (very quietly) Two cuts… and then he shook.
IMURO: You understand that?
RENSEI: (beat) …I understand the second part.
SARIKO: (setting the pot down too hard) Where is he? He went into the forest at dawn and didn't come back.
(A runner bursts in, out of breath.)
RUNNER: Imuro! Lord Goroso's sergeant — Akodo Tama — he caught Morishu at the waterfall!
RUNNER: He's to be executed in the castle yard. At dawn tomorrow.
(Sariko's cup falls and breaks.)
[SAVE]
### Travel Banter (village inn mat) — TB-crane1-a "Spilled Tea" (Rensei + Kiku)
MATSU KIKU: You flinched when he said "shook for an hour".
RENSEI: I did not.
MATSU KIKU: You did. I flinch at things too. Mostly at myself.
RENSEI: (pause) …What do you do about it?
MATSU KIKU: Walk a very long way on pilgrimage and hope it falls off somewhere.

## S06 — Castle on the Made Hill
MAP: `goroso_castle_hall` → `goroso_castle_corridor` · TRIGGER: travel to the castle
NARRATION: Lord Akodo Goroso's castle stands on a hill raised by ten thousand peasant baskets. It guards Beiden Pass.
(The hall. LORD AKODO GOROSO: scarred, two fingers missing, utterly certain. Sanae kneels before him. Rensei kneels
at the back, by the door. Goroso does not look at him once.)
AKODO GOROSO: The Crane send their Keeper of Honour to plead for a bandit.
LADY SANAE: The Crane send their Keeper of Honour to understand, my lord. A Kakita in your cells is a Crane matter.
AKODO GOROSO: A bandit in my cells is my matter. Heaven has an order. He broke it. He dies at dawn.
(Sanae is dismissed. Rensei is told to wait in the corridor. He waits. He is ignored.)
(In the corridor: two voices, around a corner. A "merchant" with swords under his cloak — BAYUSHI DEPURA — and the
sergeant, AKODO TAMA.)
BAYUSHI DEPURA: A public execution would be so… *instructive*, sergeant. For the Crane. For everyone.
AKODO TAMA: The lord's already decided.
BAYUSHI DEPURA: Then let's make sure nobody undecides him. A Crane's body in a Lion yard — imagine the poems.
(Depura passes Rensei on his way out. He glances at the boy in white, smiles politely, and forgets him instantly.)
RENSEI: (internal) …He looked straight at me and didn't see me.
RENSEI: (internal) Father always said a Kakita should fill a room. (beat) It's useful to be empty.
[SET depura_seen]
### Charm targets in the castle (optional)
- **Seoko** (Goroso's daughter, idealistic Akodo student) — [PA Charm] → she can open the cells:
  SEOKO: My father isn't cruel. He's… certain. (beat) Certainty is worse. [SET seoko_charmed]
- **Lady Tatanko** (Goroso's wife) — [PA Charm] → she admits the runaway villagers cost the estate; she'd accept a
  solution that brings the labour back.
[SAVE]

## S07 — Four Ways to Dawn
MAP: `goroso_castle_corridor` (night, the guest room) · TRIGGER: after S06
LADY SANAE: There are four ways this ends, Rensei-san. I will tell you all four, and then you will choose.
LADY SANAE: One. A blade slipped into his cell. He takes the honourable path tonight. The House is clean.
LADY SANAE: Two. We do nothing. He dies in the yard. The House is shamed, but not *involved*.
LADY SANAE: Three. His bandit friends strike from the crowd. Goroso is humiliated. The Lion will remember.
LADY SANAE: Four. We demand trial by challenge. Goroso names a champion. Morishu fights for his own life.
RENSEI: He can't hold a cup without shaking.
LADY SANAE: Then he will need a second.
RENSEI: (beat) …You're deciding what kind of Crane I am.
LADY SANAE: No. *You* are. Take your time. You have until dawn.
> CHOICE "Dawn"
  - "A blade in the cell." → [SET dawn_route 1]
  - "Let the law take its course." → [SET dawn_route 2]
  - "Help the bandits strike." → [SET dawn_route 3] (if `seoko_charmed`: Seoko opens a side gate)
  - "Demand trial by challenge." → [SET dawn_route 4] (recommended)

## S08 — The Silent Blade (BOSS)
MAP: `castle_yard` (dawn) · TRIGGER: after S07
[IF dawn_route 4]
(The castle yard. A crowd. Morishu, thin and grey, is brought out in ropes — and Rensei sees a man who is *exactly*
what his father fears he will become.)
AKODO GOROSO: The Crane demand trial by challenge. So be it. Heaven will choose.
AKODO GOROSO: I name my champion. (beat) A Kakita, at his own request.
(Kakita Yasurugi steps into the sand.)
KAKITA MORISHU: (barely audible) …I can't. I can't lift it. I'm sorry. I'm so sorry.
RENSEI: (stepping forward, bowing to Goroso) My lord. Kakita Morishu names a second.
AKODO GOROSO: Who?
RENSEI: (beat) Me.
[ELSE]
(Route 1: `goroso_cells` — Yasurugi waits in the dark by Morishu's cell. Routes 2–3: `castle_yard` (route 3 at the
side gate) — Yasurugi steps out of the crowd to finish his lord's business.)
[IF dawn_route 2] KITSUKI SEIGEN / MATSU KIKU (whoever is present): "He means to kill him before the executioner can.
So the Kakita name dies by a Kakita hand." RENSEI: "…Not like this." [END]
KAKITA YASURUGI: (silent; he only draws)
RENSEI: (drawing) Then I'll stand in your way.
[END]
[BATTLE b_boss_yasurugi]
### Boss barks / structure
- Phase 1 (duel UI): no words. The wind. Two breaths.
- If Rensei Focuses too long: (Yasurugi Strikes first — a red flash) MATSU KIKU: "Rensei!"
- Phase 2 (skirmish), RENSEI: "You hesitated once, didn't you? With a peasant." (Yasurugi's guard flickers.)
- At 25%: KITSUKI SEIGEN: "His left side, boy. He favours it."
- Defeated, KAKITA YASURUGI: (lowering his sword; his only line in the game) …Better.
(He bows to Rensei — a full bow — and walks out through the crowd. Nobody stops him.)

## S09 — And Everything Passes
MAP: `castle_yard` → `road_west` · TRIGGER: after the boss
[IF dawn_route 4]
AKODO GOROSO: (long silence) …Heaven has spoken. The ronin lives.
AKODO GOROSO: The village in my forest — it is under his protection now. And under my taxes.
TORISHIGAWA: (bowing low beside Sanae, too low for a simple headman) Most generous, my lord.
LADY SANAE: (bowing back to the headman, very slightly) Most generous.
(Morishu, untied, stands in front of Rensei with the sword Heaven's Glory held out in both hands.)
KAKITA MORISHU: It shows you what you should be. I can't bear to look at it anymore.
KAKITA MORISHU: You still can. Please.
[ITEM Heaven's Glory → equippable later (locked until Rank 2)]
[ELSE IF dawn_route 1 OR 2]
(Morishu dies. Sariko's cry carries across the yard. Sanae returns the sword to its box for the Kakita vaults.)
[ELSE IF dawn_route 3]
(Chaos in the crowd. Morishu escapes into the forest for good — with Heaven's Glory. Goroso writes to the Crane that
night, in a fury that will feed the coming war.)
[END]
(On the road east. Rensei walks beside the palanquin. For once he is not walking like a spear.)
RENSEI: My lady. The letter. The death poem. Would my father ever…
LADY SANAE: Your father is a hard man who would never write such a letter.
LADY SANAE: (beat) That is why I make sure no one ever has to find out whether that's true.
RENSEI: (quiet) …Is that what you'll write in your report? That nothing happened?
LADY SANAE: (smiling) You learn quickly. The Academy will be furious.
KITSUKI SEIGEN: (from his horse) I told you they teach nothing useful there.
[CHAPTER COMPLETE]
### Chapter complete card
**"Heaven's Glory" — complete.**
Journal: *Sent to make a fallen prodigy disappear, Rensei found a man who could cut twice and then shake for an
hour — and stood beside him.*

---
## Travel Banter unlocked by Crane Ch1
### TB-crane1-b "Adequate" (Rensei + Shizue)
SHIZUE: Your father said "adequate" to you? After a perfect graduation?
RENSEI: He also noted my left foot.
SHIZUE: My uncle once praised me by saying nothing for an entire meal. I treasured it for a year.
RENSEI: (pause) …Is that what silence means? Praise?
SHIZUE: In noble families? Usually. Sometimes it's indigestion.
### TB-crane1-c "Two Cuts" (Rensei + Natsuko)
NATSUKO: You're scared of becoming the shaking man.
RENSEI: (stiff) I don't know what you mean.
NATSUKO: Everyone on the Wall shakes after. The ones who don't are the ones to worry about.
RENSEI: (pause) …Truly?
NATSUKO: Truly. I shake every time. Then I eat something. Try it.
