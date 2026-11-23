# Traveler castle gates and curtain walls

The audit followed the published terrain, padded block grid, and current story events. A fitted gate needs a physical approach and a playable opening. A locked grate needs a blocker, a story condition, and a clear return landing. All four candidates below are installed. Native checks covered the locked Narrows and Kamen approaches and the open routes into both Hiruma interiors.

## Installed gates

| Map | Finding | Candidate |
| --- | --- | --- |
| M410 · Shiro Iuchi narrows | The east and west jambs meet a high escarpment, while the closed-looking timber leaf has no physical collision. The gate event already requires G1026. | Return the stone jambs into the cliff, add matching curtain wings and a taller lintel, and replace the visual-only swinging leaf with a story-driven lifting grate. Keep the current doorway frame. |
| M362 · Kamen Hospitality District | The Temple District arch is freestanding. Both sides can bypass a hypothetical obstruction in the arch. The east edge portal requires G891 and G893. | Run stone curtains to both map edges and put a lifting grate inside the original arch. Keep the Temple gatekeeper and inspection point on the town side. Leave the unrestricted M361 gateway open. |
| M461 · Shiro Hiruma outer bailey | The open ruined gateway can be skirted on either side. Its east touch event spans well beyond the dressing. | Tie the existing arch to two chipped stone curtains. The ruin's opening stays walkable. |
| M462 · Shiro Hiruma keep | The hall entrance is a freestanding ruined arch in front of another broad edge trigger. | Continue the curtain into the north terrain and across the southern flank. Preserve the open gate and ancestral altar route. |

The in-memory audit proved the gate lane passable in each open candidate, both side routes closed with the aperture blocked, and the event records and ground grids unchanged. Counts are 82 events on M410, 91 on M362, 77 on M461, and 78 on M462.

## Native acceptance coordinates

Coordinates here are padded block coordinates. Camera and engine positions are half-scale.

- **M410** starts at (126.4, 14.1). Leave G1026 false and walk toward (126.4, 21.0) to exercise the closed grate. Check the blocker at x124–127, z18, y4–9. Walk toward (126.0, 20.0) from (119, 20) and (132, 20) to test the wall joins. With G1026 true, the existing route in `check_river_and_bridge.py` enters M411 through event #2 at (126, 20). The return starts at (126, 18) on M410. Walk south to (126, 14) to prove it egresses without a retrigger. A debug flag set while on this side can also prove in-place lift timing.
- **M362** starts at (126, 21), with G882 and G898 set to skip unrelated scenes. Leave G891 or G893 false and aim toward (141, 21). The gatekeeper remains approachable on the town side, and the party stays west of the barrier at x132, z19–23, y4–9. Probe either end by walking along x toward (140, 12) and (140, 35). Set G891 and G893 together, then walk through (136, 21), curve to (154, 30), and approach (163, 30) for event #90 to M365. From M365 approach original portal #1 around (29, 22), then confirm the return spawning near (134, 21) on M362 can walk west through the raised grate to (126, 21).
- **M461** approaches the bailey opening with (150, 28), (157, 28), then (160.5, 28) and the original “In” choice to M462. The 2.5 m aperture spans z26–30 through x156–157. An off-axis walk at z19 or 34 should meet the stone. Choose “Not yet” once to confirm the party can step back out of the open lane, then re-enter. M462 returns to M461 town-side at (130, 20).
- **M462** approaches the hall gate with (135, 26), (143, 26), then (146.5, 26) and the existing “Go in” choice to M463. The aperture spans z24–28 through x142–143. M463 returns to M462 at (116, 20). Check the altar interaction remains usable and keep the ruined arch permanently open.

Use `castle_gate_candidates.py` and the matching `castle-gates-*-candidate` directory. The directory contains a scoped `rows.json`, new native meshes, and exact copies of the existing material textures. Each group can be staged independently with `variant(repo, group)`. The M410 row uses axis `x`, and the M362 row uses axis `z`. Both use the common native runtime for the physical blocker and lift.

## Audit queue and exclusions

| Map or family | Audit result |
| --- | --- |
| M101 Kaiu Wall garrison | Full-width terrain wall already blocks bypass at z46. The story gate is still a sealed facade with its custom choice at (39, 45) immediately in front. A later overhaul can cut an arch where the approach meets the wall and bind its opening to the existing page predicate G240 true and G255 false. Preserve the stairs to M100 and the independent G054 Hida road exit. |
| M457 Shinomen gate | The rebuilt wall spans the padded map. It already has a walkable tunnel and an open-gate choice at (81, 38) for the M458 route. The story calls it open. |
| M141 and M151 Kyuden Hida towns | The elevated stone wall already spans their padded widths. M141 portal #2 at (80, 50) uses G200. M151 uses a summer guard and siege transition choice instead. Treat them as paired variants when improving the gatehouse. |
| M228 Kyuden Doji | Full-width cliff at z36 with the reception portal at (83, 35). Access depends on G417. A later entrance cut should avoid the separate duel exit and its G1647 condition. |
| M255 Shiro Akodo | The current reception portal at (76, 34) is open. Keep the high northern route to M472 distinct from a keep gate. |
| M382 Togashi road and M383 | Current live M382 event #16 at (112, 24) leads to M623 with G947. The procession enters the garden from a separate event near (76, 19). A mountainside gatehouse can enclose the short north approach and preserve the entire east–west furnace road. M383 is now an old-save stub and its earlier garden dressing is no longer the active approach. |
| M347 Kyuden Bayushi and M391 Shiro Iuchi gardens | Their newer reception transfers are open, at M347 event #18 (76, 21) and M391 event #7 (66, 12). The freestanding M347 town gateway sits close to storefronts, with the old palace wall far behind it. A continuous curtain at the gateway line would block shops. The rear palace wall has low-grade padded flanks and can get stronger end returns as part of a separate precinct layout. |
| M399 Shiro Iuchi star field | The crag wall ends at padded x26 and x135, leaving decorative rear flanks approachable. The actual tower entry takes place in front of it at (81, 33). Its existing G998/G1000 gate animation and G999 portal implement the wax choice. A later wall-extension pass should preserve that story timing and the return from M400. |
| M361 City of Masks approach | G881 controls its actual entry at the edge. The city-facing approach has no freestanding city gate model. Add one if the entrance is being restaged, and preserve the route to the unrestricted M362 west gateway. |
| M323 Otosan Uchi south gate in year 400 | The palace wall stops at the original, unpadded footprint and can be skirted visually. The palace facade is closed in the story, and the Ink Door painting is a separate approach event. Review this wall with the M325 streets and M326 palace pass before adding new street restrictions. |
| Clan reception districts M500, M505, M510, M515, M520, M525, M530, M623 | The shared district builder reserves adjoining court routes at the four edges. The inner torii is a ceremonial marker. Tie new curtain walls to the exterior only, keeping legitimate flanking paths between the barracks, stables, training and gardens. |
