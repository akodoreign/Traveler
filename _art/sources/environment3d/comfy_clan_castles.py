"""Generate castle furnishings and finishes in the local Comfy instance."""
from comfy_shinomen_gate import queue_meshes

MODELS = {
    "castle_kaiu_lantern": "One compact Japanese Sengoku castle stone lantern with square dark iron flame cage, small folded slate roof and carved charcoal granite pedestal, functional and weathered, fine granular textures. Complete isolated miniature railway diorama prop in orthographic three-quarter view on pure white. No floor, terrain, lettering, fire bloom or shadow.",
    "castle_lacquer_supply_chest": "One freestanding late medieval Japanese nagamochi castle storage chest, long low rectangular honey-brown lacquered cedar with charcoal wrought-iron strap hinges and small bronze loop handles. Wood grain and worn corners, true scale miniature diorama look. Closed lid, isolated elevated three-quarter view on white, no platform, text, shadow or surroundings.",
    "castle_council_table": "One low sixteenth century Japanese castle council writing table, dark satin keyaki lacquer, straight plank top and small curved legs. One rolled pale silk map rests on the top with an ink stone. Rich brown wood and disciplined shapes, miniature railway diorama prop on pure white, complete elevated front view, no ground, letters or shadow.",
    "castle_diorama_matsu": "One miniature handmade Japanese garden black pine for a model railway diorama, gently twisted mature trunk, asymmetrical horizontal pads of dense dark olive ramification and finely flocked needles. Air between pads, visible trunk, no rocks, stand, soil, shadows, markings or scenery. Orthographic game prop fully isolated against pure white.",
}
SURFACES = {
    "castle_ishigaki_scan": "Flat directly front-facing full-bleed seamless material scan of charcoal gray hand-fitted sixteenth century Japanese castle granite masonry. Individually sized triangular and irregular interlocking stone faces, warm mineral flecks and muted cold shadows within the joints, no perspective, no background, no plants, no scenery, no lettering.",
    "castle_cedar_board_scan": "Top-down even-light tileable albedo scan of worn late medieval dark golden Japanese cedar floorboards, straight parallel planks, rich amber brown tones and fine restrained knots, thin dark seams. Flat diffuse lighting, no perspective, lettering, objects, borders or background.",
}
if __name__ == "__main__":
    queue_meshes({**MODELS, **SURFACES}, tuple(MODELS), "clan-castle-kit", 814601, 1710)
