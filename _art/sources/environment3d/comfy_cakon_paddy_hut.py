"""Generate the matched environmental props for Cakon's paddies and clay hut."""
from comfy_shinomen_gate import queue_meshes

PROMPTS = {
    "cakon_rice_scarecrow": "One rustic late medieval Japanese rice-field scarecrow tied to a crooked dark cedar stake, loosely hanging faded indigo work jacket with a small tawny straw hat and visible rough straw hands. Small-scale miniature railroad diorama prop, readable full front three-quarter silhouette on pure white, no person, tree, ground, sign or shadow.",
    "cakon_paddy_sluice": "A compact late medieval Japanese handmade cedar rice-paddy sluice, dark close-set planks inside two worn stone cheeks, subtle moss and iron pegs, wide foot opening under a fixed wooden crossbar. Complete isolated scratch-built miniature diorama prop, orthographic three-quarter view, plain pure white, no terrain, water, text or shadow.",
    "cakon_tomie_clay_dome": "One small late medieval fantasy Japanese isolated rough straw-tempered clay dome hut, shaped by hand over a curved bamboo frame. Dark earth-red ochre matte surface, shallow organic shrinkage in restrained scale, a recessed open dark doorway in the front and exposed bamboo lashings under the doorway arch. No second house, ground, people, fire, signs, text or shadow. Scratch-built railway diorama prop on pure white.",
}
if __name__ == "__main__":
    queue_meshes(PROMPTS, tuple(PROMPTS), "cakon-paddy-hut-props", 815440, 1758)
