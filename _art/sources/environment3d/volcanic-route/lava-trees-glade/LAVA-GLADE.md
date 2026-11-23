# Shinomen Lava Trees glade

The first daylight sample put a dense canopy between the camera and the lava trees. This candidate opens the central glade, with six inverted obsidian trees, five low basalt accents, and five vivid lava pockets. The approved emerald diorama pine frames the route in spaced groves. Fewer trees stand in the foreground, and 18 trees retain a gentle sway. Moss-covered shoulders carry the terrain beyond the old visible platform edges.

The rebuild preserves the original map catalog and collision file byte for byte. Both forest portals, the moss shrine, the side chest, and the encounter stay on their original anchors. All 73 molten cells sit outside the 778 route cells. The three inverted-tree asset files match the first candidate exactly.

The isolated stage verified 55 resource hashes and modified only the M450 environment row. The native model assets total 2.6 MB. Native review still needs to establish camera framing, walking and story flow in game.

~~~powershell
$py='C:/AI/comfy-3d/venv/Scripts/python.exe'
$work='C:/Users/akodo/Documents/Codex/2026-11-20/ok/work/volcanic-route'
$repo='C:/Users/akodo/.copilot/repos/copilot-worktrees/Traveler/akodoreign-laughing-chainsaw'
$slot='C:/Users/akodo/Documents/Codex/2026-11-20/ok/work/multi-window/profiles/slot-a'
& $py -B "$work/lava-trees-glade/build_lava_glade.py" stage $repo --profile $slot
& $py -B "$work/review_volcanic_route.py" $slot capture --map M450 --daylight --glade
~~~

The first candidate remains usable from the sibling lava-trees folder. Its existing daylight capture is unaffected by the glade capture.
