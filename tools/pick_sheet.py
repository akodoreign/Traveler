"""Candidate sheets for the speakers that have no bust in the game yet (from the bulk queue's review/ folders).
python -E tools/pick_sheet.py [--all]       -> _art/preview/agents/busts/pick_NN.png + pick_index.json
Rows are numbered; candidates 1..n left to right. Then: python -E tools/pick_sheet.py --apply "3:2,5:1,7:x"
(row:candidate; x = reject, requeue with tools/queue_busts.py --only "<name>") writes _art/busts/npc_picks.json.
Default: only the redo-queue candidates (seed > 1000: the improved prompts); --all adds the first queue's."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv, sys.argv = sys.argv, [sys.argv[0]]
import gen_busts as g  # noqa: E402
sys.argv = _argv
from PIL import Image, ImageDraw  # noqa: E402

IDX = os.path.join(g.PREVIEW, "pick_index.json")
PICKS = os.path.join(g.WORK, "npc_picks.json")


def build(all_=False):
    jobs = json.load(open(os.path.join(g.PREVIEW, "queue.json"), encoding="utf-8"))
    res = os.path.join(g.PROJ, "resource", "bust")
    have = set(os.listdir(res))
    by, order = {}, []
    for j in jobs:
        if j["kind"] != "npc" or j["key"] in have or (j["seed"] <= 1000 and not all_):
            continue
        fp = os.path.join(g.WORK, j["key"], "review", "cand_s%d.png" % j["seed"])
        if not os.path.exists(fp):
            continue
        if j["key"] not in by:
            by[j["key"]] = [j["name"], []]
            order.append(j["key"])
        by[j["key"]][1].append([j["seed"], fp])
    rows = [[k, by[k][0], by[k][1][-3:]] for k in order]     # the newest candidates (latest prompts)
    json.dump(rows, open(IDX, "w", encoding="utf-8"), indent=0)
    f = g.label_font(15)
    TW, TH, per = 110, 160, 16
    for old in [x for x in os.listdir(g.PREVIEW) if x.startswith("pick_") and x.endswith(".png")]:
        os.remove(os.path.join(g.PREVIEW, old))
    for n0 in range(0, len(rows), per):
        ch = rows[n0:n0 + per]
        sh = Image.new("RGB", (2 * (130 + 3 * TW), 8 * (TH + 4)), (40, 36, 44))
        d = ImageDraw.Draw(sh)
        for r, (k, nm, cl) in enumerate(ch):
            x0, y = (r // 8) * (130 + 3 * TW), (r % 8) * (TH + 4)
            d.text((x0 + 4, y + 4), "%d" % (n0 + r), fill=(255, 255, 0), font=f)
            ln = [""]
            for w in nm.split():
                if len(ln[-1]) + len(w) > 14:
                    ln.append("")
                ln[-1] += w + " "
            for i, l in enumerate(ln):
                d.text((x0 + 4, y + 24 + i * 17), l, fill=(240, 230, 200), font=f)
            for i, (s, fp) in enumerate(cl[:3]):
                sh.paste(Image.open(fp).convert("RGB").resize((TW, TH)), (x0 + 130 + i * TW, y))
                d.text((x0 + 132 + i * TW, y + TH - 18), str(i + 1), fill=(255, 0, 0), font=f)
        sh.save(os.path.join(g.PREVIEW, "pick_%02d.png" % (n0 // per)))
    print("%d speakers with candidates, %d sheets" % (len(rows), (len(rows) + per - 1) // per))


def apply(spec):
    rows = json.load(open(IDX, encoding="utf-8"))
    d = json.load(open(PICKS, encoding="utf-8")) if os.path.exists(PICKS) else {}
    rej = []
    for part in spec.split(","):
        if not part.strip():
            continue
        r, c = part.split(":")
        k, nm, cl = rows[int(r)]
        if c.strip().lower() == "x":
            rej.append(nm)
            continue
        seed = cl[int(c) - 1][0]
        d[k] = {"names": [nm], "file": "review/cand_s%d.png" % seed, "note": "picked via pick_sheet.py"}
        print("pick", k, nm, seed)
    json.dump(d, open(PICKS, "w", encoding="utf-8"), indent=1)
    if rej:
        print("REJECTED (requeue): " + ",".join(rej))


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--apply" in a:
        apply(a[a.index("--apply") + 1])
    else:
        build("--all" in a)
