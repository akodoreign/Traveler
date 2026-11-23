"""Generate temple-path props for Kamen no Toshi."""

from comfy_shinomen_gate import queue_meshes


PROMPTS = {
    "kamen_sewn_face_shrine": (
        "Small standing Japanese fantasy temple shrine made of aged black cedar, a slightly "
        "slanted blue-gray kawara roof, three pale sewn cloth masks respectfully hanging "
        "from the crossbar, worn granite footing. Single complete isolated voxel-game prop, "
        "three-quarter orthographic on white, no people, ground, shadows, gore or writing."
    ),
    "kamen_sun_statue": (
        "Small damaged Japanese fantasy temple statue of a sun goddess, seated on a simple "
        "stone plinth, round relief halo with worn rays behind the crown. A large old dry "
        "crack in the granite and moss at the base. Complete isolated game object on white, "
        "elevated orthographic three-quarter view, no ground, people, scenery or shadow."
    ),
    "kamen_temple_andon": (
        "A single low late Sengoku Japanese temple floor lantern, tall thin warm paper "
        "casing in a dark square cypress lattice, raised square granite foot and gently "
        "slanted cap. Wax paper seam and mild smoke staining. Isolated game prop on pure "
        "white, elevated orthographic three-quarter view, no ground, scene, text or shadows."
    ),
    "kamen_rotted_sleep_mat": (
        "One low discarded woven rice-straw sleeping mat, half rolled into a soft uneven "
        "cylinder with worn tan edges, dark red cloth repair and two thin binding cords. "
        "Complete compact isolated Japanese monastery voxel-game prop on white, elevated "
        "orthographic angle, no one on it, no ground, perspective backdrop, shadows or words."
    ),
    "kamen_temple_rock": (
        "Strict straight-down close square diffuse albedo of gray-green faulted Japanese "
        "temple cave rock, near-black narrow cracks and subtle warm candle smoke stains, "
        "organic worn limestone grain, even light. Edge to edge material scan, no scenery, "
        "objects, horizon, glyphs or highlights."
    ),
}


if __name__ == "__main__":
    queue_meshes(PROMPTS, tuple(PROMPTS)[:-1], "kamen-temple", 185127, 777)
