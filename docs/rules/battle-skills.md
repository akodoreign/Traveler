# Rules — Battle Skills (maneuvers + signatures) — DRAFT v0.1

The every-5-level picks (DESIGN §4c) choose among:
- **kata** (`kata.md`)
- **spells** (`haruki-spells.md`)
- **battle skills** (this file)

Battle skills are **gated by skill rank** (`skills.md`), not level. So "Spears 3" means the skill shows up in the
pick list once Spears reaches 3, and a player's skill choices shape which picks they get.

## 1. Universal maneuvers (3e "Raises in combat", core OCR ≈ lines 18032–18118)
Every bushi can pick these. In 3e a maneuver costs Raises (raising your own TN), so in Octopath each costs **SP and
some accuracy**, and gains from Boost.

| Maneuver (3e Raises) | Skill | Gate | SP | Effect | Boost |
|---|---|---|---|---|---|
| **Feint** (1) | Feint | any weapon 2 | 4 | No damage; **your next attack within 2 turns gets +20% damage and +10% crit** (3e: 2 Free Raises per Raise) | +20% per VP |
| **Increased Damage** (1+) | Heavy Blow | any weapon 2 | 6 | One hit at +40%, Accuracy −10% | +40% per VP |
| **Guard** (1+) | Guard | Defense 2 | 4 | Cover one ally: **enemies get −20% accuracy** against them, 1 turn | −10% more per VP |
| **Called Shot** (1/2/3: torso/limb/head) | Called Shot | any weapon 3 | 8 | Choose: **Arm** (ATK −), **Leg** (Speed −; it acts later), **Head** (stun chance; Accuracy −20%) | longer / likelier |
| **Disarm** (3) | Disarm | any weapon 3 | 10 | No damage; ignores armour; contest → the enemy's **weapon attacks are disabled for 2 turns**. Not on beasts. Melee only. | +1 turn |
| **Knockdown** (3) | Knockdown | any weapon 4 | 10 | Hit + contest → the enemy **loses its next action** (prone). Unarmed version: Throw. | +contest odds |
| **Extra Attack** (4) | Twin Strike | any weapon 5 | 12 | Two hits on one target, **both miss if the second misses** (3e rule). Two weapons: adjacent targets. | +1 hit per 2 VP |
| **Grapple** (0+) | Grapple | Jiujutsu 3 | 8 | Pin: neither side acts until a contest is won. Sumai flavour; Natsuko/Hiro. | +contest dice |

## 2. Signature battle skills per traveler (designed from their schools and skills)
### Natsuko — Hiruma scout / evasion tank
| Skill | Gate | Effect |
|---|---|---|
| **Draw Their Eyes** | Defense 2 | Taunt: enemies target her for 2 turns; works with *Razor's Edge* evasion |
| **Ambush Strike** | Stealth 3 | Huge damage **if the battle began with a pre-emptive strike**, or vs. an enemy that hasn't acted yet |
| **Yari Sweep** | Spears 3 | Hits all front-row enemies; Knockdown chance vs. small foes |
| **Piercing Shot / Signal Shot** | Kyujutsu 2 / 4 | Arrow variants (`weapons.md`) |
| **Know the Foe** | Lore: Shadowlands 3 | Analyze a Shadowlands enemy and give the party +damage vs. it for 3 turns |
| **Tetsubo Crush** | Heavy Weapons 3 (Hida kit) | Armour-breaking smash; strips Def buffs |
| **Wall-Watcher's Rest** | Hunting 3 | Field: wild camp = inn rest (Survival) |

### Rensei — Kakita duelist
| Skill | Gate | Effect |
|---|---|---|
| *Iaijutsu (Talent)* | — | Focus → Strike |
| **Cutting Courtesy** | Etiquette 3 | A polite barb (Sadane-style): an intelligent enemy loses ATK and targets Rensei |
| **Feint → First Cut** | Kenjutsu 3 | A Feint whose follow-up, if it's an Iaijutsu Strike, auto-crits |
| **Thrown Tanto** | Knives 2 | Ranged Tanto hit; interrupts casting (charge spells delayed) |
| **Head Strike** | Kenjutsu 5 | A Called Shot (head) with no accuracy penalty, if Rensei is first in turn order |
| **Tea of Stillness** | Tea Ceremony 3 | Field/camp: party +VP at the next battle's start |

### Gendo — Kitsuki magistrate + Mirumoto
| Skill | Gate | Effect |
|---|---|---|
| *Deduce (Talent)* | — | Reveal weaknesses |
| **Interrogate** | Investigation 3 | Vs. human foes: reveal 1 weakness **and** Shaken (they fear being seen through) |
| **Cite the Law** | Lore: Law 3 | Vs. criminals and bandits: Terror chance; **non-boss bandits may surrender** (battle ends, Honor +) |
| **Subdue** | Staves 3 | Nonlethal Bo strike: a KO'd human foe is **arrested** (bonus drops / quest flags) |
| **Niten Flurry** | Kenjutsu 3 (Mirumoto) | Two Katana hits at 70% each (two swords) |
| **Underworld Contact** | Underworld 3 | Field: informants (no Honor loss: a Bugei skill for the Kitsuki) |

### Shizue — Akodo tactician
| Skill | Gate | Effect |
|---|---|---|
| *Command (Talent)* | — | Turn manipulation |
| **Battle Cry** | Battle 2 | Party ATK +15% for 3 turns |
| **Lion's Charge** | Spears 3 | Yari charge: +50% damage on turn 1 (3e: the Yari's charge bonus) |
| **Akodo Formation** | Battle 4 | Party Def +20% and immune to back attacks, 3 turns |
| **Read the Field** | Battle 3 | Reveal all enemies' next actions this turn; party Speed +10% |
| **Honourable Challenge** | Iaijutsu 3 | Single out an enemy captain: only it can act against her, she gets +30% vs. it. Honor + if she wins. |
| **Storyteller's Courage** | Storytelling 3 | Cure Terror on the party and raise morale (+VP to one ally) |

### Mitsue — Shosuro infiltrator
| Skill | Gate | Effect |
|---|---|---|
| *Many Faces (Talent)* | — | Steal / copy |
| **Poisoned Edge** | Poison 2 (picked up as a character skill) | Tanto hit + **poison** |
| **Metsubishi** | Ninja Ranged Weapons 3 | Blinding powder: all front-row enemies get Accuracy −30% |
| **Shuriken Fan** | Ninja Ranged Weapons 2 | Multi-hit ranged, low damage |
| **Misdirection** | Deceit 3 | Enemies forget her; the next single-target attack meant for her hits another enemy (if confused) or misses |
| **Vanish** | Stealth 5 | Untargetable 1 turn; her next attack counts as "unaware" (works with *No Mercy*) |
| **Mask Change** | Acting 5 | Mid-battle disguise: human enemies lose their target lock; field: disguise gates |

### Tamotsu — Ide emissary (support, money)
| Skill | Gate | Effect |
|---|---|---|
| *Barter Coin (Talent)* | — | Money skills |
| **Words of Peace** | Etiquette 3 | Intelligent enemy ATK and E.Atk −20% |
| **Appraising Eye** | Commerce 3 | Analyze + better item drop rate this battle |
| **Settle the Account** | Commerce 5 | Spend money: a non-boss human enemy **leaves the battle** (paid off). Honor is unaffected if it's a fair trade. |
| **Song of the Ki-Rin** | Storytelling 3 | Party regen (small HP each turn), 3 turns (Unicorn tales) |
| **Horse-Archer's Shot** | Kyujutsu 3 (Yomanri) | A Yumi shot that ignores the back-row penalty; Speed + |
| **Gaijin Cure** | Lore: Gaijin 3 | Cure poison and disease with Burning Sands remedies |
| **Gaijin Spyglass** | Investigation 3 | Reveal **all** enemies' weaknesses (one icon each). From the Fortune's Lost item idea "gaijin telescope". |
| **Share the Stores** | Commerce 3 | Use one consumable item on **all allies** at once |
| **Hired Blade** | Commerce 4 | Spend money: a mercenary guest strikes each turn for 3 turns (price scales with level) |
| **Cavalry Charge** | Horsemanship 3 | His horse joins for one pass: a Yari hit on all front-row enemies and party Speed +10% (outdoor maps only) |
| **Reasoned Truce** | Courtier 5 | Once per battle: all human non-boss enemies lose ATK −30%, and each has a chance to **stop fighting**. Ties into his finale virtue, Compassion. |

### Sayo — wave-woman herbalist
| Skill | Gate | Effect |
|---|---|---|
| *Remedy (Talent)* | — | Concoctions (Medicine tiers) |
| **Field Dressing** | Medicine 2 | Heal one ally. Medicine 3: can treat the same ally twice per battle. |
| **Antidote** | Medicine 3 (Antidotes) | Cure poison; Poison 3 makes it cleanse all debuffs |
| **Bitter Root** | Poison 3 | Enemy E.Def −; poison chance |
| **Snare** | Hunting 3 | Set a trap: the next enemy that attacks takes damage and is rooted |
| **Pilfer (in battle)** | Sleight of Hand 3 | Steal an item; **Low Skill:** Honor penalty if the battle happens in a town |
| **Wolf's Bite** | (Ronin Warrior R1) | Counter stance vs. whoever targets her (kata-like) |

## 3. Pick-budget check (19 picks, Lv 5–95)
- **Bushi:** ~5–7 kata + ~6–8 battle skills + 3–5 universal maneuvers ≈ 19.
- **Haruki:** spells (2 per pick).
- **Tamotsu:** no kata. He has 12 signature skills (talent + 11) plus maneuvers, which fills his 19 picks.
- **Gendo:** before R2 his picks go to Interrogate, Cite the Law, Subdue and the maneuvers.
