"""AI sprite sheets, the long run (user, 2026-11-08): strict per-character specs + the v2 temporal pipeline
(tools/gen_pixelanim.py) over whole v4 sheets, keeping ComfyUI busy for days. Nothing is written into the game.

  python -E tools/gen_pixeldrive.py specs            write tools/pixelai_specs/<key>.json for every character
  python -E tools/gen_pixeldrive.py run [--workers 3] [--only natsuko,rensei] [--looks] [--busts] [--log file]
        process the work list in order: 8 travelers, Gonta, side cast, human enemies (base sheets); with --looks the
        travelers' weapon/hat look sheets (EP2000+) after the bases; with --busts, last, the dialog bust candidates
        (queue_busts.py --redo + collect_busts.py, for review only). Resumable: finished work is skipped.
        Normally started detached by tools/start_pixeldrive.bat.
  python -E tools/gen_pixeldrive.py progress         progress/<HHMM>_*.png, GIFs, PROGRESS.md

Spec (JSON): key, name, sheet (enemy_pic file), prompt, negative, seed, candidates, groups {name: {"base": hex,
"ramp": [5 hex], "anywhere": bool}}. The palette is the union of the ramps + outline darks; a pixel may only take a
group's colour if that group appears in our rig frame within 3 px (so red stays on the headband, steel and wood on
the weapon, skin on skin), except "anywhere" groups (outlines).
Output: _art/preview/agents/pixelai/sheets/<key>/f<NNN>.png (+ cand/ candidates), sheets/<key>.png (14x11 sheet).
"""
import http.client
import io
import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
import traceback
import urllib.error
import urllib.parse

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv, sys.argv = sys.argv, [sys.argv[0]]
import gen_pixelanim as pa  # noqa: E402
import gen_sprites2d as s2  # noqa: E402  (read only: ramp(), TRAVELERS, look combos)
import gen_sidecast as sc  # noqa: E402  (read only)
import gen_human_enemies as he  # noqa: E402  (read only)
sys.argv = _argv
ps, g, gp = pa.ps, pa.g, pa.gp

SPECS = os.path.join(HERE, "pixelai_specs")
SHEETS = os.path.join(ps.PX, "sheets")
FW, FH, COLS = ps.FW, ps.FH, ps.COLS
RES = ps.RES
LOCK = threading.Lock()


def hx(c):
    return "#%02x%02x%02x" % tuple(int(v) for v in c[:3])


def unhx(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


COLOR_WORDS = [((30, 26, 30), "black"), ((42, 36, 42), "black"), ((58, 44, 44), "dark brown"), ((90, 60, 40), "brown"), ((140, 100, 60), "light brown"),
               ((200, 160, 90), "tan"), ((230, 200, 120), "golden"), ((200, 170, 60), "gold"),
               ((170, 40, 40), "red"), ((120, 30, 40), "dark red"), ((220, 110, 40), "orange"),
               ((60, 120, 70), "green"), ((40, 70, 50), "dark green"), ((160, 190, 150), "sage green"),
               ((50, 70, 120), "navy blue"), ((80, 100, 130), "slate blue"), ((150, 190, 230), "pale blue"),
               ((110, 70, 150), "purple"), ((200, 180, 220), "lavender"), ((236, 236, 240), "white"),
               ((130, 130, 136), "grey"), ((70, 72, 80), "dark grey"), ((70, 80, 100), "blue-grey"),
               ((226, 176, 136), "light tan"), ((246, 206, 170), "fair")]


def cword(c):
    c = np.array(c[:3], float)
    return min(COLOR_WORDS, key=lambda w: ((np.array(w[0]) - c) ** 2).sum())[1]


GROUP_KEYS = ["skin", "hair", "top", "lower", "haori", "armor", "helm", "hat_col", "cloth", "mask_col", "pcol",
              "accent", "lace", "band", "cord", "lining", "mawashi", "sashimono", "glow"]
WEAPON_DESC = {"yari": "a long yari spear with a black lacquered shaft and a steel blade",
               "katana": "a katana with a steel blade and a black hilt", "tanto": "a short tanto dagger",
               "bo": "a long dark wooden bo staff", "yumi": "a tall yumi longbow", "tetsubo": "an iron-studded tetsubo club",
               "naginata": "a naginata polearm with a black shaft and a curved steel blade", "shakujo":
               "a shakujo staff with metal rings", "musket": "a matchlock musket", "kama": "a kama sickle",
               "nodachi": "a huge nodachi sword", "fan": "a folding fan", "none": "", "bokken": "a wooden bokken sword"}


def spec_from(d, sheet, kind, desc=None):
    # "detect": the rig's own colours for that part (gen_sprites2d ramps), used to find WHERE a group may go;
    # "ramp": the output colours. Weapon wood is the rig's WOOD but comes out black lacquer (user: Natsuko's shaft).
    groups = {"outline": {"base": "#141218", "ramp": ["#141218", "#26242e"], "anywhere": True},
              "steel": {"base": "#a0aab8", "ramp": ["#5a606c", "#969fae", "#cdd5e1", "#f8f8fc"],
                        "detect": [hx(c) for c in s2.ramp(s2.METAL)]},
              "wood": {"base": "#2a201e", "ramp": ["#1c1614", "#2a201e", "#44342a"],
                       "detect": [hx(c) for c in s2.ramp(s2.WOOD)]}}
    for k in GROUP_KEYS:
        if k in d and isinstance(d[k], tuple) and len(d[k]) >= 3:
            r = [hx(c) for c in s2.ramp(d[k])]
            groups[k] = {"base": hx(d[k]), "ramp": r, "detect": r}
    hair = cword(d["hair"]) if "hair" in d else "black"
    female = d.get("female", False)
    who = "1girl, woman" if female else "1boy, male focus, man"
    if desc is None:
        bits = [who, d.get("name", d["key"]), "%s skin" % cword(d.get("skin", (226, 176, 136))),
                "%s hair" % hair, (d.get("hairstyle") or "").replace("_", " ") + " hair",
                ("%s %s" % (cword(d["armor"]), "lacquered lamellar armor")) if "armor" in d else "",
                ("%s kimono" % cword(d["top"])) if "top" in d else "",
                ("%s haori" % cword(d["haori"])) if "haori" in d else "",
                ("%s hakama" % cword(d["lower"])) if "lower" in d else "",
                (d.get("hat") or d.get("head") or "").replace("_", " "),
                WEAPON_DESC.get(d.get("weapon", "none"), d.get("weapon", "")), "feudal japan"]
        desc = ", ".join(b for b in bits if b.strip())
    neg = []
    for col in ("red", "orange", "pink", "blue", "green", "purple", "white", "blonde"):
        if col not in hair:
            neg.append("%s hair" % col)
    neg += ["red skin", "orange skin", "red outline"]
    if not any(k in d for k in ("accent", "lace", "band")) or cword(d.get("top", (0, 0, 0))) not in ("red", "dark red"):
        neg += ["red clothes"]
    return {"key": d["key"], "name": d.get("name", d["key"]), "kind": kind, "sheet": sheet, "prompt": desc,
            "negative": ", ".join(neg), "seed": 11, "candidates": 3 if kind == "traveler" else 2, "groups": groups}


def build_specs():
    os.makedirs(SPECS, exist_ok=True)
    n = 0
    for T in s2.TRAVELERS:
        k = T["key"]
        desc = gp.CAST[k][0] if k in gp.CAST else None
        if k in pa.PROMPT_FIX:
            desc = pa.PROMPT_FIX[k][0]
        sp = spec_from(T, "trav_%s.png" % k, "traveler", desc)
        if k == "natsuko":                                   # approved check (user, 2026-11-08)
            sp["groups"]["skin"]["ramp"] = ["#764228", "#a66238", "#d48a4e", "#f0ac6c"]   # detect stays the rig's
            sp["groups"]["hair"]["ramp"] = ["#1c161a", "#342a2e", "#504244"]
            sp["negative"] += pa.PROMPT_FIX[k][1]
        json.dump(sp, open(os.path.join(SPECS, "%s.json" % k), "w"), indent=1)
        n += 1
    for C in sc.CAST:
        f = "side_%s.png" % C["key"]
        if os.path.exists(os.path.join(RES, f)):
            json.dump(spec_from(C, f, "side"), open(os.path.join(SPECS, "side_%s.json" % C["key"]), "w"), indent=1)
            n += 1
    for E in he.ENEMIES:
        f = "hum_%s.png" % E["key"]
        if os.path.exists(os.path.join(RES, f)):
            json.dump(spec_from(E, f, "enemy"), open(os.path.join(SPECS, "hum_%s.json" % E["key"]), "w"), indent=1)
            n += 1
    print(n, "specs in", SPECS)


# ------------------------------------------------------------------------------------------------- quantize
class Pal:
    def __init__(self, spec):
        cols, gid, names, dcols, dgid = [], [], [], [], []
        for gi, (nm, gr) in enumerate(spec["groups"].items()):
            names.append(nm)
            for h in gr["ramp"]:
                cols.append(unhx(h))
                gid.append(gi)
            for h in gr.get("detect", gr["ramp"]):
                dcols.append(unhx(h))
                dgid.append(gi)
        self.DL = pa.lab(np.array(dcols, np.uint8))
        self.dgid = np.array(dgid)
        self.cols = np.array(cols, np.uint8)
        self.L = pa.lab(self.cols)
        self.gid = np.array(gid)
        self.anywhere = np.array([spec["groups"][n].get("anywhere", False) for n in names])
        self.ng = len(names)

    def allowed(self, rig):
        """[FH, FW, groups] bool: a group is allowed where the rig (nearest group per pixel) has it within 3 px."""
        a = np.asarray(rig)
        L = pa.lab(a[..., :3].reshape(-1, 3))
        d = ((L[:, None, :] - self.DL[None, :, :]) ** 2).sum(2)
        rg = self.dgid[d.argmin(1)].reshape(FH, FW)
        op = a[..., 3] > 0
        al = np.zeros((FH, FW, self.ng), bool)
        k = np.ones((7, 7), np.uint8)
        for gi in range(self.ng):
            m = ((rg == gi) & op).astype(np.uint8)
            al[..., gi] = cv2.dilate(m, k) > 0 if m.any() else False
        al[..., self.anywhere] = True
        none = ~al.any(2)                                    # outside every group (edges): allow all
        al[none] = True
        return al

    def quantize(self, small, rig):
        a = np.asarray(small).copy()
        rg = np.asarray(rig)                                  # white hair/cloth gets keyed out with the white background:
        solid = cv2.erode((rg[..., 3] == 255).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0  # inside the rig body it
        fill = solid & (a[..., 3] < 230)                      # is never background, so those pixels take the rig colour
        a[fill, :3] = rg[fill, :3]
        a[fill, 3] = 255
        px = pa.lab(a[..., :3].reshape(-1, 3))
        d = ((px[:, None, :] - self.L[None, :, :]) ** 2).sum(2)
        al = self.allowed(rig).reshape(-1, self.ng)
        ok = al[:, self.gid]
        d[~ok] = 1e9
        idx = d.argmin(1).reshape(FH, FW)
        ra = np.asarray(rig.getchannel("A"))
        sil = cv2.dilate((ra > 128).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        shadow = (ra > 0) & (ra < 255)                        # the rig's soft foot shadow stays as it is: the AI
        alpha = (a[..., 3] > 110) & sil & ~shadow              # painted it as a pale slab under the feet
        out = np.dstack([self.cols[idx], (alpha * 255).astype(np.uint8)])
        out[shadow] = np.asarray(rig)[shadow]
        return Image.fromarray(out, "RGBA"), np.where(alpha, idx, -1)


# ------------------------------------------------------------------------------------------------- frames
def api(fn, *a, what=""):
    """Call the ComfyUI API, waiting out a restart / outage. An HTTP 4xx (bad workflow) is a real error and raises."""
    warned = False
    while True:
        try:
            return fn(*a)
        except urllib.error.HTTPError as ex:
            if ex.code < 500:
                raise
        except (urllib.error.URLError, http.client.HTTPException, OSError):
            pass
        if not warned:
            print("%s ComfyUI not answering (%s): waiting" % (time.strftime("%H:%M"), what), flush=True)
            warned = True
        time.sleep(10)


def post_job(wf_):
    # explicit priority: negative and increasing -> FIFO among these jobs ("front" made later jobs starve earlier ones)
    body = {"prompt": wf_, "client_id": "rt_pixeldrive", "number": -1e12 + time.time() * 1000}
    return json.loads(api(g._req, "/prompt", json.dumps(body).encode(), what="submit"))["prompt_id"]


def job_state(pid):
    """("done", image) | ("error", None) | ("waiting", None) | ("lost", None): lost = neither queued nor in history."""
    def look():
        h = json.loads(g._req("/history/" + pid))
        return h.get(pid)
    e = api(look, what="history")
    if e is None:
        q = json.loads(api(g._req, "/queue", what="queue"))
        if any(item[1] == pid for item in q["queue_running"] + q["queue_pending"]):
            return "waiting", None
        e = api(look, what="history")                       # it may have finished between the two calls
        if e is None:
            return "lost", None
    if e.get("status", {}).get("status_str") == "error":
        return "error", None
    for node in e.get("outputs", {}).values():
        for im in node.get("images", []):
            q = "/view?filename=%s&subfolder=%s&type=%s" % (urllib.parse.quote(im["filename"]),
                                                            urllib.parse.quote(im["subfolder"]), im["type"])
            return "done", Image.open(io.BytesIO(api(g._req, q, what="image"))).convert("RGB")
    return "error", None


def submit_wait(pos, neg, seeds, init, ctrl, den, tag, prio_front=True):
    """Queue one job per seed and wait for all. A job lost to a ComfyUI restart is resubmitted; the guide images are
    uploaded again first, in case the input folder changed."""
    def uploads():
        return (api(g.upload, init, "rt_pd_%s_i.png" % tag, what="upload"),
                api(g.upload, ctrl, "rt_pd_%s_c.png" % tag, what="upload"))
    iname, cname = uploads()

    def build(s):
        w = ps.wf(pos, neg, s, iname, cname)
        w["11"]["inputs"]["denoise"] = den
        return w
    jobs = [[s, post_job(build(s)), 0] for s in seeds]
    out = []
    for job in jobs:
        while True:
            st, im = job_state(job[1])
            if st == "done":
                out.append(im)
                break
            if st in ("lost", "error"):
                job[2] += 1
                if st == "error" and job[2] > 3:
                    raise RuntimeError("ComfyUI failed %s seed %s three times" % (tag, job[0]))
                print("%s %s job %s: resubmitting" % (time.strftime("%H:%M"), tag, st), flush=True)
                iname, cname = uploads()
                job[1] = post_job(build(job[0]))
            time.sleep(1.0)
    return out


def valid_frame(outp):
    """(image, index map) of a finished frame, or None if it is missing or damaged (those are deleted)."""
    if not os.path.exists(outp):
        return None
    try:
        q = Image.open(outp)
        q.load()
        idx = np.load(outp + ".npy")
        if q.size == (FW, FH) and idx.shape == (FH, FW):
            return q.convert("RGBA"), idx
    except Exception:
        pass
    for p in (outp, outp + ".npy"):
        if os.path.exists(p):
            os.remove(p)
    return None


def save_frame(q, idx, outp):
    """The index map first, the PNG last and atomically: a PNG on disk always means a complete frame."""
    with open(outp + ".npy.tmp", "wb") as f:
        np.save(f, idx)
    os.replace(outp + ".npy.tmp", outp + ".npy")
    q.save(outp + ".tmp.png")
    os.replace(outp + ".tmp.png", outp)


ANIMAP = {}


def animap(sheet):
    if not ANIMAP:
        for v in json.load(open(os.path.join(g.PROJ, "resource", "enemy_pic.json"), encoding="utf-8")).values():
            if isinstance(v, dict) and v.get("pic3d"):
                ANIMAP[os.path.basename(v["pic3d"])] = v.get("animap", [])
    return ANIMAP.get(sheet, [])


def chain(spec, pal, sheet_path, rng, aid, od, start=None):
    """One animation, frame by frame (v2 temporal pipeline). start = (ai, idx, rig) of the stand frame or None."""
    prev_ai, prev_idx, rig_prev = start if start else (None, None, None)
    first = None
    tag = os.path.basename(od)
    for i in rng:
        outp = os.path.join(od, "f%03d.png" % i)
        rig = ps.frame(os.path.basename(sheet_path), i)
        if not rig.getbbox():
            continue
        have = valid_frame(outp)
        if have:
            q, idx = have
        else:
            init = pa.init_image(rig, rig_prev, prev_ai)
            ctrl = pa.control(rig)
            with LOCK:                                        # ps.DESC is shared between the workers
                ps.DESC["_spec"] = spec["prompt"]
                pos = ps.prompt_for("_spec", aid)
            neg = gp.NEG + ", " + spec["negative"]
            den = 0.72 if prev_ai is None else 0.55
            seeds = [spec["seed"] * 100 + i * 7 + s for s in range(spec["candidates"])]
            ims = submit_wait(pos, neg, seeds, init, ctrl, den, "%s_%d" % (tag, i))
            cands = []
            cd = os.path.join(od, "cand")
            os.makedirs(cd, exist_ok=True)
            for s, im in zip(seeds, ims):
                small = g.key_out(im.resize((FW * ps.K, FH * ps.K)), holes=True).resize((FW, FH), Image.BOX)
                q, idx = pal.quantize(small, rig)
                q.save(os.path.join(cd, "f%03d_s%d.png" % (i, s)))
                cands.append((q, idx))
            if prev_idx is None:
                q, idx = min(cands, key=lambda c: int((c[1] != np.roll(c[1], 1, 0)).sum() +
                                                      (c[1] != np.roll(c[1], 1, 1)).sum()))
            else:
                q, idx = min(cands, key=lambda c: int(((c[1] != prev_idx) & ((c[1] >= 0) | (prev_idx >= 0))).sum()))
                keep = ~pa.changed(rig_prev, rig, grow=1)
                qa, pa_ = np.asarray(q).copy(), np.asarray(prev_ai)
                qa[keep] = pa_[keep]
                idx = np.where(keep, prev_idx, idx)
                q = Image.fromarray(qa, "RGBA")
            save_frame(q, idx, outp)
            with LOCK:
                STATS["frames"] += 1
        prev_ai, prev_idx, rig_prev = q, idx, rig
        if first is None:
            first = (q, idx, rig)
    return first


STATS = {"frames": 0}


def do_sheet(spec, sheet_path, outkey, am):
    """Returns True when every used frame of the sheet exists."""
    pal = Pal(spec)
    od = os.path.join(SHEETS, outkey)
    os.makedirs(od, exist_ok=True)
    seen, groups = set(), []
    for a in am:
        rng = tuple(range(a["st"], max(a["en"], a["st"] + 1)))
        if rng in seen:
            continue
        seen.add(rng)
        groups.append((a["id"], rng))
    groups.sort(key=lambda x: x[1][0])
    stand = None
    for aid, rng in groups:
        side = not (aid.endswith("_f") or aid.endswith("_b"))
        st = chain(spec, pal, sheet_path, rng, aid, od, stand if (side and stand and rng[0] != 0) else None)
        if rng[0] == 0 and st:
            stand = st
    sh = Image.new("RGBA", (FW * COLS, FH * ps.ROWS), (0, 0, 0, 0))
    for f in os.listdir(od):
        if len(f) == 8 and f.startswith("f") and f.endswith(".png"):
            i = int(f[1:4])
            sh.alpha_composite(Image.open(os.path.join(od, f)).convert("RGBA"), ((i % COLS) * FW, (i // COLS) * FH))
    tmp = os.path.join(SHEETS, "%s.tmp.png" % outkey)
    sh.save(tmp)
    os.replace(tmp, os.path.join(SHEETS, "%s.png" % outkey))
    need = sorted({i for _, r in groups for i in r if ps.frame(os.path.basename(sheet_path), i).getbbox()})
    return all(os.path.exists(os.path.join(od, "f%03d.png" % i)) for i in need)


WEAPON_WORDS = re.compile(r"\b(yari|spear|katana|sword|tanto|dagger|bo staff|staff|shakujo|yumi|longbow|bow|quiver|"
                          r"arrows|jitte|tetsubo|musket|naginata)\b", re.I)
HEAD_WORDS = re.compile(r"\b(headband|hachimaki|jingasa|travel hat|straw hat)\b", re.I)
HAT = {"jingasa": ("red lacquered jingasa, shallow conical war hat", [(150, 46, 40)]),
       "kasa": ("sugegasa, wide conical woven rice-straw travel hat, plain hat", [(208, 178, 110)]),
       "kabuto": ("kabuto samurai helmet with a gold disc crest", [(84, 86, 98), (226, 190, 80)]),
       "eboshi": ("eboshi, tall black lacquered court cap", [(40, 38, 46)]),
       "hachimaki": ("white hachimaki headband", [(238, 234, 226)])}


def look_spec(sp, T, w, h, outkey):
    """A traveler's base spec with the weapon and head item swapped; written to pixelai_specs/looks/."""
    v = dict(sp)
    v["groups"] = dict(sp["groups"])
    items = [it for it in sp["prompt"].split(", ") if not WEAPON_WORDS.search(it)]
    if h:
        items = [it for it in items if not HEAD_WORDS.search(it)]
        desc, cols = HAT[h]
        items.insert(-1, "wearing " + desc)
        for n, c in enumerate(cols):
            r = [hx(x) for x in s2.ramp(c)]
            v["groups"]["hat%d" % n] = {"base": hx(c), "ramp": r, "detect": r}
    items.insert(-1, ("holding " + WEAPON_DESC[w]) if WEAPON_DESC.get(w) else "unarmed, empty hands")
    v["prompt"] = ", ".join(items)
    v["negative"] = sp["negative"] + ", drinking straw, mascot, creature on hat, face on hat, eyes on hat, emblem on hat"
    v["key"] = outkey
    d = os.path.join(SPECS, "looks")
    os.makedirs(d, exist_ok=True)
    json.dump(v, open(os.path.join(d, "%s.json" % outkey), "w"), indent=1)
    return v


def worklist(only=None, looks=False):
    specs = sorted(f for f in os.listdir(SPECS) if f.endswith(".json"))
    trav = [t["key"] for t in s2.TRAVELERS]
    order = trav + ["side_gonta"] + [s[:-5] for s in specs if s.startswith("side_") and s != "side_gonta.json"] + \
        [s[:-5] for s in specs if s.startswith("hum_")]
    prio = json.load(open(os.path.join(HERE, "pixelai_priority.json")))        # drawn first (user requests)
    order = prio + [k for k in order if k not in prio]
    items = []
    limit = json.load(open(os.path.join(HERE, "pixelai_standonly.json")))    # key -> animation ids
    for k in order:
        if only and k not in only:
            continue
        sp = json.load(open(os.path.join(SPECS, "%s.json" % k)))
        am = animap(sp["sheet"])
        if k in limit:                                # non-recruitable, non-fighting NPCs: only what they do on the map
            am = [a for a in am if a["id"] in limit[k]]
        items.append((sp, os.path.join(RES, sp["sheet"]), k, am))
    if looks:
        ep = json.load(open(os.path.join(g.PROJ, "resource", "enemy_pic.json"), encoding="utf-8"))
        for ti, T in enumerate(s2.TRAVELERS):
            if only and T["key"] not in only:
                continue
            sp = json.load(open(os.path.join(SPECS, "%s.json" % T["key"])))
            for combo, epid, w, h in s2.look_combos(ti, T):
                pic = os.path.basename((ep.get(epid) or {}).get("pic3d", ""))
                if epid == "EP%03d" % (200 + ti) or not pic or not os.path.exists(os.path.join(RES, pic)):
                    continue
                outkey = "%s__%s_%s" % (T["key"], w, h or "own")
                items.append((look_spec(sp, T, w, h, outkey), os.path.join(RES, pic), outkey, animap(pic)))
    return items


def comfy_idle():
    q = json.loads(api(g._req, "/queue", what="queue"))
    return not (q["queue_running"] or q["queue_pending"])


def bust_stage(log_error):
    """Last stage: dialog bust candidates for review (never wired in here). Each round: wait for ComfyUI to drain,
    download what finished, forget jobs that produced nothing (lost to a restart), queue what is still missing."""
    qj = os.path.join(g.PREVIEW, "queue.json")
    py = sys.executable
    tools = HERE

    def tool(*args):
        r = subprocess.run([py, "-E", os.path.join(tools, args[0])] + list(args[1:]), cwd=g.ROOT, capture_output=True,
                           text=True)
        if r.returncode:
            raise RuntimeError("%s failed: %s" % (args[0], r.stderr[-1500:]))
    idle = 0
    while True:
        try:
            while not comfy_idle():
                time.sleep(30)
            tool("collect_busts.py")
            jobs = json.load(open(qj, encoding="utf-8"))

            def has_file(j):
                n = ("var_%s_s%d.png" % (j["variant"], j["seed"])) if j["kind"] == "variant" else "cand_s%d.png" % j["seed"]
                return os.path.exists(os.path.join(g.WORK, j["key"], "review", n))
            keep = [j for j in jobs if has_file(j)]
            json.dump(keep, open(qj, "w", encoding="utf-8"), indent=1)
            tool("queue_busts.py", "--redo")
            added = len(json.load(open(qj, encoding="utf-8"))) - len(keep)
            print(time.strftime("%H:%M"), "busts: %d images on disk, %d queued" % (len(keep), added), flush=True)
            if not added:
                break
            idle = 0
        except Exception:
            log_error("bust stage")
            idle += 1
            if idle >= 5:
                print(time.strftime("%H:%M"), "bust stage gave up; see ERRORS.txt", flush=True)
                return
            time.sleep(600)
        time.sleep(60)
    print(time.strftime("%H:%M"), "bust candidates finished: tools/pick_sheet.py to review", flush=True)


def run(workers=3, only=None, looks=False, busts=False):
    """Passes over the work list until every sheet is complete; finished frames and sheets are skipped, so a restart
    (of this runner or of ComfyUI) only costs the jobs in flight."""
    guard = socket.socket()
    try:
        guard.bind(("127.0.0.1", 18765))                      # one runner at a time; released when the process dies
    except OSError:
        print("another gen_pixeldrive runner is already active", flush=True)
        return
    # upright guide poses first (skips sheets already rendered), so a sheet is never drawn from the old leaning rig
    r = subprocess.run([sys.executable, "-E", os.path.join(HERE, "gen_upright_guides.py"), "--all"], cwd=g.ROOT,
                       capture_output=True, text=True)
    print(time.strftime("%H:%M"), "guides:", (r.stdout.strip().splitlines() or [r.stderr[-400:]])[-1], flush=True)
    if r.returncode:
        print("guide rendering failed, stopping:", r.stderr[-1500:], flush=True)
        return
    items = worklist(only, looks)
    json.dump({"total": len(items), "base": sum(1 for it in items if "__" not in it[2]),
               "frames": sum(len({i for a in it[3] for i in range(a["st"], max(a["en"], a["st"] + 1))}) for it in items)},
              open(os.path.join(ps.PX, "drive_state.json"), "w"))
    print(time.strftime("%H:%M"), len(items), "sheets in the work list", flush=True)

    def reporter():
        while True:
            time.sleep(1200)
            try:
                progress()
            except Exception:
                log_error("progress")
    threading.Thread(target=reporter, daemon=True).start()

    def log_error(what):
        with LOCK:
            open(os.path.join(ps.PX, "ERRORS.txt"), "a").write("%s %s\n%s\n" % (time.strftime("%m-%d %H:%M"), what,
                                                                               traceback.format_exc()))

    stuck = 0
    while True:
        q = [it for it in items if not os.path.exists(os.path.join(SHEETS, it[2], "complete"))]
        if not q:
            break
        before = STATS["frames"]

        def worker():
            while True:
                with LOCK:
                    if not q:
                        return
                    it = q.pop(0)
                try:
                    if do_sheet(*it):
                        open(os.path.join(SHEETS, it[2], "complete"), "w").write("1")
                        with LOCK:
                            open(os.path.join(ps.PX, "DONE.txt"), "a").write("%s %s\n" % (time.strftime("%m-%d %H:%M"),
                                                                                         it[2]))
                        print(time.strftime("%H:%M"), "sheet done", it[2], flush=True)
                except Exception:
                    log_error(it[2])
        ts = [threading.Thread(target=worker) for _ in range(workers)]
        for t in ts:
            t.start()
        for t in ts:
            t.join()
        if STATS["frames"] == before:                         # nothing moved: don't spin on a persistent error
            stuck += 1
            print(time.strftime("%H:%M"), "pass made no progress (%d); see ERRORS.txt" % stuck, flush=True)
            if stuck >= 3:
                break
            time.sleep(600)
        else:
            stuck = 0
    progress()
    print(time.strftime("%H:%M"), "sprite sheets finished", flush=True)
    if busts:
        bust_stage(log_error)


def progress():
    os.makedirs(ps.PROG, exist_ok=True)
    stamp = time.strftime("%H%M")
    rows = []
    for k in sorted(os.listdir(SHEETS)):
        d = os.path.join(SHEETS, k)
        if not os.path.isdir(d) or k == "frames":
            continue
        fs = [f for f in os.listdir(d) if len(f) == 8 and f.startswith("f") and f.endswith(".png")]
        if fs:
            rows.append((k, len(fs), os.path.exists(os.path.join(d, "complete")),
                         max(os.path.getmtime(os.path.join(d, f)) for f in fs)))
    rows.sort(key=lambda r: -r[3])
    for k, n, comp, _ in rows[:3]:                            # the three most recently active sheets
        d = os.path.join(SHEETS, k)
        sh = Image.new("RGBA", (FW * COLS, FH * ps.ROWS), (0, 0, 0, 0))
        for f in os.listdir(d):
            if len(f) == 8 and f.startswith("f") and f.endswith(".png"):
                i = int(f[1:4])
                sh.alpha_composite(Image.open(os.path.join(d, f)).convert("RGBA"),
                                   ((i % COLS) * FW, (i // COLS) * FH))
        ps.on_bg(sh, 2).save(os.path.join(ps.PROG, "%s_%s_sheet.png" % (stamp, k)))
        for nm, rng in (("stand", range(0, 8)), ("walk", range(8, 16)), ("attack", range(30, 36))):
            fr = [os.path.join(d, "f%03d.png" % i) for i in rng]
            if all(os.path.exists(f) for f in fr):
                ims = [ps.on_bg(Image.open(f).convert("RGBA"), 4) for f in fr]
                ims[0].save(os.path.join(ps.PROG, "%s_%s.gif" % (k, nm)), save_all=True, append_images=ims[1:],
                            duration=130, loop=0)
    times = sorted(os.path.getmtime(os.path.join(SHEETS, k, f)) for k, *_ in rows
                   for f in os.listdir(os.path.join(SHEETS, k)) if len(f) == 8 and f.endswith(".png"))
    hour = sum(1 for t in times if t > time.time() - 3600)
    st_path = os.path.join(ps.PX, "drive_state.json")
    total = json.load(open(st_path))["total"] if os.path.exists(st_path) else len(rows)
    planned = json.load(open(st_path)).get("frames", total * 150) if os.path.exists(st_path) else total * 150
    left = max(0, planned - len(times))
    eta = "%.1f days" % (left / hour / 24) if hour else "unknown"
    md = ["# AI sprite sheets: progress (%s)" % time.strftime("%Y-%m-%d %H:%M"), "",
          "Sheets complete: %d of %d planned (%d started). Frames done: %d. Frames in the last hour: %d. "
          "Rough time left at that rate: %s." % (sum(1 for r in rows if r[2]), total, len(rows), len(times), hour, eta),
          "", "Runner: tools\\start_pixeldrive.bat (safe to rerun; skips finished work). Log: drive_base.log. "
          "Errors: ERRORS.txt. Finished: DONE.txt. Sheets: sheets/<key>.png. GIFs: progress/<key>_<anim>.gif. "
          "Not in the game.", "", "| sheet | frames | complete |", "|---|---|---|"]
    md += ["| %s | %d | %s |" % (k, n, "yes" if c else "") for k, n, c, _ in rows]
    open(os.path.join(ps.PX, "PROGRESS.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
    print(time.strftime("%H:%M"), md[2], flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--log" in a:                                          # detached runs have no console
        sys.stdout = sys.stderr = open(a[a.index("--log") + 1], "a", encoding="utf-8", buffering=1)
    if not a or a[0] == "specs":
        build_specs()
    elif a[0] == "run":
        only = set(a[a.index("--only") + 1].split(",")) if "--only" in a else None
        run(int(a[a.index("--workers") + 1]) if "--workers" in a else 3, only, "--looks" in a, "--busts" in a)
    elif a[0] == "progress":
        progress()
