# Hida stone and Wall-top revision

The cave walls have a continuous shoulder that overlaps below the floor. Every vertex touching a playable tile stays 8.6 cm beneath the slab. Both triangles over any playable tile therefore sit below the walking surface. The outside skirts close exposed façade edges, and the main wall normals blend across adjacent scanned-rock materials.

The navy stone texture median moved from RGB 45, 68, 126 to 18, 29, 62. Dark slate carries the floor and wall surfaces, with smaller, warmer lantern pools to bring up the dressed stone, cedar, and rust-red accents.

At the Kaiu Wall, the original entrance position remains at x56,z10 in block coordinates. A 3.24 m vaulted opening extends around the arrival. All 36 native crenellations have corresponding masonry over their original footprints. The long continuous retaining wall and outer battlement extend outside the deck boundary, leaving the original walkable floor beneath the open passage.

Staging both bundles in one offline copy verified 50 unique assets and changed only the seven named environment rows. The other 325 index rows, source map catalog, collision files, and both original candidate bundles matched byte for byte.

~~~powershell
$py='C:/AI/comfy-3d/venv/Scripts/python.exe'
$work='C:/Users/akodo/Documents/Codex/2026-11-20/ok/work/hida-cave-rework'
$repo='C:/Users/akodo/.copilot/repos/copilot-worktrees/Traveler/akodoreign-laughing-chainsaw'
$slot='C:/Users/akodo/Documents/Codex/2026-11-20/ok/work/multi-window/profiles/slot-a'
& $py -B "$work/stone-relief/build_hida_relief.py" stage $repo --profile $slot
& $py -B "$work/stone-relief/build_hida_relief.py" stage $repo --profile $slot --deep
foreach ($map in 'M148','M149','M150','M815','M157','M158','M170') {
    & $py -B "$work/review_hida_caves.py" $slot capture --map $map --relief
}
~~~

The relief flag gives the new captures distinct names and uses a tighter Wall-top camera. The original previews and receipts remain in their existing locations. The root agent handles visual review and native traversal.

## Installed and checked in the native game

All seven maps were published from the exact reviewed assets. The north donjon threshold passed in both directions with the existing G211 requirement. The four inner portal legs, flare handoff, Wall arrival, Kaiu return, and Shadowlands handoff also passed. Group 14 still loads the Maho Puppet and troll on M815.

The final review corrected the outer winding of the cave shells. The exterior and floor now read continuously around the walkable openings. The 4K daylight samples include the main spaces and close views of the donjon, catacomb and deepest-cell thresholds.

The native catacomb walk fired the original roller and jade-line triggers, setting G225 and G226 in sequence.
