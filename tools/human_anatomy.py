"""Surface anatomy for the skinned human figures, ordered by school, family, and sex."""

from math import cos, pi, tau
from functools import lru_cache


# Each lobe is (height, half-height, angle in degrees, half-angle, relief).
# Angles start at the front and turn toward the outside of each limb.
HIRUMA_SCOUT = {
    "torso": (
        (92, 5, 139, 44, 1.09),     # trapezius
        (89, 4, 36, 39, .65),       # clavicular pectoralis
        (84, 6, 38, 41, 1.19),     # sternal pectoralis
        (77, 4, 62, 32, .66),       # serratus anterior
        (83, 11, 122, 45, 1.16),   # latissimus dorsi
        (76, 16, 158, 23, .78),    # erectors beside the spine
        (73, 9, 65, 37, .89),      # external oblique
        (76, 3.8, 23, 24, .78),    # upper rectus abdominis
        (72, 3.8, 20, 22, .91),
        (68, 3.7, 17, 22, .68),
        (72, 10, 0, 9, -.28),      # linea alba
        (57, 8, 141, 43, .92),     # upper gluteal contour
    ),
    "arm": (
        (91, 5, 57, 70, 1.19),     # anterior and lateral deltoid
        (89, 5, 137, 55, .77),      # posterior deltoid
        (83, 7, -10, 65, 1.13),     # biceps brachii
        (84, 7, 148, 61, 1.05),     # triceps
        (81, 6, 70, 23, .42),       # brachialis
        (72, 6, 49, 65, 1.06),      # brachioradialis
        (70, 7, -48, 65, .79),      # forearm flexors
        (70, 7, 133, 68, .74),      # forearm extensors
    ),
    "leg": (
        (56, 7, 153, 66, 1.19),     # gluteus maximus
        (58, 6, 91, 49, .56),      # gluteus medius
        (51, 2.5, 156, 48, -.35),  # gluteal fold above the hamstrings
        (61, 3, 83, 60, -.74),     # taper the thigh into the pelvis
        (49, 14, 49, 71, 1.57),    # vastus lateralis
        (47, 12, -4, 56, 1.25),    # rectus femoris
        (39, 8, -41, 60, 1.28),    # vastus medialis above the knee
        (49, 13, -88, 42, .78),    # adductors
        (46, 13, 145, 48, 1.36),   # biceps femoris
        (46, 13, -151, 48, .91),   # medial hamstrings
        (23, 8, -151, 44, 1.37),   # medial gastrocnemius
        (24, 7, 141, 50, 1.23),    # lateral gastrocnemius
        (17, 7, 103, 60, .70),     # soleus
        (20, 10, 25, 42, .59),     # tibialis anterior, beside the shin
        (13, 6, 180, 35, -.42),    # Achilles taper
    ),
}

SCHOOL_PROFILES = {
    "hiruma_scout": {
        "muscles": HIRUMA_SCOUT,
        "families": {
            "hiruma": {
                "female": ((59, 12, 86, 58, .40), (90, 6, 76, 52, -.26)),
                "male": ((59, 9, 86, 58, .16), (90, 6, 76, 52, .26)),
            },
        },
    },
}

# Apply the profile only to confirmed scouts. Model-specific conditioning
# factors tune the same muscles without inferring training from a surname.
MODEL_PROFILES = {
    "trav_natsuko": ("hiruma_scout", "hiruma", 1.0),
    "side_h_scout": ("hiruma_scout", "hiruma", .92),
    "side_ryoichi": ("hiruma_scout", "hiruma", .79),
}

# Torso, arm and leg conditioning. These are design strengths, not lore stats.
TRAINING = {
    "hiruma_scout": (1., 1., 1.),
    "hida_bushi": (1.23, 1.25, 1.03),
    "kakita_bushi": (.90, 1.12, .99),
    "kitsuki_courtier": (.52, .51, .66),
    "akodo_bushi": (1.07, 1.05, 1.12),
    "isawa_shugenja": (.51, .49, .55),
    "shosuro_shinobi": (.88, .89, 1.13),
    "ide_emissary": (.61, .61, .77),
    "shiba_yojimbo": (1.02, 1.10, 1.02),
    "shiba_bushi": (.98, 1.08, 1.04),
    "bayushi_bushi": (.95, 1.07, 1.02),
    "iuchi_shugenja": (.56, .53, .73),
    "doji_courtier": (.53, .51, .58),
    "agasha_shugenja": (.56, .57, .59),
    "daidoji_bushi": (1.05, 1.04, 1.04),
    "akodo_cavalry": (.96, .95, 1.14),
    "yogo_shugenja": (.58, .54, .60),
    "kaiu_engineer": (.79, 1.03, .83),
    "kitsu_sodan_senzo": (.56, .54, .64),
    "mantis_bushi": (1.03, 1.11, .99),
    "asahina_shugenja": (.50, .48, .56),
    "ronin": (.88, .94, .93),
    "martial_unlisted": (.90, .97, .96),
    "civilian_unlisted": (.49, .55, .61),
}

# Documented primary schools take precedence over equipment or family.
AUTHORED_SCHOOLS = {
    "trav_rensei": "kakita_bushi",
    "trav_gendo": "kitsuki_courtier",
    "trav_shizue": "akodo_bushi",
    "trav_haruki": "isawa_shugenja",
    "trav_mitsue": "shosuro_shinobi",
    "trav_tamotsu": "ide_emissary",
    "trav_sayo": "ronin",
    "side_ashimita": "shiba_yojimbo",
    "side_goro": "hida_bushi",
    "side_rin": "akodo_bushi",
    "side_hideki": "bayushi_bushi",
    "side_saran": "iuchi_shugenja",
    "side_chiyo": "doji_courtier",
    "side_daigo": "agasha_shugenja",
    "side_toshiro": "shiba_bushi",
    "side_fujio": "ide_emissary",
    "side_sakura": "daidoji_bushi",
    "side_takeo": "akodo_cavalry",
    "side_mai": "yogo_shugenja",
    "side_michio": "isawa_shugenja",
    "side_momo": "kitsuki_courtier",
    "side_shino": "kaiu_engineer",
    "side_reiko": "kitsu_sodan_senzo",
    "side_kaito": "mantis_bushi",
    "side_yoshiro": "asahina_shugenja",
    "side_kenta": "bayushi_bushi",
}
FAMILIES = frozenset("""
    hiruma hida kaiu kuni yasuki akodo matsu ikoma kitsu kakita doji daidoji asahina
    mirumoto kitsuki togashi tamori agasha isawa shiba asako bayushi shosuro soshi yogo
    ide shinjo iuchi moto yoritomo moshi tsuruchi seppun otomo miya
""".split())
FAMILY_SHAPE = {
    "hida": ((88, 7, 78, 63, .48), (59, 10, 85, 66, .26)),
    "kakita": ((87, 8, 70, 52, .18),),
    "akodo": ((87, 9, 79, 55, .22),),
    "hiruma": ((59, 8, 88, 60, .19),),
}
SEX_SHAPE = {
    "female": ((59, 12, 86, 58, .30), (90, 6, 76, 52, -.14)),
    "male": ((59, 9, 86, 58, .12), (90, 6, 76, 52, .18)),
}


def anatomy_group(spec):
    """School, family and authored sex, in roster review order."""
    key = spec.get("model_key")
    sex = "female" if spec.get("female") else "male"
    scout = MODEL_PROFILES.get(key)
    if scout:
        return scout[0], scout[1], sex
    surname = spec.get("name", "").split(maxsplit=1)
    family = surname[0].lower() if surname and surname[0].lower() in FAMILIES else "unlisted"
    school = AUTHORED_SCHOOLS.get(key)
    if not school:
        build = spec.get("build", "")
        school = "martial_unlisted" if build.startswith("armored") or build == "heavy" else "civilian_unlisted"
    return school, family, sex


def eased_bump(distance, radius):
    if abs(distance) >= radius:
        return 0.
    return (1. + cos(pi * distance / radius)) * .5


def surface_relief(muscles, conditioning, symmetric, y, angle):
    if symmetric:
        angle = abs((angle + pi) % tau - pi)
    # This angle is periodic so the two calf heads meet behind the leg.
    value = 0.
    for height, height_radius, heading, angle_radius, amount in muscles:
        vertical = eased_bump(y - height, height_radius)
        if vertical:
            angle_distance = (angle - heading * pi / 180 + pi) % tau - pi
            value += vertical * eased_bump(angle_distance, angle_radius * pi / 180) * amount
    return value * conditioning


# These landmarks define the silhouette before any school conditioning.
# Keep the deltoid cap and the transition from the iliac crest into the thigh.
BODY_LANDMARKS = {
    "arm": ((93.1, 4.4, 87, 97, 1.08), (92.2, 4.7, 22, 66, .48),
            (91.8, 5.2, 151, 57, .55)),
    "torso": ((93., 3.9, 83, 69, .80), (59., 7.2, 89, 65, .90),
              (57., 5.9, 141, 57, .47)),
    "leg": ((57.6, 6.5, 100, 69, .88), (55.8, 7., 158, 64, .48)),
}
HIP_LANDMARKS = {
    "female": {
        "torso": ((57.4, 6.6, 96, 66, .48),),
        "leg": ((56.5, 6., 96, 64, .42),),
    },
    "male": {
        "torso": ((59., 6.4, 91, 66, .25),),
        "leg": ((57.5, 6., 103, 62, .24),),
    },
}


def landmarks(section, sex, y, angle):
    points = BODY_LANDMARKS[section] + HIP_LANDMARKS[sex].get(section, ())
    return surface_relief(points, 1., section == "torso", y, angle)


def human_relief(spec, section):
    """Return an offset on the existing skin surface for a model and body section."""
    school, family, sex = anatomy_group(spec)
    muscles = HIRUMA_SCOUT[section]
    if school == "hiruma_scout":
        conditioning = MODEL_PROFILES[spec["model_key"]][2]
        if section == "torso":
            muscles += SCHOOL_PROFILES[school]["families"][family][sex]
    else:
        conditioning = TRAINING[school][("torso", "arm", "leg").index(section)]
        if spec.get("age") in ("old", "young"):
            conditioning *= .78
        if section == "torso":
            muscles += FAMILY_SHAPE.get(family, ()) + SEX_SHAPE[sex]
    def relief(y, angle):
        return (landmarks(section, sex, y, angle)
                + surface_relief(muscles, conditioning, section == "torso", y, angle))

    return relief


@lru_cache(maxsize=32768)
def shared_garment_relief(section, y, angle):
    """An outward-only envelope for equipment worn by any human model."""
    muscles = HIRUMA_SCOUT[section]
    strongest = max(values[("torso", "arm", "leg").index(section)] for values in TRAINING.values())
    clearance = max(landmarks(section, sex, y, angle) for sex in SEX_SHAPE)
    if section != "torso":
        return clearance + max(0., surface_relief(muscles, strongest, False, y, angle))
    coats = (
        surface_relief(muscles + family + sex, strongest, True, y, angle)
        for family in ((), *FAMILY_SHAPE.values())
        for sex in SEX_SHAPE.values()
    )
    scout_fit = (surface_relief(muscles + sex, 1., True, y, angle)
                 for sex in SCHOOL_PROFILES["hiruma_scout"]["families"]["hiruma"].values())
    return clearance + max(0., *coats, *scout_fit)
