"""Events standing in the air or sunk in the ground (user 2026-11-12: "this guy im supposed to talk to but hes in the
air. saw a chest in the air in the nezumi caves as well"). Builds each map's spec (no voxel build) and compares every
villager / custom NPC / chest's y with the ground under it (m.hgt). python -E tools/float_check.py [map ids]"""
import sys

import gen_maps as g


def main():
    ids = sys.argv[1:] or [k for k in g.MAPS if k not in g.DEBUG_MAPS and "M100" <= k < "M800"]
    bad = []
    for mid in ids:
        try:
            m, ev = g.make(mid)
        except Exception as ex:                                  # noqa: BLE001
            print("skip", mid, ex)
            continue
        if ev is None:
            continue
        for key, e in ev.ev.items():
            role = e.get("role")
            if role not in ("villager", "custom", "itemchest", "clerk", "hotel") or "pos" not in e:
                continue
            if role == "custom" and e.get("mdlid") == "CE000":
                continue                                         # invisible triggers
            x, y, z = int(e["pos"][0]), int(e["pos"][1]), int(e["pos"][2])
            if not (0 <= x < m.w and 0 <= z < m.d):
                bad.append((mid, key, role, e.get("mdlid"), x, y, z, "off map"))
                continue
            ground = int(m.hgt[z, x]) + 1
            if abs(y - ground) >= 2:
                bad.append((mid, key, role, e.get("mdlid") or e.get("itemid"), x, y, z, "y %d vs ground %d" % (y, ground)))
    for b in bad:
        print(*b)
    print("floating / sunk events: %d" % len(bad))


if __name__ == "__main__":
    main()
