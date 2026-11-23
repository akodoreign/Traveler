"""Generate the Zumiki ice cave, Doji tide cave, and Phoenix fox cave props."""
from comfy_shinomen_gate import queue_meshes

PROMPTS = {
    "zumiki_ice_cave_crystal_curtain": (
        "Group of attached tapered clear cerulean ice columns and hanging icicles for a snowy Japanese "
        "diorama cave, deep lapis cores, ice-blue reflections and clean off-white edges, saturated natural "
        "blue. Continuous three-dimensional miniature, complete isolated three-quarter on pure white, "
        "no base, ground, background, floor shadows, writing or people."
    ),
    "doji_tide_cave_marker": (
        "One weathered Japanese sandstone tide marker for a late medieval shoreline, tapered carved "
        "stone column with horizontal water marks and a deep crane-blue tied cord. Warm pale stone above, "
        "ocher barnacles below, elegant clean miniature railroad diorama craftsmanship. Complete isolated "
        "elevated three-quarter on pure white, no scenery, floor, text, writing or people."
    ),
    "phoenix_fox_cave_votive_pair": (
        "Two small distinct weathered vermilion-stained Japanese stone fox shrine figurines with "
        "rich scarlet bibs at the foot of a low basalt votive slab, miniature diorama hand-painted finish, "
        "deep red and honey amber highlights, intentional clean silhouette. Complete isolated three-quarter "
        "on pure white, no floor, shadows, scene, people, or writing."
    )
}
if __name__=="__main__":
    queue_meshes(PROMPTS, tuple(PROMPTS), "ice-tide-fox-branch-caves", 613374, 6411)
