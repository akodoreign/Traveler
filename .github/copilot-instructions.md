# Packed native assets

- Treat the active `project\rtpacks` generation as the source for packed
  `resource\native_*` models, motions, materials, and PNG textures.
- Extract assets with `tools\rt_packs.py extract` into a separate overlay before
  editing. Add new assets to the overlay; use an explicit `--remove-list` for
  removals. Build with `--previous` and `--overlay`, then verify the generation
  before publication. Do not edit pack files in place.
- Loose assets may be local overrides or uncommitted work. Never discard them
  merely because a packed asset has the same path; only remove files proven
  byte-identical to the active pack, using the recoverable stopped-game cutover.
- Preserve compatibility with clients that have not installed the pack loader.
  Follow `docs\asset-pack-prototype.md` for release and cleanup procedures.
