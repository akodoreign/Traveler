# Rules — Traits, Rings & Octopath Stats — DRAFT v0.1

Sources:
- *L5R 3e Core*: family trait bonuses (Book of Earth, OCR ≈ lines 5429–7560) and school benefits (Book of Water).
- Rings = **the lower of their two Traits**: Air = Reflexes/Awareness · Earth = Stamina/Willpower · Fire =
  Agility/Intelligence · Water = Strength/Perception · Void stands alone.
- Constants are placeholders for engine balancing; the *shape* is the design.

## 1. Family + school bonuses (3e, from OCR)
| Traveler | Family bonus | School benefit | Notes |
|---|---|---|---|
| Natsuko | Hiruma **+1 Stamina** | Hiruma Scout **+1 Stamina** | ✅ Both confirmed on the page images (pp. 48, 124). Stealth starts at 2. |
| Rensei | Kakita **+1 Agility** | Kakita Bushi **+1 Reflexes** | |
| Gendo | Kitsuki **+1 Perception** | Kitsuki Courtier **+1 Intelligence** | (Mirumoto: +1 any; not taken, since it is a secondary school) |
| Shizue | Akodo **+1 Perception** | Akodo Bushi **+1 Agility** | |
| Haruki | Isawa **+1 Willpower** | Isawa Shugenja **+1 Intelligence** | |
| Mitsue | Shosuro **+1 Awareness** | Shosuro Shinobi **+1 Reflexes** | |
| Tamotsu | Ide **+1 Awareness** | Ide Emissary **+1 Perception** | |
| Sayo | none (born ronin) | depends on her **first ronin school**: Warrior +1 Str / Duelist +1 Agi / Yojimbo +1 Ref | chosen in the prologue |

## 2. Trait → Octopath stat mapping
| Octopath stat | Driven by | Why (3e) |
|---|---|---|
| **Max HP** | **Earth** ring (+ Stamina) | Wound ranks are Earth-based |
| **Max SP** | **Void** + Willpower (+ Rank for shugenja) | Void Points and spell slots (Ring + School Rank) |
| **P.Atk** | **Strength** | Damage rolls Strength + the weapon's DR |
| **P.Def** | **Stamina** (+ armour) | Resilience |
| **E.Atk** | **Intelligence**; per-element potency × (that **Ring** / 3) for shugenja | Spells roll the element's Ring |
| **E.Def** | **Willpower** | Resisting magic and fear |
| **Accuracy** | **Agility** | Attack = Agility + weapon skill |
| **Speed** | **Reflexes** (+ Insight Rank) | Initiative = Reflexes + Insight Rank |
| **Evasion** | **Reflexes** | TN to be hit = Reflexes × 5 + 5 |
| **Crit** | Agility + **Void** | Exploding dice and Void spends |
| *(field)* Perception | Discern, spotting hidden items, ambush odds | |
| *(field)* Awareness | Social path actions; resisting Charm/Confuse | |

Draft formulas (L = level; T = trait as a decimal, interpolated between schedule steps):
- MaxHP = (60 + 30·Sta + 20·Earth) · (1 + L/12)
- MaxSP = (20 + 12·Void + 6·Wil) · (1 + L/15); shugenja ×1.4
- P.Atk = (10 + 9·Str) · (1 + L/14) + weapon · P.Def = (8 + 8·Sta) · (1 + L/14) + armour
- E.Atk = (10 + 9·Int) · (1 + L/14) · E.Def = (8 + 8·Wil) · (1 + L/14)
- Speed = 20 + 12·Ref + 3·Rank (+ L/4) · Evasion% = 2·Ref + armour/kata modifiers · Accuracy% = 90 + 2·Agi
- Crit% = 2 + Agi + Void

## 3. Starting traits (Lv 1) and trait schedules
Order: **Sta Wil | Str Per | Agi Int | Ref Awa | Void**. 3e base is 2 everywhere, then family + school, then
creation points (designed to fit each concept).
- After Lv 61 every traveler gains +1 to two traits at Lv 70, 80 and 90 (post-game).
- The schedules are built so the **ring gates in `kata.md` / `kiho.md` are met at the listed levels.**

| Traveler | Lv 1 traits → rings (Air/Earth/Fire/Water/Void) | Schedule (Lv: +1 trait) | Lv 61 traits |
|---|---|---|---|
| **Natsuko** | 4 3 · 2 3 · 3 2 · 3 2 · 2 → A2 E3 F2 W2 V2 | 6 Ref · 12 Awa (**Air 3 at 12** → *Striking as Wind* at Lv 15) · 18 Str (**Str 3 for the Tetsubo**, Hida kit at Lv 21) · 24 Sta · 28 Agi · 32 Ref · 36 Wil · 38 Int · 42 Wil · 46 Per · 50 Ref · 54 Void · 58 Agi · 60 Sta | 6 5 · 3 4 · 5 3 · 6 3 · 3 → A3 **E5** F3 W3 V3 |
| **Rensei** | 2 2 · 2 2 · 3 2 · 3 3 · 3 → A3 E2 F2 W2 V3 | 5 Agi · 10 Ref · 14 Int · 20 Void · 24 Agi · 28 Sta · 32 Ref · 36 Wil · 40 Awa · 44 Str · 48 Per · 52 Agi · 56 Void · 60 Int | 3 3 · 3 3 · 6 4 · 5 4 · 5 → A4 E3 F4 W3 **V5** |
| **Gendo** | 2 3 · 2 3 · 2 4 · 2 3 · 3 → A2 E2 F2 W2 V3 | 6 Per · 12 Sta · 18 Int · 22 Agi (Mirumoto starts) · 26 Ref · 30 Str · 34 Agi · 38 Wil · 42 Per · 46 Ref · 50 Void · 54 Awa · 58 Agi | 3 4 · 3 5 · 5 5 · 4 4 · 4 → A4 E3 **F5** W3 V4 |
| **Shizue** | 2 2 · 3 3 · 3 2 · 2 2 · 2 → A2 E2 F2 W3 V2 | 8 Int (**Fire 3 at 8** → *Striking as Fire* at Lv 15) · 12 Str · 16 Per · 20 Sta · 24 Wil · 28 Agi · 32 Awa · 36 Str · 40 Void · 44 Per · 48 Agi · 52 Ref · 56 Sta · 60 Int | 4 3 · 5 5 · 5 4 · 3 3 · 3 → A3 E3 F4 **W5** V3 |
| **Haruki** | 2 3 · 3 3 · 2 3 · 2 3 · 3 → A2 E2 F2 W3 V3 | 6 Per · 10 Agi (Fire 3: *Channel the Fire Dragon*) · 14 Sta (Earth 3) · 18 Ref (Air 3) · 22 Int · 26 Wil · 30 Str (**Water 4**) · 34 Per · 38 Awa · 42 Void (**Void 4**: stronger Void spells) · 46 Int · 50 Wil · 54 Sta (Earth 4) · 58 Agi (Fire 4) | 4 5 · 4 5 · 4 5 · 3 4 · 4 → A3 E4 F4 W4 V4 *(−1 Void after Ch4: see haruki-spells §5)* |
| **Mitsue** | 2 2 · 2 2 · 3 2 · 3 3 · 2 → A3 E2 F2 W2 V2 | 4 Agi · 10 Ref · 16 Awa · 20 Int · 24 Per · 28 Ref · 32 Sta · 36 Agi · 40 Awa · 44 Wil · 48 Str · 52 Void · 56 Ref · 60 Int | 3 3 · 3 3 · 5 4 · 6 5 · 3 → **A5** E3 F4 W3 V3 |
| **Tamotsu** | 2 3 · 2 3 · 2 3 · 2 3 · 2 → A2 E2 F2 W2 V2 | 6 Awa · 10 Wil · 14 Per · 20 Sta · 24 Void · 28 Int · 32 Awa · 36 Ref · 40 Str · 44 Wil · 48 Sta · 52 Agi · 56 Per · 60 Awa | 4 5 · 3 5 · 3 4 · 3 6 · 3 → A3 E4 F3 W3 V3 (**Awareness 6**) |
| **Sayo** (Warrior start) | 2 2 · 3 3 · 3 3 · 2 2 · 2 → A2 E2 F3 W3 V2 | 8 Sta · 10 Wil (**Earth 3 at 10** → *Earth* at Lv 10) · 16 Ref · 19 Awa (**Air 3 at 19** → *Wind* at Lv 20) · 24 Int · 28 Agi · 32 Per · 36 Str · 40 Void · 44 Sta · 48 Wil · 52 Agi · 56 Ref · 60 Int | 4 4 · 4 4 · 5 5 · 4 3 · 3 → A3 E4 **F5** W4 V3 (balanced) |
- Sayo, Duelist start: swap Str 3 / Agi 3 for Str 2 / Agi 4, and move "Lv 4: Str" to the front of her schedule so
  *Striking as Water* (Water 3) is still reached by Lv 5.

## 4. Checks
- **Role check** (verified with `scratchpad/traits.py`, which applies the schedules):
  - Natsuko: the only Earth 5 → highest HP; Ref 6 → evasion tank.
  - Rensei: Agility 6 and Void 5 (crit duelist); Ref 5 for speed.
  - Mitsue: Ref 6 and Air 5 → evasion and speed.
  - Shizue: Water 5 and Str 5 → Akodo damage.
  - Haruki: an even 4 in every element (an Isawa generalist).
  - Gendo: Fire 5 (Int/Agi). Tamotsu: Awareness 6 for social. Sayo: balanced, Fire 5.
- **Gate check (all pass):** Natsuko Air 3 at 12 (needed by 15) · Shizue Fire 3 at 8 (15) · Sayo Water/Fire 3 at 1,
  Earth 3 at 10 (10), Air 3 at 19 (20) · Mitsue Air 3 at 1.
- Haruki's kiho: Water 4 at 30 (*Speak to the Soul*, *Parting the Waves*); Void 4 at 42 (*Ancestral Guidance*, *Touch
  the Void Dragon*); Earth 4 at 54 (*Grasp the Earth Dragon*). **Fire 5 (*Purity of Shinsei*) only comes
  post-game.** Either accept that, or give him "Fire +1 at Lv 70".

## 5. Open points
1. ✅ Hiruma bonuses verified.
2. Tune the constants in a prototype (RPG-Cobo `class.json` growth curves, or a plugin computing stats from traits).
3. Show Rings and Traits in the status screen (an L5R flavour layer), with Octopath stats derived from them.
