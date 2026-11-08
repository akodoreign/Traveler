# Engine — RPG-Cobo setup and the battle prototype (session 3)

Status: **M0 (engine up) done · M1 (battle prototype) done** — Suki, Void Points and Boost verified in a test battle.

## 1. Where things are
| Path | What |
|---|---|
| `_tools/rpgcobo-tool/` | RPG-Cobo engine/editor (clone of akodoreign/rpgcobo-tool). `rpgcobo.exe` = editor; `-testplay` = game |
| `_tools/rpgcobo-tool/project/data/` | Game database (JSON). Installed from the default template, then rewritten by `tools/gen_data.py` |
| `_tools/data_orig/` | Pristine copies of the template data files (gen_data rebuilds from these every run) |
| `_tools/rpgcobo-tool/project/plugin/rokugan/` | **Our battle plugin** (`plugin.sk`, `RokuganBattle.sk`), enabled in `plugin/plugin.json` |
| `_tools/rpgcobo-tool/project/resource/` | Assets. `enemy_pic.json` + `enemy_pic/*.png`: EP100–EP106 Crab Ch1 monsters, **EP200–EP207 travelers**, **EP300–EP326 side cast**, **EP400–EP427 human enemies** (all HD-2D sprites); `renderset.json` (rt_hd2d_*), `vox/map/*` tiles |
| `tools/` | Generators and helpers (below) |
| `_art/preview/` | Preview renders and test screenshots |
| `.mcp.json` | Registers the engine's MCP server (`rpgcobo.exe -mcp-stdio`) for Claude Code (loads on the next session; the editor must be running) |

## 2. Generators (procedural content; all idempotent)
| Script | Output |
|---|---|
| `tools/gen_data.py` | type.json (12 bits = Katana, Yari, Tanto, Tetsubo, Yumi, Bo, Fire, Water, Air, Earth, Void, Jade) · cond K030 **Suki** · skills S100–S105 weapon strikes, S110 Razor's Edge, S111 Jade Strike · weapons W100–W105 (T1) · enemies E100–E106 (Crab Ch1 set) + E190 training dummy · players P100–P107 (the eight travelers) · setting (title, start party Natsuko/Rensei/Gendo/Shizue, Boost in battlecmd4) · M001 encounter groups (1 goblin raid, 2 egg caves, 3 training) · plugin.json |
| `tools/gen_sprites2d.py` | **The sprite pipeline + the eight travelers (EP200–EP207).** True 2D pixel-rule art (no 3D rendering): 80×68 frames, 8×4 sheet, 27 frames (idle·walk·ready·attack·cast·hurt·guard·KO·victory). Per-character spec dict: hairstyle (ponytail, long, long_topknot, bob, short, spiky, mane, bun, chonmage, bald), bangs, face shape, eyes (normal/narrow/old/closed/glow), brows, mouth, facial hair, scar, masks (cloth, mempo, porcelain, death paint, reed, noh, stitched), head (hachimaki, headcloth, kabuto, kabuto_full + crest), hat (jingasa, eboshi), build (normal, armored, armored_light, heavy o-yoroi, robe, monk, peasant, round), height/wide, age, haori + fur trim, cloak, patterns (waves, diamonds, stripes, dots, checks, flames), clan mon, laced armour, weapons (yari, naginata, katana, nodachi, tetsubo, bo, shakujo, tanto, kama, fan, yumi), props (mapcase, quiver, basket, daisho, saya, jitte, gunbai, ofuda, scroll, gourd, inro, lantern, swordsback). Attack/idle/victory animations per fighting style (thrust, slash, smash, shoot, iai). **Arm rig (side views):** fixed-length 2-bone IK with an anatomical elbow fold; weapons hang off the near fist and two-handed weapons pull the far fist onto the grip (`rig_arms`, `TWO_HAND`); grip fists, a lit near-arm layer with a contact outline, forged blades (`forge_blade`; metal kept out of the outline pass). Preview: `tools/preview_arms.py`. |
| `tools/gen_sidecast.py` | EP300–EP326: 27 supporting-cast sprites from `docs/art/cast-looks.md` (L5R wiki + adventure notes). |
| `tools/gen_human_enemies.py` | EP400–EP427: bestiary A1–A7 human enemies (bandits, ronin, contentious samurai, ashigaru, pirates, cultists, ninja); gen_data turns them into E200–E227 (test groups M001 gid 4 / 5). |
| `tools/gen_maps.py` + `plugin/rokugan/RokuganMapGen.sk` | **Procedural maps.** Python designs each map (column grid of block id + height, plus objects: free-block trees/rocks/lamps, block fills, prefab map assets) with a Rokugani kit (plaster/dark-wood buildings with gabled kawara roofs, torii, shrines, the Kaiu Wall, piers, fences); writes `tmp/rt_mapgen/job.json`, runs the engine once, the plugin builds every `.bw` and quits. Registers maps in map.json with events (NPCs, portals, chests, autorun cutscenes guarded by global flags), render preset, encounters. Maps are padded with scenery so the camera never shows the void. Crab Ch1: **M100** Wall watchtower (night, S01 opening + goblin raid), **M101** Wall garrison, **M102** Coast Road (random battles), **M103** Hoshi-no-Ichi, **M104** quarry camp (S04 Sumai); battle backdrops **M810** Wall at night, **M811** coast, **M812** quarry. New Game starts on M100. Block ids: page | index<<5 (see the module docstring); event pos = blocks, spawn/inimap pos = world units (2 blocks). |
| `plugin/rokugan/RokuganField.sk` | Field systems: `rt_follow` escort followers (breadcrumb trail; `lead` = event id number), Sumai weapon swap (`::Rokugan.sumaiBegin/End`), `-rtvar G0xx,...` playtest flag switch. |
| `tools/preview_cast.py` | Preview sheets `_art/preview/travelers_final.png`, `sidecast_final.png`. |
| `tools/gen_render.py` / `tools/gen_terrain_tex.py` | HD-2D render presets (deep focus, matte IBL, PBR fog — fog colour low byte is an exponent) and pixel-texture painting of the voxel map tiles. |
| `tools/gen_travelers.py`, `gen_sprites.py`, `gen_sprites3d.py` | Superseded experiments (voxel recolour / stick sprites / 3D-rendered sprites). |
| `tools/gen_enemy_art.py` | EP100 Goblin in a Hat (drawn straw jingasa) · EP101 Nezumi Warrior · EP102 Cave Beetle (drawn from scratch) · EP103 Mamushi · EP104 Tide Crab · EP105 Nezumi Shaman. Preview: `_art/preview/enemies_crab_ch1.png`. Restore `_tools/enemy_pic.orig.json` first when re-running |
| `tools/voxlib.py` | MagicaVoxel reader (scene graph, palette), RPG-Cobo palette encoding (**0x1BBGGRR**, 1-based voxel index), preview renderer |
| `tools/wincap.py` / `tools/winkeys.py` | Capture a window by PID / send keys to it (for automated playtests until MCP is connected) |

## 3. The battle plugin (`plugin/rokugan/RokuganBattle.sk`)
| System | Implementation |
|---|---|
| **Suki** | Enemy score prop `RES` (shields, editable in the DB). Weakness = any attribute bit with `EDR < 0` (set with `opt_elemdef`, −50 = ×1.5). The `attack` event chips one shield per weakness hit; at 0 → cond K030 (uncommandable, `rem_turn [2,2]`) so the enemy loses its pending action (engine swaps uncommandable actors to S000) and next turn's action; damage taken ×1.5 while open; shields refill at the first `preturn` after the condition ends. |
| **Void Points** | Per-battle state (not saved): start 1, +1 each `preturn`, not on the turn after boosting, max 5 (plugin prop). |
| **Boost** | Battle command `boost` (slot battlecmd4) cycles 0..min(3, VP) without ending the character's input. `precommand` applies it: normal weapon attacks get +n hits, skills ×(1+n) power. Auto battle spends VP when full. |
| **UI** | Enemy list per enemy: `Name [shields] ? ? ?` → weakness names appear once hit; `SUKI!` while open. Party list: `Name VP n (+boost)`. Pops: SUKI!, BOOST xN, RESOLVE. |
| **Log** | `[RT] …` lines on stdout (plugin prop `log`). |
| **HD-2D screen** | `RPGStage.launch` / `changeRenderSetting` wrapped: a colour-grade matrix on the deferred output pass (saturation ×1.12, warm highlights) and a full-screen vignette image (`resource/efx/rt_vignette.png`, from gen_render) inserted between `stage3d` and the stage UI. Map weather (gen_render): field = drifting **cloud shadows** (dappled light pools), battle = warm floating **motes**. Weather/renderset colours are signed int32. |
| **Turn order** | Each turn's random speed factor is pre-rolled one turn ahead (`Rokugan.rollOrder`) and reused by an overridden `SkillCommand.calcCommandOrder`, so the `#n` ranks and the **portrait bar** (THIS TURN / NEXT rows at the top; current actor drops, acted/fallen dim; portraits from `tools/gen_portraits.py` → `resource/efx/portrait/`) show the real order. Verified over several turns: NEXT becomes the actual next order. |
| **Talents** | Battle command `talent` (battlecmd5) → each traveler's talent skill (gen_data S110, S120–S127); plugin `onTalent` adds the special parts. Natsuko **Razor's Edge** (guard + enemy single-target attacks drawn to her 2 turns) · Rensei **Iaijutsu** (Focus, then Strike: certain crit ×2.5) · Gendo **Deduce** (reveals all weaknesses) · Shizue **Command** (party ATK up + party acts first next turn via the pre-rolled order) · Haruki **Attune** (next spell ×1.5) · Mitsue **Many Faces** (steal) · Tamotsu **Barter Coin** (spends 5% of zeni, min 50: damage grows with the spend) · Sayo **Remedy** (heal + cure poison). All verified in-engine. |
| **Animation fixes** | `atk_normal` overridden so picture models play `atkani`; sprites use `replay:false` on loops. |

## 4. How to test
```
cd _tools/rpgcobo-tool
rpgcobo.exe -testplay -battle M001 3 -debuglv 5     # training dummy (30000 HP): Suki + Boost cycles
rpgcobo.exe -testplay -battle M001 1 -debuglv 3     # Crab Ch1 goblin raid with the Goblin in a Hat
rpgcobo.exe -testplay -battle M001 4 -debuglv 3     # human mobs: bandit, ronin, drunken samurai, ashigaru
rpgcobo.exe -testplay -battle M001 5 -debuglv 3     # cultists & ninja
```
**Full regen order:** gen_data → gen_maps (only when map designs change; gen_data re-registers maps itself) → **gen_render last** (it sets presets on the registered maps).
Regenerate sprites: restore `_tools/enemy_pic.orig.json` → gen_enemy_art → gen_sprites2d → gen_sidecast → gen_human_enemies → gen_data → gen_render.

**Engine quirks fixed in the plugin:** the stock `atk_normal` script skipped attack animations for picture models (`if(ispic) return`); the battle re-requests `stand` every frame, so looping animations must be `replay:false` or they freeze on frame 0.
Redirect stdout to a file and grep `[RT]`. In battle: **V** = auto battle, Z = apply, X = back. The game pauses
while its window is not focused.

**Verified (session 3):** weak hits chip shields 3→2→1→0 · SUKI! · the enemy's queued action and next action are
skipped · shields refill after two turn-ends · VP 1→5 cap · no VP gain after a boost · Boost x3 = 4 hits (each hit
chips a shield). No script errors.

## 5. Next steps (M1 polish → M2 vertical slice)
1. Weakness icons instead of names; shield pips. (Suki sprite effect done: broken enemies are desaturated/darkened via setHSV and restored on recovery.)
2. Turn order: done (labels + THIS TURN / NEXT portrait bar).
3. Talents: v1 done (see §3). Still to do: the kata toggle (`rules/kata.md`), talent upgrades at Rank thresholds, per-traveler command names.
4. Rumble meter for the Egg Caves (Crab Ch1's gimmick) as the first chapter gimmick hook.
5. **M2:** build Crab Ch1 maps from `storyboards/crab-ch1.md` (Wall watchtower, garrison, coast road, Hoshi-no-Ichi,
   quarry, Egg Caves) with the production script's events.
6. Localisation: jobs, basic items and status conditions are English (`gen_data.LOCAL`; these tables need plain-string names), and baked-in .ui labels are patched by `tools/patch_ui.py` (same-byte-length replacements). Still Japanese: unused template weapons/armour/enemies and some menu layouts.
