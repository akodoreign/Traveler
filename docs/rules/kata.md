# Rules — Kata (L5R 3e → Octopath) — DRAFT v0.1

Source: *L5R 3e Core Book Revised*, Book of Fire, pp. 204–216 (OCR `_research/books_txt/L5R - 3E - Core Book
Revised.ocr.clean.txt`, lines ≈ 21370–22530). Effects are **paraphrased for design** — never copy book text into the
game. Numbers marked ⚠ have OCR damage; check the page image before balancing.

Rank thresholds (DESIGN §4c): **R1 Lv 1 · R2 Lv 21 · R3 Lv 41 · R4 Lv 51 · R5 Lv 61.** Kata are taken with the
**every-5-levels pick** (Lv 5, 10, 15 … 95), so the level numbers below are the *earliest* pick that can take them.

---

## 1. How 3e kata work (summary)
- **Preparation:** 10–60 minutes of practice. Only **one kata prepared at a time**; it stays prepared while active.
- **Activation:** free, on your turn right after you declare your posture. It can be switched off and on for the
  rest of its duration (1–3 hours, or 24 h if prepared for twice as long).
- **Requirement:** a bushi school Rank (e.g. "Hida 1, Hiruma 2"), or a plain Insight Rank for common and shared
  kata, which counts your highest bushi school. **Clan rule:** your highest bushi school *of that clan* counts as
  one Rank lower for another school of the same clan. Example: Hiruma 5 counts as Hida 4.
- **Cost:** 2–9 XP. Many kata also have a **ring gate** (e.g. Earth 3).
- **Melee only** unless the kata says otherwise. A thrown weapon never benefits.
- **Void clause:** extra Void Points spent **once, when preparation finishes**, empower the kata for its whole
  duration.
- Most kata are **trade-offs**, not pure buffs: +attack for −initiative, +defence for −damage, and so on.

## 2. Octopath translation — the "Kata Stance" system

| 3e concept | Octopath / RPG-Cobo implementation |
|---|---|
| Learn kata (XP) | Pick at an every-5-levels slot, **or** a story reward from a sensei NPC or guest. |
| Prepare (1 at a time) | Each traveler has **1 Kata slot**, set from the menu at an **inn, camp or save shrine** — not mid-dungeon. This is the cost of preparation time. |
| Activate (free, after posture) | **Free toggle at the start of the traveler's turn**; it doesn't use the turn. On/off as often as wanted. Lasts the whole battle; duration in minutes is ignored. |
| Void clause | On the **first activation each battle**, the player may pay the listed **VP** ("Void Points" = Boost Points) to empower the kata until the battle ends. |
| Melee-only | The kata is **suppressed while a Yumi is equipped or used**, except Mantis kata, which allow ranged weapons. |
| Weapon specials | katana / daishō → **Katana** (the wakizashi is assumed) · naginata → **Yari** · two-handed or heavy weapon → **Tetsubo** (and Yari for Moto's Burning Strike) · unarmed / one-handed → **Tanto**, **Bo** or no weapon. |
| Armor specials | Armour gets a **Light / Heavy tag**. Octopath has no armour weights, but RPG-Cobo item data can carry a custom tag. Heavy armour gives +Def, −Speed and −Evasion. |
| Ring gates (Earth 3 …) | A **level gate** set where that traveler's ring-weighted stat curve reaches 3 (worked out when the stat curves exist). |
| Striking as Void | Gives **2 extra Kata slots** (3 active at once). A late capstone for anyone who learns all four common Strikings. |

**Postures** (several kata refer to them): *Full Attack* = a **Boosted** attack command that turn; *Full Defense* =
the **Defend** command; *Attack / Defense* = an ordinary turn.

**Conversion table** (used for every kata below, so the numbers stay consistent):

| 3e effect | Octopath effect |
|---|---|
| TN to Be Hit ±5 | physical Evasion ±10% |
| ±2 rolled attack dice | Accuracy ±10% and Crit ±5% |
| ±2 rolled damage dice | damage ±20% |
| ±1 kept die (damage) | damage ±25% |
| Initiative ±5 | Speed ±10% (turn order) |
| Free Raise | +10% potency on that action (stackable) |
| Wound penalties | the **Shaken** status (−Accuracy/−Evasion per stack). Reaching "Down" = KO. |
| Honor Rank | the party **Honor tier** (1–5), the town-reputation meter (schools.md, Shizue R2) |
| Fear effect | the **Terror** status (may skip a turn) |
| Exploding dice | Crit rate up (explode on 9s → a larger crit-rate bonus) |
| Extra attack per round | +1 hit at no VP cost |
| Insight Rank | the traveler's current **Rank (R1–R5)** |

---

## 3. Per-traveler kata lists

Secondary-school ranks (schools.md):
- **Gendo:** Mirumoto rank = his Rank − 1, from Lv 21. So M1 at R2, M2 at R3, M3 at R4, M4 at R5.
- **Natsuko:** Hida secondary rank = her Rank − 1. Because of the clan rule, Hiruma already counts as Hida − 1, so
  the secondary school adds **no new Crab kata**. It adds the tetsubo and heavy-armour kit.

### Hiruma Natsuko — evasion tank (Yari, Yumi; Tetsubo via Hida at R2)
| Pick | Kata (req.) | Octopath effect |
|---|---|---|
| Lv 5 | **Striking as Earth** (IR1, Earth 3) | Evasion +10%, Accuracy −10%. The basic "draw fire" stance. |
| Lv 15 | **Striking as Wind** (IR1, Air 3) | Speed +10%, damage −20%. Can be switched on in turn 1 before turn order is set, but then it can't be switched off until turn 2. |
| Lv 25 | **Shell of Stone** (Hiruma 2 · heavy armour) | **Armour mode:** doubles her armour's Def bonus *or* her Defend's damage reduction. She can't Boost attacks; Accuracy −10%. An alternative to the evasion build once the Hida kit unlocks. |
| Lv 41 | **Stance of the Wall** (Hiruma 3) | Evasion +10%, Speed −20%. Back and side attacks on her are impossible. **Wall counter:** when an enemy targets the ally next to her in the formation, she gets a free strike at +10% (3e: free Raise against foes moving past). **VP 1:** Evasion +10% more; **VP 1:** the counter gets +10% more. |
| Lv 51 | **Shards of Earth** (Hiruma 4) | Her next hit **ignores Def buffs and armour** (pierce). If the target hasn't acted yet this battle, it must pass an Earth contest or **lose its next turn**. The kata ends after one hit; **VP 2** makes it last one more hit. Her armour-breaker vs. carapaced Shadowlands bosses. |
| Lv 61 | **Unyielding Fury** (Hida 4 ⇐ Hiruma 5) ⚠ | When she takes damage, she may spend 1 VP to **counterattack** her attacker (max 1 per round). If the hit would KO her: no VP cost and **double damage**. Only one attack action per turn while active. |
| (opt.) | Striking as Fire / Water → **Striking as Void** (IR2) | 3 kata slots at once — a late-game build target. |
- *Hida's Avalanche* (Hida 5) is out of her reach. Keep it for Hida NPCs: a Wall sergeant guest, or a rival boss.

### Kakita Rensei — first-strike duelist (Katana, Tanto)
| Pick | Kata (req.) | Octopath effect |
|---|---|---|
| Lv 5 | **Kakita's First Stance** (Kakita 1 · katana) | Can be activated when a **duel starts** (Duel path action and duel bosses). He uses the **Honor tier in place of one stat** for the whole duel; Focus pool −1. **VP 2:** Honor +1 in the duel. |
| Lv 10 | **The Empire Rests on Its Edge** (IR1 · katana) | When learned, pick a High Skill (default **Etiquette**). While active: physical attack + (skill rank × k), but path actions using that skill (**Charm**) are halved. *Sword mode vs. court mode* — his arc in one switch. |
| Lv 25 | **Watchful Falcon** (Kakita 2) | Field: spot hidden items and treasure, and no back attacks or ambushes. Battle: +10% Accuracy vs. evasive foes. Charm/social success −. **VP 2:** a second +10%. |
| Lv 30 | **Victory of the Wind** (IR2 · katana) | **Execute stance:** +10% damage per HP quarter the target has lost (max = his Rank), but base damage −25%. |
| Lv 41 | **One Leg Stance** (Kakita 3 · katana *or* yari, learned per weapon) ⚠ | Speed +20% (a large turn-order jump). **VP 2:** Evasion becomes Reflexes-scaled (×3 ≈ +30%). |
| Lv 45 | **The World Is Empty** (IR3 · katana) | **All-in:** on activation, + attack and damage per VP held, this turn and the next. Then **all VP are lost**, damage −25%, and no VP regen for the rest of the battle. |
| Lv 51 | **One Strike Blade** (Kakita 4) | Give up one hit of a multi-hit attack to gain either **Speed +30% for the rest of the battle** or **+30% on his next hit** this turn. Can't Defend while active. **VP 1:** +10% more. |
| Lv 61 | **One Truth** (Kakita 5) | One attack action per turn; damage −20%. **Non-boss foes whose Honor doesn't exceed the party Honor tier can't target him** until he attacks them; dishonourable enemies with Honor 0 (Shadowlands, maho) ignore this. Hitting a slower foe: Reflexes contest → it **loses one of its actions** that round (works on multi-action bosses). **VP 2:** Honor +1. |
| Lv 70 | **Standing on the Heavens** (IR5 · katana) | When an attack would hit him, spend 1 VP to **force a re-roll** (a strong dodge). If his VP reaches 0: Evasion −20% and no crits for the rest of the battle. |

### Kitsuki Gendo — investigator + Mirumoto two-sword breaker (Katana, Bo)
*No kata before Lv 21: a courtier school isn't a bushi school. His early picks are skill masteries.*
| Pick | Kata (req.) | Octopath effect |
|---|---|---|
| Lv 25 | **Thunder and Steel** (Mirumoto 1 · katana · **pair kata**) | Needs a **shugenja ally in the active party** (Haruki or a shugenja guest). Both add Earth to Def and Fire to Atk (the shugenja may add it to spells instead). Both act at the **slower** of their two speeds. **VP 2:** bonuses doubled. "Bond kata." |
| Lv 30 | **The Empire Rests on Its Edge** (IR1 · katana) | He picks **Investigation**: attack + rank, but the **Discern** path action is halved while active. *The mind or the blade.* |
| Lv 41 | **My Brother's Soul** (Mirumoto 2 · katana) | His hits **ignore one magical defence** on the target (Aura of Flame, Armor of the Emperor …; the buff stays, his hits bypass it), *or* he gets +damage vs. spellcasters (chosen on activation). Speed −10%. His answer to maho-tsukai. *(Checked against the page image, p. 210.)* |
| Lv 51 | **Time Between Breaths** (Mirumoto 3 · katana) | While **Defending**, after he is attacked he may spend 1 VP to **counter** at +25% damage. Defend ends, but his turn still comes as normal. |
| Lv 61 | **Breaking Waves** (Mirumoto 4 · katana or unarmed) | When an enemy uses an **empowered or charged attack** on him, Agility contest → the enemy loses the empowerment, and Gendo stores that many +10% stacks for his next attack (max = his Rank). He can't Boost above 1 VP himself. |
| Lv 70 | **Victory of the River** (IR4 · katana) | Each hit marks the target: −20% evasion vs. his attacks until the end of next turn (stacks). His own Evasion −20%; can't Defend. |
- *Endless Strike* (Mirumoto 5) is out of his reach → the signature kata of **Mirumoto Hikaru** (the ageless
  tattooed Dragon in Sayo's arc, secretly the legendary Mirumoto Kichi). He could teach Gendo a *taste* of it as a
  post-game reward.

### Akodo Shizue — Honor-scaling commander (Katana, Yari)
| Pick | Kata (req.) | Octopath effect |
|---|---|---|
| Lv 5 | **Striking as Water** (IR1, Water 3) | Damage +20%, Evasion −10%. Akodo add Water to damage, so it fits her. |
| Lv 15 | **Striking as Fire** (IR1, Fire 3) | Accuracy +10% and Crit +5%; Speed −10%. |
| Lv 41 | **Fury Without End** (Akodo 3) | Immune to Shaken, Terror and other "distraction" debuffs for the whole battle. **Price:** after the battle she is left at **1 HP with no VP regen until she rests at an inn or camp**. |
| Lv 45 | **The Soul's Roar** (Matsu 2 ⇐ Akodo 3) | Attack and damage + (Honor tier × k); Evasion −10%. **VP 1:** twice the Honor bonus, Evasion −20%. Works with her R2 *Strength of Purity*: an honourable party makes her very strong. |
| Lv 51 | **Gentle Blade of Winter** (Akodo 4 · katana) | Every ~10% of the target's max HP she deals adds one stack of **Shaken** (lasts 2 × Rank turns). **VP 2:** two stacks per trigger. |
| Lv 55 | **Tsuko's Storm** (Akodo 4) | While she Boosted last turn, enemy bonuses against her (their crit and Boost bonus) are reduced. Switching it off mid-battle costs 1 VP. **VP 2:** reduced further. (Low priority; may cut.) |
| Lv 61 | **Matsu's Vengeance** (Akodo 5) | Speed, attack and damage + (2 × Honor tier); **Evasion −40%**. Crits on "9s" (big crit-rate bonus). Damage gets a floor of Honor + 1. **VP 1:** Honor +1. Glass-cannon capstone. |

### Shosuro Mitsue — infiltrator and debuffer (Tanto, Yumi)
*Scorpion kata list both "Shosuro Ninja" and "Shosuro Shinobi" (the OCR shows both spellings); treat them as the
same school.*
| Pick | Kata (req.) | Octopath effect |
|---|---|---|
| Lv 5 | **Striking as Wind** (IR1, Air 3) | Speed +10%, damage −20%. |
| Lv 25 | **The Tail's Reach** (Shosuro 2) | +20% damage vs. enemies **slower than her / that haven't acted yet**; Evasion −10%. **VP 1:** the penalty drops to −4%. Works with her R2 *No Mercy*. |
| Lv 41 | **Cut Under the Mountain** (Shosuro 3 · tanto/one-handed · light armour) | +20% Evasion vs. **heavy-armoured or two-handed** enemies, +40% vs. enemies with both (tag them in the enemy data). Attacking such foes: Speed +10% and +10%. |
| Lv 45 | **Sundering Grace** (Bayushi 2 ⇐ Shosuro 3) | Each hit: Reflexes contest → stacking **Accuracy −10%** on the target for Rank + 1 turns; her damage −25%. **VP 2:** −20% per stack. |
| Lv 51 | **Blackened Sight** (Shosuro 4) | Enemies **can't crit** her, and their attacks on her lose damage scaled by her Air. Lost on any turn she Boosts an attack or Defends: she has to keep moving. |
| Lv 61 | **Choking Air** (Bayushi 4 ⇐ Shosuro 5 · light armour) | +20% Evasion vs. enemies slower than her, +10% more vs. enemies under 50% HP; damage −20%. Lets her stand in as a second evasion tank. |

### Sayo — ronin, "the wave-woman's elements" (Katana, Yumi)
*Ronin schools are bushi schools, but clan kata are clan secrets. Sayo's niche is the **complete common set**: she is
the only traveler with all five by R2, and so the first to run 3 kata at once.*
| Pick | Kata | Octopath effect |
|---|---|---|
| Lv 5 | **Striking as Water** | Damage +20%, Evasion −10%. |
| Lv 10 | **Striking as Earth** | Evasion +10%, Accuracy −10%. |
| Lv 15 | **Striking as Fire** | Accuracy +10% / Crit +5%, Speed −10%. |
| Lv 20 | **Striking as Wind** | Speed +10%, damage −20%. |
| Lv 25 | **Striking as Void** (IR2) | **3 kata slots.** She mixes the four elements (e.g. Earth + Fire cancel out each other's accuracy penalty). |
- Story option: a guest sensei teaches her one shared IR kata as a quest reward, e.g. *Victory of the Wind* from a
  ronin swordmaster in Ronin Ch2. That would be her only "borrowed" form.

### Isawa Haruki — no kata; partner in pair kata
- Haruki is the **shugenja half** of *Thunder and Steel* (with Gendo, or a Mirumoto guest) and of **Eyes of the
  Phoenix** (with a Shiba guest, below).
- His every-5 picks are **spells** (spell index; ML tiers by Rank).

### Ide Tamotsu — no kata
- He is a courtier; his every-5 picks are courtier battle skills and Ide techniques. An optional Shinjo secondary
  school (*Shinjo's Breath*) was considered and **not recommended**: it blurs his pacifist-diplomat identity.

---

## 4. Kata reserved for guests and enemies
| Kata | Holder | Notes |
|---|---|---|
| Hida's Avalanche | Hida NPC (Wall sergeant guest / Crab rival boss) | Stacking damage vs. one target, falling evasion; carries over on a kill. |
| Endless Strike | **Mirumoto Hikaru** (ageless Dragon, Ronin Ch3) | Up to 3 extra hits at reduced damage (checked on the page image). |
| Eyes of the Phoenix | **Shiba Toshiro / Shiba Ashimita** + Haruki | Pair kata: the Shiba acts just after Haruki; Haruki may spend 1 VP to give the Shiba +30% Evasion vs. one attack; Haruki's buffs on him can't fail; the Shiba adds Haruki's Void to attack. Lovely Phoenix-arc beat. |
| Tail of the Sun · Touching the Infinite · Deeper Reflection · Heaven's Wing | Shiba guests (Yari = naginata) | Heaven's Wing: dump all VP for that many extra attacks, then forced Defend. Deeper Reflection: +2 VP for the battle. |
| Watchful Falcon, One Leg Stance (yari) | **Daidoji Sakura**, Doji Chiyo | Crane guests. |
| The Soul's Roar, Tsuko's Storm | **Matsu Kiku** (guest) | |
| Sundering Grace, Choking Air | **Bayushi Hideki** (guest) | |
| Mantis kata (Boundless Fury, Howl of the Son of Storms, Prayer's End, Strength of Waves, Strike of the Cliff's Edge) | Mantis pirates and bosses (Crane Ch3 "The White Squid"; Crane–Mantis piracy) | The only kata that also work with **ranged** weapons → pirate archers. |
| Unicorn kata (Shinjo's Breath, Thundering the Sky, Howl of the Moto, Moto's Burning Strike, Otaku's Void) | **Moto Benjiro** (guest, Howl of the Moto / Burning Strike); Iuchi Karasu; Unicorn enemies | Otaku's Void = shift dice between attack/damage/evasion → the "rebalance" command. |

## 5. Open points
1. **Weapon coverage:** kata use Katana heavily. Tetsubo appears only through Natsuko's Hida kit and Hida NPCs.
   Revisit with the weapon review (02-travelers.md).
2. **Ring-gate levels** wait for the ring-weighted stat curves.
3. ✅ Checked against the page images (book pp. 207–210):
   - Hida's Avalanche cost = **9**.
   - Unyielding Fury: 1 Void → a free attack on the attacker; free and doubled when the hit would bring her to Down.
   - One Leg Stance: the book itself prints the errata ("+10 Initiative").
   - Endless Strike: as summarised.
   - My Brother's Soul **corrected**: it ignores a magical defence; it doesn't dispel.
4. Should a kata's VP be refunded if the kata is switched off in the same turn? Proposal: no.
5. **Balance:** 4–7 kata per bushi traveler use about a third of their 19 every-5 picks; the rest go to skill
   masteries, battle skills and spells.
