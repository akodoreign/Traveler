"""Generate handpicked environment sources for the Dragon garden and autumn valley."""

import sys

from comfy_shinomen_gate import queue_meshes


PROMPTS = {
    "togashi_garden_stone": (
        "One low ancient Japanese karesansui garden boulder, asymmetrical uncut gray-blue slate, "
        "flattened base, one higher sloping end, fractures running diagonally and a tiny amount of moss "
        "at the foot. Read as one single body, irregular but quiet silhouette, large uninterrupted "
        "stone surfaces. One isolated complete game prop on pure white in orthographic three-quarter "
        "view, no scenery, people, ground or shadows."
    ),
    "autumn_valley_maple": (
        "One mature Japanese mountain maple with an uneven crooked brown split trunk and three large "
        "dense separated lobes of amber, ochre and dark russet foliage. A legible silhouette at a "
        "distance and broad clusters of color. Realistic low-poly stylized voxel game reference, "
        "full freestanding tree in orthographic three-quarter view, pure white background, no "
        "ground, objects, inscriptions, loose leaves or shadows."
    ),
    "autumn_camp_cooking_tripod": (
        "One simple sixteenth-century Japanese outdoor cooking tripod, three stout cypress branches "
        "bound with rope and a single matte-black round iron cooking pot hanging from the meeting "
        "point. Worn wood and warm brown rope. Clear large shapes, no little debris. Full isolated "
        "game prop in elevated orthographic three-quarter view on white, no smoke, ground or shadow."
    ),
    "autumn_valley_leaf_litter": (
        "Flat top-down albedo material of packed autumn earth with scattered dry amber Japanese "
        "maple leaves and small russet leaf fragments. Tiny scale, matte, even diffuse light and "
        "a controlled ochre and dark Umber palette. Edge to edge, no artifacts, props, printed forms or scenery."
    ),
}

ROOMS = {
    "autumn_welcome_irori": (
        "A low square Japanese inn irori hearth, simple broad dark cypress rim on four short square feet, "
        "dark ash and a sturdy black iron tea kettle. Distinct shapes and a restrained rich brown warm "
        "palette. Entire isolated game prop cutout on pure white, raised three-quarter view, no base plate, "
        "floor, shadow, additional furniture, people or words."
    ),
    "autumn_soshi_writing_set": (
        "Single low dark lacquered Japanese writing bench with one ivory rolled paper scroll and one "
        "small black rectangular inkstone. Fitted square joinery, smooth red-black wood, clean strong "
        "silhouette. A complete isolated sixteenth-century Japanese game asset in elevated three-quarter "
        "view on pure white, no background walls, floor, shadows or lettering."
    ),
    "autumn_soshi_brocade": (
        "Orthographic material scan of woven dark oxblood Japanese silk brocade, a small repeating "
        "subtle brass geometric lattice, dark rich red, edge-to-edge diffuse, exactly flat, no drape, "
        "room, curtains, light glints, printed words or ornaments."
    ),
}

CAVES = {
    "autumn_yotomo_pigeon_house": (
        "One original late medieval Japanese wooden pigeon house, a small raised cedar dovecote with "
        "dark squared posts, five obvious oval bird entry holes, a low cypress pitched roof and tiny "
        "landing shelf. Complete isolated one-object game prop against pure white, elevated orthographic "
        "three-quarter view with no birds, base, ground, backdrop, set, shadow or words."
    ),
    "autumn_yotomo_storage_vat": (
        "Single large round Japanese cedar vat with faded reddish wooden staves, broad plank lid, two "
        "dark woven bands and a short block stand. Clean silhouette and low-key wood color. Full isolated "
        "single-object game asset in three-quarter orthographic view on pure white, no set, background, "
        "base plane, furniture, shadows, words or people."
    ),
    "autumn_yotomo_cave_limestone": (
        "Strict flat diffuse texture scan of the surface of dark dry charcoal limestone. Very subtle "
        "bluish gray spars and fine grains with pale powdery off-white mineral deposits in fine creases. "
        "Edge-to-edge albedo only. Even light and no scenery, wall objects, props, letters or shapes."
    ),
}


if __name__ == "__main__":
    if "--rooms" in sys.argv:
        queue_meshes(ROOMS, tuple(ROOMS)[:-1], "autumn-valley-rooms", 438609, 1082)
    elif "--caves" in sys.argv:
        queue_meshes(CAVES, tuple(CAVES)[:-1], "autumn-valley-caves", 438621, 1088)
    else:
        queue_meshes(PROMPTS, tuple(PROMPTS)[:-1], "autumn-valley", 438560, 1073)
