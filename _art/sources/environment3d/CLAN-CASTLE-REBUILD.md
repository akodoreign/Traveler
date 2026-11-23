# Roamable clan castles

The expansion adds twelve districts and four keep floors to each castle. The environment pass follows the generated terrain and collision for each district. The art kit adds fitted tiled roofs, keep tiers, masonry and timber panels, district props, miniature pines, animated garden ponds, and separate furnishings. The eight castles use their own palette and retain their chapter events and activities. The Kabuki deck and its four stage lights are preserved on M555.

| Castle | Reception and keep floors | Additional grounds |
| --- | --- | --- |
| Kyuden Hida | M500–M504 | M535–M545 |
| Kyuden Doji | M505–M509 | M546–M556 |
| Shiro Akodo | M510–M514 | M557–M567 |
| Kyuden Isawa | M515–M519 | M568–M578 |
| Kyuden Bayushi | M520–M524 | M579–M589 |
| Shiro Kitsuki | M525–M529 | M590–M600 |
| Shiro Iuchi | M530–M534 | M601–M611 |
| Kyuden Togashi | M623–M627 | M612–M622 |

## Door and route checks

Native round trips covered reception to garden, approach to first floor, and all three sets of stairs in each castle. The Hida town gate also passed both ways on its original G200 flag. Logs are named `castle-native-*-round-trip.log` and `castle-native-*-stairs.log`.

On M573, the sealed library has a fitted recess centered on trigger #8. The return from M296 now faces the courtyard at the original threshold. G671 still controls entry and the door leaf. The game confirmed that the closed door leaves the party outside, and that the open door allows entry and an unobstructed return. The archive contains 3840 × 2160 captures of both states.

## Reproduction

`build_clan_castles.py` generates map rows, terrain meshes, water surfaces, and fixture removal plans. `install_clan_castles.py` stages exact maps in an isolated native profile and publishes the tested data. The installed map-aware plan is in `tools/clan_castle_art.json`. `preview_clan_castles.py` captures native daylight frames. `verify_clan_castle_routes.py` drives the existing entrances and stairs. Generate all castle assets through the three `comfy_clan_castle*.py` recipes. The Comfy job receipts, material scans, and source meshes are archived next to the art recipe. The environment catalog tracks installed coverage by map ID.

The user approved reuse of finished Traveler props across maps, including non-voxel textured meshes. Refit scale and position for each use and build the terrain for each map's layout.

The daylight palette pass enriched 36 selected textures. Use `polish_environment_tiles.py` with the isolated profile after regenerating original surfaces. The approved color direction is brilliant color where appropriate, with luminous details and deep color giving the Shadowlands its own eerie beauty.
