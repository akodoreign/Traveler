"""Write the two art prompts (cores, limbs) for a batch of seven cast members from their look specs.

py -3.12 -E tools\\cutout_prompt.py hanae haku hayato h_archer h_kuni h_engineer h_herbalist
"""
import sys

import gen_sidecast as sc

COLOURS = {
    "black": (30, 28, 32), "charcoal grey": (72, 72, 82), "grey": (150, 150, 158), "white": (236, 236, 236),
    "cream": (232, 222, 196), "dark brown": (86, 62, 44), "brown": (128, 92, 60), "ochre-brown": (160, 122, 62),
    "tan": (196, 164, 116), "mustard yellow": (212, 168, 60), "golden yellow": (238, 200, 88),
    "orange": (226, 120, 50), "burnt orange": (190, 92, 44), "red": (176, 44, 44), "dark red": (124, 36, 40),
    "crimson": (168, 30, 50), "pink": (230, 160, 170), "purple": (116, 74, 156), "lavender": (198, 190, 216),
    "navy blue": (48, 56, 84), "slate blue": (70, 88, 120), "blue": (64, 100, 170), "light blue": (150, 190, 232),
    "teal": (56, 128, 120), "sea green": (72, 150, 122), "green": (60, 122, 80), "dark green": (44, 68, 52),
    "olive green": (110, 120, 70), "grey-brown": (112, 100, 88), "muted blue-grey": (92, 104, 120),
}
HAIR = {"short": "short hair", "spiky": "short spiky hair", "mane": "a long shaggy mane of hair",
        "chonmage": "hair in a samurai topknot", "ponytail": "hair in a high ponytail", "bun": "hair in a bun",
        "bob": "a chin-length bob", "long": "long loose hair", "bald": "a completely bald head",
        "long_topknot": "long hair in a topknot"}
HEADWEAR = {"jingasa": "a low conical lacquered war hat", "kasa": "a wide woven straw hat",
            "hachimaki": "a cloth headband", "headcloth": "a cloth head-wrap", "kabuto": "a samurai helmet",
            "kabuto_full": "a horned samurai helmet", "eboshi": "a tall black court cap"}
BUILD = {"armored": "full lamellar armor with {lace} lacing over a {top} kimono, armor coloured {armor}",
         "armored_light": "light lamellar armor with {lace} lacing over a {top} kimono, armor coloured {armor}",
         "robe": "a {top} robe with a {accent} sash, no armor", "monk": "a {top} monk's robe, no armor",
         "peasant": "a plain worn {top} work jacket with a rope belt, no armor",
         "heavy": "heavy lamellar armor with {lace} lacing, armor coloured {armor}, on a big broad torso",
         "round": "a {top} kimono over a round belly, {accent} sash, no armor"}
HEAD = """Create an ORIGINAL pixel-art CHARACTER RIG PARTS ATLAS for a Japanese fantasy RPG on a plain flat pure WHITE background (no checkerboard, no texture). Production source artwork for puppet rigs, NOT animation frames, NOT assembled people. Exactly SIX equal-width COLUMNS and SEVEN equal-height ROWS: 42 isolated pieces, ONE centered piece per cell with generous white gutters; no text, labels or grid lines. Leave a clear empty margin on all four edges; every piece of the bottom row must be COMPLETE and fully inside the image. Every piece has a continuous dark outline. Crisp detailed illustrated pixel art like sophisticated adult-proportioned 1990s Japanese RPG battle sprites: thin dark outlines, restrained shaded cloth, readable faces, realistic anatomy, NOT chibi. All pieces at one consistent scale.
COLUMN 1: detached HEAD with a short neck, three-quarter view facing RIGHT. COLUMN 2: the same head, FRONT view. COLUMN 3: the same head, BACK view. Heads show head, hair, any headwear and a bare neck only: no shoulders, no collar.
COLUMNS 4, 5 and 6 are SLEEVELESS TORSO CORES on a tailor's dummy, like armless vests: from the collar to just below the belt, with a short flare of cloth below the belt. ABSOLUTELY NO sleeves, NO arms, NO hanging sleeve cloth on either side, NO head, NO hair, NO legs. Each torso ends at both shoulders in the dummy's bare arm socket: a plain flat GREY-BROWN disc on EACH side, clearly visible. The dummy's neck stub on top is the same flat GREY-BROWN. COLUMN 4: three-quarter view facing RIGHT. COLUMN 5: FRONT view. COLUMN 6: BACK view. All three torsos in a row are the same garment and the same narrow armless silhouette.
The seven ROWS, top to bottom, are seven different people; repeat each identity faithfully across the six cells:
{rows}"""
LIMB = """Create an ORIGINAL pixel-art CHARACTER RIG LIMBS ATLAS for a Japanese fantasy RPG on a plain flat pure WHITE background (no checkerboard, no texture). Every piece has a continuous dark outline; leave a clear empty margin on all four edges. Production modular artwork for puppet rigs, NOT poses, NOT animation frames, NOT assembled characters. Exactly SIX equal-width COLUMNS and SEVEN equal-height ROWS: 42 isolated pieces, one complete limb per cell, generous white gutters; no text, labels or grid. Crisp detailed illustrated pixel art for adult-proportioned 1990s Japanese RPG battle sprites: thin dark outlines, controlled fabric shading, realistic anatomy, NOT chibi. Every limb hangs perfectly straight and vertical, relaxed and unoccluded, complete at both ends for overlapping joints.
COLUMN 1: a full relaxed LEFT ARM seen from the front, from the shoulder through the sleeve to a loosely curled hand at the bottom, holding nothing. COLUMN 2: the matching RIGHT ARM from the front. COLUMN 3: the LEFT ARM seen from behind. COLUMN 4: the RIGHT ARM seen from behind. COLUMN 5: one complete LEG in side view, straight and vertical, long and slim, from the hip through thigh and shin to the foot, toes pointing RIGHT; the foot is small and natural (about one fifth of the leg's height in length). COLUMN 6: the other leg in the same side view, toes also pointing RIGHT. Legs are two separate trouser legs with rounded hip ends, no pelvis, feet complete. Each arm cell contains ONLY the arm and its sleeve: no torso, no robe skirt, no trouser cloth and no second layer of differently coloured fabric beside or behind the arm. Sleeves are close-fitting kimono sleeves that end at the wrist, not wide hanging drapes.
The seven ROWS, top to bottom, match seven different people:
{rows}
NO weapons or accessories anywhere. All four arm views and both legs for EVERY row."""


def colour(rgb):
    return min(COLOURS, key=lambda name: sum((a - b) ** 2 for a, b in zip(COLOURS[name], rgb)))


def describe(key):
    c = next(character for character in sc.CAST if character["key"] == key)
    top, lower, accent, armor, lace = sc.CLAN[c["clan"]]
    tones = {name: colour(c.get(name) or default) for name, default in
             (("top", c.get("haori") or top), ("lower", lower), ("accent", accent), ("armor", armor), ("lace", lace))}
    skin = "tan" if c["skin"] == sc.TAN else "pale" if c["skin"] == sc.PALE else "light"
    who = ("elderly " if c.get("age") == "old" else "") + ("woman" if c.get("female") else "man")
    if c.get("height", 0) <= -6:
        who = "child of about ten"
    build = c.get("build", "normal")
    armored = build.startswith("armored") or build == "heavy"
    face = [f"{skin} skin", "a completely bald head" if c.get("hairstyle") == "bald" else
            f"{colour(c['hair'])} " + HAIR.get(c.get("hairstyle"), "short hair")]
    face += [text for flag, text in ((c.get("facial"), f"a {str(c.get('facial')).replace('_', ' and ')}"),
                                     (c.get("scar"), "a scar on the face"), (c.get("glasses"), "round glasses"),
                                     (c.get("mask"), f"a {c.get('mask')} mask over the face")) if flag]
    wear = c.get("hat") or c.get("head")
    if wear:
        item = HEADWEAR.get(wear, wear)
        if wear == "jingasa" and (c.get("hat_col") or c["clan"] in ("peasant", "eta", "ronin")):
            item = "a conical woven straw hat"
        face.append(f"wearing {item} on all three heads")
    for name in ("eyes", "brow", "mouth"):
        if c.get(name):
            face.append(f"{c[name]} {'brows' if name == 'brow' else name}")
    outfit = BUILD.get(build, "a {top} kimono with a {accent} sash, no armor").format(**tones)
    if c.get("haori") and not armored:
        outfit = f"a {tones['top']} haori coat over a {colour(c.get('top', top))} kimono, {tones['accent']} sash, no armor"
    if c.get("pattern"):
        outfit += f", subtle {c['pattern']} pattern"
    if c.get("trim") == "fur":
        outfit += ", fur trim"
    sleeves = (f"{tones['armor']} lamellar shoulder and forearm guards with {tones['lace']} lacing over {tones['top']} sleeves"
               if armored else "completely bare muscular arms" if build == "monk" else f"{tones['top']} sleeves")
    legs = f"{tones['lower']} " + ("hakama legs with " + tones["armor"] + " shin guards, dark sandals" if armored
                                   else "rough trousers tied at the calf, straw sandals on bare feet"
                                   if build in ("peasant", "monk") or c["clan"] in ("peasant", "eta")
                                   else "pleated hakama legs, white tabi socks and sandals")
    label = f"{c['name']} ({c['clan']} clan {who})"
    return (f"{label}: {', '.join(face)}; {outfit}.", f"{label}: {skin} hands; {sleeves}; {legs}.")


def pending():
    """Cast keys not yet in a batch: hirelings first, then the cast list in order."""
    import json
    import hirelings
    import rig3d
    done = {key for batch in json.loads((rig3d.ROOT / "tools" / "cutout_batches.json").read_text()).values()
            for key in batch} | {"yosai"}
    order = [h["key"] for h in hirelings.HIRELINGS] + [c["key"] for c in sc.CAST]
    return [key for key in dict.fromkeys(order) if key not in done]


def main():
    if sys.argv[1:] == ["next"]:
        todo = pending()
        print(f"{len(todo)} left; next: {' '.join(todo[:7])}")
        sys.argv[1:] = todo[:7] + ["rows"]
    if len(sys.argv) not in (8, 9):
        sys.exit(__doc__)
    rows = [describe(key) for key in sys.argv[1:8]]
    for template, column in ((HEAD, 0), (LIMB, 1)):
        text = "\n".join(f"ROW {i + 1} {row[column]}" for i, row in enumerate(rows))
        print(text if len(sys.argv) == 9 else template.format(rows=text))     # an eighth argument: rows only
        print("=" * 20)


if __name__ == "__main__":
    main()
