"""Queue props for the River of Gold cave, Lion hill cave, and the old mine."""
from comfy_shinomen_gate import queue_meshes

PROMPTS = {
    "river_cave_water_polished_boulder": (
        "One small group of rounded, water-polished limestone boulders, with vivid lapis and ochre mineral "
        "seams and bright green moss in the top cracks. Graded deep blue shadows, no grain noise, miniature "
        "model-railroad diorama scale and complete readable silhouette. Isolated raised three-quarter angle "
        "on pure white, no water, ground slab, text, shadows or scenery."
    ),
    "lion_cave_ocher_standing_stone": (
        "One eroded amber sandstone standing stone with an old chiseled lion paw emblem on the face, "
        "for a Japanese fantasy hill cave. Ochre mineral planes, fine red veins beneath a lacquer-orange "
        "votive cord. Strong layered rock texture but clean silhouette. Complete isolated three-quarter "
        "on pure white, no ground slab, text, cast shadow or background."
    ),
    "lion_cave_old_mine_ore_basket": (
        "One old Japanese wooden mine ore sledge carrying a large dark wicker work basket and a few "
        "rich ochre stone chunks. Tied dark wood joints and iron runner plates, soft copper tint at the "
        "edges, 1:24 miniature diorama prop, readable clean forms. Complete isolated elevated three-quarter "
        "view on pure white, no ground, text, shadows, people or background."
    ),
}
if __name__=="__main__":
    queue_meshes(PROMPTS, tuple(PROMPTS), "river-and-lion-branch-caves", 499726, 4651)
