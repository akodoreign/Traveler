# Voxel characters: skinning a cast member onto the engine's 3-D rig

The lofted, art-projected 3-D Natsuko (`tools/model3d.py`, `tools/blender/build_chara.py`) is
**scrapped**. Its face could not be made clean. Characters are now skinned the way RPG-Cobo itself
builds 3-D people: as a MagicaVoxel `.vox` file of rigid parts that ride the bones of a stock
`.mot` skeleton. Hiruma Natsuko (`CV100`) is the first one.

## 1. How the engine builds a voxel character

| Piece | Where |
|---|---|
| Entry (`vox`, `mot`, `pal`, `colsize`, `vox_itemr`/`vox_iteml`) | `resource/chara_vox.json` (`CVnnn`) |
| Builder | `RPG3DVoxChara` in `src/rpg/RPG3DObject.sk` (`setCharaVox`, `setEquipVox`, `updatePartsVisibles`) |
| Skeletons + motions | `resource/mot/leg2_woman/woman_{1,2,3}.mot`; Blender sources in `_tools/rpgcobo-tool/work/mot/leg2_woman/*.blend` |
| Weapons | `resource/equip_vox.json` (spears `EV007`, `EV012`, `EV013`) |

* The `leg2` skeleton has 12 bones: `hip`, `leg_L/R`, `body`, `arm_L/R`, `hand_L/R`, `item_L/R`, `head`, `face`.
* A `.vox` has one model per part, named in its nTRN node. The names are `head0`, `face0`-`face3`,
  `body0`, `arm_L0`-`2`, `arm_R0`-`2`, `leg_L0`-`1` and `leg_R0`-`1`. Each part is **rigid** on one bone.
  The motion picks a variant per frame through a bone custom property: arm poses, blink and talk faces,
  sitting legs. A missing variant falls back to `…0`.
* The pivot of every variant comes from its `…0` sibling's `_t`. Variants are therefore drawn in the same
  local box as `…0`, even though the editor shows them side by side.
* MagicaVoxel `_t` is the model **centre**, so `world = _t + local - size//2`. Axes: z up, the front is
  -y, and +x is the character's left. One voxel is 1/16 of a unit (`VOX_SCALE`) and 1/16 of a Blender unit.
* `cv.pal` is an optional `[index, packed ABGR, …]` override applied to the file's palette. Leave it out
  when the `.vox` carries its own palette.
* `head0` is drawn with a polygon offset so hair wins against the face block that sits inside it.

Rules that keep a skin fitting the skeleton (not "stretched over" it):
1. **Keep every part's box size and `_t`.** That is what places the part on its bone. To grow a part,
   add an even number of voxels on one side and move `_t` by half the growth. Existing voxels keep their
   world position. Natsuko's `head0` grew 26→34 in y for the ponytail, with `_t.y` 2→6.
2. Draw inside the template's silhouette near the joints: neck, shoulders and hips. Change shape freely
   away from them: hair, sode, obi knot, ponytail. Parts don't deform, so the template's joint overlap is
   what hides the seams.
3. Face blocks `face0`-`face3` share one shell. Only the eyes and mouth differ.
4. Keep bands and trim at least 1-2 voxels thick, and exaggerate the silhouette features that identify the
   character: hair mass, headband and shoulder plates.

## 2. Designing a skin from the art

The workflow comes from voxel-artist practice. See the MagicaVoxel format spec at
<https://github.com/ephtracy/voxel-model/blob/master/MagicaVoxel-file-format-vox.txt> and its
`-extension.txt` companion.

1. Pick the closest stock model as the base. Natsuko uses `woman_soldier.vox` on `woman_2.mot`, the
   model `CV100` already used with only a palette swap.
2. Quantize the reference art (`_art/sources/cutout/trav_natsuko*.png`) to a small palette, about
   3 tones per material: navy, plate, red, gold, skin, hair.
3. Per part, recolour and reshape the base inside its box (section 1). Natsuko's skin includes:
   * hair recoloured to her dark brown, the soldier's visor removed, a red hachimaki with a back knot
     and tails, a high ponytail and side locks
   * the base expressions kept, with tan skin and brown eyes
   * a navy kimono collar with a white V, a lamellar dō with red lacing and gold edges, a red obi with
     a knot, and kusazuri
   * arms coloured by distance from the shoulder: sode, sleeve, red cord, laced kote, then the hand
   * legs: hakama, suneate, tabi and waraji
4. Check the result on the real skeleton in Blender (section 3), adjust, and repeat.

## 3. Tools

| Command | Purpose |
|---|---|
| `python -E tools\voxskin_natsuko.py` | Rebuilds `resource/vox/chara/trav_natsuko.vox` from `woman_soldier.vox` (deterministic). |
| `tools\voxfile.py` | Lossless `.vox` reader/writer (`VoxFile.load/save`, `.model(name)`, `.trans`, `.set_translation`, `.palette`). |
| `blender -b _tools\rpgcobo-tool\work\mot\leg2_woman\woman_2.blend --factory-startup --python tools\blender\vox_fit_render.py -- <skin.vox> <out_dir> [frame …]` | Swaps every template part for the skin's voxels, copies the nearest template vertex weights, lets the motion's drivers pick variants, and renders front, 3/4 and back PNGs per frame. |

Use `woman_1.blend`/`woman_3.blend` for skins on those motions.

## 4. Installing Blender (Windows, no admin)

Blender is only needed for the fit check and the `.blend` motion sources; the game does not use it.
1. Download the portable zip `blender-5.3.0-windows-x64.zip` from <https://www.blender.org/download/>,
   or from the release folder at <https://download.blender.org/release/>.
2. Extract it to `%LOCALAPPDATA%\Programs\Blender\`. That gives
   `C:\Users\<you>\AppData\Local\Programs\Blender\blender-5.3.0-windows-x64\blender.exe`.
3. Check it with `blender.exe -b --factory-startup --python-expr "import bpy; print(bpy.app.version_string)"`.
4. Run scripts headless with `blender.exe -b <file.blend> --factory-startup --python <script> -- <args>`.
   Blender's bundled Python already has numpy, which `tools\voxfile.py` needs. Scripts add `tools\` to
   `sys.path` themselves.

## 5. Using it in game

`CV100` now points at `trav_natsuko.vox` on `woman_2.mot` with `vox_itemr: EV007` (spear). The old
palette override was removed. Party member `P100` still walks as the 2-D sprite `EP200`. Switching
her to the 3-D model is a separate opt-in. To skin another cast member, copy
`tools\voxskin_natsuko.py` and choose the closest base model and motion.
