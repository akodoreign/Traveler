
# Cloth layering and decals

The audit covers all 22 equipped native body and cape routes, both shared body templates for cross-equippable pieces, all 451 actor default records, the seven unique signature meshes beyond those equipped routes, and all 12 Shosuro Mitsue outfit records. Hiruma's A173 uses the same mesh as the shared item and has its own wearer atlas and mon.

## Staged repairs

| Priority | Route | Change |
|---|---|---|
| 1 | Togashi Yosai, starter A111, side_yosai_signature | The source specifies closed boots. The shared body foot protrudes through the toe and outer sole. Live V2 is cloth-review/yosai-boot-weights/native_tailoring/side_yosai_signature.mdl. Root verified the fit and same-side boot weights in four daylight stance and walk contacts. The fit preserves the body, UVs, textures, decals, wraps, and visible tattoo opening. V1 remains available as the geometry-only rollback. |
| 1 | All nine travelers in generated bodies, including Mitsue A180–A187 and A189–A192 | The runtime adds a separate older sash on top of the generated garment's integrated belt. On current Rensei, Gendo, Yosai, and Mitsue signatures this places a second dangling shape across the knot or nearby skirt. The installed cloth-review/player-tailoring-sash.patch skips the extra player sash when a generated body outfit was mounted. Preserve fallback sash registration, Yosai ink, and the generated waist details. Root verified Rensei, Mitsue Fox, and Yosai in daylight. |
| 2 | A124 Asahina Robes, A167 Robe of the Five Rings | The deep cuff mouths sit beside broad skirts. At neutral three-quarter view the hand generally exits behind the bell cuff, with a small sliver at the outer rim on A124. Capture raised forearm, delivery and recovery before fitting. Local weight transfer on the rolled cuff or a small shell clearance is appropriate if the sliver turns into a penetration. |
| 2 | Mitsue A182/A186 Fox Household Kimono and A189/A191 Castle Records Clerk Robe | Compare the Fox red obi and folded ivory lining against the separated garment views. The reinforced Fox cuff nearly hides the near palm at rest, and the reinforced Clerk sleeve has a long loose edge adjacent to the skirt. Check bend and reach from both sides and retain their intended drape. |
| 2 | A125 Sailor's Oilskin | Separate cape model attaches over the current body armor. Check cape contact under raised shoulders on A100 and under the bulkier A173/A141. The contact sheet uses A100 as the underlayer. |
| 3 | Mitsue A180/A184 Shinobi, A181/A185 Maid, A183/A187 Soldier, A190/A192 Pilgrim | Keep the mask and capelet as authored. Check Shinobi close sleeves on flex, Maid cuffs and apron on reach and walk, Soldier plate-to-cuff transitions on guard, and Pilgrim capelet/loose tabs on arm raise. Fox tail and costume headwear are distinct attached accessories to include in the root capture. |
| 3 | Kitsuki Gendo signature, Kakita Rensei signature, shared A153, mixed A109/A168/A173 | Current Gendo garment-only crop shows open cloth cuffs and no duplicate hand geometry. Validate hand visibility in the book and glasses fidget. Rensei's collar uses the deliberate showThroat setting. Check obi contact during the bow, the mantle and wide sleeve on A153, and arm/skirt transitions on the mixed armors. |

## Geometry and material findings

- All 21 generated body item records and all 12 Mitsue body records hide the shared core and wrap when equipped. The cape is an outer layer. Of 451 actor defaults, Yosai is the single full-core exception for the cutouts and chest tattoo. Kakita's default keeps the throat material for the V-shaped neckline while the rest of the core is covered. Core intersections elsewhere can still arise on an actor falling back to legacy body gear.
- The garment materials render opaque. Separate decal models use alpha cutout on UVs projected to the garment faces. A pale strip that appears in the garment-only cuff view is the material of its lining. A coral shape that appears only after the body layer is enabled belongs to the shared hands or body. Several rear and profile flags come from wrists directly in front of a skirt and need no fix.
- The waist sheet isolates the older sash mesh. Its overlap persists when all decal sheets are hidden. The one-line player-loader change addresses the duplicate mesh layer while keeping the integrated knots, ties and waist hardware.
- Waist ties, folds and sewn lower panels normally share the garment's mesh. Their movement depends on the existing drape and obi controls. For a reproduced collision, transfer local sleeve or tie weights or adjust garment clearance with the shared body frozen. Keep softer surfaces flexible and keep the rigid section weights on their existing plates. Regenerate the dependent decal projection only if the surface carrying it is moved.
- Yosai front and opposing three-quarter bind-space authoring views show exposed-foot area reduced from 6,397/9,433/5,666 pixels to 0/22/10. The residual is a tiny sole edge trace. Companion file yosai-boot-fit/yosai-boot-fit.json records the installed-source and staged SHA-256 values.
- Shared armor plate trim, studs, approved outfit colors and clan marks stay installed as authored. The cloth audit contains no recolor proposal.

## Source and review files

- outputs/cloth-layer-contact-review.png 
- outputs/mitsue-cloth-layer-contact-review.png
- outputs/cloth-cuff-layer-detail.png
- outputs/cloth-waist-layer-detail.png
- outputs/yosai-boot-layer-preview.png
- cloth-review/cloth-layer-observations.json
- cloth-review/decal-alpha-observations.json
- author_cloth_layer_review.py, author_cuff_contact.py, author_sash_contact.py and fit_yosai_boot_toes.py

The contact sheets use installed garment geometry in bind pose. The finer cuff sheet isolates the body hands, and the waist sheet separates the extra older sash. The root live checks cover Yosai V2 and the sash guard. Motion review for the other cuff and skirt priorities and the optional A153 decal fit remains with root.


## Decal projection and follow-up

The 284 resolved sheets were reviewed at both visible and fully opaque alpha. No fully opaque Mitsue artwork crosses its garment silhouette. Reinforced Maid A185, Clerk A191 and Pilgrim A192 each show one partially opaque edge sample at 3 pixels per model unit in the profile view. Their existing decals are retained. The leading shared profiles are A116 Kaiu Lamellar, A153 Tamori Ward-Robe and A108 Crab Plate.

A153 has a separate candidate at cloth-review/ward-robe-dense/seat-0.06/A153_decal.mdl. The front and back grids sample 24 divisions instead of 12, use barycentrically interpolated garment normals and weights at each hit, and sit closer to the existing cloth. The same 12 clan atlases, alphas, UV registration, and A153_decal.pm descriptor are used. At 9 pixels per model unit the aggregate overflow across the two opposing profile views drops from 1,088 to 242 pixels. The Lion front photograph has a visibly intact mark, front aggregate area stays at about 98 percent, and rear coverage stays effectively unchanged. Preview outputs/tamori-ward-robe-decal-clearance.png. Root can copy only A153_decal.mdl and roll back by restoring the current file. Check both profile views and bend recovery before adopting this projection on A116 or A108.

The Yosai signature geometry-only pilot was followed by a local boot-weight pass after motion showed the ankle escaping. Original soles had average 13.53 percent and 18.34 percent opposite-leg influence from the skirt blend. V2 follows the shared male same-side foot and shin weights through the boot and eases into the original trouser weighting through the calf. No body masking was needed. Root's daylight recheck confirmed both closed boots through stance and mid-step. Root verified the installed sash removal preserved Yosai's ink and Mitsue's fox tail.

