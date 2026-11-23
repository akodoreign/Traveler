# Doorway centering audit

The published environment index has 51 doorway registrations and 31 decorative door and stoop pairs stored as individual placements. I compared them against the generator's padded world cuts and the live event catalog. The candidate covers 16 registered door assemblies, 31 decorative stoops, four fixed decorative door slabs, and four portal trigger centers.

## Placement rules

In an ordinary two-block opening, the asset origin for a town or Dragon frame goes at the cut's left edge, `cut.x / 2` metres. The visual midpoint and stoop midpoint are each half a metre east of that origin. The closed `kudo_shut_door` slab is authored around its midpoint and needs the midpoint as its asset origin. The runtime leaf hinge sits 0.073 m along the frame and 0.076 m deep. This is a deliberate rotation pivot and travels with its frame.

The threshold y equals the cut's bottom. Set the stoop base to the walking surface elevation immediately before the cut, `(world.hgt[z - 1, x] + 1) / 2` metres. Inspect both opening cells so a floor tier or sloped approach does not pull the stair off a jamb. The native portal's padded-block x equals the opening midpoint. Keep its y and z at the existing trigger tier and approach distance.

## Registered assemblies

All frame/stoop midpoint values below equal the voxel opening midpoint after the adjustment. All affected rows use `town_door_stoop_half`. The JSON records the complete before and after rows, exact cut dimensions, threshold height and grade, and linked event coordinates.

| Map | Door event | Frame origin x before → after (m) | Verified midpoint x (m) |
| --- | --- | --- | --- |
| M457 | 79 | 20 → 19.5 | 20 |
| M457 | Decorative | 29.5 → 29 | 29.5 |
| M351 | 3 | 36 → 35.5 | 36 |
| M351 | 2 | 47 → 46.5 | 47 |
| M351 | 4 | 55.5 → 55 | 55.5 |
| M360 | 85 | 20 → 19.5 | 20 |
| M360 | 86 | 47.5 → 47 | 47.5 |
| M362 | 2 | 20 → 19.5 | 20 |
| M369 | 97 | 20 → 19.5 | 20 |
| M369 | 2 | 32.5 → 32 | 32.5 |
| M369 | 98 | 43.5 → 43 | 43.5 |
| M369 | 99 | 50.5 → 50 | 50.5 |
| M375 | 2 | 36 → 35.5 | 36 |
| M347 | 94 | 25 → 24.5 | 25 |
| M347 | 95 | 32.5 → 32 | 32.5 |
| M347 | 96 | 49 → 48.5 | 49 |

The other 35 registered frames already match the corresponding cut laterally. M415/M416 Cakon shutters and the herbs, inn, teahouse, and trade entries meet the cut and local two-metre grade. The three M379 Dragon village frames and two active triggers also match. The high Dragon mountain inn M380 uses a one-metre stoop that correctly rises from 3.5 m to 4.5 m. Only its trigger x needs an edit. The nine Hoshi M103 frames align laterally. Its lower frontage includes a one-block grade change on the approach and the stoops use the grade directly at the wall. The elevated decorative Hoshi door is 1.5 m above its local grade without a portal or a stoop. The six-block Shiro Iuchi M399 entry is already centered on padded x81.

## Fixed decorative doors

| Map | Stoop origins x after correction (m) |
| --- | --- |
| M351 | 22.5, 29.5, 62 |
| M360 | 29.5, 38.5 |
| M362 | 28.5, 37, 45.5, 54 |
| M364 | 18, 26.5, 65 |
| M372 | 19, 31.5, 43 |
| M374 | 18, 24, 49, 54 |
| M375 | 18, 26, 45, 53 |
| M347 | 17, 40 |
| M349 | 17, 24.5, 32, 39.5, 47, 54.5 |

Each stoop above shifts left 0.5 m except the four M374 stoops, which shift left 0.75 m. M374's fixed slabs shift left 0.25 m to x18.5, x24.5, x49.5, and x54.5. The other 27 fixed slabs were already centered.

## Native route checks

Coordinates are padded blocks in event order `x, y, z, facing`. Approach from smaller z at the listed x. Enter and immediately leave from the given interior portal to verify the return clears the trigger. The destination ID, event ID, and portal settings remain the installed values.

| Exterior and event | Trigger before → after | Destination entry and return trigger |
| --- | --- | --- |
| M360 Hisatu Kensu #85 | (39, 4, 24, 0) → (40, 4, 24, 0) | M955 inn #1 at (21, 2, 8, 2) |
| M375 Perfume Petal Blossom #2 | (71, 4, 25, 0) → (72, 4, 25, 0) | M376 beautiful house #1 at (7, 2, 12, 2) |
| M380 Dragon mountain road #2 | (86, 7, 24, 0) → (87, 7, 24, 0) | M381 common room #1 at (6, 2, 12, 2) |
| M387 autumn Buried Leaves #1 | (39, 4, 25, 0) → (40, 4, 25, 0) | M388 Welcome Road inn #1 at (6, 2, 11, 2) |

For a nearby visual reference, M360's two fixed doors should sit flush over their stoops at z12.882 m, with the inn at x20 m center. M374 is the clearest decorative before and after because the slab and stoop both move. M362's hospitality building changes are independent of the temple curtain and portcullis, with the building entry at (40, 4, 25, 0). The separate castle gate pass owns the curtain and gate solids on M410, M362, M461, and M462.

## Applying the candidates

`door-centering-candidate.json` holds three independently scoped sets of exact replacements. `replace_index_field` updates only the requested field against the current index and checks that each before row occurs once. `replace_live_positions` checks the before pose and destination for each installed event and edits only its position. `variant` returns the persistent generator source patch for the same four positions. The static verification compared generator world geometry, wall sets, and event payloads before and after. All four changed triggers passed straight-in and return walks in the native game. Daylight frames of the Hisatu Kensu and Perfume Petal Blossom doors are archived.

`door-centering-builder.patch` carries the art placement corrections into the six environment builders for the next regeneration. Run the patch from the directory containing the builders. The candidate compiled all six proposed sources in memory and the patch passed `git apply --check`.
