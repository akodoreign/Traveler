"""Generate memorial garden pond and tea pavilion pieces."""

from comfy_shinomen_gate import queue_meshes


PROMPTS={
    "bayushi_pond_koi":(
        "One single Japanese koi carp for a game pond, rich vermilion red and warm white "
        "scale pattern with distinct charcoal dashes. Straight horizontal relaxed swimming "
        "pose, spread fins and a clear side profile in orthographic three-quarter view "
        "slightly from above. Fully isolated on solid white, with no shadows, water or scene."
    ),
    "bayushi_water_lilies":(
        "One compact floating group of three dark green rounded lily pads with visible "
        "veins and a single soft pink-white lotus flower with a warm gold center. Fully "
        "isolated small voxel-game asset on pure white, orthographic three-quarter view "
        "from above, no water, roots, scene, shadows or writing."
    ),
    "bayushi_pond_basin":(
        "Single late-medieval Japanese carved dark granite water basin with a short "
        "bamboo water spout joint and a few smooth rounded damp stones at its feet. "
        "Dense bluish gray textured stone, moss green lower edges, weathered golden "
        "bamboo. Complete isolated game prop on white, orthographic three-quarter view, "
        "no scene, people, floor, text or shadows."
    ),
    "bayushi_garden_moss":(
        "Strict overhead high-detail edge-to-edge diffuse material scan of deep emerald "
        "moss and soft short foliage between worn gray-black gravel in a shaded Japanese "
        "garden. Natural uneven scale, rich greens, matte soft even light, no scenery, "
        "objects, paths drawn into it, symbols or shadows."
    ),
}


if __name__=="__main__":
    queue_meshes(PROMPTS,tuple(PROMPTS)[:-1],"bayushi-garden",197057,865)
