# Revised volcanic route

M442 replaces the stepped lava banks with one continuous ravine. The river rises with the mountain beneath three layers of broken basalt on the bank. The party stair retains its original two surveyed climbs, gate and encounter cells.

M443 uses the original hazardous basin footprint for a recessed molten pool. Its inner wall rises through glass, oxidized rock, and broken indigo basalt to an eroded outer lip, with relief fragments along the rim. The shrine has brighter lacquer over its existing footprint.

M896 carries the same indigo basalt across the arena and into the irregular lava banks. Stone slabs mark a broad crossing at the existing battle grade. The crossing spans z29.5 to z34.5 in world coordinates. The native floor and all four scripted encounter registrations remain intact, and the formation checks retain clearance at the original positions.

The offline stage verified all 65 asset hashes and changed exactly the three named environment rows. The original catalog, collision files, and 41 shared asset hashes matched. The original candidate and its receipt remain available in the parent folder.

~~~powershell
$py='C:/AI/comfy-3d/venv/Scripts/python.exe'
$work='C:/Users/akodo/Documents/Codex/2026-11-20/ok/work/volcanic-route'
$repo='C:/Users/akodo/.copilot/repos/copilot-worktrees/Traveler/akodoreign-laughing-chainsaw'
$slot='C:/Users/akodo/Documents/Codex/2026-11-20/ok/work/multi-window/profiles/slot-a'
& $py -B "$work/layered-basalt/build_layered_basalt.py" stage $repo --profile $slot
& $py -B "$work/review_volcanic_route.py" $slot walk
foreach ($map in 'M442','M443','M896') {
    & $py -B "$work/review_volcanic_route.py" $slot capture --map $map --layered-basalt
}
~~~

Use the same camera and lighting as the earlier capture for comparison. The layered-basalt suffix keeps both captures. The supervisor still needs to inspect the native bank profiles and run combat across the dry slabs before publication.
