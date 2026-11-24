"""Townsfolk outfits (user 2026-11-24: "change out a lot of the a100 outfit. 90% of the NPC uses it. Random for 90% of
the current users of a100 for one of the other outfits please").

The side cast's field outfit is its record in resource/native_tailoring/index.json "defaults" (RokuganNativeChara
setNative -> setTailoredOutfit; no generator writes those records, the file itself is the source). This picks, with a
fixed seed, 90% of the side cast in the generic Travelling Clothes (A100) and dresses each in one of POOL instead, spread
evenly; the other 10% keep A100. A changed record keeps its clan and gets "was": "A100", so a rerun picks the same people
again (idempotent) and the choice survives later edits elsewhere in the file.

Left alone: enemies (EP* keys: road bandits, bosses), the travelers (trav_*), anyone whose picture is a party member
(their field look must match the A100 they wear in the party: Ryoichi, Kage ch3, Kafu without his sword), fitted
aliases (a "palette" record) and everyone not in A100.

Pool: the other plain robes ordinary townsfolk already wear (stock meshes, dyed per wearer's clan / the commoner
regional dyes of tools/gen_commoner_dyes.py, which imports POOL). Left out: armour (A101-A173 plates, lamellar,
do-maru), A167 Robe of the Five Rings (Imperial priests only), A111 Shugenja's Haori (no townsperson wears it), the
fitted per-character aliases (A124_miyoshi, A135_lion_takeo, ...) and the travelers' signature costumes.

Shrine maidens (user 2026-11-24: "you have permission to use hiruma's miko outfit on any ladies near a shrine. i know its
normally locked to her, but shrine madens woudl be nice"): MIKO women wear Natsuko's miko costume (items A209 ->
trav_natsuko_miko, undyed) instead of a random draw. Rule: a woman (native_human base shared_female) of the A100 side
cast standing within 10 m of a shrine's prayer step (shrine_rites) or on a shrine's own map, whose part is the shrine
(not visitors: the widow, old women praying, the eta girl Akari, the geisha-house hostess, innkeepers, hirelings).
Hiruma Natsuko's own record is not touched.

python -E tools/vary_npc_outfits.py [--dry-run]"""
import collections
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project")
INDEX = os.path.join(PROJ, "resource", "native_tailoring", "index.json")
SEED = 20261124
KEEP = 0.10                                           # share of the A100 townsfolk left in A100
FROM = "A100"
POOL = ("A124", "A127", "A140", "A153")               # Asahina robes, Shadow Cloth, Isawa robe, Tamori ward-robe
MIKO_ITEM = "A209"                                    # Hiruma Natsuko's miko costume (trav_natsuko_miko)
MIKO = (
    "side_miko",            # "Shrine maiden": M424 Village of Floating Flowers, 5 m from the village shrine's step
    "side_shrinekeeper",    # "Shrine-keeper": sweeps the lower shrine of the Oracle's shrine town (M438); M315, M351
)


def party_keys():
    """Native keys of every party member's picture (player.json mdlid -> enemy_pic.json pic3d file name)."""
    players = json.load(open(os.path.join(PROJ, "data", "player.json"), encoding="utf-8"))
    pics = json.load(open(os.path.join(PROJ, "resource", "enemy_pic.json"), encoding="utf-8"))
    out = set()
    for pl in players.values():
        path = (pics.get(pl.get("mdlid") or "") or {}).get("pic3d") or ""
        if path:
            out.add(os.path.basename(path).rsplit(".", 1)[0].split("__")[0])
    return out


def candidates(defaults, party):
    return sorted(k for k, v in defaults.items()
                  if k.startswith("side_") and k not in party and not v.get("palette")
                  and (v.get("mesh") == FROM or v.get("was") == FROM))


def plan(defaults, party):
    """key -> item for every candidate (FROM for the kept share, MIKO_ITEM for the shrine maidens)."""
    keys = candidates(defaults, party)
    out = {k: MIKO_ITEM for k in MIKO if k in keys}
    keys = [k for k in keys if k not in out]
    rng = random.Random(SEED)
    order = list(keys)
    rng.shuffle(order)
    keep = int(round(len(order) * KEEP))
    pool = list(POOL)
    rng.shuffle(pool)
    out.update({k: FROM for k in order[:keep]})
    for i, k in enumerate(order[keep:]):
        out[k] = pool[i % len(pool)]
    return out


def main():
    dry = "--dry-run" in sys.argv
    raw = open(INDEX, "rb").read()
    data = json.loads(raw)
    items, defaults = data["items"], data["defaults"]
    gear = json.load(open(os.path.join(PROJ, "resource", "native_gear", "gear.json"), encoding="utf-8"))
    tex = os.path.join(PROJ, "resource", "native_tailoring", "tex")
    before = collections.Counter(v.get("mesh") for v in defaults.values())
    changes = plan(defaults, party_keys())
    for key, item in sorted(changes.items()):
        rec = defaults[key]
        clan = gear["palettes"].get(key) or "ronin"
        mesh = items[item]["mesh"]
        if items[item].get("dyed"):
            assert os.path.exists(os.path.join(tex, clan, mesh + ".png")), (key, clan, mesh)
        new = dict(items[item])                          # the item's own fit (mesh, dyed, decal, coverCore, showThroat)
        new["clan"] = rec.get("clan", clan)
        if item != FROM:
            new["was"] = FROM
        defaults[key] = new
    after = collections.Counter(v.get("mesh") for v in defaults.values())
    side = collections.Counter(changes.values())
    print("A100 townsfolk considered: %d; kept in A100: %d; changed: %d" % (
        len(changes), side[FROM], len(changes) - side[FROM]))
    print("new outfits: " + ", ".join("%s %d" % (m, side[m]) for m in POOL + (MIKO_ITEM,)))
    print("shrine maidens: " + ", ".join(k for k, v in sorted(changes.items()) if v == MIKO_ITEM))
    print("all defaults in A100: %d -> %d (of %d)" % (before[FROM], after[FROM], len(defaults)))
    text = (json.dumps(data, indent=2, ensure_ascii=True) + "\n").encode("utf-8")
    if dry or text == raw:
        print("index.json " + ("unchanged" if text == raw else "not written (--dry-run)"))
        return
    with open(INDEX, "wb") as f:
        f.write(text)
    print("index.json written")


if __name__ == "__main__":
    main()
