# Traveler tent reuse

Gonta's Old Quarry camp on M104 and its M812 arena supply the finished `quarry_tent` and `quarry_tent_flap` assets. The south opening, rear canvas, support poles, and existing flap animation carry over with the same pivot. Match the finished prop to the footprint and rebuild the terrain for each map. The original army or market interaction anchors define the aisle and doorway.

## Shiro Iuchi

M603, M604, M605, and M610 each have four former stepped-tent footprints. The installed pass includes 16 tent and flap pairs, 96 exact stock geometry removals, and the same pole and rear barriers used on the quarry map. It exports a fresh terrain mesh without the old tent silhouettes. The plans preserve the previous art changes, existing placements, materials, and story events.

`prepare_castle_tents.py` writes `clan-castles-iuchi-tents`. Use the `iuchi-tents` group with the existing castle installer with the plan's pole and rear barriers.

## Older stock maps

| Map | Setting | Reused tents |
| --- | --- | ---: |
| M214 | Crane lines | 17 |
| M215 | Ridge at dawn | 3 |
| M323 | Antique market | 2 |
| M325 | City stalls | 2 |
| M337 | Historical war camp | 6 |
| M825 | Border meadow battle | 7 |

`prepare_world_tent_fits.py` writes `clan-castles-world-stock-tents` for the `world-stock-tents` installer group. The rows cover props and have a `propOnly` marker. The six maps still need their individual terrain passes. The Crane command tent uses a 1.2× fit, and the historical command tent uses 1.4×. The market pairings keep neutral linen and the original merchant aisle. The static walk proof reports zero new unreachable interactions and no collision changes outside each tent's footprint.

The Ojatara road and town, Soshi camp, Dragon town, autumn town and refugee camps, Hafuna fields, Mirumoto camp, siege camp, and caravan road already have no surviving stock tent filler from this builder. Keep their fitted art.

M267 and M273–M274/M276 still have separate plaster placeholders called tents in their map designs. Review those with their terrain and story entrances. They include enclosed and guarded locations with different collision requirements.

The 53 tents are installed. All six older maps loaded for a native 4K check. The Shiro Iuchi tent entrance and the garden and keep links passed native walking checks. Its hitching rails sit to the side of the tent openings.
