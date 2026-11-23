"""Queue the memorial, Willow teahouse, and first Scorpion road fixtures."""

from comfy_shinomen_gate import queue_meshes


PROMPTS={
    "scorpion_memorial_stele":(
        "One restrained dark slate memorial stele inside a shallow late-medieval Japanese "
        "garden canopy, weathered square footing, small plinth ledge, aged cypress, rain "
        "darkened stone. Complete isolated game landmark on pure white, orthographic "
        "three-quarter angle, no scene, people, shadow or writing."
    ),
    "scorpion_grove_cedar":(
        "One aged Japanese cedar with a thick split trunk and tall broken vertical silhouette. "
        "Uneven limbs, deep-shadow dark foliage and roots visible all around the base. "
        "Complete isolated natural voxel-game asset on white, orthographic three-quarter "
        "view, no other trees, soil plane, scenery, people or cast shadow."
    ),
    "scorpion_willow_tea_service":(
        "One formal Japanese iron kettle beside a bamboo whisk, two modest stoneware bowls, "
        "and folded gray cloth on a low dark-red lacquer tray. Small isolated late-medieval "
        "Japanese inn game prop on white, elevated orthographic angle, fully visible and "
        "no scenery or writing."
    ),
    "scorpion_shutai_sake_store":(
        "One tight assembly of tall dark Japanese cedar sake casks with braided rice-straw "
        "bands and one closed earthenware vessel, thin cypress slatted stand. Late medieval "
        "roadside inn supplies, fully isolated game object on pure white, orthographic "
        "three-quarter view, no shadow, background scene, or writing."
    ),
    "scorpion_damp_gravel":(
        "Strict overhead tileable square game diffuse material of damp dark brown mountain "
        "gravel. Fine worn stones, small gray pebbles, deep ochre earth and moss at natural "
        "irregular intervals. Soft even light, edge-to-edge with no scenery or objects."
    ),
}


if __name__=="__main__":
    queue_meshes(PROMPTS,tuple(PROMPTS)[:-1],"scorpion-road",192767,841)
