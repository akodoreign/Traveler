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
| `tools/gen_sprites2d.py` | **The sprite pipeline + the eight travelers (EP200–EP207).** True 2D pixel-rule art (no 3D rendering): 80×68 frames, 14×11 sheet, 154 rigged poses (idle·walk·run·attacks·casts·hurt·guard·KO·victory·interactions·front/back views); high-resolution sheets add side and front gesture rows. Per-character spec dict: hairstyle (ponytail, long, long_topknot, bob, short, spiky, mane, bun, chonmage, bald), bangs, face shape, eyes (normal/narrow/old/closed/glow), brows, mouth, facial hair, scar, masks (cloth, mempo, porcelain, death paint, reed, noh, stitched), head (hachimaki, headcloth, kabuto, kabuto_full + crest), hat (jingasa, eboshi), build (normal, armored, armored_light, heavy o-yoroi, robe, monk, peasant, round), height/wide, age, haori + fur trim, cloak, patterns (waves, diamonds, stripes, dots, checks, flames), clan mon, laced armour, weapons (yari, naginata, katana, nodachi, tetsubo, bo, shakujo, tanto, kama, fan, yumi), props (mapcase, quiver, basket, daisho, saya, jitte, gunbai, ofuda, scroll, gourd, inro, lantern, swordsback). Attack/idle/victory animations per fighting style (thrust, slash, smash, shoot, iai). **Arm rig (side views):** fixed-length 2-bone IK with an anatomical elbow fold; weapons hang off the near fist and two-handed weapons pull the far fist onto the grip (`rig_arms`, `TWO_HAND`); grip fists, a lit near-arm layer with a contact outline, forged blades (`forge_blade`; metal kept out of the outline pass). All battle-character and foe models apply a shared 1.2 display multiplier without changing animation-cell boundaries. Preview: `tools/preview_arms.py`. |
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

### The 3-D mannequin under the sprite art

`tools\rig3d.py` solves every pose on a light 3-D skeleton and lays each drawn part along its
projected bone; nothing is drawn per pose. JSON profiles in `tools\cutout_profiles` name the
transparent parts (head, torso, waist, thigh/shin/foot, one relaxed arm per side and view, weapon)
with their anchor and socket pixels. Arms are cut into overlapping upper-arm, forearm and hand
layers at their `elbow` and `wrist` sockets. Character space is x forward, y up, z toward the
camera; `N` is the camera-side half of the body and `F` the far half.

- The rest skeleton is calibrated per view from that view's torso sockets, so shoulders, hips and
  neck land exactly on the artwork in the side (32 degrees toward the camera), front and back views.
  Each sleeve is pinned to the drawn shoulder; bones keep their length, parts only foreshorten
  along their own bone, and depth order comes from the solved depth.
- Feet are planted targets. The pelvis sinks to keep both fixed-length legs in reach; knees point
  where the toes point. Feet swap to camera-facing or heel art by their heading.
- `tools\rig3d_poses.py` holds the clips as controls: feet in leg lengths from beneath each hip,
  hands in arm reaches from their own shoulder, weapon direction, lean/twist, kicks. Standing is a
  small stagger (camera-side foot a little back, toes to the camera); combat is a compact base with
  that foot as the rear foot. Attack tables are six evenly spaced keys per weapon family
  (`pole`, `blade`, `iai`, `short`, `bow`, `fist`); `critical` / `void_critical` reuse two of them.

- Two-handed weapons put the second hand on the shaft a set distance from the first. A sheathed
  katana is the real blade clipped at the scabbard mouth: the `iai` family grips hilt and scabbard,
  pulls the scabbard back, draws from the hip and cuts outward over a dropped rear knee.
  The `fist` family (Togashi Yosai) never shows a weapon: guard, jab, reverse punch, chop, front kick.

```powershell
py -3.12 -E tools\build_cutout_batch.py                       # cut atlas art into parts + profiles
py -3.12 -E tools\rig3d_sheet.py trav_rensei --review "idle8:0,fidle:0,atk_draw:3" --zoom 3
py -3.12 -E tools\rig3d_sheet.py trav_rensei --install        # bake 211 frames, install the sheet
```

`--review` writes `_art\preview\rig3d\review.png` (one row per character) without touching game
assets. Baking keeps the legacy 182 frame indices and appends squat, celebration, critical and
void_critical; a pose that leaves its native 208x184 cell is an error, not a clipped frame.
`tools\test_rig3d.py` checks the invariants.

Equipment looks (`trav_<key>__<weapon>_<hat>`) are the same rig with swapped gear:
`tools\rig3d_gear.py` draws the weapon or head item and `tools\rig3d_looks.py --install` bakes every
look the plugin can select. Weapon families `club` and `gun` cover the tetsubo and musket.

Cast batches are seven characters per pair of drawn atlases (heads + armless torsos; arms + legs):

```powershell
py -3.12 -E tools\cutout_prompt.py next                # the next seven keys and their art rows
tools\cutout_batch.ps1 cast12 <cores image id> <limbs image id> "release message"
```

`cutout_prompt.py` writes the art description from each `gen_sidecast.CAST` entry (hirelings first,
then cast order). The batch script cuts the atlases into parts (keying out a flat backdrop, finding
the dummy's arm sockets for the shoulders), bakes and installs the seven sheets, runs the invariants
and a real battle, and releases with `tools\release_here.py`. `tools\cutout_batches.json` records
which keys are done; everything not listed there still uses its previous sheet.
The cast bake scales the assembled cutout around its foot anchor at X 121%, Y 90%, Z 110%, with
a wider 248x184 output cell. To rebake installed batches without recutting the atlases, run
`py -3.12 -E tools\cutout_batch_run.py --rebake` (append batch names to limit the scope).
Cast heads render at 82% of their authored size and sit into the collar using each view's drawn
shoulder sockets. Travelers and Togashi Yosai keep their original head fit.
Cast faces keep their neutral angle during ordinary animation, following the collar without
independent head motion. Explicit emote clips can still move the head.

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
| **Hired support framing** | With a hireling in the third row, the normal battle camera uses at least the wider 12-unit arena viewport, plus support and narrow-screen padding. Battles without a hireling and victory shots keep their existing framing. |
| **Turn-order portraits** | THIS TURN and NEXT prefer face-and-shoulder crops of the character's dialog bust (travel look where available), retaining gold ally/red enemy frames. Characters without a bust keep their sprite portrait. Rebuild only bust thumbnails with `python -E tools\gen_portraits.py --busts-only`. |

## 4. How to test

Dragon's Breath (`S460`) and Breath of the Fire Dragon (`S335`) share
`RokuganDragonBreath.sk` and `resource/efx/rt/dragon_breath.ptd`. The stream
plays once after charging and sweeps the opposing formation; normal targeting
still applies (all enemies for the tattoo, one target for the spell).

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

### Parallel Windows playtests

Use Python 3.12 or newer and run these commands from the Traveler worktree. A testplay profile uses the unchanged
RPG-Cobo executable in its own folder. Profiles keep separate saves and client settings, logs, screenshots,
temporary files, and a physical copy of the project. Allow about 7 GiB for each copy. The default profile location
is `%LOCALAPPDATA%\RokuganTraveler\Instances`.

```powershell
python tools/traveler_instances.py provision qa-a
python tools/traveler_instances.py provision qa-b
python tools/traveler_instances.py launch qa-a
# Separate terminal
python tools/traveler_instances.py launch qa-b -- -map M555 '[48,12,48,0]'
```

Use `sync qa-a` while that slot is closed to copy new and updated worktree files into it. Saves and settings stay
in the slot. Provision a fresh slot when removed worktree assets must also disappear. Run `launch --dry-run qa-a`
to inspect the arguments, paths and environment before launch. Each launch records its own file under the slot's
`log`. Use `--profiles C:\path\to\instances` before the command to choose another profile location.

RPG-Cobo derives its testplay window ID and working directory from the executable's folder. A second launch
in the same folder can bring that folder's existing window forward and return exit code 7. Independent slots use
different folder IDs. Plain `rpgcobo.exe` opens the editor. The Traveler batch launcher and these slots both use
`-testplay`. The debug window lowers its sound gain when it loses focus. Keyboard input follows the focused window.

### Critical presentation and reusable animation clips

`RokuganVoidCrit.sk` wraps `SkillCommand.attackAction` after damage/crit resolution. The first successful
critical in a command can play a special striker clip; a Void critical first shows its school attack title
and bust for **1,500 ms**, removes the entire banner, then plays the action. Multi-hit/multi-target actions
show each kind once per command. School gifts remain in the existing `onAttack` hook; no crit rolls, damage,
VP costs, conditions, or story logic are moved into presentation.

The actor's **current** `animap` (including equipment variants) supplies the clips:

| Kind | Attack-specific clip | Generic fallback |
|---|---|---|
| Critical | `critical_<key>` | `critical` |
| Void critical | `void_critical_<key>` | `void_critical` |

`<key>` is `skill.rt_anim_key`, falling back to `skill.atkact.atkani.id` (for example `slash1`).
Authors can append independent ranges without changing existing atlas frame numbers. Entries use the normal
`id`, `st`, `en`, `spd`, `loop:false`, `replay:true` fields; `en > st` and `spd > 0` are required.
Missing clips retain the native attack. Invalid looping/non-replayable ranges are logged and skipped.

For a character/attack override, register after the extension loads:

```javascript
::Rokugan.registerCritical("P101", "iai", "void_critical", {
    clip = "void_critical_iai",
    title = "Strike with No Thought!",
    title_ms = 1500,
    speed = 0.65
});
// Set rt_anim_key = "iai" on the authored skill; clones retain this key.
```

Character and attack selectors also accept `"*"`. Lookup priority is exact character/attack, character/*,
*/attack, then */*. A configured clip is tried before the convention-based IDs. Ordinary critical speed
defaults to 1; Void critical speed defaults to 0.65. Set `speed = 1` to disable slow motion. The title is
clamped to 1-2 seconds and clip speed is bounded so an authored special finishes within 2 seconds (with a
2.1-second playback watchdog). Only the selected animation layer is affected, never global game time.
The native attack script still handles its sound, effects and projectiles; hit/damage application remains
in the engine and runs once after the special animation.

Run `py -3.12 -E tools\test_critical_presentation.py` for real-engine checks and title/action/cleanup screenshots
under `_art\preview\critical_presentation`. It uses `engine_lock`, stops only its own process, and temporarily
aliases existing frames in memory: it does not generate art or change production crit chances. Coordinate the
single-instance engine with other running tests first.

### Many Faces introduction

The willow-teahouse escape pauses at a single, non-cancellable Many Faces choice immediately before
Mitsue becomes a teahouse servant. Confirming it continues the original narration and exit sequence.

### Mitsue's wardrobe

`RokuganCostumes.sk` and `tools\mitsue_costumes.py` define Mitsue-only body disguises. Mitsue cannot wear
ordinary body armor. Costumes are earned through Many Faces scenes, automatically equipped, never sold
in shops, and protected against selling or discarding. The shinobi costume starts with a removable,
Mitsue-only head-slot mask. Disguises replace its headwear with their matching cap, fox ears, or helmet.

The equipped costume grants its arts in battle and the field skill menu; changing it removes those
arts without teaching them permanently. Shinobi grants Steal/Copy, maid grants herbal healing, fox
grants Trickster, clerk grants Deduce, pilgrim grants Elemental Ward, and soldier grants Cover/Heavy Slash.
Costume arts use TP (8 by default, retaining a higher existing TP cost). Trickster always costs 8 TP;
its random borrowed art bypasses weapon, ingredient, learning, Void, and limited-use requirements,
not the TP cost. Neither manual selection nor Auto can use an art without enough TP.

Scorpion district-shrine tailors exchange an owned original (equipped or carried) plus the requested
materials for its reinforced version, preserving the disguise's arts and appearance. Silk is found
in the Egg Caves, a clasp on the Crane coast, and Shells can be stolen from Tide Crabs. Each road keeps
its own bag and equipment; switching travelers starts an unvisited road with a fresh bag. The finale
merges the saved bags once, retaining costumes without duplicating them.

`tools\test_mitsue_costumes.sk` checks restrictions, headwear, outfit-only arts, TP payment, tailoring
from equipment and the bag, protected items, saved wardrobe snapshots, and the final inventory merge.
`tools\test_mitsue_trickster.sk` runs once before and once during a battle to check the actual School
menu's TP gate and borrowed kata, recipes, Void spells, and already-used Drawing the Void.

### Kudo investigation guidance

The Scorpion Chapter 1 marker includes the governor's investigation conversation in Kitsune Hall,
followed by the dock-hand or Hana if another suspect clue is needed. These targets require Rui's introduction
and disappear when the night departure begins; failed Eavesdrops still leave guaranteed clue sources.
This keeps an unfinished investigation from falling through to Chapter 2's still-locked road.
`tools\gen_maps.py` derives the target coordinates from the conversations rather than duplicating them.
`tools\test_scorpion_marker.sk` reproduces the reported save's flags and checks the investigation,
night departure, and eventual Chapter 2 handoff without saving or changing a player's save file.

The governor's Eavesdrop is guaranteed (100%). `G848` remains the old attempt flag; `G858` records a
successful listen, so a save with a failed old attempt can retry without farming additional clues.
Old saves did not distinguish success from failure, so an already-successful old attempt can also
earn one additional clue on its first retry; subsequent talks cannot award another.
The existing Many Faces disguise scene is offered immediately after success and again on later talks
until `G849` records the reveal. The original kitchen-servant interaction remains available too.
`tools/test_scorpion_governor.sk` exercises the real dialogue: retry an old failed attempt, decline
the disguise, then reopen it on a second talk and verify that the clue is counted only once.

## 5. Next steps (M1 polish → M2 vertical slice)
1. Weakness icons instead of names; shield pips. (Suki sprite effect done: broken enemies are desaturated/darkened via setHSV and restored on recovery.)
2. Turn order: done (labels + THIS TURN / NEXT portrait bar).
3. Talents: v1 done (see §3). Still to do: the kata toggle (`rules/kata.md`), talent upgrades at Rank thresholds, per-traveler command names.
4. Rumble meter for the Egg Caves (Crab Ch1's gimmick) as the first chapter gimmick hook.
5. **M2:** build Crab Ch1 maps from `storyboards/crab-ch1.md` (Wall watchtower, garrison, coast road, Hoshi-no-Ichi,
   quarry, Egg Caves) with the production script's events.
6. Localisation: jobs, basic items and status conditions are English (`gen_data.LOCAL`; these tables need plain-string names), and baked-in .ui labels are patched by `tools/patch_ui.py` (same-byte-length replacements). Still Japanese: unused template weapons/armour/enemies and some menu layouts.
