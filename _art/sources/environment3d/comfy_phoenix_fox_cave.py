"""Queue miniature props for the northern Phoenix trail and the fox cave."""
from comfy_shinomen_gate import queue_meshes

PROMPTS={
    "phoenix_cave_fox_offering_table": (
        "A low Sengoku-period rural Japanese shrine offering bench in dark red lacquered cypress, "
        "sitting on two separate stout supports, with a small wrapped rice offering and two white "
        "ceramic sake vessels. Textured model railway miniature with crisp legible wood joinery. "
        "Whole standalone prop on white, elevated three-quarter view, even light, no floor, "
        "cast shadow, text, handles, additional shrine or people."
    ),
    "phoenix_north_road_trail_stele": (
        "One sculptural waist-high natural split dark gray and indigo field-stone marker from a mountain "
        "trail in Sengoku Japan, flecks of feldspar and moss entirely on the stone, tied with a single "
        "saffron braided sacred rope and restrained white zigzag paper. Model railway scenery, saturated "
        "local color, compact silhouette, no text, floor, outdoor backdrop, shadow or people."
    ),
}

if __name__=="__main__":
    queue_meshes(PROMPTS,tuple(PROMPTS),"phoenix-fox-cave-details",852711,7217)
