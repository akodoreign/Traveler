# Akodo Gusai duel fit

Both duels referenced EP834. Its shared male body still used the old face, skin colors and weapon, while Gusai's field and party appearances use EP554 and the regenerated `side_gusai` actor.

| Appearance | Runtime route |
| --- | --- |
| Story events | EP554 → `side_gusai` on M240 event 1, M245 event 6, M273 event 14 and M274 event 21 |
| Companion | P127 → EP554. Gear follows the equipped item. |
| Barracks duel | M001 encounter 51 → E351 in M834 → EP834 |
| Camp duel | M001 encounter 68 → E389 in M833 → EP834 |

The two duel entries now use `side_gusai_portrait_face`, the exact portrait previously fitted to the production neck socket. The recorded face albedo was sRGB 198, 142, 105. The calibrated skin target was sRGB 196, 143, 109 and the existing accepted body descriptor uses `0x8f4727ff` for core, throat, neck and hands. The source and fit metadata are in the worktree under `_art/sources/human3d/cast_heads/side_gusai_repaired_atlas.glb` and `side_gusai.json`. The fitted face positions and weights are reused as exported.

The duel wears the approved A135 Lion armor variant, its Lion decal, the original separately bound sash and a regenerated W100 katana. Gusai remains bareheaded during both duels. Width 1.055 uses the geometric mean of his field appearance’s horizontal proportions. Height 1.036 uses his approved humanoid profile. The enemy data, animation bank, story, equipment inventory and field registrations stay intact.

## Installation and verification

Run `python -B install_gusai.py <tool-directory> --check` to verify the target dependencies. On a closed profile, rerun without `--check`. The installer changes only the EP834 entries in the human and tailoring manifests plus `native_human/EP834.pm`.

Evaluate `gusai_field_proof.sk` after the original field event loads. M245 event 6 is available early in the barracks. For `gusai_duel_proof.sk`, evaluate once from M245 for the barracks arena or from M274 for the camp arena, then evaluate again after combat loads. Other starting maps send the E351 duel to M811 for daylight review. Look for `[GUSAI FIELD FIT]` and `[GUSAI DUEL FIT]` in the game log.
