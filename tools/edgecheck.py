"""Edge-exit direction check (user, 2026-11-10: "going left you should keep going left ... or east"): every exit on a
map's edge should land on the OPPOSITE edge of the next map (leave west -> arrive on the east side).
python -E tools/edgecheck.py [MAP ...]     prints every edge exit and flags the ones that land on the wrong side."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_maps as gm  # noqa: E402

OPP = {"w": "e", "e": "w", "f": "b", "b": "f"}
NAMES = {"w": "west/left", "e": "east/right", "f": "south/front", "b": "north/back"}
_cache = {}


def built(mid):
    if mid not in _cache:
        _cache[mid] = gm.make(mid)
    return _cache[mid]


def side_of(m, bx, bz):
    """Nearest edge of map m to block bx, bz, and how far (blocks, measured inside the padding-free area)."""
    px, pb, pt = (gm.PAD_X, gm.PAD_BOTTOM, gm.PAD_TOP) if getattr(m, "exits", None) is not None or True else (0, 0, 0)
    d = {"w": bx - px, "e": (m.w - px) - bx, "f": bz - pb, "b": (m.d - pt) - bz}
    s = min(d, key=d.get)
    return s, d[s]


def moves_of(e):
    """(dest map, block x, block z) for each map move this event can make."""
    out = []
    if e.get("role") == "portal" or e.get("dest"):
        dm, de = e["dest"]["mapid"], e["dest"].get("evid")
        if e["dest"].get("pos"):
            out.append((dm, e["dest"]["pos"][0] * 2, e["dest"]["pos"][2] * 2))
            de = None
        try:
            _m2, ev2 = built(dm)
            t = ev2.ev.get("#%d#" % de) if ev2 is not None and de is not None else None
            if t:
                out.append((dm, t["pos"][0], t["pos"][2]))
        except Exception as ex:  # noqa: BLE001
            print("   (could not build", dm, ex, ")")
    for s in json.dumps(e.get("page") or []).split('"cmd_mapmove"')[1:]:
        try:
            dest = json.loads("{" + s.split('"dest": ', 1)[1].split("}", 1)[0] + "}")
        except (IndexError, ValueError):
            continue
        p = dest.get("pos")
        if p and dest.get("mapid"):
            out.append((dest["mapid"], p[0] * 2, p[2] * 2))
    return out


def main():
    ids = sys.argv[1:] or [k for k in gm.MAPS if "M100" <= k < "M800" and k not in gm.DEBUG_MAPS]
    bad = 0
    for mid in ids:
        if mid in gm.INTERIORS or mid in gm.ROOM_OFS:
            continue
        try:
            m, ev = built(mid)
        except Exception as ex:  # noqa: BLE001
            print(mid, "build failed", ex)
            continue
        for key, side in getattr(m, "edge_out", []) or []:
            e = ev.ev[key]
            for dm, bx, bz in moves_of(e):
                if dm in gm.INTERIORS or dm in gm.ROOM_OFS or dm == mid:
                    continue
                m2, _ = built(dm)
                if m2.w < 2 * gm.PAD_X + 4:
                    continue
                s2, dist = side_of(m2, bx, bz)
                ok = s2 == OPP[side] and dist <= 12
                if not ok:
                    bad += 1
                print("%s %-4s %s %s -> %s lands %s (%d from that edge)" % (
                    "  " if ok else "!!", mid, key, NAMES[side], dm, NAMES[s2], dist))
    print("-- %d exits land on the wrong side (or away from an edge)" % bad)


if __name__ == "__main__":
    main()
