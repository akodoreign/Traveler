# Published-map color audit

The broad review examined 69 archived scene captures plus the current Coast Road, Yasuki, Doji, and Phoenix 4K captures. Daylight formerly used a dawn HDR cube and similar blue-gray ambient levels on the roads. The first coastal candidate introduced clearer material contrast and a higher sun. In wide camera angles it exposed the dark lower half of the meadow panorama. The horizon revision uses a coastal cube with blue atmospheric color across the downward gameplay view and keeps the tide cave's wet stone distinct from the water. The separate M828 third test restores the brighter ground direction and adds steady shadowless bounce for both combat formations.

## Staged and offline verified

| Candidate | Maps | Intended contrast |
| --- | --- | --- |
| `coast-horizon` | M102, M470, M474, M486, M828 | Indigo and emerald accents. Clear turquoise shallows over darker water. Amber sand and rich cedar. Blue-gray cave floor. |
| `phoenix-horizon` | M475, M487, M799, M846 | Emerald woodland and warm ochre rock with scarlet shrine accents. Cool clear springs remain distinct from the earth. The outdoor pair shares the exact coastal-horizon light presets. |
| `retrospective-review` | M212, M236, M480, M481, M811, M829 | Bright exposed and submerged shoreline, warm coastal route, rich blue-gray cave stone and clear tidal pools. |
| `retrospective-review` | M414–M420, M883–M885 | Crane blue and ivory in town. Amber timber, rich reed greens, and blue-green river and paddies. |
| `retrospective-review` | M350, M351, M359, M360 | Welcoming river and spring blues separated from green plantings, warm dry routes, and tiled roofs. |
| `hoshi-color-review` | M103, M120–M125 | Outdoor emerald greens and varnished wood. Amber light, warm paper, and individual indigo, teal, crimson, or plum accents distinguish the rooms. |
| `scorpion-color-review` | M345, M347–M349, M362, M364, M366 | Crimson lacquer, lively jade, deep blue roofs and amber paving. Lavender stone and amber fixtures separate the Sewn Faces shrine from the markets. |
| `dragon-color-review` | M379, M380, M382, M872 | Alpine blue and snowy white with fir, jade roof tiles, amber track and slate. M872 keeps its authored combat lighting pending the arena fill review. |
| `bayushi-shrine-pond` | M586 | Brighter Shrine Court moss and cedar, a crimson roof and jade water. Four original animated koi stay in the two wet basins on either side of the dry bridge. |
| `doji-cave-color-restore` | M486 | Restores the earlier mineral-bank color from the original texture over the installed V2 slate, with a slightly stronger amber glow. The ochre path and water retain their installed texture bytes. |
| `yasuki-cave-color-restore` | M480, M481, M829 | Keeps the earlier colorful stone and crab accents. Boosts clear highlights in the existing water and gives the existing amber lamps a moderate lift. This supersedes those three cave rows in the older retrospective test. |

The staged rows preserve source worlds, story, collision, prop coordinates, animations, and water clocks. Map lighting uses scoped identifiers. Shared render presets and voxel materials keep their existing bytes. The five coastal rows have native comparisons and were installed on the horizon revision. Native approval for the M828 third test and the latest palette cohorts is pending. The two town cohorts also have a 16-pair offline texture comparison at `town-material-swatches.jpg`.

## Visually flagged for follow-up

| Locations | Observed issue | Candidate treatment |
| --- | --- | --- |
| M399/M403/M408/M411/M412/M881/M882, Iuchi field and storm scenes | Background and ambient contrast are still weak in archived shots | Preserve the existing plum/storm story palette and water. Test amber vs indigo lighting locally. |
| M422/M424/M888, winter roads and battle | The new water reads richly, but the old sunrise horizon remains in archived wide shots | Keep the tested water and snow colors. Consider a separate clear winter camera horizon after the current coastal review. The M423 barge stays at night. |

Kuni wasteland understatement stays in place. Story night, storms and ceremonial interiors should still use distinct, colorful light; a sunny field preset is scoped to appropriate maps.

## Stage commands

```powershell
& $py coastal-grade/coastal_revision.py stage $repo coastal-grade/coast-horizon --profile $slot
& $py coastal-grade/coastal_revision.py stage $repo coastal-grade/phoenix-horizon --profile $slot
& $py coastal-grade/coastal_daylight.py stage $repo coastal-grade/retrospective-review --profile $slot
& $py coastal-grade/arena_key_fill.py stage $repo coastal-grade/coast-final --profile $slot
& $py coastal-grade/town_palette.py stage $repo coastal-grade/hoshi-color-review --profile $slot
& $py coastal-grade/town_palette.py stage $repo coastal-grade/scorpion-color-review --profile $slot
& $py coastal-grade/town_palette.py stage $repo coastal-grade/dragon-color-review --profile $slot
& $py coastal-grade/shrine_pond.py stage $repo coastal-grade/bayushi-shrine-pond --profile $slot
& $py coastal-grade/preview_shrine_pond.py $slot $outputs
& $py coastal-grade/cave_color_restore.py stage $repo coastal-grade/doji-cave-color-restore --profile $slot
& $py coastal-grade/cave_color_restore.py stage $repo coastal-grade/yasuki-cave-color-restore --profile $slot
```

Run the native previews in their natural scoped settings. The existing `--daylight` test override forces the old field render profile after launch, so omit it for these checks. The stage commands use existing map files and apply only the render and palette aliases.

