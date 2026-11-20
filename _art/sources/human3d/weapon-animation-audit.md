# Traveler weapon animation audit

Reviewed the native item registry, equipment and motion routing, and the existing daylight footage for Rensei, Natsuko, and Tamotsu. The footage shows overall timing and silhouette. Close contact and clearance findings below identify the frames for supervisor review. The recommendations concern the game's prop geometry and authored poses.

## Kakita recovery candidate

The staged script and bank are under `source/kakita_void.py` and `assets/kakita_void.mot`. Their destinations in the Traveler worktree are `tools/blender/kakita_void.py` and `_tools/rpgcobo-tool/project/resource/native_chara/kakita_void.mot`.

- Rensei (`trav_rensei`, P101) reaches this bank with any live katana or Kakita weapon. Start review with W100 and W131, then spot-check W130 and one other katana. The base ranges remain frames 0–60 and 61–121 at 30 fps.
- Frames 23–29 start the return after the cut, turn the blade toward the fitted scabbard, and move the sword hand to the same bind-space socket as the parked hilt. Frame 30 returns to the parked mesh. The hand briefly stays on the hilt and then settles. For the hatted bank, add 61 to those frame numbers.
- Review the scabbard mouth and lower tip from both oblique sides on frames 27–31. The sheathe uses the authored transition and the shipped blade/scabbard meshes, whose shape differs by item. Watch for a residual tip or overlap to the rear. Check the hatted gesture and the no-hat turnaround at normal speed.
- The bank exported successfully. No gameplay tests or live worktree edits were performed. This candidate addresses the recovery. The initial special draw and ordinary `iai` draw each still need their own continuity pass.

## Priority order and other equipped families

| Priority | Native items and motion route | Findings and supervisor review |
| --- | --- | --- |
| 1 | Kakita W130, W131 and katana W100, W110, W121, W134, W139, W143, W148, W151, W156, W157, W158. Rensei uses `iai` and dedicated `kakita_void.mot`. Other wearers use `blade`. | The special's hand and mesh had a hard switch at recovery. The staged candidate addresses that transition. Review standard blade guard and movement separately, with a side angle on both hands and any sleeve or scabbard intersection. Ordinary `iai` uses a different visibility transition and its animated support hand target moves relative to a still pelvis-bound scabbard. |
| 1 | Yari W101, W111, W116, W122, W123, W127, W128, W138, W152. Shared `pole` route plus Natsuko's dedicated `spear_void.mot`. | W101 uses a wearer-fitted spear. Preserve the fast airborne rotation. Review the guide hand during catch and the next three frames, approximately 47–56% of the special. It deliberately opens during the spin. At regrip, the authored target follows the shaft but the arm reach clamp can pull the palm away. Review shared ready, run and the end of normal thrust for the same gap. Constrain the held segment during contact, with a reach margin before locking the guide hand. |
| 1 | Yumi W104, W114, W132, W135, W149, W153. Shared `bow` poses. | Keep the current fitted Tamotsu scale. Native items bind to the rigid weapon bone. The authored draw hand travels toward the cheek, while the native weapon pose does not consume the old sprite `weapon_draw` flag. Start W104 by giving the visible string a center point that follows the draw contact between the fixed end anchors, then let the center return at the existing release marker. Audit bow hand, string, and sleeve in the same view before propagating to every fitted item. |
| 2 | Tetsubo W103, W113, W117, W120, W125, W126, W129. Shared `club` route. | The authoring pass varies support-hand separation by load and contact. Check the fitted wraps for both palms during ready, load and the end of the follow-through. Compare the whole torso, knees and weapon silhouette during load and recovery. Review the overhead path with each hat and bulky armor sleeve present. |
| 2 | Tanto W102, W107, W112, W124, W133, W137, W140, W145, W147, W150, W155. Shared `short` route. | The general `short` family inherits the same roll pass as blade swings. Use a view that exposes the short fitted handle to check palm and fingers during idle and draw. Keep the free hand and blade separate from costume seams. Inspect visibility on the first and final draw frames. |
| 2 | Naginata W161, bō W105, W115, W144, W154 and shakujō W141. Shared `pole` route. | All three inherit the yari grip offsets and attack poses. Check shaft ends and fittings against headwear, body and ground through guard, run and recovery. Separate the visual timing of these item silhouettes where shared poses obscure their distinctive ends. |
| 3 | Bokken W136, kama W146, and musket W142. Dedicated `combat_bokken`, `combat_kama`, and `combat_musket` banks. | Check the bokken in recovery as an exposed prop. Use side views of the kama to reveal the short handle and prevent the head from merging with the opposite sleeve. Check musket carry, aim and recoil for consistent receiver and support-hand contact, shoulder clearance, and a readable prop silhouette. |
| 3 | Claws W159, W160. Shared `fist` route with two hand-bound meshes. Unarmed W106 uses the same family. | Each claw mesh already follows its own hand. Review whether fingers and knuckles read through both mounted meshes, and whether the mirrored silhouette stays clear of the cuffs. |

The registry also lists custom fan and nunchaku banks. The inspected live native item table has no item using either kind. If a skill equips one separately, review that skill's prop and its own motion event.

## Rig review

- `tools/blender/chara3d.py` solves a primary hand to the pose and an optional support hand to a point along the weapon. The two-bone reach limit can leave the support hand short. Measure grip-to-axis separation after solving, and use the fitted item's wrap interval to assess contact.
- Wrist and finger frames mostly inherit the arm or hand pose. A palm socket alone does not make a convincing hold. Put an open-palmed release, a moving guide hand, and each closed hold into the visual comparison.
- Runtime prefers the actor-fitted equipped mesh. Review the actual item with the intended body and costume on a daylight map. Inspect ready, movement, anticipation, effect contact and recovery. Check the ordinary and special motion separately where they use different banks.
