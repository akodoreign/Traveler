"""Collect the bulk bust queue (tools/queue_busts.py) once ComfyUI has worked through it, for review.
python -E tools/collect_busts.py [--partial]
For every job in _art/preview/agents/busts/queue.json that has finished (ComfyUI /history): download the image into
_art/busts/<key>/review/ (cand_s<seed>.png for NPCs; var_<look>_s<seed>.png for traveler looks, composited onto the
approved base so only the masked area changes, like gen_busts.py variants), then contact sheets:
_art/preview/agents/busts/review_npc_<NN>.png (5 speakers per sheet, crab path first, candidates side by side) and
review_variants.png. Unfinished jobs are listed; rerun later. Nothing is wired into the game here.
To use a pick: NPCs from gen_busts.CHARS -> NPC_PICK; others: copy the candidate to _art/busts/<key>/approved_base.png,
add a CHARS entry (names, prompt, base_file="approved_base.png", variants=[], npc=True), then `gen_busts.py npc <key>`.
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv, sys.argv = sys.argv, [sys.argv[0]]
import gen_busts as g  # noqa: E402
sys.argv = _argv

from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

QJS = os.path.join(g.PREVIEW, "queue.json")


def fetch(pid):
    h = json.loads(g._req("/history/" + pid))
    if pid not in h:
        return None
    for node in h[pid]["outputs"].values():
        for im in node.get("images", []):
            q = "/view?filename=%s&subfolder=%s&type=%s" % (im["filename"], im["subfolder"], im["type"])
            return Image.open(io.BytesIO(g._req(q))).convert("RGB")
    return None


def main():
    jobs = json.load(open(QJS, encoding="utf-8"))
    waiting, got = [], 0
    for j in jobs:
        rd = os.path.join(g.WORK, j["key"], "review")
        os.makedirs(rd, exist_ok=True)
        name = ("var_%s_s%d.png" % (j["variant"], j["seed"])) if j["kind"] == "variant" else "cand_s%d.png" % j["seed"]
        out = os.path.join(rd, name)
        j["file"] = out
        if os.path.exists(out):
            continue
        im = fetch(j.get("prompt_id", "")) if j.get("prompt_id") else None
        if im is None:
            waiting.append(j)
            continue
        if j["kind"] == "variant":
            c = g.CHARS[j["key"]]
            base = g.base_image(j["key"])
            m = g.variant_mask(c, base, j["regions"]).filter(ImageFilter.GaussianBlur(6))
            im = Image.composite(im.resize(base.size, Image.LANCZOS), base, m)
        g.save_png(im, out)
        got += 1
    print("downloaded %d, still waiting %d" % (got, len(waiting)))
    # sheets
    npcs, seen = [], {}
    for j in jobs:
        if j["kind"] == "npc" and os.path.exists(j["file"]):
            seen.setdefault(j["key"], []).append(j)
    for key, js in seen.items():
        npcs.append((js[0].get("name", key), [Image.open(x["file"]) for x in js], [x["seed"] for x in js]))
    tw, th = 200, 292
    for n0 in range(0, len(npcs), 5):
        chunk = npcs[n0:n0 + 5]
        sh = Image.new("RGB", (tw * 3 + 260, (th + 8) * len(chunk)), (40, 36, 44))
        d = ImageDraw.Draw(sh)
        f = g.label_font(18)
        for r, (name, ims, seeds) in enumerate(chunk):
            y = r * (th + 8)
            d.text((8, y + 8), name, fill=(240, 230, 200), font=f)
            for i, (im, s) in enumerate(zip(ims, seeds)):
                sh.paste(im.resize((tw, th)), (260 + i * tw, y))
                d.text((264 + i * tw, y + th - 22), "seed %d" % s, fill=(255, 255, 0), font=f)
        g.save_png(sh, os.path.join(g.PREVIEW, "review_npc_%03d.png" % (n0 // 5 + 1)))
    vs = [j for j in jobs if j["kind"] == "variant" and os.path.exists(j["file"])]
    if vs:
        g.sheet([Image.open(j["file"]) for j in vs], ["%s %s s%d" % (j["key"], j["variant"], j["seed"]) for j in vs],
                os.path.join(g.PREVIEW, "review_variants.png"), cols=6, tw=220)
    print("sheets in", g.PREVIEW)


if __name__ == "__main__":
    main()
