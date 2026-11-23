"""Queue the west-marsh landmarks and riverbank materials."""

from comfy_shinomen_gate import queue_meshes


PROMPTS = {
    "kudo_marsh_barge": (
        "A single full shallow sixteenth-century Japanese plank cargo barge, abandoned with "
        "dark water-stained wood and one plain wet quilt covering the cargo in the center. "
        "Low outline, broken prow, loose coil of hemp rope and reeds caught in the hull. No figures "
        "or bodies. Complete isolated three-quarter orthographic game asset on a pure white background, "
        "no visible water, floor, scenery, shadow or words."
    ),
    "kudo_sap_willow": (
        "Single gnarled Japanese willow tree in a haunted wetland, split gray trunk with short dark "
        "rust streaks of botanical sap and irregular sparse pale green leaves, knots and visible twisting "
        "roots. No gore, no anthropomorphic face. Complete isolated stylized 3D game prop, slightly elevated "
        "three-quarter orthographic view, white background, no floor, shadow, text or other plants."
    ),
    "kudo_ford_slab": (
        "One deliberately hewn flat broad irregular stepping stone, low weathered dark granite slab with "
        "pale water-worn edges and a trace of green moss below its top, broad gripping surface. Completely "
        "isolated orthographic three-quarter asset on white, no ground plane, water, objects or labels."
    ),
    "kudo_miya_casket": (
        "One very small weatherworn Japanese medieval dark wooden ritual casket with worn brass corners, "
        "slightly open lid, three dull white quartz chunks visible inside. Mud staining and old moss around "
        "feet. Complete isolated stylized orthographic game prop on plain white, no shadows, text or ground."
    ),
    "kudo_marsh_silt": (
        "Overhead orthographic dark fantasy texture scan of earthy olive-gray wet silt, small dark "
        "pebbles, occasional patches of fine iron-red clay and uneven ripple marks. Diffuse overcast "
        "lighting, square tileable edge to edge, no objects, perspective, shadows or vegetation."
    ),
}


if __name__=="__main__":
    queue_meshes(PROMPTS,tuple(PROMPTS)[:-1],"kudo-marsh",889221,611)
