"""Build a resumable staging pack of native RPG-Cobo battle foes."""
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from zlib import crc32

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent
ROOT = TOOLS.parent
PROJECT = ROOT / "_tools" / "rpgcobo-tool" / "project"
STAGE = ROOT / "_art" / "preview" / "foe3d"

# Explicit source-art families: new or renamed art must be classified before export.
FAMILIES = {
    "goblin": "goblin_hat goblin_anim goblin_warmonger foe_goblin_sneak foe_goblin_chucker foe_goblin_berserker",
    "ratfolk": "nezumi_warrior boss_nezumi_shaman",
    "ogre": "troll boss_troll boss_cellar_ogre foe_ogre_hag foe_free_ogre",
    "demon": "boss_kommei boss_tsukakoro boss_red_oni boss_ianwa boss_ashimoshi boss_hioninmaru boss_kuzushi "
             "boss_ryozo_oni boss_nashiko_true boss_okura oni_spawn boss_regret foe_onibaba foe_tsuno other_face",
    "ghoul": "gaki ash_ghoul foe_aka_name foe_ghul foe_zokujin_miner foe_zokujin_hunter",
    "tengu": "tengu boss_tengu_red",
    "serpent": "mamushi paddy_python sea_eel blood_leech foe_blood_eel boss_orochi foe_nukekubi",
    "naga": "naga_scout boss_naga_champion",
    "swimmer": "foe_aoizame foe_ningyo",
    "crab": "tide_crab",
    "crawler": "cave_beetle kumo_brood tsuchigumo boss_horror foe_hyakuhei foe_heart_grubs foe_oni_no_akuma",
    "flier": "cave_bats giant_hornet carrion_crow foe_hanemuri",
    "beast": "onikage snow_bear grey_wolf foe_badger foe_crocodile foe_bakeneko foe_mujina foe_monkeys "
             "foe_tiger foe_ape wild_boar wolfrider boss_tomie_tiger kappa",
    "plant": "lava_dryad toothed_poppy boss_kansen_hana foe_tanglevines foe_stinger_plant",
    "spirit": "yurei boss_shelf_kami boss_stolen_face mieko_shadow fire_elemental umibozu paper_spirit "
              "fear_shade fever_spirit will_o_wisp foe_muck_monster foe_shadowspawn boss_nashiko_time foe_skull_tide",
    "relic": "powder_keg bloodstone_basin inkpot lantern burning_bridge guardian_stone boss_mine_guardian",
}
BOSS_HUMANS = {
    "akutsukai": ("moto_akutsukai", None), "yasurugi": ("clan_duellist", "yasurugi"),
    "miyako": ("blood_acolyte", "miyako"), "chihaya": ("mantis_corsair", "chihaya"),
    "yosuke": ("storm_renegade", "yosuke"), "katsuo": ("hatamoto_champion", "katsuo"),
    "masanori": ("clan_duellist", "masanori"), "otamai": ("maho_tsukai", "otamai"),
    "nagai": ("matsu_berserker", "nagai"), "seppun_duelist": ("hatamoto_champion", None),
    "rokuro": ("matsu_berserker", "rokuro"), "mieko_dark": ("maho_tsukai", "mieko"),
    "ushimo": ("hatamoto_champion", "ushimo"), "akuro": ("stitched_monk", "akuro"),
    "kumpei": ("clan_duellist", "kumpei"), "munashii": ("stitched_monk", "munashii"),
    "naohida": ("bandit_lord", "naohida"), "kurosho": ("iuchi_shugenja", "kurosho"),
    "order_enforcer": ("snake_enforcer", None), "crab_shade": ("heavy_infantry", "kisada"),
    "nashiko_bride": ("blood_acolyte", "nashiko"),
}
CLIPS = (("stand", "idle8", 9, 8, True), ("fight", "ready", 2, 8, True),
         ("walk", "walk8", 9, 12, True), ("attack", None, 7, 14, False),
         ("magic", "cast", 6, 10, False), ("damage", "hurt", 4, 12, False),
         ("guard", "guard", 3, 10, False), ("dead", "collapse", 6, 10, False))
ALIASES = {"attack": "atk atk_normal slash1 punch1 stick1 bow1 blast1",
           "magic": "cast magic1 spell", "damage": "hurt pain", "dead": "ko down"}
ATTACK = {"fist": "atk_thrust", "pole": "atk_thrust", "blade": "atk_slash", "iai": "atk_draw",
          "short": "atk_thrust", "club": "atk_overhead", "bow": "atk_slash", "gun": "atk_slash"}


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path, data):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    temporary.replace(path)


def clips(family):
    frames, animap = [], []
    for name, pose, count, speed, loop in CLIPS:
        start = len(frames)
        pose = pose or ATTACK[family]
        # Loop back to the exact first pose; never interpolate into the next clip.
        n = count - 1 if name in ("stand", "walk") else count
        frames.extend((pose, i % n, n) for i in range(count))
        frames.append(frames[-1])
        for alias in (name, *ALIASES.get(name, "").split()):
            animap.append(dict(id=alias, st=start, en=start + count - 1, spd=speed, loop=loop, replay=not loop))
    return frames, animap


def plan():
    from chara3d_sheet import family, look
    from gen_human_enemies import ENEMIES, config
    from gen_sidecast import CAST
    from gen_sprites2d import TRAVELERS
    from gear_palette import costume_tones

    authored = {item["key"]: config(item) for item in ENEMIES}
    existing = {"side_" + item["key"] for item in CAST} | {"trav_" + item["key"] for item in TRAVELERS}
    creature = {name: kind for kind, names in FAMILIES.items() for name in names.split()}
    pictures = read(PROJECT / "resource" / "enemy_pic.json")
    refs = defaultdict(dict)
    for eid, enemy in read(PROJECT / "data" / "enemy.json").items():
        if enemy.get("mdlid") and not str(enemy.get("name", "")).startswith("(unused"):
            refs[enemy["mdlid"]][eid] = enemy.get("name", eid)
    jobs = {}
    unclassified = []
    for ep, names in sorted(refs.items(), key=lambda entry: int(entry[0][2:])):
        source = Path(pictures[ep]["pic3d"]).stem
        spec = authored.get(source.removeprefix("hum_"))
        if source in existing:
            spec = look(source)
        elif source.startswith("boss_") and source[5:] in BOSS_HUMANS:
            template, person = BOSS_HUMANS[source[5:]]
            key = "side_" + person if person else None
            spec = authored[template] | (look(key) if key in existing else {})
            if key not in existing:
                spec.update(costume_tones(spec.get("clan", spec.get("mon")), spec))
        elif spec:
            spec = spec | costume_tones(spec.get("clan", spec.get("mon")), spec)
        kind = "human" if spec else creature.get(source)
        if not kind:
            unclassified.append(f"{ep} ({source})")
            continue
        kin = family(spec) if spec else "fist"
        _, animap = clips(kin)
        jobs[ep] = dict(source=source, enemies=names, recipe=kind, spec=spec, family=kin, animap=animap,
                        picture=pictures[ep]["pic3d"])
    if unclassified:
        raise ValueError("Unclassified foe art: " + ", ".join(unclassified))
    return jobs


def costume(c, skin, spec):
    head = {"head": 1.}
    if spec.get("hat") == "jingasa":
        straw = tuple(spec.get("hat_col", c.STRAW))
        skin.add(c.tube([((0, 115, 0), 16, 17), ((0, 116.8, 0), 15, 16),
                         ((0, 125, 0), 3, 3.2)], 36), straw, head)
        skin.add(c.tube([((0, 115, 0), 16.3, 17.3), ((0, 115.9, 0), 16, 17)], 36),
                 c.shade(straw, .63), head)
    if spec.get("sashimono"):
        spine = {"spine": 1.}
        skin.add(c.box((-9, 108, 3), (.8, 33, .8)), c.WOOD, spine, smooth=False)
        skin.add(c.box((-9, 120, 10), (1, 16, 7.5)), tuple(spec["sashimono"]), spine, smooth=False)


def human(c, spec):
    spec = dict(spec)
    if spec.get("head") in ("kabuto", "kabuto_full"):
        spec["iron_cap"] = True
        spec.setdefault("armor", spec.get("helm", (75, 74, 80)))
    if spec.get("head") == "headcloth":
        spec.update(head="hachimaki", band=spec.get("cloth", spec["accent"]))
    skin = c.build_character(spec)
    costume(c, skin, spec)
    return skin


def creature_model(c, entry):
    from mathutils import Vector

    src, kind = entry["source"], entry["recipe"]
    seed = crc32(src.encode("ascii"))
    palettes = {
        "goblin": (101, 127, 67), "ratfolk": (110, 82, 65), "ogre": (122, 102, 79),
        "demon": (137, 57, 55), "ghoul": (100, 125, 111), "tengu": (59, 61, 77),
        "serpent": (86, 108, 67), "naga": (82, 131, 118), "swimmer": (60, 109, 135),
        "crab": (64, 120, 139), "crawler": (78, 64, 86), "flier": (58, 65, 81), "beast": (110, 87, 67),
        "plant": (82, 118, 54), "spirit": (129, 158, 181), "relic": (116, 87, 64),
    }
    main = tuple(max(12, min(240, v + (seed >> (i * 4)) % 29 - 14)) for i, v in enumerate(palettes[kind]))
    if "tiger" in src or "bakeneko" in src:
        main = (208, 122, 49)
    elif "snow" in src or "yurei" in src:
        main = (198, 208, 211)
    elif "fire" in src or "burning" in src or "lava" in src:
        main = (185, 74, 40)
    elif "crab" in src:
        main = (64, 120, 139)
    dark, light = c.shade(main, .55), c.shade(main, 1.1, 24)
    ivory, eye = (222, 209, 157), (249, 167, 66)
    skin, joints = c.Skin(), {"root": ((0, 0, 0), "root", 0)}

    def joint(name, p, motion, phase=0):
        joints[name] = (p, motion, phase)
        return name

    def orb(p, size, colour=main, bone="root"):
        skin.add(c.ellipsoid(p, size, 16, 10), colour, {bone: 1.})

    def rod(a, b, r1, r2, colour=main, bone="root"):
        a, b = Vector(a), Vector(b)
        tangent = (b - a).normalized()
        u = tangent.cross(Vector((1, 0, 0) if abs(tangent.x) < .8 else (0, 1, 0))).normalized()
        v = tangent.cross(u)
        n = 10
        verts = [tuple(p + r * (u * math.cos(i * math.tau / n) + v * math.sin(i * math.tau / n)))
                 for p, r in ((a, r1), (b, r2)) for i in range(n)]
        faces = [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
        skin.add((verts, faces + [tuple(reversed(range(n))), tuple(range(n, 2 * n))]), colour, {bone: 1.})

    def fin(points, colour, bone):
        skin.add((points, [(0, 1, 2), (0, 3, 1), (1, 3, 2), (2, 3, 0)]), colour, {bone: 1.})

    def eyes(x, y, z, bone):
        for s in (-1, 1):
            orb((x - 1, y, s * z), (3.3, 3.2, 2.6), dark, bone)
            orb((x + 1, y, s * z), (2.1, 1.7, 1.7), eye, bone)

    if kind in {"goblin", "ogre", "ratfolk", "demon", "ghoul", "tengu", "naga"}:
        size = {"goblin": .66, "ratfolk": .85, "ghoul": .87, "tengu": .95,
                "demon": 1.13, "ogre": 1.22, "naga": .96}[kind]
        y = 57 * size
        h = joint("head", (5, y + 15, 0), "head")
        orb((0, y - 15, 0), (12, 21, 17 * size), dark)
        orb((1, y, 0), (16 * size, 22 * size, 19 * size))
        orb((8, y + 25 * size, 0), (13 * size, 13 * size, 13 * size), main, h)
        snout = 11 * size if kind in ("ratfolk", "tengu", "naga") else 6 * size
        orb((14 * size + 8, y + 22 * size, 0), (snout, 4.7 * size, 7 * size), light, h)
        eyes(10 + 11 * size, y + 28 * size, 7.6 * size, h)
        skin.loft([(y - 28, 12, 18 * size), (y - 16, 15, 20 * size), (y - 13, 15, 19 * size)],
                  (98, 63, 47), lambda _: {"root": 1.}, n=16, pleats=None)
        for s in (-1, 1):
            z = s * 17 * size
            a = joint("arm" + str(s), (0, y + 7, z), "leg", s)
            rod((0, y + 7, z), (6, y - 6, 1.5 * z), 7 * size, 5 * size, main, a)
            rod((6, y - 6, 1.5 * z), (17, y - 21, 1.6 * z), 5.4 * size, 4 * size, light, a)
            orb((18, y - 21, 1.61 * z), (6 * size, 5 * size, 4.5 * size), main, a)
            for digit in (-1, 0, 1):
                rod((20, y - 22, 1.61 * z + 2.5 * digit), (25, y - 24, 1.61 * z + 3 * digit),
                    1.15, .12, ivory, a)
            if kind != "naga":
                l = joint("leg" + str(s), (-2, y - 19, .65 * z), "leg", -s)
                rod((-2, y - 19, .65 * z), (-5, 11, .8 * z), 8 * size, 5 * size, dark, l)
                orb((0, 5, .82 * z), (9 * size, 5, 6 * size), main, l)
            if kind in ("demon", "ogre", "goblin", "ratfolk"):
                rod((4, y + 28 * size, .7 * z), (-1, y + 42 * size, z), 4.8 * size, .25, ivory if kind in ("demon", "ogre") else main, h)
            if kind == "tengu":
                w = joint("wing" + str(s), (-7, y + 10, .7 * z), "wing", s)
                for i in range(5):
                    fin([(-6, y + 9, .7 * z), (-20 - i * 6, y + 31 - i * 5, z * (2.8 - i * .24)),
                         (-29 - i * 5, y + 8 - i * 5, z * (2.6 - i * .24)), (-16, y + 13, z)], dark, w)
        if kind in ("naga", "ratfolk"):
            for i in range(8):
                p = (-i * 7, max(6, y - 32 - i * 4), 8 * math.sin(i * .6))
                orb(p, (9, max(2, 10 - i), max(2, 10 - i)), main, joint(f"tail{i}", p, "tail", i))
        if "shaman" in src or "miner" in src or "warmonger" in src or "chucker" in src or "hat" in src:
            if "hat" in src:
                skin.add(c.tube([((6, y + 33 * size, 0), 18, 19),
                                 ((6, y + 35 * size, 0), 16, 17), ((6, y + 46 * size, 0), 2, 2)], 24),
                         c.STRAW, {h: 1.})
            else:
                a = "arm1"
                rod((17, y - 45, 28 * size), (24, y + 24, 28 * size), 2.5, 1.8, c.WOOD, a)
                orb((24, y + 28, 28 * size), (5, 7, 5), ivory if "shaman" in src else dark, a)
    elif kind in ("serpent", "swimmer"):
        heads = 3 if "orochi" in src else 1
        for k in range(heads):
            for i in range(13):
                p = (45 - 7.2 * i, 9 + (max(0, 5 - i) * 6 if kind == "serpent" else 15),
                     9 * math.sin(i * .59 + k) + (k - (heads - 1) / 2) * max(0, 6 - i) * 5)
                b = joint(f"segment{k}_{i}", p, "tail", i)
                radius = 4 + 8 * math.sin((i + 1) / 15 * math.pi) if i else 10
                orb(p, (10, radius * (.7 if kind == "swimmer" else .85), radius), main if i % 3 else dark, b)
                if i == 0:
                    orb((p[0] + 8, p[1] - 2, p[2]), (11, 5.5, 8), light, b)
                    for side in (-1, 1):
                        orb((p[0] + 7, p[1] + 3, p[2] + side * 7), (2, 1.5, 1.5), eye, b)
                if kind == "swimmer" and i in (3, 7, 12):
                    fin([p, (p[0] - 14, p[1] + 21, p[2]), (p[0] - 19, p[1] - 3, p[2]), (p[0] - 5, p[1], p[2] + 3)], dark, b)
    elif kind == "crab":
        coral, tips = (187, 105, 75), (224, 152, 108)
        # A shallow, wide carapace with one continuous shell, not an insect's segmented back.
        skin.loft([(11, 12, 19), (14, 17, 26), (18, 19, 30), (22, 17, 28),
                   (26, 13, 23), (28, 7, 12), (29, 1, 2)], main, lambda _: {"root": 1.}, n=36)
        skin.loft([(15.8, 18, 28), (18, 19.5, 30.5), (19.8, 19, 30)], light,
                  lambda _: {"root": 1.}, n=36)
        orb((2, 13, 0), (15, 5, 21), (158, 151, 114))
        for s in (-1, 1):
            for i, x in enumerate((10, 3, -5, -12)):
                p = (x, 17, s * (22 - i))
                elbow = (x - 3 - i, 24 - i, s * (34 - i))
                ankle = (x - 9 - i, 10, s * (43 - i))
                tip = (x - 11 - i, 1, s * (48 - i))
                b = joint(f"leg{s}_{i}", p, "leg", s * (-1) ** i)
                rod(p, elbow, 3.5, 2.8, main, b)
                orb(elbow, (2.9, 2.9, 2.9), dark, b)
                rod(elbow, ankle, 2.7, 1.6, light, b)
                rod(ankle, tip, 1.7, .35, coral, b)
            p = (11, 17, s * 18)
            b = joint(f"claw{s}", p, "claw", s)
            elbow, wrist = (19, 15, s * 30), (29, 19, s * 26)
            rod(p, elbow, 4.7, 4, main, b)
            rod(elbow, wrist, 4.3, 5.2, coral, b)
            size = 1.13 if s > 0 else .9
            palm = (34, 20, s * 25)
            orb(palm, (8 * size, 6 * size, 7 * size), coral, b)
            # Curved fingers leave a distinct open V from the battle camera.
            for side in (-1, 1):
                a = (37, 20, s * 25 + side * 4.5 * size)
                knuckle = (43, 21, s * 25 + side * 7.3 * size)
                end = (48 + (2 if side == s else 0), 22, s * 25 + side * 3.1 * size)
                rod(a, knuckle, 3.8 * size, 2.5 * size, coral, b)
                rod(knuckle, end, 2.6 * size, .65, tips, b)
            stalk, pupil = (17, 22, s * 7), (22, 30, s * 9)
            rod(stalk, pupil, 1.5, 1.3, main)
            orb(pupil, (2.9, 2.7, 2.6), dark)
            orb((23.6, 30.5, s * 9), (1.3, 1.5, 1.4), eye)
    elif kind == "crawler":
        count = 4 if any(word in src for word in ("kumo", "tsuchi", "horror", "hyakuhei")) else 3
        orb((-10, 21, 0), (25, 16, 24), dark)
        for i in range(4):
            orb((-25 + 11 * i, 26, 0), (11, 12 + i, 18), main)
        h = joint("head", (17, 19, 0), "head")
        orb((24, 18, 0), (13, 9, 13), light, h)
        eyes(33, 22, 8, h)
        for s in (-1, 1):
            for i in range(count):
                p = (-23 + i * 15, 18, 14 * s)
                b = joint(f"leg{s}_{i}", p, "leg", s * (-1) ** i)
                elbow, tip = (p[0] - 4, 29, s * (33 + i)), (p[0] + 10, 2, s * (43 + i))
                rod(p, elbow, 4, 3, main, b)
                rod(elbow, tip, 3.2, .8, dark, b)
            jaw = joint(f"claw{s}", (25, 17, s * 11), "leg", s)
            rod((28, 17, s * 10), (41, 15, s * 17), 5, 4, main, jaw)
            for off in (-1, 1):
                rod((40, 15, s * 17 + 3 * off), (51, 14, s * 17 + off), 3, .18, light, jaw)
    elif kind in ("beast", "flier"):
        airborne = kind == "flier"
        bear = any(w in src for w in ("bear", "ape", "mujina"))
        low = any(w in src for w in ("badger", "crocodile"))
        y = 47 if airborne else 39 if bear else 19 if low else 30
        orb((-5, y, 0), (28, 17 if bear else 13, 14), main)
        orb((16, y + 2, 0), (17, 15, 14), dark)
        h = joint("head", (18, y + 5, 0), "head")
        orb((26, y + 8, 0), (15, 12, 11), main, h)
        orb((38, y + 4, 0), (16 if "crocodile" in src else 10, 5.5, 7), light, h)
        eyes(36, y + 12, 7, h)
        t = joint("tail", (-25, y, 0), "tail", 2)
        rod((-25, y, 0), (-51, y + (13 if "tiger" in src else -4), 5), 6, 2, dark, t)
        for s in (-1, 1):
            rod((23, y + 13, 8 * s), (22, y + 26, 12 * s), 5, 1, main, h)
            if airborne:
                w = joint(f"wing{s}", (2, y + 4, 10 * s), "wing", s)
                for i in range(6):
                    fin([(7, y + 5, 7 * s), (3 - i * 6, y + 5 - i, (47 - i * 4) * s),
                         (-7 - i * 6, y + 3 - i, (41 - i * 4) * s), (-4, y + 8, 16 * s)], main if i % 2 else dark, w)
            else:
                for x in (-21, 16):
                    p = (x, y - 2, 10 * s)
                    b = joint(f"leg{x}_{s}", p, "leg", s * (1 if x > 0 else -1))
                    rod(p, (x + 2, 11, 13 * s), 7 if bear else 5, 3.7, main, b)
                    orb((x + 5, 4, 13 * s), (8, 4, 5), light, b)
        if "tiger" in src or "bakeneko" in src:
            for x in (-22, -13, -4, 6, 16):
                skin.add(c.tube([((x, y - 6, 0), 1.4, 13), ((x - 3, y + 4, 0), 2, 14.2),
                                 ((x - 5, y + 12, 0), 1, 7)], 16), dark, {"root": 1.})
        if "wolfrider" in src:
            orb((-3, y + 19, 0), (9, 13, 9), (114, 94, 65))
            orb((0, y + 33, 0), (8, 8, 8), (105, 129, 65))
            rod((-4, y + 7, 14), (22, y + 50, 14), 2.4, .25, c.WOOD)
    elif kind in ("plant", "spirit"):
        plant = kind == "plant"
        orb((0, 13 if plant else 27, 0), (20, 13, 19), dark)
        for i in range(5):
            p = (4 * math.sin(i), 16 + i * 11, 0)
            b = joint(f"coil{i}", p, "tail", i)
            orb(p, (17 - i * 1.8, 13, 17 - i * 1.4), main, b)
        h = joint("head", (8, 58, 0), "head")
        orb((10, 66, 0), (17, 16, 16), light, h)
        eyes(23, 69, 8, h)
        for i in range(6 if plant else 4):
            angle = i * math.tau / (6 if plant else 4)
            x, z = math.cos(angle), math.sin(angle)
            b = joint(f"frond{i}", (0, 34, 0), "tail", i * 2)
            rod((0, 34, 0), (27 * x, 47, 27 * z), 4, 2.5, main, b)
            fin([(24 * x, 46, 24 * z), (40 * x, 66, 40 * z), (37 * x + 7, 40, 37 * z), (33 * x, 57, 33 * z - 4)], light, b)
            if plant:
                orb((x * 19, 71, z * 19), (9, 4, 9), c.shade(light, .82, 16), h)
    else:
        if "bridge" in src:
            for i in range(9):
                skin.add(c.box((-36 + 9 * i, 8 + (4 - abs(i - 4)), 0), (4.2, 3, 17)), main, {"root": 1.}, smooth=False)
            for i in range(5):
                rod((-30 + i * 15, 11, 5 * (-1) ** i), (-25 + i * 15, 31, 5 * (-1) ** i), 5, .2, (244, 145, 57))
        elif "stone" in src or "guardian" in src and "mine" in src:
            for i in range(5):
                p = (5 * math.sin(i * 2), 8 + i * 10, 0)
                skin.add(c.ellipsoid(p, (19 - i * 1.5, 11, 19 - i * 1.5), 6, 4), main, {"root": 1.}, smooth=False)
            eyes(13, 39, 6, "root")
        else:
            basin = "basin" in src
            height = 22 if basin else 42
            skin.loft([(0, 14, 14), (4, 18, 18), (height / 2, 23, 23),
                       (height - 3, 18, 18), (height, 16, 16)], main,
                      lambda _: {"root": 1.}, n=24, band=(2.8, lambda row, col: dark if row in (1, 2, 6, 7, 12, 13) else c.shade(main, .88 + (col % 3) * .1)))
            if basin or "lantern" in src or "inkpot" in src:
                b = joint("light", (0, height, 0), "head")
                orb((0, height + 3, 0), (15, 8, 15), (156, 58, 50) if basin else light, b)
    return skin, joints


def creature_rig(c, scene, frames, joints, recipe):
    from mathutils import Matrix

    rig = c.make_armature({name: c.frame(p, c.np.asarray(p) + c.EY, c.EX)
                           for name, (p, _, _) in joints.items()})
    for frame, (pose, i, count) in enumerate(frames):
        t = i / max(1, count - 1)
        wave = math.sin(math.tau * i / count)
        pulse = math.sin(math.pi * t)
        striking = pose.startswith("atk_")
        drift = (10 * pulse if striking else -5 * pulse if pose == "hurt" else 0)
        rise = (3 * wave if recipe in ("flier", "spirit", "swimmer") else 0) + (3 * pulse if pose == "cast" else 0)
        tilt = 72 * t if pose == "collapse" and recipe != "relic" else 0
        root = Matrix.Translation(c.blender((drift, rise, 0))) @ Matrix.Rotation(math.radians(tilt), 4, "Y")
        for bone in rig.pose.bones:
            _, motion, phase = joints[bone.name]
            angle, axis = 0., "Y"
            if motion == "wing":
                angle, axis = phase * (18 + 24 * wave), "X"
            elif motion == "claw":
                angle, axis = phase * (27 * pulse if striking else 4 * wave), "Z"
            elif motion == "leg":
                angle = phase * (23 * wave if pose == "walk8" else 14 * pulse if striking else 0)
            elif motion == "tail":
                angle, axis = 9 * math.sin(math.tau * i / count + phase * .58), "Z"
            elif motion == "head":
                angle = 17 * pulse if striking else -12 * pulse if pose == "hurt" else 3 * wave
            rest = bone.bone.matrix_local
            pivot = Matrix.Translation(rest.translation)
            local = pivot @ Matrix.Rotation(math.radians(angle), 4, axis) @ pivot.inverted()
            bone.matrix_basis = rest.inverted() @ root @ local @ rest
            for path in ("location", "rotation_quaternion", "scale"):
                bone.keyframe_insert(path, frame=frame, group=bone.name)
    scene.frame_start, scene.frame_end = 0, len(frames) - 1
    scene.frame_set(0)
    return rig


def asset_names(ep):
    return (f"{ep}.mdl", f"{ep}.pm", f"{ep}.mot")


def valid(directory, ep):
    mdl, pm, mot = (directory / name for name in asset_names(ep))
    return (all(p.is_file() and p.stat().st_size for p in (mdl, pm, mot))
            and f'motiondata = "{ep}.mot"' in pm.read_text(encoding="utf-8"))


def install(packs, jobs):
    models, sources = {}, {}
    sizes = {"crab": (.021, .65, .60), "crawler": (.018, .72, .57),
             "serpent": (.018, .83, .60), "beast": (.019, 1.1, .63),
             "flier": (.018, 1.45, .55), "human": (.013, 1.54, .47)}
    for folder in packs:
        for ep, entry in read(folder / "foes.json").items():
            spec = jobs.get(ep)
            if not spec or entry["source"] != spec["source"] or entry["picture"] != spec["picture"] or not valid(folder, ep):
                raise ValueError(f"{folder}: stale or invalid foe asset {ep}")
            scale, height, radius = sizes.get(entry["recipe"], (.016, 1.40, .52))
            models[ep] = dict(animap=entry["animap"], scale=scale, height=height, radius=radius)
            if entry["recipe"] == "human":
                models[ep]["human"] = True
            sources[ep] = (folder, entry["recipe"])
    if jobs.keys() != models.keys() or any(jobs[ep]["recipe"] != recipe for ep, (_, recipe) in sources.items()):
        raise ValueError("Provide a complete pack and any updated model packs, in that order")
    out = PROJECT / "resource" / "native_foe"
    out.mkdir(exist_ok=True)
    for ep, (folder, _) in sources.items():
        for name in asset_names(ep):
            shutil.copyfile(folder / name, out / name)
    for folder in packs:
        if (folder / "tex").is_dir():
            shutil.copytree(folder / "tex", out / "tex", dirs_exist_ok=True)
    if (out / "tex" / "foe_skin_color.png").is_file():
        from foe_skin_maps import install_skin_maps

        install_skin_maps(out, jobs)
    write(out / "index.json", models)
    print(f"Installed {len(models)} battle models in {out}")


def update_installed(pack, jobs):
    out = PROJECT / "resource" / "native_foe"
    models = read(out / "index.json")
    entries = read(pack / "foes.json")
    if not entries or models.keys() != jobs.keys():
        raise ValueError("An existing complete roster and a nonempty update pack are required")
    for ep, entry in entries.items():
        spec = jobs.get(ep)
        if (not spec or any(entry[k] != spec[k] for k in ("source", "picture", "recipe"))
                or entry["animap"] != models[ep]["animap"] or not valid(pack, ep)):
            raise ValueError(f"{pack}: stale or invalid foe asset {ep}")
    from foe_skin_maps import install_skin_maps

    # Put the staging files on the installed volume so Path.replace also works
    # when the artist exported the pack to a separate drive.
    with tempfile.TemporaryDirectory(prefix="foe-update-", dir=out.parent) as temp:
        stage = Path(temp)
        shutil.copytree(pack / "tex", stage / "tex")
        for texture in (stage / "tex").iterdir():
            if not (out / "tex" / texture.name).is_file() or texture.read_bytes() != (out / "tex" / texture.name).read_bytes():
                raise ValueError(f"{texture.name}: shared texture changed; use a complete pack")
        for ep in entries:
            shutil.copyfile(pack / f"{ep}.pm", stage / f"{ep}.pm")
        install_skin_maps(stage, {ep: jobs[ep] for ep in entries})
        for ep in entries:
            (stage / f"{ep}.pm").replace(out / f"{ep}.pm")
            for ext in ("mdl", "mot"):
                name = f"{ep}.{ext}"
                shutil.copyfile(pack / name, out / name)
            name = f"{ep.lower()}_skin.png"
            (stage / "tex" / name).replace(out / "tex" / name)
    print(f"Updated {len(entries)} installed battle models")


def export(job_path, material_only=False):
    sys.path.insert(0, str(HERE))
    import bpy
    import chara3d as c
    from chara3d_native import animate, clearCaches, save_piece
    from foe_surfaces import FoeSurface, make_textures

    job = read(job_path)
    out = job_path.parent
    scratch = out / "partial"
    scratch.mkdir(exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    textures = make_textures(out / "tex")
    installed = PROJECT / "resource" / "native_foe"
    journal = out / "completed.json"
    completed = set(read(journal)) if journal.exists() else set()
    for i, (ep, item) in enumerate(job.items(), 1):
        if ep in completed and valid(out, ep):
            continue
        print(f"FOE [{i}/{len(job)}] {ep} {item['source']} ({item['recipe']})", flush=True)
        frames, _ = clips(item["family"])
        clearCaches()
        if item["recipe"] == "human":
            rig = c.make_armature(c.rest_frames()) if material_only else animate(scene, ep, frames, item["family"])
            mesh = human(c, item["spec"])
        else:
            mesh, joints = creature_model(c, item)
            if material_only:
                rig = c.make_armature({name: c.frame(p, c.np.asarray(p) + c.EY, c.EX)
                                       for name, (p, _, _) in joints.items()})
            else:
                rig = creature_rig(c, scene, frames, joints, item["recipe"])
        if material_only:
            if not valid(installed, ep):
                raise RuntimeError(f"Missing installed model for {ep}")
            shutil.copyfile(installed / f"{ep}.mot", scratch / f"{ep}.mot")
        save_piece(scene, scratch, rig, ep, mesh, ep, write_motion=not material_only,
                   surface=FoeSurface(item, textures))
        if not valid(scratch, ep):
            raise RuntimeError(f"Incomplete asset trio for {ep}")
        animation = rig.animation_data.action if rig.animation_data else None
        armature = rig.data
        bpy.data.objects.remove(rig, do_unlink=True)
        bpy.data.armatures.remove(armature)
        if animation and animation.users == 0:
            bpy.data.actions.remove(animation)
        for name in asset_names(ep):
            (scratch / name).replace(out / name)
        completed.add(ep)
        write(journal, sorted(completed))
    if completed != set(job) or not all(valid(out, ep) for ep in job):
        raise RuntimeError("The completed pack does not match the foe inventory")
    write(out / "foes.json", {ep: {k: v for k, v in item.items() if k != "spec"} | {"model": f"{ep}.pm"}
                              for ep, item in job.items()})
    print(f"FOE Finished {len(job)} native model packs: {out}", flush=True)


def launch():
    sys.path.insert(0, str(TOOLS))
    from chara3d_sheet import blender_exe

    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--plan", action="store_true", help="inventory and validate without starting Blender")
    mode.add_argument("--only", nargs="+", metavar="EP", help="build selected foe picture IDs in a separate pack")
    mode.add_argument("--humans", action="store_true", help="stage only the human foe costumes")
    mode.add_argument("--install", nargs="+", type=Path, metavar="PACK", help="install a complete staged pack and updates")
    mode.add_argument("--update-installed", type=Path, metavar="PACK", help="apply a textured partial pack to the installed roster")
    parser.add_argument("--materials", action="store_true", help="refresh installed models while reusing battle motions")
    args = parser.parse_args()
    jobs = plan()
    if args.update_installed:
        update_installed(args.update_installed, jobs)
        return
    if args.install:
        install(args.install, jobs)
        return
    if args.only:
        missing = set(args.only) - jobs.keys()
        if missing:
            parser.error("Unknown picture IDs: " + ", ".join(sorted(missing)))
        jobs = {ep: item for ep, item in jobs.items() if ep in args.only}
    if args.humans:
        jobs = {ep: item for ep, item in jobs.items() if item["recipe"] == "human"}
    print(f"{len(jobs)} foe pictures / {sum(len(job['enemies']) for job in jobs.values())} enemy records: "
          + ", ".join(f"{kind}={count}" for kind, count in sorted(Counter(j["recipe"] for j in jobs.values()).items())),
          flush=True)
    if args.plan:
        return
    digest = sha256(json.dumps(jobs, sort_keys=True).encode())
    digest.update(str(args.materials).encode())
    for source in (Path(__file__), HERE / "chara3d.py", HERE / "chara3d_native.py",
                   HERE / "foe_surfaces.py", HERE / "anime_head.py", TOOLS / "rig3d_poses.py", TOOLS / "human_anatomy.py"):
        digest.update(source.read_bytes())
    out = STAGE / digest.hexdigest()[:16]
    out.mkdir(parents=True, exist_ok=True)
    path = out / "job.json"
    write(path, jobs)
    log = out / "blender.log"
    print(f"Staging at {out}; progress below, full output in {log.name}.", flush=True)
    command = [blender_exe(), "-b", "--factory-startup", "--threads", "4", "--python-exit-code", "1",
               "--python", str(Path(__file__).resolve()), "--", str(path)]
    if args.materials:
        command.append("--materials")
    with log.open("a", encoding="utf-8") as output, subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace"
    ) as proc:
        for line in proc.stdout:
            output.write(line)
            output.flush()
            if line.startswith("FOE "):
                print(line.rstrip(), flush=True)
        if proc.wait():
            raise SystemExit(f"Blender failed (exit {proc.returncode}); see {log}. Rerun to resume.")


if __name__ == "__main__":
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]
        export(Path(args[0]), material_only="--materials" in args)
    else:
        launch()
