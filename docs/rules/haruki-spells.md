# Rules — Isawa Haruki's Spells → Octopath Skills — DRAFT v0.1

Sources:
- *L5R 3e Core* spell chapter (all 143 elemental spells; list and lines in `spell-and-kata-index-3e-core.md`).
- *Masters of Magic*: the Phoenix First Tier spells and the multi-element spells.

Effects are paraphrased. Every number is a **first-pass proposal** for balancing later.

## 1. Translation rules (shugenja → Octopath)
| 3e | Octopath / RPG-Cobo |
|---|---|
| Spell slots per element per day | One **SP** pool. Cost by Mastery Level: **ML1 6 · ML2 10 · ML3 16 · ML4 24 · ML5 34 · ML6 48**. |
| Rings (Air/Earth/Fire/Water/Void) | Ring weighting feeds **E.Atk / E.Def** (DESIGN §4c). The spell's element sets which enemy shields it hits. |
| Raises / "Special Raises" | **Boost (VP 1–3).** Each spell's own Special Raise *is* its Boost effect wherever one exists: extra target, more damage, longer duration. That keeps the translation faithful. |
| Affinity (Isawa: any) | ✅ **Water + Void** (user decision). Boosting a Water or Void spell counts **one level higher** (VP 1 = Boost 2). Talent **Attune** adds a per-turn element on top. |
| **Ishiken-do** advantage (3e: 10 points, **5 for Phoenix**; needed to cast Void; +1 free Raise whenever Void Points enhance a spell; gives an **Obligation to the Isawa**) | Haruki **starts with Ishiken-do**. **Any Boosted spell gets one free Boost effect on top** (the free Raise). Story: the Obligation is why the Isawa keep him close after the childhood accident. |
| Void spells (3e: cast with *current Void Points* as the Ring) | ✅ **Void Points are the fuel (AP-style, user decision).** Void spells **cost VP, not SP**: ML1–2 = 1 VP · ML3–4 = 2 VP · ML5 = 3 VP. Their power scales with the **VP he still holds after paying**. *Drawing the Void* generates VP, so managing the Void economy is his play pattern. Available **from R1** on the normal tier schedule. |
| Durations: 5 rounds / 1 minute / 1 hour+ | **3 turns / 5 turns / the whole battle.** |
| "Full Concentration" spells | **Concentration:** the effect lasts until Haruki **takes damage** or casts another Concentration spell. Shields him; synergy with Natsuko's taunt. |
| Radius or cone area | **All enemies.** "Self" stays self; touch/target = single. |
| Casting time / ritual | **Field-only** (menu), or a **charge**: cast now, resolves at the start of his next turn. |
| Weapon-summon spells (Yari of Air, Tetsubo of Earth, Katana of Fire, Bo of Water) | **Kami Weapons:** an immediate hit **of that element *and* weapon type**. Haruki's basic Attack then *becomes* that weapon and element for the battle. **He can break Yari/Tetsubo/Katana/Bo shields**, which helps the weapon-coverage problem. |
| Lightning spells (the Osano-wo line) | **Fire** element (Osano-wo is the Fortune of Fire *and* Thunder). |
| Jade Strike / Tomb of Jade | **Jade** element: hits **only Tainted** enemies, which are often weak to it. |
| Field utility spells | **Field skills** in the map menu, like path actions. Many come from **scrolls found in chests**, so exploration teaches magic; the level picks go to battle spells. |

**How Haruki learns spells:**
- **Start (Lv 1):** Sense, Commune, Summon, Counterspell, plus 6 spells (3 of his Affinities, 3 others), as in 3e.
- **Every-5-level pick:** **2 battle spells** from any unlocked Mastery tier.
- **Tier unlocks:** ML1 at R1; ML2–3 at R2 (Lv 21); ML4 at R3 (Lv 41); ML5 at R4 (Lv 51); ML6 at R5 (Lv 61).
- **Field spells** come from scrolls and story.
- **Phoenix First Tier secrets** come from the **Elemental Masters** as story rewards.

## 2. Starting kit (Lv 1)
| Spell | Skill | Target | SP | Boost |
|---|---|---|---|---|
| **Path to Inner Peace** (Water 1) | Heal HP (the core heal) | 1 ally | 6 | Heal more per VP. ✅ **VP 3: heals all allies** ("mass Path to Inner Peace", approved by the user). |
| **Bo of Water** (Water 1) | Kami Weapon: **Water + Bo** hit, then his attack stays Water/Bo | 1 enemy | 6 | +1 hit per VP (3e: +1k0 once) |
| **Drawing the Void** (Void 1) | **+1 VP now** (can exceed the normal cap for this turn). Once per battle. | self | — (free) | *Ishiken free Raise:* **+2 VP** instead when cast with Void Attuned |
| **The Fury of Osano-wo** (Fire 1) | Fire (thunder) bolt; nearby enemies may be **Silenced** 1 turn. **Stronger in storm weather** (rain/storm map states). | 1 enemy | 6 | +damage |
| **Tempest of Air** (Air 1) | Air gust: light damage, **Accuracy −** 2 turns; more damage vs. low-Earth (frail) enemies | all enemies | 8 | +1 turn, +damage |
| **Earth's Touch** (Earth 1) | Def or E.Def + for 3 turns | 1 ally | 6 | +1 target (1 VP), larger bonus (2 VP) |
| Counterspell | **Counter-prayer:** a reaction set this turn; the next enemy spell is cancelled (the SP cost scales with that spell's tier) | — | 6+ | Fortified: can't be countered back |
| Sense · Commune · Summon | **Field:** detect hidden spirits, people and items · ask the local kami (hint system) · conjure a small amount of an element (light, water, stone) for puzzles | — | 2–4 | — |

## 3. Battle spell list (picks), by element
Rank = earliest tier. Utility marked **F** = field skill (scroll or story).

### Water — healer core (Affinity)
| Spell (ML) | Skill | Target | SP | Boost |
|---|---|---|---|---|
| Sympathetic Energies (1) | **Take a debuff off an ally onto himself**, or pass one of his buffs to an ally. *His guilt as a mechanic.* | 1 ally | 6 | — |
| Reversal of Fortunes (1) | **Fortune:** the ally's low damage rolls are re-rolled (raises the damage floor), 5 turns | 1 ally | 6 | +2 turns |
| Castle of Water (1) | **Water ring:** melee attacks on Haruki may fail (Earth contest), and attackers take light damage | self | 6 | wider / higher (stronger) |
| Rejuvenating Vapors (2) | Restore **50% SP** to an ally and cure fatigue debuffs. Once per inn rest. | 1 ally | 10 | — |
| Heart of Mortality (2) | **Bond** one ally for the whole game: his spells on that ally can't miss and reach them anywhere. Swappable at an inn. | 1 ally | 10 | — |
| Regrow the Wound (3) | **Concentration HoT:** heals the target every turn | 1 ally | 16 | +heal |
| Near to Ice (3) | Ally ignores **Shaken** and HP-threshold penalties | 1 ally | 16 | +2 turns |
| Bane of the Scorpion (3) | Cure **poison** | 1 ally | 16 | — |
| Silent Waters (3) | **Contingency:** store an ML ≤ 3 spell that fires on a trigger ("when an ally falls → Path to Inner Peace") | self | 16 | — |
| Hand of Jurojin (4) | Cure **disease**, including supernatural ones. *Darkfever, Phoenix Ch1/Ch3.* | 1 ally | 24 | — |
| Peace of the Kami (6) | **Full heal + cleanse all.** Once per battle. | 1 ally | 48 | — |
| Words of the Kami (6) | **Purge:** Tainted non-bosses destroyed; Tainted bosses → 1 HP, contested. The whole party is **deafened** 1 turn (Silence). | all enemies | 48 | — |
| Whirlpool (5) / Rise, Water (6) | Water-map AoE drowning (damage grows each turn) / **summon a Water kami** ally (3 turns) | all / summon | 34 / 48 | +turns |
| F: Purify Water (1) · Reflections of Pan Ku (1, identify nemuranai) · Reflective Pool (2, scry a known place → map reveal) · The Ties that Bind (2, quest-item tracker) · Wave-Borne Speed (2, dash) · Wisdom and Clarity (2, read lore books for extra info) · Way of Still Waters / Walking upon the Waves (3, swim / water-walk paths) · **Sacred Ground** (4, return to a consecrated shrine = fast travel) · Symbol / Wall of Water (4) · Part Water · Power of the Ocean · Waves Are Ever-Changing (5, animal form → small passages) | | | | |

### Fire — damage
| Spell (ML) | Skill | Target | SP | Boost |
|---|---|---|---|---|
| Katana of Fire (1) | Kami Weapon: **Fire + Katana** | 1 enemy | 6 | +1 hit |
| The Fires that Cleanse (1) | Fire burst — **Haruki takes half the damage too** | all enemies | 8 | +damage |
| Burst (1) | Flash: **Blind** (Accuracy −) 2 turns | all enemies | 6 | — |
| Biting Steel (1) | +ATK to an ally's **steel** weapon (Katana, Yari, Tanto; not Tetsubo, Bo or Yumi) for the battle | 1 ally | 6 | — |
| Fires of Purity (1) | **Fire sheath:** whoever the ally hits, or is hit by, takes Fire damage | 1 ally | 6 | +damage |
| The Fires from Within (2) | Fire orb | 1 enemy | 10 | **+1 extra target per VP** (3e Raise) |
| Speed of Flame (2) | Ally **acts first** next turn (Speed ++) | 1 ally | 10 | +1 target |
| Hurried Steps (2) | **Haruki acts again at once, but only to cast**; a Fire spell costs −25% SP | self | 10 | — |
| Aura of Flame (2) | Fire thorns on himself | self | 10 | — |
| Inferno's Tooth (2) | Heat an enemy's weapon or armour: damage each turn and ATK −. Only vs. metal-armoured/armed foes. | 1 enemy | 10 | +turns |
| Tail of the Fire Dragon (2) | For 3 turns his attack is a **Fire whip** (ranged, hits back rows) | self | 10 | — |
| Hungry Blade (3) | Ally Crit ++ and Accuracy + | 1 ally | 16 | — |
| Burn the Mind (3) | Big debuff; chance it **loses its turn** | 1 enemy | 16 | — |
| Heart of the Inferno (3) | Heavy Fire blast. **Consumes a "spell scroll" item**, or Haruki takes half the damage. | all enemies | 16 | +damage |
| Breath of the Fire Dragon (3) | For 2 turns his action becomes a strong Fire breath; he can't cast meanwhile | 1 enemy | 16 | — |
| Light of Yakamo (4) | Holy sunlight: **more damage vs. dishonourable** (Honor < 2) and **Tainted** foes; Honor-0 foes blinded | all enemies | 24 | +damage |
| Death of Flame (4) | **Accuracy and E.Atk −** (big; 3e lowers Agility and Intelligence) | 1 enemy | 24 | +turns |
| Fire Walking (4) | Ally immune to Fire until the first magical fire hits them | 1 ally | 24 | +1 target |
| Wall of Fire (4) | Enemies take Fire damage **whenever they act**, 3 turns | all enemies | 24 | +turns |
| Follow the Flame (5) | 3 turns: **a free extra Fire hit each turn** on any enemy, + burn | self | 34 | — |
| Everburning Rage (5) | Target treated as "Down": **skips 1 turn** and takes more damage. Not on bosses. | 1 enemy | 34 | +1 target |
| Strike of Osano-wo (5) | Fire cyclone + knockdown. Cost: a scroll item, or Haruki takes damage. | all enemies | 34 | — |
| Burn the Soul (5) | **Escalating Concentration DoT** (tiny → huge). **Using it costs party Honor** — "an unspeakable horror". | 1 enemy | 34 | — |
| Hochiu's Call of Heaven (6) · Rise, Flame (6) · Tempest of Fire (6) | Self fire aura (big AoE every turn, immune to ranged) · summon a Fire kami · **ultimate AoE**: afterwards his non-Fire spells cost +50% SP until an inn | — | 48 | — |
| F: Extinguish (1, put out fires; dampens Fire for 1 turn) · Ignite (1) · Waiting Flame (3, **set a fire trap on the map** → bonus damage on battle start) · Symbol of Fire (4) | | | | |

### Air — debuffs, illusion, utility
| Spell (ML) | Skill | Target | SP | Boost |
|---|---|---|---|---|
| Yari of Air (1) | Kami Weapon: **Air + Yari** | 1 enemy | 6 | +1 hit |
| Wind-Borne Slumbers (1) | **Sleep** (bosses: drowsy, Accuracy −) | 1 enemy | 6 | **+1 target per VP** |
| Way of Deception (1) | **Mirage:** 50% of attacks on Haruki miss; −30% after each offensive action he takes | self | 6 | +10% per VP (max 80%) |
| Mists of Illusion (2) | **Decoy:** the enemies' next single-target attack hits an illusion | party | 10 | — |
| The Eye Shall Not See (3) | Haruki is **untargetable** until he acts offensively | self | 16 | — |
| Summon Fog (3) | All combatants Accuracy −; Fire damage −; field: avoid encounters | all | 16 | — |
| Know the Mind (4) | **Reveals the enemy's next 2 actions** (field: an NPC's secret thought) | 1 enemy | 24 | — |
| Symbol of Air (4) | Battle form: **Sleep** all enemies on a failed contest, else a big debuff | all enemies | 24 | — |
| Wall of Air (4) | Party **immune to ranged/arrow** attacks, 3 turns | party | 24 | +turns |
| Poison of the Wind Spider (5) | Poison + blind cloud, damage each turn | all enemies | 34 | — |
| Whirlwind (5) | Damage each turn + Speed −− | all enemies | 34 | — |
| Slayer's Knives (5) | Wind-corridor damage + knockback (back-row enemies pushed off) | all enemies | 34 | — |
| Blessings of Jizo (6) · Rise, Air (6) · The Wrath of Kaze-no-Kami (6) | **Reflect all spells** on himself, 5 turns · summon an Air kami (ranged-proof aura) · ultimate storm: once per inn rest | — | 48 | — |
| F: By the Light of Lady Moon (1, reveal hidden items/traps) · **Quiescence of Air** (1, silence bubble → Mitsue's Eavesdrop/Stealth bonus) · Cloak of Night (1) · Nature's Touch (1, speak to animals) · Benten's Touch (2, **Charm/Barter +**) · Hidden Visage (2) · Secrets on the Wind (2, long-range eavesdrop) · **Whispering Wind** (2, lie detector — pairs with Gendo) · Echoes of a Breeze (2, send a message) · Call upon the Wind (2, float over gaps) · Essence of Air (3, walk through walls → secret rooms) · **Forgotten Murmurs** (3, make an NPC forget → **retry a failed chance path action** and erase the reputation penalty) · Mask of Wind (3) · Wisdom of the Kami (3, +path-action skill) · False Realm · Lady Moon's Legion (4, party invisible → no encounters for N steps) · Command the Clouds (5, change map weather) | | | | |

### Earth — wards, debuffs, anti-Taint
| Spell (ML) | Skill | Target | SP | Boost |
|---|---|---|---|---|
| Tetsubo of Earth (1) | Kami Weapon: **Earth + Tetsubo** | 1 enemy | 6 | +1 hit |
| Jade Strike (1) | **Jade** bolt: only damages Tainted. Wasted on the untainted, *and they are insulted* (an NPC reaction in the field). | 1 enemy | 6 | +damage; **VP 2: +1 target** |
| Earth's Stagnation (1) | Speed − and Evasion − | 1 enemy | 6 | — |
| Elemental Ward (1) | Resist one chosen element | self | 6 | VP 2: +1 element |
| Force of Will (1) | **Endure:** the ally survives one lethal hit at 1 HP, 2 turns | 1 ally | 6 | +1 turn |
| Armor of Earth (2) | Physical damage − (Rank × 4%) on himself | self | 10 | — |
| Courage of the Seven Thunders (2) | Immune to **Terror**; lasts twice as long if party **Honor ≥ 3** | 1 ally | 10 | +1 target |
| Grasp of Earth (2) | **Rooted:** Evasion −20%, Speed − | 1 enemy | 10 | — |
| The Mountain's Feet (2) | Immune to knockback, knockdown and "lose next turn" effects | 1 ally | 10 | — |
| Tremor (2) | Terror (weak) chance on all enemies; field: collapse weak structures | all enemies | 10 | — |
| Curse of Stone (3) | Speed −20% and ATK − | 1 enemy | 16 | **VP 2: +1 target** |
| Benevolent Protection of Shinsei (3) | **Sanctuary:** each enemy must pass a Willpower check to attack (once each). Stronger inside temples. | all enemies | 16 | — |
| Earth's Protection (3) | Party immune to weather and terrain hazards; Fire/Air spell damage − | party | 16 | — |
| Strength of the Crow (3) | **Taint immunity** for the party on Shadowlands/Shinomen maps (one day = until an inn) | party | 16 | — |
| Armor of the Emperor (4) | Ally damage taken −(Rank × 8%), 5 turns. **The tank buff.** | 1 ally | 24 | — |
| Death of Stone (4) | Def and E.Def − (big) | 1 enemy | 24 | — |
| Tomb of Jade (4) | **Jade:** encase a Tainted foe; damage every turn until it breaks free | 1 enemy | 24 | harder to break |
| Spikes of Earth (5) | Damage + Speed − for the rest of the battle | all enemies | 34 | — |
| Earthquake (5) | **Terror (strong)** + knockdown on all enemies; allies must pass a check or lose their turn | all | 34 | — |
| Prison of Earth (5) | **Seal a spirit** (oni, kami, summoned or other non-mortal) in a diamond: instant win vs. non-boss spirits. Consumes a Diamond. | 1 enemy | 34 | — |
| Kami's Strength (6) · Fraying of Ningen-do (6) · Rise, Earth (6) | Ally immune to physical, magic halved, 3 turns, once per battle · huge AoE (sacrifice an item, or Earth spells weakened afterwards) · summon an Earth kami | — | 48 | — |
| F: **Fires from the Forge** (1, repair bridges and objects → traversal) · Speed Growth (1, grow vines) · Hands of Clay (2, climb) · Walk Without Passing (2, no tracks → fewer outdoor encounters) · Immortal Steel (3, *ritual*: +ATK to one weapon for good — story item) · Shatter (4, break obstacles) · Wall of Earth (4, make a bridge or wall) · Symbol of Earth (4) · Divide into Ash (5, dig) | | | | |

### Void — Affinity element (Ishiken-do, from R1). **Costs VP, not SP**; power scales with the VP still held.
| Spell (ML) | Skill | Target | VP cost | Effect of VP held |
|---|---|---|---|---|
| Drawing the Void (1) | +1 VP (+2 with Void Attuned), once per battle (starting kit) | self | 0 | — |
| Essence of Void (2) | Target **can't use Boosted or charged moves** while Haruki Concentrates | 1 enemy | 1 | longer hold: the escape chance falls per VP held |
| Altering the Course (2) | Next turn, spending all VP counts as **one Boost level above max** | self | 1 | — |
| Kharmic Intent (3) | **Shared VP pool** with one ally for the battle | 1 ally | 2 | — |
| Void Release (4) | The ally uses **Haruki's Void-based stat** in place of one of theirs, 3 turns | 1 ally | 2 | +1 turn per VP held |
| Void Strike (4) | **Steal VP** (or the charge of a "gathering" enemy move); Haruki gains it | 1 enemy | 2 | +1 stolen per 2 VP held |
| Void Suppression (5) | Swap the target's highest stat with its lowest, 3 turns | 1 enemy | 3 | — |
| *Void Fist-like basic* — **Void Bolt** *(invented filler for an ML1 attack)* | Void damage, single target; ignores elemental resistances | 1 enemy | 1 | +damage per VP held |
- **Play pattern:** gather VP (Drawing the Void, natural +1/turn, *Self No Self* kiho), then spend it in bursts.
  He is the party's **Void battery**: Kharmic Intent lends VP to allies.
| F/story: Sense Void (1, astral scouting → reveal the map and spirits) · Moment of Clarity (3, spend VP → path-action skill +) · **Divine the Future** (5, ask one question = a big hint; no VP regen until 2 inn rests) · **Rise from the Ashes** (5, *ritual*: undo the last 6 hours of harm, Taint and poison. **Not death.** A Ch4 / finale set-piece.) | | | | |

### Harmony skills (*Masters of Magic* multi-element) — need two elements Attuned; can't be Boosted
| Pair (ML) | Skill |
|---|---|
| Air + Fire (2) | Wind-and-ember cone: damage + Accuracy − + **no ranged attacks** for enemies |
| Earth + Fire (2) | **Burning stone weapon** for an ally (strong; any weapon type) |
| Earth + Water (2) | **Water wall:** melee attackers repelled; Air/Fire attacks on Haruki weakened |
| Fire + Water (3) | **Drain:** Fire blast that heals Haruki (capped at the damage dealt) |
| Air + Earth (3) | **Stone double:** a decoy that also draws physical attacks |
| Air + Water (2) | Field: animal-companion bond (6 months) |

### Phoenix First Tier secrets — story rewards from the Elemental Masters (*Masters of Magic*)
- Air:
  - *Dreamwalker* (4): walk in a sleeper's dreams → **Mieko dream scenes** in Ch3–4.
  - *Vision of Comfort* (2): crowds see him as someone they trust.
- Earth:
  - *Fortify the Soul* (3): an ally takes no crit damage N times.
  - *Wandering Stone* (5): a teleport anchor anywhere, even across spirit realms.
- Fire:
  - *A Fire Divided* (3): HP transfer from a willing donor (can be himself).
  - *Invigorating Flame* (3): charges a weapon with fire "charges" for big hits.
- Water:
  - *Frozen Tomb* (4): freeze a foe; it breaks if the foe takes damage.
  - *Find the Source* (2): vision of who cast a known spell → **mystery tool** for Gendo's and Haruki's arcs.
- Void:
  - *Yumi of the Void* (1): a bow of nothingness, power = VP spent. **Gives Haruki the Yumi weapon type.**
  - *Saving Fortune* (4): bank lucky rolls → stored crits.

### Water — Rank 5 ultimates (post-game; user request 2026-11-05: a raise, a party heal, a party heal-over-time)
*Invented, in the spirit of the 3e list (3e has no resurrection; Path to Inner Peace and Regrow the Wound scaled up).*
| Spell (ML) | Skill | Target | SP | Boost |
|---|---|---|---|---|
| Mass Path to Inner Peace (5) | Heal HP: Path to Inner Peace on the whole party, with no VP needed | all allies | 30 | +heal |
| Rain of Regrowth (6) | Regrow the Wound on the whole party: heals every turn | all allies | 40 | +heal |
| Return the Soul (6) | **Revive** a fallen ally, healed to half their HP | 1 ally | 44 | — |

### Void — Rank 5 ward (post-game; user request 2026-11-05: Void as a protection against fear)
*Invented: the Void holds no fear. Courage of the Seven Thunders (Earth 2) is the single-ally version.*
| Spell (ML) | Skill | Target | VP cost | Effect of VP held |
|---|---|---|---|---|
| Stillness of the Void (4) | The whole party is **immune to Terror** for 4 turns: there is no fear in the Void | all allies | 2 | — |

## 4. Recommended curve (default auto-picks; the player can change them)
| Lv | Picks |
|---|---|
| 5 | Void Bolt, Jade Strike |
| 10 | Sympathetic Energies, Wind-Borne Slumbers |
| 15 | Katana of Fire, Force of Will |
| 20 | Reversal of Fortunes, Yari of Air |
| 25 (R2) | Altering the Course, The Fires from Within |
| 30 | Essence of Void, Regrow the Wound |
| 35 | **Kharmic Intent**, Courage of the Seven Thunders |
| 40 | Strength of the Crow, Curse of Stone |
| 45 (R3) | Armor of the Emperor, **Void Strike** |
| 50 | Light of Yakamo, **Void Release** |
| 55 (R4) | Follow the Flame, **Void Suppression** |
| 60 | Whirlwind, Near to Ice |
| 65 (R5) | Peace of the Kami, Kami's Strength |
- *Hand of Jurojin* is granted by the story in Ch3 (the Darkfever).
| 70 | Mass Path to Inner Peace, Stillness of the Void |
| 75 | Rain of Regrowth, Return the Soul |
| 70+ | Free choice; summons and ultimates |

## 5. Open points
1. ✅ **Water + Void Affinity, Ishiken-do from the start, Void spells paid in VP** (user, session 2).
2. The Ch4 cost ("permanent loss of some of his Void"), now that Void is his fuel → proposal: his **Void stat** −1
   (lower Void-spell power), but he gains the passive **"Whole"** (Mieko's half returned): Water heals also cleanse 1
   debuff, and *Drawing the Void* becomes usable twice per battle. The loss stings, but the reward is better.
   ✅ **Approved by the user** ("something a water shugenja might do").
3. ✅ The party heal (Path to Inner Peace at VP 3) is approved. Rejuvenating Vapors' SP restore is still a minor
   invented convenience.
4. Kokujin-cult enemies and **Togashi Akuro** use *Unattunement* (kiho.md) to seal Haruki's Attune element. Design
   the counterplay: Elemental Ward, Harmony skills.
5. ✅ Checked against the page images: Death of Flame (Agility + Intelligence); Way of Deception (−30% per
   offensive action, as written). Grasp of Earth's escape TN is still unchecked (minor).
