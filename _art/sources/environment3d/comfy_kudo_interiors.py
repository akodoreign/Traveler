"""Queue original furnishings for Kudo's three story interiors."""

from comfy_shinomen_gate import queue_meshes


PROMPTS = {
    "kudo_fox_pillar": (
        "One slender Japanese carved cypress interior post. Hand carved nine-leaf motif near the "
        "top, pale ochre wood with muted dark forest green lower insert, small iron collar and simple "
        "square base. A single whole stylized historical game asset, orthographic view on pure white, "
        "no floor, room, lettering or shadows."
    ),
    "kudo_mantis_chart_desk": (
        "One low late-Sengoku Japanese officer's desk of dark lacquered wood with small worn brass "
        "corners. A folded off-white river chart, polished smooth stone paperweight and narrow ink brush "
        "on top. Three-quarter orthographic single isolated game prop, entire object clear on pure "
        "white, no ground, surrounding objects, shadows, person or text."
    ),
    "kudo_carp_sake_rack": (
        "One compact traditional Japanese inn cedar shelving unit loaded with a few naturally uneven "
        "rounded cream ceramic sake jars, each closed with indigo fabric tied in plain hemp. Rugged leg "
        "joints, one low side board, chest-high simple carpentry. Orthographic three-quarter full isolated "
        "game asset on white, no ground, shadow, figures or writing."
    ),
    "kudo_bamboo_food_cover": (
        "One covered serving tray for a late-Sengoku Japanese household, low matte black lacquer tray "
        "holding a rounded woven straw and bamboo food cover on a white cloth, small reddish cord loop "
        "at the top. Complete isolated three-quarter game asset on pure white, no other objects, "
        "shadows, scenery or text."
    ),
    "kudo_inn_mat": (
        "Strictly orthographic square close-up albedo scan of uniform tightly woven muted amber brown "
        "tatami, thin parallel rush fibres, a little wear and straw sheen. Edge to edge only plain woven "
        "weave. Natural diffuse light, no frame, border, objects, shadow, scenery or lettering."
    ),
}


if __name__=="__main__":
    queue_meshes(PROMPTS,tuple(PROMPTS)[:-1],"kudo-interiors",428851,659)
