"""Queue original furniture and a small stable pony for Traveler's Hida pass."""
from comfy_shinomen_gate import queue_meshes


PROMPTS = {
    "hida_siege_serving_tray": (
        "Single historic small Japanese castle serving tray with a smoked-red low lacquered tray, "
        "two cream ceramic sake cups and squat blue-grey lidded sake bottle fixed on the tray. "
        "Quiet court service, restrained 1500s shape, rich garnet and indigo accents. "
        "One complete isolated 3D miniature, elevated three-quarter orthographic on white. "
        "No figure, ground, backdrop, writing or shadow."
    ),
    "hida_siege_archive_cabinet": (
        "One sixteenth-century Japanese noble household cabinet, small low smoked cedar "
        "paper and scroll cabinet with three full-width drawers, black iron ring pulls, "
        "rich lacquered oxblood drawer fronts, deep navy bindings on three parchment "
        "scrolls resting on it. Clean joinery and silhouette. Complete standalone "
        "model railway diorama piece on white, no writing, floor, figures or cast shadow."
    ),
    "hida_tethered_bay_pony": (
        "A single short sturdy bay Japanese mountain pony, standing in a quiet neutral stance "
        "on four straight, clearly separated legs, with black mane, narrow cream forehead mark, "
        "black tail, warm chestnut brown coat, simple dark brown rope halter, no saddle or rider. "
        "Beautiful realistic fine miniature animal for a model railway diorama. The complete "
        "pony including all four hooves and tail, three quarter side view, pure white background, "
        "no lead pole, ground, scenery, text or shadows."
    ),
}

if __name__ == "__main__":
    queue_meshes(PROMPTS, tuple(PROMPTS), "hida-siege-decor", 882043, 7591)
