# Bestiary — Random-Encounter Monsters (mobs) — v0.1

Octopath model:
- **archetypes** with **tier variants** (I–IV; a new name and palette, stronger stats, one new skill per tier)
- **regional encounter tables** with a **danger level**

Bosses are in `bosses.md`; the stat formula is in `bosses.md` §0 (mob HPx = 1.0 unless noted).
- Weapons: Katana · Yari · Tanto · Tetsubo · Yumi · Bo
- Elements: Fire · Water · Air · Earth · Void · Jade
- Materials: Crystal · Obsidian

**Tiers ↔ chapter bands:**
- **I** = Ch1 areas (Lv 1–10)
- **II** = Ch2 (18–26)
- **III** = Ch3 (28–36)
- **IV** = Ch4 (40–48)
- **V** = finale/post-game (54+; Shinomen and the Shadowlands deep)

Columns: L · HPx · Res(olve) · Weak · Resist · Skills · Drop / Steal.
**Human foes** follow the Honor rules: many **surrender** at low HP (Cite the Law, Settle the Account, Honourable
Challenge). Sparing them gives Honor +; killing surrendered foes gives Honor −.

---

## A. HUMAN FOES

### A1. Bandits (*sanzoku*)
| Tier | Name | L | HPx | Res | Weak | Resist | Skills | Drop / Steal |
|---|---|---|---|---|---|---|---|---|
| I | Road Bandit | 2–6 | 1.0 | 2 | Katana, Yumi | — | *Shakedown* (steals 20 zeni) | Rice Ball / Zeni ×30 |
| II | Mountain Bandit | 18–24 | 1.0 | 3 | Katana, Yumi, Fire | — | *Ambush* (acts first on battle 1) | Herbal Salve / Bandit's Bandana |
| III | Bandit Captain | 28–34 | 1.6 | 5 | Katana, Air | — | *Rally* (allies ATK+) | Fine Sake / Captain's Purse |
| IV | Kolat-paid Brigand | 40–46 | 1.4 | 4 | Tanto, Yumi | Bo | *Poisoned Blade* | Antidote / Kolat Coin (lore) |
- All tiers **surrender** at 25% HP (Cite the Law / Settle the Account).

### A2. Ronin
| Tier | Name | L | HPx | Res | Weak | Resist | Skills | Drop / Steal |
|---|---|---|---|---|---|---|---|---|
| I | Hungry Ronin | 3–8 | 1.1 | 3 | Yari, Yumi | — | *Desperate Cut* (big hit, accuracy −) | Old Whetstone / Straw Hat |
| II | Sword-for-Hire | 19–25 | 1.2 | 4 | Yari, Air | Katana | *Wolf's Technique* (vs. its attacker: +damage) | Ronin's Inro / Chipped Tsuba |
| III | Wave-man Duelist | 29–35 | 1.3 | 5 | Tanto, Earth | Katana | *Iaijutsu Feint* | Duelist's Cord / Sake Gourd |
| IV | Masterless Champion | 41–47 | 1.6 | 6 | Yari, Bo | Katana | *Strike Like Wind* (2 hits) | Fine Katana Fragment / Ronin's Writ |
- They **can be hired** after the battle (Barter Coin: "a sword for coin"); spared ronin may appear as hired help.

### A3. Contentious Samurai (*proud duelists, drunks, honour-seekers*)
| Tier | Name | L | HPx | Res | Weak | Resist | Skills | Drop / Steal |
|---|---|---|---|---|---|---|---|---|
| I | Drunken Samurai | 4–9 | 1.2 | 3 | Bo, Water | — | *Sake Breath* (Confuse chance), *"Insult!"* (taunts a random ally) | Cheap Sake / Gaudy Fan |
| II | Glory-Hungry Bushi | 19–25 | 1.3 | 4 | Yari, Air | Katana | *Demand Satisfaction* (challenges one ally; others −acc vs. him) | Honor Token / Lacquered Inro |
| III | Clan Duellist (Crane/Lion/Scorpion palette per region) | 29–35 | 1.4 | 5 | by clan* | Katana | *Clan Kata* (as `kata.md`) | Clan Mon Charm / Fine Hilt-wrap |
| IV | Hatamoto's Champion | 41–47 | 1.6 | 6 | by clan* | Katana | *Kata + Iaijutsu opening* | Champion's Sageo / Glory Scroll |
- *By clan: Crane duellists are weak to Yari/Air; Lion to Tanto/Water; Scorpion to Yumi/Jade; Crab to Air/Tanto.
- **Honourable Challenge** (Shizue) or **Duel** turns the fight into a 1-on-1 and ends it on Suki. Glory + if won
  clean.
- **Never surrender** (pride), but at 25% they **yield** to a Duel or Charm attempt.

### A4. Ashigaru & Clan Patrols (hostile at war borders)
| Tier | Name | L | HPx | Res | Weak | Resist | Skills | Drop / Steal |
|---|---|---|---|---|---|---|---|---|
| I | Ashigaru Spearman | 3–7 | 1.0 | 3 | Katana, Tanto | Yari | *Spear Line* (hits front row) | Rice Ration / Straw Sandals |
| II | Border Patrol | 19–24 | 1.1 | 3 | Tanto, Yumi | Yari | *Call Reinforcement* | Patrol Writ / Ration Tin |
| III | Sergeant of Spears | 29–34 | 1.4 | 5 | Katana, Fire | Yari | *Form Ranks* (Def+ to all) | Lacquered Jingasa / Signal Horn |
| IV | Heavy Infantry (Crab/Lion) | 41–46 | 1.6 | 6 | Tetsubo, Bo | Katana, Tanto | heavy armour (tag) | Plate Scale / Armour Cord |
- **Bribery works** (Barter Coin). **Path writs** (story items) end the fight before it starts.

### A5. Pirates & Wako (Crane coast, Mantis isles)
| Tier | Name | L | HPx | Res | Weak | Resist | Skills | Drop / Steal |
|---|---|---|---|---|---|---|---|---|
| I | Dock Ruffian | 2–7 | 1.0 | 2 | Bo, Katana | — | *Kama Hook* (Speed −) | Fish Stew / Rope |
| II | Wako Raider | 20–25 | 1.1 | 3 | Katana, Yumi | Water | *Boarding Hook* | Sea Salt / Pirate Charm (fake) |
| III | Mantis Corsair | 30–35 | 1.3 | 4 | Air, Yari | Water | *Strike of the Cliff's Edge* (ranged kata) | Storm Kama / Pearl |
| IV | Storm Legion Renegade | 42–46 | 1.5 | 5 | Bo, Air | Water | *Typhoon Sweep* (AoE) | Storm Legion Token / Gaijin Coin |

### A6. Cultists & Maho-users
| Tier | Name | L | HPx | Res | Weak | Resist | Skills | Drop / Steal |
|---|---|---|---|---|---|---|---|---|
| I | Painted Cultist (Kokujin's) | 5–9 | 1.0 | 2 | Water, Bo | — | *Frenzy* (ATK+, Def−) | Ink Pot / False Tattoo Brush |
| II | Blood-Hungry Acolyte | 20–25 | 1.1 | 3 | Jade, Water | — | *Blood Bolt* (pays HP; Taint 1) | Jade Dust / Bloodstained Scroll |
| II | Stitched-face Monk (City of Masks) | 20–25 | 1.0 | 4 | Tanto, Fire | — | *Give Us Your Face* (Silence); **freed on Suki** (Honor +1, max +3 per chapter) | Old Paper / — |
| III | Maho-tsukai | 30–35 | 1.3 | 5 | Jade, Fire | Earth | *Summon Ghoul*, *Taint Touch* | Purity Charm / Maho Fetish (lore) |
| IV | Bloodspeaker Adept | 42–48 | 1.6 | 6 | Jade, Void | Fire | *Blood Shout* (damage transfers to an ally), *Command the Taint* | Bloodspeaker Sigil / Obsidian Shard (Taints the user) |

### A7. Ninja / Spies (Scorpion lands; any night map)
| Tier | Name | L | HPx | Res | Weak | Resist | Skills | Drop / Steal |
|---|---|---|---|---|---|---|---|---|
| II | Shadow-in-Black | 20–26 | 1.0 | 3 | Fire, Yumi | Air | *Metsubishi* (Blind) | Smoke Pellet / Ninja-to Shard |
| III | Kolat Agent | 30–35 | 1.1 | 4 | Jade, Bo | — | *Vanish* (untargetable 1 turn), *Poison Needle* | Poison Kit / Kolat Cipher |
| IV | Shosuro Renegade | 42–46 | 1.2 | 5 | Fire, Bo | Air, Tanto | *Many Faces* (copies a party skill once) | Actor's Mask / Shosuro Powder |

---

## B. BEASTS

### B1. Wolves
| Tier | Name | L | HPx | Res | Weak | Resist | Skills | Drop / Steal |
|---|---|---|---|---|---|---|---|---|
| I | Grey Wolf | 2–6 | 0.8 | 2 | Yari, Fire, Yumi | — | *Pack Bite* (+damage per wolf alive) | Wolf Pelt / — |
| II | Mountain Wolf | 18–24 | 0.9 | 3 | Yari, Fire | — | *Howl* (calls 1 wolf) | Thick Pelt / Wolf Fang |
| III | Winter Wolf | 28–34 | 1.0 | 3 | Fire, Yari | Water | *Frost Bite* (Speed −) | Winter Pelt / Silver Fang |
| IV | Bakemono Wolf-rider | 40–46 | 1.4 | 5 | Jade, Yari | — | goblin rider + wolf (two-part target) | Goblin Saddle / Tainted Fang |
| — | **Wolf-Spirit** (rare, forests at night) | 30+ | 1.5 | 6 | Fire, Void | physical half | *Moon Howl* (Terror 1) | Spirit Fur (Air accessory) / — |
- **Animal Handling / Signal Shot** can **scare the pack away** (the battle ends, no exp).

### B2. Snakes & Serpents
| Tier | Name | L | HPx | Res | Weak | Resist | Skills | Drop / Steal |
|---|---|---|---|---|---|---|---|---|
| I | Mamushi Viper | 2–7 | 0.6 | 2 | Tanto, Fire | — | *Venom Fang* (Poison) | Viper Skin / Venom Sac |
| II | Paddy Python | 18–24 | 1.2 | 3 | Katana, Fire | — | *Constrict* (binds 1 ally; Grapple) | Python Hide / — |
| III | Shadow-Snake (Order of the Snake summons; den maps) | 28–33 | 0.6 | 2 | Fire, Air | physical half | *Shadow Bite* (Poison) | Shadow Scale / — |
| IV | River Orochi-spawn | 40–46 | 1.8 | 6 | Air, Yari | Water | *Coil*, *Tidal Lash* (AoE) | Orochi Scale (Water accessory) / Spawn Pearl |
| V | Naga Scout (Shinomen; *not evil*: talk-down possible on Suki) | 54–58 | 1.6 | 6 | Air, Yari | Water | *Pearl Spear* | Naga Pearl / — |

### B3. Bears, Boars & Big Game
| Tier | Name | L | HPx | Res | Weak | Resist | Skills | Drop / Steal |
|---|---|---|---|---|---|---|---|---|
| I | Wild Boar | 3–8 | 1.2 | 3 | Yari, Yumi | — | *Charge* (front row) | Boar Meat / Tusk |
| II | Black Bear | 19–24 | 1.6 | 4 | Yari, Fire | — | *Maul*, *Roar* (Terror 1) | Bear Hide / Bear Gall (medicine) |
| III | Snow Bear | 29–34 | 1.8 | 5 | Fire, Yari | Water | *Crushing Hug* (binds) | Snow Hide / — |
| IV | Elder Boar (*kami-touched*) | 41–46 | 2.0 | 6 | Fire, Jade | Earth | *Earthshake Charge* (AoE + Knockdown) | Sacred Tusk (Earth accessory) / — |

### B4. Birds, Insects & Small Things
| Tier | Name | L | HPx | Res | Weak | Resist | Skills | Drop / Steal |
|---|---|---|---|---|---|---|---|---|
| I | Carrion Crow | 1–5 | 0.5 | 1 | Yumi, Air | — | *Peck Eyes* (Blind chance) | Crow Feather / — |
| I | Cave Beetle | 3–6 | 0.8 | 3 | Tetsubo, Fire | Tanto | carapace | Beetle Shell / — |
| II | Giant Hornet | 18–23 | 0.6 | 2 | Fire, Air | — | *Sting* (Poison), swarm ×3 | Hornet Honey (heal) / Stinger |
| II | Cave Bat Swarm | 19–23 | 0.5 | 1 | Yumi, Fire | — | *Screech* (Silence) | Bat Guano (Daigo's reagent) / — |
| III | Tsuchigumo (giant spider) | 29–35 | 1.4 | 5 | Fire, Jade | — | *Web* (Speed −−), *Poison Bite* | Spider Silk / Venom Gland |
| III | Tengu Crow-Warrior (canal/bridge maps) | 28–33 | 1.2 | 4 | Yumi, Air | — | *Feather Blade*, *Taunt* | Tengu Feather / — |
| IV | Kumo Brood (Shinomen) | 42–48 | 1.0 | 4 | Fire | Earth | swarm ×4, *Cocoon* | Kumo Silk (accessory: evasion) / — |

### B5. Sea & River Creatures
| Tier | Name | L | HPx | Res | Weak | Resist | Skills | Drop / Steal |
|---|---|---|---|---|---|---|---|---|
| I | Tide Crab | 2–7 | 1.0 | 3 | Tetsubo, Earth | Water | carapace, *Pinch* | Crab Meat / Shell |
| I | Blood Leech (River of Gold marsh) | 4–8 | 0.7 | 2 | Fire, Jade | — | *Drain* (heals itself; Taint chance) | — / Sea Salt (salt makes it let go) |
| II | Kappa (river imp; *bow to it and it bows back, spilling its water: instant Suki*) | 19–24 | 1.1 | 4 | Fire, Etiquette* | Water | *Drag Under* (Grapple) | Cucumber (heal) / Kappa Plate |
| III | Sea Serpent Eel | 30–35 | 1.3 | 4 | Air, Yari | Water | *Electric Coil* (Paralyze) | Eel (heal) / — |
| IV | Umibozu Shade (storm seas) | 42–46 | 2.0 | 6 | Fire, Void | Water, physical half | *Wave Wall* (party Speed −) | Ghost Lantern / — |
- *Kappa: the **Bow** command (Etiquette) makes it bow back, spill the water from its head-dish, and fall into Suki.

---

## C. SHADOWLANDS & TAINTED
(Crab lands beyond the Wall; Shinomen deep; any Taint map. **Taint tiles** apply.)
| Tier | Name | L | HPx | Res | Weak | Resist | Skills | Drop / Steal |
|---|---|---|---|---|---|---|---|---|
| I | Goblin (*bakemono*) | 1–7 | 0.8 | 2 | Yari, Jade, Fire | — | *Scavenge* | Goblin Knife / Shiny Trinket |
| II | Goblin Warmonger | 18–25 | 1.0 | 3 | Jade, Yari | — | *Frenzy* | Rusty Blade / Jade Dust |
| III | Ogre (*bog hag palette in marsh maps*) | 29–35 | 2.0 | 6 | Jade, Tetsubo | Tanto | *Club Smash* (Knockdown) | Ogre Tooth / — |
| III | Zombie | 28–33 | 1.3 | 3 | Jade, Fire, Bo | Terror, Poison | *Grab* (Grapple); rises once unless Fire/Jade finishes it | Grave Dirt / — |
| III | Onikage (demon horse) | 30–35 | 1.5 | 5 | Jade, Yari, Fire | — | *Trample*, high Speed | Onikage Hoof / — |
| IV | Troll | 40–46 | 2.4 | 7 | Tetsubo, Fire | — | *Regenerate* (10%/turn unless burned) | Troll Hide / — |
| IV | Moto Akutsukai (winged undead rider) | 42–48 | 1.8 | 6 | Jade, Fire, Bo | Terror | *Dive*, *Death Cry* (Terror 2) | Bone Wing / Tainted Spur |
| IV | Maho-bujin | 41–46 | 1.4 | 4 | Yari, Katana, Jade | — | *Taint Strike* | Tainted Armour Scale / — |
| V | Oni Spawn (*lesser oni*) | 54–60 | 2.2 | 8 | Jade, element by colour | Terror | *Oni Rage*, *Fear Aura* (Terror 2) | Oni Horn (Fire accessory) / Oni Blood |
| V | Lava Tree Dryad | 55–60 | 1.8 | 6 | Water, Jade | Fire | *Ember Rain* (AoE) | Lava Seed / — |
| V | Toothed Poppy (field) | 54–58 | 0.6 | 2 | Fire, Air | — | swarm ×5, *Bite*, *Pollen* (Sleep) | Poppy Seed (Sleep item) / — |
- **Jade weakness everywhere.** Crystal reveals invisible ones. Obsidian works but Taints the user.

## D. SPIRITS & THE DEAD
| Tier | Name | L | HPx | Res | Weak | Resist | Skills | Drop / Steal |
|---|---|---|---|---|---|---|---|---|
| I | Will-o'-wisp (*hitodama*) | 3–8 | 0.5 | 1 | Water, Bo | physical half | *Lure* (Confuse) | Spirit Flame (Fire item) / — |
| II | Yurei (restless ghost) | 19–25 | 1.1 | 3 | Water, Void, Crystal | physical half | *Grief Wail* (Terror 1) | Ghost Lock of Hair / — |
| II | Fear Shade (Ianwa's spawn; Shiro Akodo) | 19–24 | 0.8 | 3 | Jade, Fire | physical half | *Dread Touch* (Terror 1) | Ghost Lock of Hair / — |
| II | Gaki (hungry ghost) | 20–25 | 1.2 | 4 | Water, Jade, Crystal | physical half | *Devour* (steals SP) | Rice Offering / — |
| III | Fever Spirit (Phoenix Darkfever) | 30–35 | 0.9 | 3 | Water, Jade | physical half | *Darkfever Breath* (Poison) | Fever Ash / — |
| III | Ghost-Guard (White Snow) | 30–35 | 1.0 | 4 | Fire, Katana | physical half | rises again near a basin | Frozen Badge / — |
| III | Paper-spirit (*tsukumogami*, archives) | 30–44 | 0.6 | 2 | Fire, Tanto | — | *Paper Cut* (bleed) | Old Paper / — |
| IV | Ink-pot Spirit (*tsukumogami*, archives) | 41–45 | 0.9 | 3 | Fire, Bo | Water | *Ink Splash* (Blind) | Old Paper / Ink Pot |
| IV | Lantern Spirit (*chochin-obake*) | 41–45 | 0.8 | 3 | Water, Yumi | Fire | *Lick* (Confuse), *Flare* | Spirit Flame / — |
| III | Singing Servant (possessed by Regret; Shiro Iuchi) | 30–35 | 0.9 | 3 | Water, Bo | Terror | *Hum* (Silence unless ears are covered); **breaking it wakes it** (non-lethal; Honor +1, max +3) | — / Wax Plug (sell) |
| IV | Frost Spirit | 32–36 | 1.0 | 3 | Fire, Jade | Water | *Ice Mist* (Speed −) | Frost Shard / — |
| IV | Kansen Wisp (corrupted kami) | 42–48 | 1.2 | 5 | Crystal, Air | physical half | *Corrupt* (Taint 1), invisible | Kansen Mist / — |
| IV | Fire Elemental (Tamori's Furnace) | 42–46 | 1.4 | 4 | Water, Bo | Fire | *Flare* (AoE Fire) | Ember Core / — |
- **Bless** (Haruki) can **lay a ghost to rest** mid-battle (a yurei/gaki leaves; half exp, Honor +).

## E. THE PAST (year 400, Dragon Ch2–4)
| Tier | Name | L | HPx | Res | Weak | Resist | Skills | Drop / Steal |
|---|---|---|---|---|---|---|---|---|
| II | Palace Guard (tachi-armed) | 20–25 | 1.1 | 3 | Bo, Yari | Katana | *Straight Cut* | Antique Tsuba / — |
| III | Gaijin Musketeer | 30–36 | 1.0 | 4 | Yari, Bo | — | *Volley* (ranged); **using a dropped musket: History −15** | Musket Ball (no use: anachronism) / — |
| III | Gaijin Pikeman | 30–35 | 1.2 | 4 | Tanto, Air | Yari | *Pike Wall* | Gaijin Coin / — |
| IV | Gusai Mantis Marine | 41–46 | 1.3 | 5 | Air, Katana | Water | *Boarding Rush* | Gusai Sash / — |

---

## F. REGIONAL ENCOUNTER TABLES (danger level = recommended Lv)
| Region / map type | Danger | Common (×) | Uncommon | Rare / night only |
|---|---|---|---|---|
| **Kaiu Wall & Crab coast** | 1–8 | Goblin I, Tide Crab I, Carrion Crow | Road Bandit I | Will-o'-wisp |
| **Hoshi-no-Ichi caves** | 3–8 | Cave Beetle, Mamushi Viper | goblins | — |
| **Shadowlands (Ch3)** | 28–35 | Goblin Warmonger, Zombie, Onikage | Ogre | Toothed Poppy (V-palette, weaker) |
| **Kyuden Hida environs** | 18–25 | Mountain Bandit, Drunken Samurai II-palette | Border Patrol | Yurei |
| **Kyuden Hida donjon & trap catacombs** | 20–25 | Goblin Warmonger, Cave Bat Swarm | Yurei | — |
| **Crane coast & Beiden forest** | 2–8 | Road Bandit I, Grey Wolf, Wild Boar | Hungry Ronin | Will-o'-wisp |
| **Crab–Crane border** (land-bridge, border camps) | 20–25 | Border Patrol, Tide Crab II-palette, Glory-Hungry Bushi | Sword-for-Hire | Yurei (night) |
| **Crane sea & isles** | 20–35 | Wako Raider, Tide Crab, Sea Serpent Eel | Mantis Corsair | Umibozu Shade (storm) |
| **Kyuden Doji archives** | 40–46 | Paper-spirit, Ink-pot Spirit | Lantern Spirit | — |
| **Mantis isles (present)** | 1–8 | Dock Ruffian, Tide Crab, Carrion Crow | Hungry Ronin | — |
| **Tortoise Island & cove** | 20–25 | Kappa, Wako Raider, Cave Bat Swarm | Tide Crab II-palette | — |
| **Dragon mountains** | 40–48 | Winter Wolf, Snow Bear, Mountain Bandit IV-palette | Tengu Crow-Warrior | Wolf-Spirit |
| **Tamori's Furnace** | 42–46 | Fire Elemental, ash-ghoul | — | — |
| **Year 400 capital & coast** | 20–45 | Palace Guard, Gaijin Musketeer, Gaijin Pikeman | Gusai Marine | — |
| **Lion plains & border** | 1–8 | Ashigaru Spearman, Grey Wolf, Road Bandit | Drunken Samurai I | — |
| **Shiro Akodo roads (winter)** | 18–25 | Mountain Wolf, Glory-Hungry Bushi, Border Patrol | Black Bear | Yurei |
| **Shiro Akodo under-dojo** | 20–25 | Fear Shade, Cave Bat Swarm | — | — |
| **Lion west road (spring, Ch3)** | 28–35 | Bandit Captain, Sword-for-Hire, Mountain Wolf III-palette | Glory-Hungry Bushi III-palette | — |
| **Lion mountains (Kaze-no-Tani)** | 28–35 | Winter Wolf, Bandit Captain, Sword-for-Hire | Snow Bear | — |
| **Sorrow's Path** | 40–46 | Heavy Infantry, Hatamoto's Champion, Sergeant of Spears | — | — |
| **Phoenix roads & Kamatori** | 1–8 | Will-o'-wisp, Grey Wolf, Road Bandit | — | — |
| **Snowbound pass (Phoenix)** | 18–25 | Painted Cultist II-palette, Mountain Wolf | Black Bear | Yurei |
| **Isawa Mori (Darkfever)** | 28–35 | Fever Spirit, Tsuchigumo, Gaki | Blood-Hungry Acolyte | — |
| **Phoenix sea-cliffs** | 40–46 | Frost Spirit, Wako Raider IV-palette | Kansen Wisp | — |
| **Scorpion south & Kudo** | 1–8 | Road Bandit, Mamushi Viper, Carrion Crow | Hungry Ronin | Will-o'-wisp |
| **River of Gold west bank (marsh)** | 4–8 | blood-leech, Goblin I | Mamushi Viper | — |
| **Plains north of Shiro no Soshi** | 18–25 | Shadow-in-Black, Paddy Python, Giant Hornet | Glory-Hungry Bushi | Yurei |
| **City of Masks: Temple District** | 22–25 | Stitched-face Monk, Kansen Wisp II-palette | Paper-spirit | — |
| **Ojatara Valleys** | 1–35 (by chapter) | Mountain Bandit, Border Patrol, Grey/Mountain Wolf | Blood-Hungry Acolyte (Ch3) | Gaki (the mine) |
| **Shiro Iuchi tower (Ch3, ears covered)** | 30–35 | Singing Servant | — | — |
| **Shiro Iuchi wind tunnel** | 40–46 | possessed Legion, Moto Akutsukai (palette) | — | — |
| **Cakon & the eta roads** | 1–8 | Dock Ruffian, Wild Boar, Carrion Crow | Hungry Ronin | Tengu (bridge) |
| **Floating Flowers & river** | 18–25 | Wako Raider, Paddy Python, Kappa | Glory-Hungry Bushi | Shadow-Snake (den) |
| **Mountain of the White Snow** | 28–35 | Snow Bear, Winter Wolf, Frost Spirit | Ghost-Guard | Wolf-Spirit |
| **Oracle's volcano town** | 40–46 | Kolat Agent, Shosuro Renegade, Fire Elemental | — | — |
| **Thunder plain road (pre-finale level bridge)** | 50–56 | Goblin V-palette, Ogre V, Onikage IV+ | Moto Akutsukai | Oni Spawn |
| **Plains of Thunder (finale)** | 54–58 | Goblin V-palette, Ogre V, Oni Spawn | Moto Akutsukai | — |
| **Shinomen Mori (finale)** | 55–60 | Kumo Brood, Naga Scout, Lava Tree Dryad, Toothed Poppy | Oni Spawn | Wolf-Spirit |
| **Post-game: Shadowlands deep / Hiruma Castle** | 61–80 | all IV/V archetypes with a "Fallen" palette (+30% stats) | Troll Elder | Orochi-spawn (V) |

## G. Notes
- **Octopath pacing:** 3–4 archetypes per area plus 1 rare. Encounter-rate passives (Trailblazing, Walk Without
  Passing, sneak-walk) apply (`skills.md`).
- **Non-violent exits:**
  - wolves and bears: scare off
  - humans: surrender, bribe, or a writ
  - ghosts: Bless
  - Naga: talk-down
  - kappa: Bow
  These make the Honor and path-action systems matter outside story fights.
- Every **drop/steal** listed here goes into `equipment.md` (next).
