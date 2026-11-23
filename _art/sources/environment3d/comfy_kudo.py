"""Queue market and riverside source assets for the Kudo map family."""

from comfy_shinomen_gate import queue_meshes


PROMPTS = {
    "kudo_cargo_boat": (
        "Single narrow late-Sengoku Japanese river punt, shallow open planked wooden hull with two low "
        "thwarts, one folded mulberry red cloth bundle in the bow, an old wooden oar laid lengthwise. "
        "Worn cedar with dark waterline. Complete isolated game prop, orthographic three-quarter on "
        "pure white, no water, ground, shadow, writing, person or buildings."
    ),
    "kudo_reed_bank": (
        "One low irregular cluster of Japanese riverbank reeds and sedges, long gently bowed tawny "
        "seedheads with dark olive blades, pale yellow older strands; roots close together. Complete "
        "isolated foliage asset, orthographic three-quarter image on white, no visible mud or pot, "
        "no scenery, shadow or writing."
    ),
    "kudo_eel_basket": (
        "Single hand-woven tapered oval Japanese freshwater eel basket with its lid secured, narrow "
        "upright bamboo slats and rough mid-brown weaving, thick dark wet lower ends, hemp carrying handle. "
        "Complete orthographic three-quarter game object on flat white, no floor, figures or text."
    ),
    "kudo_river_lantern": (
        "Single freestanding traditional small Japanese dock lantern on a short weathered cedar post, "
        "rectangular box enclosure of warm faded paper with thin black timber lattices, blue-black "
        "weatherproof cap, rope collar. No electronics. Whole isolated asset on pure white, "
        "three-quarter orthographic, no floor, text or shadows."
    ),
    "kudo_river_silt": (
        "Strict overhead orthographic game material sample of damp tawny gray river silt with dense "
        "fine dark pebbles and natural water-worn shallow ridges, tileable edge to edge, subtle "
        "feature scale, diffuse natural light, no horizon, buildings, plants, text or props."
    ),
}


if __name__=="__main__":
    queue_meshes(PROMPTS,tuple(PROMPTS)[:-1],"kudo",712521,551)
