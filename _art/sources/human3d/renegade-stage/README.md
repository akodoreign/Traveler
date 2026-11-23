# Shosuro Renegade

All three Shosuro Renegade enemy IDs, E227, E561 and E951, share native model EP427. The previous cave pass bound EP427 to the regenerated female body, upright Shosuro Shiko portrait and fitted W124 tanto. The older mask still covered the face and visually dominated the model.

The new ivory Noh mask uses a separate watertight shell fitted to Shiko's exact native head. It has the original dark high brows and narrow red mouth, plus real apertures for both eyes. It follows the shared skeleton's `head` joint. The hair and underlying face retain their accepted shapes, and the neck keeps its fitted overlap at 99.2375 and 99.925 native units. The prepared mask is available as `ep427_renegade_noh.glb`.

The matching body descriptor uses Shiko's sampled albedo of sRGB 244, 199, 178 and the accepted native color `0xe79474ff` across core, hands, neck and throat. The generated A120 Scorpion Silk Armour keeps its folds, normal map, dark hems and original gold trim. Its new crimson atlas restores a small woven diamond pattern. Width 1.10 gives the existing shared female body and armor more room across the torso and hips.

The independent sash, W124 tanto, 50-joint rig, existing attack bank, enemy IDs, encounter positions and damage behavior are preserved.

| Enemy | Existing encounters |
| --- | --- |
| E227 | Base enemy alias retained in enemy data. Its encounter clones share EP427. |
| E561 | M437 encounter 3 → M894 |
| E951 | M437 encounter 7 and encounters on M471–M474 and M482–M486 |

## Apply and verify

Run `python -B install_renegade.py <tool-directory> --check` to verify the target. Rerun without `--check` on a closed profile. The installer edits only EP427 in the two registries, copies its matching body descriptor and adds the four mask and dye assets.

Evaluate `renegade_foe_proof.sk` from M437 for the M894 route with E561 and E951. Starting elsewhere queues all three aliases in daylight on M811. Evaluate again after combat loads. The fixture verifies the actual masks, dye, skin, joints, weapon and attack bank. Inspect the eyes and mask by the temples in front and strict-side views.

The [bind-space preview](renegade-bind-review.png) shows the prepared front and side fits. `fit-check.json` records the exact head hash, aperture coordinates and mask clearance. On the native mask, 18,446 vertices follow `head` with a minimum forward clearance of 0.135 native units. Both eye openings pass the offline visibility check. Native daylight review is the remaining step.
