"""Queue a restrained frost, cypress and jade palette for Shiro Iuchi."""

from comfy_shinomen_gate import queue_meshes


PROMPTS = {
    "iuchi_mountain_birch": (
        "One compact mountain birch with a forked gray-white trunk and a narrow crown of dark sparse "
        "olive bronze leaves, lightly frosted tips, thick distinct trunks. Entire isolated voxel-game "
        "prop on a plain white back, three-quarter orthographic, no base plate, scenery, letters, shadow."
    ),
    "iuchi_tower_andon": (
        "One square Japanese cypress andon lantern, four dark straight corner posts, plain ivory rice paper "
        "framed with an indigo border and a small square wood cap. Entire isolated original game prop in "
        "three-quarter orthographic on white, no floor, studio sweep, shadow, patterns, props or lettering."
    ),
    "iuchi_jade_seam": (
        "One compact low ashy slate boulder with three jagged raw jade-green veins in the exposed fracture, "
        "muted teal mineral and darker slate, one uninterrupted stone mass. Isolated single original game "
        "asset on pure white, no pedestal, studio floor, backdrop, outline, letters or shadow."
    ),
    "iuchi_frosted_meadow": (
        "Strict continuous top-down game albedo of frost-tipped short winter grass, pale sage and dull "
        "straw with gray brown earth between specks, small uniform scale, edge-to-edge, fully diffuse, no "
        "blocks, scenery, horizon, letters, snow mounds, studio floor, or other objects."
    ),
    "iuchi_jade_wall_scan": (
        "Flat diffuse albedo scan of a dark slate mountain mine wall, desaturated charcoal blue and "
        "occasional thin muted teal veins, low contrast mineral grain, soft even illumination, edge to "
        "edge only, no crystals jutting out, cavern, horizon, bricks, text or objects."
    ),
}


if __name__ == "__main__":
    queue_meshes(PROMPTS, tuple(PROMPTS)[:3], "iuchi-tower", 762709, 1107)
