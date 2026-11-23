"""Queue Ojatara valley and refugee-town voxel sources."""

from comfy_shinomen_gate import queue_meshes


PROMPTS = {
    "ojatara_patched_canopy": (
        "Freestanding late sixteenth century Japanese mountain refugee shelter, four slender "
        "rough cypress posts, a torn walnut-brown oiled cloth canopy patched with indigo and ash gray "
        "cloth, short rope ties. Open on three sides, all feet visible, single compact voxel-game "
        "prop on white, orthographic three-quarter angle, no people, ground, shadows or text."
    ),
    "ojatara_costume_trunk": (
        "Small handmade Japanese travelling troupe costume chest, rectangular dark-red and black "
        "lacquered cedar, two weathered iron carrying rings, chipped corners, several tiny broken "
        "gray goose fletched arrow shafts lodged in one end. Closed, isolated complete game prop "
        "on pure white, elevated orthographic three-quarter angle, no scenery or text."
    ),
    "ojatara_stone_waypost": (
        "Single rough cut Japanese mountain roadside waypost in gray slate, squat upper carved "
        "cap, small ankle-high resting stone at its foot, rain-darkened earthy hues and pale "
        "patchy lichen. No lettering or markings. Complete isolated game object centered on pure "
        "white, elevated orthographic three-quarter view, no ground or cast shadows."
    ),
    "ojatara_field_sacks": (
        "Three crumpled straw rice sacks and a folded plain blanket in a portable bamboo "
        "carrying tray, late medieval Japanese refugee market supplies. Small rope knot details, "
        "unbleached beige fibers, dusty muted gray cloth. Isolated complete game prop on white, "
        "elevated orthographic three-quarter view, no figure, scenery, shadow, or writing."
    ),
    "ojatara_burnt_loam": (
        "Strict overhead edge-to-edge seamless albedo material of rain-darkened ash and "
        "burned field loam in a mountain valley. Some split straw fibers, angular dark fragments, "
        "muted walnut and slate, matte even light, no scenery, horizon, perspective or words."
    ),
}


if __name__ == "__main__":
    queue_meshes(PROMPTS, tuple(PROMPTS)[:-1], "ojatara", 182867, 761)
