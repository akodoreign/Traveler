"""Pixel-art sprites with ComfyUI: a feasibility test (2026-11-08; nothing in the game is changed).
Checkpoint (Illustrious / NoobAI, already installed) + the Pixel-Art-XL LoRA (nerijs, models/loras/pixel-art-xl.safetensors)
-> 1024x1024 full-body side view on a flat background -> key out -> crop -> downscale to the sprite's pixel height
(box filter) -> palette quantize -> hard alpha. Compares with our procedural sprites (enemy_pic, 80x68 frames).
python -E tools/pixelai_test.py singles        sheet singles.png (+ per-checkpoint picks)
python -E tools/pixelai_test.py anim           Natsuko idle (8) + attack (4) by img2img from frame 0 -> GIFs
Output: _art/preview/agents/pixelai/
"""
import os
import sys
import time

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv, sys.argv = sys.argv, [sys.argv[0]]
import gen_busts as g  # noqa: E402
sys.argv = _argv

OUT = os.path.join(g.ROOT, "_art", "preview", "agents", "pixelai")
RES = os.path.join(g.PROJ, "resource", "enemy_pic")
LORA = "pixel-art-xl.safetensors"
CKPTS = ["waiIllustriousSDXL_v170.safetensors", "NoobAI-XL-v1.1.safetensors"]
FW, FH = 80, 68

STYLE = ("pixel art, 16-bit jrpg battle sprite, game sprite, full body, from side, facing right, standing, "
         "small character, whole body visible, feet visible, simple background, white background, solo, "
         "masterpiece, best quality")
NEG = ("3d, realistic, photo, blurry, gradient, scenery, detailed background, cropped, out of frame, multiple views, "
       "text, watermark, signature, frame, border, close-up, portrait, upper body, nsfw")
CAST = {
    "natsuko": ("1girl, young woman samurai scout, tan skin, dark brown hair, long ponytail, red hachimaki headband, "
                "dark blue-grey lamellar armor with red lacing, slate-blue kimono, one shoulder guard, holding a long "
                "yari spear, feudal japan", "trav_natsuko.png", 56),
    "gonta": ("1boy, huge fat muscular sumo wrestler, black hair in a topknot with a red cord, bare chest, white "
              "mawashi belt, bare feet, broad grin, feudal japan", "side_gonta.png", 60),
    "ashigaru": ("1boy, ashigaru foot soldier, conical jingasa helmet, dark blue-grey lamellar armor, sashimono banner "
                 "flag on a pole on his back, holding a yari spear, feudal japan", "hum_ashigaru.png", 52),
}


def wf(pos, neg, seed, ckpt, w=1024, h=1024, lora=1.0, image=None, denoise=1.0, steps=28, cfg=6.0):
    n = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ckpt}},
        "2": {"class_type": "LoraLoader", "inputs": {"model": ["1", 0], "clip": ["1", 1], "lora_name": LORA,
                                                    "strength_model": lora, "strength_clip": lora}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": pos, "clip": ["2", 1]}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip": ["2", 1]}},
        "6": {"class_type": "KSampler", "inputs": {"model": ["2", 0], "positive": ["3", 0], "negative": ["4", 0],
                                                   "latent_image": ["5", 0], "seed": seed, "steps": steps,
                                                   "cfg": cfg, "sampler_name": "euler_ancestral",
                                                   "scheduler": "normal", "denoise": denoise}},
        "7": {"class_type": "VAEDecode", "inputs": {"samples": ["6", 0], "vae": ["1", 2]}},
        "8": {"class_type": "SaveImage", "inputs": {"images": ["7", 0], "filename_prefix": "rt_pixelai/f"}},
    }
    if image:
        n["9"] = {"class_type": "LoadImage", "inputs": {"image": image}}
        n["5"] = {"class_type": "VAEEncode", "inputs": {"pixels": ["9", 0], "vae": ["1", 2]}}
    else:
        n["5"] = {"class_type": "EmptyLatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}}
    return n


def to_sprite(im, height, colors=24, bbox=None):
    """Big render -> sprite: key out, crop to the figure (or a given bbox), box-downscale to `height`, quantize,
    hard alpha. Returns (sprite RGBA, bbox used)."""
    rgba = g.key_out(im, holes=True)
    a = np.asarray(rgba.getchannel("A"))
    if bbox is None:
        ys, xs = np.nonzero(a > 128)
        bbox = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    c = rgba.crop(bbox)
    k = height / c.height
    sm = c.resize((max(1, round(c.width * k)), height), Image.BOX)
    arr = np.asarray(sm).copy()
    alpha = arr[..., 3] > 110
    rgb = Image.fromarray(arr[..., :3])
    q = rgb.quantize(colors=colors, method=Image.MEDIANCUT, dither=Image.NONE).convert("RGB")
    out = np.dstack([np.asarray(q), (alpha * 255).astype(np.uint8)])
    return Image.fromarray(out, "RGBA"), bbox


def in_frame(sp):
    """Place a sprite in an 80x68 frame, feet on the bottom row, centred."""
    f = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
    s = sp
    if s.width > FW or s.height > FH:
        s = s.copy()
        s.thumbnail((FW, FH), Image.NEAREST)
    f.alpha_composite(s, ((FW - s.width) // 2, FH - s.height))
    return f


def ours(sheet):
    im = Image.open(os.path.join(RES, sheet)).convert("RGBA")
    return im.crop((0, 0, FW, FH))


def on_bg(im, scale, bg=(52, 60, 52)):
    b = Image.new("RGBA", im.size, bg + (255,))
    b.alpha_composite(im)
    return b.convert("RGB").resize((im.width * scale, im.height * scale), Image.NEAREST)


def singles():
    os.makedirs(OUT, exist_ok=True)
    rows, times = [], []
    for key, (desc, sheet, hgt) in CAST.items():
        row = [("ours", in_frame(ours(sheet)))]
        for ck in CKPTS:
            for seed in (11, 12):
                t0 = time.time()
                big = g.queue(wf("%s, %s" % (STYLE, desc), NEG, seed, ck))[0]
                times.append(time.time() - t0)
                tag = "%s_%s_s%d" % (key, ck.split("_")[0].split("-")[0], seed)
                big.save(os.path.join(OUT, "big_%s.png" % tag))
                sp, _ = to_sprite(big, hgt)
                sp.save(os.path.join(OUT, "sprite_%s.png" % tag))
                row.append((tag.split("_", 1)[1], in_frame(sp)))
        rows.append((key, row))
    # sheet: per character one row; each cell 1x and 4x
    cw = FW * 4 + FW + 30
    sh = Image.new("RGB", (cw * 5, len(rows) * (FH * 4 + 30)), (30, 28, 34))
    d = ImageDraw.Draw(sh)
    f = g.label_font(16)
    for r, (key, row) in enumerate(rows):
        y = r * (FH * 4 + 30)
        for i, (lb, fr) in enumerate(row):
            x = i * cw
            sh.paste(on_bg(fr, 1), (x + 4, y + 4))
            sh.paste(on_bg(fr, 4), (x + FW + 14, y + 4))
            d.text((x + 4, y + FH * 4 + 8), "%s %s" % (key, lb), fill=(240, 230, 200), font=f)
    sh.save(os.path.join(OUT, "singles.png"))
    print("singles.png; %.1f s per image (1024x1024, 28 steps)" % (sum(times) / len(times)))


def anim(ck=CKPTS[0], seed=12):
    """Idle: frame 0 shifted (breathing bob) and re-rendered by img2img at low denoise; attack: prompt pose changes
    by img2img at higher denoise. Shows how much the model drifts between frames."""
    desc, sheet, hgt = CAST["natsuko"]
    tag = "natsuko_%s_s%d" % (ck.split("_")[0].split("-")[0], seed)
    p0 = os.path.join(OUT, "big_%s.png" % tag)
    base = Image.open(p0).convert("RGB") if os.path.exists(p0) else g.queue(wf("%s, %s" % (STYLE, desc), NEG, seed,
                                                                                 ck))[0]
    _, bbox = to_sprite(base, hgt)
    bbox = (bbox[0] - 40, bbox[1] - 60, bbox[2] + 40, bbox[3])     # one crop for every frame (no jitter from it)
    frames, times = [], []
    bob = [0, 2, 4, 6, 6, 4, 2, 0]
    for i, dy in enumerate(bob):
        src = Image.new("RGB", base.size, (255, 255, 255))
        top = base.crop((0, 0, base.width, bbox[3] - 120))           # upper body sinks dy px, legs stay
        src.paste(base, (0, 0))
        src.paste(top, (0, dy * 4))
        name = g.upload(src, "rt_pixelai_idle_%d.png" % i)
        t0 = time.time()
        im = g.queue(wf("%s, %s" % (STYLE, desc), NEG, seed, ck, image=name, denoise=0.35))[0]
        times.append(time.time() - t0)
        frames.append(to_sprite(im, hgt, bbox=bbox)[0])
    att = ["holding the yari ready, crouching", "pulling the yari back, winding up",
           "lunging forward, thrusting the yari straight forward, attack", "recovering after the thrust"]
    aframes = []
    name0 = g.upload(base, "rt_pixelai_base.png")
    for i, a in enumerate(att):
        t0 = time.time()
        im = g.queue(wf("%s, %s, %s" % (STYLE.replace("standing, ", ""), desc, a), NEG, seed, ck, image=name0,
                        denoise=0.6))[0]
        times.append(time.time() - t0)
        aframes.append(to_sprite(im, hgt, bbox=bbox)[0])
    for nm, fs, ms in (("idle", frames, 150), ("attack", aframes, 220)):
        W = max(f.width for f in fs)
        H = max(f.height for f in fs)
        big = []
        for fr in fs:
            c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            c.alpha_composite(fr, ((W - fr.width) // 2, H - fr.height))
            big.append(on_bg(c, 4))
        big[0].save(os.path.join(OUT, "natsuko_%s.gif" % nm), save_all=True, append_images=big[1:], duration=ms,
                    loop=0)
        strip = Image.new("RGB", (W * 4 * len(big), H * 4))
        for i, b in enumerate(big):
            strip.paste(b, (i * W * 4, 0))
        strip.save(os.path.join(OUT, "natsuko_%s_strip.png" % nm))
    print("anim done; %.1f s per frame (img2img)" % (sum(times) / len(times)))


if __name__ == "__main__":
    a = sys.argv[1:] or ["singles"]
    if "singles" in a:
        singles()
    if "anim" in a:
        anim()
