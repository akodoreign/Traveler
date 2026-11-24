"""Regional commoner robes (user 2026-11-22: "go through the generic A100 robes and vary the colors based on region ...
i know there will be a lot of different browns for peasants but they all look generic").
Every townsperson in the generic Travelling Clothes (A100) dyed "peasant" / "eta" / "ronin" wore one texture each. This
re-dyes those textures the way blender/generated_wardrobe.dyes does (each pixel split over the five garment role
colours, the baked folds kept as shade): per region of Rokugan four everyday palettes (local dyes: Crab slate and
indigo, Crane grey-blue, Lion ochre, Phoenix persimmon, Scorpion maroon, Dragon moss, Unicorn plum, Mantis teal),
eta one muted regional palette, ronin four of their own. Writes
  resource/native_tailoring/tex/<peasant|eta|ronin>/<mesh>_<region>_<k>.png  (ronin: <mesh>_any_<k>.png)
  plugin/rokugan/RokuganCommonerDyes.sk  (::Rokugan.DYE_REGION map -> region; the pick happens at runtime)
2026-11-24: most A100 townsfolk now wear one of the other plain robes (tools/vary_npc_outfits.py POOL); those meshes get
the same regional dyes, so MESHES = A100 + POOL.
python -E tools/gen_commoner_dyes.py [--maps-only] [--mesh A124,A127]"""
import io
import json
import os
import sys
from contextlib import redirect_stdout

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gear_palette import NATIVE_CLANS  # noqa: E402
from vary_npc_outfits import POOL  # noqa: E402

PROJ = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project")
TEX = os.path.join(PROJ, "resource", "native_tailoring", "tex")
MESHES = ("A100",) + tuple(POOL)
VARIANTS = 4
# Four everyday dyes per region (all a step below samurai colours). The generic robe is painted almost wholly in the
# brown roles, so every role takes a regional dye: one person's main dye, the next one's as the second.
REGIONS = {
    "crab": ((84, 98, 116), (52, 62, 92), (104, 104, 100), (92, 70, 52)),          # slate, indigo, iron, bark
    "crane": ((122, 148, 170), (88, 110, 140), (176, 172, 160), (110, 150, 180)),   # grey-blue, indigo, bleached, sky
    "lion": ((166, 124, 54), (128, 76, 40), (182, 150, 72), (150, 118, 80)),        # ochre, rust, mustard, tan
    "phoenix": ((176, 94, 52), (196, 140, 64), (132, 64, 40), (150, 104, 76)),      # persimmon, saffron, rust, clay
    "scorpion": ((118, 42, 46), (60, 50, 54), (140, 70, 60), (86, 46, 62)),         # maroon, charcoal, brick, plum
    "dragon": ((90, 112, 66), (110, 104, 58), (60, 84, 60), (130, 138, 96)),        # moss, olive, pine, lichen
    "unicorn": ((112, 76, 116), (140, 104, 70), (130, 116, 140), (80, 58, 96)),     # plum, horse-tan, heather, violet
    "mantis": ((56, 114, 108), (78, 128, 104), (176, 156, 112), (40, 76, 84)),      # teal, sea green, sand, deep sea
}
UNDYED = (150, 128, 96)                                                            # hemp


def mix(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def value(rgb, f):
    return tuple(min(255, c * f) for c in rgb)


def rich(rgb, f=.82, sat=1.25):
    """A step deeper and more saturated: the town lighting washes cloth out (user 2026-11-21: no pastels)."""
    grey = sum(rgb) / 3
    return tuple(max(0, min(255, (grey + (c - grey) * sat) * f)) for c in rgb)


def person(main, second):
    """(top, lower, accent, armor, lace) for a robe in `main` with `second` worked in."""
    main, second = rich(main), rich(second)
    return (main, value(second, .85), mix(main, UNDYED, .35), value(main, .82), second)


def variants(dyes):
    return [person(dyes[k], dyes[(k + 1) % len(dyes)]) for k in range(len(dyes))]


def ronin_variants(pal):
    """Wanderers: their own greens and browns, swapped about and faded."""
    top, lower, accent, armor, lace = pal
    return [pal, (lower, top, accent, armor, lace), tuple(value(mix(c, UNDYED, .45), 1.08) for c in pal),
            (value(mix(top, accent, .3), .85), value(lower, .9), accent, armor, lace)]


def dye(rgb, source, target):
    """blender/generated_wardrobe.dyes for one target palette, from a texture already dyed with `source`."""
    anchors = np.asarray(source, float) / 255
    normalized = rgb / np.maximum(.05, rgb.max(axis=2, keepdims=True))
    comparison = anchors / np.maximum(.05, anchors.max(axis=1, keepdims=True))
    hue = ((normalized[:, :, None] - comparison[None, None]) ** 2).sum(axis=3)
    power = (rgb.max(axis=2)[:, :, None] - anchors.max(axis=1)) ** 2
    weight = np.exp(-12 * hue - 4 * power)
    weight /= np.maximum(1e-6, weight.sum(axis=2, keepdims=True))
    original = weight @ anchors
    shade = np.clip(rgb.max(axis=2) / np.maximum(.055, original.max(axis=2)), .22, 1.49)
    out = (weight @ (np.asarray(target, float) / 255)) * shade[:, :, None]
    return (np.clip(out, 0, 1) * 255 + .5).astype(np.uint8)


def textures(meshes=MESHES):
    n = 0
    for mesh in meshes:
        for clan in ("peasant", "eta", "ronin"):
            rgb = np.asarray(Image.open(os.path.join(TEX, clan, mesh + ".png")).convert("RGB"), float) / 255
            source = NATIVE_CLANS[clan]
            if clan == "ronin":                                  # wanderers: their own greens and browns, varied
                jobs = {"any": ronin_variants(source)}
            elif clan == "eta":                                  # muted: the region shows through grey and brown
                jobs = {r: [tuple(mix(c, e, .6) for c, e in zip(variants(d)[0], NATIVE_CLANS["eta"]))]
                        for r, d in REGIONS.items()}
            else:
                jobs = {r: variants(p) for r, p in REGIONS.items()}
            for region, pals in jobs.items():
                for k, pal in enumerate(pals):
                    Image.fromarray(dye(rgb, source, pal)).save(
                        os.path.join(TEX, clan, "%s_%s_%d.png" % (mesh, region, k)), optimize=True)
                    n += 1
    print("commoner dyes: %d textures (%s)" % (n, ", ".join(meshes)))


def regions():
    """map -> region: a town's own clan (gen_maps TOWN_WARDS / ISLAND_WARDS), names that say whose land it is, else
    the road it is on; interiors follow their town."""
    import gen_maps as gm
    mp = json.load(open(os.path.join(PROJ, "data", "map.json"), encoding="utf-8"))
    with redirect_stdout(io.StringIO()):
        gm.marker_pass(mp)
    road = {"P100": "crab", "P101": "crane", "P102": "mantis", "P103": "lion", "P104": "phoenix", "P105": "scorpion",
            "P106": "unicorn", "P107": None}
    clan = {"Crab": "crab", "Crane": "crane", "Lion": "lion", "Phoenix": "phoenix", "Dragon": "dragon",
            "Scorpion": "scorpion", "Unicorn": "unicorn", "Mantis": "mantis", "Tortoise": "mantis", "Ronin": None}
    names = [("Shadowlands", "crab"), ("Kaiu", "crab"), ("Hida", "crab"), ("Hiruma", "crab"), ("Yasuki", "crab"),
             ("Doji", "crane"), ("Kakita", "crane"), ("Daidoji", "crane"), ("Akodo", "lion"), ("Kitsu", "lion"),
             ("Isawa", "phoenix"), ("Kamatori", "phoenix"), ("Bayushi", "scorpion"), ("Kamen no Toshi", "scorpion"),
             ("Soshi", "scorpion"), ("Kitsuki", "dragon"), ("Togashi", "dragon"), ("Mirumoto", "dragon"),
             ("Dragon", "dragon"), ("Shioden", "dragon"), ("Tamori", "dragon"), ("Iuchi", "unicorn"),
             ("Yotomo", "unicorn"), ("Ide", "unicorn"), ("Buried Leaves", "unicorn"), ("Perfume Petal", "unicorn"),
             ("Silk", "mantis"), ("Gusai", "mantis"), ("Mantis", "mantis"), ("Tortoise", "mantis")]
    out = {}
    for mid, m in mp.items():
        if not ("M100" <= mid < "M800"):
            continue
        name = m.get("name", "")
        hit = next((r for word, r in names if word in name), None)
        r = hit or road.get(gm.MAP_PATH.get(mid))
        if r:
            out[mid] = r
    for reg in gm.TOWN_WARDS + gm.ISLAND_WARDS:
        r = clan.get(reg["clan"])
        for mid in (*reg["sources"], reg["mid"], reg.get("room")):
            if mid and r:
                out[mid] = r
            elif mid:
                out.pop(mid, None)
    for room, parent in gm.AUTO_INTERIOR_PARENT.items():
        if parent in out:
            out[room] = out[parent]
    for room, (parent, _door) in getattr(gm, "INTERIOR_PARENT", {}).items():
        if parent in out:
            out[room] = out[parent]
    path = os.path.join(PROJ, "plugin", "rokugan", "RokuganCommonerDyes.sk")
    rows = ", ".join("%s = \"%s\"" % kv for kv in sorted(out.items()))
    body = ("// Generated by tools/gen_commoner_dyes.py: the region of Rokugan each map lies in (commoners' everyday dyes).\n"
            "::Rokugan.DYE_REGION <- { %s };\n" % rows +
            "::Rokugan.DYE_MESHES <- { %s };\n" % ", ".join("%s = true" % m for m in MESHES))
    with open(path, "w", encoding="utf-8") as f:
        f.write(body + RUNTIME)
    print("commoner dyes: %d maps in %d regions" % (len(out), len(set(out.values()))))


RUNTIME = r"""
//	Townsfolk in the generic Travelling Clothes (A100) or the other plain robes (DYE_MESHES) dyed peasant / eta / ronin:
//	the dye of the region the map lies in, one of four looks per region picked from the person's key (the same person
//	always looks the same there). RokuganNativeChara addTailoredPart asks commonerDye for the texture name (null = the
//	clan's own dye).
::Rokugan.DYE_VARIANTS <- { peasant = 4, eta = 1, ronin = 4 };
::Rokugan.dyeKey <- null;
::Rokugan.commonerDye <- function( record, clan){
	try{
		if( !record || !record["dyed"] || !(record.mesh in this.DYE_MESHES) || record["palette"] || !(clan in this.DYE_VARIANTS))
			return null;
		local key = this.dyeKey || "", mid = ::rpgstage ? ::rpgstage["mapid"] : null;
		local region = clan == "ronin" ? "any" : (mid && (mid in this.DYE_REGION) ? this.DYE_REGION[mid] : null);
		if( !region) return null;
		local h = 0;
		foreach( c in key) h = (h * 31 + c) & 0x7fffffff;
		local pick = record.mesh .. "_" .. region .. "_" .. (h % this.DYE_VARIANTS[clan]);
		return ::getResource( "/resource/native_tailoring/tex/" .. clan .. "/" .. pick .. ".png") ? pick : null;
	}catch( ex){ printexception( ex); }
	return null;
};
//	whose robe: the key the native picture is made for (the same name RokuganNativeChara reads from pic3d)
::Rokugan._rt_create_dye <- ::Rokugan.createNativeChara;
::Rokugan.createNativeChara <- function( v, player=null){
	local key = null;
	try{
		local pc = v["mdl"];
		if( !pc && v["mdlid"]) pc = ::rpgres[v.mdlid];
		local path = pc ? pc["pic3d"] : null;
		if( path){
			local parts = path.split( "/"), file = parts[length( parts) - 1];
			key = file.slice( 0, file.len() - 4).split( "__")[0];
		}
	}catch( ex){}
	::Rokugan.dyeKey = key;
	local r = ::Rokugan._rt_create_dye( v, player);
	::Rokugan.dyeKey = null;
	return r;
};
"""


if __name__ == "__main__":
    if "--maps-only" not in sys.argv:
        only = sys.argv[sys.argv.index("--mesh") + 1].split(",") if "--mesh" in sys.argv else MESHES
        textures(tuple(only))
    regions()
