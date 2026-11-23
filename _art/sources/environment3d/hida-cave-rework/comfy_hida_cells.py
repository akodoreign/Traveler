"""Queue props for the next pass through the Hida cells and trap galleries."""
from comfy_shinomen_gate import queue_meshes

PROMPTS={
    "hida_cell_cedar_bench": (
        "One low Sengoku-period Japanese guardroom bench, aged smoked cedar with clear pegs, "
        "a neatly folded indigo sitting cloth, and small scuffs. Strong clean silhouette and "
        "subtle middle-scale wood grain, tabletop model railroad miniature. Complete standalone "
        "object on plain white, an elevated three-quarter view, no writing, cast shadow, floor, "
        "scene, chains, bars or people."
    ),
    "hida_cell_iron_lamp": (
        "One compact Japanese stone-corridor oil lamp, black forged iron cage on a squared "
        "smoked cedar support, warm cream oiled paper inside, small old brass fittings. "
        "Model railway diorama, clean physical material relief, amber and deep charcoal. "
        "Standalone complete lamp on pure white, no cast shadow, letters, scene or people."
    ),
    "hida_catacomb_basalt_drains": (
        "One compact natural rainy Japanese stone drainage channel, three adjacent dark "
        "volcanic rock steps with amber quartz seams and a simple narrow water-cut groove. "
        "Historic Japanese castle foundation scenic prop, dark cobalt-gray rock with clearly "
        "readable eroded edges and restrained realistic grain. Complete isolated diorama "
        "piece on pure white, no water splash, people, writing, floor or cast shadow."
    ),
}

if __name__=="__main__":
    queue_meshes(PROMPTS,tuple(PROMPTS),"hida-cells-and-drains",878331,7413)
