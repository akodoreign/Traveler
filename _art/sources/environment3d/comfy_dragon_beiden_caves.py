"""Queue meshes for the Dragon mountain cave and Beiden bandit hideout."""
from comfy_shinomen_gate import queue_meshes

PROMPTS = {
    "dragon_cave_mountain_shale": (
        "One broad natural green-black alpine shale outcrop, fractured sloping dark jade plates, "
        "saturated evergreen moss in a few seams and warm quartz flecks as accents. Tiny Japanese railway "
        "diorama feel. Readable eroded silhouette. One isolated complete elevated three-quarter prop "
        "on white, no floor, people, text or backdrop."
    ),
    "beiden_cave_bandit_folding_cot": (
        "A low sixteenth-century Japanese rough campsite cot or sleeping bench, worn red-brown cedar "
        "frame, rolled dark russet wool blanket and flax pillow. Compact miniature with real material "
        "texture and distinct posts. Entire isolated miniature on pure white, no cast shadows, sign, "
        "floor, text, weapons or scene."
    ),
    "beiden_cave_bandit_sack_rack": (
        "A shallow Japanese trail storehouse rack made of dark cedar, three tightly tied cloth "
        "provision sacks with moss green, tobacco brown and indigo dyes, worn rope bindings, wooden "
        "peg joinery. One continuous tiny railroad diorama prop on plain white, no floor, writing, "
        "cast shadow, backdrop or people."
    ),
}
if __name__ == "__main__":
    queue_meshes(PROMPTS, tuple(PROMPTS), "dragon-beiden-branch-caves", 844221, 7169)
