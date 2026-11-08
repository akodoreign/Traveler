"""AI sprite animations v2: fixed palette + temporal consistency (user feedback 2026-11-08: "way too red", "do more
frames to eliminate flicker"). Same s11 style and rig guidance as gen_pixelsheet.py, but frame by frame:
  1. init image = the previous CHOSEN AI frame (x12), with the regions where our rig's frame changed (vs. the rig's
     previous frame, grown) replaced by our current rig frame -> the look carries over, the new pose comes from the rig;
     ControlNet union canny of our current rig frame; lower denoise (0.55) when there is a previous frame.
  2. N candidates (seeds) per frame; each is post-processed (key out, x12 box downscale to 80x68, alpha clipped to our
     silhouette, quantized to the character's FIXED palette with red only where our rig frame has its red accent).
  3. the candidate closest to the previous chosen frame is kept (palette-index difference on the overlap).
  4. temporal pass: pixels where our rig frame did not change keep the previous chosen frame's pixel exactly.
python -E tools/gen_pixelanim.py natsuko [stand,atk_thrust] [--n 3]
Output: _art/preview/agents/pixelai/anim2/<key>/<anim>_NN.png, <key>_<anim>.gif (ours | AI, 6x), sheet strips.
"""
import io
import json
import os
import sys
import time

import cv2
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv, sys.argv = sys.argv, [sys.argv[0]]
import gen_pixelsheet as ps  # noqa: E402
g = ps.g
gp = ps.gp
sys.argv = _argv

OUT = os.path.join(ps.PX, "anim2")
FW, FH, K = ps.FW, ps.FH, ps.K

# Fixed palettes (RGB). "accent" colours may only appear where our rig frame has its accent (headband, cords).
PAL = {
    "natsuko": {
        "base": [(20, 18, 26), (38, 36, 48),                                   # outlines
                 (46, 54, 70), (64, 76, 96), (88, 102, 124), (118, 132, 154), (160, 172, 190),   # slate armour
                 (48, 54, 72), (66, 84, 116), (92, 110, 142),                    # slate-blue cloth
                 (28, 22, 26), (52, 42, 46), (80, 66, 68),                       # dark hair
                 (118, 66, 40), (166, 98, 56), (212, 138, 78), (240, 172, 108),  # warm darker skin (bust cand_28)
                 (42, 32, 30), (68, 52, 42),                                     # lacquered spear shaft
                 (150, 160, 176), (206, 214, 226), (248, 248, 252),              # steel, highlights
                 (210, 200, 170)],                                               # pale cord / tabi
        "accent": [(150, 38, 34), (196, 54, 44)],                                # headband, a few cords
    },
}
PROMPT_FIX = {
    "natsuko": ("1girl, young woman samurai scout, (brown skin, dark-skinned female:1.2), (black hair, dark brown "
                "hair:1.2), long ponytail, red headband, (blue-grey lacquered samurai armor, slate gray armor:1.4), "
                "lamellar do, sode shoulder plates, kote, suneate, slate-blue kimono, (black lacquered wooden yari "
                "spear with a steel blade:1.2), feudal japan",
                ", red armor, red clothes, red hair, orange hair, red skin, red spear, red outline, pink"),
}


def lab(c):
    a = np.array(c, np.uint8).reshape(-1, 1, 3)
    return cv2.cvtColor(a, cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(np.float32)


def accent_mask(rig):
    """Where our rig frame is red (the headband, lacing), grown 1 px."""
    a = np.asarray(rig).astype(int)
    r, gg, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    m = (al > 0) & (r > 120) & (r > gg + 50) & (r > b + 50)
    return cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0


def quantize(small, rig, key):
    """small: 80x68 RGBA (AI, after key-out + downscale). Nearest palette colour in Lab; accent colours only inside
    the rig's accent mask. Alpha: AI alpha AND our silhouette grown 2 px."""
    pal = PAL[key]
    base, acc = pal["base"], pal["accent"]
    allc = np.array(base + acc, np.uint8)
    L = lab(allc)
    nb = len(base)
    a = np.asarray(small).copy()
    px = lab(a[..., :3].reshape(-1, 3))
    d = ((px[:, None, :] - L[None, :, :]) ** 2).sum(2)
    am = accent_mask(rig).reshape(-1)
    d[~am, nb:] = 1e9                                     # no red outside the accent area
    idx = d.argmin(1).reshape(FH, FW)
    sil = cv2.dilate((np.asarray(rig.getchannel("A")) > 0).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    alpha = (a[..., 3] > 110) & sil
    out = np.dstack([allc[idx], (alpha * 255).astype(np.uint8)])
    return Image.fromarray(out, "RGBA"), np.where(alpha, idx, -1)


def changed(rig_prev, rig_cur, grow=2):
    """Pixels where the rig frame changed (colour or alpha), grown."""
    if rig_prev is None:
        return np.ones((FH, FW), bool)
    a, b = np.asarray(rig_prev).astype(int), np.asarray(rig_cur).astype(int)
    m = (np.abs(a - b).sum(2) > 0)
    return cv2.dilate(m.astype(np.uint8), np.ones((2 * grow + 1, 2 * grow + 1), np.uint8)) > 0


def up(im):
    return im.resize((FW * K, FH * K), Image.NEAREST)


def init_image(rig_cur, rig_prev, prev_ai):
    """x12 init: the previous chosen AI frame, with the changed regions taken from our current rig frame."""
    bg = Image.new("RGBA", rig_cur.size, (255, 255, 255, 255))
    bg.alpha_composite(rig_cur)
    rig_rgb = bg.convert("RGB")
    if prev_ai is None:
        return up(rig_rgb).filter(ImageFilter.GaussianBlur(3))
    pb = Image.new("RGBA", prev_ai.size, (255, 255, 255, 255))
    pb.alpha_composite(prev_ai)
    m = Image.fromarray((changed(rig_prev, rig_cur) * 255).astype(np.uint8))
    mix = Image.composite(rig_rgb, pb.convert("RGB"), m)
    return up(mix).filter(ImageFilter.GaussianBlur(2))


def control(rig_cur):
    bg = Image.new("RGBA", rig_cur.size, (255, 255, 255, 255))
    bg.alpha_composite(rig_cur)
    big = up(bg.convert("RGB"))
    e = cv2.Canny(np.asarray(big.filter(ImageFilter.GaussianBlur(1.5)).convert("L")), 40, 120)
    return Image.fromarray(e).convert("RGB")


def run_frame(key, aid, rig_cur, rig_prev, prev_ai, prev_idx, n, seed0):
    init = init_image(rig_cur, rig_prev, prev_ai)
    ctrl = control(rig_cur)
    iname = g.upload(init, "rt_pa_%s_i.png" % key)
    cname = g.upload(ctrl, "rt_pa_%s_c.png" % key)
    desc, negx = PROMPT_FIX.get(key, (ps.DESC[key], ""))
    ps.DESC[key] = desc
    pos = ps.prompt_for(key, aid)
    neg = gp.NEG + gp.EXTRA_NEG.get(key, "") + negx
    den = 0.72 if prev_ai is None else 0.55
    pids = []
    for s in range(n):
        w = ps.wf(pos, neg, seed0 + s, iname, cname)
        w["11"]["inputs"]["denoise"] = den
        r = json.loads(g._req("/prompt", json.dumps({"prompt": w, "client_id": "rt_pixelanim",
                                                       "front": True}).encode()))
        pids.append(r["prompt_id"])
    cands = []
    for pid in pids:
        while True:
            im = ps.fetch(pid)
            if im is not None:
                break
            time.sleep(0.5)
        rgba = g.key_out(im.resize((FW * K, FH * K)), holes=True)
        small = rgba.resize((FW, FH), Image.BOX)
        q, idx = quantize(small, rig_cur, key)
        cands.append((q, idx))
    if prev_idx is None:
        # first frame: the candidate with the least colour noise (fewest isolated pixels)
        def noise(c):
            i = c[1]
            return int((i != np.roll(i, 1, 0)).sum() + (i != np.roll(i, 1, 1)).sum())
        best = min(cands, key=noise)
    else:
        def diff(c):
            i = c[1]
            both = (i >= 0) | (prev_idx >= 0)
            return int(((i != prev_idx) & both).sum())
        best = min(cands, key=diff)
    q, idx = best
    if prev_ai is not None:                               # temporal pass: unchanged rig pixels stay identical
        keep = ~changed(rig_prev, rig_cur, grow=1)
        qa, pa = np.asarray(q).copy(), np.asarray(prev_ai)
        qa[keep] = pa[keep]
        idx = np.where(keep, prev_idx, idx)
        q = Image.fromarray(qa, "RGBA")
    return q, idx


def anims(key, names, n):
    am = {a["id"]: a for a in ps.animap(ps.SHEET[key])}
    od = os.path.join(OUT, key)
    os.makedirs(od, exist_ok=True)
    t0 = time.time()
    nf = 0
    base_ai, base_idx, base_rig = None, None, None
    for nm in names:
        a = am[nm]
        rng = list(range(a["st"], max(a["en"], a["st"] + 1)))
        prev_ai, prev_idx, rig_prev = base_ai, base_idx, base_rig   # each animation starts from the stand frame
        frames = []
        for k, i in enumerate(rng):
            rig = ps.frame(ps.SHEET[key], i)
            q, idx = run_frame(key, nm, rig, rig_prev, prev_ai, prev_idx, n, 1100 + i * 10)
            q.save(os.path.join(od, "%s_%02d.png" % (nm, k)))
            frames.append((rig, q))
            prev_ai, prev_idx, rig_prev = q, idx, rig
            nf += 1
            if base_ai is None:
                base_ai, base_idx, base_rig = q, idx, rig
        gif = []
        for rig, q in frames:
            c = Image.new("RGB", (FW * 12 + 12, FH * 6), (30, 28, 34))
            c.paste(ps.on_bg(rig, 6), (0, 0))
            c.paste(ps.on_bg(q, 6), (FW * 6 + 12, 0))
            gif.append(c)
        gif[0].save(os.path.join(OUT, "%s_%s.gif" % (key, nm)), save_all=True, append_images=gif[1:],
                    duration=int(1000 / max(1.0, a["spd"])) if nm != "stand" else 150, loop=0)
        strip = Image.new("RGB", (FW * 6 * len(frames), FH * 6))
        for k, (_, q) in enumerate(frames):
            strip.paste(ps.on_bg(q, 6), (k * FW * 6, 0))
        strip.save(os.path.join(OUT, "%s_%s_strip.png" % (key, nm)))
    print("%d frames, %.1f s per frame (%d candidates each)" % (nf, (time.time() - t0) / max(1, nf), n))


if __name__ == "__main__":
    a = sys.argv[1:]
    key = a[0]
    names = a[1].split(",") if len(a) > 1 and not a[1].startswith("--") else ["stand", "atk_thrust"]
    n = int(a[a.index("--n") + 1]) if "--n" in a else 3
    anims(key, names, n)
