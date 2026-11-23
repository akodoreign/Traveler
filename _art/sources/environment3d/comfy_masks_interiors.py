"""Generate the Sweet Cup and Monastery of the Silent Self fixtures."""

from comfy_shinomen_gate import queue_meshes


PROMPTS = {
    "kamen_sweet_cup_counter": (
        "Compact sixteenth-century Japanese tea shop counter, worn warm cypress plank top, "
        "three rolled cloths and two stacked earthen cups, solid cedar joinery and a small "
        "indigo service cloth on one end. Isolated complete stylized game prop centered "
        "on pure white, elevated orthographic three-quarter view, no scene, text or shadows."
    ),
    "kamen_scriptorium_desk": (
        "Late medieval Japanese temple scriptorium writing desk with a folding scroll laid "
        "over a dark low cedar table, three worn bamboo brushes in a dull celadon holder, "
        "one shallow inkstone. Isolated game prop on pure white, elevated orthographic "
        "three-quarter view, no scene, people, shadows, or legible text."
    ),
    "kamen_monastery_dais": (
        "Single low square monastery meditation platform of dark cypress boards, four "
        "pale rush mats inset in the top, softly beveled edge and a broad stable step. "
        "Restrained late-medieval Japanese woodwork. Isolated complete compact game prop "
        "on pure white, elevated orthographic three-quarter view, no scene, people or shadows."
    ),
    "kamen_sun_reliquary": (
        "One small square late-medieval Japanese Buddhist reliquary cabinet, black lacquered "
        "wood with worn bronze corner plates and a broad muted gold sun disk on the front. "
        "Quiet refined joinery, weathered finish, single fully visible stylized game prop on "
        "pure white, isolated elevated orthographic three-quarter view, no scenery or text."
    ),
    "kamen_temple_cypress": (
        "Seamless square game diffuse material swatch, overhead closeup of worn gray-brown "
        "Japanese cypress floor boards with broad shallow foot-polished edges, tightly "
        "laid irregular width boards. Soft even lighting, edge to edge; no props or text."
    ),
}


if __name__ == "__main__":
    queue_meshes(PROMPTS, tuple(PROMPTS)[:-1], "masks-interiors", 174173, 743)
