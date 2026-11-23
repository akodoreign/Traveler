# Hida cave review

The donjon cells use blue flagstone, rust-red ironwork, cedar benches, and amber Japanese lanterns. Real scanned rock and normal textures carry through the drain gallery, deepest cell, and donjon battle arena. The narrow main passages have opaque stone shoulders, clear space beneath the roofs, and depth behind the openings. The original Hunyuan bench, iron lamp, and basalt drain assets are included.

The four-map offline stage verified 40 assets. It changed only M148, M149, M150, and M815 in the native environment index. The live catalog and collision files matched byte for byte. All nine random encounter groups in each first cave and M001 groups 13, 14, and 23 still point to M815. The actual native preview for M815 boots group 14 and checks the puppet-troll foe.

## Stage and preview

~~~powershell
$py='C:/AI/comfy-3d/venv/Scripts/python.exe'
$work='C:/Users/akodo/Documents/Codex/2026-11-20/ok/work/hida-cave-rework'
$repo='C:/Users/akodo/.copilot/repos/copilot-worktrees/Traveler/akodoreign-laughing-chainsaw'
$slot='C:/Users/akodo/Documents/Codex/2026-11-20/ok/work/multi-window/profiles/slot-a'
& $py -B "$work/build_hida_caves.py" stage $repo --profile $slot
foreach ($map in 'M148','M149','M150','M815') {
    & $py -B "$work/review_hida_caves.py" $slot capture --map $map
}
& $py -B "$work/review_hida_caves.py" $slot portals
~~~

Use a closed isolated slot. The root agent runs the native previews. The capture helper also accepts `--story-light` for the map's original underground lighting.

## Traversal

M148 has a straight x61 route from the north threshold to the south tunnel. Its original goblin ambush still triggers around z30. The rat-way interaction at x57,z10 has a visible floor hatch and uses the original scene warp.

M149 keeps the wide edge triggers centered at x82. Their volumes reach the real x61 tunnel, so walk through x61 at z2 or z54. The catacomb track passes the roller at x61,z16 and the jade line at x61,z25. From the north arrival, take the connected passage through x51,z5, x47,z11, and x50,z18. From the jade line, backtrack to the northern cross passage at x64,z18 and take the east curve through x68,z16, x72,z22, x69,z29, then return to x61,z31 for the southern tunnel. The receipt records sampled route cells from the original geometry.

M150's north entrance, battle start at x56,z14, troll at x56,z29, and side chest remain in their original positions. The restraint frames sit behind the story actors and leave their approach open. Check the native tunnel return at x56,z2.

## Deep tunnels and Kaiu Wall

The second bundle is staged independently with `build_hida_caves.py stage <repository> --profile <closed slot> --deep`. It verifies 28 native resource files, including 20 shared assets that match the first bundle. M157, M158 and M170 each have a default daylight view. Use `portals --leg flare-to-wall`, `portals --leg kaiu-return`, or `portals --leg kaiu-shadowlands` to review their original scripted transitions.

M157 keeps the blue-flare scene at x61,z10 and the original jade cache. The approach begins with shoring and opens into rougher natural stone. The M158 arrival passes beneath a roofed passage at the original x56 arrival. The story warp remains one-way and leads onto the same battlement deck and boss scene.

M170 keeps the Kaiu return at the west bore and the existing point-of-no-return choice at x113,z19. The playable east route leaves the early straight corridor below the wall, then bends through x73,z27, x82,z38, x108,z34 and x117,z25 before returning to the far story anchor. The path shading follows the connected native route. The former trap floor cells, both possible companion scenes and the Shadowlands handoff remain in place.
