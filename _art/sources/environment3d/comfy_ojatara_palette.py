"""Generate fabric and ground references for Ojatara's richer color pass."""

from comfy_furnace import generate


PROMPTS={
    "ojatara_indigo_canvas":(
        "Square strictly flat top-down diffuse material scan of very dark rich Japanese "
        "indigo-dyed hemp canvas with tight visible woven thread, slight natural wear, "
        "matte material. Consistent deep navy blue and fine fibers, edge to edge. No "
        "folds, big patches, furniture, scenery, highlights, text, border or shadows."
    ),
    "ojatara_oxblood_canvas":(
        "Square strictly top-down diffuse albedo texture scan of deep oxblood rust-red "
        "madder dyed hemp canvas used for a Japanese roadside shelter. Dense visible weave, "
        "fine weathering and a dark warm saturated red color. Flat matte even light, "
        "edge to edge without folds, objects, floor, shadows, scene or text."
    ),
    "ojatara_offwhite_canvas":(
        "Square strictly overhead matte diffuse albedo material scan of tightly woven raw "
        "cream hemp canvas. Natural oatmeal and warm ivory colored visible threads, fine "
        "smoke staining at irregular intervals. Soft even illumination. Edge to edge "
        "without folds, objects, writing, floor, scenery or cast shadows."
    ),
    "ojatara_earth_v2":(
        "Edge-to-edge square flat overhead diffuse terrain material scan. Damp dark umber "
        "compacted loam on a footpath in a rural Japanese mountain valley. Very irregular "
        "fine gray-brown grit, tiny dark pebbles, and few quiet subtle warm burnt orange "
        "flecks. No broad diagonal marks, footprints, patterns, shadow, scenery or horizon."
    ),
}


if __name__=="__main__":
    generate(PROMPTS,"comfy-ojatara-palette-images.json",195581)
