# 3-D-backed pixel-art characters

Every human character is one skinned vertex mesh on an armature, built and posed in Blender, and rendered
at sprite resolution into pixel art. No frame is drawn: a new outfit, weapon or animation is a change to the
model or the pose numbers. This replaces the voxel skin (`docs/VOXEL_CHARACTERS.md`) and the 2-D cutout rig.

The offline sheets are art previews. The game uses native weighted meshes for the human base looks
listed in `project/resource/native_chara/roster.json`. Actors outside the index retain their existing visuals.

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
  Fitted sections share the body's cross-sections and bone weights. Robes have open fronts over divided hakama, and the shoulder plates ride the upper-arm bones. `--outfit bare --weapon none` shows the underwear and wraps.
- **Weapon**: its own piece on the `weapon` bone, grip at the bone's origin. A sword also has a scabbard on the hip
  and a hilt on the `sheathed` bone that shows while the blade is put away.
- **Detail is painted, not modelled**: lacing, pleat folds, hems, crests and hair sheen are per-face colours
  (`paint=` or a `band` function). Brocade repeats in garment space and deforms with the fabric.
- Colours come from the look specs in `gen_sprites2d.TRAVELERS` and `gen_sidecast.CAST`; `LOOK3D` in
  `chara3d_sheet.py` overrides them per character.

## Commands

```powershell
py -3.12 -E tools\chara3d_sheet.py trav_natsuko --review "idle8:0,fidle:0,atk_thrust:3" --zoom 4
py -3.12 -E tools\chara3d_sheet.py trav_natsuko --review --outfit bare --weapon katana
py -3.12 -E tools\chara3d_all.py --list                       # done / to do at the current builder version
py -3.12 -E tools\chara3d_all.py                              # bake all 349 sheets into _art\preview\chara3d\sheets
py -3.12 -E tools\chara3d_native_all.py                       # export native bodies, outfits, weapons and shared motion
py -3.12 -E tools\chara3d_native_all.py --check               # check asset inventory and registry against game data
py -3.12 -E tools\chara3d_gear_all.py                         # export shared gear and wearer texture atlases
py -3.12 -E tools\chara3d_gear_all.py --check                 # verify the wearable catalog, meshes and textures
py -3.12 -E tools\test_native_gear.py                        # test live equips, clan colour and unequipping
py -3.12 -E tools\chara3d_victory_all.py                     # build inventory meshes and victory motion banks
py -3.12 -E tools\chara3d_victory_all.py --check             # verify the weapon and dance catalog
py -3.12 -E tools\test_native_victory.py                     # exercise weapon changes and victory playback
py -3.12 -E tools\test_chara3d_native.py                      # export and play the native Natsuko test in Pleasant Eaves
```

A sheet takes about 50 seconds per worker (211 frames). Progress is in `tools\chara3d_done.json`, keyed by a hash of
the builder, pixel pass and pose library, so changing any of them re-bakes everyone on the next run.
`--install` rescales each registration so the finer sheets (1.4 sprite pixels per model unit, 292x256 cells) keep
their world size. The legacy `--release` battle check does not verify each installed character or equipment
variant; do not use it as acceptance for a roster rollout.

Blender: portable 5.3.0 under `%LOCALAPPDATA%\Programs\Blender\` (or set `BLENDER` to the exe).

## Native engine

`tools\blender\chara3d_native.py` exports weighted `.pm`/`.mdl` pieces and shared `.mot` files by
animation family. `RokuganNativeChara.sk` keeps ordinary actor timing, equipment look selection,
collision and picking, and supplies skeletal transforms to the meshes instead of displaying the
sprite. No sprite frames are generated for native actors. Bodies, outfits and weapons bind to the
same skeleton.

Native idle loops end before the walk cycle so characters keep their feet planted while breathing.

Native visuals start at 75% of their original scale. Togashi Yosai, Hiruma Natsuko, and Ide Tamotsu
are the tallest travelers, in that order. The roster uses authored height, width, build, age, and
size where available, with small, stable height and frame differences for unspecified looks.
Costume variants of the same person share proportions. Equipment follows the same transform;
interaction bounds are unchanged. Run `tools\chara3d_native_all.py --index-only` to refresh
proportions without rebuilding the meshes.

Native skin colors use cheek midtones from each character's dedicated neutral dialogue bust,
tempered by the authored body palette so painted highlights and shadows do not carry over in
full. Characters without a usable dedicated reference keep their authored color. Run
`tools\chara3d_native_all.py --bust-skin` to refresh matched bodies without re-exporting animations or gear.

Travelers and story companions get their starting equipment from `STARTER_WEAR` in
`tools\gen_data.py`. Weapons stay tied to each character's story loadout. Native characters
with starter armor use the wrapped base body when their body slot is empty; helmets and masks
follow their own slots. Squeak still uses his legacy model. Existing saves keep their loadouts.

## Equipped clothing

`tools/gear_catalog.py` maps armor IDs to shared body garments, headwear, masks, and the oilskin cape.
The game resolves worn item IDs when creating a native field leader, follower or battle actor. Clothing
meshes use the body’s existing rig. Robes, armor and hats reference the wearer’s UV atlas, based on
their clan and original character palette. Materials such as jade, wood and straw retain their finish.
The same item geometry is reused across wearers. With an empty body slot, the character wears their
original everyday outfit.

Each wearable also has a transparent 128 × 64 decal sheet for every clan palette. Each sheet
contains a primary emblem and a secondary mark. The exporter projects the marks onto two
surfaces per item, such as the chest and back of a robe or the crown and front of a jingasa.
The decals use the garment’s bone weights. Unaffiliated wearers use stitch marks. Sheets are
in `project/resource/native_gear/decal/<clan>/<item>.png`.

New wearable armor IDs need a design in the catalog. Run the gear exporter after adding a design or
changing a character palette. Assets are stored in `project/resource/native_gear`.

## Weapons and victory

The inventory weapon ID selects the mesh, so weapons of the same type can have different grips,
fittings, and materials. Unarmed attacks and hand weapons have their own visible states. Existing
combat motion families are shared where appropriate, with dedicated carry and combat tracks for
the musket and weapons that cannot be sheathed.

Each native actor has a victory clip for their authored weapon, and playable native actors have
clips for the weapon types they can equip. Weapon-specific grips and flourishes are combined with
character footwork and finishes in `tools/victory_poses.py`. The eight travelers have authored styles.
The victory sequence uses the currently equipped weapon and the same body rig as combat.

## Known gaps

- Cloth follows the skeleton through authored weights. It has no cloth simulation.
- Kneeling poses crumple skirts and coats; some raised weapons leave the cell.
- Native lighting does not yet match the offline pixel-art treatment.
- Nonhuman characters and legacy sprite looks outside the native roster use their existing art.
