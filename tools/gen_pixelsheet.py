"""AI-painted sprite sheets in the locked s11 style, posed by our procedural rig (user, 2026-11-08).
For every frame of a v4 sheet (14x11 frames of 80x68, resource/enemy_pic/<sheet>; animap unchanged):
  our frame -> x12 nearest (960x816) on white = img2img init (smoothed) + ControlNet union (canny of the same frame)
  -> waiIllustrious + pixel-art-xl LoRA, the character's s11 prompt, ONE seed for the whole sheet
  -> key out -> x12 box downscale back to 80x68 (same position: poses, feet and timing stay ours)
  -> alpha clipped to our frame's silhouette grown 2 px -> quantized to the sheet's palette (taken from frame 0).
Output (never the game files): _art/preview/agents/pixelai/sheets/<key>.png (+ frames/<key>/fNNN.png, gifs/).
python -E tools/gen_pixelsheet.py natsuko [--frames 0-7,30-35] [--submit-only] [--collect]
python -E tools/gen_pixelsheet.py --progress        progress sheet + GIFs of finished animations -> progress/<HHMM>_*.png
Jobs are submitted all at once (ComfyUI queues them: "queue up a ton"); --collect builds what has finished.
"""
import json
import os
import sys
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv, sys.argv = sys.argv, [sys.argv[0]]
import gen_busts as g  # noqa: E402
import gen_pixelai as gp  # noqa: E402
sys.argv = _argv

PX = os.path.join(g.ROOT, "_art", "preview", "agents", "pixelai")
SHEETS = os.path.join(PX, "sheets")
PROG = os.path.join(PX, "progress")
RES = os.path.join(g.PROJ, "resource", "enemy_pic")
FW, FH, COLS, ROWS, K = 80, 68, 14, 11, 12
CN = "controlnet-union-sdxl-1.0-promax.safetensors"
JOBS = os.path.join(SHEETS, "jobs.json")

# order (user): Natsuko, the other travelers, Gonta, then common enemies
ORDER = ["natsuko", "rensei", "gendo", "shizue", "haruki", "mitsue", "tamotsu", "sayo", "gonta", "ashigaru",
         "bandit", "ronin", "nezumi"]
SHEET = {k: v[1] for k, v in gp.CAST.items()}
SHEET.update(gonta="side_gonta.png", ashigaru="hum_ashigaru.png")
DESC = {k: v[0] for k, v in gp.CAST.items()}
DESC["gonta"] = ("1boy, huge fat muscular sumo wrestler, black hair in a topknot with a red cord, bare chest, white "
                 "mawashi belt, bare feet, broad grin, feudal japan")
DESC["ashigaru"] = ("1boy, ashigaru foot soldier, conical jingasa helmet, dark blue-grey lamellar armor, sashimono "
                    "banner flag on a pole on his back, holding a yari spear, feudal japan")
SEED = {k: 11 for k in ORDER}                  # the user's pick (s11); per-character override after picking
DENOISE, CN_STRENGTH = 0.72, 0.65


def animap(sheet):
    d = json.load(open(os.path.join(g.PROJ, "resource", "enemy_pic.json"), encoding="utf-8"))
    for v in d.values():
        if isinstance(v, dict) and (v.get("pic3d") or "").endswith("/" + sheet):
            return v.get("animap", [])
    return []


def frame(sheet, i):
    guide = os.path.join(PX, "guides", sheet)              # upright guide poses when rendered (gen_upright_guides.py)
    im = Image.open(guide if os.path.exists(guide) else os.path.join(RES, sheet)).convert("RGBA")
    c, r = i % COLS, i // COLS
    return im.crop((c * FW, r * FH, c * FW + FW, r * FH + FH))


def wf(pos, neg, seed, init_name, ctrl_name):
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": gp.PRESET["ckpt"]}},
        "2": {"class_type": "LoraLoader", "inputs": {"model": ["1", 0], "clip": ["1", 1], "lora_name": "pixel-art-xl.safetensors",
                                                    "strength_model": 1.0, "strength_clip": 1.0}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": pos, "clip": ["2", 1]}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip": ["2", 1]}},
        "5": {"class_type": "LoadImage", "inputs": {"image": init_name}},
        "6": {"class_type": "LoadImage", "inputs": {"image": ctrl_name}},
        "7": {"class_type": "ControlNetLoader", "inputs": {"control_net_name": CN}},
        "8": {"class_type": "SetUnionControlNetType", "inputs": {"control_net": ["7", 0],
                                                                 "type": "canny/lineart/anime_lineart/mlsd"}},
        "9": {"class_type": "ControlNetApplyAdvanced", "inputs": {"positive": ["3", 0], "negative": ["4", 0],
                                                                  "control_net": ["8", 0], "image": ["6", 0],
                                                                  "strength": CN_STRENGTH, "start_percent": 0.0,
                                                                  "end_percent": 0.85, "vae": ["1", 2]}},
        "10": {"class_type": "VAEEncode", "inputs": {"pixels": ["5", 0], "vae": ["1", 2]}},
        "11": {"class_type": "KSampler", "inputs": {"model": ["2", 0], "positive": ["9", 0], "negative": ["9", 1],
                                                    "latent_image": ["10", 0], "seed": seed, "steps": 28, "cfg": 6.0,
                                                    "sampler_name": "euler_ancestral", "scheduler": "normal",
                                                    "denoise": DENOISE}},
        "12": {"class_type": "VAEDecode", "inputs": {"samples": ["11", 0], "vae": ["1", 2]}},
        "13": {"class_type": "SaveImage", "inputs": {"images": ["12", 0], "filename_prefix": "rt_pixelsheet/f"}},
    }


def guides(fr):
    """(init, control) at 960x816: our frame x12 on white, the init slightly smoothed, the control its canny."""
    bg = Image.new("RGBA", fr.size, (255, 255, 255, 255))
    bg.alpha_composite(fr)
    big = bg.convert("RGB").resize((FW * K, FH * K), Image.NEAREST)
    init = big.filter(ImageFilter.GaussianBlur(3))
    e = cv2.Canny(np.asarray(big.filter(ImageFilter.GaussianBlur(1.5)).convert("L")), 40, 120)
    ctrl = Image.fromarray(e).convert("RGB")
    return init, ctrl


def pose_hint(i, am):
    for a in am:
        if a["st"] <= i < max(a["en"], a["st"] + 1):
            return a["id"]
    return ""


HINT = {"walk": "walking", "run": "running", "atk": "attacking", "damage": "hurt, recoiling", "avoid": "dodging",
        "guard": "guarding", "die": "lying defeated on the ground", "collapse": "falling down",
        "victory": "victory pose", "spell": "casting a spell", "chant": "chanting", "item": "using an item",
        "talk": "talking", "nod": "nodding", "rei": "bowing", "seiza": "kneeling in seiza", "think": "thinking",
        "surprise": "surprised", "laugh": "laughing", "_f": "front view, facing the viewer",
        "_b": "back view, from behind"}


def prompt_for(key, aid):
    style = gp.STYLE
    extra = [v for k, v in HINT.items() if k in aid]
    if aid.endswith("_f") or aid.endswith("_b"):
        style = style.replace("from side, facing right, ", "")
    if extra:
        style = style.replace("standing, ", "")
    return "%s, %s%s" % (style, DESC[key], (", " + ", ".join(extra)) if extra else "")


def load_jobs():
    return json.load(open(JOBS, encoding="utf-8")) if os.path.exists(JOBS) else {}


def submit(key, frames=None):
    os.makedirs(SHEETS, exist_ok=True)
    jobs = load_jobs()
    sheet = SHEET[key]
    am = animap(sheet)
    used = sorted({i for a in am for i in range(a["st"], max(a["en"], a["st"] + 1))})
    frames = frames or used
    n = 0
    # "front": sprite jobs go ahead of the bust queue; front jobs run newest first, so submit in reverse
    for i in reversed(frames):
        jk = "%s/%d" % (key, i)
        if jk in jobs:
            continue
        fr = frame(sheet, i)
        if not fr.getbbox():
            continue
        init, ctrl = guides(fr)
        iname = g.upload(init, "rt_ps_%s_%03d_i.png" % (key, i))
        cname = g.upload(ctrl, "rt_ps_%s_%03d_c.png" % (key, i))
        aid = pose_hint(i, am)
        w = wf(prompt_for(key, aid), gp.NEG + gp.EXTRA_NEG.get(key, ""), SEED[key], iname, cname)
        r = json.loads(g._req("/prompt", json.dumps({"prompt": w, "client_id": "rt_pixelsheet", "front": True}).encode()))
        jobs[jk] = {"pid": r["prompt_id"], "t": time.time(), "anim": aid}
        n += 1
    json.dump(jobs, open(JOBS, "w", encoding="utf-8"), indent=0)
    print("%s: %d frames submitted" % (key, n))


def fetch(pid):
    h = json.loads(g._req("/history/" + pid))
    if pid not in h:
        return None
    for node in h[pid]["outputs"].values():
        for im in node.get("images", []):
            import io
            q = "/view?filename=%s&subfolder=%s&type=%s" % (im["filename"], im["subfolder"], im["type"])
            return Image.open(io.BytesIO(g._req(q))).convert("RGB")
    return None


def post(big, ours, pal=None):
    rgba = g.key_out(big.resize((FW * K, FH * K)), holes=True)
    small = rgba.resize((FW, FH), Image.BOX)
    a = np.asarray(small).copy()
    sil = cv2.dilate((np.asarray(ours.getchannel("A")) > 0).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    alpha = (a[..., 3] > 110) & sil
    rgb = Image.fromarray(a[..., :3])
    q = rgb.quantize(palette=pal, dither=Image.NONE) if pal else rgb.quantize(colors=32, method=Image.MEDIANCUT,
                                                                                dither=Image.NONE)
    out = np.dstack([np.asarray(q.convert("RGB")), (alpha * 255).astype(np.uint8)])
    return Image.fromarray(out, "RGBA"), q


def collect(key):
    jobs = load_jobs()
    fd = os.path.join(SHEETS, "frames", key)
    os.makedirs(fd, exist_ok=True)
    sheet = SHEET[key]
    palp = os.path.join(fd, "palette.png")
    pal = Image.open(palp) if os.path.exists(palp) else None
    done = 0
    for jk, j in sorted(jobs.items(), key=lambda kv: int(kv[0].split("/")[1]) if kv[0].startswith(key + "/") else 0):
        if not jk.startswith(key + "/"):
            continue
        i = int(jk.split("/")[1])
        out = os.path.join(fd, "f%03d.png" % i)
        if os.path.exists(out):
            done += 1
            continue
        big = fetch(j["pid"])
        if big is None:
            continue
        big.save(os.path.join(fd, "big%03d.png" % i))
        sp, q = post(big, frame(sheet, i), pal)
        if pal is None:                                   # the first finished frame fixes the sheet's palette
            pal = q
            q.save(palp)
        sp.save(out)
        j["done"] = time.time()
        done += 1
    json.dump(jobs, open(JOBS, "w", encoding="utf-8"), indent=0)
    # sheet
    sh = Image.new("RGBA", (FW * COLS, FH * ROWS), (0, 0, 0, 0))
    for f in os.listdir(fd):
        if f.startswith("f") and f.endswith(".png"):
            i = int(f[1:4])
            sh.alpha_composite(Image.open(os.path.join(fd, f)).convert("RGBA"), ((i % COLS) * FW, (i // COLS) * FH))
    sh.save(os.path.join(SHEETS, "%s.png" % key))
    return done


def on_bg(im, s=4, bg=(52, 60, 52)):
    b = Image.new("RGBA", im.size, bg + (255,))
    b.alpha_composite(im)
    return b.convert("RGB").resize((im.width * s, im.height * s), Image.NEAREST)


def progress():
    os.makedirs(PROG, exist_ok=True)
    stamp = time.strftime("%H%M")
    jobs = load_jobs()
    lines = []
    for key in ORDER:
        if not any(k.startswith(key + "/") for k in jobs):
            continue
        n = collect(key)
        tot = sum(1 for k in jobs if k.startswith(key + "/"))
        lines.append((key, n, tot))
        fd = os.path.join(SHEETS, "frames", key)
        am = animap(SHEET[key])
        seen = set()
        for a in am:
            rng = list(range(a["st"], max(a["en"], a["st"] + 1)))
            if (a["st"], a["en"]) in seen or len(rng) < 2:
                continue
            fs = [os.path.join(fd, "f%03d.png" % i) for i in rng]
            gif = os.path.join(PROG, "%s_%s.gif" % (key, a["id"]))
            if all(os.path.exists(f) for f in fs) and not os.path.exists(gif):
                seen.add((a["st"], a["en"]))
                ims = []
                for i, f in zip(rng, fs):
                    ai = Image.open(f).convert("RGBA")
                    ou = frame(SHEET[key], i)
                    c = Image.new("RGB", (FW * 8 + 8, FH * 4), (30, 28, 34))
                    c.paste(on_bg(ou), (0, 0))
                    c.paste(on_bg(ai), (FW * 4 + 8, 0))
                    ims.append(c)
                ims[0].save(gif, save_all=True, append_images=ims[1:], duration=int(1000 / max(1, a["spd"])),
                            loop=0)
                ims[0].save(os.path.join(PROG, "%s_%s_%s.png" % (stamp, key, a["id"])))
        sh = os.path.join(SHEETS, "%s.png" % key)
        if os.path.exists(sh):
            on_bg(Image.open(sh).convert("RGBA"), 2).save(os.path.join(PROG, "%s_%s_sheet.png" % (stamp, key)))
    # PROGRESS.md
    done_t = sorted(j["done"] for j in jobs.values() if j.get("done"))
    rate = (len(done_t) - 1) / ((done_t[-1] - done_t[0]) / 3600) if len(done_t) > 2 and done_t[-1] > done_t[0] else 0
    md = ["# AI sprite sheets: progress (%s)" % time.strftime("%Y-%m-%d %H:%M"), "",
          "Frames/hour: %.0f. Sheets: sheets/<key>.png (not in the game). GIFs: progress/<key>_<anim>.gif "
          "(left ours, right AI)." % rate, "", "| character | frames done | of |", "|---|---|---|"]
    md += ["| %s | %d | %d |" % l for l in lines]
    p = os.path.join(PX, "PROGRESS.md")
    old = open(p, encoding="utf-8").read().split("\n## Notes", 1)[1] if os.path.exists(p) and "\n## Notes" in \
        open(p, encoding="utf-8").read() else "\n"
    open(p, "w", encoding="utf-8").write("\n".join(md) + "\n\n## Notes" + old)
    print("\n".join("%s %d/%d" % l for l in lines), "| %.0f frames/h" % rate)


def parse_frames(s):
    out = []
    for part in s.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a), int(b or a) + 1))
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--progress" in a:
        progress()
    else:
        keys = [k for k in a if k in SHEET]
        fr = parse_frames(a[a.index("--frames") + 1]) if "--frames" in a else None
        for k in keys:
            if "--collect" in a:
                print(k, collect(k))
            else:
                submit(k, fr)
