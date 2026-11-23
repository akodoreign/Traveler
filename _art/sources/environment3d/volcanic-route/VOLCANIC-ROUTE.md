# Volcanic route native review

M442 adds a stepped basalt switchback with rope waymarkers and a lava stream in the foreground ravine. Its five original grades and trigger positions remain in the native map. M443 rebuilds the shrine in cedar, copper, and vermilion over the existing sealed shrine footprint. A dark basalt bank encloses the crater lava basin. There is no cave portal on this route. M896 places a recessed lava ribbon between the original formations, with a dry central crossing over a solid native floor for combat movement. The native M001 groups 149–151 and 153 remain registered, including the E559 champion.

Rock 01 diffuse and GL normal textures supply broad stone detail. The candidate reuses the fitted Comfy bronze lantern, crusted lava bank, and rope waymarker meshes. Thirty-two timed lava frames and sparse heat effects give the molten channel visible movement.

The build receipt records all 66 native asset hashes, the original map and collision hashes, source anchors, and the formation clearance measurements. Staging twice in an offline fixture produced the same rows and assets. The other 317 environment rows, the complete map catalog, and all three original collision files matched the live copy.

## Stage and verify in a closed playtest slot

~~~powershell
$py='C:/AI/comfy-3d/venv/Scripts/python.exe'
$work='C:/Users/akodo/Documents/Codex/2026-11-20/ok/work/volcanic-route'
$repo='C:/Users/akodo/.copilot/repos/copilot-worktrees/Traveler/akodoreign-laughing-chainsaw'
$slot='C:/Users/akodo/Documents/Codex/2026-11-20/ok/work/multi-window/profiles/slot-a'
& $py -B "$work/volcanic_route.py" stage $repo --profile $slot
& $py -B "$work/review_volcanic_route.py" $slot walk
& $py -B "$work/review_volcanic_route.py" $slot capture --map M442 --daylight
& $py -B "$work/review_volcanic_route.py" $slot capture --map M443 --daylight
& $py -B "$work/review_volcanic_route.py" $slot capture --map M896
~~~

The capture helper defaults to story lighting, verifies the running molten animation, checks the actual scripted champion on M896, and saves true 3840 × 2160 captures to the session outputs. The supervisor still needs to check the native sample, walking, story triggers, and a full attack crossing before publication. Source rebuilds use the same recipe with `build` and the repository path.

After review, use the existing `install_environment_rows.install` with `STAGE` set to this candidate's `native_environment` and select M442, M443, and M896. Its default update mode replaces only those rows.
