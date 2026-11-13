"""Make every pose of a sprite sheet match its stand frames (user, 2026-11-11: "have comfyUI start editing the different
poses so they are closer to each other in sprite colors etc. like you did with heads ... give it reject and retry and
have it report back").

    pythonw -E tools/anim_harmonize.py run [--only side_sachiko,natsuko] [--limit N] [--palette-only] [--no-install]
    python  -E tools/anim_harmonize.py status

Per installed AI sheet (pixelai/sheets/<key>/complete), on the game sheet as it is now (after frame_fixes):
 1. Reference = the stand frames (anim "stand"). Reference palette = their colours.
 2. Palette pass (CPU): every other frame's off-palette colours go to the nearest reference colour (CIE Lab), except
    effects (bright, unsaturated: slash arcs) and small accents (off-palette blobs <= ACCENT_PX: glints).
 3. Score each frame: mean dE to the palette before mapping, "foreign" share (big off-palette regions), and a
    head / body / legs colour histogram distance to the stand frames. Facing (raw sheets face RIGHT) is flagged.
 4. Frames still over the threshold: ComfyUI img2img from the palette-mapped frame (low denoise, the sheet's spec
    prompt, canny control from the frame itself), CANDS candidates per round, up to 3 rounds (new seeds, more
    denoise). Reject a candidate if its silhouette IoU with the frame < 0.85, its head turns the other way, or its
    region score is not better. If none passes: keep the palette-only frame, flag "needs eye".
 5. Install: original sheet backed up once in _art/frame_orig/harmonize/, result written to resource/enemy_pic and
    kept in anim_harmonize/out/ (install_aisheets.py re-applies it while the AI frames are unchanged); then
    badframes.py --apply (existing fixes on top) and, every few sheets, gen_portraits.py.
 6. Report: anim_harmonize/contact/<key>.png (before above after, per animation), logs/<key>.json (per-frame scores and
    accept / reject / retry), harmonize.log, SUMMARY.md.
Watchdog (user: "teach it how to restart it when necessary"): if ComfyUI's /system_stats fails for 5 min or one
prompt runs for 20 min, the hung main.py is stopped; C:\\AI\\comfy-headless\\start-comfy.ps1 (logwrap) relaunches it.
"""
import hashlib
import json
import os
import subprocess
import sys
import threading
import time
import traceback
import urllib.request

import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv, sys.argv = sys.argv, [sys.argv[0]]
import gen_pixeldrive as pd  # noqa: E402
from atomic_io import save_png, copy_file  # noqa: E402  (atomic writes: the game may be running)
sys.argv = _argv
ps, pa, g, gp = pd.ps, pd.pa, pd.g, pd.gp

ROOT = os.path.normpath(os.path.join(HERE, ".."))
PIC = os.path.join(ROOT, "_tools", "rpgcobo-tool", "project", "resource", "enemy_pic")
EPJ = os.path.join(ROOT, "_tools", "rpgcobo-tool", "project", "resource", "enemy_pic.json")
WORK = os.path.join(ROOT, "_art", "preview", "agents", "anim_harmonize")
OUT, LOGS, CONTACT = (os.path.join(WORK, d) for d in ("out", "logs", "contact"))
BACKUP = os.path.join(ROOT, "_art", "frame_orig", "harmonize")
STATE = os.path.join(WORK, "state.json")
FW, FH, COLS = pd.FW, pd.FH, pd.COLS
K = ps.K

MAP_DE = 22.0          # off-palette colour within this dE -> mapped (drift)
ACCENT_PX = 10         # off-palette blobs this small and far from the palette are kept (glints, small props)
REGION_T = 0.42        # head/body/legs histogram distance over this -> ComfyUI pass
FOREIGN_T = 0.06       # share of pixels in big off-palette regions over this -> ComfyUI pass
IOU_MIN = 0.85
CANDS = 2
ROUNDS = ((0.28, 0), (0.34, 1), (0.40, 2))
LYING = {"die", "collapse", "seiza", "sit", "seiza_rei", "rei_full", "sleep", "kneel"}  # (all 6 tries rejected on facing)
FORCE = {}             # tools/harmonize_force.json {key: [frames]}: sent to ComfyUI whatever the score (seen by eye)
LOG = open(os.path.join(WORK, "harmonize.log"), "a", encoding="utf-8", buffering=1) if os.path.isdir(WORK) else None


def _jd(o):
    """json default: numpy scalars (bool_, float32, int64) as plain Python values."""
    return o.item() if hasattr(o, "item") else str(o)


def log(*a):
    s = time.strftime("%m-%d %H:%M:%S ") + " ".join(str(x) for x in a)
    print(s, flush=True)
    if LOG:
        LOG.write(s + "\n")


# ------------------------------------------------------------------------------------------------ ComfyUI watchdog
COMFY = "http://127.0.0.1:8188"
WD = {"down_since": None, "run_id": None, "run_since": None, "last_restart": 0.0, "restarts": 0}


def _get(path, timeout=10):
    with urllib.request.urlopen(COMFY + path, timeout=timeout) as r:
        return json.loads(r.read())


def restart_comfy(why):
    """Stop the hung ComfyUI main.py (both the venv launcher and the real interpreter); the supervisor loop in
    C:\\AI\\comfy-headless\\start-comfy.ps1 (logwrap) starts it again. Wait up to 3 min for /system_stats."""
    WD["last_restart"] = time.time()
    WD["restarts"] += 1
    log("WATCHDOG restart ComfyUI:", why)
    ps1 = ("Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*main.py*' -and "
           "$_.CommandLine -like '*--port 8188*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }")
    subprocess.run(["powershell", "-NoProfile", "-Command", ps1], capture_output=True, timeout=60)
    t0 = time.time()
    while time.time() - t0 < 180:
        time.sleep(10)
        try:
            _get("/system_stats", 5)
            log("WATCHDOG ComfyUI back after %d s" % (time.time() - t0))
            WD["down_since"] = WD["run_id"] = None
            return True
        except Exception:
            pass
    log("WATCHDOG ComfyUI not back after 3 min (the supervisor relaunches it; still waiting)")
    return False


def watchdog():
    while True:
        time.sleep(30)
        try:
            now = time.time()
            if now - WD["last_restart"] < 600:                       # give a fresh start 10 min
                continue
            try:
                _get("/system_stats", 10)
                WD["down_since"] = None
            except Exception:
                WD["down_since"] = WD["down_since"] or now
                if now - WD["down_since"] > 300:
                    restart_comfy("/system_stats failing for 5 min")
                continue
            q = _get("/queue", 10)
            run = q.get("queue_running") or []
            rid = run[0][1] if run else None
            if rid != WD["run_id"]:
                WD["run_id"], WD["run_since"] = rid, now
            elif rid and now - WD["run_since"] > 1200:
                restart_comfy("prompt %s running for 20 min" % rid[:8])
        except Exception:
            log("watchdog error", traceback.format_exc()[-300:])


IPA = {"file": "ip-adapter-plus_sdxl_vit-h.safetensors", "clip": "CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors"}


def run_job(pos, neg, seed, init, ctrl, den, tag, ref=None):
    """One img2img job; resubmitted if lost to a restart. Returns an RGB image.
    ref = (image, weight, weight_type): IP-Adapter (ComfyUI_IPAdapter_plus) conditions the model on that image -
    the sheet's stand frame - so the outfit / face follow it; the canny control still holds the pose."""
    def uploads():
        a = pd.api(g.upload, init, "rt_hz_%s_i.png" % tag, what="upload")
        b = pd.api(g.upload, ctrl, "rt_hz_%s_c.png" % tag, what="upload")
        c = pd.api(g.upload, ref[0], "rt_hz_%s_r.png" % tag, what="upload") if ref else None
        return a, b, c
    iname, cname, rname = uploads()

    def build():
        w = ps.wf(pos, neg, seed, iname, cname)
        w["11"]["inputs"]["denoise"] = den
        w["13"]["inputs"]["filename_prefix"] = "rt_harmonize/f"
        if ref:
            w["20"] = {"class_type": "IPAdapterModelLoader", "inputs": {"ipadapter_file": IPA["file"]}}
            w["21"] = {"class_type": "CLIPVisionLoader", "inputs": {"clip_name": IPA["clip"]}}
            w["22"] = {"class_type": "LoadImage", "inputs": {"image": rname}}
            w["23"] = {"class_type": "IPAdapterAdvanced", "inputs": {
                "model": ["2", 0], "ipadapter": ["20", 0], "image": ["22", 0], "clip_vision": ["21", 0],
                "weight": ref[1], "weight_type": ref[2], "combine_embeds": "concat", "start_at": 0.0, "end_at": 1.0,
                "embeds_scaling": "V only"}}
            w["11"]["inputs"]["model"] = ["23", 0]
        return w
    pid = pd.post_job(build())
    tries = 0
    while True:
        st, im = pd.job_state(pid)
        if st == "done":
            return im
        if st in ("lost", "error"):
            tries += 1
            if tries > 4:
                raise RuntimeError("job %s failed %d times" % (tag, tries))
            iname, cname, rname = uploads()
            pid = pd.post_job(build())
        time.sleep(2)


# ------------------------------------------------------------------------------------------------ colour helpers
def lab(rgb):
    a = np.asarray(rgb, np.float32).reshape(-1, 1, 3) / 255.0
    return cv2.cvtColor(a, cv2.COLOR_RGB2LAB).reshape(-1, 3)


def crop(im, i):
    return im.crop(((i % COLS) * FW, (i // COLS) * FH, (i % COLS + 1) * FW, (i // COLS + 1) * FH))


SKIP_GROUPS = ("outline",)     # outline pixels follow the silhouette: not part of the look (steel/wood stay in:
# a grey under-shirt maps to the steel family - Yosai walk 11-12, lead 2026-11-11)


class Ref:
    def __init__(self, frames, spec=None):
        cnt = {}
        for f in frames:
            a = np.asarray(f)
            op = a[..., 3] == 255
            for c in map(tuple, a[op][:, :3]):
                cnt[c] = cnt.get(c, 0) + 1
        cols = [c for c, n in cnt.items() if n >= 2] or list(cnt)
        self.cols = np.array(cols, np.uint8)
        self.L = lab(self.cols)
        # colour family of each reference colour: the spec group (skin, hair, armor, band...) whose ramp is nearest,
        # so a shade change inside a family does not count, a hood turning from hair-black to steel-grey does
        names, gl = [], []
        for nm, gr in ((spec or {}).get("groups") or {}).items():
            for h in gr["ramp"]:
                names.append(nm)
                gl.append(pd.unhx(h))
        if names:
            GL = lab(gl)
            near = np.sqrt(((self.L[:, None, :] - GL[None, :, :]) ** 2).sum(2)).argmin(1)
            fam = [names[j] for j in near]
        else:
            fam = ["c%d" % j for j in range(len(cols))]
        self.fams = sorted(set(fam))
        self.fam = np.array([self.fams.index(f) for f in fam])
        self.skip = np.array([f in SKIP_GROUPS for f in fam])
        hs = [self.regions(np.asarray(f)) for f in frames]
        self.height = float(np.mean([h[2] for h in hs]))
        self.hist = (np.mean([h[0] for h in hs], 0), np.mean([h[1] for h in hs], 0))

    def nearest(self, rgb):
        L = lab(rgb)
        d = np.sqrt(((L[:, None, :] - self.L[None, :, :]) ** 2).sum(2))
        return d.argmin(1), d.min(1), L

    def index(self, a):
        op = a[..., 3] == 255
        idx = np.full(a.shape[:2], -1)
        if op.any():
            uc, inv = np.unique(a[op][:, :3], axis=0, return_inverse=True)
            n, _, _ = self.nearest(uc)
            idx[op] = n[inv.reshape(-1)]
        return idx

    def regions(self, a):
        """(whole-figure family shares, upper-third family shares, figure height); weapon and outline pixels left out."""
        idx = self.index(a)
        body = idx >= 0
        body[body] = ~self.skip[idx[body]]
        nf = len(self.fams)
        ys = np.nonzero(body.any(1))[0]
        if len(ys) < 4:
            return np.zeros(nf), np.zeros(nf), 0
        top, bot = ys.min(), ys.max() + 1
        fam = np.where(body, self.fam[np.maximum(idx, 0)], -1)
        v = fam[fam >= 0]
        up = fam[top:top + max(3, int((bot - top) * 0.35))]
        u = up[up >= 0]
        return (np.bincount(v, minlength=nf) / max(1, len(v)), np.bincount(u, minlength=nf) / max(1, len(u)),
                bot - top)

    def region_dist(self, a):
        """max(whole-figure, upper-third) family histogram distance to the stand frames (0 same .. 1 nothing shared);
        lying / kneeling poses (figure under 70% of the stand height) use the whole figure only."""
        g_, u_, h = self.regions(a)
        d = float(np.abs(g_ - self.hist[0]).sum() / 2)
        if h >= 0.7 * self.height:
            d = max(d, float(np.abs(u_ - self.hist[1]).sum() / 2))
        return d


def palette_pass(ref, fr, keep_accents=True):
    """(mapped frame, mean dE, foreign share). Only fully opaque pixels are touched (the soft foot shadow stays)."""
    a = np.asarray(fr).copy()
    op = a[..., 3] == 255
    if not op.any():
        return fr, 0.0, 0.0
    uc, inv = np.unique(a[op][:, :3], axis=0, return_inverse=True)
    n, d, L = ref.nearest(uc)
    inv = inv.reshape(-1)
    dpx = d[inv]
    chroma = np.sqrt(L[:, 1] ** 2 + L[:, 2] ** 2)
    effect = (L[:, 0] > 88) & (chroma < 14)                    # white / pale slash arcs and sparks
    far = np.zeros(a.shape[:2], bool)
    far[op] = (dpx > MAP_DE) & ~effect[inv]
    keep = np.zeros(a.shape[:2], bool)
    foreign = 0
    if far.any():
        nlab, lbl, stats, _ = cv2.connectedComponentsWithStats(far.astype(np.uint8), connectivity=8)
        for k in range(1, nlab):
            if keep_accents and stats[k, cv2.CC_STAT_AREA] <= ACCENT_PX:
                keep[lbl == k] = True
            else:
                foreign += stats[k, cv2.CC_STAT_AREA]
    eff = np.zeros(a.shape[:2], bool)
    eff[op] = effect[inv]
    new = ref.cols[n[inv]]
    sub = a[op]
    m = ~(keep[op] | eff[op])
    sub[m, :3] = new[m]
    a[op] = sub
    return Image.fromarray(a, "RGBA"), float(dpx.mean()), foreign / float(op.sum())


def facing_right(fr, skin_cols):
    """True / False / None: is the face (skin pixels in the head band) on the right half of the head?"""
    a = np.asarray(fr)
    al = a[..., 3] == 255
    ys = np.nonzero(al.any(1))[0]
    if len(ys) < 10 or skin_cols is None or not len(skin_cols):
        return None
    top = ys.min()
    band = a[top:top + max(6, (ys.max() - top) // 5)]
    bal = band[..., 3] == 255
    xs = np.nonzero(bal.any(0))[0]
    if len(xs) < 4:
        return None
    sk = np.zeros(bal.shape, bool)
    L = lab(band[..., :3].reshape(-1, 3)).reshape(bal.shape + (3,))
    for c in lab(skin_cols):
        sk |= (np.sqrt(((L - c) ** 2).sum(2)) < 10) & bal
    if sk.sum() < 3:
        return None
    return bool(np.nonzero(sk)[1].mean() > (xs.min() + xs.max()) / 2.0)


def iou(a, b):
    x, y = np.asarray(a)[..., 3] > 0, np.asarray(b)[..., 3] > 0
    u = (x | y).sum()
    return float((x & y).sum() / u) if u else 1.0


def head_agree(ref, cand, orig):
    """Head band colour layout matches the original better than the mirrored original (the head did not turn)."""
    ci, oi = ref.index(np.asarray(cand)), ref.index(np.asarray(orig))
    ys = np.nonzero((oi >= 0).any(1))[0]
    xs = np.nonzero((oi >= 0).any(0))[0]
    if len(ys) < 4:
        return True
    y0, y1 = ys.min(), ys.min() + max(6, (ys.max() - ys.min()) // 4)
    x0, x1 = xs.min(), xs.max() + 1
    c, o = ci[y0:y1, x0:x1], oi[y0:y1, x0:x1]
    m = (c >= 0) | (o >= 0)
    same = ((c == o) & m).sum()
    mir = ((c == o[:, ::-1]) & m).sum()
    return same >= mir


# ------------------------------------------------------------------------------------------------ per sheet
def entries():
    pics = json.load(open(EPJ, encoding="utf-8"))
    by = {}
    for ep, v in pics.items():
        if isinstance(v, dict) and v.get("pic3d"):
            by.setdefault(os.path.basename(v["pic3d"]), (ep, v))
    return by


def ai_fp(key):
    d = os.path.join(pd.SHEETS, key)
    h = hashlib.sha1()
    for f in sorted(os.listdir(d)):
        if len(f) == 8 and f.startswith("f") and f.endswith(".png"):
            st = os.stat(os.path.join(d, f))
            h.update(("%s %d %d;" % (f, st.st_size, int(st.st_mtime))).encode())
    return h.hexdigest()


_PALS = {}


def PAL_OF(spec):
    if spec["key"] not in _PALS:
        _PALS[spec["key"]] = pd.Pal(spec)
    return _PALS[spec["key"]]


HEAD_SHARE = 0.28      # top share of the figure kept from the original frame in the reference pass (face + hair)


def keep_head_weapon(ref, cand, orig, rig=None, pal=None, pal_names=()):
    """Composite for the IP-Adapter pass: the original frame's head (top HEAD_SHARE of its figure) and its weapon pixels
    (colours of the spec's steel / wood groups, grown 1 px) over the new frame. Yosai test: 0.8 linear fixed the robe
    but paled the faces and turned the staff gold."""
    o, c_ = np.asarray(orig).copy(), np.asarray(cand).copy()
    op = o[..., 3] > 0
    ys = np.nonzero(op.any(1))[0]
    if not len(ys):
        return cand
    keep = np.zeros(op.shape, bool)
    keep[:ys.min() + int(round((ys.max() - ys.min() + 1) * HEAD_SHARE))] = True
    keep &= op | (c_[..., 3] > 0)
    weapon = np.zeros(op.shape, bool)
    if rig is not None and pal is not None:           # where the procedural rig draws the weapon (steel / wood groups):
        r = np.asarray(rig)                              # the rig, not the AI colours - a grey under-shirt is "steel"
        L = pd.pa.lab(r[..., :3].reshape(-1, 3))         # colour too and must not be kept
        g_ = pal.dgid[((L[:, None, :] - pal.DL[None, :, :]) ** 2).sum(2).argmin(1)].reshape(r.shape[:2])
        names = list(pal_names)
        wg = [names.index(n) for n in ("steel", "wood") if n in names]
        weapon = (r[..., 3] > 0) & np.isin(g_, wg)
        weapon = cv2.dilate(weapon.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    m = keep | (weapon & (op | (c_[..., 3] > 0)))
    c_[m] = o[m]
    return Image.fromarray(c_, "RGBA")


def comfy_frame(spec, ref, aid, i, mapped, orig, base_score, rec, refimg=None, rounds=None, tries_key="tries"):
    """Up to 3 rounds of CANDS img2img candidates; the best accepted one or None.
    refimg = (image, weight, weight_type) adds the IP-Adapter reference (the stand frame)."""
    white = Image.new("RGBA", mapped.size, (255, 255, 255, 255))
    white.alpha_composite(mapped)
    init = pa.up(white.convert("RGB")).filter(ImageFilter.GaussianBlur(2))
    ctrl = pa.control(mapped)
    with pd.LOCK:
        ps.DESC["_spec"] = spec["prompt"]
        pos = ps.prompt_for("_spec", aid)
    neg = gp.NEG + ", " + spec["negative"]
    oa = np.asarray(orig)
    solid = cv2.erode((oa[..., 3] == 255).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    sil = cv2.dilate((oa[..., 3] > 0).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    shadow = (oa[..., 3] > 0) & (oa[..., 3] < 255)
    best = None
    rec.setdefault(tries_key, [])
    for den, rnd in (rounds or ROUNDS):
        for s in range(CANDS):
            seed = 7000 + i * 31 + rnd * 7 + s + (500 if refimg else 0)
            im = run_job(pos, neg, seed, init, ctrl, den, "%s_%d_%d_%d" % (spec["key"], i, rnd, s), ref=refimg)
            small = np.asarray(g.key_out(im.resize((FW * K, FH * K)), holes=True).resize((FW, FH), Image.BOX)).copy()
            fill = solid & (small[..., 3] < 230)
            small[fill] = np.asarray(mapped)[fill]
            alpha = (small[..., 3] > 110) & sil & ~shadow
            small[..., 3] = np.where(alpha, 255, 0)
            small[shadow] = oa[shadow]
            cand, _, _ = palette_pass(ref, Image.fromarray(small, "RGBA"), keep_accents=False)
            if refimg:                                    # (lead 2026-11-12) robe/body from the new frame only: the
                cand = keep_head_weapon(ref, cand, orig, ps.frame(spec["sheet"], i), PAL_OF(spec), list(spec["groups"]))
            if refimg:                                    # keep every candidate for eye review
                cd = os.path.join(OUT, spec["key"], "cand")
                os.makedirs(cd, exist_ok=True)
                cand.save(os.path.join(cd, "f%03d_r%d_s%d.png" % (i, rnd, s)))
            sc = ref.region_dist(np.asarray(cand))
            ok_iou = iou(cand, orig)
            ok_head = head_agree(ref, cand, orig)
            verdict = "accept" if ok_iou >= IOU_MIN and ok_head and sc < base_score * 0.9 else "reject"
            why = [] if verdict == "accept" else [w for w, bad in (("iou", ok_iou < IOU_MIN), ("facing", not ok_head),
                                                                   ("no gain", sc >= base_score * 0.9)) if bad]
            rec[tries_key].append({"round": rnd, "den": den, "seed": seed, "iou": round(ok_iou, 3), "head_ok": bool(ok_head),
                                 "region": round(sc, 3), "verdict": verdict, "why": why})
            if verdict == "accept" and (best is None or sc < best[1]):
                best = (cand, sc)
        if best:
            return best
    return None


REF_ROUNDS = ((0.42, 0), (0.50, 1), (0.58, 2))   # more freedom than the plain pass: the outfit has to change
REF_T = 0.30                                       # side-view upright frames whose region score is still over this


def ref_targets(key, frames, force):
    """Frames for the reference pass: forced ones, the plain pass's "needs eye", and upright side-view frames whose
    colour-family score vs the stand frames is still high (head or outfit different)."""
    out = []
    for i, r in frames.items():
        i = int(i)
        if r.get("ref_final"):
            continue
        side = not r["anim"].endswith(("_f", "_b")) and r["anim"] not in LYING
        score = r.get("region_final", r.get("region_palette", 0))
        if i in force or r["final"] == "palette (needs eye)" and side or side and score > REF_T:
            out.append(i)
    return sorted(out)


def ref_pass(key, spec, ep, entry, weight, wtype, only_frames=None, install_it=True):
    """IP-Adapter pass on the installed (already harmonized) sheet: reference = stand frame 0."""
    spec = dict(spec, key=key)                            # candidates under out/<key>/cand (spec key is "yosai")
    sheet = spec["sheet"]
    src = Image.open(os.path.join(PIC, sheet)).convert("RGBA")
    am = [a for a in entry.get("animap", []) if isinstance(a, dict) and "st" in a]
    stand = next((a for a in am if a["id"] == "stand"), {"st": 0, "en": 1})
    ref = Ref([crop(src, i) for i in range(stand["st"], stand["en"])], spec)
    r0 = crop(src, stand["st"])
    white = Image.new("RGBA", r0.size, (255, 255, 255, 255))
    white.alpha_composite(r0)
    refimg = (pa.up(white.convert("RGB")), weight, wtype)
    lp = os.path.join(LOGS, key + ".json")
    frames = json.load(open(lp)) if os.path.exists(lp) else {}
    todo = only_frames if only_frames is not None else ref_targets(key, frames, FORCE.get(key, []))
    od = os.path.join(OUT, key)
    os.makedirs(od, exist_ok=True)
    out = src.copy()
    n = 0
    for i in todo:
        rec = frames.setdefault(str(i), {"anim": "?", "final": "palette", "tries": []})
        cur = crop(src, i)
        base = ref.region_dist(np.asarray(cur))
        forced = i in FORCE.get(key, [])
        # forced frames were picked by eye because the score cannot see their fault (Yosai grey under-shirt scored like a
        # clean frame; all 6 IP-Adapter candidates were rejected "no gain"): for them only facing + silhouette gate
        got = comfy_frame(spec, ref, rec.get("anim", "stand"), i, cur, cur, 1e9 if forced else base,
                          rec, refimg=refimg, rounds=REF_ROUNDS, tries_key="ref_tries")
        rec["ref_settings"] = [weight, wtype]
        if got:
            rec["ref_final"], rec["final"], rec["region_ref"] = "accept", "ref", round(got[1], 3)
            got[0].save(os.path.join(od, "f%03d.png" % i))
            out.paste(got[0], ((i % COLS) * FW, (i // COLS) * FH))
            n += 1
        else:
            rec["ref_final"] = "reject"
        json.dump(frames, open(lp, "w"), indent=1, default=_jd)
        log("  ref %s f%d: %s" % (key, i, rec["ref_final"]))
    save_png(out, os.path.join(OUT, sheet))
    before = os.path.join(BACKUP, sheet)
    contact(key, Image.open(before).convert("RGBA") if os.path.exists(before) else src, out, am, frames)
    if install_it and n:
        install(key, sheet, out)
    return n, len(todo)


def harmonize(key, spec, ep, entry, palette_only):
    sheet = spec["sheet"]
    src = Image.open(os.path.join(PIC, sheet)).convert("RGBA")
    am = [a for a in entry.get("animap", []) if isinstance(a, dict) and "st" in a]
    limit = json.load(open(os.path.join(HERE, "pixelai_standonly.json"))).get(key)
    if limit:                                         # map-only NPCs: just what they do on the map
        am = [a for a in am if a["id"] in limit]
    stand = next((a for a in am if a["id"] == "stand"), {"st": 0, "en": 1})
    ref_ids = list(range(stand["st"], stand["en"]))
    ref = Ref([crop(src, i) for i in ref_ids], spec)
    aid_of = {}
    for a in sorted(am, key=lambda a: a["en"] - a["st"]):
        for i in range(a["st"], max(a["en"], a["st"] + 1)):
            aid_of.setdefault(i, a["id"])
    used = sorted(i for i in aid_of if i not in ref_ids and i < COLS * ps.ROWS and crop(src, i).getbbox())
    skin = [pd.unhx(h) for h in spec["groups"].get("skin", {}).get("ramp", [])]
    out = src.copy()
    od = os.path.join(OUT, key)
    os.makedirs(od, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)
    lp = os.path.join(LOGS, key + ".json")
    frames = json.load(open(lp)) if os.path.exists(lp) else {}
    for i in used:
        orig = crop(src, i)
        done = os.path.join(od, "f%03d.png" % i)
        rec = frames.get(str(i))
        if rec and os.path.exists(done) and (palette_only or rec.get("final") != "pending"):
            out.paste(Image.open(done).convert("RGBA"), ((i % COLS) * FW, (i // COLS) * FH))
            continue
        mapped, de, foreign = palette_pass(ref, orig)
        r0 = ref.region_dist(np.asarray(orig))
        r1 = ref.region_dist(np.asarray(mapped))
        rec = {"anim": aid_of[i], "dE": round(de, 2), "foreign": round(foreign, 3), "region_before": round(r0, 3),
               "region_palette": round(r1, 3), "facing_right": facing_right(orig, skin), "tries": []}
        final = mapped
        side_view = not aid_of[i].endswith(("_f", "_b"))  # front / back views legitimately show other colours
        forced = i in FORCE.get(key, [])                  # frames seen by eye (tools/harmonize_force.json)
        rec["forced"] = forced
        upright = aid_of[i] not in LYING                  # lying / kneeling: the head check cannot work there
        if forced or (side_view and upright and (r1 > REGION_T or foreign > FOREIGN_T)):
            if palette_only:
                rec["final"] = "pending"
            else:
                got = comfy_frame(spec, ref, aid_of[i], i, mapped, orig, r1 if not forced else r1 / 0.9 + 1e-6, rec)
                if got:
                    final = got[0]
                    rec["final"], rec["region_final"] = "comfy", round(got[1], 3)
                else:
                    rec["final"] = "palette (needs eye)"
        else:
            rec["final"] = "palette"
        final.save(done)
        frames[str(i)] = rec
        json.dump(frames, open(lp, "w"), indent=1, default=_jd)
        out.paste(final, ((i % COLS) * FW, (i // COLS) * FH))
    os.makedirs(OUT, exist_ok=True)
    save_png(out, os.path.join(OUT, sheet))
    contact(key, src, out, am, frames)
    return frames, out


def contact(key, before, after, am, frames):
    seen, rows = set(), []
    for a in am:
        r = tuple(range(a["st"], a["en"]))
        if r and r not in seen and a["id"] in ("stand", "walk", "run", "atk_main", "spell", "damage", "victory",
                                               "guard", "item", "talk", "dash", "jump", "chant", "die"):
            seen.add(r)
            rows.append((a["id"], r[:10]))
    s = 2
    W = 90 + max(len(r) for _, r in rows) * FW * s
    H = len(rows) * (FH * s * 2 + 14)
    sh = Image.new("RGB", (W, H), (110, 150, 110))
    d = ImageDraw.Draw(sh)
    y = 0
    for aid, r in rows:
        d.text((3, y + 4), "%s\nbefore\n\n\n\nafter" % aid, fill=(255, 255, 0))
        for k, i in enumerate(r):
            for row, im in ((0, before), (1, after)):
                f = crop(im, i).resize((FW * s, FH * s), Image.NEAREST)
                sh.paste(f, (90 + k * FW * s, y + 12 + row * FH * s), f)
            fl = (frames.get(str(i)) or {}).get("final", "stand")
            col = {"comfy": (80, 200, 255), "ref": (255, 120, 255), "palette (needs eye)": (255, 80, 80), "pending": (255, 160, 0)}.get(fl)
            d.text((90 + k * FW * s + 2, y), str(i) + ("" if not col else " " + fl.split()[0]),
                   fill=col or (255, 255, 255))
        y += FH * s * 2 + 14
    os.makedirs(CONTACT, exist_ok=True)
    sh.save(os.path.join(CONTACT, key + ".png"))


def install(key, sheet, out):
    os.makedirs(BACKUP, exist_ok=True)
    b = os.path.join(BACKUP, sheet)
    if not os.path.exists(b):
        Image.open(os.path.join(PIC, sheet)).save(b)
    save_png(out, os.path.join(PIC, sheet))


def tool(*args):
    r = subprocess.run([sys.executable, "-E", os.path.join(HERE, args[0])] + list(args[1:]), cwd=ROOT,
                       capture_output=True, text=True)
    if r.returncode:
        log("%s failed: %s" % (args[0], r.stderr[-600:]))


FIRST = set()          # --first k1,k2: these sheets go first (the trial sheets, for an early look)


def worklist(only):
    ents = entries()
    keys = []
    for k in sorted(os.listdir(pd.SHEETS)):
        sp = os.path.join(pd.SPECS, k + ".json")
        if not os.path.exists(sp):                        # traveler weapon / hat looks: pixelai_specs/looks/
            sp = os.path.join(pd.SPECS, "looks", k + ".json")
        if os.path.exists(os.path.join(pd.SHEETS, k, "complete")) and os.path.exists(sp) and (not only or k in only):
            spec = json.load(open(sp))
            if "__" in k:                                 # a look spec carries the base sheet name
                spec = dict(spec, sheet="trav_%s.png" % k)
            if spec["sheet"] in ents:
                n = sum(1 for f in os.listdir(os.path.join(pd.SHEETS, k)) if len(f) == 8 and f.endswith(".png"))
                keys.append((-n, k, spec, ents[spec["sheet"]]))           # full 150-frame sheets first
    keys.sort(key=lambda x: (x[1] not in FIRST, x[0], x[1]))
    return [(k, s, e) for _, k, s, e in keys]


def run(a):
    os.makedirs(WORK, exist_ok=True)
    guard = __import__("socket").socket()
    try:
        guard.bind(("127.0.0.1", 18766))
    except OSError:
        log("another anim_harmonize runner is active")
        return
    only = set(a[a.index("--only") + 1].split(",")) if "--only" in a else None
    FIRST.update(a[a.index("--first") + 1].split(",") if "--first" in a else [])
    limit = int(a[a.index("--limit") + 1]) if "--limit" in a else None
    palette_only, no_install = "--palette-only" in a, "--no-install" in a
    if not palette_only:
        threading.Thread(target=watchdog, daemon=True).start()
    state = json.load(open(STATE)) if os.path.exists(STATE) else {}
    fp_ = os.path.join(HERE, "harmonize_force.json")
    FORCE.update({k: v for k, v in (json.load(open(fp_)) if os.path.exists(fp_) else {}).items() if not k.startswith("_")})
    work = worklist(only)
    log("start: %d sheets, palette_only=%s install=%s" % (len(work), palette_only, not no_install))
    n = 0
    for key, spec, (ep, entry) in work:
        fp = ai_fp(key)
        st = state.get(key, {})
        if st.get("ai_fp") == fp and st.get("status") == "installed":
            continue
        if limit is not None and n >= limit:
            break
        n += 1
        try:
            frames, out = harmonize(key, spec, ep, entry, palette_only)
            c = {}
            for r in frames.values():
                c[r["final"]] = c.get(r["final"], 0) + 1
            status = "palette-only" if palette_only else "done"
            if not no_install and not palette_only:
                install(key, spec["sheet"], out)
                status = "installed"
                tool("badframes.py", "--apply")
                if n % 8 == 0:
                    tool("gen_portraits.py")
            state[key] = {"ai_fp": fp, "status": status, "ep": ep, "sheet": spec["sheet"], "counts": c,
                          "contact": os.path.join(CONTACT, key + ".png"), "time": time.strftime("%m-%d %H:%M")}
            json.dump(state, open(STATE, "w"), indent=1, default=_jd)
            log("sheet %s (%s): %s" % (key, ep, c))
        except Exception:
            log("ERROR", key, traceback.format_exc()[-1500:])
    if not no_install and not palette_only:
        tool("gen_portraits.py")
    summary(state)
    log("finished pass; restarts:", WD["restarts"])


def summary(state):
    tot = {}
    for v in state.values():
        for k, n in v.get("counts", {}).items():
            tot[k] = tot.get(k, 0) + n
    eyes = [(k, v["counts"].get("palette (needs eye)", 0)) for k, v in state.items()
            if v.get("counts", {}).get("palette (needs eye)")]
    md = ["# Animation harmonize (%s)" % time.strftime("%Y-%m-%d %H:%M"), "",
          "Sheets: %d (%s). Frames: %s." % (len(state), ", ".join("%s %d" % (s, sum(1 for v in state.values()
                                                                               if v["status"] == s))
                                                             for s in sorted({v["status"] for v in state.values()})),
                                          ", ".join("%s %d" % kv for kv in sorted(tot.items()))),
          "ComfyUI restarts by the watchdog this run: %d." % WD["restarts"], "",
          "Needs eye (palette-only after 3 rejected rounds): " + (", ".join("%s %d" % e for e in eyes) or "none"),
          "", "| sheet | EP | status | frames | contact |", "|---|---|---|---|---|"]
    md += ["| %s | %s | %s | %s | contact/%s.png |" % (k, v.get("ep"), v["status"], v.get("counts"), k)
           for k, v in sorted(state.items())]
    open(os.path.join(WORK, "SUMMARY.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--log" in a:
        sys.stdout = sys.stderr = open(a[a.index("--log") + 1], "a", encoding="utf-8", buffering=1)
    os.makedirs(WORK, exist_ok=True)
    if LOG is None:
        LOG = open(os.path.join(WORK, "harmonize.log"), "a", encoding="utf-8", buffering=1)
    if a and a[0] == "run":
        run(a[1:])
    elif a and a[0] == "ref":
        # python -E tools/anim_harmonize.py ref --only side_yosai,natsuko [--weight 0.7] [--type "style transfer"]
        #        [--frames 11,12] [--no-install]          IP-Adapter pass (reference = stand frame 0)
        b = a[1:]
        only = b[b.index("--only") + 1].split(",") if "--only" in b else None
        wt = float(b[b.index("--weight") + 1]) if "--weight" in b else 0.6
        wty = b[b.index("--type") + 1] if "--type" in b else "linear"
        fr = [int(x) for x in b[b.index("--frames") + 1].split(",")] if "--frames" in b else None
        fp_ = os.path.join(HERE, "harmonize_force.json")
        FORCE.update({k: v for k, v in (json.load(open(fp_)) if os.path.exists(fp_) else {}).items()
                      if not k.startswith("_")})
        guard = __import__("socket").socket()
        try:
            guard.bind(("127.0.0.1", 18767))
        except OSError:
            log("another anim_harmonize ref runner is active")
            sys.exit(0)
        threading.Thread(target=watchdog, daemon=True).start()
        state = json.load(open(STATE)) if os.path.exists(STATE) else {}
        tot = 0
        for key, spec, (ep, entry) in worklist(set(only) if only else None):
            if state.get(key, {}).get("ref") and fr is None:
                continue
            try:
                n, m = ref_pass(key, spec, ep, entry, wt, wty, fr, "--no-install" not in b)
                log("ref sheet %s: %d of %d frames accepted (weight %.2f, %s)" % (key, n, m, wt, wty))
                if key in state and fr is None:
                    state[key]["ref"] = [n, m]
                    json.dump(state, open(STATE, "w"), indent=1, default=_jd)
                tot += n
            except Exception:
                log("ERROR ref", key, traceback.format_exc()[-1500:])
        if tot and "--no-install" not in b:
            tool("badframes.py", "--apply")
            tool("gen_portraits.py")
        log("ref pass finished")
    elif a and a[0] == "status":
        summary(json.load(open(STATE)) if os.path.exists(STATE) else {})
        print(open(os.path.join(WORK, "SUMMARY.md"), encoding="utf-8").read())
