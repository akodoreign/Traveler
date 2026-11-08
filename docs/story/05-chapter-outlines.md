# Story Bible — 05: Scene-level outlines for the thin chapters (DRAFT v0.1)

These expand the chapters `02-travelers.md` marked as thin or original. Format per scene:
**place · what happens · systems used** (path actions, talents, guests, rules docs). Recommended levels follow
02-travelers: Ch1 ≈ 1–10, Ch2 ≈ 20–25, Ch3 ≈ 30–35, Ch4 ≈ 40–45.
- Static NPCs keep their source names. Original NPCs are marked *(orig.)*.
- Rank-1 rule: great lords treat the travelers as nobodies.

---

## LION — Akodo Shizue

### Ch3 · "The Deadly Message" (Rank 2, ≈ Lv 30–35) — Adventure Ideas hook + orig.
Theme: *Honor is what you answer for when no one is watching.*

| # | Scene | Systems |
|---|---|---|
| 1 | **Shiro Akodo, spring thaw.** Not Toturi but his karo, **Akodo Kagehisa** *(orig.)*, hands Shizue a lacquered tube with Toturi's seal. Orders: speak to no one; deliver it to "the old man of Kaze-no-Tani" in the mountain foothills. The audience lasts three lines. She realises she was chosen because a Rank 1 messenger is expendable. | Rank-1 rule; Glory check (doors close) |
| 2 | **Village of the Burned Bridge** *(orig.)*: Lion refugees from Crane border raids. A bandit chief holds the ford toll. | **Duel** path action (bandit chief); **Akodo Ijako** joins as guest (sodan-seizo cousin, *Call the Dead*) |
| 3 | **An "Imperial courier inspector"** with Miya papers asks to examine sealed messages "for the Emperor's safety". Refusing politely costs nothing. Refusing rudely brings a Glory hit. | Etiquette check; foreshadows **Miya Yachiko** (Ch1) |
| 4 | **Waystation in a sleet storm.** The tube cracks in the cold. The seal is broken, and inside are three words in Toturi's hand: ***"Kill these messengers."*** Party banter, if present: Gendo ("evidence is testimony"), Mitsue ("burn it"), Rensei ("deliver it — that is the point"). | Tea/inn banter; **Honor choice flag** |
| 5 | **A roadside shrine.** Ijako speaks with an Akodo ancestor: "A message is a blade. Who holds the hilt?" A hint that someone else is hunting them. | Ijako's guest skill; Ancestral Guidance (if Haruki is present) |
| 6 | **The pass ambush.** "Bandits", actually ronin paid in Imperial coin. Discern / Eavesdrop / Interrogate reveals a Miya travel writ and a letter to a *Crane* general in the same hand. | Battle; **Discern / Eavesdrop / Interrogate**; enemies may surrender (Cite the Law) |
| 7A | **Deliver it anyway** (the honour path). **Kaze-no-Tani hermitage.** The retired sensei **Akodo Shōgen** *(orig.)* reads it and laughs: "Toturi remembers." It is an old Akodo test: he only teaches those who deliver *knowing* what it says. **Boss: Shōgen, a test duel** (iaijutsu opening → kata stances; he uses *Fury Without End*). He agrees to come down from the mountain. | **Duel boss**; reward: battle skill **Read the Field** early + story Advantage *Strategist's Eye* |
| 7B | **Destroy it / turn back.** Yachiko's hired killers have been told to make sure the message *never arrives*, whatever she chooses. **Boss: the Miya killers** (a Seppun-trained duelist + archers). Back at Shiro Akodo the karo says she failed the test but proved loyal. Shōgen never comes, so Ch4's battle is harder (no advisor buff). | Boss battle; branch flag `shogen_joined` |
| 8 | **Both paths:** the killers' letters prove **Miya Yachiko is feeding both armies** false reports, to keep the clans bleeding so none can challenge the Hantei (The Blood of Family canon). Toturi reads the evidence in silence and says one word: "Again." | Sets up Ch4; Yachiko escapes (Imperial status protects her) |

### Ch4 · "Sorrow's Path" (Rank 3, ≈ Lv 41–45) — orig.
Setting: **Kanashimi no Komichi** (Sorrow's Path), the old Lion–Crane battlefield. Matsu Joruri's victory is painted in
Shiro Akodo's mural, and the **Crane banner the oni stole in Ch2 was taken here** (Shadow of a Doubt). Both armies
are back on the same ground.

| # | Scene | Systems |
|---|---|---|
| 1 | **Lion camp at the ford.** Uncle **Akodo Hiruto**'s contingent; cousin **Akodo Gusai** (who started the war in Ch1) eager to charge; the Matsu vanguard under champion **Matsu Rokuro** *(orig.)*. Shōgen advises if he joined. | Camp hub; `shogen_joined` → party buff |
| 2 | **The forged apology.** A Crane apology letter delivered at night was swapped for an insult. Every witness describes a lovely courtier **with blue eyes**. | Discern / Eavesdrop clue minigame |
| 3 | **"She uses the same method twice."** (Nashiko's vanity, Of Family and Honor.) So the *Lion's* conciliatory letter to the Crane was surely swapped too. Someone must cross the river before dawn. | Deduction choice |
| 4 | **The go-between:** if Rensei is recruited, he crosses under a truce flag (a crossroads beat; both travelers' banter). Otherwise **Daidoji Atsuko**, the Crane spy Shizue cleared in Ch2, repays the debt and goes. | Crossroads hook; Ch2 payoff |
| 5 | **Night:** Matsu Rokuro has been ridden by one of Nashiko's errand-demons (Fear-type). He will charge at dawn regardless. Gusai wants to join him for glory. Shizue must persuade or out-rank her cousin. | **Duel** (Gusai, non-lethal) or Command dialogue |
| 6 | **Dawn: hold the ford.** A battlefield event chain in waves: Matsu berserkers by mistake, a Crane counter-charge, a burning bridge. Hold for N turns while the go-between reaches the Crane general. | Defence-wave battle; **Command**, Akodo Formation, Battle Cry |
| 7 | **Boss: the possessed Matsu champion.** Weak: jade, and **obsidian** (Fear), but obsidian Taints whoever uses it: an obsidian blade found in Gusai's tent is the tempting shortcut. His terror aura hits both armies. Breaking the possession frees Rokuro alive. | `enemies.md` Shuten-type rules; Courage of the Seven Thunders helps |
| 8 | **Mid-ford:** the two generals meet. The battle stops; the war does not. Shizue reports truthfully that **the Lion charged first** (her own cousin), knowing it costs her house Glory. *Honor when no one is watching* is now a choice everyone watched. | Honor +, Glory −; finale virtue seeded |
| 9 | **The courtier's empty tent:** a Crane court mask, white hair-dye, a smooth stone carved like jade (she is colour-blind). The trail points north and east → finale. | Shared Nashiko clue set |
- **Ending beat:** "I could not stop the war. Only one battle." — "One is enough today."

---

## PHOENIX — Isawa Haruki

### Ch1 · "The Silent Kami" (Rank 1, ≈ Lv 1–10) — The Blood of Family (Phoenix side) + orig.
| # | Scene | Systems |
|---|---|---|
| 1 | **Shiro no Kamatori** (five towers, copper-edged walls that look built of fire at sunset). Haruki copies teacher **Isawa Hoju**'s unfinished family history; Hoju teases him about counting elements on his fingers. | Tutorial: field spells **Sense / Commune / Summon** |
| 2 | **Night:** Hoju dies at his desk, bleeding from the eyes (maho). The castle-garden kami fall **silent**, and Commune fails. | Spirit-wasteland debuff (spells −1 tier on this map) |
| 3 | **Isawa Kamasari** (Hoju's arrogant nephew) blames the Lion. The Phoenix envoys leave west with the Imperial magistrate **Miya Yachiko**; Haruki goes as the lowest member, carrying scrolls. | Rank-1 rule |
| 4 | **Hoju's study:** the history names a Bloodspeaker bound a generation ago by killing the young shugenja **Kaiki**. Haruki finds the **jade chains**: their lock grows cold near the spirit. | Key item: **jade-chain compass** (hot/cold map search) |
| 5 | **Magonojo river:** the burned warehouses from the Lion raid. Haruki discovers the Phoenix were **secretly supplying the Crane army**. His clan's hands aren't clean. | Discern-style Reflections of Pan Ku on the ashes |
| 6 | **A despoiled shrine:** a restless spirit; yojimbo **Shiba Ashimita** (haunted since birth by his grandfather's screaming ghost) is assigned to Haruki. | Guest: Shiba Ashimita; pair kata *Eyes of the Phoenix* teased |
| 7 | **Akodo Hiruto's castle** (crossroads with Lion Ch1). Mid-boss: the ghost **Ashimoshi**, a samurai trapped in a silent hurricane. | Boss 1 |
| 8 | **Climax (shared with Lion Ch1):** **binding O-Tamai** with the jade chains. If Shizue isn't recruited, Akodo Ijako stands in. **Boss: O-Tamai's red-shadow oni** (soul damage = SP drain). | Boss 2; `enemies.md` maho rules |
- **Ending beat:** among Hoju's papers, a child's note in Haruki's own hand from twelve years ago: "I'm sorry, Mieko." Nobody
  else knows what it means.

### Ch3 · "The Darkfever" (Rank 2, ≈ Lv 30–35) — canon 1123 event + orig. (replaces "The Ashes of the Snake")
**Canon basis** (3e core timeline and *Imperial Histories* ch. 5): in 1123 a solar eclipse frees **Oni no Kuzushi**
after two centuries of confinement. It stays bound to a forgotten Isawa estate deep in the Isawa woodlands and spreads
a magical plague, later called the **Darkfever**; many die before "clever magistrates" find and destroy it.
- **Our addition:** the estate is the **Mieko family's forest house**, where eight-year-old Haruki's Void outburst
  split Mieko's soul. That night it also **cracked the oni's seal**; the eclipse finished the job. His childhood
  wound has a body count.
- ✅ Decided (user): the oni keeps its canon name. The Break mechanic was renamed **Suki** to avoid the clash. Its
  gimmick still fits its name ("unbalancing"): it knocks the *party* off balance.

| # | Scene | Systems |
|---|---|---|
| 1 | **The eclipse at Kyuden Isawa:** two murders at the memorial court (Ch2) still point at Mieko. During the eclipse every kami in the city shrieks. Within days, fever villages. | Story |
| 2 | **Healer's crisis:** plague towns; Haruki and (if recruited) Sayo treat the sick. Mechanic: a triage minigame with limited SP and Remedy ingredients, and choices about who to save first. | **Hand of Jurojin** unlock (ML4: early, as a story-granted spell); Sayo's Remedy |
| 3 | **The Council's hubris:** the Elemental Masters blame "peasant uncleanliness". Isawa Rujo (Master of Earth, about to be forced to abdicate) brushes Haruki off. | Rank-1 rule; canon colour |
| 4 | **An Emerald magistrate's yoriki** *(orig.: Doji Hayato, a tired Crane)* is the only official listening. Haruki becomes his guide: the "clever magistrates" of canon. | Investigation; Discern if Gendo is present |
| 5 | **Mapping the plague:** the infection spreads outward from one point in the forest. Haruki recognises it: the house where it happened. | Reflective Pool / map reveal |
| 6 | **The forest estate:** rotting gardens; a child's go board left mid-game; ghostly replays of that night. **Mieko's dark half** is here, drawn to the place of her breaking. First clash; she escapes, laughing that he "broke more than me". | Mid-boss: Mieko's dark half |
| 7 | **Boss: Oni no Kuzushi.** Gimmick: its *Unbalancing Breath* **leaves a traveler "Off-Balance"** (that traveler skips their next turn: the party's own Suki), and it **refills its Resolve** each time. The party must cleanse or guard-swap to keep their footing. Weak to Jade, Water, Bo. | `enemies.md` oni rules |
| 8 | **The sealed library (reward):** for ending the plague, the Council grudgingly opens the sealed archive. Haruki reads how souls are split and joined, and the record of the **Snake Clan**'s destruction by a Shuten Doji (obsidian / jade / crystal: the Unicorn crossroads hook). The Master of Air grants him the secret spell ***Dreamwalker***. | First Tier spell reward; Unicorn hook |
- **Ending beat:** the magistrate's report credits "the Isawa"; Haruki's name is left out. He's relieved. He knows
  now what Ch4 will cost.

---

## RONIN — Sayo

### Ch2 · "The Noble and the Ronin" (Rank 2, ≈ Lv 20–25) — Adventure Ideas hook + Entanglements & Tied Snakes
| # | Scene | Systems |
|---|---|---|
| 1 | **The Tōkaidō-like river road.** A spoilt young lord, **Ikoma Sadanobu** *(orig.; a Lion governor's son)*, has his retainers beat a devout ronin pilgrim, **Jinnai** *(orig.)*, then shouts for help "apprehending the criminal". Sayo, nobody to anyone, steps between them. | Tutorial: Low vs. High skill; **Pilfer** Sadanobu's travel writ (Honor −) or Sumai-less bluff |
| 2 | **Branded a bandit:** wanted posters in two towns. Sayo and Jinnai flee on a rice barge; she patches his ribs. Jinnai's prayer beads are carved with a tiny snake. | Remedy tutorial (`sayo-remedy.md`); Jinnai as guest |
| 3 | **Village of Floating Flowers** (a river stop between Crab, Scorpion and Sparrow lands): soap-opera villagers; a sleazy Yasuki merchant in love with a branded eta woman (Sayo's old patient); the geisha-house Madame from Ryoko Owari; the beloved harbourmaster. | Side-quest hub; Barter/Pilfer economy |
| 4 | **Sadanobu's retainers arrive in force.** A storm battle on the jetties: the "storm of retainers". If Sayo spares them, the village shelters her. | Battle; enemies surrender at low HP |
| 5 | **The snake den under the harbourmaster's floor mats.** The **Order of the Snake** is no cult. It is a century-old society that removes *usurpers* and protects true lines. Jinnai is one of them. | Discovery |
| 6 | **"Only Snakes may pass":** the trap room. Crawl on your belly through white sand, or be bitten by shadow-snakes. Samurai party members lose face (Honor −) unless they crawl. **Sayo doesn't care.** | Puzzle; Honor choice per party member (comic) |
| 7 | **The stone serpent's mouth → the judgement.** A bodiless voice weighs Sayo and finds her "of no line at all — therefore free to carry what no line can". | Story |
| 8 | **Boss: cult enforcers** who think she's a spy (shadow-snake summons). Jinnai stops the fight. His house guarded a secret on the Mountain of the White Snow, and he is the last. He's dying of an old wound. | Boss; Jinnai's Ch3 hand-off |
- **Ending beat:** Jinnai gives Sayo his beads: "The Order is not my secret to give. The mountain is." → Ch3.
- ✅ Jinnai is a **monk guest** (user decision): a lay brother of the Order of Osano-Wo carrying martial kiho
  (kiho.md §2). He survives his wound. He hands Sayo the Ch3 task, then reappears in **finale Act 1** defending his
  order's **Shrine of Osano-Wo**.

### Ch4 · "The Oracle's Choice" (Rank 3, ≈ Lv 41–45) — canon 1123 + orig.
**Canon basis** (*Imperial Histories* ch. 5): the Oracle of Fire prepares to leave his body for the Fire Dragon's
court. His chosen successor appears to be **a young eta woman**, which has immense theological consequences.
**Scorpion agents** try to manipulate the choice; their schemes are "complicated by the actions of traveling samurai
in the area". They fail, and the chosen successor takes the mantle.

| # | Scene | Systems |
|---|---|---|
| 1 | **A volcano-side shrine town** (the Oracle's seat). Pilgrims in their thousands. **Akari** *(orig.)*, the eta woman Sayo once nursed through fever, sends for her: "The fire talks to me. I'm scared." | Hub; reunion |
| 2 | **Three factions arrive:** Scorpion agents who want a different successor; Order of the Snake scouts who want to use Sayo's Ch3 secret ("blood means nothing") to bring down a lineage; temple priests who want the eta girl gone quietly. | Faction dialogue; Eavesdrop (Mitsue), Discern (Gendo) |
| 3 | **The eta quarter:** samurai can't enter without defilement. Sayo walks in. **Ume-baa** (her mentor) and **Hiro** (giant eta undertaker, guest) help hide Akari. | Guest: Hiro; **Anatomy** unlock from Ume-baa (`sayo-remedy.md` §4) |
| 4 | **The poisoned well:** the Scorpion try to make Akari "unclean" in a way the priests can't ignore. Sayo traces the poison. | Remedy: Rhubarb/Antidote; Poison skill (craft the counter) |
| 5 | **The blue-eyed woman** whispers to every faction in turn, wearing a different face each time (she uses the same method twice). Sayo sees her because nobody hides from a ronin girl. | Nashiko clue; finale lead-in |
| 6 | **The temptation:** the Order offers to make Sayo "somebody": a name, a house, a place. All she has to do is hand over the Ch3 secret. **She refuses.** | Story choice (no wrong answer, but Sayo's virtue locks in) |
| 7 | **Night race to the crater shrine:** Scorpion assassins on the rooftops, then the **Great Naga's champion** (the Order's guardian, a naga warrior: honourable, not evil) blocking the stair. | Chase battles; **boss: the Naga champion** (can be *talked down* after Break → Honor +) |
| 8 | **The ascension:** a race, not a fight. Sayo gets Akari to the fire alive. The old Oracle ascends; **Akari takes the mantle.** Sayo gains **no Oracle powers** (user rule). | Cinematic; keepsake: **ember charm** (once per battle: a small Fire hit or a revive) |
- **Ending beat:** Sayo keeps the Ch3 secret for the villagers, not for any lord. She chooses her family at last: the
  other seven.

---

## CRANE — Kakita Rensei

### Ch4 · "The Play No One Performs" (Rank 3, ≈ Lv 41–45) — orig. (built on the Mirror, Mirror Nashiko facts)
Nashiko facts used: a Crane courtier centuries ago, abused by a stepfather; she sought justice by marrying above him,
the **Emerald Champion Doji Komatsu**, who jilted her for a prettier face; through maho she destroyed his court.
She is vain, wants to be called **Empress**, is **colour-blind**, fears **disfigurement**, can read only **one mind at
a time**, and **doesn't know a play was written about her**.

| # | Scene | Systems |
|---|---|---|
| 1 | **Kyuden Doji, after the border war.** Lady **Doji Sanae** (the "Keeper of the House Honour") orders Rensei to help bury a truth: the woman behind the Crab–Crane crisis (crossroads) was **a Doji**, and the same woman destroyed Komatsu's court four centuries ago. | Rank 3 now: doors open a crack |
| 2 | **The Kyuden Doji archives:** a library maze. A censor-monk guards the forbidden shelves. | **Charm** the archivist, or Watchful Falcon kata (Perception) |
| 3 | **The forbidden noh play** *(orig.: "The Empress of Nothing")*. Written by a survivor of Komatsu's court and banned ever since. It names her weaknesses: colour-blindness (the stone-for-jade scene), fear of disfigurement, the "Empress" title, one mind at a time. | Key item: **the play script**. It unlocks **finale debuffs** (each scene Rensei knows → a Nashiko Resolve shield is visible from the start) |
| 4 | **A rehearsal in secret:** Rensei recruits court actors to stage one scene, testing whether the play's "mirror trick" works. If Mitsue is present, she directs (a crossroads beat; she knows acting). | Mini-game: stage the scene (timing choices); Acting / Etiquette |
| 5 | **His father, Kakita Sadahiro** *(orig.)*, learns of it. The Kakita name must not be tied to a Doji demon. He commands silence and the burning of the play. | Story |
| 6 | **Sanae's test:** she asks whether he would rather keep the House's honour or save the Empire. There is no right answer, and she is watching which he chooses. | Choice flag |
| 7 | **Boss: his father in a formal duel** (non-lethal, first blood). The duel Rensei has feared all his life. Iaijutsu opening, then kata. His father uses *One Strike Blade* and *Kakita's First Stance*. If Rensei wins, the play survives. If he loses, Sanae secretly saves a copy. | **Duel boss** (Iaijutsu talent showcase; `kata.md`) |
| 8 | **Aftermath:** Sanae, unexpectedly, covers for him. "A sword that only cuts what it is told to is a very dull sword." | Ending beat |
- **Timing:** summer 1123 (Horse/Goat), like Lion Ch4. **Sorrow's Path** happens the same weeks. If both travelers are in the
  party, Rensei's crossing of the ford in Lion Ch4 happens *on his way* to Kyuden Doji.

---

## SCORPION — Shosuro Mitsue

### Ch4 · "The Eve" (Rank 3, ≈ Lv 41–45) — canon 1123 + Blood and Iron epilogue + orig.
**Canon basis** (*Imperial Histories* ch. 5): Bayushi Shoju, troubled by a prophecy that the last Hantei will doom the
Empire and urged on by the Bloodsword *Ambition*, decides on a coup. He visits the **Kami Togashi** in Dragon lands to
ask his guidance. Togashi's answer (paraphrased): *a bloodline will end, and if he succeeds the Empire will be saved.*
Shoju takes this as approval. A few months later, the Coup.

| # | Scene | Systems |
|---|---|---|
| 1 | **The Iron Box whispers.** Since Ch1 the Box holding Iuchiban's heart has spoken in Mitsue's sleep. Her sensei **Shosuro Norie** orders it destroyed in the only fire hot enough: **Tamori's Furnace**, in Dragon lands. | Story; the Box as a cursed key item (−1 VP at battle start until destroyed) |
| 2 | **The road north through Dragon country**, disguised as a pilgrim troupe. If Gendo is recruited, this is the **Tamori's Furnace crossroads** (03-crossroads). | **Many Faces** field disguise; Acting gates (`skills.md`) |
| 3 | **A dying Bayushi courier** in a mountain inn, carrying sealed orders to Scorpion garrisons: muster dates for the capital. He mistakes Mitsue's mask for a friend's. | **Eavesdrop** (his fever-talk) |
| 4 | **The Champion's procession** passes. Shoju is going to **Kyuden Togashi**. Mitsue, a Rank 3 nobody, joins the servants' train in a new face. | Disguise infiltration (stealth segment) |
| 5 | **The High House of Light:** she overhears Togashi's answer to her Champion: *a bloodline will end.* She is the only person in the game who knows what Shoju means to do. | **Eavesdrop climax** (can't fail: the scene is fated) |
| 6 | **Duty's knife:** report it (to whom? betray her clan?) or keep silent. She can tell no one, and the game forbids it: dialogue options to speak are greyed out. *Duty is the promise you keep when you know what it costs.* | Locked choice (a deliberate design beat) |
| 7 | **Tamori's Furnace:** **boss: the Bloodspeaker remnant hunting the Box** at the volcano's mouth. A maho-tsukai with a stolen face; Taint attacks; jade weakness. | `enemies.md` maho rules; Jade |
| 8 | **The Box goes into the fire.** If Gendo is present, he saw the courier's orders too, and keeps her secret (crossroads payoff). | Box destroyed → the cursed key item is removed |
- **Ending beat:** Mitsue gives the party a smile and a Scorpion "Favor" pendant each, then walks back toward
  Otosan Uchi. The Coup is *a few months* away (canon), at the start of autumn (3e calendar: Rooster ≈ October).
  The finale happens just before it.

---

## Still to outline (later)
- Weak-ish but source-backed chapters can wait for the scene-script pass.
- **Template chapter for the user's approval:** suggestion **Lion Ch2 "Shadow of a Doubt"**. It is the closest in
  tone to Octopath, has a clear festival structure and covers every system (Duel, minigames, jade prizes, a charm
  boss).
