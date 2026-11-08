# Rules overview — L5R → Octopath (for review)

All files are drafts. Sources: the OCR'd 3e *Core Book Revised* and *Masters of Magic*, plus the 5e core and
*Emerald Empire* for flavour. Effects are paraphrased; no book text goes into the game.

## The system on one page
- **Levels → Insight Rank:** R1 Lv 1–20 · R2 21–40 · R3 41–50 · R4 51–60 · R5 61+ (cap 99).
  - Each Rank threshold → the next **school technique** (`schools.md`).
- **Every level:** stats grow from L5R **Traits**, on a per-traveler schedule (`stats.md`).
  - Earth→HP, Water/Strength→ATK, Fire/Intelligence→E.Atk, Air/Reflexes→Speed and Evasion, Void→SP and Crit.
- **Every 2 levels:** +1 **skill rank** (`skills.md`).
  - Skills are capped by Rank: 3 / 5 / 7 / 9 / 10, so each Rank opens the next 3e mastery tier.
  - **Path actions use skills** (Duel = Iaijutsu, Charm = Etiquette, Pilfer = Sleight of Hand …).
  - **Low Skills cost Honor.**
- **Every 5 levels:** one pick from:
  - **kata:** stances, 1 slot (3 with Striking as Void), set at inns; free toggle in battle; VP empowers them
    (`kata.md`)
  - **battle skills:** 3e maneuvers plus each traveler's signatures, gated by skill rank (`battle-skills.md`)
  - **spells**, for Haruki: 2 per pick (`haruki-spells.md`)
- **Story rewards:**
  - Haruki's **kiho** (max 5, from Brotherhood temples; `kiho.md`)
  - Phoenix **First Tier secret spells**
  - advantages, named blades
- **Battle:**
  - **Suki** (Resolve shields) and Void Points (VP).
  - Weaknesses: 6 weapons, 6 elements, and the **materials crystal and obsidian** (`enemies.md`). **Obsidian is a
    corrupt material:** using it inflicts **Taint** on the user (user ruling).
  - The Break mechanic is called **Suki** ("opening"), renamed from Kuzushi so the canon Darkfever oni *Oni no
    Kuzushi* can keep its name.
  - Statuses: **Terror**, **Shaken**, **Taint**.
- **Weapons:** 3e damage ratings → power and traits (Katana Boost bonus, Tetsubo armour-break, Bo evasion…).
  Arrow types → Yumi shot skills (`weapons.md`).
- **Sayo's Remedy:** Alfyn-style base + catalyst concoctions from Rokugani herbs (ginseng, rhubarb, jade petal,
  hanabi…) (`sayo-remedy.md`).

## Decisions (✅ = approved by the user, session 2)
1. ✅ **Natsuko → evasion ("dodge") tank**, with an optional heavy-armour mode from the Hida kit at R2.
2. ✅ **Haruki = Water + Void Affinity, with Ishiken-do from the start.** **Void Points are his AP:** Void spells cost
   VP and scale with the VP he holds; *Drawing the Void* fuels it. Ch4 costs him 1 Void (the "Whole" passive is
   proposed in haruki-spells §5).
3. ✅ **Mass Path to Inner Peace** (VP 3 heals the party). Rejuvenating Vapors' SP restore stays a small invention.
4. **Gendo** gets no kata until his Mirumoto secondary school at R2.
5. **Tamotsu** gets no kata; he relies on courtier and trader battle skills. ✅ He starts at **Status 3–4**: the
   Ide are personable and loved by everyone.
6. ✅ **Kiho:** Haruki (≤ 5), plus two **monk guests**: **Jinnai** (Ronin arc) and a **Togashi tattooed man** in the
   Dragon chapters, with dark-humour flavour (`kiho.md` §2). Tattooed Togashi count as monks.
7. **Sayo** is the only one with all five common kata (her "wave-woman's elements" niche).
8. Some kata and kiho are deliberately **enemy/guest-only** (Hida's Avalanche, Endless Strike, Unattunement, Way of
   Void…).

## Verified against the page images
- Hiruma bonuses.
- Crab, Crane and Dragon kata.
- Heart of Stone and Parting the Waves.
- Death of Flame and Way of Deception.
- Battle/Defense/Iaijutsu masteries.
- Shosuro R4/R5.

The tool for this is `scratchpad/render_page.py`.

## Still to do (rules)
- Final numbers: balancing in an engine prototype.
- ✅ Boss and battle sheets: `bosses.md` (every battle id in the scripts).
- Equipment and nemuranai list (`equipment.md`, including every drop and steal named in `bosses.md`).
