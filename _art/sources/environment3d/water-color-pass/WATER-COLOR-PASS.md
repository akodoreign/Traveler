# Cold water color and flow

The winter River of Gold gains a sapphire surface with cyan crests and gentle downstream roll. The winter jetty battle keeps its darker steel-blue storm water. The Iuchi woods brook uses clear turquoise to distinguish it from the deep river.

| Maps | Liquid | Authored cycle | Phases |
| --- | --- | ---: | ---: |
| M422, M423, M424, M888 | River and barge | 17.8 s | 64 |
| M889 | Winter jetty storm | 9.6 s | 64 |
| M403 | Iuchi brook | 13.0 s | 32 |

The winter sheets have twice as many intermediate phases within the same authored periods. The movement closes a full UV tile each cycle and the soft crest pattern deforms while it drifts. Each map keeps its original water mesh and roughness, and the animation uses its own texture prefix. The cave maps, lava, snow, map geometry, collision and story entries are outside the scope.

## Stage and install

From the Coast Road scratch folder, point at the worktree and an idle isolated profile. The stage command copies the six reviewed map baselines into that profile and overlays the candidate there.

```powershell
$py = 'C:/AI/comfy-3d/venv/Scripts/python.exe'
$repo = 'C:/Users/akodo/.copilot/repos/copilot-worktrees/Traveler/akodoreign-laughing-chainsaw'
$slot = 'C:/Users/akodo/Documents/Codex/2026-11-20/ok/work/multi-window/profiles/slot-a'
& $py water-color-pass/clear_water.py stage $repo water-color-pass/bundle --profile $slot
```

Use the existing native preview runner with M422 and M889 to compare calm and storm daylight. M423 should carry the same sapphire as the banks, and M403 should keep the 13-second brook cycle. The standard preview prints current phase count and period. After the native review, run the same recipe with `publish`. It compares the isolated profile's candidate bytes and the live world and event fingerprints before merging only the six water rows.

The offline check resolved all 166 staged resources. The 160 textures wrap smoothly across the last and first phases, and all three clocks match their source maps. See `water-material-review.jpg`, `winter-sapphire-water-motion.gif` and `water-static-verification.json` for the source-material review. Native sunlight and terrain framing belong to the in-game review.
