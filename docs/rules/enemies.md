# Rules — Enemy Design & Suki Weaknesses — DRAFT v0.1

Builds on DESIGN §2 (Suki = Octopath Break; *Resolve* points as shields) and the lore keys in
`story/00-synthesis.md`:
- **jade** vs. Taint / Regret
- **crystal** vs. spirits / Desire / the invisible
- **obsidian** vs. Fear

## 1. Suki rules
- Each enemy has **Resolve** (shield points): **2–6** for common foes, **8–14** for chapter bosses, **16–30** for
  the finale and superbosses.
- Hits that match one of its **weaknesses** (weapon type, element or material) remove 1 Resolve per hit. Boosted
  multi-hits remove more.
- At 0 the enemy is **Suki** (unbalanced): it loses the rest of this turn and next turn's action, takes **+50%
  damage**, and its Resolve refills when it recovers. (Octopath standard.)
- **Weakness discovery:**
  - Hidden "?" icons are revealed by hitting the weakness, or by Gendo's **Deduce**, Tamotsu's **The Heart Listens /
    Appraising Eye**, Natsuko's **Know the Foe** (Shadowlands only), **Lore: X** analysis, or Haruki's **Speak to
    the Soul** (element only).
- **Materials (not elements):** **Crystal** and **Obsidian** are weakness icons hit only by **items** (crystal
  dust, obsidian shard, crystal-tipped arrows) or by *material-coated weapons* (story rewards).
  - ✅ **Obsidian is a corrupt material** (user ruling): in Rokugan it is used almost only by the corrupted. Every
    use of an obsidian item or weapon **gives the user Taint (1 stack)**. Obsidian weapons in **enemy** hands
    inflict Taint on the travelers they hit.
  - So obsidian is a **temptation key**: the only sure answer to Fear-type demons, at a price. Clean alternatives
    stay open: Courage of the Seven Thunders and Death Trance blunt Fear, and jade still removes Resolve, just more
    slowly. Taint can be cleansed (Jade Remedy, shrines), so a careful party can afford a little obsidian. **Jade** is both an
  element (spells, Remedy) and a material (jade arrows, jade-studded tetsubo).

## 2. Enemy families (templates)
| Family | Typical weaknesses | Resists / immunities | Signature behaviour (from L5R) |
|---|---|---|---|
| **Bandits, ronin, ashigaru** | Katana, Yari, Yumi; Fire | — | Can **surrender** (Cite the Law, Settle the Account, Honourable Challenge) → no kill, bonus Honor; flee at low HP |
| **Samurai (clan soldiers)** | depends on school: heavy-armoured Crab → Tetsubo, Bo; Crane duelists → Yari, Yumi | Know the School bonuses apply | Use real **school techniques** and **kata** (`kata.md` §4); duelists counter Katana |
| **Shadowlands goblins / bakemono** | **Jade**, Fire, Yari, Tetsubo | — | Swarms; Taint attacks |
| **Ogres / trolls (carapace)** | **Jade**, **Tetsubo** (armour-breaker), Earth | Tanto (weak vs. carapace) | Carapace = +Def that Heavy Weapons ignore |
| **Undead (zombies, skeletons)** | **Jade**, Fire, **Bo / Tetsubo** (blunt) | **Terror**, poison, sleep | Slow; rise again unless finished with Fire or Jade |
| **Oni** | **Jade**, element varies; **true name** → reveals one more weakness and −Resolve (Gendo / Ancestral Guidance / story) | High Resolve; regenerate | Carry Fear (Terror auras); **Prison of Earth** can seal minor oni |
| **Maho-tsukai** | **Jade**, Katana, Void (spell disruption: *My Brother's Soul*, Counter-prayer) | — | **Maho** skills: pay their own HP to cast; inflict **Taint**; summon. Using maho counts as a *charged* move (Essence of Void blocks it). |
| **Spirits: kami, ghosts, gaki** | **Crystal**, element opposed to their own; Water (purify) | **Physical** (weapons glance off) unless jade/crystal | Possession; silence; only magic and materials hurt them fully |
| **Kansen** (corrupted kami; Blood and Iron) | **Crystal**, magic | Physical | Invisible clouds; corrupt shugenja |
| **Shuten Doji servants** (Snake lore: Fear / Regret / Desire) | **Obsidian** (Fear; Taints the user), **Jade** (Regret), **Crystal** (Desire) | each one resists the other two materials; jade still works at half effect on every Shadowlands servant | Spread by **sight / hearing / touch** → key items (blindfold, wax earplugs, gloves) protect the party |
| **Beasts** (wolves, bears, the weretiger) | Yari, Yumi, Fire | — | Terror via Signal Shot; Animal Handling can calm them (no-kill) |
| **Lying Darkness / Nothing-touched** (finale) | **Crystal** (reveals), **Void** | Most elements | Invisibility, mimicry; masks |
| **Naga** (the Naga waking, 1120s; optional encounters) | Air, Yari | Water | Pearl magic; not evil → talk-out option |

## 3. Status effects (shared by heroes and enemies)
| Status | Source (L5R) | Effect |
|---|---|---|
| **Terror** (strength 1–5) | Fear rank | Each turn, chance (by strength vs. the target's Willpower) to **skip the turn**; can't Boost |
| **Shaken** (stacks) | wound penalties | −Accuracy / −Evasion per stack |
| **Taint** (stacks) | Shadowlands, maho | Stacking −max HP; at high stacks, "Tainted" (now weak to Jade **yourself**). Cleansed by Jade Remedy, Strength of the Crow, shrines. |
| Poison · Blind · Sleep · Silence · Paralyze | poisons, Burst, Wind-Borne Slumbers, deafened (Fury of Osano-wo), atemi | Octopath standard |
| **Prone** | Knockdown | Loses next action |

## 4. Boss design rules
1. **Every chapter boss uses at least one exploit from its source adventure** (the research notes list them, e.g.
   Nashiko is colour-blind; Kansen are hurt only by crystal; the Coward breaks after one jade hit).
2. **Phases** at 66% and 33% HP: new skills, and new weaknesses revealed or hidden.
3. **Telegraphed big moves** ("gathering Void…") → Tamotsu's *When the Veil Moves* and Gendo's *Breaking Waves*
   counter these.
4. Human bosses **use their canon school** (`kata.md` §4 lists their kata). Duelist bosses open with an iaijutsu exchange.
5. **Honor matters:** some human bosses offer **surrender at 25% HP**. Accepting gives Honor and a different
   epilogue line; refusing gives the drops.

## 5. Next
- Per-chapter boss sheets (stats, Resolve, weaknesses, phases), drawn from the research notes, once the scene
  scripts start.
