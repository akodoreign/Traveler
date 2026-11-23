# Smooth Traveler furniture

The screenshot shows the damaged shoji panel in the Shiro Iuchi storm room. It used a voxelized version of a textured mesh. The replacement uses a new continuous textured Hunyuan mesh with cypress rails and torn paper. Three widely reused storage props and the broken Shadowlands cart receive the same treatment.

| Original placement | Replacement | Placements |
| --- | --- | --- |
| iuchi_storm_broken_frame | smooth_iuchi_storm_shoji | 11 in M412 and M882 |
| hoshi_trade_chest | smooth_hoshi_trade_chest | 11 |
| hoshi_storage_jar | smooth_hoshi_storage_jar | 26 |
| salt_crate | smooth_coast_salt_crate | 17 |
| shadowlands_broken_cart | smooth_shadowlands_cart | 2 in M174 and M458 |

The intended scope is 67 decorative placements on 21 maps. All new props fit the original measured width, height, depth, and floor pivot. The installer uses the current manifest, changes only the prop key, and retains every placement coordinate, scale, rotation, and animation value. Native geometry and event catalog files are used for isolated verification. Publication installs the tested art and manifest rows while preserving the live map collision, portals, catalog, and existing asset files.

## Reproduce and check

The four-piece furniture batch uses the existing Coast kit environment and its ComfyUI services. Run `queue_smooth_furniture.py` from the Coast kit, wait for all four Hunyuan GLBs, then run `install_smooth_furniture.py fit <worktree>` from the same directory. The `fit-proof.json` file records each source, exported bounds, triangle count, and native file hashes. Source filenames and prompt receipts are named for these four props.

Run `install_smooth_furniture.py stage <worktree> --profile <idle-profile>` with the fit-proven bundle. Suggested native checks are M412 and M882 for the shoji, M122 for the chest and jar, and M415 for the crate. Follow up with the same command using `publish` once the staged art is reviewed. Use `--only <original-key> ...` for a partial tranche. If the shoji is installed first, stage and publish the three still-legacy keys together.

## Broken Shadowlands cart

The cart uses its original clean Comfy reference for the fresh Hunyuan mesh. The faded vermilion cloth and dark cedar body retain the prop’s color cues. The two road placements keep their 2.02 × 1.07 × 1.12 m base footprint and their existing transforms. The isolated stage, fit, and publish commands accept `--only shadowlands_broken_cart`. The mesh job receipt is in `sources/shadowlands-cart-job.json`. Replay M458 or M174 to check the fitted prop.

If a map is rebuilt later using the old art recipe, reuse the finished models by carrying over the same single-key substitutions.

## Native review

The five smooth prop meshes are installed across 21 maps, with 67 placements. The storm room and arena, Hoshi goods room, Cakon harbour, watchpost, and Fallen Road passed native daylight review. The two cart placements retain their original scale, yaw, and position.
