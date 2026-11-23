"""Generate activity props for the eight clan castles."""
from comfy_shinomen_gate import queue_meshes

PROMPTS = {
    "castle_snow_pine": "One realistic handbuilt model railroad Japanese black pine in winter without a display base. Natural broad miniature silhouette, scattered thin powder snow on the top of dark green flocked needle clumps, most lower foliage is deep green, gnarled dark bark. Single isolated whole game prop in elevated three-quarter view on pure white, no plinth, ground plane, text, scenery or shadow.",
    "castle_lion_makiwara": "One Sengoku Japanese castle courtyard archery target, thick tightly wound circular tawny straw makiwara mounted on a low dark brown wooden trestle, thin muted gold and umber center rings. Miniature railway diorama proportions, photographed diffuse elevated front view with complete silhouette against pure white. No shadow, ground, lettering, arrows or scenery.",
    "castle_isawa_incense": "One small Japanese late medieval five-element temple incense vessel, a squat patinated dark bronze bowl on three curved feet and a removable lid with five tiny openings, red-brown bronze with warm edges. Complete isolated specimen on white, elevated three-quarter view, miniature scale, no smoke, flame, pedestal, lettering, shadows or surroundings.",
    "castle_kitsuki_archive": "One low wide Japanese late medieval wooden castle records cabinet, five orderly rows of narrow dark camphor drawers, little black iron drawer pulls and a warmly oiled cedar top. Clean miniature railway diorama furniture, isolated complete against pure white, elevated three-quarter front view, no shadows, text, objects on top or scenery.",
}
if __name__ == "__main__":
    queue_meshes(PROMPTS, tuple(PROMPTS), "clan-castle-activities", 815173, 1748)
