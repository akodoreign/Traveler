# Asset pack prototype

The Git release stores packed native assets in packs, not as duplicate loose
files. Older clients should download a fresh ZIP. Local loose-file cleanup
remains a separate recoverable operation. `boot.sk` mounts `project/rtpacks/active.json`
only when present; otherwise the existing loose-file loader is unchanged.
Packed files take precedence over same-named loose files. Packed meshes, animations,
materials and PNGs are decompressed on demand and checked against their CRC.
An incomplete pack set is not mounted. This does not accelerate rendering or
reduce texture memory.

For an existing development checkout with uncommitted loose edits, a local
`rtpack-dev-loose` file in the game folder temporarily restores loose precedence.
The marker is ignored by Git and must not be used for distributed builds. Move
approved edits into a new generation and remove the marker after migration.

`tools/rt_packs.py` builds deterministic, content-versioned sets with a 49 MiB
maximum per pack and index (below GitHub's 50 MiB warning and 100 MiB block).
Files are compressed independently so that a model can be loaded without
unpacking the rest of the set. Already-compressed PNGs generally do not shrink.
The installer requires a **stopped, independently copied** profile created by
`tools/traveler_instances.py` and explicitly enabled for packs. It verifies all downloaded bytes and
assets before atomically switching the active index, keeps the previous pack
generation, and optionally removes only loose assets identical to the new or
previous verified generation. It preserves other loose files, though packed
assets take precedence at runtime.
It rejects a running profile and coordinates with the instance launcher's slot
lock. Do not start the executable directly while installing or updating.

Example, using a fresh independent profile (the copy may take substantial disk
space), with that profile stopped:

```
python tools\traveler_instances.py --profiles .\profiles provision packtest
python tools\rt_packs.py enable-test-profile .\profiles\packtest
python tools\rt_packs.py build .\profiles\packtest\project .\pack-output
python tools\rt_packs.py install-test-profile .\profiles\packtest .\pack-output\GENERATION --prune-matching
python tools\traveler_instances.py --profiles .\profiles launch packtest
```

The build command prints `GENERATION`. The output must be outside the source
project; the installer copies it into the profile. To update a stopped profile,
publish the contents of one generation directory together at an HTTPS URL and run:

```
python tools\rt_packs.py update-test-profile .\profiles\packtest https://example.com/GENERATION/active.json --prune-matching
```

Only use a trusted HTTPS origin and a pack generation built for the same game
version. The updater downloads to a private staging directory, checks size,
SHA-256 and every decoded asset, then activates atomically. An interrupted or
corrupt download leaves the prior generation active. Old generations remain on
disk for recovery, so subsequent updates can temporarily consume more space.

To rebuild after editing a complete loose source tree, supply
`--previous .\pack-output\GENERATION`. Existing members stay in their prior
shards when possible; unchanged compressed entries are reused and overflow
creates new shards. The profile updater reuses already-installed shards with
matching SHA-256 instead of downloading them. The in-game updater also reuses
same-named shards after checking their size and CRC against the release
manifest. Adding files may change the last
shard; deleting or changing a file changes its shard. Rebuilding identical input
returns the existing generation.

For a sparse edit without extracting all assets, put only additions and
replacements under `OVERLAY\resource\native_*` and use:

```
python tools\rt_packs.py build OVERLAY .\pack-output --previous .\pack-output\GENERATION --overlay --remove-list .\remove.txt
```

`remove.txt` is optional and contains exact resource-relative paths, one per
line; absent paths are preserved by default. To edit an existing asset, first run
`python tools\rt_packs.py extract .\pack-output\GENERATION OVERLAY resource/native_chara/example.mdl`.
Extraction verifies the pack and never overwrites an existing file. Paths in both
the overlay and removal list are rejected. Builds stop if the loose source changes
while being read.
For the currently installed generation, use the directory
`_tools\rpgcobo-tool\project\rtpacks\GENERATION` as `GENERATION` for both
`extract` and `build --previous`; the tools read its parent `active.json`.
An inactive older installed generation needs its own matching `active.json`.
Tests run with
`python -m unittest discover -s tools -p "test_rt_packs*.py" -v`.

An isolated full-game profile with 13,542 packed native assets and no matching
loose copies passed field (M399) and battle (M001) bot runs. Its field screenshot
differed from the loose-file baseline by a mean 0.359 per 8-bit RGB channel.
The loader uses the engine's `TempBuffer` for decompressed resources; a normal
`ByteBuffer` passed small tests but caused native crashes during full gameplay.
This verification does not cover every map, asset type, or upgrade path.

For an old-client-compatible release, `stage-compatible-release` creates a
separate overlay containing packs, their index, `version.json`, and an updated
manifest while **retaining the loose assets in that manifest**:

```
python tools\rt_packs.py stage-compatible-release .\release-candidate\rt_manifest.json .\pack-output\GENERATION .\release-overlay --version 125
```

The source manifest must describe the pack-enabled boot script, loader and
updater and must match every packed asset. The staging command does not edit
the release candidate or publish anything. Apply the overlay only to an
independently prepared release candidate and publish its files together in
one commit (or publish the version file last if the host is not atomic).
GitHub limits a single push to 2 GiB. If a generation exceeds that limit,
publish its shards in smaller versioned commits without adding them to the
release manifest, then publish the complete manifest and active index together.
Verify every published shard before activation; never expose an incomplete
generation as active. The release script does not split oversized pushes.
Alternatively, after coordination, `release_here.py "message" --scoped
--paths-file APPROVED_PATHS --pack-generation DIRECTORY` stages only the paths
listed one per line in the UTF-8 file, stages the generated overlay, and
publishes it with its normal commit/push. `--scoped` requires a clean staging
area and constructs the manifest from staged Git blobs, so unrelated working
edits are not silently included. Without `--scoped`, the legacy script stages
**all tracked changes**. It refuses pack releases if source assets or pack
integration do not match, or tracked assets change during preparation. Supply
new loader and cutover-tool paths among `paths` on their first release. It also
bundles the offline cleanup tools into the updatable game's `rtpack-tools`
folder, with instructions. Once packs are active,
subsequent releases must supply a current generation. **This command commits
and pushes immediately**; do not run it during concurrent asset edits. The
compatible release keeps old clients functional but duplicates assets and is
not used for pack-only releases.
On the first pack release, explicitly stage the new loader and
`tools\rt_packs.py` and `tools\rt_pack_cutover.py`, together with every approved
new loose asset. The preflight reports packed assets missing from the manifest.

For pack-only releases, review and stage the intended changes and remove the
generation's packed asset paths from the Git index, without deleting local work.
Use `release_here.py "message" --from-index --pack-only --pack-generation
DIRECTORY`. This mode retains the reviewed index, verifies the full generation,
and refuses a manifest that still contains its packed assets. It does not require
unstaged working files to match. Do not pre-stage generated
pack files, the runtime cleanup bundle, `version.json`, or `rt_manifest.json`.
Stage the exact working versions of `tools\release_here.py` and
`tools\rt_packs.py`, which execute the release. As with the other mode, this
command commits and pushes immediately, so run it only after review.

For an explicitly coordinated Windows installation, `tools\rt_pack_cutover.py`
provides a recoverable, offline cutover. It verifies the complete active pack
set and only selects loose files byte-identical to their packed counterparts.
The game and editors must be closed, and no one may edit that installation
during cutover. These commands do not run automatically:

```
python tools\rt_pack_cutover.py prepare PATH_TO_GAME
python tools\rt_pack_cutover.py apply PATH_TO_GAME TRANSACTION_ID
python tools\rt_pack_cutover.py seal PATH_TO_GAME TRANSACTION_ID
python tools\rt_pack_cutover.py restore PATH_TO_GAME TRANSACTION_ID
```

`prepare` records candidates; `apply` rechecks and moves them into quarantine.
Changed or newly created loose files remain on disk. Quarantine consumes disk
space until the separately invoked `seal` checks the quarantined bytes and
discards duplicates; retain the transaction and its referenced pack generation
for recovery. `restore` never overwrites existing loose files and reports
conflicts. It restores quarantined files even when packs are damaged, and
restores sealed files from the verified retained generation. If that generation
is damaged or removed after sealing, those files cannot be recovered from it.
This tool locks the game executable against startup but cannot coordinate
arbitrary external editors. Never invoke it against the live working tree
without coordinating with everyone editing it.
The bundled tools require Windows and Python 3.12 or newer; they are delivered
by the in-game updater, but Python itself is not included.

The in-game updater checks the target index, skips packed loose assets, downloads
unpacked assets normally, and activates the index only after checking all pack
files against the manifest. Older clients may require a fresh download. The
older mirror-based `release.py` does not coordinate packs; use the pack-aware
`release_here.py` path. Versioning entire packs can make small updates larger,
and Git history retains old blobs even after loose files leave the current tree.

The engine's native `.sx` reader is present, but a direct keyless
`SKPackageBuilder` probe produced an index that `SKPackage()` rejected with
`No License`; no usable package license was available in this checkout. This
prototype instead uses the engine's built-in zlib and resource interfaces.
