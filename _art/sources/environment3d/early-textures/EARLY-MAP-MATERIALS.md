# Early-map material pass

The Coast Road uses a continuous ground atlas tied to the approved daylight colors. The sand, carriage lane, and grass edge share one world-space projection. The cliff uses Rock 01 diffuse and normal scans with short slanted fractures. Interlocking seawall courses have gently rounded faces and darker splash marks close to the water.

The Kaiu Garrison uses its original tile sizes with additional masonry and cedar relief. Hoshi-no-Ichi receives a continuous track and verge atlas and a separate scanned rock surface. Town props, stage geometry, encounter tables, gates, and doors use their verified rows.

| Map | Candidate | Original quads |
| --- | --- | ---: |
| M102 Coast Road | m102-finish | 4,384 |
| M101 Kaiu Garrison | m101-review | 542 |
| M103 Hoshi-no-Ichi | m103-review | 793 |

Run from the Coast Road working folder. For M102, install the final coast color candidate in the same profile first. The material recipe merges its terrain key onto the currently staged row, so the color preset, water, and plant color remain available for the native review.

```powershell
$py = 'C:/AI/comfy-3d/venv/Scripts/python.exe'
& $py early-textures/early_materials.py stage $repo early-textures/m102-finish --profile $slot
& $py run_preview.py $repo M102 --profile $slot
```

The source and candidate vertex positions are byte-equal in all three maps. The exporter adds tangents and material-local normals and preserves the original triangle winding. Each receipt fingerprints the collision map and verifies the story row and every staged resource. The repeated offline install left all unrelated rows equal across 314 maps. The identical command with `publish` compares the profile's exact approved terrain and row with the candidate before writing to the live checkout.

The finish candidate can stage over the graded Coast Road or its first material review. Its ground diffuse and normal PNGs match the first review byte for byte. Use `--finish` during preparation to rebuild the revised materials with the selected coast grade bundle.
