# Packed native assets

- Treat the active `project\rtpacks` generation as the source for packed
  `resource\native_*` models, motions, materials, and PNG textures.
- Extract assets with `tools\rt_packs.py extract` into a separate overlay before
  editing. Add new assets to the overlay; use an explicit `--remove-list` for
  removals. Build with `--previous` and `--overlay`, then verify the generation
  before publication. Do not edit pack files in place.
- Packed assets take precedence over same-named loose files. Loose assets may
  contain uncommitted work: preserve them and incorporate approved edits into a
  new generation. Use the recoverable stopped-game cutover for local cleanup.
- Do not add packed loose assets back to Git. Older clients must download a fresh
  ZIP. Follow `docs\asset-pack-prototype.md` for releases and cleanup.
