"""One-off sample for the upright guide poses: Natsuko and Rensei idle (8 frames each) through the approved pipeline
(gen_pixeldrive specs/palette), written to _art/preview/agents/pixelai/upright/, with a before/after at 6x.
Rows of the strip: old rig, new rig, old AI (the superseded frames, where they exist), new AI.
python -E tools/upright_sample.py [--strips-only]"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv, sys.argv = sys.argv, [sys.argv[0]]
import gen_pixeldrive as d  # noqa: E402
sys.argv = _argv
from PIL import Image, ImageDraw  # noqa: E402

ps, g = d.ps, d.g
OUT = os.path.join(ps.PX, "upright")
FW, FH = ps.FW, ps.FH
KEYS = ["natsuko", "rensei"]
N = 8


def old_rig(sheet, i):
    im = Image.open(os.path.join(ps.RES, sheet)).convert("RGBA")
    return im.crop(((i % ps.COLS) * FW, (i // ps.COLS) * FH, (i % ps.COLS) * FW + FW, (i // ps.COLS) * FH + FH))


def main():
    os.makedirs(OUT, exist_ok=True)
    for k in KEYS:
        sp = json.load(open(os.path.join(d.SPECS, "%s.json" % k)))
        od = os.path.join(OUT, k)
        os.makedirs(od, exist_ok=True)
        if "--strips-only" not in sys.argv:
            d.chain(sp, d.Pal(sp), os.path.join(ps.RES, sp["sheet"]), tuple(range(N)), "stand", od)
        rows = {"old rig": [old_rig(sp["sheet"], i) for i in range(N)],
                "new rig": [ps.frame(sp["sheet"], i) for i in range(N)]}
        sup = os.path.join(d.SHEETS, k, "superseded_lean")
        rows["old AI"] = [Image.open(os.path.join(sup, "f%03d.png" % i)).convert("RGBA")
                          if os.path.exists(os.path.join(sup, "f%03d.png" % i)) else None for i in range(N)]
        rows["new AI"] = [Image.open(os.path.join(od, "f%03d.png" % i)).convert("RGBA") for i in range(N)]
        S = 6
        sh = Image.new("RGB", (FW * S * N, FH * S * 4), (30, 28, 34))
        dr = ImageDraw.Draw(sh)
        f = g.label_font(22)
        for y, (lb, fr) in enumerate(rows.items()):
            for x, im in enumerate(fr):
                if im is not None:
                    sh.paste(ps.on_bg(im, S), (x * FW * S, y * FH * S))
            dr.text((8, y * FH * S + 6), "%s: %s" % (k, lb), fill=(255, 255, 0), font=f)
        sh.save(os.path.join(OUT, "%s_before_after.png" % k))
        gif = []
        for i in range(N):
            c = Image.new("RGB", (FW * S * 2 + 12, FH * S), (30, 28, 34))
            old = rows["old AI"][i] if rows["old AI"][i] is not None else rows["old rig"][i]
            c.paste(ps.on_bg(old, S), (0, 0))
            c.paste(ps.on_bg(rows["new AI"][i], S), (FW * S + 12, 0))
            gif.append(c)
        gif[0].save(os.path.join(OUT, "%s_before_after.gif" % k), save_all=True, append_images=gif[1:], duration=130,
                    loop=0)
    print("samples in", OUT)


if __name__ == "__main__":
    main()
