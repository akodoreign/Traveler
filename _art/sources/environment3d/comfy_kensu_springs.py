"""Queue original props for the paddies, hot springs, and city approach."""

from comfy_shinomen_gate import generate, queue_meshes


PROMPTS = {
    "kensu_bath_supplies": (
        "One waist-high collection of stacked sixteenth-century Japanese cypress bath buckets, "
        "one folded undyed bathing towel and a shallow wooden dipper resting on a low cedar "
        "bench. Isolated game prop, elevated orthographic three-quarter view on pure white, "
        "full object, no people, writing, floor or shadow."
    ),
    "kensu_spring_rocks": (
        "One low wide cluster of three large rounded slate and gray granite stones at a "
        "natural Japanese hot spring, dark water stains, faint warm mineral color in the "
        "cracks. Complete isolated voxel-game prop on pure white, elevated orthographic "
        "three-quarter view, no water, steam, ground or scenery."
    ),
    "kensu_rice_seedlings": (
        "Isolated low cluster of nine fine upright young rice shoots in three staggered "
        "rows, thin vivid olive-green leaves with visible empty air between them, no soil, "
        "water, pot or ground. Fully visible centered on white, elevated orthographic "
        "three-quarter view, for a late-medieval Japanese paddy game tile."
    ),
    "kensu_field_jizo": (
        "Small aged Japanese wayside carved stone Jizo statue on a squat rough square "
        "footing. Rounded serene face worn by age, two hand-carved folds, simple faded muted "
        "vermilion bib, unpolished dark granite. Complete isolated prop, three-quarter "
        "orthographic on white, no ground, scene, lettering, or shadow."
    ),
    "kensu_path_clay": (
        "Strict overhead edge-to-edge diffuse game texture scan of compressed weathered "
        "earth from a rural Japanese paddy road. Warm muddy gray, tiny scattered gray "
        "grit, subtle worn fibers and dark moist mottling. Flat soft lighting, no "
        "prop, water, horizon, perspective, shadows, symbols, or markings."
    ),
}


if __name__ == "__main__":
    queue_meshes(PROMPTS, tuple(PROMPTS)[:-1], "kensu-springs", 178327, 751)
    generate({
        "kensu_meadow_scan": (
            "Strict overhead square edge-to-edge game material scan of a late summer Japanese "
            "rice country meadow. Natural quiet low grass, tiny subtle clover, modest ochre blades "
            "and irregular sparse exposed damp soil, fine organic changes, no paving pattern and "
            "no built objects. Top down, diffuse flat light, no scenery, horizon, shadows or lettering."
        ),
    }, "comfy-kensu-meadow-images.json", 179174)
