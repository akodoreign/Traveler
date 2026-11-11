"""Where can a player level before the next chapter? (user 2026-11-11: "I found it extremely difficult to move on to
the Hida road as my level was to low and didn't have a place to level. this may be true in other areas paths as
well.")  For each path the test player has run (_art/preview/bot/story_N/play.txt): the maps each chapter visits,
the random-encounter foe levels there (map.json + enemy.json; flagged groups counted too), and the next chapter's
recommended level from its chapter card.  python -E tools/level_gaps.py
"""
import json
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.path.join(ROOT, "_tools", "rpgcobo-tool", "project", "data")
BOT = os.path.join(ROOT, "_art", "preview", "bot")


def main():
    mp = json.load(open(os.path.join(DATA, "map.json"), encoding="utf-8"))
    en = json.load(open(os.path.join(DATA, "enemy.json"), encoding="utf-8"))

    def foe_levels(mid):
        lv = [en[f["id"]]["LV"] for g in (mp.get(mid, {}).get("encount") or []) if g.get("rate")
              for f in g.get("enemies") or [] if f.get("id") in en]
        return (min(lv), max(lv)) if lv else None

    for n in range(8):
        p = os.path.join(BOT, "story_%d" % n, "play.txt")
        if not os.path.exists(p):
            continue
        chap, rec, maps = 0, {}, {}
        name = None
        for line in open(p, encoding="utf-8", errors="replace"):
            m = re.match(r"== (\w+) path", line)
            if m:
                name = m.group(1)
            m = re.search(r"RESUMED at leg \d+ \(M\d+ [\d,]+, chapter (\d+)\)", line)
            if m:
                chap = int(m.group(1))
            m = re.search(r"CHAPTER (\d+) - .*Recommended level (\d+)", line)
            if m:
                chap = int(m.group(1))
                rec[chap] = int(m.group(2))
            m = re.match(r"\s+\d+ (M\d+)\s", line)
            if m:
                maps.setdefault(chap, set()).add(m.group(1))
        print("== %s (story_%d)" % (name, n))
        for c in sorted(maps):
            lvls = [(mid, foe_levels(mid)) for mid in sorted(maps[c])]
            lvls = [(mid, l) for mid, l in lvls if l]
            top = max((l[1] for _, l in lvls), default=0)
            nxt = rec.get(c + 1)
            gap = (nxt - top) if (nxt and top) else None
            flag = "  <-- GAP %d" % gap if gap is not None and gap > 3 else ""
            print("  ch%d rec %s: foes up to Lv %s on %s; next chapter rec %s%s" % (
                c, rec.get(c, "?"), top or "-", ", ".join("%s %d-%d" % (mid, l[0], l[1]) for mid, l in lvls) or "no battles",
                nxt or "-", flag))


if __name__ == "__main__":
    main()
