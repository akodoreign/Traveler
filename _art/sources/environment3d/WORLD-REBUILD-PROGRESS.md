# Traveler world rebuild

## Installed and checked

- Dragon town, Togashi road, Togashi garden, and the mountain wolf arena are `M379`, `M382`, `M383`, and `M872`. The fitted Dragon inn and its approach `M380` and `M381` were installed earlier.
- Buried Leaves and the autumn valley cover `M387` through `M395` and the matching bandit arena `M875`. The Welcome Road inn and Hafuna turnoff passed both directions in the game. The market inn and trader have working ajar doors, with closed leaves on decorative facades.
- Yotomo village, pigeon cave, vat chamber, and their battle maps are `M396`, `M397`, `M398`, `M876`, and `M877`. The roof is physically walkable underneath. The six adjusted event positions put arrival and return markers on the cave passages. `yotomo-cave` and `yotomo-vat` passed both directions in the game.
- The environment inventory records 118 installed map passes out of 698. Use `inventory/map-catalog.csv` to track the full scope, including side districts, interiors, caves, alternate states, and battle maps.

## Pick up here

- Shiro Iuchi starts at `M399` with the star field, tower floors `M400`–`M402`, and the battle map `M878`. The woods and camp connect to the jade mines `M403`–`M407`, `M879`, and `M880`. The next connected stretch is `M408`–`M412`. The `comfy_iuchi_tower.py` jobs generated the frost and mine-wall scans, birch, andon, and jade seam. Inspect those models for artifacts and fit them to the built maps.
- The Dragon inn and outfitter interiors `M962` and `M963`, Buried Leaves trader `M965`, and side districts `M642` and `M646` still need their own passes. Their door dressing is present on the parent maps.

## Working rules

1. Lead with readable shapes and a tight color palette. Inspect Comfy meshes for baked scenery, white backdrops, and stray geometry before staging them. Make structures such as doors and shelves from clean, separately modeled pieces when fit matters.
2. Use the actual doorway cut and floor grade for the door and stoop. Bind ajar leaves to live entrance events. Walk into and out of caves and doors using the native game so that the visible opening and trigger can be checked together.
3. Build and review daylight frames at 3840 × 2160 in the two isolated profiles. Check both gameplay distance and close angles. Keep animated details and background props outside the travel and formation lanes.
4. Use `install_environment_rows.py --preserve-existing` when publishing a new group. Keep existing row and shared asset bytes intact. Archive the map receipt, art recipe, source assets, and selected daylight samples before moving to the next group.
