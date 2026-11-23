"""Queue original props for the remaining volcanic stair and shrine maps."""
from comfy_shinomen_gate import queue_meshes

PROMPTS={
    "volcano_cave_rope_waymarker": (
        "One compact Sengoku Japanese mountain pilgrimage trail marker carved from natural black "
        "basalt with a flattened top, tied around the middle with amber braided rice straw and "
        "three short cream paper strips. Real basalt texture, clearly readable detailed miniature. "
        "Complete upright mesh reference on white, no terrain, signs, writing, statue, people or shadows."
    ),
    "volcano_cave_crusted_lava_bank": (
        "One horizontal miniature volcanic lava shelf, heavy irregular jagged black basalt crust "
        "with deep fire-orange and yellow hot cracks along one side and charred surfaces. Strong "
        "crisp profile, real detailed basalt, tabletop railway diorama scenery. Isolated entire asset "
        "on plain white, no floor, scene, smoke, fireball, light rays, cast shadow or text."
    ),
    "volcano_cave_bronze_lantern": (
        "One dark cast bronze Japanese pilgrimage lantern on a squat natural basalt fieldstone foot. "
        "Rich umber and jade verdigris, cream parchment in the little window, a quiet golden glow only "
        "within the lantern, flared simple bronze roof. Tiny model railway diorama with physically "
        "real materials. Complete standalone game prop from elevated three-quarter view on white, "
        "no letters, smoke, people, floor, cast shadow or scenery."
    ),
}

if __name__=="__main__":
    queue_meshes(PROMPTS,tuple(PROMPTS),"volcanic-cave-details",863855,7352)
