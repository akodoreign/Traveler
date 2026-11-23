"""Generate the Coast Road Egg Caves' limestone and underground prop references."""

from comfy_furnace import generate

PROMPTS = {
    "egg_limestone": ("Game texture scan. Direct flat orthographic view of natural light olive gray coastal cave "
        "limestone with gently layered rough eroded strata. Damp pits and alternating thick beds, occasional "
        "thin dark mineral streaks, off-white calcite. Even soft neutral light only, all four edges filled with "
        "the same stone, no perspective or scene or objects. Irregular coherent rock strata throughout."),
    "egg_silt": ("Realistic top down orthographic diffuse texture of mottled fine cave mud and mineral silt, "
        "old ochre stone chips with cool dark gray green damp patches and pale tan sandy grains. Fine detail, "
        "chunk scale one or two fingers wide. Even soft lighting. Square tiled flat scan, no plants no framed view."),
    "egg_calcite": ("Isolated cave formation, one group of up to four calcite stalagmites fused at the base, "
        "wide gently stepped fluted bases tapering into softly rounded broken points, mottled warm limestone "
        "with cream mineral streaks. Realistic detail in a fine voxel 3d game asset. Orthographic three-quarter "
        "view, white surrounding background, no people or text or landscape."),
    "egg_nest": ("One low round broad handwoven animal nest made of irregular thin straw, river reeds, "
        "twigs and brown dry grass, shallow center and double uneven ring, realistic straw texture, "
        "no eggs and no other item, isolated entire object, orthographic three-quarter view on pure white, "
        "no background floor, no words."),
}

if __name__ == "__main__":
    generate(PROMPTS, "comfy-egg-caves-receipts.json", 438251)
