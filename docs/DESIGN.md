# Rokugan Traveler — Design Document (DRAFT v0.1)

Status: **draft, pending user decisions** (see "Open decisions" at the bottom). Nothing here is final.

## 1. Pitch

Eight travelers — one samurai or shugenja from each of the seven Great Clans, plus one ronin — each set out on a
personal journey across the Emerald Empire. Like Octopath Traveler, you pick one traveler to start, recruit the
others as you meet them in their home towns, and play each one's story in four chapters. The separate threads
slowly reveal a single hidden enemy, resolved in a shared final chapter.

## 2. What we take from Octopath (design only, no assets)

| Octopath feature | Rokugan Traveler version |
|---|---|
| 8 travelers, pick 1 to start, recruit the rest | Same. Each traveler's Chapter 1 happens in their clan's lands. |
| 4 chapters per traveler, recommended level per chapter | Same. Chapters adapted from the user's adventure PDFs. |
| Shield points + weakness icons → **Break** (enemy skips turn, takes more damage) | **Suki** (隙, the kendo/budō term for an *opening* in an opponent's guard). Enemy *Resolve* points; hitting a weakness chips one off; at 0 the enemy is **open** (Suki): it skips its turn and takes more damage. *(Renamed from "Kuzushi" in session 2, at the user's request: the canon Darkfever oni is named Oni no Kuzushi and keeps that name.)* |
| Boost Points (VP), +1 per turn, spend up to 3 | **Void Points**, the L5R stat. Max 5, +1 per turn (not on the turn you spend). Spend 1–3 to multi-hit or strengthen. |
| 6 weapon types + 6 elements | Weapons: **Katana, Yari, Tanto, Tetsubo, Yumi, Bo**. Elements: **Fire, Water, Air, Earth, Void, Jade**. Jade is the anti-Shadowlands element (Octopath's "light"); Maho is enemy-only (its "dark"). |
| Path Actions, noble vs rogue pairs, town reputation | Path Actions in pairs. One is *honourable* (level- or money-gated, always safe); its partner is *chance-based* and failing it costs **Honor** in that town (Octopath's reputation). |
| Jobs / secondary jobs | Clan schools as base job; later "Different School" secondary jobs (Hida Bushi, Kakita Duelist, Isawa Shugenja...). |
| Travel banter between party members | "Tea ceremony" conversations at inns. |
| HD-2D look | RPG-Cobo's voxel HD-2D renderer. |

### Path Actions (proposed)

| Effect | Honourable (gated, safe) | Chance-based (Honor risk) |
|---|---|---|
| Fight an NPC | **Lion — Duel** (iaijutsu challenge, level-gated) | **Crab — Sumai** (wrestle; % chance) |
| Lead an NPC | **Phoenix — Bless** (level-gated) | **Crane — Charm** (court etiquette; % chance) |
| Learn information | **Dragon — Discern** (Kitsuki method; level-gated) | **Scorpion — Eavesdrop** (% chance) |
| Obtain an item | **Unicorn — Barter** (money; gaijin trade ways) | **Ronin — Pilfer** (% chance) |

## 3. The eight travelers

**Superseded by `docs/story/02-travelers.md`** (cast chosen 2026-10-16): Hiruma Natsuko (Crab), Kakita Rensei
(Crane), Kitsuki Gendo (Dragon), Akodo Shizue (Lion), Isawa Haruki (Phoenix), Shosuro Mitsue (Scorpion), Ide Tamotsu
(Unicorn, diplomat-trader), Sayo (born-ronin herbalist). The table below is the original proposal, kept for history.

| Clan | Path | School / role | Weapons | Octopath analogue |
|---|---|---|---|---|
| Crab | Sumai | Hida Bushi — tank, heavy hits, taunt | Tetsubo, Yari | Olberic |
| Crane | Charm | Kakita Duelist — single-target crits, iaijutsu "focus/strike" | Katana, Tanto | — (new) |
| Dragon | Discern | Mirumoto two-sword — multi-hit Suki breaker | Katana, Bo | — |
| Lion | Duel | Akodo Commander — party buffs, counter | Katana, Yari | — |
| Phoenix | Bless | Isawa Shugenja — Fire/Air/Earth/Water caster | Bo | Cyrus |
| Scorpion | Eavesdrop | Bayushi/Shosuro — debuffs, poison, steal | Tanto, Yumi | Therion |
| Unicorn | Barter | Iuchi Shugenja *or* Shinjo/Utaku rider — healer *or* archer | Yumi, Yari | Ophilia / H'aanit |
| Ronin | Pilfer | Wave-man — items, versatility | Katana, Yumi | Alfyn / Tressa |

Healing coverage: Unicorn (if Iuchi) + Phoenix (Water). If Unicorn is a Shinjo rider instead, the Phoenix
becomes the main healer and Crab or Crane needs a support kit.

## 4. Story structure

**Superseded by `docs/story/` (00-synthesis, 01-world-and-timeline, 02-travelers, 03-crossroads-and-finale).** Era set
to winter 1122 → spring 1123, ending on the eve of the Coup; Doji Nashiko is the final antagonist and is destroyed.
Original proposal kept below for history.

Era recommendation: **c. 1120–1123 IC, the years before the Scorpion Clan Coup.** Most of the adventures already
sit there (And Does Not Descend, Mirror Mirror, Shadow of a Doubt, Blood of Family, Fortune's Lost, Of Family and
Honor). Post-Four-Winds adventures (City of Masks, Howl of the Phoenix, Blood and Iron) get their premises
re-dated.

| Traveler | Chapters drawn from |
|---|---|
| Crab | Tamago Maho (Ch1, nezumi caves) → Mirror, Mirror (Shadowlands horror) |
| Crane | And Does Not Descend (the disgraced Kakita son) → The Edge of Treachery (White Squid pirates) |
| Dragon | Hindsight I–III (murdered ise zumi, the painting, the past) |
| Lion | Shadow of a Doubt (Akodo Winter Court) → The Blood of Family (Bloodspeaker O-Tamai) |
| Phoenix | Howl of the Phoenix (re-dated) + Phoenix side of The Blood of Family |
| Scorpion | Blood and Iron (Kudo, Kitsune vs Suzume) → City of Masks (the lost city) |
| Unicorn | Fortune's Lost (Iuchi–Soshi war tribunal) |
| Ronin | The Ronin's Sword (cursed blade) → Honor and Eta (eta village, weretiger) → Entanglements & Tied Snakes |
| **Finale** | Of Family and Honor: Akutenshi **Doji Nashiko** serving Fu Leng is the hidden hand behind incidents in every story. Past Heroes / Order of the Snake supply the conspiracy layer. |

## 4b. L5R rules → Octopath gameplay translation (REQUIRED before engine work)

User requirement (2026-10-16): when building the engine, translate the L5R tabletop rules into Octopath-style
gameplay and skills. Draft mapping to refine once the rulebooks are consulted:

| L5R rule | Octopath-style translation (draft) |
|---|---|
| Five Rings (Earth, Water, Fire, Air, Void) + 10 Traits (Stamina, Willpower, Strength, Perception, Agility, Intelligence, Reflexes, Awareness, Void) | Character stats. Earth→HP/defence, Water→physical attack/heal power, Fire→attack/elemental attack, Air→speed/evasion, Void→Void Point max (Octopath VP). Traits as sub-stats feeding these. |
| Void Points (spend for +1k1, etc.) | **Boost** (VP): +1/turn, spend 1–3 to boost. |
| Roll & Keep, Raises (call extra difficulty for better effect) | Boost spending; also a "Raise" choice on some skills (lower accuracy, bigger effect). |
| Schools & Techniques (Rank 1–5) | Base job per traveler; techniques unlock as job skills by Insight Rank (level). |
| Kata, Kiho, stances (Attack, Full Attack, Defense, Full Defense, Center) | Kata = passive "support skills"; stances = a per-turn stance command (Octopath 2 "latent power"-like). |
| Shugenja spells by element + spell slots per Ring | Spell skills by element using SP; Phoenix/Unicorn/other shugenja jobs. |
| Iaijutsu duel (assess, focus, strike) | **Duel path action** minigame (Lion) and a Kakita-style "focus then strike" skill. |
| Wound ranks / penalties | HP; low-HP penalty status. |
| Fear / Fear rank | Status effect (skip turn chance / no Boost). |
| Honor / Glory / Status | Honor = town reputation for path actions; Glory = fame unlocking court access/dialogue. |
| Shadowlands Taint, jade, crystal, obsidian | Taint stacking debuff; jade/crystal/obsidian as elements/weaknesses (Suki keys). Obsidian Taints its user (`rules/enemies.md`). |
| Weapon keywords (katana, yari, tetsubo, yumi, tanto, bo, naginata…) | Octopath weapon types for weaknesses. |
| Skills (Courtier, Etiquette, Sincerity, Investigation, Stealth…) | Path actions and dialogue checks. |
| Advantages/Disadvantages | Traveler passives and story flags. |

### 4c. Insight Rank ↔ level bands and per-level gains (user spec, 2026-10-16)

**Rank bands (user-defined):**

| Insight Rank | Levels | Story placement (approx.) |
|---|---|---|
| **Rank 1** | 1–20 | Chapter 1 (+ early Ch2 travel) |
| **Rank 2** | 21–40 | Chapters 2–3 |
| **Rank 3** | 41–50 | Chapter 4 |
| **Rank 4** | 51–60 | Crossroads late game + Finale |
| **Rank 5** | 61+ (cap 99, Octopath-style) | Post-game / superbosses |

**What a level gives** — gains are drawn from L5R's own advancement pieces (techniques, skills, kata, kiho, spells,
rings/traits) instead of Octopath's JP shop. Draft pattern, to tune once the 3e core/Masters of Magic OCR is done:

| When | Gain | Octopath equivalent | Notes |
|---|---|---|---|
| **Every level** | Stat growth from the character's Rings/Traits curve (Earth→HP/DEF, Water→ATK/healing, Fire→elemental ATK, Air→SPD/EVA, Void→max Void Points & SP) | Stat growth | Each school weights the rings differently (Hida = Earth, Isawa = their element, Kakita = Fire/Air). |
| **Every 2 levels** | **+1 Skill rank** chosen from the school's skill list (Kenjutsu, Iaijutsu, Kyujutsu, Courtier, Investigation, Sincerity, Medicine…) | (new) passive growth | Skill ranks are small passives (e.g. Kenjutsu → katana damage; Iaijutsu → Focus stacks; Medicine → healing). **Path Actions are gated by Skill rank, not just level** (Duel ← Iaijutsu, Charm ← Courtier/Etiquette, Discern ← Investigation, Barter ← Commerce, Eavesdrop/Pilfer success ← Stealth/Sleight of Hand, Sumai ← Jiujutsu, Bless ← Theology). |
| **Every 5 levels** (5, 10, 15 …) | **One new technique** from the character's pool: a **battle skill**, a **kata** (support skill / stance, e.g. Striking as Earth = guard stance, Striking as Fire = power stance), a **kiho** (Void-fuelled ki technique; Togashi/monk-flavoured, available to Void-heavy characters), or **spells** (shugenja learn 1–2 per pick, by element) | Learning battle skills / support skills | Bushi lean to kata, shugenja to spells, Dragon/Phoenix/Ronin can take kiho. |
| **Rank threshold** (levels 1, 21, 41, 51, 61) | **New School Technique** (the L5R Rank 1–5 technique) = a major passive or an upgrade to the traveler's **Talent** | Job "divine skill"/latent power | E.g. Kakita R1 = Iaijutsu Focus/Strike; R3 = Strike ignores defence; R5 = act first every round. |
| **Story rewards** (not levels) | **Advantages** (and occasionally Disadvantages) from chapter events; **Honor/Glory** changes | Story items / unlocks | E.g. finishing Natsuko Ch3 grants *Way of the Land: Shadowlands*. |

**Rank-specific rules:**
- Insight Rank shown on the status screen next to level; NPC dialogue and court access check **Rank + Status**
  (a Rank 1 samurai is ignored by daimyo regardless of level — reinforcing the low-status start).
- Equipment tiers can be Rank-gated (fine/excellent blades, nemuranai).
- Secondary schools (Octopath II secondary jobs) unlock at **Rank 2** via shrines/dojos, mirroring L5R's
  "Multiple Schools" / "Different School" advantage.

Sources to confirm numbers: 3e Core Book Revised and 4e/5e core (in the user's Drive folder), Masters of Magic
(spells), Book of Earth/Air/Fire/Water/Void (school techniques).

**Detailed rules docs (session 2):**
- `docs/rules/schools.md`: each traveler's school, R1–R5.
- `docs/rules/kata.md`: the Kata Stance system and the **3e→Octopath conversion table**.
- `docs/rules/kiho.md`: kiho for Haruki and enemies.
- `docs/rules/haruki-spells.md`: spells → skills, SP by Mastery Level, Kami Weapons, Concentration.
- `docs/rules/skills.md`: the skill-rank track and mastery unlocks.

Correction to the row above: in 3e, kiho are for **monks and shugenja only**, not Dragon/Ronin bushi. Bushi take
kata; Haruki takes ≤ 5 kiho as story rewards.

## 5. Technical approach

- Engine: RPG-Cobo (`_tools/rpgcobo-tool`). Base on `TurnBattleRunner`.
- Custom systems as RPG-Cobo **plugins** in `project/plugin/`:
  1. `rt_suki` — Resolve points, weakness reveal, unbalanced state (skip turn, +damage taken), recover next turn.
  2. `rt_void` — Void Point gain/spend, boosted multi-hit (`atknum`) and power.
  3. `rt_turnorder` — visible current/next-turn order bar (until the engine ships its own action-order battle).
  4. `rt_pathactions` — the eight path actions as event commands, with per-town Honor.
- Elements and weapon types → RPG-Cobo `type.json` attribute bits (one bit per weapon type + element) so the
  existing `defenseRate()` handles damage multipliers; Suki reads the same bits for weaknesses.
- Build and test through the engine's MCP server (`rpgcobo.exe -mcp-stdio`).

## 6. Milestones (proposed)

1. **M0 — Engine up:** template installed, a test map runs, MCP connected to Claude Code. ✅ (session 3; MCP via
   `.mcp.json`, active from the next session)
2. **M1 — Battle prototype:** Suki + Void Points + turn order working in a test fight. ✅ Suki, VP, Boost verified
   (`docs/ENGINE.md`); turn-order bar still to do.
3. **M2 — Vertical slice:** one traveler's Chapter 1 end to end (town, path action, dungeon, boss).
4. **M3 — All eight Chapter 1s + recruitment.**
5. **M4+ —** Chapters 2–4, finale, polish.

## 7. Legal / fan-project guardrails

- Non-commercial, free, with a clear "unofficial fan work" disclaimer naming FFG (L5R) and Square Enix (inspiration).
- No ripped Octopath assets, code, music or text. No scanned sourcebook art or verbatim book text; adventure plots are
  adapted and rewritten.
- RPG-Cobo is Apache-2.0: keep its LICENSE/NOTICE with any build.

## Open decisions
Tracked in `NOTES.md` session log.
