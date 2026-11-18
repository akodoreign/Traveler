# 3-D-backed pixel-art characters

Every human character is one skinned vertex mesh on an armature, built and posed in Blender, and rendered
at sprite resolution into pixel art. No frame is drawn: a new outfit, weapon or animation is a change to the
model or the pose numbers. This replaces the voxel skin (`docs/VOXEL_CHARACTERS.md`) and the 2-D cutout rig.

Status: the pipeline runs end to end for the whole roster, but the art is not yet at the target quality
(see "Known gaps"). Nothing from it is installed in the game until `chara3d_all.py --install` is run.

## Pieces

| File | Role |
|---|---|
| `tools\blender\chara3d.py` | Runs inside Blender. Builds the body, hair, clothes and weapon as one mesh with authored bone weights, poses the armature, and renders each frame three ways: lit, flat colour, part id. |
| `tools\rig3d_poses.py` | The pose library (shared with the old sprite rig): feet, hands, weapon direction, lean and twist per clip and frame. |
| `tools\chara3d_sheet.py` | Calls Blender, then turns the passes into pixel art: a four-tone ramp per material chosen by how lit the pixel is, dark outlines around the figure and between parts. `--review` writes a page of poses. |
| `tools\chara3d_all.py` | The batch run over the whole roster, in parallel. |

How a character is put together (`build_character`):
- **Body**: a bare figure in a loincloth, chest wrap and wrist and ankle wraps. Head and hair are scaled about the neck (`HEAD`).
- **Outfit**: a list of layers over the body (`OUTFITS`): `kimono`, `hakama`, `coat`, `obi`, `armour`, `footwear`.
  Each layer is the body's own cross-sections grown outward, so it follows the limbs. `--outfit bare` shows the body alone.
- **Weapon**: its own piece on the `weapon` bone, grip at the bone's origin. A sword also has a scabbard on the hip
  and a hilt on the `sheathed` bone that shows while the blade is put away.
- **Detail is painted, not modelled**: lacing, pleat folds, hems, crests and hair sheen are per-face colours
  (`paint=` or a `band` function), which is what reads at this resolution.
- Colours come from the look specs in `gen_sprites2d.TRAVELERS` and `gen_sidecast.CAST`; `LOOK3D` in
  `chara3d_sheet.py` overrides them per character.

## Commands

```powershell
py -3.12 -E tools\chara3d_sheet.py trav_natsuko --review "idle8:0,fidle:0,atk_thrust:3" --zoom 4
py -3.12 -E tools\chara3d_sheet.py trav_natsuko --review --outfit bare --weapon katana
py -3.12 -E tools\chara3d_all.py --list                       # done / to do at the current builder version
py -3.12 -E tools\chara3d_all.py                              # bake all 349 sheets into _art\preview\chara3d\sheets
py -3.12 -E tools\chara3d_all.py --install --release 20       # install into the game, test, push every 20
```

A sheet takes about 50 seconds per worker (211 frames). Progress is in `tools\chara3d_done.json`, keyed by a hash of
the builder, pixel pass and pose library, so changing any of them re-bakes everyone on the next run.
`--install` rescales each registration so the finer sheets (1.4 sprite pixels per model unit, 292x256 cells) keep
their world size. `--release` runs a real battle before each push.

Blender: portable 5.3.0 under `%LOCALAPPDATA%\Programs\Blender\` (or set `BLENDER` to the exe).

## Known gaps

- Faces, hair and cloth are simpler than the reference art; armour and robes need more shape and trim.
- Kneeling poses crumple skirts and coats; some raised weapons leave the cell.
- Hats, helmets, masks, beards, haori coats and most props are not built yet; only spear-like, sword, bow and
  club weapons have models. Non-human foes have no model.
- Installed sheets have not been checked in the field, only that a battle runs.
