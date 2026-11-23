# Scene color review

I reviewed 66 installed scenery captures and grouped the places with the strongest need for more color. The candidates use map-local descriptor aliases, so a material shared elsewhere keeps its original art.

| Area | Scoped maps | Color direction |
| --- | ---: | --- |
| Shadowlands march, Shifting Waste, and Shiro Hiruma | 21 | Cool slate and deep plum around dried wine-red taint and ochre route cues. The brightest notes stay on terrain that tells the player something. |
| Shiro Iuchi tower, siege camp, wind tunnel, and jade mines | 17 | Amber wood against indigo and plum, yellow bronze details, clear emerald seams, and a forest-green Dragon camp canvas. |
| Buried Leaves, the Soshi camp and hall, and Yotomo | 5 | Scorpion crimson in brocade and lacquer, stronger reddish canvas and indigo awnings, and autumn warmth against violet roof tiles. |

## Preview and install

Start in the existing Coast Road scratch folder with an idle isolated RPG-Cobo slot. Set the two local paths before running the following commands.

```powershell
$py = 'C:/AI/comfy-3d/venv/Scripts/python.exe'
$repo = 'C:/Users/akodo/.copilot/repos/copilot-worktrees/Traveler/akodoreign-laughing-chainsaw'
$slot = 'C:/Users/akodo/Documents/Codex/2026-11-20/ok/work/multi-window/profiles/slot-a'
& $py color-audit/scene_palette.py stage $repo color-audit/bundle-dried --profile $slot
foreach ($map in 'M458','M465','M408','M412','M394','M396') {
    & $py run_preview.py $repo $map --profile $slot --daylight
    if ($LASTEXITCODE -ne 0) { break }
}
```

After the native preview, use the same recipe with `publish`. It compares the profile's palette rows, resource payloads, collision maps, and story against the review receipt before merging only the reviewed rows into the live index. The new descriptors and textures use a `_story_palette` suffix and load the original models. The original texture remains available for every map outside this set.

The optional `prepare` command rebuilds resources from the live baseline before publication. To isolate a group for additional review, pass `--groups shadowlands`, `--groups iuchi`, or `--groups autumn` to `prepare` and choose a separate bundle directory.

The offline profile verified all 43 story and world pairs, 53 unchanged mesh references, and 42 texture dimensions and alpha planes. The geometry, event data, instance transforms, portcullis, water, light, and animation parameters stay in place. `material-review.jpg` shows the revised material swatches. Initial native daylight review approved Iuchi and the Soshi hall. The revised Shadowlands floor avoids pastel pink by deepening the plum and taint colors and adding seamless mottling. The ochre route material and all other textures match the previewed bundle. See `dried-material-review.jpg` for the two revised swatches.

