"""Generate structures for the Yasuki sea cave and its connected smugglers' route."""
from comfy_shinomen_gate import queue_meshes

PROMPTS = {
    "yasuki_cave_tide_scored_rocks": (
        "A single isolated hand-built 1:24 seaside railway diorama rock section, "
        "layered rough dark cobalt slate with blunt ochre mineral strips and pale barnacle clusters "
        "at the lower edge, broad convincing coastal erosion, finely textured with deep wet blue cracks. "
        "Rich dark color with natural relief. Complete isolated three-quarter object on flat white, "
        "no ground plane, cast shadow, text, water surface, frame or people."
    ),
    "yasuki_cave_boat_landing": (
        "A compact late medieval Japanese fishing and smuggler sea-cave landing, "
        "complete stained black cedar plank platform, thick timber legs, irregular plank ends, "
        "two tied mooring cleats and subtle manila rope loops. Deep navy Yasuki accents beside colored wood, "
        "clean 1:24 miniature game prop. Complete isolated elevated three-quarter view on flat white, "
        "no underlying ground, water, lettering, frame, shadow or people."
    ),
    "yasuki_cave_covered_supply_bales": (
        "A single tight rounded pile of three sixteenth-century Japanese smuggler supply bales in a damp sea cave, "
        "woven golden straw and dark walnut ropes under a partly opened deep indigo waxed cloth, "
        "glints of gold stitching, textured miniature diorama furniture. Complete three-quarter view on flat white, "
        "no platform, floor, background, cast shadow, text, water or people."
    ),
}
if __name__ == "__main__":
    queue_meshes(PROMPTS, tuple(PROMPTS), "yasuki-sea-cave", 1058824, 3826)
