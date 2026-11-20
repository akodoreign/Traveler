# Traveler asset regeneration

## User requirements

Replace every old model with fresh 3D generation. Use Hunyuan3D for the source geometry of people, heads, outfits, hats, masks, weapons, and other visible equipment. Reuse the game rig, attachment points, equipment rules, and item IDs to integrate the new assets. New variants may be fitted or dyed from newly generated source meshes.

Generate exactly two anatomy bases, one male and one female. Use them to derive musculature, weight, chest volume, and stature. Fit the garments with the same controls, fit the separate head at the neck, and then scale the assembled actor. Keep hats, outfits, and weapons independently attachable. Use rounded anatomy and realistic fabric drape at a consistent level of detail.

Use the existing dialogue busts under `_tools/rpgcobo-tool/project/resource/bust` for identity and expressions. Neutral heads and necks stay straight. Tilting belongs in the animation. Gendo's head tilt is specific to his thinking-disbelief expression. Haruki's right iris and pupil move toward screen-left. Retain Kakita Rensei's intended small mark while clearing the Hunyuan artifacts under his eyes. Author separate control channels for blinks, brows, and mouth expressions so the heads can be used for animated emoji.

Generate fresh outfits and surface textures and decal sheets. Use richer clan dyes with clear material differences and recognizable existing crests. Give Shosuro Mitsue's shinobi, maid, fox, soldier, clerk, and pilgrim costumes extra detail. Keep the costumes and reinforced variants exclusive to Mitsue and verify the restriction through gameplay. Fit her accessories and costume headwear separately.

Complete the human and equipment pass before the dedicated animation and Void critical pass. The creature notes contain the Void critical choreography.

## Integrated through the current human pass

- The two fresh anatomy meshes are installed on 349 people and 102 human foes. All eight traveling party members have separate, level portrait-derived heads. The cast reference catalogue maps existing busts to other people. Further cast and human foe head replacements remain in production.
- The 21 standard body clothing IDs and Rensei’s signature starter robe use freshly generated fabric or armor sculpts with clan dyes, normals and decals. Rensei’s waistband clearance was corrected above the obi and the sleeves now follow the cuffs. Default clothing bindings point to the fresh garment library for the cast and human foes. Six more named signature outfits have been fitted and installed.
- All 12 Mitsue costume bodies, including reinforced variants, plus five hats, her shinobi mask and fox tail are installed from fresh source sculpts. The fits and source meshes are archived in the wardrobe folder. RPG-Cobo verified all 12 costume variants, bespoke decals, animated fitting, and exclusive equipment access.
- The 19 standard hats, masks and cape designs are installed from fresh meshes. Weapons and remaining unique cast heads continue through the generation queue. The human and equipment pass is still in progress.

## Neck and stance review

- Keep the original neck proportions on both shared bodies. Refitted all eight traveler heads by measuring the head and body neck centers and translating the entire head on its bind. Use the same alignment method for new heads. Exposed neck color is matched to each face. Rensei’s portrait atlas repair removes the extra mark above his left eye and blends the lower neck. His tailored robe exposes the new throat surface inside the V-neck while covering the body beneath the cloth.
- The new upright idle stance uses balanced toe angles, knee directions and a smaller breathing motion. It is installed on the seven cast banks, five weapon-specific combat banks and all 102 human battle foe motions. A 64-frame joint comparison confirmed that the visible lateral knee imbalance was removed and the sampled non-idle transforms remained identical.
- Rensei’s obi ties follow the belt through the revised stance. RPG-Cobo exercised the new body and head, collar visibility, combat clips, all 12 Mitsue costumes, the exclusive equip rules and a modular human foe. Portable head and fit channels now start at zero.
- Further human heads still need individual neck review as regenerated sculpts replace them. Dedicated combat choreography remains a later pass.


## Body color and clothing fit

- Sample the regenerated head’s cheek albedo and use one base color for the underlying shared body, wrists, hands, neck and throat. The authored per-character samples are in `skin_tones.json`. Outfit materials use separate texture files.
- Seat the heads as complete rigid pieces on the original neck shape. Neutral heads face ahead. Keep Gendo’s thinking tilt in the animation. His corrected crop leaves the jawline intact.
- Capture several angles in idle, walk, guard, and bow before approving a fitted outfit. Gendo’s replacement sculpt has fitted sleeves. Transfer sleeve weights from the underlying forearm. Use blended weights and shared body shape controls for cloth. Anchor loose panels at the belt with a gradual falloff.
- Natsuko’s breastplate follows the spine rigidly at its core and blends along the borders. Additional common armor, Shizue, and two Mitsue soldier fits are staged in `work/armor-rig-stage` for individual review.
- Both shared bodies use separate silhouette guides for the wrists and fingers. Tighten or relax the sleeve fit on the measured arm. The finished hand shape comes from the original fresh body sculpt.


- Gendo’s head uses two measured neck center guides. Their average offset moves the head into place on the existing skeleton. The head atlas now blends the skin under his jaw and down to the collar. His signature coat was regenerated with tapered sleeves after removing the arm-bound mannequin caps proved unreliable.


## Shared humanoid skeleton

- The two shared human bodies now use one 50-bone hierarchy with a pelvis, spine, chest, collarbones, neck, head, arms, hands, finger chains, legs, and the existing prop and hair attachments. `joint_guides.json` records the rest positions in model space. Both bodies carry weights for all 28 finger joints.
- The hierarchy and bind transforms are defined in `tools/blender/chara3d.py`. The Blender and RPG-Cobo motion exporters convert the solved joint positions into parent-relative transforms. Every human shares this topology. Continue using rigid alignment for each separate head and follow the body arm and torso weights when fitting apparel.
- Rebuilt 131 motion banks covering the cast, human battle foes, inventory-specific combat, and victory. RPG-Cobo checked all eight travelers, a town NPC, a human foe, a weapon victory clip, and the fitted Mitsue costume routes.

- The full catalog check loaded each of the 451 human body descriptors with its assigned native motion. It verified the shared joints and skin bindings for all 349 cast models and all 102 human foes. The live field regression also equipped and removed all 40 ordinary garments.

## Generation queue and review

- The serial Hunyuan3D service on port 8189 completed the previous eight-head batch by 10:48 on November 20, 2026. The RTX 5070 returned to idle once the queue cleared. The next eight portrait-derived head jobs and a gaijin musket source are recorded in `garment-queue.json`. Query `/queue` and each recorded job's history for live status.
- Review new cast heads in front, three-quarter, and profile views. A generated bust may carry a patch of its old collar below the chin. Fit the head as one rigid piece, remove or retouch the unwanted collar, and sample the cheek albedo for the shared body's exposed neck and hands. Store successful fit measurements beside the source GLBs.
- Weapon generation uses complete transparent silhouettes. Fit approved source geometry to the existing weapon and hand bones, and to the pelvis and sheathed bones where appropriate. Preserve the inventory IDs and battle motion banks. Keep the imported textures and source GLBs with the fit records.


## Daylight combat animation

- Coast Road battle map M811 is the review fixture. The live game loaded generated Rensei, Gendo, and Kappa meshes and applied an ordinary hit and a Kakita Void hit. The latter used the same combat damage path and returned Rensei to his original position after the passage. The hat and bareheaded animation ranges are separate.
- The native battle stance moves hips, knees, shoulders, and head through a continuous loop with planted humanoid feet. Each actor has a slightly different playback rate. Ordinary movement and attacks use the shared 50-bone bank with a 120 ms pose crossfade.
- Every Traveler has five off-turn fidgets. Props include Ide's pocket watch, Hiruma's map and satchel, and Kitsuki's book. Haruki counts on articulated fingers. The 104 creature rigs and 102 native human foes each have five compatible fidgets. Keep at least ten seconds between gestures for each actor and cancel a waiting gesture when its actor acts or receives an action.
- Build the banks with tools/blender/combat_fidgets.py, tools/blender/combat_motion.py, and tools/foe_fidgets.py. Use tools/blender/kakita_void.py to rebuild Rensei's two Void variants. Continue regenerating all mesh and texture assets. Existing portraits are art references for new heads.

## Verified installs and next models

- Three side-cast portraits have been fitted and installed from new Hunyuan meshes. The cast keys are `side_ryuzoji`, `side_tatanko`, and `side_chihaya`. Chihaya’s human battle picture `EP128` also uses the new face. Each head was rigidly fitted to the original body neck, reviewed across three angles, and given a matching underlying skin tone. The source GLBs and placement measurements are in `cast_heads`. The portable fitted GLBs include distinct right and left blinks, brow raise and knit, smile, frown, and open mouth. Native face-expression animation still needs integration.
- Fifty equipped inventory item IDs are now fitted from 12 new Hunyuan weapon types. Each native weapon is independently attachable, with separate sword hand and sheathed hilt weights on the right bones. The scabbards also use a generated source. Source GLBs and the rebuild plan are in `weapons`. The existing item IDs and motion banks stay in place. The seven tetsubo IDs, and the authored weapon fallbacks on field actors and human foes, still need fresh fitted geometry.
- The eight-head batch beginning with Kafu all exported, and the gaijin musket source exported and was installed as part of the inventory pass. Another six portrait jobs for Eriko, Keiyomi, Akiko, Kasiko, Mutsuye, and Shahai are recorded in `garment-queue.json`. Review live results before resubmitting. As of this pass, 12 of the 451 human model slots use an individually fitted new portrait, including one shared battle alias. The cast reference catalogue has 289 available busts and 60 cast entries requiring new references. Other battle portrait aliases can use the same approved source as their matching story actor where the character is confirmed.

## Actor-specific equipment fits

- Ide's six available yumi have individual fittings with twice the original nock span around the original grip. The original W104 was approximately 52 units and his fitted version is 104. Hiruma's W101 fitting reduces the band near the spearhead while keeping the grip and blade positions. Battle setup looks for a wearer-specific equipped weapon before the general item.
- Seat hats on the skull and keep the brim and exposed hair clear of the eyes. A hat may hide or trim the enclosed section of a strand, bun, or topknot when it prevents a proper seat. Keep a complete uncovered hairstyle. Rensei's A170 and Sayo's A102 use fitted shapes with rigid head weights and existing clan atlases. The optional export_hat_hair.py creates a covered head variant if a future fit requires it.

## Combat presentation review

- Approved the fast two-rotation Hiruma yari Void in the daylight M811 playtest. The model and camera returned to their combat positions. The standard damage path resolved one hit. Ordinary sword, spear, and bow motions also passed the daylight combat test after the next motion polish.
- The Heart Listens uses its original first-turn weakness reveal. Ide opens his arms and a hand-drawn heart rises while his bow rests behind his shoulder. The user approved the live visual. Keep distinct Traveler mannerisms even when skills share underlying animations or effects.

- Song of the Ki-Rin uses its own vocal performance, musical-note effect, and concluding bow. In M811, all three allies received the original Regeneration and Ide returned to his fitted yumi. The shared school catalog records distinct movement and effect notes for all eight Travelers.

- Yosai’s 41-bone tattoo dragon is staged as a native effect, with Summon, Hover, Breath, and Vanish clips. The source GLB, build instructions, and fire socket contract are in `tattoo_dragon`.

## November 20 cast batches

- The 11:33 queue reached zero after Empress, Uji, and Rujo all exported successfully. A low-usage GPU at that point indicates the completed serial jobs. Confirm the current queue and histories before retrying.
- The next eight and the nine additional head jobs are listed in `garment-queue.json`. The nine reframed bust inputs in `reframed_heads` preserve complete chins and longer hair for the portraits whose first crops were too short.
- Uji and Empress are with the rigging pass. Keep Rujo’s intended orange hair tips. His cut-off topknot and contaminated neck need individual review before the fit.

- All eight jobs in the 11:39 batch exported. Seven from the first eight were held for source crop corrections. Kage, Tadaka, Tomeko, Shiruko, Pale Courtier, Himeko, and Miyako now have longer jaw, neck, or hair references and distinct replacement prompt IDs in `garment-queue.json`. Sanro advanced to fitting and is held for collar clearance and upward pitch correction.

- Daiyu passed the source review for the reframed set. The generated mesh retains a complete jaw, neck, and silver hair silhouette. The fit needs collar trimming and matching skin on the shared body. The rigging pass has the generated file and landmark notes.

## Latest daylight approvals

- Yosai's S460 Void presentation transforms him into the rigged dragon at his tattoo, follows the animated muzzle with a continuous field sweep, then restores the monk and camera. The user approved the live sequence. Normal and boosted casts without a landed critical still use the original beam exactly once.
- A Traveler now visibly staggers and falls before the held knockout pose. The approved roll, arm brace, push-up, and stand frames stay identical. Kakita and Hiruma passed the normal Revival Draught check. The Kappa, Giant Hornet, Will-o'-wisp, and Nezumi Shaman defeat clips passed the existing hide check.
- Hiruma's A173 armor and A110 Kabuto use actor-specific dark Crab navy atlases. Light iron-grey markings and hardware and red lacing read in daylight. The original UV layouts and mark alpha carry through. Build the colors with tools/make_hiruma_crab_navy_v2.py and the mark sheets with tools/make_hiruma_crab.py. Keep material and decal review separate from body skin and fits.

- All nine fuller-reference jobs exported by 12:00. Daiyu, Seoko, and Takeo moved to fitted review. Kusuri and Uona showed fused clothing at their long locks during the fit, so the isolated head-only references are queued as separate revisions. Shogen and Toturi also have head-only revisions queued. Keep Bayushi Kei and Kuhime out of the live catalog pending hair-color and lighting correction.
- The corrected Kage and Tadaka sources preserve the previously truncated jaws. The rigging pass has their new GLB paths and collar-trim notes. Keep Kage’s white eyes and both of Tadaka’s braids.

- Deepened Hiruma's warm accents to true red. The first studded pass adds blued-steel fasteners on her A173 plates and A110 Kabuto, and aged brass fasteners on the A141 Antique Do-maru variants. Both armor routes and the Hiruma emblems passed daylight review. The rivet guide projects onto rigid regions of the original fitted UVs. Leave cloth, ties, and padding free of metal studs. See the author_rivet_guides.py and paint_plate_rivets.py tools.

- Haruki's S391 Void Bolt now gathers at his free hand, arcs in lavender to the target, and breaks into rings. Daylight tests covered the ordinary cast and a forced Void critical. Both hit the selected foe while leaving the other untouched. The existing hit callback still owns damage. The spell-flight choreography notes record the reusable element routes.
- First skin review updates are texture-only. Haruki's bright baked cheek patch is reduced to his cheek tone. Gendo's jaw-to-neck band is softened locally. Frontal and angled daylight routes loaded the new atlases and the original neck bindings.

- Gendo's complete head moved −0.65 fore, −1.25 vertical, and +0.15 lateral in native bind coordinates to seat on the body neck. The installed round Blackened Bronze frames are a separate head-bound mesh. The daylight fixture checked the neck, glasses and eye alignment in three views. The portable trav_gendo_separate_glasses.glb carries the final rigid placement and seven expression targets. Use the installed native head atlas alongside this version.

- Corrected the shell of Yosai's closed wrapped boots to clear the shared body foot. The refit kept the robe and tattoo opening as authored. The first shell refit showed some residual clipping during the Coast Road walk. The final mesh also matches the shared body's foot-to-shin weights on each side and blends back into the trousers. Both boots covered the feet in the daylight stance and captured steps.

- The player loader skips the legacy sash for generated outfits with an integrated waist layer. Daylight checks kept Rensei's starter robe, Mitsue's Fox costume and Yosai's signature robe and verified that the Fox tail and Yosai's ink stay attached. See cloth-layering.md for the static audit and pending sleeve and cape motion checks.

- Use padded helmet ties that emerge at the temples, follow both cheeks, cross under the chin above the collar, and end at a small side knot. The current Soldier A183/A187, shared A110 and A160, Hiruma A110, and Gendo A110 meshes use that route. Coast Road captured each of those variants. The headwear setting restores the full original portrait for Hiruma and Mitsue and invalidates the Soldier costume look cache. Rensei's A160-only topknot trim and Shizue's A110-only fringe tuck passed in daylight. The full Rensei head was verified again with helmets hidden. Retain the approved Soldier cords and the previous Soldier-only covered hairstyle. The forehead graft was reverted at the user's request. Close this fringe revision. The eight human foe helmet routes are listed in kabuto-coverage.json.

- Kakita Yuko uses the newly generated side_yuko_portrait_face on the shared female rig. The short neck is skin-matched to her cheek and the collar fragment was removed. Coast Road confirmed her front and oblique appearance and the native neck and finger joints. The source and fit measurements are in cast_heads. Continue from head-generation-continuation.md for prompt status and the latest mesh review.

- Refit all eight rigid human foe helmet routes listed in kabuto-coverage.json on the new A110/A160 source sculpts. Each has a wearer-specific cord and covered-hair layout with its matching crest and palette. All eight passed Coast Road route checks and front, oblique and side inspection. Heavy Infantry and the Crab Shade retained their separate face masks. With helmets hidden, Yosuke and the Crab Shade restored their ordinary face and hair routes.

## Fit the complete character on the shared skeleton

1. Resolve the actor's installed shared male or female body. Load the matching fitted armature and verify all 50 rest joints, parents and transforms against the native mesh. The shared-rig-reference.png guide shows both fitted body templates and the articulated fingers.
2. Use both feet and the pelvis to establish floor and symmetry. Check pelvis, spine, chest, neck and head in front and strict side. Use the clavicles, upper arms, elbows, wrists and fingers for sleeves, hands and grips. Use both hip-to-foot chains for trousers, shin pieces and boots. The shared armature controls all worn layers.
3. Measure two nearby cross-sections of the shared body neck and express their centers in the head bone's rest coordinates. Use the skin ring and the skeleton's forward direction to define the socket. Measure the clean corresponding ring and facing direction on the generated head.
4. Place the whole generated head by mapping its measured socket frame onto the body socket frame at the chosen character scale. Keep the shared body neck in its original shape. Clear source collar remnants only after placing the head.
5. Skin to the same armature. Keep facial geometry rigid on the head joint. Where a narrow overlapping seam has mixed head and neck influence, match the adjoining body weight blend.
6. Attach weapons to the shared grip and stow bones. Match flexible garment weighting to the body and preserve established drape at loose hems and cuffs. Keep armor plates rigid on their supporting segment with movement at the joints and seams.
7. Verify the exported bone mapping and the assembled seam in strict front and side and through a small head turn and nod. Record the axis, ring centers, width and depth. Inspect the full dressed body from front and side at rest and through a stride and guard pose. Check neck, shoulders, wrists, hips, knees, boots and any equipped props. Hold candidates with incompatible neck geometry.

Goro's first daylight fit was pulled for neck alignment. Goro, Togawa, and Iuchi must go through the shared-armature procedure before their next installs.

- Grandmother is the first accepted head from the full shared-armature fit procedure. The fitted face and A100 garment loaded on the verified 50-joint female rig in Coast Road front, oblique, profile, and walk checks. The narrow lower seam shares neck influence with the body. The dark baked nape tint is still visible. Her portable seven-expression mesh and socket measurements are in cast_heads.

- Grandmother's daylight profile showed a tapered rear flap left in the generated head. Isolating the head, the shared body, and A100 located the flap on the head itself. The local head-mesh refit straightened the rear neck outline and softened the dark baked collar tone. Both profiles and six walk frames passed on Coast Road. The small remaining crease at the lower hairline is attached geometry.

## Grandmother replacement, party proportions, and active abilities

- Grandmother's earlier fitted head was retired after the daylight side review. The field actor is on its baseline placeholder while the replacement is prepared. The fresh front-facing reference produced a clean straight lower neck in geometry workflow `c1e65b34-c916-49dd-bdf3-f9e06f058a10`, then the same 20,000-face geometry with paint in `4622ed9a-e6b6-4a2f-93d9-9a5f9b681910`. Both GLBs are in `cast_heads`. Fit the fresh geometry to the female neck socket. Repair the atlas around the eyes and rear crown before a live install. Keep her original gray irises visible.
- All 29 playable human proportion profiles live in `tools/chara3d_native_all.py` and apply to the skinned assembly, including fitted clothes, decals and props. The Coast Road lineup checks Yosai tallest, Natsuko second and Gonta broadest using the same neutral stance, floor, and camera. These adjustments set whole-body depth, stature and breadth. The rest-space body and garment fitting tools remain the starting point for anatomical sculpt changes.
- The active combat presentation audit reconciles 284 selectable skill IDs. `active-ability-coverage.csv` records the route used by each ID. Regenerate the eight rig-family banks per group with `tools/blender/ability_animation/export_spell_motion.py` and `export_school_motion.py` using the second script with `--bank school` and `--bank support`. Pass the repo and a scratch output folder after Blender's `--`, with `spell_profiles.json` copied into the scratch folder. The mark generator writes alongside its profile source. Run it from a scratch copy with Pillow, then install the resulting `efx/rt/ability` and `native_chara/ability` folders under the project resources.

- Togashi Yosai now uses the regenerated upright face on the shared male rig. His final 20% size adjustment held both neck rings fixed. The open robe collar, face-derived body skin tone, and live Coast Road verification are detailed in [Yosai rigging notes](yosai-rigging-notes.md). The local `traveler-humanoid-rigging` skill carries the illustrated full workflow.
