"""Queue distinct market, hospitality, and temple props for Kamen no Toshi."""

from comfy_shinomen_gate import queue_meshes


PROMPTS = {
    "kamen_mask_display": (
        "Single late Sengoku Japanese street market carpenter's display rack of painted wooden "
        "festival masks on a narrow dark cedar frame. Three different stylized human stage masks "
        "and one pale fox mask, restrained indigo, cream, and aged vermilion. No living figures. "
        "Complete isolated game asset, orthographic three-quarter view on white, no ground or text."
    ),
    "kamen_hospitality_lantern": (
        "Single freestanding Japanese covered hospitality lantern, dark stained cypress pedestal "
        "and gently rounded faded mulberry paper shade with shallow bronze roof. Subtle fabric repair, "
        "late sixteenth century regional street prop. Complete isolated game object on white, "
        "orthographic three-quarter view, no shadows, scenery or writing."
    ),
    "kamen_merchant_awning": (
        "One compact open-front late-Sengoku Japanese street shop shade, four cedar supports and "
        "low wine-red dyed hemp awning with undyed cream edge, knotted rope and short hanging folds. "
        "Freestanding modular game asset, fully visible isolated three-quarter orthographic on white, "
        "no shop wall, person, ground plane, signs or shadow."
    ),
    "kamen_shrine_offering_stand": (
        "One orderly weathered Japanese temple-offering stand, low cedar table, two small ceramic "
        "water bowls, one folded white cloth and a tiny bronze incense cup. Stone footings, narrow "
        "wood joinery. Complete isolated orthographic game prop on pure white, no scenarios, shadow "
        "ground, people or text."
    ),
    "kamen_old_flagstones": (
        "Strictly overhead close square diffuse game material scan of irregular late-medieval Japanese "
        "city courtyard granite flagstones fitted tightly in a rammed clay bed. Muted gray-brown stones "
        "softened by foot traffic, subdued light. Edge to edge texture only, no scenery, sky, shadows or objects."
    ),
}


if __name__=="__main__":
    queue_meshes(PROMPTS,tuple(PROMPTS)[:-1],"city-of-masks",173123,707)
