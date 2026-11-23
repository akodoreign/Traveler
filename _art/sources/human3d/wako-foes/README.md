# Wako and neighboring Ronin foes

E539 is the Wako encounter in M422 and M888. Its coastal variants E333, E338, E419, and E431 use the same EP417 appearance. The old EP417 shape was visible even on the shared male base because the generic A100 garment hid the torso. The flat-material face, old headcloth and old weapon were still attached over it.

This pass reuses five fitted head and skin pairs with their existing shared male bind. It gives the Wako a broader working build and a fitted shadow-cloth cut in plain blue slate. The combat width runs on the existing rig for the body and cloth, with rigid headwear, face, and weapons. The Wako nodachi and its saya come from the generated sword sources and are re-fitted to the original long-blade dimensions and current weapon, stow and pelvis joints.

| Foe appearance | Fitted portrait | Wardrobe and weapon | Body breadth |
| --- | --- | --- | --- |
| EP417 Wako Raider | Daidoji sailor with fitted hachimaki | Slate A127 and 57-unit nodachi | 1.15 |
| EP404 Hungry Ronin | Sparrow Ronin | Worn A100, jingasa and W100 | 1.03 |
| EP1300 Ikoma Retainer | Lion sergeant | A135 Lion armor, jingasa and W101 | 1.09 |
| EP1301 Retainer Captain | Seppun guard | A109 Lion armor and W110 | 1.17 |
| EP1302 Snake Enforcer | Bayushi guard with fitted charcoal facecloth | Dark green A120 and W100 | 1.08 |

The calibrated donor skin materials are copied onto each foe's own body descriptor. `wako-fits.json` records the original face sample and applied material value. The fit is applied through the existing foe and outfit index entries.

## Install and test

Run the checked installer against an RPG-Cobo tool directory or a closed scratch profile from the workspace.

```powershell
python -E work/human-foes/wako-stage/install_wako.py work/multi-window/profiles/slot-a --check
python -E work/human-foes/wako-stage/install_wako.py work/multi-window/profiles/slot-a
Copy-Item -LiteralPath work/human-foes/wako-stage/wako_foe_proof.sk -Destination work/multi-window/profiles/slot-a/tmp
```

Use `wait,1000|evalf,tmp/wako_foe_proof.sk|wait,2300|evalf,tmp/wako_foe_proof.sk`. A field start in M422 enters M888 with two E539 Wako, one E533 retainer, and one E531 Hungry Ronin. M424 enters M889 with E534, E535, and E536. These fixture entries need no story flags. They verify native IDs, 50 joints, calibrated shared-body materials, armor route, weapons, and attack playback. Use daylight for fit review, especially the fitted hachimaki and the Retainer's jingasa.

The nodachi's native files and textured preview GLB are under `project/resource/native_human`. To rebuild the stage, run `prepare_wako.py` with the worktree path, then execute `export_wako_nodachi.py -- WORKTREE` in Blender Python with the RPG-Cobo Blender exporter available.
