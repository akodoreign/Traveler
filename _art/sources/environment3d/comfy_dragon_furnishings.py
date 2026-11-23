"""Generate mountain inn furniture and the garden procession fixtures."""

import sys

from comfy_furnace import generate
from comfy_shinomen_gate import queue_meshes


PROMPTS={
    "dragon_inn_hearth":(
        "One low Japanese mountain inn irori hearth module, square dark cypress frame "
        "around charcoal fire stones and a matte black pot, ash below, small wooden "
        "trivet at the side. Authentic restrained late-medieval craft. Complete isolated "
        "game prop from elevated three quarters on white, no room, people or shadows."
    ),
    "dragon_procession_bell":(
        "One compact late-medieval Japanese temple procession bell on a small dark "
        "timber carrying frame. Strong starched white braid, deep oxidized bronze bell, "
        "and muted gold fittings. Complete isolated game object clipped to no ground, "
        "raised three-quarter orthographic on solid white, no people or text."
    ),
    "dragon_garden_stone_lantern":(
        "Single weathered Japanese garden stone lantern, blue-gray mountain slate, "
        "open light chamber, small green moss at joints, boldly carved weathered cap. "
        "Whole isolated game fixture on white with raised three-quarter view, no scene, "
        "shadow, people or lettering."
    ),
    "dragon_inn_hanging_screen":(
        "Single late medieval Japanese mountain inn doorway screen, dark green woven "
        "cloth with indigo vertical borders on a narrow black cypress rail, lightly "
        "frayed bottom, a clear soft cloth silhouette. Isolated fully visible game prop "
        "on white in raised three-quarter view, no scenery, people, text, or shadows."
    ),
    "dragon_inn_burnished_cypress":(
        "Strict overhead diffuse material scan of burnished dark reddish brown cypress "
        "boards in a Japanese mountain inn. Fine worn grain, organic matte accents, "
        "signs of many feet. Square edge-to-edge and softly lit without objects, words "
        "or perspective."
    ),
}

CLEAN_PALETTE = {
    "dragon_clean_wall_plaster": (
        "Uniform warm ochre pale clay plaster for a late medieval Japanese inn, strictly flat diffuse "
        "surface scan, subtle trowel texture, clean smooth base color, small scale, edge to edge, "
        "no wall boards, joints, dark spots, worn patches, flowers, trim, lighting gradients or scenery."
    ),
    "dragon_clean_lacquered_wood": (
        "Flat 90 degree diffuse surface scan of one warm dark Japanese cypress board, continuous subtle "
        "tight linear wood grain, no seams, no knots, rich reddish brown, even illumination, fine low "
        "contrast grain only, edge to edge square, no scenery or props."
    ),
}


if __name__=="__main__":
    if "--clean-palette" in sys.argv:
        generate(CLEAN_PALETTE, "comfy-dragon-clean-palette.json", 823734)
    else:
        queue_meshes(PROMPTS,tuple(PROMPTS)[:-1],"dragon-furnishings",202511,893)
