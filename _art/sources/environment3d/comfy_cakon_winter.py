"""Generate small props for the River of Gold winter route and rice barge."""
from comfy_shinomen_gate import queue_meshes

PROMPTS={
    "rokugan_frosted_river_reeds":"One airy miniature diorama clump of dormant Japanese river reeds with dark ochre upright stems and a little sparkling hoarfrost on leaves. Small white dusting at the base only, muted bronze and blue shadows, separated thin irregular blades. Whole isolated game prop in elevated three-quarter view, pure white studio backdrop with no scene, floor, shadow or words.",
    "rokugan_barge_rice_bales":"A compact stack of two Edo-era Japanese tawara rice bales in molded straw sleeves, bound with thin dark straw cords and visible hand-tied knots. Weathered warm amber straw, coarse but clean fiber detail, true miniature diorama craft. Single whole game prop in orthographic three-quarter view, isolated on pure white, no ground, platform, people, text or shadows.",
    "rokugan_winter_fox_offering":"One little weathered red-painted Japanese stone fox statue on a short square gray granite foot, sparse soft snow on ears and foot, narrow fox ears and tail curled near paw, small faded red bib, detailed natural scale model game prop. Complete three quarters on a solid white background, no landscape, text, cast shadow, people or scenery.",
}
if __name__=="__main__":
    queue_meshes(PROMPTS,tuple(PROMPTS),"cakon-winter-river",816083,1818)
