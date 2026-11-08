# Rules — Skills & Mastery Unlocks (L5R 3e → Octopath) — DRAFT v0.1

Source: *L5R 3e Core*, Book of Water, Skills (OCR clean ≈ lines 10400–11620). Mastery abilities are paraphrased.
Conversion table: `kata.md` §2.

## 1. The skill track
- **3e:** skills have Ranks 1–10. *Every* skill gains generic masteries: R1 one Emphasis; R3 teach; **R5 +1 Free Raise**
  with the skill; R7 more Emphases; **R10 Grand Master** (+5 Insight, unlimited Raises). Many skills add their own
  R3/R5/R7/R10 abilities.
- **Octopath implementation (DESIGN §4c "every 2 levels"):**
  - At **every even level**, the traveler gets **1 skill rank to assign** (the "Practice" menu; auto-assign optional).
    That is 49 ranks by Lv 98.
  - School skills **start at Rank 1**. Two signature skills start at Rank 2.
  - **Skill cap by Insight Rank: R1 → 3 · R2 → 5 · R3 → 7 · R4 → 9 · R5 → 10.** The caps line up with the 3e
    mastery breakpoints (3/5/7/10), so each new Rank opens the next mastery tier. This replaces "level" as the gate.
  - **Generic masteries in game:** R5 = **+10%** on everything that uses the skill (path-action odds, potency);
    R10 = **+20%**, and path actions with that skill can't fail vs. non-boss NPCs.
  - Some skills are **Low Skills** (Deceit, Sleight of Hand, Stealth with some Emphases, Underworld, Poison, Forgery…).
    Using them in towns can cost **town Honor** if witnessed. This replaces the reputation loss of Octopath's failed
    chance actions with a canon mechanic.

## 2. Path actions use skills, not level
| Path action | Traveler | Style | Skill | How the skill rank works |
|---|---|---|---|---|
| **Duel** | Shizue | honourable (battle) | **Iaijutsu** (+Kenjutsu) | The Rank gates which NPCs will accept the challenge. Iaijutsu masteries add **Focus** uses in the duel mini-battle. |
| **Sumai** | Natsuko | chance | **Jiujutsu** | Odds = f(rank vs. NPC rank). Masteries add unarmed damage in the Sumai bout. |
| **Charm** | Rensei | chance | **Etiquette** (Courtier assists) | Odds + (Etiquette masteries add +5/+10/+20 → +10/+20/+30%). |
| **Bless** | Haruki | honourable (lead NPCs) | **Theology** | The rank gates who will follow him (NPC "piety rank"). |
| **Discern** | Gendo | honourable | **Investigation** | The rank gates NPCs. R5 = one **re-examination** of an NPC already discerned (finds a second secret); R10 = two. |
| **Eavesdrop** | Mitsue | chance | **Stealth** (Investigation assists) | Odds by rank. **Low Skill:** a failure costs Honor (as OT1's failed Scrutinize). |
| **Barter** | Tamotsu | honourable (buy from NPCs) | **Commerce** | 3e haggle: **5% → 10% (R5) → 15% (R7) → 20% (R10)** off. Plus Etiquette for the price "TN". |
| **Pilfer** | Sayo | chance | **Sleight of Hand** | Odds by rank. **Low Skill:** a failure costs Honor and a witnessed success costs Honor too. *The wave-woman pays a different price than samurai.* |

## 3. Per-traveler skill lists (3e school skills + character skills)
**Bold** = starts at Rank 2.

| Traveler | School skills | Character / kit skills |
|---|---|---|
| Natsuko | Athletics, Defense, **Hunting**, Lore: Shadowlands, **Stealth**, Spears | Jiujutsu (Sumai), Kyujutsu (Yumi); Heavy Weapons (Tetsubo) via the Hida kit at R2 |
| Rensei | Etiquette, **Iaijutsu**, Kenjutsu, Kyujutsu, Meditation | **Etiquette**→Charm stays at 1 (he is *bad* at court at first — story); Tea Ceremony, Knives (Tanto), Courtier |
| Gendo | Courtier, Etiquette, **Investigation**, Meditation, Theology, Lore: Law | Underworld (a *Bugei* skill for Kitsuki: no Honor loss), **Know the School: Scorpion** (yoriki); from R2 (Mirumoto): Kenjutsu, Defense, Staves (Bo) |
| Shizue | **Battle**, Defense, Kenjutsu, Kyujutsu, Lore: History, Storytelling | **Iaijutsu** (Duel), Spears (Yari), Know the School: Crane (the Lion–Crane war) |
| Haruki | Calligraphy, Meditation, **Spellcraft**, **Theology**, Lore: Ghosts | Medicine (healer flavour), Staves (Bo), Tea Ceremony |
| Mitsue | Athletics, Deceit, Defense, Kenjutsu, Ninja Ranged Weapons, **Stealth**, Underworld | **Acting** (actress), Knives (Tanto), Kyujutsu (Yumi), Investigation, Poison |
| Tamotsu | **Commerce**, Courtier, Etiquette, Horsemanship, Investigation, Storytelling | Kyujutsu (Yumi, Yomanri emphasis), Spears (Yari), Animal Handling, Lore: Gaijin |
| Sayo | Ronin bushi (canon, ≈ line 16806): Defense, Hunting, Kenjutsu, Kyujutsu + **any 3** = **Medicine** (Herbalism), **Sleight of Hand**, Underworld. (If her first Rank is the Duelist's, she also gets Iaijutsu.) | Poison (antidotes), Stealth |

## 4. Mastery → Octopath effects (only skills the travelers use)
### Battle skills
| Skill | R3 | R5 | R7 | R10 |
|---|---|---|---|---|
| **Defense** | Start every battle in **Defend** for free | (+10% generic) | Defend's evasion bonus also applies on turns he or she **Boosts** an attack | Can use items while Defending without leaving Defend |
| **Iaijutsu** | **+1 Focus** in duels | +10% | Focus also adds **crit chance** | **+1 more Focus** |
| **Kenjutsu** (Katana) | — | **Boost cap 4** on Katana attacks (3e: one more Void on damage) | — | Crit up (9s explode) |
| Weapon skills, generic | — | Immune to **Shaken**'s Accuracy penalty with that weapon | — | Crit up |
| **Heavy Weapons** (Tetsubo) | — | Ignore **10% Def** (armour) | Ignore **20% Def** | Crit up |
| **Knives** (Tanto) | — | Off-hand: **dual-tanto** passive (a second weak hit) | **+1 hit** on Tanto skills | Crit up |
| **Kyujutsu** (Yumi) | Back-row / evasive-target accuracy +5% | +5% more | +5% more | +10% more |
| **Spears** (Yari) | +damage vs. **Large or mounted** enemies (tag) | **Speed +5%** with a Yari | **Cover** (guard an ally) works better | Crit up |
| **Staves** (Bo) | — | Ignores armour-based Def bonuses | **Knockdown** chance (pushes the enemy's turn back) | Crit up |
| **Jiujutsu** | +unarmed damage (Sumai) | — | +damage | +damage (kept die) |
| **Battle** | Pre-battle: **"Read the field"** at save points → the next battle starts with +1 VP for the party | Once per battle: after an ally's hit, Shizue gains Speed (turn-order jump) | The field bonus is shared with the whole party | +3 VP at battle start (once per dungeon) |
| **Spellcraft** | Identify enemy spells → **Counter-prayer** costs −50% | +10% spell potency | — | — |
| **Know the School: X** | — | Bonus applies to rank techniques too | — | — |
| (base) | +attack and +evasion vs. **enemies from that clan's schools** = rank × 2% (×2 with an Emphasis) | | | |

### Field / support skills
| Skill | Mastery effects in game |
|---|---|
| **Meditation** | Camp/shrine command **"Meditate"**: restore VP for the next battle. R5: more; R7: plus a perception buff (*Zanji*); R10: full. |
| **Tea Ceremony** | Camp: the party **starts the next battle with +1 VP** (R5 +2, R7 +4, R10 max). The cooperative roll lets unskilled allies join. A Crane/Rensei signature. |
| **Medicine** | Sayo's **Remedy** potency tiers (R3/5/7/10 add dice). Field: forage herbs (Herbalism). Treating the same ally twice needs R3 / R7 / R10. |
| **Hunting** | *Survival:* wild camps restore like an inn. *Trailblazing:* **fewer encounters** in wilderness. |
| **Stealth** | R5: a **sneak-walk** field mode (fewer encounters, slower); R7: **pre-emptive strike** odds up for the party; R10: sneak at normal speed. |
| **Athletics** | Climbing and jumping shortcuts on the map (rank-gated ledges). |
| **Acting** | **Disguise gates** for Mitsue's story and her field "Many Faces": R3 other clan/caste; R5 other gender; R7 **a specific person**; R10 nonhuman. |
| **Etiquette** | Social contests +5/+10/+20 → Charm/Barter odds; resists enemy **Charm/Confuse**. |
| **Courtier** | Town **rumours** (side-quest hints, 50% true!); spreading rumours → change an NPC's attitude. |
| **Investigation** | Discern retries (R5/R10); spot hidden objects. |
| **Commerce** | Barter discount 5/10/15/20%; appraise items (sell prices +). |
| **Horsemanship** | Horse travel on the world map (faster, fewer encounters). R5: the horse can't be ambushed. |
| **Underworld** | Black-market shops and smuggler contacts. **Bugei for Kitsuki/magistrates** (no Honor loss for Gendo). |
| **Theology** | Bless gates; shrine interactions. Grand Master (+10 Insight) → a hidden late shrine event. |
| **Lore: X** | **Analyze** that enemy family (reveals weaknesses). Lore: Shadowlands also powers Hiruma R3 damage. Lore: Ghosts → spirits. |
| **Animal Handling** | Tame and recruit animal **followers** (04-cast "followers"). |
| **Poison** | Craft poisons (Low) / antidotes (free Raise on Medicine). |
| **Calligraphy** | Read and forge (with Forgery) ciphered documents → puzzle gates. |

## 5. Open points
1. **Auto-assign** profile for players who don't want micromanagement: each traveler gets a default priority list.
2. Do NPCs need "skill ranks" (1–10) for the path-action gates? Proposal: yes, one number per NPC per path action.
   Easier than Octopath's level comparison and setting-true.
3. ✅ Ronin skill lists checked (core ≈ lines 16801–16920). Sayo's list is canon-compatible.
4. ✅ Battle, Defense, Iaijutsu and Know the School checked against the page images (pp. 102, 105).
