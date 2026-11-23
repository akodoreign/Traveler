"""Queue original fixtures and material scans for the Iuchi siege and storm."""

import sys

from comfy_shinomen_gate import queue_meshes


SIEGE = {
    "iuchi_siege_field_hearth": (
        "One compact late medieval Japanese field kitchen hearth. One matte charcoal iron pot nested in a low stone ring, "
        "short split log beside it, strong clean forms, large clear shapes. Complete isolated three-quarter game prop on "
        "uniform white. No smoke, base plane, display tray, stand, scenery, text, or shadow."
    ),
    "iuchi_wind_buttress": (
        "One freestanding natural jagged flake of grey-blue slate, tilted diagonally, one broad stone face, low cold sage "
        "lichen only in the deep seams. Uncut irregular rock with a solid silhouette, complete isolated three-quarter game "
        "prop on uniform pure white. No plinth, platform, ground, other objects, lettering, or shadows."
    ),
    "iuchi_wind_cleft_scan": (
        "Flat front-on dark weathered Japanese mountain slate mineral albedo scan. Medium cool gray fractured strata with "
        "thin pale dry seams, low contrast broad material, small realistic pore grain, absolutely no rocks protruding, "
        "horizon, border, plants, floor, reflections, or letters. Even diffuse exposure."
    ),
    "iuchi_scoured_sand_scan": (
        "Strict straight overhead albedo scan of matte wind-scoured mountain sand. Warm desaturated ivory and fine small "
        "lengthwise streaks with shallow dry granular ridges, diffuse even light with no shadows or other objects, seamless."
    ),
}

STORM = {
    "iuchi_storm_broken_frame": (
        "One isolated small section of a broken Japanese wood lattice screen, dark squared hand-cut cypress bars, "
        "three clean coarse damaged openings and a little torn dull ivory paper. Whole single game prop at elevated "
        "three-quarter on solid white. No backdrop, floor, objects, people, captions or shadows."
    ),
    "iuchi_storm_dais_stone": (
        "Square flat diffuse game albedo scan of slate paving worn smooth by foot traffic, restrained mineral charcoal "
        "gray with tiny natural mica grains, even light, only one stone surface edge-to-edge, no objects, grid, or texture bands."
    ),
    "iuchi_storm_woven_cloth": (
        "Edge-to-edge flat albedo scan of rich Japanese dark indigo woven cloth with tiny slate-blue threads, even diffuse light, "
        "subtle low contrast grain. No folds, printed graphics, fringe, objects, shadows or scenery."
    ),
}


ROAD = {
    "iuchi_valley_pack_basket": (
        "An isolated late-medieval Japanese travel pack. One dark amber handwoven bamboo pannier with deep russet "
        "rope loops and a neatly rolled indigo bedding mat across the top. Keep the entire three-quarter prop in "
        "view on a pure white background without a floor, shadow, display stand, people, writing, or scenery."
    ),
    "iuchi_valley_wayside_stone": (
        "A single squat hand-hewn roadside stone marker from premodern Japan, battered dark basalt with a ridge cap "
        "and moss along the foot. No inscriptions. Compact isolated three-quarter game prop on pure white without "
        "base plane, shadows, lettering, people, or scenery."
    ),
}


if __name__ == "__main__":
    if "--tower" in sys.argv:
        queue_meshes(STORM, tuple(STORM)[:1], "iuchi-storm-room", 764141, 1207)
    elif "--road" in sys.argv:
        queue_meshes(ROAD, tuple(ROAD), "iuchi-valley-road", 764162, 1216)
    else:
        queue_meshes(SIEGE, tuple(SIEGE)[:2], "iuchi-wind-siege", 764112, 1199)
