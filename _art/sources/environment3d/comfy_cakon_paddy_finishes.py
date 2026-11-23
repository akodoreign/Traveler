"""Generate finishing props for Cakon's paddy road and clay hut."""
from comfy_shinomen_gate import queue_meshes

PROMPTS={
    "cakon_paddy_jizo": "One small Japanese wayside Jizo statue for a model railway diorama, tranquil shaven stone monk holding a jewel, dark weatherworn slate-gray granite, subtly carved robes, a tied faded red bib and moss at its integral small carved stone foot. Isolated whole three-quarter game prop on solid white, no terrain slab, letters, shadow, vegetation or scenery.",
    "cakon_tomie_herb_rack": "One low cedar and bamboo rack for drying herbs in a rural medieval Japanese clay cottage. Three shallow woven trays, a few dark green dried herb and ochre straw bundles, wooden pegged trestles, subtle grain. Complete miniature diorama game prop isolated on pure white, no building, people, ground, text or shadow.",
    "cakon_paddy_mud_scan": "Flat straight-down seamless square albedo texture scan of a moist natural Japanese rice paddy bund, dusky burnt sienna silt with sparse fine dusty beige grit, very small gravel and faint shallow rake marks. Matte even daylight, no visible scenery, no vegetation, no objects, no perspective, no letters. Edge to edge.",
}
if __name__=="__main__":
    queue_meshes(PROMPTS,tuple(PROMPTS)[:2],"cakon-paddy-finishes",815574,1774)
