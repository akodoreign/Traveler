"""Queue the command tent, funerary table and burnt Shioden timber."""

from comfy_shinomen_gate import queue_meshes


PROMPTS = {
    "ojatara_white_canopy": (
        "A freestanding shelter for a late sixteenth-century Japanese command outpost, "
        "tall undyed off-white oiled cloth roof with two faint wine-red ties, six dark "
        "cedar poles and widely open front. Complete isolated game prop on pure white, "
        "three-quarter orthographic, no ground, people, shadow or lettering."
    ),
    "ojatara_funeral_offering": (
        "A restrained Japanese mountain manor memorial table, weathered narrow dark "
        "cypress, one shallow ceramic dish of folded linen, an unmarked paper plaque and "
        "a few faded white flowers in a brown stoneware jar. Single isolated game prop "
        "on full white, elevated orthographic angle, no person, scene or lettering."
    ),
    "ojatara_collapsed_timber": (
        "One compact section of a burned Japanese cypress manor after collapse: four "
        "charred beams, two blackened plank ends, gray ash on patches of worn brown "
        "charcoal, precise squared late-medieval joinery. Isolated complete voxel game "
        "prop on white, elevated three-quarter orthographic, no fire, scenery or words."
    ),
    "ojatara_autumn_meadow": (
        "Seamless overhead square game diffuse material of mottled autumn foothill grass "
        "in rural Japan, low faded green blades, some amber hay and dusty earth. Quiet "
        "fine organic pattern, flat even light, edge to edge without scenery or objects."
    ),
}


if __name__ == "__main__":
    queue_meshes(PROMPTS, tuple(PROMPTS)[:-1], "ojatara-camp", 188213, 819)
