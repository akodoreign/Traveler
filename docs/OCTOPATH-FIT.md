# Octopath Fit — how Rokugan Traveler maps onto Octopath Traveler's mechanics (v0.1)

The story is approved (user, session 2). This document makes the **game structure** behave like Octopath Traveler,
and lists every place we deliberately deviate. Rule of thumb: **if Octopath has a way to do it, use Octopath's way;
custom mechanics only where L5R needs them, and at most one gimmick per chapter.**

---

## 1. The Octopath skeleton we adopt as-is
| Octopath element | Rokugan Traveler |
|---|---|
| Choose 1 of 8 starters; the starter **cannot leave the party** until their Ch4 is done (OT1) | Same. The starter's Ch1 plays solo. |
| Recruit by **visiting the others' starting towns** and playing their Ch1 with the party present (OT1) | Same. The 8 Ch1 towns are spread over the map (§4). |
| **Party of 4** in battle; the others wait at the **tavern/inn** (swap there) | Same; the inn is the swap point (also where kata are set, `rules/kata.md`). |
| A chapter belongs to one traveler; **that traveler must be in the party** to start it | Same. Other members speak only in optional **Travel Banter**. |
| Chapter shape: **intro cutscene → town (path actions) → dungeon (save point at the end) → boss → wrap-up** | **Every chapter script follows this shape** (§3 audits the Ch1s). |
| **Recommended level** per chapter, shown on the map; "danger level" per area | Ch1 ≈ 1–10 · Ch2 ≈ 20–25 · Ch3 ≈ 30–35 · Ch4 ≈ 40–45 · crossroads ≈ Ch2–3 level · finale ≈ 55–60. Lines up with Rank bands (R2 at 21, R3 at 41). |
| **Break**: shields + weakness icons; Break = lose a turn, take more damage | **Suki** (Resolve shields). Same rules: the broken enemy loses its current/next action, takes +50%. |
| Octopath's **BP**: +1 per turn (not on a turn you Boost), max 5, spend up to 3 | **Void Points (VP)** = Octopath's BP, identical rules (renamed VP by the user, session 3). *Exception:* Haruki's Void spells are **paid** in VP (user-approved). |
| Unique **Talent** command per traveler | Razor's Edge, Iaijutsu, Deduce, Command, Attune, Many Faces, Barter Coin, Remedy. |
| **Path actions** in 4 pairs (honourable / chance-based), with town reputation for failed chance actions | Same 4 pairs. Reputation = **town Honor**; Low Skills cost Honor (`rules/skills.md`). |
| **OT2 Crossed Paths** (two-traveler chapters) | The 4 **crossroads** chapters (`story/03`). |
| **OT2 guests / OT1 Hire-and-Allure** | Guests ("Call Guest", limited uses per battle) and hired help (`story/04`). |
| Side stories (NPC quests with an icon on the map) | Same; every guest has 2 side stories (`story/04` B3). |
| **Travel Banter** (OT1) / inn conversations (OT2) | Same; triggered at inns. |
| Final hidden chapter after all Ch4s | The finale, "The Empress of Nothing" (`story/03`). |
| Shrines that grant secondary jobs | **Dojo and shrine visits** unlock secondary schools (Hida, Mirumoto…) at R2. |

## 2. Where we deviate (and why it's still Octopath-shaped)
| Deviation | Octopath analogue that keeps it familiar | Rule |
|---|---|---|
| **No JP shop**: skills come from **level picks** every 5 levels + Rank techniques (user's rank bands) | Like learning skills, but the "shop" is the level-up screen | The level-up screen shows: new technique, new skill rank, pick 1 of N. |
| **Kata stances** (a free toggle, 1 slot) | OT2 **Latent Power** (a per-traveler toggle) + support skills | One kata slot = one equipped "stance"; it never costs a turn. |
| **Skill ranks gate path actions** (not level) | OT1 gated path actions by level | The NPC info card shows the required rank instead of the required level. |
| **Honor / Glory / Status** | Town reputation (Honor); Glory/Status = which NPCs will *talk* | Status only changes **dialogue and access**, never combat. |
| **Taint** status | A persistent negative status (OT2-style lasting debuff) | Cleared at shrines or with jade items; shown as a stacking icon. |
| **Field skills** (sneak, climb, swim, scry…) | Octopath has almost none → keep them **minimal** | They are **interaction prompts** on marked map spots (like OT2's ladder/rope points), gated by skill rank, or simple **passives** (encounter rate down = OT's *Evasive Maneuvers*). No free-roam stealth system. |
| **Branching choices** in chapters | OT2 has a few dialogue choices; OT1 almost none | **Max 1–2 choices per chapter.** They change dialogue, rewards and later flags, **never the dungeon or the boss**. Multi-route climaxes (Crane Ch1, Lion Ch1) all end in **the same boss fight**. |
| **Minigames** (painting, dance, triage, code puzzle…) | Octopath has very few | Convert most to **path actions or dialogue choices** (§3). Keep **one light set-piece per chapter at most**. Battle gimmicks (timers, hazards) are fine: OT2 bosses use them. |
| **Crossroads are "shared chapters"**, not separate extra chapters | OT2 Crossed Paths | Each crossroads is **owned** by one traveler's chapter (it counts toward their 4). For the partner it is **bonus content**: extra scenes, dialogue and a reward, playable only with the partner in the party. **Without the partner, a story NPC stands in** (e.g. Akodo Ijako for Shizue). This avoids telling the same events twice. Owners: Lion Ch1 ⇄ Phoenix Ch1 (co-owned, two versions) · Crane Ch2 (+Crab) · Unicorn Ch2 = Scorpion Ch3 (co-owned) · Scorpion Ch4 (+Dragon). |
| **Solo segments** (Sayo in the eta village; Rensei ignored in the corridor) | OT chapters already focus on one traveler | Implement as a **cutscene + short solo walk**, never a solo *battle* with the party removed. |

## 3. Audit of the written scripts → required conversions
| Script | Fits as written | Convert / trim |
|---|---|---|
| **Crab Ch1** | Prologue tutorial battle; town (path action Sumai on Gonta); cave dungeon; boss | The rooftop chase → a **cutscene + a short follow-the-nezumi walk**. The **Rumble meter** stays (it is the chapter's one battle gimmick). The Stealth/Hunting tracking "minigame" → an interaction prompt. |
| **Crane Ch1** | Village (Charm), forest dungeon, castle, duel boss | The lantern-pulley puzzle → **3 interaction points** in the forest dungeon (cut the right rope). The **four dawn routes**: one dialogue choice; the Yasurugi boss is the same in all routes. |
| **Dragon Ch1** | Town (Discern), Gusai ruins dungeon, beach boss | Riichi's code "puzzle" → a **Discern on Riichi** plus one dialogue choice. The Gusai stair code is the dungeon's layout (the path is the code), not a puzzle UI. The **tide timer** stays (battle gimmick). |
| **Lion Ch1** | Castle town, clue gathering (path actions), boss | The **clue board** → the standard Octopath "talk / Discern / Eavesdrop the NPCs" town structure, with a 5-clue gate. The shrine search uses the **jade-chain compass** as a simple "colder/warmer" text prompt at 4 spots. The 3 climax routes are one choice; the O-Tamai boss is the same. |
| **Lion Ch2** (template) | Castle hub; boss | The **11-week calendar** → **4 fixed event beats** (bracket → history dinner → debate → dance + arrest). The **bracket** = 3 back-to-back Duel battles (path-action battles, fine). Painting and dance → **one dialogue choice each**, with the prize given either way (better choice = better prize). |
| **Phoenix Ch1** | Castle town, road, shrine, mid-boss, shared boss | Fine. The spirit-wasteland debuff = a map-wide passive (like OT2's weather states). |
| **Scorpion Ch1** | Court (Eavesdrop), road, town, marsh dungeon, boss | The eavesdrop "minigame" → plain **Eavesdrop** path actions on 3 marked NPCs. The disguise infiltration → *Many Faces* as a cutscene trigger. The **ritual counter + drop-the-Box-on-Suki** boss stays (battle gimmick). |
| **Unicorn Ch1** | Camps (Barter), courts, cave dungeon, boss | **Rubble rescue** → an event battle with a turn counter (OT2-style); keep it. **Powder kegs** in the boss fight: keep as the boss gimmick, but then the rubble battle becomes a short cutscene instead (one gimmick per chapter). The testimony mechanic → path actions plus a final dialogue choice. |
| **Ronin Ch1** | Market town (Pilfer), village, field mini-boss, boss | The tengu **knock-off** mechanic is a mini-boss gimmick; fine. The weretiger's **three forms** = boss phases (standard). The caste gate = a solo cutscene walk (§2). |
| **Phoenix Ch3 outline** | — | The **triage minigame** → a sequence of **Bless/Remedy interactions** with sick NPCs (path actions + item use), not a separate UI. |

**Fake choices** (Octopath does this too): when a "wrong" option would break a traveler's arc (killing Mieko in
Phoenix Ch4, accepting the Emperor's glory in Dragon Ch4 can stay real because it only colours the epilogue), the
option is shown, the traveler refuses it in-character, and the story continues on the canonical line.

**Gimmick budget per chapter (the rule from now on):** one battle gimmick (a timer, hazard or special disarm) **or**
one field set-piece, never both. Everything else is town / path actions / dungeon / boss.

## 4. World map & recruitment order (OT1-style)
Each Ch1 town is a starting town; the others are recruitable there.
| Traveler | Ch1 town (region) | Notes |
|---|---|---|
| Natsuko | **Hoshi-no-Ichi** (Yasuki coast; Crab lands, near the Wall) | south-west |
| Rensei | **Pleasant Eaves** village (Lion lands, Beiden Pass) | centre-west |
| Gendo | **Isle of Silk** (Mantis isles) | south-east sea; reached by ship (the early world map needs a ferry route) |
| Shizue | **Akodo Hiruto's castle town** (Lion–Phoenix–Crane border) | centre-north |
| Haruki | **Shiro no Kamatori** (Phoenix) | north |
| Mitsue | **Kyuden Bayushi** (Scorpion), story → Kudo | south |
| Tamotsu | **Town of Buried Leaves** (Ojatara Valleys, Spine of the World) | west |
| Sayo | **Cakon** (Crane coast) | east |
- **Lion and Phoenix Ch1 share a climax.** Whichever is played second gets the shortened "crossroads" version
  (both scripts already support this).
- Like OT1, all Ch1s are about Lv 1–10 and can be done in any order. Ch2s open after a soft level gate.

## 5. Battle rules summary (Octopath numbers, L5R names)
- Party 4 + 1 guest call (OT2). Turn order bar shows this turn and the next (Octopath).
- **Suki:** shields 2–6 common, 8–14 bosses (`rules/enemies.md`). Broken enemies skip the action and take +50%.
- **VP:** start each battle with 1 (Tea Ceremony and Battle mastery can add more; `rules/skills.md`). +1 per turn,
  max 5, Boost up to 3 (4 with Kenjutsu 5 on Katana attacks).
- **Kata:** toggled for free at the start of the traveler's turn (≈ Latent Power).
- **Status effects:** Octopath's standard set + Terror, Shaken and Taint (`rules/enemies.md`).
- **Escape, items, Defend** (= 3e Full Defense): Octopath standard.

## 6. Engine notes (RPG-Cobo)
- The chapter shape maps onto map events + one battle troop per boss. Flags are save variables.
- The gimmicks needed so far: a **turn-counter boss** (Scorpion Ch1, Unicorn rubble), **terrain hazards** (tide,
  rumble, powder kegs), **command-swap** (Kommei oni), **multi-form boss** (weretiger). Plan these as reusable
  battle-plugin hooks in `rt_suki` / a new `rt_gimmicks` plugin (DESIGN §5).
- Path-action gating by skill rank: a small plugin reading each NPC's required rank.

## 7. Next
1. Apply the §3 conversions to the scripts as each one gets its production pass. (The scripts stay as they are for
   now; this table is the instruction.)
2. Write the crossroads and Ch2–4 scripts **already in this shape** (one gimmick, two choices max).
