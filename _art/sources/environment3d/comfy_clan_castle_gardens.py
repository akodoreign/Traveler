"""Generate objects used in castle gardens and clan activities."""
from comfy_shinomen_gate import queue_meshes

PROMPTS = {
    "castle_iris_clump": "A single airy clump of purple Japanese water iris with upright narrow leaves, two violet blooms and one closed bud, little model railway diorama plant. Complete isolated orthographic elevated game asset on pure white, no ground, roots platform, text, shadow, reflections or container.",
    "castle_tamori_stones": "One natural arrangement of three gray Japanese zen garden stones on a hand-built miniature railway diorama, one tall split stone and two lower companions, all contacting the ground. Weathered irregular coarse slate with a small amount of dark moss. Isolated on a solid white background, no earth bed, foliage, shadow, plinth or text.",
    "castle_unicorn_saddle": "One sixteenth century Japanese riding saddle on its compact oak stand with a folded rich dark plum brocade saddle cloth. Brown wood stirrups, laced leather. Complete miniature railway diorama stable prop in orthographic three-quarter view, isolated on white, no horse, objects, text, floor, shadow or backdrop.",
    "castle_bayushi_mask_stand": "One Sengoku Japanese performing arts display prop: a small freestanding lacquered cedar tabletop rail holding three handmade theatrical masks, simple face-shaped masks in warm white, black, and deep cinnabar with red silk ties. Isolated full silhouette in orthographic three-quarter view on pure white, no bench, human, ground, text or shadow.",
}
if __name__ == "__main__":
    queue_meshes(PROMPTS, tuple(PROMPTS), "clan-castle-gardens", 814637, 1730)
