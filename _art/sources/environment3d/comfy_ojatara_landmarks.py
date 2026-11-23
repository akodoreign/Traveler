"""Queue bell hill, tribunal, and Perfume Petal Blossom fixtures."""

from comfy_shinomen_gate import queue_meshes


PROMPTS = {
    "ojatara_yotomo_bell": (
        "Single large antique Japanese bonsho bronze temple bell suspended from a simple "
        "open cedar bell stand, pale green patina and plainly visible bottom rim. The space "
        "inside its open bottom is empty. Straight cedar legs and rope suspension, original "
        "voxel-game prop on pure white, orthographic three-quarter view without scenery."
    ),
    "ojatara_tribunal_seat": (
        "One formal low sixteenth-century Japanese official's tribunal bench and writing "
        "table, aged cypress trestles, deep indigo cushion, narrow cypress surface with "
        "tied paper petitions. Fully isolated on pure white, complete stylized game prop, "
        "elevated orthographic three-quarter angle, no people, scene, shadows or text."
    ),
    "ojatara_flower_planter": (
        "Single rustic low Japanese bark-and-cedar planter, large fragrant pale plum "
        "blossoms and soft cream petals between short bent twig stems. Slight moss, warm "
        "brown handmade joinery. Complete isolated voxel game prop on pure white with "
        "space around it, elevated orthographic angle, no ground or writing."
    ),
    "ojatara_grave_marker": (
        "Small understated weathered Japanese memorial on a dark mountain grave path. "
        "Two upright rough slate memorial stones, one lower stone and a tiny bowl at their "
        "feet. Faint pale lichen, hand-carved rounded corners, no legible marks. Isolated "
        "complete voxel game prop on a pure white background, elevated orthographic angle."
    ),
    "ojatara_rain_stone": (
        "Flat overhead seamless diffuse game texture scan of wet dark Japanese mountain "
        "footpath slate. Fine angular grains, mottled walnut and cool charcoal, muted "
        "soft light and no hard reflections. Edge to edge, no scenery, objects or text."
    ),
}


if __name__ == "__main__":
    queue_meshes(PROMPTS, tuple(PROMPTS)[:-1], "ojatara-landmarks", 187165, 791)
