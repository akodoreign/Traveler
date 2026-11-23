"""Queue the original scene props for the chapter-three Shadowlands march."""

from comfy_shinomen_gate import queue_meshes


PROMPTS = {
    "tainted_poppy_clump": (
        "One small irregular clump of eight deep crimson wild Japanese poppy flowers with dark purple "
        "centers, thin stems and blue-green basal leaves. Some blossoms face diagonally, three partially "
        "closed buds. Photoreal stylized dark fantasy vegetation, complete isolated asset on pure white, "
        "orthographic raised three-quarter view, no pot, ground plane, shadow, text or person."
    ),
    "shadowlands_tar_bridge_end": (
        "Single smashed end of a narrow rugged Japanese wooden footbridge from a dark fantasy wasteland. "
        "Cedar crossbeam, two split rail posts and a few uneven gray planks with charcoal tar on the "
        "lowest edges. No long bridge attached. Complete isolated object, orthographic on pure white, "
        "no ground, person, writing or shadow."
    ),
    "shadowlands_obsidian_tree": (
        "One supernatural burned Japanese tree of fractured black obsidian, with a charcoal trunk splitting "
        "into three warped claw-like limbs and thin dull orange molten veins at the lower roots. Rugged "
        "bark-like obsidian facets retain a strongly tree-shaped silhouette. Complete isolated stylized "
        "dark fantasy prop in three-quarter view on white, no ground, shadows, smoke, text or foliage."
    ),
    "shadowlands_watchpost_winch": (
        "Single weathered late-medieval Japanese fortification timber winch and hemp cable, two upright "
        "cedar supports, a wooden drum with coiled rope and iron handle, blackened on one side. Complete "
        "isolated gameplay prop orthographic on clean white, no ground, shadow, person, text or background."
    ),
    "toshi_kijo_gravestone": (
        "One weathered broken Japanese medieval five-ring stone memorial with a chipped square base and "
        "slumped top, dark moss in a fracture, pale blue gray mountain stone, one short length of old "
        "unbleached rope. Completely isolated on white, orthographic raised three-quarter view, "
        "no text, person, ground surface, shadow or scenery."
    ),
    "shadowlands_ochre_ash": (
        "Flat strictly overhead texture only, warm ashen volcanic grit and long pale grey flakes "
        "mixed with ocher loess and deep dry cracks. Weathered dark fantasy field material, square "
        "tileable uniform photographic scale, edge to edge, diffuse illumination, no scenery, text or objects."
    ),
}


if __name__=="__main__":
    queue_meshes(PROMPTS,tuple(PROMPTS)[:-1],"shadowlands-march",783919,501)
