# Hut and barrel replacements

## Confirmed screenshot location

The roadside structure in the screenshot matches the Dragon procession road, M382. Its placement lines up with the adjacent bell, cedar, rear boulder, and lamp. The published model is `dragon_slate_waystation` at (49.75, 3.5, 12.75). The same model appears in the Dragon mountain town, M379, at (51.25, 2, 11.75).

`dragon_roadside_shelter.py` builds a new waiting shelter with an open front, a bench, distinct slate courses, and a restrained wood palette. The `dragon-waystation-replacement.json` receipt carries before and after versions of both environment rows, their exact placement changes, and the model and texture hashes. The swap keeps all transforms and requires no terrain, event, or runtime edit. Review both native placements before installing.

## New Cakon kits

`cakon_huts.py` exports models with bottom-center origins and entrances facing negative Z. The sizes below are world units in X, Y, Z order.

| Model | Size | Intended placement |
|---|---|---|
| `cakon_riverside_hut` | 2.34 × 1.68 × 1.84 | M414 behind the riverbank, centered at world X 34, 38 and 42, Z 12.75 |
| `cakon_hamlet_hut` | 2.86 × 2.17 × 2.36 | M418 on the original 2.5 × 2 hut footprints |
| `cakon_hamlet_shrine` | 4.84 × 3.00 × 3.28 | M418 on the original shrine roof footprint |
| `cakon_staved_barrel` | 0.65 × 0.82 × 0.65 | Closed barrel with tapered staves and narrow bands |
| `cakon_staved_barrel_lid` | 0.532 × 0.065 × 0.532 | Independent lid for a matching barrel placement |

The hut doors are closed scenery. Keep the stage's existing event and collision footprint behavior when replacing the old fill blocks.

## Prepared river cooperage

`river_cooperage.py` builds two footprint-fit candidates. The `river-cooperage-replacement.json` receipt lists the existing rows, proposed rows, and dependency hashes.

- M349, Shutai. Replace five `scorpion_shutai_sake_store` props with `shutai_fitted_sake_casks`. The new rack, tall rope-banded cask, and small earthenware jar fit the old footprint.
- M877, vat chamber arena. Replace six `autumn_yotomo_storage_vat` placements with `yotomo_fitted_storage_vat`. Check the wood-block vats baked into the arena during the native preview.
- M398, Yotomo vat chamber. Five native vat placements share the old model key. Three also overlap the legacy `EP212` sprites at events `#82#`, `#83#`, and `#84#`. Resolve those overlapping visuals in the same pass as the swap and preserve the rest of the encounter layout.
- M396, Yotomo village. Four `autumn_yotomo_pigeon_house` placements need separate review. Their elevated silhouette, perforations, and perches are part of the intended prop.

The catalog has 1,757 stock `EP212` barrel sprite events across 125 maps. Existing conditions gate 1,692 of them. Keep those event lifecycles when updating their visual asset so a cleared barricade stays clear. The four Cakon interiors M967, M968, M970, and M971 each have one ungated stock barrel.
