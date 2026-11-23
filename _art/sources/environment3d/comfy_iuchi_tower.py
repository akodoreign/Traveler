"""Queue a restrained frost, cypress and jade palette for Shiro Iuchi."""

import sys

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

FITTINGS = {
    "iuchi_tower_screen": "One freestanding narrow dark cypress Japanese wind screen, three open horizontal lattice bays over muted indigo cloth, straight generous joinery, clear full silhouette, single isolated game prop, orthographic three-quarter angle on plain white, no floor, shadows, writing, base or scenery.",
    "iuchi_mine_cart": "One late medieval fantasy Japanese push cart for stone, simple worn square cedar box with two dark solid wooden wheels, small load of broad dusty green jade-bearing rocks. Strong simple silhouette, complete isolated single voxel game prop, elevated three-quarter on plain white, no floor, scenery, text or shadows.",
    "iuchi_mine_memorial": "A very small Japanese mountain memorial, a single roughly hewn gray slate stone and one low cedar offering ledge holding a white folded paper strip. Quiet and restrained, one isolated prop from three quarter on clean white, no base plate, floor, shadows, vegetation or lettering.",
    "iuchi_riverbed_stone": "Square top-down albedo of a shallow Japanese forest brook's pebble bed, smooth small dark river stones with muted sage-grey, slate-blue and amber earth. Completely flat diffuse scan, even light, edge to edge with no scenery, water reflections, text or larger objects.",
}


UNDERSTORY = {
    "iuchi_brook_reeds": "One compact tuft of eight forest stream sedge blades, bent olive green leaves and two muted straw tips. One isolated voxel-game prop, plain white backdrop, fully visible from elevated three-quarter, no dirt mound, flowers, floor plane, shadow, surrounding objects or text.",
    "iuchi_split_slate_shelf": "One wide low fractured blue charcoal slate shelf, a single uninterrupted silhouette with three angular facets and dark moss near the foot. Complete original game prop on clean solid white, no stage, ground plane, background card, shadows, other rocks, cut gemstone decoration or lettering.",
}


if __name__ == "__main__":
    if "--brook-pebbles" in sys.argv:
        stones = {"iuchi_brook_pebbles": "Two low rounded natural gray river stones, one rounded dark gray boulder and one smaller smooth pale gray river stone touching it at the foot. A little muted olive moss in the seam. Fully visible isolated voxel game prop photograph on pure uniform white, no shadows, scenery, people, creatures, characters, silhouette cutout, plinth, shelf, pedestal, floor or base plane."}
        queue_meshes(stones, tuple(stones), "iuchi-brook-pebbles", 762901, 1159)
    elif "--understory" in sys.argv:
        queue_meshes(UNDERSTORY, tuple(UNDERSTORY), "iuchi-understory", 762765, 1143)
    elif "--fittings" in sys.argv:
        queue_meshes(FITTINGS, tuple(FITTINGS)[:3], "iuchi-fittings", 762731, 1127)
    else:
        queue_meshes(PROMPTS, tuple(PROMPTS)[:3], "iuchi-tower", 762709, 1107)
