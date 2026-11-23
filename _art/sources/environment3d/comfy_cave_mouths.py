"""Queue stone surrounds for five measured cave-mouth profiles."""
from comfy_shinomen_gate import queue_meshes

COMMON=(
    " Complete isolated three-dimensional miniature portal surround, elevated three-quarter view. "
    "Show both sides and the inner walls. The narrow opening runs through front to back, "
    "with pure white visible through it. Include no solid rear slab, fake painted cavity, "
    "ground plane, scenery, people, text, hardware or cast shadow."
)
PROMPTS={
    "mouth_tide_cut_basalts": (
        "A low broad sea-cave mouth eroded between dark cobalt coastal basalt shelves. "
        "Two layered irregular headlands form the jambs and a gently flattened overhang "
        "forms the roof. Warm reddish seams and traces of deep emerald sea moss." + COMMON
    ),
    "mouth_blue_ice_fissure": (
        "A narrow blue-ice gorge entrance between two unequal fractured glacier walls. "
        "Thin crystalline sheets interlock over a tall irregular opening, rich cobalt interiors "
        "and clear sky-blue edge highlights. Show the opening between the two feet." + COMMON
    ),
    "mouth_lava_tube_vesicular": (
        "A natural dark volcanic lava tube mouth. A thick low dark basalt crown with gentle "
        "vesicular texture and little deep red mineral veins, asymmetric rounded passage, "
        "black cooled inner surface. Let the actual opening occupy a third of the silhouette." + COMMON
    ),
    "mouth_carved_jade_monolith": (
        "A solid vivid deep emerald jade monolith with a gently rounded through passage carved from it, "
        "fine natural jade structure, flanking rough mountain-rock pinch points, understated gold "
        "incision just around the opening. A carved threshold within clear natural stone." + COMMON
    ),
    "mouth_shale_ravine_split": (
        "An asymmetric mountain cave entrance formed from a natural split in very dark blue-green shale. "
        "Layered wedge-shaped outcrops form a tall angled passage with a wide enough clear foot opening. "
        "Rich fir moss only in a few seams. Coherent large stone relief and restrained fine texture." + COMMON
    ),
    "mouth_moss_limestone_cove": (
        "A low wide natural coastal passage with rounded ledges of weathered golden-gray limestone. "
        "Jagged horizontal strata above the shallow dark recess, deep green moss on the lower jambs, "
        "cream clay and a few gravel shards beside the stone feet. Broad clean shapes, restrained fine texture." + COMMON
    ),
    "mouth_limestone_karst_teeth": (
        "A broad uneven limestone cave lip with a few short hanging drips and a naturally broken asymmetrical crown. "
        "Two large carved-by-water ivory pillars frame a deep open slot. Fern green and warm ochre weathering "
        "on selected lower seams. Keep drips above a deliberately broad and tall clear center." + COMMON
    ),
    "mouth_stepped_ruin_hall": (
        "A weathered fantasy shrine chamber entrance of deep fitted pale sandstone and amber shadow, "
        "three broad low steps rising to the central carved lintel with a dark through passage. Two inset square "
        "blind niches form the shoulders. Stone blocks age differently at their seams, with very restrained "
        "blackened gold relief around the center. Broad cool pale stone structure, crisp shapes, subtle scan texture."
        + COMMON
    ),
}

if __name__=="__main__":
    queue_meshes(PROMPTS,tuple(PROMPTS),"cave-mouth-variants",894171,7587)
