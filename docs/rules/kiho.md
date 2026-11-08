# Rules — Kiho (L5R 3e → Octopath) — DRAFT v0.1

Source: *L5R 3e Core Book Revised*, Book of Air, pp. 266–275 (OCR `_research/books_txt/L5R - 3E - Core Book
Revised.ocr.clean.txt`, lines ≈ 27432–28365). 49 kiho indexed with `scratchpad/kiho.py`, which anchors on the
`MASTERY:` lines. Paraphrase only. ⚠ = OCR damage; check the page image.

## 1. 3e rules (summary)
- **Who:** monks (3 at start, +2 per Rank). **Shugenja may learn kiho** at a cost of XP = Mastery, need **Ring ≥
  Mastery** in the kiho's element, and may know at most **one kiho per shugenja school Rank**. Bushi and courtiers
  can't, unless they hold a monk school.
- **Types:**
  - **Martial:** delivered by an *unarmed* strike, one per attack, no action cost.
  - **Internal:** defensive; one active at a time; activated by 15 min of meditation, or 1 Void + a complex action.
  - **Kharmic:** a triggered reaction; one active at a time.
  - **Mystical:** no limit on how many are active.
- Every kiho has a **drawback**, like kata. Mastery levels range from 3 to 8.

## 2. Who gets kiho in *Rokugan Traveler*
| Holder | Why |
|---|---|
| **Isawa Haruki** | The only traveler who qualifies (shugenja). Max **5 kiho**, one per Rank. They come from **story rewards at Brotherhood temples or shrines**, not from the level picks, so they don't compete with his spells. |
| **Enemies:** Togashi Kokujin's tattooed cultists (1120 canon); **Togashi Akuro** (Hindsight antagonist) | Martial and atemi kiho become enemy skills: paralysis, blindness, VP drain. Kokujin's cult appears in Phoenix Ch2 *The Silent Court*. |
| ✅ **Jinnai** *(orig.)*: Ronin arc guest | A lay brother of the **Order of Osano-Wo** (fire-and-thunder martial monks; their shrine is the finale's Act 1 battlefield), and also a member of the Order of the Snake. Guest skills: **Freezing the Lifeblood** (paralyze, 2 uses) and **Chi Protection** (heal and cure atemi effects, 1 use). Passive: Kharmic Strike counter. |
| ✅ **Togashi Yosai** *(orig.)*: Dragon arc guest | A tattooed Togashi (*ise zumi* count as monks). **Dark humour:** cheerfully narrates his own likely deaths and keeps a tally of the Fortunes' attempts on his life. Tattoos (3e core, Book of Water):<br>- **Crow:** Taint immunity, but Shadowlands beasts *always* target him ("Apparently I'm delicious").<br>- **Dragon:** fire breath on several foes; it burns him too.<br>- **Arrowroot:** heals an ally, and he takes half the wounds.<br>Guest skills: *Dragon's Breath* (Fire AoE, self-damage, 2) and *Arrowroot* (heal ally, self-damage, 2); Crow is a passive taunt vs. Tainted foes. Appears in Dragon Ch1 (Isle of Silk: one of the murdered monks was his order-brother), in the Tamori's Furnace crossroads, and in the finale. Hunting Kokujin's cultists → also a cameo in Phoenix Ch2. |

### Octopath implementation
- **Internal and Kharmic kiho** → **toggle buffs** costing **1 VP to activate** (3e "1 Void"). Only one Internal
  and one Kharmic can be active at a time. Active until the battle ends or Haruki turns them off.
- **Mystical kiho** → mostly **field abilities**, used from the map menu like path actions.
- The *drawback is mandatory*. It is what makes kiho feel unlike spells.

## 3. Haruki's kiho menu (he picks 5 of these over the game)
| Kiho (element, ML, type) | Earliest | Octopath effect |
|---|---|---|
| **Self No Self** (Void 3, Internal) | R1, once his Void reaches 3 | Spend his turn meditating → **restore VP to max**. After that he can't Boost for 2 turns. **Once per inn rest.** *Thematic core: the boy with half a soul learns that "self" is empty.* Recommended first kiho (Phoenix Ch1 or Ch2 reward). |
| **Channel the Fire Dragon** (Fire 3, Internal) | R1 | Fire and ice damage to him −(Rank × 10%). Field: lets him cross heat and cold hazard tiles. Drawback: the party's ambush/pre-emptive odds drop, since he is "easily surprised". |
| **Heart of Stone** (Earth 3, Kharmic) | R1 (Earth 3 at Lv 14) | After taking damage: spend 1 VP to **cut that hit's damage by a flat amount** (3e: −10 Wounds ≈ 12% of max HP). Once per hit; several hits per round are fine. *(Checked on the page image, p. 269.)* |
| **Ebb and Flow** (Water 3, Kharmic) | R1 | While Defending, each enemy that **misses** him earns a counter next turn with +accuracy (more for a wider miss). His weak Bo finally matters. |
| **Speak to the Soul** (Water 4, Mystical) | R2+ | **Field:** touch an NPC or object → learn its strongest element, whether it's an awakened *nemuranai*, and whether it carries **Taint or the Lying Darkness**. A key story tool: Bloodspeaker relics, Nashiko's mask. |
| **Ancestral Guidance** (Void 4, Mystical) | R3 (Void 4 at Lv 42) | **Field:** commune with local ancestors or restless spirits; ask up to Void-rank questions; cryptic hint system. Lion+Phoenix crossroads (Bloodspeaker's Skull). |
| **Touch the Void Dragon** (Void 4, Internal) | R3 (Void 4 at Lv 42) | **Regional element +1:** caves Earth, coast Water, plains Air, volcanic/forge Fire. Spells of the map's element get +1 tier. Drawbacks: **enemy shugenja on the map learn his kit** (they resist his Attune element); in Tainted maps he gains **Taint** each turn. Strong with Attune. |
| **Parting the Waves** (Water 4, Internal) | R2 (Water 4 at Lv 30) | All damage to him −(Water × 4%). **Drawback: his own damage drops by the same percentage.** *(Checked, p. 274.)* |
| **Purity of Shinsei** (Fire 5, Mystical) | post-game (his Fire reaches 5 only after Lv 61; stats.md) | **Field:** lights dark dungeons (bigger vision radius). **Battle:** Tainted, Lying Darkness, Gaki and Jigoku enemies get **Terror** at Fire-rank strength. Shinomen Mori finale. |
| **Grasp the Earth Dragon** (Earth 4, Internal) | R4 (Earth 4 at Lv 54) | He can't be KO'd except by lethal "death" effects (a Guts-style survival at 1 HP); debuffs reduced by his Rank. Drawback: **he can't cast verbal spells**, only basic attacks and items. A last-stand stance. |

### Kept out of Haruki's menu, on purpose
- **Martial and atemi kiho** (Air/Earth/Fire/Water Fist, Falling Star Strike, Freezing the Lifeblood, Death Touch,
  Stain upon the Soul, Slap the Wave): they need unarmed monk training → enemy and monk-guest kit.
- **Unattunement** (Void 5): "an abomination to shugenja" → **Togashi Akuro / Kokujin boss skill** (seals one of
  the party's elements for the battle).
- **Way of Void (Kukan-do)** (Void 7): both sides lose all Rank techniques → a **boss gimmick**: the travelers
  fight with skills only.
- ML 6–8 legendaries (Eight Directions Awareness, Walk through the Mountain, Spirit of Water, Root the Mountain,
  Harmony of the Mind): reserved for **Mirumoto Hikaru / Togashi NPCs** and story set-pieces.

## 4. Enemy kiho kit (Kokujin's cultists, Akuro)
| Kiho | Enemy skill |
|---|---|
| Freezing the Lifeblood | **Paralyze** one traveler for Rank turns; the victim spends VP to try to break free. |
| Falling Star Strike | **Blind** (accuracy down a lot) for Fire turns. |
| Stain upon the Soul | Stacking −Accuracy/−damage, no HP damage. |
| Void Fist / Overwhelm the Spirit | **VP drain**: steals or burns the target's Boost Points. |
| Kharmic Strike | Telegraphed **counter stance**: guaranteed counter on each hit taken. |
| Slap the Wave | AoE **Confuse** that hits allies too (cultists are reckless). |
| Way of Flame | Self-buff (+damage) that burns its own HP each turn. Pairs with *Death Touch* for Akuro's final phase. |

## 5. Next
1. ✅ ⚠ entries checked against the page images (Heart of Stone, Parting the Waves).
2. *Masters of Magic* mentions kiho about 40 times. Check it for shugenja-specific kiho rules or new kiho.
3. 4e *Book of Air/Earth/Fire/Water/Void* have 4e kiho lists (and 4e kata). Mine them for enemy variety only;
   3e stays the base.
