"""Generate the riverbank, docks, and market assets for Cakon."""

import sys

from comfy_shinomen_gate import queue_meshes


RIVER = {
    "cakon_herb_cluster": "One small wild Japanese riverbank ginseng clump, five pointed deep green leaflets per branch and a few muted red berries, upright clean silhouette, isolated 3/4 game asset on pure white, roots at ground height, no base, ground, scenery, border, cast shadow or text.",
    "cakon_mooring_gear": "One isolated premodern Japanese waterfront game prop, amber jute mooring rope wound in a large neatly layered low coil and a dark stained timber bollard rising behind it. 3/4 view, charcoal wood, matte coarse fibers, all parts fit fully in frame. Pure white backdrop, no floor, inset platform, signs, shadows or surroundings.",
    "cakon_cedar_deck_scan": "Flat directly overhead seamless albedo photograph of worn dark golden oiled Japanese cedar deck wood, interesting straight long low contrast grain, fine dark seams and small pores. Diffuse light, no cast shadows, no context, zero perspective or visible objects, full bleed.",
    "cakon_river_silt_scan": "Flat directly overhead seamless albedo photograph of finely grained wet river silt, slate olive brown with dispersed tiny rounded stone chips. Matte and diffuse full bleed, no horizon, highlights, perspective, scenery, borders or visible objects.",
}
MARKET = {
    "cakon_fish_basket": "One low late medieval Japanese split bamboo fishmonger's basket with several visible silver-blue river fish inside; robust russet weave, natural shape, 3/4 view. Isolated game prop on solid white without people, extra props, water, stand, white base, flooring, shadow, labeling or text.",
    "cakon_market_crock": "One squat deep chestnut Japanese stoneware storage crock with smooth simple curved walls, a tied russet fabric lid and dark narrow foot, irregular kiln patina. Isolated three-quarter game prop on pure white with no platform, border, people, shadows, floor, letters or context.",
    "cakon_plaster_scan": "Flat perpendicular seamless albedo sample of smooth Japanese lime plaster with a fine hand-applied texture and subtle pale ivory mottling. No deep cracks, sparse warm tones, full bleed no objects or scenery, no floors, no borders or lettering.",
    "cakon_stone_setts_scan": "Flat directly overhead seamless albedo of late medieval Japanese dark grey-blue cut river-stone street setts, tidy staggered rectangular pieces with thin joints and softly rounded edges. Matte subtle variations, even diffuse lighting, full bleed.",
}
VILLAGE = {
    "cakon_maple_miniature": "One miniature narrow Japanese maple for a hand-built model railway diorama. Layered, separated pads of compact coarse clump foliage, asymmetrical and airy on a crooked scale-model gray brown bark trunk. Soft copper, russet and muted ochre leaves, restrained natural values like railway scenery foam, no oversized balls of foliage. Full silhouette, 3/4 front game view on solid white, completely isolated, no base, no ground, no shadow.",
    "cakon_thatch_bundle": "A compact loose bundle of cut rice straw tied with premodern Japanese jute rope for a rural late medieval diorama. Fiber texture visible from above, rich ochre-brown varied subtle color, isolated three quarters neutral pure white background, no floor base, no characters, no lettering.",
}
BOATS = {
    "cakon_river_barge": "One 1:35 scale scratch-built model railroad diorama boat, a late medieval Japanese shallow-draft river cargo barge. Long narrow low hand-built timber hull with a blunt raised bow and a tapered stern, dark chestnut weathered boards and thin plank seams, open low cargo deck, no sail or cabin. Delicately modeled model-making details, dark ochre grain with small charcoal metal fittings. Entire single boat isolated in elevated three-quarter side view on pure white, absolutely no base, water, stand, wake, cargo, figures, lettering or background.",
}
CANAL = {
    "cakon_canal_maple_log": "One realistic miniature railroad diorama prop, a single straight old fallen maple log worn flat along its top from use as a footbridge, weathered dark bark and realistic tawny end grain. Clearly one log, bark attached, no handrails or bridge framework. Isolated elevated three-quarter view, white background, no floor, water, terrain, writing, shadow, or surrounding objects.",
    "cakon_paddy_red_stone": "One isolated low triangular iron-red granite boulder for a miniature railway diorama. Weathered matte dark russet stone with pale mineral flecks, lichen only along the bottom. Isolated game prop, three-quarter on solid white, no base, floor, shadow, writing or other objects.",
}
PADDIES = {
    "cakon_cedar_diorama": "One small-scale Japanese cedar model for a miniature railway diorama. Tall, locally tapered irregular silhouette, coarse olive flocked foliage pads with visible branch tips and a warm gray trunk, naturally dusty, clean separation between crown and foot. Orthographic whole tree game prop on pure white, no round display base, floor, surroundings, shadows or lettering.",
    "cakon_paddy_stalks": "One distinct small clump of early-season rice stalks for a miniature model railway agricultural diorama. Eight slender varied leaf stems with muted yellow-green tips and dark green bases, all growing from the same point. One isolated airy natural game prop against solid white, no soil slab, water, frame, shadow or backdrop objects.",
}
HUT = {
    "cakon_herb_bowl": "One small scratch-built miniature old Japanese rough brown clay mortar with a short wooden pestle inside, one prop, tiny grey mineral flecks in deep umber pottery. Muted natural diorama colors. Entire isolated three-quarter view on pure white, no floor, stand, cast shadows, lettering, herbs, people or surrounding objects.",
    "cakon_earthen_wall_scan": "Flat straight-on seamless albedo scan of matte dark straw-tempered clay plaster for a weathered old Japanese rural cottage miniature. Deep red-brown umber with only a few tiny exposed fibers, subtle shallow dry tool marks, diffuse even light, no crumbling chunks, perspective, objects, background or borders.",
}


if __name__=="__main__":
    batch,receipt,seed,mesh_seed=RIVER,"cakon-riverbank",787511,1241
    if "--market" in sys.argv:
        batch,receipt,seed,mesh_seed=MARKET,"cakon-market",787621,1247
    elif "--village" in sys.argv:
        batch,receipt,seed,mesh_seed=VILLAGE,"cakon-village",787776,1268
    elif "--boats" in sys.argv:
        batch,receipt,seed,mesh_seed=BOATS,"cakon-model-boats",788032,1273
    elif "--canal" in sys.argv:
        batch,receipt,seed,mesh_seed=CANAL,"cakon-canal",788173,1292
    elif "--paddies" in sys.argv:
        batch,receipt,seed,mesh_seed=PADDIES,"cakon-paddies",788297,1304
    elif "--hut" in sys.argv:
        batch,receipt,seed,mesh_seed=HUT,"cakon-hut",788418,1310
    queue_meshes(batch,tuple(batch)[:1 if batch is HUT else 2],receipt,seed,mesh_seed)
