# School and skill choreography

The installed skill and player tables supply the roster and skill routes in `skill-choreography.json`. Build that catalog with `python tools/build_skill_choreography.py` after regenerating game data. It is a design inventory. The first live pilot is the yari Void critical. Kakita's existing Void pass stays in place.

## Playable schools

| School | Signature | Effect and reuse |
| --- | --- | --- |
| Hiruma | Compress into a scout's low stance, leap on a shallow arc, spin the yari twice, then land on the thrust | Cold wind. Share the motion with the Akodo spear branch. |
| Kakita | One clean cut on a low, fast pass, turn, optionally touch the equipped hat, return | Keep the existing Kakita clip. Use the Void cut line only if it helps read the single impact. |
| Kitsuki | Glasses catch light as the actor leans in and points out the evidence | Resolve evidence markers one by one. Share the investigation rig with Ide's spyglass and scout assessment. |
| Akodo | One hand commands the line and closes at the wrist as the party moves into formation | Staggered gold standards on ally positions. Use the yari leap for a compatible polearm attack and the line charge for a sword charge. |
| Isawa | Count out the invocation with the fingers. Each mote converges on one palm, followed by the cast | Element variants change particles, hand release, and target landing. Keep the caster readable behind the seal. |
| Shosuro | Drop low into an offset shadow, come out at the target's flank, and withdraw | Save the silhouette for the reveal. Powder, shuriken, and quick tanto branches share the first two pose beats only. |
| Ide | Open hands, pause for the response, draw an accord with a restrained gold ripple | Recovery and peace skills share the pose. Bow attacks use the equipped bow's actual grip and draw animation. |
| Ronin | Reach down to the medicine pouch and brace the support hand during the toss | Remedy, diagnosis, and field dressing can share the action. Combat techniques use the held weapon family. |
| Hida | Load the rear foot, rotate hips then shoulders, follow through on a full-body tetsubo swing | Compact dust and ground shock ring at contact. Use the same arc for other large two-handed clubs as their grips allow. |
| Matsu | Drop the shoulder into a committed rush, cut through the line, arrest momentum after the cut | Rust-gold afterimage. Use the existing per-target hit schedule for Lion's Charge. |
| Shiba Yojimbo | Catch the attack in a planted cross-guard before returning to ready | A short ember ward aligns with the protected target. |
| Seppun | Stand tall, turn to cover the protected target, and settle into a heel-led guard | Ivory edge light on the same ward rig. Keep the Shield effect anchored in world space. |
| Yoritomo | Rotate into a low shoulder-led sweep, stepping off the back foot | Sea spray for melee, storm variant for casting. Scale arcs to the equipped weapon. |
| Shinjo | Pass through the lane with a draw or a shot, then ride the motion back under control | Use the mounted pass only if a mount is present in that context. Reuse the draw or line charge on foot. |
| Doji | Draw the strokes of `義` with the katana tip in a readable camera plane and close with a diagonal cut | Use one brush tip trail and one strike. Check glyph stroke order and readable orientation in the shot. |
| Tamori | Ground the knees before the palm or staff lifts | Share Isawa's spell skeleton. Use coarse earth fragments and a heavy set-down for stone. |
| Togashi | Tattoo lines wake, then the head and coiled body of an original Eastern dragon emerge from Yosai and rise into a full-width fire sweep | The dragon needs its own deforming rig, jaw timing, and a tracked mouth origin. Reuse the current breath sweep path for visuals. The Void hit follows existing targeting. |

## How each Traveler performs

| Traveler | Posture and tempo | Hands, props, effects and finish |
| --- | --- | --- |
| Hiruma Natsuko | Gaze scans before the body moves. Keep her low and alert, with quick, quiet landings and a balanced ready stance. | Read the lane, shift weight into the yari and use the map and satchel when a scouting skill needs them. Razor's Edge closes to a narrow, mobile silhouette. Her Void leap spins the yari twice, points the tip, and lands on the hit. |
| Kakita Rensei | Restrained and upright before a sudden, precise cut. Draw power from one committed step. | The sheath hand works first. Let a thin Void line mark the single cut and allow the optional hat-brim gesture its own beat. Keep the finish composed. |
| Kitsuki Gendo | A small turn of the head is the start of a deduction. Use the briefly skeptical pose when the evidence changes. | Glasses and book give the hands a purpose. Read the foe from the page, look up, settle before closing it. Bring that same discipline to the two hands in a Mirumoto action. |
| Akodo Shizue | Centered, proud and certain. Set the feet first and deliver orders with clean angles and a firm voice. | Keep the command signal short. Use staggered gold standards to show party formation. A charge keeps the chest high until the committed forward lean, then finishes in a planted guard. |
| Isawa Haruki | Think through a count before casting. The head and wrist settle, then confidence arrives with the spell release. | Finger counts summon one mote at a time. Keep Water fluid, Earth low and heavy, Fire abrupt, Air light, and Void quiet. Let the counting action resolve before the element takes over the frame. |
| Shosuro Mitsue | Deliberate stage timing. The eyes and leading shoulder sell a false beat before the actual attack. | Gloves, sleeves and available outfit accents make the action believable. Powder blooms at the aim point, and the blade disappears from view only as she returns the hand. |
| Ide Tamotsu | Open chest and warm gaze. Have him include the room and take a performer's breath before a longer phrase. | The Heart Listens opens both arms and releases a rising rose outline. Song of the Ki-Rin uses a high conducting hand, a rhythmic hand at his chest, small purple-gold notes, and a poised bow. The bow comes to rest behind his shoulder for both. |
| Sayo | Compact, grounded movement and calm confidence. Give her the patience of someone who has mixed remedies in poor weather. | She finds the pouch by touch, holds it steady and follows through with the working hand. A theft is quick and understated. A field dressing ends with a deliberate check of the recipient. |

## Ide performance hooks

- Insight Rank 2, S724, runs through the existing first-turn reveal. The 1.4-second open-arms motion opens into a cartoon heart that traces and floats for 1.05 seconds.
- Song of the Ki-Rin, S543, uses the existing voice ability. The performance is a sung Unicorn tale. Its separate 1.7-second pose rises from a deep breath into a one-handed phrase and a finishing bow. The small note effect follows Ide while the stock regeneration still goes to all allies.

## Shared effects and motion routes

| Catalog route | Blocking and timing |
| --- | --- |
| `blade_cut`, `short_lunge`, `kakita_pass`, `kanji_cut`, `line_charge` | Wrist and blade through a clean silhouette. Trails start just after weapon acceleration, peak at contact and clear before the return. Stretch the recover phase for heavier gear. |
| `yari_thrust`, `yari_leap`, `staff_sweep` | A readable tip lead with shoulders, offhand and planted feet doing distinct jobs. Spears use a narrow line for thrust, staves use a lower broad arc for sweep. |
| `club_swing`, `unarmed`, `kiho_or_kata`, `kata_stance` | Wind from the hips, plant and finish. A taught stance has a short settle and no extra impact. Throw or slam effects only appear when the existing result applies. |
| `draw_shot`, `thrown`, `mounted_pass` | Release on the existing ammo event, track the projectile to the existing target, and make the draw action match the actual rigged prop. For a group volley, share one release and retain the ordinary target timing. |
| `spell`, `control_cast`, `healing_cast`, `ward`, `formation`, `evade_guard`, `sheathed_focus` | Pose changes at the caster, effect resolves at its existing target. Use upward bubbles for Water and support, curling ribbons for Air, short angular facets for Earth and Jade, advancing licks for Fire and a narrow edge for Void. |
| `study`, `accord`, `remedy`, `steal`, `powder`, `shadow` | Small actor gestures, useful props, and brief target-anchored results. Emphasize each effect with contrast in daylight and a readable size. |
| `tattoo_breath`, `tattoo_heal`, `tattoo_dragon` | The ordinary breath keeps its existing result and emitter. The Void variant replaces its presentation at the agreed cast beat, with the dragon attachment and field-wide sweep. |
| `guest`, `weapon_family`, `scripted`, `system`, `passive` | Guests animate the proxy wielding the weapon. Unclassified attacks resolve by actual equipped weapon if compatible. Leave visual ownership with the existing script for macros, system transitions and passive upgrades. |

Use a shared 50-bone bank for mounted props and humanoid abilities. Keep prop fit and clothing weights separate. Place long moves in the render presentation layer so they return to the combat slot, never relocate collision or change turn order. Time each existing gameplay hit to its impact. Transitions restore animation, camera, VFX ownership and the actor's combat slot if the stage changes. Keep battle recovery to about two seconds past the cut-in. Use the daylight Coast Road battle window for review.

## Yari Void pilot

The pilot uses the first Void critical of a compatible single-target normal yari attack. Hiruma and Akodo actors need a loaded native yari and the shared spear bank. The actor coils through frame 10, leaps at frame 11, spins the yari twice between frames 12 and 27, drives the spear into the target near frame 34, and turns back to the original spot before frame 60. The camera focuses the flight and thrust on fixed battle cameras. The normal hit effect still runs. Two short airborne wind accents use the existing Yari of Air particles.

The animation bank and plugin are staged for root to install and review. Other school signatures are design routes. The Togashi dragon asset and rig are being handled separately from the pilot.
