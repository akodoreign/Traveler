"""Fast-travel posts in clan colours (user 2026-11-22: "all of them should get their own colored boxes (based on clans)").
Copies the Crab road-map post (map_vox exterior #10, post1: an orange box with a grey leg and mark) to exterior #60-#66, one per
road, with its palette overrides (pal0: index, 0xMMBBGGRR with the material byte MM kept) dyed: the box in the
clan's main colour, the leg and mark in its accent. gen_maps.TRAVEL_POST names the block each road's posts use.
python -E tools/gen_travel_posts.py   (idempotent)"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gear_palette import NATIVE_CLANS  # noqa: E402

PROJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_tools", "rpgcobo-tool", "project")
POSTS = {60: "crane", 61: "dragon", 62: "lion", 63: "phoenix", 64: "scorpion", 65: "unicorn", 66: "ronin"}
BODY = {11, 12, 13, 15, 17, 18, 19}             # greys (46 .. 165): the leg and the mark on the box
BOX = {169, 170, 171, 172}                      # the box (Crab's orange, dark .. bright; engine-checked 2026-11-22)


def word(flags, rgb):
    r, g, b = (max(0, min(255, int(round(c)))) for c in rgb)
    return (flags << 24) | (b << 16) | (g << 8) | r                       # (the engine reads the low byte as red)


def dyed(src, clan):
    top, lower, accent, armor, lace = NATIVE_CLANS[clan]
    out = copy.deepcopy(src)
    pal = out["pal0"]
    boxes = sorted(i for i in pal[::2] if i in BOX)
    for k in range(0, len(pal), 2):
        idx, w = pal[k], pal[k + 1]
        flags, grey = w >> 24, w & 255
        if idx in BODY:                                                     # the leg and the painted mark
            pal[k + 1] = word(flags, [c * (0.45 + grey / 165.0 * 0.85) for c in accent])
        elif idx in BOX:                                                    # the box itself: the clan colour
            f = 0.75 + 0.5 * boxes.index(idx) / max(1, len(boxes) - 1)
            pal[k + 1] = word(flags, [c * f for c in top])
    return out


def main():
    path = os.path.join(PROJ, "resource", "map_vox.json")
    data = json.load(open(path, encoding="utf-8"))
    ext = data["exterior"]
    src = ext["#10#"]
    for n, clan in POSTS.items():
        ext["#%d#" % n] = dyed(src, clan)
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")
    print("travel posts: exterior %s" % ", ".join("#%d %s" % kv for kv in POSTS.items()))


if __name__ == "__main__":
    main()
