# Rules — Battle & Boss Sheets (all `b_*` ids) — v0.1

Covers every battle id in `story/production/` and `story/sidestories/`. Numbers are **first-pass**, to be tuned in
the engine prototype.
- Weapons: **Katana · Yari · Tanto · Tetsubo · Yumi · Bo**
- Elements: **Fire · Water · Air · Earth · Void · Jade**
- Materials: **Crystal · Obsidian** (item-only; obsidian Taints its user)
- Rules: `rules/enemies.md` (Suki, statuses, boss rules)

## 0. Stat formula (enemy level L)
| Stat | Regular foe | Notes |
|---|---|---|
| HP | (60 + 26·L) × **HPx** | bosses have HPx 6–16; mid-bosses 4–6 |
| P.Atk / E.Atk | 10 + 4·L | ±20% by role |
| P.Def / E.Def | 8 + 3.5·L | armoured foes +30% P.Def; spirits +40% P.Def (physical halved) |
| Speed | 20 + 2·L | |
| Resolve | 2–6 regular · 6–8 mid-boss · 8–14 chapter boss · 16–28 finale | Suki = loses its next action, +50% damage taken |
| VP-like charge | bosses with "gathering" moves telegraph 1 turn ahead | counters: When the Veil Moves, Breaking Waves, Void Strike, Essence of Void |
- **Drops:** each sheet lists a guaranteed drop. Steal (Many Faces / Pilfer) gives a rarer item.
- **Weakness discovery:** see `enemies.md` §1.
- Format of a boss sheet: L · HPx · Resolve · Weak · Resist · Skills · **Gimmick** · Phases · Drop / Steal.

---

## 1. CRAB (Natsuko)
| id | L | Foes | Resolve | Weak | Notes |
|---|---|---|---|---|---|
| b_goblin_raid | 1 | goblin ×4, "Goblin in a Hat" | 2 / 3 | Yari, Jade, Fire | tutorial; scripted prompts |
| b_cave_nezumi_a/b | 4–5 | nezumi warrior ×3 | 2 | Yari, Fire, Bo | Rumble meter active |
| b_cave_beetles | 4 | cave beetle ×3 | 3 | Tetsubo, Fire | carapace (Tanto weak) |
| b_donjon_goblins | 21 | goblin experiment ×3 | 3 | Yari, Jade | |
| b_duel_noboru | 22 | Shiba Noboru | 5 | Yari, Air | Duel (non-lethal); route only |
| b_sl_goblins | 31 | warmonger goblin ×4 | 3 | Jade, Yari | Taint tiles |
| b_sl_onikage | 32 | onikage ×2 | 5 | Jade, Yari, Fire | demon horses; high Speed |
| b_sl_akutsukai | 34 | Moto akutsukai ×2 | 6 | Jade, Fire, Bo | hard; only on a failed hide |
| b_siege_breach_a | 42 | Bakemono wolf-rider ×2, goblin warmonger ×2 | 5 / 3 | Jade, Yari | Crab Ch4 outer yard; two-part targets (storyboard) |
| b_siege_breach_b | 43 | maho-bujin ×2, ogre | 4 / 6 | Jade, Tetsubo | Crab Ch4 cellar stair; protect the courtiers (the ogre targets them first) |
**b_boss_grasping_paw** (Crab Ch1) — L 7 · HPx 7 · Resolve 6
- Foes: **Nezumi Shaman** + nezumi ×2.
- Weak: Yari, Fire, Bo.
- Skills: *Name-Magic* (Silence 2 turns), *Pack Call* (summons 1 nezumi).
- **Gimmick: the Rumble meter** (shared with the cave). Area skills and Boosted multi-hits fill it; when full, a
  cave-in hits everyone and stuns the shaman.
- Variant **b_boss_grasping_paw_ryozo**: + Seppun Ryozo (L 7, HPx 3; *Egg Rite* heals an ally 20%).
- Guest: Squeak (*Pocket Sand*).
- Drop: Nezumi Bone Charm (+item find). Steal: Painted Egg (cure Silence).

**b_boss_puppet_troll** (Crab Ch2) — L 24 · HPx 8 · Resolve 8
- Foes: **Maho Puppet** + **Troll** (a hazard; untargetable until the puppet breaks).
- Puppet — Weak: Jade, Fire, Yari. Skills: *No Pure Breaths* (Silence + damage), *Veil Lash*.
- **Gimmick:** each turn the troll smashes the highest-threat ally (Natsuko's taunt draws it). Breaking the puppet
  makes the troll attack the puppet.
- Drop: Filed Chain Link (key: shows Crab Ch3 lore). Steal: Torn Veil (accessory: +evasion vs. women — a joke item).

**b_boss_kommei** (Crab Ch3) — L 35 · HPx 10 · Resolve 12
- Foes: **Oni no Kommei** + maho-bujin ×2 (Resolve 4; weak Yari, Katana).
- Weak: Jade, Tetsubo, Fire. Resist: Water.
- Skills: *Two-Faced Strike*, *Command the Taint* (Taint +1 to all).
- **Gimmick: Body-swap.** Every 3rd turn it swaps two travelers' command menus for 2 turns. Its **back face** is a
  separate target (Resolve 4); breaking it ends the swaps.
- Optional guest: Kage (*Berserk Smash*; takes double damage).
- Drop: Kommei Mask (accessory: immune to command-swap). Steal: Oni Ichor (Fire damage item).

**b_boss_tsukakoro** (Crab Ch4) — L 45 · HPx 11 · Resolve 14
- Foes: **Oni no Tsukakoro** (a bouncing bone-cage).
- Weak: Tetsubo, Jade, Earth. Resist: Air, Tanto.
- Skills: *Bounce Chain* (hits 2–4 targets in a row; Razor's Edge redirects to Natsuko), *Rattle* (Terror 2).
- If `flare_fired`: +1 turn of Crab archer volleys (fixed damage each turn).
- Drop: Bone-cage Fragment (Tetsubo upgrade material). Steal: none.

---

## 2. CRANE (Rensei)
| id | L | Foes | Resolve | Weak | Notes |
|---|---|---|---|---|---|
| b_bokken_bout | 1 | senior student | 3 | Tanto, Air | tutorial (Iaijutsu) |
| b_forest_bandits_a/b | 5–6 | bandit ×3 | 2 | Katana, Yumi | surrender at low HP; `forest_village_spared` |
| b_camp_sentries_a/b | 22 | seduced sentry ×3 | 3 | Katana, Bo | freed on Suki |
| b_storm_yosuke | 33 | Yosuke the Bold + pirates ×2 | 7 / 3 | Katana, Water | fake charms (gimmick preview) |
| b_archive_spirits | 42 | paper-spirit ×4 | 2 | Fire, Tanto | |
| b_archive_guardian | 43 | shelf kami | 6 | Fire, Void | mid-boss |
**b_boss_yasurugi** (Crane Ch1) — L 8 · HPx 7 · Resolve 8
- Foes: **Kakita Yasurugi**.
- Weak: Yari, Tanto, Air. Resist: Katana (he counters katana users).
- Phase 1: **duel UI** (Assessment → Focus → Strike). He Strikes first if the player over-Focuses.
- Phase 2: skirmish. Skills: *Kakita's First Stance* (Honor-scaled), *Way of the Crane* (acts first).
- Guests: Kiku (*Battle-Joy*), Seigen (*Evidence*).
- Drop: none (story). Steal: Yasurugi's Spare Hilt-wrap (+crit).

**b_boss_iron_cranes** (Crane Ch2) — L 25 · HPx 4 each (×3, ×4 with Natsuko) · Resolve 6 each
- Foes: **bewitched Daidoji generals**.
- Weak: Yari, Tanto, Water (cold water wakes them).
- **Gimmick: Charmed generals.** Damage feeds Miyako's hold (she heals them 10% per turn). **Suki frees a general**
  (it leaves the battle).
- Win when all are freed or defeated (defeated gives a worse epilogue line).
- Drop: Daidoji War Fan (accessory). Steal: Miyako's Love-token (key, finale lore).

**b_midboss_chihaya** (Crane Ch3) — L 31 · HPx 5 · Resolve 7
- Foes: **Chihaya the Quick**.
- Weak: Yumi, Air. Immune: Knockdown.
- **Fake charm** (+evasion): steal it or break it with Suki.
- Drop: Tadanobu's Letters (key). Steal: Pirate Charm (fake, still works: +evasion).

**b_boss_katsuo** (Crane Ch3) — L 35 · HPx 10 · Resolve 12
- Foes: **Katsuo the White Brother** (+ **Ryohei** L 34, HPx 5, Resolve 8, weak Katana/Bo, if not released).
- Katsuo — Weak: Jade, Katana, Fire. Maho: pays 5% HP per cast; Taint on hit.
- **Gimmick: fake charms.** Each turn he hands a charm (+ATK / +evasion / regen) to one enemy. Steal it, or break
  it with Suki (the wearer is stunned for 1 turn).
- Drop: White Squid Pearl (Water accessory). Steal: Blood-ink Brush (E.Atk +).

**b_boss_masanori** (Crane Ch4) — L 45 · HPx 12 · Resolve 14
- Foes: **Kakita Masanori** (formal duel, first blood).
- Weak: Yari, Tanto, Air. Resist: Katana.
- Phase 1: **duel UI** (he has +1 Focus; *One Strike Blade* → he acts first).
- Phase 2: kata (*Kakita's First Stance* uses Honor; *Watchful Falcon* gives +accuracy).
- **Win:** Suki once **and** land a crit. On a loss the story continues (the copy route).
- Drop: none (story: Father's Hilt-wrap is given afterwards). Steal: none.

---

## 3. DRAGON (Gendo)
| id | L | Foes | Resolve | Weak | Notes |
|---|---|---|---|---|---|
| b_dock_tutorial | 1 | drunk sailor | 2 | Bo, Katana | Deduce tutorial |
| b_gusai_thugs_a/b | 5–6 | kama thug ×3 | 3 | Bo, Katana | surrender to Cite the Law |
| b_cove_crabs | 21 | tide crab ×3 | 3 | Tetsubo, Earth | carapace |
| b_cove_guards | 22 | hypnotised guard ×3 | 3 | Bo, Air | Interrogate stops them |
| b_izumida_musketeers | 32 | gaijin musketeer ×3 | 4 | Yari, Bo | ranged; muskets lower History if used |
| b_front_land | 42 | gaijin pikemen waves | 4 | Yari, Fire | defend 6 turns |
| b_front_mantis | 42 | Mantis champion | 6 | Yari, Air | or talk via Discern |
| b_front_lighthouse | 43 | raiders ×4 | 3 | Fire, Yumi | escort Isawa Sanro (History −30% if he falls) |
| b_harbour_musketeers | 43 | musketeer ×4 | 4 | Yari, Bo | barrels lower History |
**b_boss_tide** (Dragon Ch1) — L 8 · HPx 6 (team) · Resolve 5 / 3
- Foes: **hypnotised ronin shugenja ×2** + Mantis thugs ×2.
- Shugenja — Weak: Air, Bo. Thugs — Weak: Katana, Yari.
- **Gimmick: the tide.** Every 3 turns the front row becomes **Waist-deep** (Speed and Evasion −20%), then
  **Drowning** (damage per turn).
- Interrogate / Know the Mind makes a shugenja stop fighting.
- Drop: Tortoise Ferry Token (key). Steal: Mantis Sake (heal).

**b_boss_ushimo** (Dragon Ch2) — L 24 · HPx 8 · Resolve 10
- Foes: **Seppun Ushimo**.
- Weak: Bo, Yari, Water.
- Phase 1: duel UI (Gendo's *Daisho Technique* lets him use Kenjutsu).
- Phase 2: skirmish.
- **Gimmick: don't kill.** Below 25% a killing blow is refused ("History shudders": History −10, he stays at
  1 HP). Win with **Suki below 25%** or a non-lethal skill (Subdue, Knockdown).
- Drop: Ushimo's Gratitude (story; a key NPC). Steal: none.

**b_boss_parley** (Dragon Ch3) — L 35 · HPx 6 (captain) · Resolve 12
- Foes: **gaijin vanguard captain** + gaijin ×2 + **Togashi Akuro** (untouchable).
- Captain — Weak: Katana, Water, Air.
- **Akuro:** can't be damaged (Crab tattoo); takes extra actions (Wasp). Win when the captain falls; Akuro then
  leaves.
- Gunpowder barrels on the deck: History −10 per use.
- Drop: *Shukujo* (story: Seikidera's sword, which won't ring for Gendo). Steal: Gaijin Spyglass (accessory).

**b_boss_kumpei_flagship** (Dragon Ch4) — L 45 · HPx 12 · Resolve 14
- Foes: **Kakita Kumpei** + flagship cannons (a timer hazard).
- Weak: Katana, Water, Air.
- Skills: *Living Ink Sigil* (copies 1 party buff per turn), *Brushstroke Blade*.
- Cannons fire every 2 turns (every 4 if the land front was won).
- **The vial:** break him before turn 8, or he throws it (a cutscene; no reward).
- Buffs from won fronts: artillery (fewer cannons), Mantis ships (an enemy loses 1 action per turn), ward (party
  E.Def +).
- Drop: Living Ink Pot (Void accessory). Steal: Kami-ichor Drop (one-time full VP).

---

## 4. LION (Shizue)
| id | L | Foes | Resolve | Weak | Notes |
|---|---|---|---|---|---|
| b_warehouse_raid | 1 | Phoenix guard ×3 | 2 | Katana, Yari | Command tutorial |
| b_duel_ashimita | 6 | Shiba Ashimita | 5 | Yari, Air | Duel; win or lose honourably |
| b_bracket_1/2/3 | 20–22 | Ikoma bard / Matsu / Kaiu Yutaka | 3/4/6 | varies | Duel bracket |
| b_fear_shades | 22 | fear-shade ×3 | 3 | Jade, Fire | Terror tutorial |
| b_bridge_bandit | 30 | bandit chief | 5 | Katana, Yari | Duel |
| b_pass_ronin | 32 | ronin ×3 | 4 | Yari, Yumi | surrender (Cite the Law) |
| b_shogen_test | 34 | Akodo Shogen | 8 | Air, Tanto | Duel (route A); uses *Fury Without End* |
| b_gusai_duel | 42 | Akodo Gusai | 6 | Yari, Air | Duel (non-lethal) |
| b_ford_waves_1–5 | 42–44 | Matsu berserkers / Crane riders / archers / burning bridge / terror wave | 3–5 | per wave | defence set-piece; Knockdown/Subdue earn Honor |
**b_nagai_possessed** (Lion Ch1, mid-boss) — L 6 · HPx 4 · Resolve 6
- Weak: Jade (Hojiki's real stone as an item), Water.
- Skill: *Ancestral Rage*.
- Drop: Matsu Sensei's Bokken.

**b_boss_otamai** (Lion Ch1 / Phoenix Ch1, shared) — L 9 · HPx 8 · Resolve 8
- Foes: **O-Tamai** (in a borrowed body) + **red-shadow oni**.
- Weak: Jade, Fire, Katana.
- Oni: **soul damage** (drains SP/VP instead of HP).
- **Gimmick: the jade chains.** Each Suki on O-Tamai unlocks the *Jade Chain* command; **3 chains = victory**.
- Map: the spirit-wasteland debuff ends on victory.
- Drop: Jade Chain Fragment (Jade-element weapon mod). Steal: Bloodspeaker's Ring (key lore).

**b_boss_ianwa** (Lion Ch2) — L 25 · HPx 7 · Resolve 10
- Foes: **Oni no Ianwa** (+ Kafu as a guest if `kafu_joins`).
- Weak: Jade, Fire.
- **No attacks of its own.** **Gimmick: Charm.** Each turn it charms 1 ally into attacking another (jade gear
  lowers the chance; *Death Trance* blocks it 1 round).
- **Coward rule:** at the first Suki, it flees (victory).
- Drop: Kafu's Love Letters (story). Steal: Coward's Tooth (accessory: +escape).

**b_boss_miya_killers** (Lion Ch3) — L 35 · HPx 8 / 3 · Resolve 10 / 4
- Foes: **Seppun-trained duelist** + archers ×2.
- Duelist — Weak: Yari, Tanto, Earth. Archers — Weak: Katana, Air.
- No gimmick (the chapter's set-piece is the message).
- Drop: Miya Letters (key). Steal: Duelist's Inro (heal ×3).

**b_boss_rokuro_demon** (Lion Ch4) — L 45 · HPx 12 · Resolve 16
- Foes: **Matsu Rokuro, ridden by a Fear-demon**.
- Weak: Jade, Yari, Water, **Obsidian** (big Suki damage; Taint +1 to the user per hit).
- Skills: *Terror Aura* (Terror 2–3 to all, every turn), *Matsu's Fury*.
- Breaking the possession frees Rokuro alive.
- Drop: Rokuro's Gratitude (story). Steal: Demon's Shadow (Terror-immunity accessory, Taint-cursed).

---

## 5. PHOENIX (Haruki)
| id | L | Foes | Resolve | Weak | Notes |
|---|---|---|---|---|---|
| b_shrine_guardian_shards | 5 | guardian-stone ×3 | 3 | Water, Bo | Void/VP and mass-heal tutorial |
| b_pass_cultists | 22 | Kokujin cultist ×4 | 3 | Water, Bo, Air | they surrender if Hioninmaru flees |
| b_forest_fever_spirits | 32 | fever spirit ×3 | 3 | Water, Jade | Darkfever (poison aura) |
| b_mieko_shadows_a/b | 42–43 | shadow fragment ×3 | 4 | Water, Void | they copy Haruki's spells |
**b_ashimoshi** (Phoenix Ch1, mid-boss) — L 7 · HPx 5 · Resolve 6
- Weak: Water, Void; physical damage halved (spirit).
- **Silent Wind:** every other turn, spells are sealed.
- Drop: Hurricane Bead (Air accessory).

**b_boss_hioninmaru** (Phoenix Ch2) — L 25 · HPx 7 · Resolve 10
- Foes: **Hioninmaru** + Kokujin cultists ×3.
- Weak: Jade, Water, Void.
- Maho: pays HP per cast; Taint on hit.
- **Coward:** if all cultists fall, he loses 1 Resolve per turn.
- Drop: "The Consumer" scroll (if not already kept). Steal: Bloodspeaker Tattoo-ink (Fire item).

**b_mieko_dark_mid** (Phoenix Ch3, mid-boss) — L 33 · HPx 5 · Resolve 9
- Weak: Water, Void. She flees at 50%.
- `showed_scroll` gives the party 1 free turn.
- Drop: none.

**b_boss_oni_no_kuzushi** (Phoenix Ch3) — L 35 · HPx 11 · Resolve 14 (+1 if `stayed_extra_day`)
- Foes: **Oni no Kuzushi**.
- Weak: Jade, Water, Bo.
- **Gimmick: Unbalancing Breath.** Every 2 turns one traveler becomes **Off-Balance** (loses their next turn), and
  the oni regains 2 Resolve. Counters: *The Mountain's Feet*, Defend, a guest, turn-order tricks.
- Darkfever aura: Poison to all each turn (Water heals cleanse it).
- Drop: Cracked Seal Shard (Earth accessory). Steal: Fever-black Pearl (poison item).

**b_boss_mieko_dark** (Phoenix Ch4) — L 45 · HPx 12 · Resolve 16 (−2 per `dream_keys`)
- Foes: **Mieko (dark half)**, Void element.
- Weak: Water, Bo, Void (*Void Strike* steals her charge).
- Skills: Void spells that **cost her VP**; *Void Drain* (steals 1 VP from a traveler).
- At 0 HP the fight ends and the **choice** follows (a fake choice → Join).
- Drop: none (story: "Whole"). Steal: none.

---

## 6. SCORPION (Mitsue)
| id | L | Foes | Resolve | Weak | Notes |
|---|---|---|---|---|---|
| b_road_bandits | 2 | bandit ×3 | 2 | Tanto, Yumi | Steal tutorial |
| b_marsh_leeches | 6 | blood-leech ×4 | 2 | Fire, Jade | Taint tiles |
| b_stitched_monks_a/b | 22–23 | stitched-face monk ×3 | 4 | Tanto, Fire | freed on Suki |
| b_furnace_elementals | 42 | fire elemental ×3 | 4 | Water, Bo | |
| b_ash_ghouls | 43 | ash-ghoul ×3 | 4 | Jade, Water | |
**b_kommei_brood** (Scorpion Ch1, mid-boss) — L 5 · HPx 4 · Resolve 6
- Weak: Jade, Fire.
- Demonstrates the command-swap once (foreshadowing Crab Ch3).
- Drop: Fox Charm (+E.Def).

**b_boss_kansen_hana** (Scorpion Ch1) — L 8 · HPx 7 · Resolve 8
- Foes: **Kitsune Hana, possessed by a Greater Kansen**.
- Weak: Air, Water; **Crystal** (full damage). Physical damage halved.
- **Gimmick: the ritual counter (10 turns) + disarm.** Suki → she **drops the Iron Box**, and the counter stops.
  **Steal** takes the Box. Past turn 7: the Oracle of Blood half-forms (a drowning grapple; jade bypasses its
  carapace). At turn 10 it rises fully: *Blood Tide* (heavy party damage each turn) until Hana is broken.
- Crystal source for Ch1 parties: Crystal Shard ×4 in the west marsh (the Miya caravan relics; storyboard).
- Drop: Iron Box (cursed key item). Steal: Kansen Mist (Air item).

**b_boss_munashii** (Scorpion Ch2) — L 25 · HPx 9 · Resolve 12
- Foes: **Abbot Munashii**.
- **Crystal does full damage; everything else half.** Weak: Katana, Fire, Air.
- Phase 2: the true mask, which **copies party buffs** (*Mask of Many*).
- If `mitsue_wore_giseiki`: Giseiki's counter-word gives a free Suki once.
- Drop: Munashii's Mask (accessory: copy 1 enemy buff). Steal: Crystal Rosary (crystal item ×2).

**b_boss_iuchi_hit_squad** (Unicorn Ch2 = Scorpion Ch3) — L 28 · HPx 4 each / 6 · Resolve 5 / 7
- Foes: **Iuchi shugenja ×3** + **amulet-bearer**.
- Shugenja — Weak: Yari, Yumi, Air. Amulet-bearer — Weak: Tanto, Katana.
- **Gimmick: the silence bubble.** Every other turn spells are sealed (warned a turn ahead). Breaking the
  amulet-bearer ends it.
- Drop: Meishodo Amulet (Silence-immune accessory). Steal: Wax Earplugs (key, if not yet held).

**b_boss_stolen_face** (Scorpion Ch4) — L 45 · HPx 12 · Resolve 14
- Foes: **Bloodspeaker remnant**.
- Weak: Jade, Katana, Air.
- **Gimmick: Stolen Face.** At 66% and 33% it takes a party member's face, copies their last skill, and its
  weaknesses become that traveler's weapon types.
- Maho: Taint on hit.
- The Iron Box's curse is active (−1 VP) one last time.
- Drop: none (story). Steal: Bloodspeaker's Mirror (accessory: reflect 1 debuff).

---

## 7. UNICORN (Tamotsu)
| id | L | Foes | Resolve | Weak | Notes |
|---|---|---|---|---|---|
| b_camp_thugs | 2 | thug ×3 | 2 | Yumi, Yari | Barter Coin tutorial |
| b_cave_guerrillas | 6 | peasant guerrilla ×4 | 2 | Yari, Water | surrender; powder-keg preview |
| b_tower_servants | 31 | possessed servant ×3 | 3 | Bo, Jade | Covered Ears; Suki wakes them |
| b_mine_dead_a/b | 33 | risen dead ×4 | 3 | Jade, Fire, Bo | Terror-immune; raw jade usable as an item |
| b_tunnel_legion | 42 | possessed Legion ×4 | 4 | Jade, Yari | Covered Ears; no voice skills |
**b_boss_naohida** (Unicorn Ch1) — L 8 · HPx 7 · Resolve 7
- Foes: **Naohida** + guerrillas ×2.
- Weak: Yari, Yumi, Water.
- **Gimmick: powder kegs.** Any Fire hit detonates one (a big AoE on both sides).
- Barter Coin can buy off the guerrillas. At low HP he escapes (victory).
- Drop: Gaijin Dao Shard (story). Steal: Powder Bomb (Fire item ×2).

**b_boss_mine_guardian** (Unicorn Ch3) — L 35 · HPx 10 · Resolve 12
- Foes: **mine guardian** (ancient Iuchi armour) + risen dead ×2.
- Weak: Jade (raw jade item: free use), Fire, Yari.
- Drop: Jade weapons (one per party member). Steal: Guardian's Lantern (Fire accessory).

**b_boss_kurosho_regret** (Unicorn Ch4) — L 45 · HPx 14 (Doji) / 6 (Kurosho) · Resolve 18 / 10
- Foes: **Shuten Doji of Regret** + **Iuchi Kurosho** (possessed).
- Doji — Weak: Jade, Water, Void. Kurosho — Weak: Air, Bo.
- **Gimmick: the Wail.** Every 3 turns, travelers **without Covered Ears** must resist possession (2 turns).
  Covered Ears blocks voice skills.
- **Nihime's curse:** once at 50%, Kurosho's Resolve → 0 (a free Suki).
- `shahai_kept_close`: Karasu's fork + Shahai's reversed song stun the Doji for 1 turn.
- Drop: Regret's Silence (Silence/possession-immune accessory). Steal: none.

---

## 8. RONIN (Sayo)
| id | L | Foes | Resolve | Weak | Notes |
|---|---|---|---|---|---|
| b_dock_thugs | 1 | thug ×2 | 2 | Katana, Yumi | Remedy tutorial |
| b_alley_ambush | 4 | Tetsuo + disguised Lion | 3 / 4 | Katana, Yumi | |
| b_bakemono | 6 | bakemono ×6 | 2 | Katana, Fire, Jade | Pilfer the loot baskets |
| b_retainers_road | 20 | retainer ×3 | 3 | Katana, Yumi | they flee at half |
| b_storm_jetties | 22 | retainer ×4 + captain | 3 / 5 | Katana, Yumi | |
| b_snow_beasts | 31 | snow beast ×2 | 4 | Fire, Yumi | |
| b_frost_spirits | 32 | frost spirit ×3 | 3 | Fire, Jade | |
| b_lion_checkpoint | 30 | Border Patrol ×3 (Lion palette) | 3 | Tanto, Yumi | skipped with `writ_pilfered`; bribable (Barter Coin) |
| b_well_agents | 42 | Scorpion agent ×3 | 4 | Yumi, Katana | |
| b_race_assassins_1–5 | 42–44 | assassin ×2–3 | 4 | Yumi, Air | no full heal between (set-piece) |
**b_tengu_bridge** (Ronin Ch1, mini-boss) — L 5 · HPx 4 each (×2) · Resolve 5
- Weak: Yumi, Air.
- **Knock-off:** heavy hits and Knockdowns put a fighter "in the canal" for 2 turns.
- *Compliment* (Etiquette) makes one lose a turn.
- Drop: Tengu Feather (+Speed).

**b_boss_tomie_cho** (Ronin Ch1) — L 8 · HPx 8 · Resolve 9 (form 3)
- Forms:
  1. **old woman** (cover = high evasion; **Fire flushes her out**)
  2. **hybrid** (claw combos; Terror roar)
  3. **tiger** (fast)
- Weak: Fire, Yari, Yumi.
- Hiro's *No-dachi Sweep*: ×2 damage.
- Drop: Tiger's Fang (Katana mod: +crit). Steal: Old Woman's Tea (full heal, 1).

**b_boss_snake_enforcers** (Ronin Ch2) — L 25 · HPx 3 each (×2; built and tested, was 4) · Resolve 7
- Foes: snake enforcers + **shadow-snake** summons (Resolve 2; weak Fire, Air; Poison bites; every 2 turns).
- Enforcers — Weak: Katana, Fire, Jade.
- **The battle ends** when the first enforcer is broken, or would fall (Jinnai intervenes).
- Drop: Snake Ring (key lore). Steal: Shadow-snake Fang (poison item).

**b_boss_ghost_guard_basin** (Ronin Ch3) — L 35 · HPx 4 each (×3) + basin · Resolve 5 / basin 10
- Foes: **rebel ghost-guard ×3** + **the bloodstone basin**. (Built: the third guard is the **Shade of the Crab Lord** - boss art, Res 6, also weak to Jade - and the guards' physical halving spares the katana.)
- Guards — Weak: Fire, Katana (physical halved). Basin — Weak: Jade, Water, Bo.
- **Gimmick:** every 2 turns a fallen guard rises again; break the basin to end it.
- Guest: Mirumoto Hikaru (*Endless Strike*).
- Drop: Bloodstone Shard (Void accessory). Steal: none.

**b_boss_naga_champion** (Ronin Ch4) — L 45 · HPx 12 · Resolve 16
- Foes: **Great Naga's champion**.
- Weak: Air, Yari, Fire. Resist: Water.
- Skills: *Pearl Spear*, *Coil*.
- **Talk-down on Suki** (`naga_talked_down`; Honor +).
- Drop: Naga Pearl (Water accessory). Steal: none.

---


## 9. FINALE
| id | L | Notes |
|---|---|---|
| b_shrine_wave_1–7 | 55–57 | goblins · breach · burning fanatics · ogre ram (+"Ryozo" if `oni_named_ryozo`: L 56, HPx 6, Resolve 10, weak Jade, Bo) · abbot escort · close the breach · spidery horror (wave boss: HPx 8, Resolve 12, weak Fire, Jade). Two parties alternate. |
| b_shinomen_a/b | 56 | Shadowlands beasts; Naga-trail terrain |
| b_kumo_spiders | 56 | only if rude to Mamoru (Kumo ×3; weak Fire) |
**b_final_nashiko_p1 "The Bride"** — L 58 · HPx 14 · Resolve 20 − broken shields
- Weak: Jade, Crystal, Fire.
- **Invisible** (crystal / thin jade reveals her; `nashiko_unmasked` → visible on turn 1).
- **Blood Shouting:** damage transfers to her seduced champions (×2) unless the Bloodspeaker book broke it.

**b_final_nashiko_p2 "Body of Damned Time"** — L 58 · HPx 14 · Resolve 24 − broken shields
- Weak: Void, Water, Jade.
- **Aging timer:** stacking stat drain each turn. "Whole" Water heals cleanse it.

**b_final_nashiko_p3 "True Form"** — L 60 · HPx 16 · Resolve 28 − broken shields
- Weak: **Jade, Crystal, Obsidian** (obsidian Taints its user).
- Exploit commands:
  - *Smooth Stone Decoy* — she loses a turn
  - *Disfiguring Strike* — any crit to the face staggers her
  - *"Empress" Bait* — needs `rehearsal_quality` good; she drops her guard for 1 turn
  - *Two Voices* — Mamoru's tip; her next action is wasted
  - *Immovable Hand of Peace* — Tamotsu R5; locks her for 1 turn
- At 10% she flees, and the callback montage plays → the scripted end.

---

## 10. SIDE STORIES (`sidestories/`)
| id | L | Foes | Resolve | Weak |
|---|---|---|---|---|
| b_ss_rin_bandits | 9 | bandit ×3 (protect the courier) | 2 | Katana, Yumi |
| b_ss_rin_hunters | 26 | blood-hunter ×2 | 5 | Jade, Yari |
| b_ss_hideki_duel | 23 | Unicorn duellist | 5 | Tanto, Air |
| b_ss_saran_scavengers | 23 | scavenger ×3 | 3 | Water, Bo |
| b_ss_daigo_bats | 23 | cave bat ×4 | 2 | Fire, Yumi |
| b_ss_toshiro_vault_kami | 33 | vault kami | 7 | Water, Void |
| b_ss_goro_troll | 33 | troll | 8 | Tetsubo, Fire |
| b_ss_fujio_maho | 33 | maho-tsukai (talk-down possible) | 7 | Jade, Water |
| b_ss_sakura_agent | 19 | Daidoji agent | 5 | Yari, Air |
| b_ss_takeo_race | 19 | Lion riders ×3 (turn race) | 3 | — |
| b_ss_michio_troll | 19 | loose troll | 6 | Tetsubo, Fire |
| b_ss_team_nest | 46 | Shadowlands nest (boss: brood-mother, HPx 8, Resolve 12) | 12 | Jade, Fire, Tetsubo |
| b_ss_shino_thugs | 5 | thug ×3 | 2 | Bo, Yari |
| b_ss_shino_retainers | 33 | retainer ×3 | 4 | Katana, Yari |
| b_ss_kaito_ring | 5 | ringer | 3 | Bo |
| b_ss_kaito_tadayasu | 43 | Tadayasu + Storm Legion ×2 (HPx 6, Resolve 10) | 10 | Bo, Katana, Water |
| b_ss_yoshiro_seabeast | 21 | sea-beast | 6 | Air, Jade |
| b_ss_kiku_escort | 5 | bandit ×4 (Kiku can't attack) | 2 | Katana |
| b_ss_karasu_hunters | 32 | Taint-hunter ×3 | 4 | Jade |
| b_ss_benjiro_father | 33 | Moto akutsukai (his father; HPx 6, Resolve 10) | 10 | Jade, Fire |
| b_ss_hiro_well_guardian | 43 | tiger-spirit | 9 | Fire, Yari, Jade |
| b_ss_jinnai_bandits | 21 | bandit ×4 | 2 | Bo, Katana |
| b_ss_yosai_cultists | 5 | Kokujin cultist ×3 | 3 | Water, Bo |

## 11. Next
- Tune in the engine prototype (DESIGN M1). Validate Suki counts against Octopath pacing (Ch1 bosses break about
  twice per fight; finale phases about 3–4 times).
- Write drop and steal items into the equipment list (`rules/equipment.md`, still to do).
