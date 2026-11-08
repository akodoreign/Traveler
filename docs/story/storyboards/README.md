# Storyboards — chapter-by-chapter map walkthroughs (v1)

**What this is:** for every chapter, a **branching storyboard**: the route through the chapter as a flowchart, then
every map the player walks through, Octopath style. Each map shows where things are (entrances, NPCs, shops,
chests, path-action targets, triggers, encounters), followed by a **simulated playthrough** and the
**findings** it turned up. Findings are fixed in `production/` (or in the rules) and logged at the end of each file.

**Sources for geography:**
- **Map A:** the *Emerald Empire* (4e) geography map, p. 14 (provided by the user). It uses translated names.
- **Map B:** the user's political map of family borders and roads ("Rokugan, Ende des Monats des Hasen 1129 IK",
  F. Mahn, 2019). It shows a later year, but the roads and family borders still hold for 1123.
- **Fortune's Lost** area and cave maps (`Adventures In Rokugan/`), for the Ojatara Valleys and Naohida's caves.

Positions below are given **relative to Map A's labelled icons**. Canon names come first. A Map A label is given
only where the match is certain: Hida Palace = **Kyuden Hida**; Esteemed Palaces of the Crane = **Kyuden Doji**;
Imperial City = **Otosan Uchi**; Silk and Shadow Palace = **Kyuden Bayushi**; Journey's End = **Ryoko Owari**;
High House of Light = **Kyuden Togashi**; Isawa Elemental Academies = **Kyuden Isawa**; Violence Behind Courtliness
City = **Toshi Ranbo**; Yasuki Estates = **Yasuki Yashiki**; Carpenter Castle = **Kaiu Shiro**; Beiden = **Beiden
Pass**; Castle of the Fox / Sparrow / Hare = the Kitsune / Suzume / Usagi minor-clan seats.

---

## 1. Legend (ASCII maps)
North is up unless a map says otherwise. One character ≈ one tile block (not to scale).
```
@  arrival / entry point            >x  exit to map x (named in the table)
I  inn: save, party swap, Travel Banter, kata setting       t  tavern / tea house (hire help, rumours)
W  weapon shop    A  armour shop    S  item shop    $  black market (Underworld 3)
+  shrine: cleanse Taint, Bless spot, Meditate       §  save point (dungeons; Octopath's crystal)
c  chest          C  locked lacquer box (Sayo: Sleight of Hand; Octopath's purple chest)
!  story trigger  ?  side-story icon   1-9  path-action NPCs (numbers match the NPC table)
*  field prompt (skill-gated: Athletics ledge, Hunting tracks, Tremor wall, Calligraphy cipher, …)
B  boss   b  fixed battle / mid-boss   ≈  random-encounter zone (towns have none)
#  wall / cliff   ^  mountain / rock   ~  water   %  trees   "  grass / paddy   =  road / bridge   :  stairs
```

## 2. Octopath map conventions (the targets every storyboard is checked against)
| Map type | Octopath target | Rokugan rule |
|---|---|---|
| **Town** | 1–3 screens; inn, tavern, weapon/armour/item shops, church; 8–15 NPCs with path-action info; 3–6 chests; 1–2 side-story icons | Same. The **shrine** replaces the church (Taint cleanse). Shops follow `equipment.md` G by region and tier. At least **one NPC per path action** has something worth taking (an item, info or a fight), so every traveler is useful in every town. |
| **Field route** (between towns) | 1–2 screens, a danger-level sign at the entrance, 2–4 chests, one side path or hidden area | Same. The danger sign shows the bestiary `F` region and its recommended level. Hidden paths are `*` prompts (Athletics, Hunting). |
| **Dungeon** | 2–4 screens, a save point just before the boss, 6–10 chests, one off-path dead end with a treasure, the boss at the far end | Same. The dungeon's encounter table comes from bestiary `F`. One chest per dungeon is **skill-locked** (`*`), so revisiting later with another traveler pays off. |
| **Boss room** | Its own small map; the save point is in the room before | Same. |
| **Revisit** | Octopath never locks a dungeon after its chapter | **Rule:** every dungeon stays enterable after its chapter, unless the story destroys it. If the story destroys it, every chest must be reachable before the point of no return, and the game warns the player ("You won't be able to return…"). |

**Chest contents by chapter band:**
- Ch1: Rice Balls, Antidotes, Eye Drops, T1 gear, 50–200 zeni, Jade Dust ×1.
- Ch2: Herbal Salves, Incense, T2 gear, 300–800 zeni.
- Ch3: Ginseng Tonic, Fine Sake, T3 gear, 1,000–2,500 zeni.
- Ch4: T4 gear, Kami-ichor-tier items.
- Finale: T5 gear.

Haruki's **field-spell scrolls** are hidden in chests (`haruki-spells.md`): Summon Fog, Tremor, Know the Mind, and others.
One sits in each Ch1–Ch2 dungeon.

## 3. Recruiting (OT1 rule, newly written: storyboard finding R-1)
The production Ch1 files only covered the **starter** version. They had no rule for meeting a traveler who isn't
the starter. **The fix, applied to every Ch1:**
- Each Ch1 has a **Join point**: a fixed spot in the Ch1 **town**, marked `J` on its map. That is where the
  traveler stands when the party arrives.
- Talking to them plays a 4–6-line **meeting** (the other travelers are present, but silent, per OT1). Then comes
  the OT1 prompt: *"Will you join <name> on their journey?"*
  - **Yes:** the traveler joins at the party's **average level − 2** (never below their Ch1 minimum). Then their
    chapter opening plays as a **"Memory" cutscene**: the scenes before the town, with no battles and no tutorial
    popups. Play resumes at the scene the Join point names.
  - **No:** they stay at the Join point. Later, they can join without starting their chapter. Their Ch1 then
    starts from the **chapter icon** on their map instead (Octopath's "hear their story" icon).
- The **starter** plays everything, including the tutorial battle.
- A traveler's chapter 1 can't start until they are in the party. Chapters 2–4 need them in the **active four**.

### 3b. Guests (OT2 rule: finding G-1)
- **One active guest** at a time (Party 4 + 1 guest call). When a second guest joins, the player picks which one is
  active. The other **waits at the inn** and can be swapped at any inn while their chapter is running.
- Guest barks in battle play only for the guest who is present (a speaker check on each bark).
- Story guests (Squeak, Gonta, Seigen, Kiku…) leave at their chapter's end unless a side story keeps them.
- **Story companions** (Karasu in Unicorn Ch4, Kage in Crab Ch3) can follow and speak in scenes without taking the
  guest slot. They have no battle skills unless the script adds a one-off (Kage's `kage_fought`).
- **Story-locked guests** (the script needs their lines in battle, e.g. Togashi Yosai in Dragon Ch1/Ch4) can't be
  swapped out. An optional guest who joins meanwhile (Kitsuki Momo) waits on the roster until the lock ends.

### 3c. Non-fatal battles (OT rule: Olberic's Challenge never ends the game)
- **Duel** path-action battles, the bracket, and "test" duels: a loss gives the loss text and the story continues.
- Battles marked **front / wave / escort** in a set-piece (Dragon Ch4's fronts, for example): a loss loses that
  objective, not the game, unless the script says otherwise.
- Every other battle: a loss is a game over, as normal (return to the last save).

## 4. The overworld
Octopath has no free-roaming world map. **Towns connect through field routes**, and a **world-map screen** handles
fast travel between visited towns. Rokugan Traveler works the same way: **nodes** (towns, dungeons, landmarks) are
joined by **route maps** (field maps with encounters).

### 4a. Sketch (layout follows Map A; roads follow Map B)
```
 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ THE GREAT NORTHERN MOUNTAINS ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 ^ UNICORN        ^  [KT] Kyuden Togashi        [OV] Oracle's volcano     [RT] red torii cliff  ~
 ^  (Shiro Shinjo)^      [TF] Tamori's Furnace                              (Cliffside Shrine) ~~
 ^                ^  DRAGON  [DM] mtn town · inn      [KI] Kyuden Isawa ==== [CT] coast temple ~~~
 ^ [SI] Shiro     ^          [SK] Shiro Kitsuki       [IM] Isawa Mori              PHOENIX     ~~~
 ^  Iuchi ========^===================================[KM] Shiro no Kamatori =====(coast road)~~~
 ^^ SPINE OF   ===^= [WL] Wounded Lion · White Snow   [ZU] Zumiki · snow pass > [TC] Treaty City~
 ^ [OJ] OJATARA   ^     LION     [SA] SHIRO AKODO ===== [BB] Burned Bridge ===== [HC] Hiruto's  ~~
 ^  VALLEYS       ^ [KZ] Kaze-no-Tani        [TR] Toshi Ranbo         [MR] Magonojo    castle  ~~~
 ^  (Buried Leaves, Soshi) [SP] Sorrow's Path ford =========== [OU] OTOSAN UCHI ~~~~~~~~~~~~~~~~~~
 %%%%%% [PT] Plains of Thunder ·      [VP] Beiden Pass · Pleasant Eaves · Goroso's forest   ~~~~~
 %%%%%%%  Shrine of Osano-Wo   [CM] City of Masks*      [KA] Kakita Academy · [KD] KYUDEN DOJI ~
 % SHINOMEN %   [SS] Shiro no Soshi                            CRANE           [CP] Crane port~~
 %%% MORI %%%%      SCORPION  [KB] KYUDEN BAYUSHI · Traitor's Grove       [CK] Cakon (river) ~~~~
 %%%%%%%%%%%            [RO] Ryoko Owari                                                  ~~~~~
 ^ TWILIGHT %%%     [KU] Kudo (Fox | Sparrow) ==== [FF] Floating Flowers     [GS] Garden Under ~~~
 ^ MTNS   CRAB           (River of Gold)                   [YY] Yasuki Yashiki   Shadow City ~~~
 ^ [KW] KAIU WALL ======== [KH] KYUDEN HIDA ===== [HI] Hoshi-no-Ichi ~~~~~~~~ [TI] Tortoise Isle ~~
 ##### (Wall gate) ####                                 ~~~~~~~~~~~~~~ MANTIS [IS] Isle of Silk~~
 SHADOWLANDS: tar chasm · lava trees · poppy fields · Toshi no Kijo     ~~~~~~ [KG] Kyuden Gusai~~
```
`*` The City of Masks exists only during Scorpion Ch2 ("last week there was nothing here"). After that chapter, the
node shows its empty plain.

### 4b. Nodes
**Starting towns (Ch1)**

| Node | Map A position | Chapters | Danger (route) |
|---|---|---|---|
| **HI** Hoshi-no-Ichi | Crab coast between Yasuki Estates and the Temple of the Morning Sun | Crab Ch1 | 1–8 |
| **VP** Pleasant Eaves / Beiden Pass | at "Beiden", between the Lion and Scorpion hills | Crane Ch1 | 2–8 |
| **IS** Isle of Silk | Coastal Islands, near the Palace of the Mantis | Dragon Ch1 | 1–8 |
| **HC** Hiruto's castle | where the Lion, Phoenix and Crane borders meet, between Loyalty Castle and the Castle of the Centipede | Lion Ch1 | 1–8 |
| **KM** Shiro no Kamatori | southern Phoenix lands, north of HC | Phoenix Ch1 | 1–8 |
| **KB** Kyuden Bayushi | Silk and Shadow Palace | Scorpion Ch1 (→ Kudo) | 1–8 |
| **OJ** Town of Buried Leaves | Spine of the World, west of the Castle of Organization (Fortune's Lost map) | Unicorn Ch1 | 1–8 |
| **CK** Cakon | southern Crane coast, at a river mouth near Wall Above the Ocean Village | Ronin Ch1 | 1–8 |

**Later nodes**

| Node | Map A position | Chapters |
|---|---|---|
| **KW** Kaiu Wall (Natsuko's post, the Wall gate) | the Twilight Mountains line, between Kaiu Shiro and Hida Palace | Crab Ch1, Ch3; epilogue |
| **KH** Kyuden Hida | Hida Palace | Crab Ch2, Ch4 |
| Shadowlands | beyond the Wall, south-west | Crab Ch3; post-game |
| **YY** Yasuki Yashiki · **GS** Garden Under Shadow City | Yasuki Estates; the Crab–Crane coastal border | Crane Ch2 (crossroads) |
| **KA** Kakita Academy · **KD** Kyuden Doji | Esteemed Palaces of the Crane | Crane Ch1 (start), Ch4; epilogue |
| **CP** Crane port · the Crane sea | Northern Crane coast | Crane Ch3 (unlocks the **ship**) |
| **TI** Tortoise Island · **KG** Kyuden Gusai ruins | Mantis islands | Dragon Ch1–2 |
| **OU** Otosan Uchi, and the year-400 layer | Imperial City | Dragon Ch2–4 (through the ink portal); epilogue |
| **SK** Shiro Kitsuki | Dragon lands, south slope | epilogue (Gendo's office) |
| **DM** Dragon mountain town · **KT** · **TF** | High House of Light; the volcano near Fire Tooth Castle | Scorpion Ch4 (crossroads) |
| **SA** Shiro Akodo | central Lion lands, between the Swift Sword and Sacred Watch icons | Lion Ch2, Ch3 |
| **BB** Village of the Burned Bridge · **KZ** Kaze-no-Tani | the Lion–Crane border road; the western Lion hills | Lion Ch3 |
| **SP** Sorrow's Path ford | the river between Lion and Crane, south of Toshi Ranbo | Lion Ch4 |
| **ZU** Zumiki-mihari · **TC** Honored Treaty City | the Lion–Phoenix border, in the north | Phoenix Ch2 |
| **KI** Kyuden Isawa · **IM** Isawa Mori | Isawa Elemental Academies, and its forest | Phoenix Ch3 |
| **CT** coast temple town · **RT** red torii cliff | the Phoenix coast, near Cliffside Shrine | Phoenix Ch4 |
| **SS** Shiro no Soshi · **CM** City of Masks | Scorpion's north-west edge, toward Seikitsu Pass | Scorpion Ch2; Unicorn Ch1 (Soshi court) |
| **OJ** valleys: Shiro Iuchi, Perfume Petal Blossom, jade mines, Yotomo | the Fortune's Lost area map | Unicorn Ch1–4; Scorpion Ch3 |
| **KU** Kudo · **FF** Floating Flowers | the River of Gold, between the Castle of the Fox and the Castle of the Sparrow | Scorpion Ch1; Ronin Ch2 |
| **WL** Village of the Wounded Lion · Mountain of the White Snow | northern Lion hills, below the Dragon mountains | Ronin Ch3 |
| **OV** the Oracle's volcano town | Great Northern Mountains, between the Dragon and Phoenix lands | Ronin Ch4 |
| **PT** Plains of Thunder · Shrine of Osano-Wo · Shinomen Mori | the plain north-east of Shinomen Forest; the forest itself | Finale |

### 4c. Travel gates (what opens the map)
| Gate | Opens | Octopath analogue |
|---|---|---|
| Start | Every Ch1 town by road, except the Isle of Silk | OT1: every starting town is reachable |
| **Mantis ferry** (docks at Hoshi-no-Ichi and Cakon, 100 zeni) | Isle of Silk from the start. Tortoise Island after Dragon Ch1 (Tortoise Ferry Token) | OT2's ships, in a limited form |
| **Danger signs** on route maps | Ch2+ regions show the recommended level (soft gate, no hard lock) | OT1's danger levels |
| **The Crane ship** (Crane Ch3) | Coastal sailing: Crane coast ↔ Phoenix coast ↔ Mantis isles; fast travel at sea | OT2's ship |
| **Horse** (Tamotsu, Horsemanship) | Faster travel on routes, fewer encounters | Evasive-maneuvers passive |
| **The Wall gate** | Shadowlands, only during Crab Ch3; reopens post-game | Story-locked area |
| **The ink portal** (Tortoise Island) | Year-400 layer, Dragon Ch2–4 only | Story-locked area |
| **Shinomen edge** | Shown from the start with "The trees will not let you pass." Opens for the finale | OT's sealed final area |
| **Hatomu's Map** (key item) | Reveals the whole world map (side story) | — |

---

## 5. Index
| Traveler | Ch1 | Ch2 | Ch3 | Ch4 |
|---|---|---|---|---|
| Natsuko (Crab) | [crab-ch1](crab-ch1.md) | [crab-ch2](crab-ch2.md) | [crab-ch3](crab-ch3.md) | [crab-ch4](crab-ch4.md) |
| Rensei (Crane) | [crane-ch1](crane-ch1.md) | [crane-ch2](crane-ch2.md) | [crane-ch3](crane-ch3.md) | [crane-ch4](crane-ch4.md) |
| Gendo (Dragon) | [dragon-ch1](dragon-ch1.md) | [dragon-ch2](dragon-ch2.md) | [dragon-ch3](dragon-ch3.md) | [dragon-ch4](dragon-ch4.md) |
| Shizue (Lion) | [lion-ch1](lion-ch1.md) | [lion-ch2](lion-ch2.md) | [lion-ch3](lion-ch3.md) | [lion-ch4](lion-ch4.md) |
| Haruki (Phoenix) | [phoenix-ch1](phoenix-ch1.md) | [phoenix-ch2](phoenix-ch2.md) | [phoenix-ch3](phoenix-ch3.md) | [phoenix-ch4](phoenix-ch4.md) |
| Mitsue (Scorpion) | [scorpion-ch1](scorpion-ch1.md) | [scorpion-ch2](scorpion-ch2.md) | = Unicorn Ch2 | [scorpion-ch4](scorpion-ch4.md) |
| Tamotsu (Unicorn) | [unicorn-ch1](unicorn-ch1.md) | [unicorn-ch2-scorpion-ch3](unicorn-ch2-scorpion-ch3.md) | [unicorn-ch3](unicorn-ch3.md) | [unicorn-ch4](unicorn-ch4.md) |
| Sayo (Ronin) | [ronin-ch1](ronin-ch1.md) | [ronin-ch2](ronin-ch2.md) | [ronin-ch3](ronin-ch3.md) | [ronin-ch4](ronin-ch4.md) |
| All | [finale](finale.md) | | | |

## 6. Findings log (all chapters)
Each chapter file ends with its own findings. Cross-cutting ones:
- **R-1** No recruit version for Ch1s → §3 rule, plus a Join point and Memory cutscene in every Ch1 production file.
- **G-1** Chapters that give two guests at once (Crane Ch1, Dragon Ch1) → §3b one-active-guest rule.
- **N-1** Nashiko's disguises had no path-action behaviour → she **blanks** Discern and Eavesdrop (crab-ch2 F-4).
- **P-1** Lion Ch1 and Phoenix Ch1 share one week and one boss, with no rule for playing the second → **pair
  rule**: first = as written, plus silent cameos; second = a playable flashback ("That week…") with locked shared
  choices.
- **C-1** The co-owned Unicorn Ch2 = Scorpion Ch3 had the same problem → both owners present: counts for both;
  one owner: the other's view is a later flashback with the verdict locked; Mitsue's view scales to Lv 30–35.
- **D-1** The Dragon arc trapped the party in the year 400 from Ch2 to Ch4 → **the Ink Door** (Miyoshi's duplicate
  painting, found at the end of Ch2) links the year-400 south gate and the Tortoise cove; it closes after Ch4.
- **Y-1** Togashi Yosai is "lost in the ink" between Dragon Ch2 and Ch4 → any present-day appearance in that window
  must be gated (`dragon_ch2_not_done`, as Phoenix Ch2 does; Scorpion Ch4 needs it too).
- **S-1** Many dungeons put their only save at the entrance, or at a story beat several maps before the boss → each
  storyboard checks for a `§` directly before the boss.
- **T-1** Every town must give each path action a target. Most Ch1 towns were missing 3–5 of the 8 → NPC rows added.
