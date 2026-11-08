# Story Bible — 04: Supporting Cast & Hireables (DRAFT v0.2)

Changes in v0.2 (user decisions 2026-10-16): **guests work like Octopath Traveler II**; **all pregen-derived
characters get new names** (source→new mapping kept in §B4 for traceability).

---

## A. Hireable systems

### A1. Guests (Octopath Traveler II model) — primary system
- **One guest at a time** travels with the party of four. Guests are **not** party members: they don't take a slot,
  don't level, and can't be controlled turn by turn.
- In battle a guest is used through a **"Call Guest" command** (any traveler's turn, costs that traveler's action). Each
  guest has **2–3 signature actions** with a **limited number of uses per battle**, refreshed after each fight; some have
  a stronger "once per rest" action.
- **How guests join:**
  - **Side stories** (most guests): help an NPC and they offer to travel with you.
  - **Story-locked guests:** some chapters attach a guest automatically for that chapter only (e.g. the boy-Emperor's
    guard captain in the Dragon's past chapter; Moto Benjiro in the Lion's Ch2 climax). They leave when the chapter ends;
    some can be re-recruited later via a side story.
- Each guest's **secret** unlocks a follow-up side story that upgrades one of their actions.
- Guest banter: lines change based on which travelers are in the party (hooks in §B3).
- Swap guests at **inns** (the guest waits there until fetched).

### A2. Followers (Octopath I "Allure/Guide") — via Path Actions
- **Crane (Charm)** and **Phoenix (Bless)** can lead town NPCs out of town. A follower can be called in battle a few
  times like a mini-guest (one action, e.g. a Kaiu engineer drops a barricade, a monk heals, a geisha's song lowers
  enemy morale). Followers and guests are separate (you can have one of each).

### A3. Hired Help — Ide Tamotsu's *Barter Coin*
- Pay gold for a one-off mercenary strike (ronin, ashigaru archers, Yasuki bodyguards); cost scales by chapter.

### A3b. Hireables (built 2026-10-21; user: Octopath Traveler 0 / II style)
- Generic townsfolk, hired for zeni or recruited by winning the traveler's path action (Natsuko: Sumai).
- One at a time, alongside the guest. They follow on the field and stand in the battle's back row.
- A traveler spends their turn on **Call** to have them do one powered-up action. Charges are per hire; when they run
  out, the hireling walks home to the spot where they were hired.
- The Crab roster and numbers live in `tools/hirelings.py`. Example: the Kuni Shugenja's *Earth Becomes Sky*; with
  Boost 2+ (two Raises) it becomes *Earth Becomes Jade*.

### A4. Finale: Allies' Muster
- Every major ally earned across the eight stories appears in the finale's escape-blocking montage; some contribute a
  once-per-battle action in the last fight.

---

## B1. Each traveler's supporting cast
(Adventure NPCs who are *not* pregens keep their source names for now; renaming them is optional.)

### Hiruma Natsuko (Crab)
Hiruma Kage (family daimyo), Kaiu Takakana (karo of Kyuden Hida, mentor), Hiruma Ryoichi (friend; peasant weapons),
Hida Sachiko (comic Wall Crab), **Squeak-of-Many-Eggs** (orig., young nezumi), Hida Kisada (the Great Bear).
Antagonists: Seppun Ryozo, the nameless oni, Oni no Kommei, Nashiko (as Asako Kuhime).

### Kakita Rensei (Crane)
Lady Doji Sanae (orig., Keeper of the House Honour), Kakita Masanori (orig., father), Kakita Morishu / the Green Ronin,
Sariko, Torishigawa, Kakita Yasurugi (silent duelist). Antagonists: Lord Akodo Goroso, the White Squid brothers, Doji
Miyako (Nashiko).

### Kitsuki Gendo (Dragon)
Kitsuki Yasu (lord), Riichi (boy with perfect memory), Muika (eta mortician), Yoritomo, Tadayasu & Kosai,
**Togashi Yosai** (orig., tattooed monk with dark humour — guest). Year 400:
Hantei Kusada, Doji Seikidera, Doji Tomeko, Bayushi Atsuki, Shiba Katsutoshi, Isawa Sanro (future Asahina), Kakita
Miyoshi, Seppun Ushimo & Tsuhime. Antagonists: Kakita Kumpei, Togashi Akuro, Gusai Iami.

### Akodo Shizue (Lion)
Akodo Hiruto (uncle/lord), Akodo Gusai (reckless cousin), **Akodo Ijako** (cousin, sodan-seizo — guest), Akodo Hojiki,
Akodo Toturi, Akodo Nishi, Akodo Kafu, **Moto Benjiro** (guest), Daidoji Atsuko (spy). Antagonists: O-Tamai, Oni no
Ianwa, Miya Yachiko.

### Isawa Haruki (Phoenix)
Isawa Hoju (teacher), Isawa Mieko (orig.), Asako Keiki, **Shiba Ashimita** (haunted yojimbo — guest), Isawa Kamasari,
Isawa Hiroshi. Antagonists: Mieko's dark half, Hioninmaru, Kokujin's cultists, the Darkfever oni (option).

### Shosuro Mitsue (Scorpion)
Bayushi Shoju (from afar), Shosuro Norie, Yoritomo Rui, Shosuro Osuko, Soshi Giseiki (soul in a mask), Miya Hatomu.
Antagonists: Kansen-possessed Kitsune Hana, Abbot Munashii, Soshi Bantaro & Shinobu.

### Ide Tamotsu (Unicorn)
Shinjo Miyahana (sensei), Naohida, Iuchi Daiyu, Iuchi Shahai, Iuchi Hiroichi, **Iuchi Karasu** (porcelain-masked
Shadowlands survivor — guest), Shinjo Tsune, Persimmon the pony. Antagonists: Iuchi Kurosho, the Shuten Doji of
Regret, "Waruko"/Soshi Nihime, the Iuchi hit squad.

### Sayo (Ronin)
Ume-baa (orig., eta herbalist mentor), **Hiro** (giant eta undertaker — guest), Mibu Kagemaro, **Jinnai** (orig., ronin
pilgrim and Osano-Wo monk — guest), Ji-ji, Mirumoto Hikaru (ageless tattooed Dragon), **Akari** (orig., the eta woman chosen by the Oracle of Fire
— Ch4). Antagonists: Tomie Cho (weretiger), the spoilt young lord, the Great Naga, Scorpion agents trying to change the
Oracle's choice.

---

## B2. Recurring cross-story NPCs
| NPC | Appears in | Thread |
|---|---|---|
| **Doji Nashiko** | Crab Ch2–4, Crab/Crane crossroads, echoes elsewhere | Final antagonist |
| **The blue-eyed woman** | Glimpsed once by every traveler | Nashiko's echo |
| **Bayushi Depura** | Crane Ch1, Crab/Crane crossroads | Scorpion schemer |
| **Miya Yachiko** | Lion Ch1, Ch3 | Imperial houses keep the clans at war |
| **Moto Benjiro** | Lion Ch2 → finale | The Moto curse |
| **Iuchi Karasu** | Unicorn arc → Phoenix Ch3 | Shadowlands lore-giver |
| **Shosuro Norie** | Unicorn Ch1–2, Scorpion Ch3 | Rival-ally |
| **Stich'Kik** | Finale | Nezumi guide |

---

## B3. Guest roster (25)
"Joins via" = where the guest's recruiting side story is offered. Actions are draft.

| # | Guest | Clan / school | Signature actions (uses/battle) | Joins via | Secret → 2nd side story | Banter with |
|---|---|---|---|---|---|---|
| 1 | **Akodo Rin** | Lion / Akodo + Seppun guard | *Cover* (protect ally, 2), *The Clouds Part* (first-turn speed buff, 1) | Unicorn Ch1 (tribunal escort) | Raised herself as the "son" her father wanted; a lost love, her Seppun grandmaster. **Her Seppun grandmother gives her a drop of Imperial blood**, which is why she is stalked in Unicorn Ch2 (Kurosho's sacrifice). | Shizue, Rensei |
| 2 | **Bayushi Hideki** | Scorpion / Bayushi bushi | *Pincers and Tail* (lower enemy evasion, 2), *Strike at the Tail* (disarm, 1) | Unicorn/Scorpion crossroads | His Unicorn stepfather killed his father; kharmic tie to half-sister Saran | Mitsue, Tamotsu |
| 3 | **Iuchi Saran** | Unicorn / Iuchi shugenja | *Path to Inner Peace* (heal, 3), *Rolling River* (water AoE, 1) | Unicorn Ch2 | Child of the war; the truth of her birth (joint story with Hideki) | Tamotsu, Haruki |
| 4 | **Doji Chiyo** | Crane / Doji courtier | *Test of Honor* (cancel an enemy action, 1), *Whisper from the Soul* (debuff, 2) | Unicorn Ch1 (the swing vote) | Plain-faced, brilliant, disgusted by the Crane cult of beauty — Nashiko's foil | Rensei, Mitsue |
| 5 | **Mirumoto Daigo** | Dragon / Agasha shugenja | *Firecracker* (fire, random targets, 2), *Katana of Fire* (buff, 1) | Unicorn Ch2 (Dragon peacekeepers) | Prankster scientist; rivalry with best friend Toshiro | Gendo, Haruki |
| 6 | **Shiba Toshiro** | Phoenix / Shiba bushi | *Spear Wall* (2), *One With Nothing* (give an ally an extra action, 1) | with Daigo | Burned hands; his family blade was taken from him; claustrophobic | Haruki, Natsuko |
| 7 | **Hiruma Goro** | Crab / Hida bushi | *Troll-Breaker* (bare-handed heavy hit, 2) | Crab Ch2 (court bodyguards) | Bent katana; brother got their father's sword; felt an ancestor's pride once | Natsuko |
| 8 | **Ide Fujio** | Unicorn / Ide emissary | *Scandalous Letter* (enemy skips turn, 1), *Encourage* (buff, 2) | Crab Ch2 | Writes racy, popular letters; an ex-lover turned maho-tsukai over him | Tamotsu, Rensei |
| 9 | **Daidoji Sakura** | Crane / Daidoji + Shiba | *Blank Scroll* (Void guard, 2) | Crab Ch2 | Left the Daidoji over a pitch-filled gorge; seeks her dead mother's approval | Rensei, Haruki |
| 10 | **Kitsu Takeo** | Lion / Akodo cavalry | *Charge* (line attack, 2) | Crab Ch2 | The ancestors have never spoken to him; secret wife; loves Yogo Mai | Shizue |
| 11 | **Yogo Mai** | Scorpion / Yogo shugenja | *Ward* (2), *Confession* (reveal & lower defence, 1) | Crab Ch2 | Sweet — and secretly enjoys extracting confessions; the Yogo curse | Mitsue |
| 12 | **Isawa Michio** | Phoenix / Earth tensai, Inquisitor | *Amaterasu's Fire* (anti-Taint, 2), *Earth Ward* (1) | Crab Ch2 | Brilliant, arrogant; a dark secret about the limits of what he knows | Haruki |
| 13 | **Kitsuki Momo** | Dragon / Kitsuki magistrate | *Perfect Recall* (reveal weakness, 2) | Dragon Ch1 | Born a plum farmer's daughter; made samurai for saving her lord's life | Gendo, Sayo |
| 14 | **Kaiu Shino** | Crab / Kaiu engineer | *Barricade* (party guard, 1), *Caltrops* (slow, 2) | Dragon Ch1 (Mantis isles) | Fled an abusive marriage; hides her beauty | Natsuko |
| 15 | **Kitsu Reiko** | Lion / Kitsu sodan-senzo | *Ancestor's Voice* (buff/debuff, 2) | Dragon Ch1 | Spoiled rebel; once faked an ancestor's voice so a friend could duel | Shizue, Gendo |
| 16 | **Kaito** | Mantis / Mantis bushi (no family name) | *Any Weapon* (copies the last weapon type used, 2) | Dragon Ch1 | Never knew his mother; killed a Lion boy in a childhood duel; a corrupt Storm Legion captain hates him | Gendo, Sayo |
| 17 | **Asahina Yoshiro** | Crane / Asahina shugenja | *Peace Ward* (party damage reduction, 2) | Dragon Ch2 | Survived a cursed boating trip that killed his love | Rensei, Haruki |
| 18 | **Shosuro Kenta** | Scorpion / Bayushi bushi | *Ambush* (first-strike crit, 1), *Disguise* (2) | Dragon Ch1 | Disillusioned spy who saw what the Lion did at Beiden Pass | Mitsue |
| 19 | **Matsu Kiku** | Lion / Matsu | *Battle-Joy* (big damage, self-debuff after, 1) | Crane Ch1 | Gentle outside battle; terrified of her own battle-joy; secretly loves Crane art | Shizue, Rensei |
| 20 | **Kitsuki Seigen** | Dragon / Kitsuki | *Evidence* (reveal weakness & next move, 2) | Crane Ch1 | World-weary ex-magistrate serving the Crane honour-keeper | Gendo |
| 21 | **Iuchi Karasu** | Unicorn / Iuchi shugenja | *Jade Strike* (anti-Taint, 2), deadpan quips | Unicorn Ch3 | Porcelain mask, glowing eyes; months a Shadowlands prisoner | Everyone (comic) |
| 22 | **Moto Benjiro** | Unicorn / Moto bushi | *Death Trance* (party fear immunity, 1), *Oni-Bane* (2) | Lion Ch2 | Rides into the Shadowlands to die well; the Moto curse | Natsuko, Shizue |
| 23 | **Shiba Ashimita** | Phoenix / Shiba bushi | *Guardian* (2), *Grandfather's Storm* (spirit sense, 1) | Lion/Phoenix crossroads | Haunted since birth by his grandfather's screaming ghost | Haruki |
| 24 | **Akodo Ijako** | Lion / Kitsu-trained sodan-seizo | *Call the Dead* (summon an ancestor strike, 1), *Mask Rite* (2) | Lion Ch1 | Her mother died bearing her; fears meeting her in the Lands of the Dead | Shizue, Haruki |
| 25 | **Hiro** | eta / undertaker | *No-dachi Sweep* (AoE, 2) | Ronin Ch1 | Clawed by the weretiger… the curse may take him | Sayo |
| 26 | **Jinnai** *(orig.)* | Ronin / lay brother of the Order of Osano-Wo (monk) | *Freezing the Lifeblood* (paralyze, 2), *Chi Protection* (heal/cure, 1); passive Kharmic Strike counter | Ronin Ch2 | Secretly of the Order of the Snake; the last of the house that guarded the Mountain of the White Snow | Sayo, Natsuko |
| 27 | **Togashi Yosai** *(orig.)* | Dragon / tattooed Togashi (*ise zumi*, monk) | *Dragon's Breath* (Fire AoE, self-damage, 2), *Arrowroot* (heal an ally, takes half the wounds, 2); passive **Crow** (Taint-immune; Shadowlands foes always target him) | Dragon Ch1 (the murdered monks were his order-brothers) | Dark humour: keeps a tally of the Fortunes' attempts to kill him. He hunts Kokujin's cultists, the order-brothers who fell. | Gendo, Haruki, Natsuko |

Notes:
- Guests 7–12 form a pre-made **Phoenix Inquisitor team** (Michio's group) — an optional side-quest chain; Takeo & Mai's
  romance unfolds across their side stories.
- The Mirror, Mirror pregens' dark secrets deliberately mirror Nashiko — their second side stories echo the finale's
  virtue debate.

---

## B4. Name mapping (source → new name) — for traceability only, not shown in game
| New name | Source character | Source |
|---|---|---|
| Akodo Rin | Akodo Ryuko | Fortune's Lost pregen |
| Bayushi Hideki | Bayushi Hayato | Fortune's Lost pregen |
| Iuchi Saran | Iuchi Li-Hsu | Fortune's Lost pregen |
| Doji Chiyo | Doji Himeko | Fortune's Lost pregen |
| Mirumoto Daigo | Mirumoto Seiji | Fortune's Lost pregen |
| Shiba Toshiro | Shiba Kiyoshi | Fortune's Lost pregen |
| Hiruma Goro | Hiruma Yasuji | Mirror, Mirror pregen |
| Ide Fujio | Ide Masafumi | Mirror, Mirror pregen |
| Daidoji Sakura | Daidoji Kame | Mirror, Mirror pregen |
| Kitsu Takeo | Kitsu Kikuzo | Mirror, Mirror pregen |
| Yogo Mai | Yogo Sumiko | Mirror, Mirror pregen |
| Isawa Michio | Isawa Ryoji | Mirror, Mirror pregen |
| Kitsuki Momo | Kitsuki Fumiko | Hindsight pregen |
| Kaiu Shino | Kaiu Watsuko | Hindsight pregen |
| Kitsu Reiko | Kitsu Mihime | Hindsight pregen |
| Kaito | Kanimoto | Hindsight pregen |
| Asahina Yoshiro | Asahina Jikoji | Hindsight pregen |
| Shosuro Kenta | Shosuro Yakawa | Hindsight pregen |
| Matsu Kiku | Matsu Yanuriko | And Does Not Descend pregen |
| Kitsuki Seigen | Kitsuki Taja | And Does Not Descend pregen |

**Session 2 fix:** five guests are **adventure NPCs, not pregens**: Iuchi Karasu (Fortune's Lost), Moto Benjiro
(Shadow of a Doubt), Shiba Ashimita and Akodo Ijako (The Blood of Family), Hiro (Honor and Eta). Session 1 had
renamed them (Kuroha, Temur, Hayate, Mayu, Gonzō). That broke the "static characters stay static" rule below, so
their **source names were restored** throughout the docs.

## Decided
- **Static characters stay static** (user, 2026-10-16): adventure and canon NPCs keep their names and rank; only
  pregen-derived guests are renamed. Guests start low-rank too and are treated accordingly by great lords.
