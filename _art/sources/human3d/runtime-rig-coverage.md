# Human and foe runtime rig audit

The installed character roster contains 349 field and party actors and 102 human foe model IDs. All 451 entries have a modular body descriptor, shared male or female body, face descriptor and mesh, and native motion. Registered individual hats, masks, garments, weapons, and covered-head variants referenced by those entries had files on disk. Both portable shared body skins contain 50 named joints, including the neck, head, hands and fingers.

The combat data contains 762 named enemy entries with model IDs. Its 368 human enemy entries resolve through the 102 native human foe models. The other 394 resolve through 104 registered creature models. The 21 legacy model references outside the native catalog are the engine's explicitly unused combat entries. One other tutorial record has no model.

## Field actors and story variants

The following event variants resolve through the field event loader in `RokuganLook.sk`. They reuse the actor's exact native body, head, proportions and outfit, with the standard field size adjustment. A separate gold question-mark picture replaces the original badge that was painted into the old sprite sheet. Event IDs, requirements, position, collision, dialogue, and the generated yellow and blue quest-marker states were retained.

| Appearance ID | Existing native model | Live story placement |
| --- | --- | --- |
| EP1165 | EP382, Kitsu Takeo | M536 event 8 |
| EP1166 | EP383, Yogo Mai | M541 event 13 |
| EP1167 | EP384, Ide Fujio | M539 event 14 |
| EP1168 | EP385, Daidoji Sakura | M538 event 13 |
| EP1169 | EP381, Hiruma Goro | M101 events 16 and 17 |
| EP1170 | EP380, Isawa Michio | M101 event 19 |
| EP1171 | EP314, Moto Benjiro | M444 event 11 |

Takeo, Fujio, Sakura, Goro, and Michio reuse their fitted textured portrait heads. Mai and Benjiro reuse their identity-specific native head assemblies. Their independent portrait sculpts were not installed by this pass.

Both EP435 encounter stand-ins, M177 event 3 and M355 event 3, resolve to the installed EP123 creature rig used by the corresponding E247 and E455 fights. The same field hook can already identify a matching native body for 69 additional live foe placements across 25 model IDs. Creature stand-ins use their existing combat model scale with the original field event collision and spawn rules. Powder kegs and bloodstone basins remain on the object-hazard route.

## Alternate and reserved routes

- The audit inspected nested model assignments in the current map and battle data. The static cast route had no additional named human fallback after the seven exact side-story aliases.
- Mitsue's disguises go through native equipment on P105. They preserve her body and use their registered outfit and headwear pieces. The leader, battle members, and party followers resolve the base actor before applying equipment. A follower also passes its live wearer to the same creation hook.
- The 340 alternate `__weapon_head` sheets remain available to the legacy look fallback. No authored map event or embedded map script selected one directly. Engine sample maps retain their own fallback presets. CV011, the woman soldier in M006, and CV017, the fairy in M008, are sample placements. They do not have a Traveler story identity.
- The authored head holds remain in `cast-head-holds.csv`. A working native body route has no bearing on unfinished or held portrait sculpt approval.

## Daylight verification

Run `tools/test_native_side_story.sk` through the existing game runner after the real events spawn. It checks the original event object, exact native key, 50 joints, separated head and clothing, non-colliding gold billboard, and normal 1.25 field size. For a creature it checks the exact native model and idle bank.

- For Goro and Michio, use M101 around their event positions (27, 22) and (33, 14.5) with G286, G233, G234, G235 and G236 set. Keep G292 and G1213 unset. Verify each from its own position if event range only loads one.
- For Takeo, use M536 near (28, 8) with G233 and G1644 unset. For the normal quest marker state, G054 should be set.
- For the Kommei stand-in, use M355 near (30, 9) with G854 unset. M130 events 9–11, M131 events 13–15, and M172 events 4–7 exercise additional existing creature rigs when their encounter flags permit the props.

Both native playtest profiles passed the daylight runtime fixture for all eight quest-marked placements across seven characters, both Kommei stand-ins, and ten representative creature placements. The checks confirmed the actual event actor, native identity, 50-joint human skin, separate head and outfit, field scale and gold badge. Creature cases covered Nezumi in M130, beetles in M131, and Goblin Warmongers in M172. The remaining creature placements were audited statically. Full animation and wardrobe clearance were outside these fixture checks.
