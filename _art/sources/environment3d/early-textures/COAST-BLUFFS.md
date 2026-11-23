# Coast Road bluff geometry

The visible Coast Road uses a continuous sculpt across the old stepped cliff heights. The model carries the approved cliff and grass hues into the slopes, applies the scanned rock normal over the face, and bends the UV chart down the escarpment to keep the grain at a natural scale. Eight shoreline stones and the pines use the fitted diorama meshes.

The installed block-world collision stays in place. The road, grass verge, sandy ledge, tidepool rims, culverts, and lower cave floor retain their original positions and UVs. The revised Egg Caves entrance uses a rounded visible lip at the existing roof, and the 41 fitted interior faces retain their exact positions. The approach still meets the threshold at `[96,4,32,0]`. The higher cliff uses the original support elevation at all 5,719 checked cell centers. The new surface curves between those centers where the old renderer had square edges. Upward transitions are still rounded cliff edges and the original jumps still follow the block-world collision.

Stage on an idle profile with the accepted Coast Road color and material pass already installed.

```powershell
$py = 'C:/AI/comfy-3d/venv/Scripts/python.exe'
& $py early-textures/coast_bluffs.py stage $repo early-textures/m102-bluff-review --profile $slot
& $py run_preview.py $repo M102 --profile $slot
& $py run_preview.py $repo M102 --profile $slot --entrance
```

Review the road in both directions, the visible shore walking line, and the cave threshold with the existing story unlock. The native review should verify the revised terrain alongside the current daylight grade. Offline staging succeeded twice with every other map row byte-equivalent in JSON, and the exact map file, story fields, and coast water sequence matched.

## Rounded throat and quieter surfaces

The follow-up uses `m102-throat-review`. Stage it over the initial sculpt or the approved material-only map with the same command. The rounded opening runs into a dark sleeve that ends just past the existing threshold. Higher cliff shoulders merge into the outer ring while the original tunnel surfaces remain behind the visible lining. A worn trail crosses the existing verge and enters the mouth at the original grade. Grass returns at the lowest ledge and tapers into the rock. Fine diffuse and normal detail was reduced at both the cliff and the path.

The second revision kept all 448 low faces and 41 cave faces at their original positions. It also passed 25 straight-line visual clearance checks across the center of the entrance. Its offline installation worked over the first sculpt and preserved the exact adjoining map rows, water recipe, map file, and story row.

## Sealed rock apron

The latest review bundle is `m102-sealed-review`. It uses a front-facing rock apron, a fitted cross-section behind the lip, and continuous sidewalls and ceiling through the old passage depth. The walking portal and collision retain their original coordinates. The front arch clears the road-facing entrance. The sleeve at the rear ends against opaque rock at the existing north bank.

The native-winding verifier checked 25 clear passage rays and 142 solid-rock rays across the rim, angled flanks, sidewalls, ceiling, and rear. It discards back-facing triangles in its test. The revised mesh uses the previous review's exact road, verge, cliff, and opening textures.

```powershell
& $py early-textures/coast_bluffs.py stage $repo early-textures/m102-sealed-review --profile $slot
& $py early-textures/verify_coast_throat.py early-textures/m102-sealed-review
```

## Joined limestone entrance

The current `m102-limestone-review` bundle uses a single front stone surface that reaches the ground at both jambs. Its upper band and side returns join the apron to the sculpted bluff. The old 41 tunnel faces remain represented in the unchanged collision world. The current render uses the continuous visible bore lining and the exact previous floor.

This revision reuses the accepted textures byte for byte. The verifier checks 25 clear passage rays and 362 rock hits, including 220 view rays reconstructed from both entrances in `preview_coast.sk`. Those view rays probe the lower jambs, stone above the lip, and bore ceiling.

```powershell
& $py early-textures/coast_bluffs.py stage $repo early-textures/m102-limestone-review --profile $slot
& $py early-textures/verify_coast_throat.py early-textures/m102-limestone-review
```

## Visible limestone floor and moss

The latest `m102-dressed-review` bundle fits a visible stone floor from the verge overlap at world z14.08 through the end of the bore at z20.50. It follows the original support and the half-metre drop at z17.5. Dark moss gathers in the lower jamb joints. Short seams and small chips give the limestone lip more relief above the original opening.

All 365 downward floor probes hit the expected elevations. The 25 clearance and 362 occlusion probes still pass. The bundle retains the current daylight background and the previous road materials.

```powershell
& $py early-textures/coast_bluffs.py stage $repo early-textures/m102-dressed-review --profile $slot
& $py early-textures/verify_coast_throat.py early-textures/m102-dressed-review
```
