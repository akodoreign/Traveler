"""Drawn art for the new foes' PLACEHOLDER sprites (tools/new_foes.py, EP2600-EP2637; lead 2026-11-14: "queue proper
sheets for them ... the ones that read worst as recolours first"). Monster-style sheets like gen_monsters.py: one idle
figure, a 1-px breathing bob (4 idle frames), then gen_enemy_art.animate builds the attack and hurt rows. Enemies face
right (toward the party).

  python -E tools/gen_foe_art.py draw [key ...]          txt2img candidates (ComfyUI, the pixelai preset) ->
                                                          _art/preview/agents/foe_art/<key>/cand_<n>.png + contact.png
  python -E tools/gen_foe_art.py install KEY N [--flip]  candidate N (mirrored if it faces left) -> foe_<key>.png,
                                                          enemy_pic.json entry (memo no longer PLACEHOLDER, so
                                                          gen_placeholder_foes.py leaves it), then run gen_portraits
Candidates are picked by eye (facing right, whole figure, reads as the creature); a rejected key is simply drawn again
with new seeds (draw KEY --seed N)."""
import json
import os
import sys
import time

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv, sys.argv = sys.argv, [sys.argv[0]]
import gen_pixeldrive as pd  # noqa: E402
import gen_enemy_art as ea  # noqa: E402
import new_foes  # noqa: E402
sys.argv = _argv
from atomic_io import save_png  # noqa: E402

g, gp = pd.g, pd.gp
ROOT = os.path.normpath(os.path.join(HERE, ".."))
RES = os.path.join(ROOT, "_tools", "rpgcobo-tool", "project", "resource")
WORK = os.path.join(ROOT, "_art", "preview", "agents", "foe_art")
W, H, GROUND = 80, 68, 3               # idle frame (animate pads it to 96 wide: the 480x204 monster sheets)

# key: (prompt, figure height in px of the 68-px frame, flying, scale in battle)
FOES = {
    "zokujin_miner": ("small stocky stone-skinned humanoid, grey rocky skin like granite, glowing amber eyes, bald, "
                      "short legs, holding a stone pick, loincloth, cave dweller, not a goblin", 40, False, 0.55),
    "zokujin_hunter": ("small stocky stone-skinned humanoid hunter, grey rocky granite skin, glowing amber eyes, "
                       "holding a stone-tipped spear, crouching, fur loincloth, not a goblin", 40, False, 0.55),
    "monkeys": ("three small brown macaque monkeys huddled together, red faces, one holding a stolen rice ball",
                34, False, 0.5),
    "ningyo": ("feral ningyo merfolk, human torso and fish tail, pale blue-green scales, wild seaweed hair, "
               "sharp teeth, clawed hands, rising from the water on its tail", 54, False, 0.65),
    "tsuno": ("tsuno ravager, muscular horned demon beast-man warrior, two long curved horns, dark red-brown skin, "
              "bestial face with fangs, crude black armor, holding a heavy curved blade", 60, False, 0.7),
    "nukekubi": ("nukekubi, a flying disembodied human head with very long black hair streaming behind it, pale "
                 "face, glowing eyes, bared teeth, no body, floating in the air", 34, True, 0.5),
    "onibaba": ("onibaba, a demon crone, hunched old woman with grey-blue skin, wild white hair, small horns, "
                "fangs, ragged dark kimono, holding a large kitchen knife", 54, False, 0.68),
    "hyakuhei": ("hyakuhei, a hulking mass of many dead samurai soldiers fused into one body, many arms holding "
                 "rusty spears and swords, rotten armor plates, several skull faces, undead", 62, False, 0.75),
}
NEG_X = ", facing left, from behind, back view, multiple characters, background scenery, text"


def wf_txt2img(pos, neg, seed):
    P = gp.PRESET
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": P["ckpt"]}},
        "2": {"class_type": "LoraLoader", "inputs": {"model": ["1", 0], "clip": ["1", 1],
                                                     "lora_name": "pixel-art-xl.safetensors",
                                                     "strength_model": P["lora"], "strength_clip": P["lora"]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": pos, "clip": ["2", 1]}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip": ["2", 1]}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 1024, "batch_size": 1}},
        "11": {"class_type": "KSampler", "inputs": {"model": ["2", 0], "positive": ["3", 0], "negative": ["4", 0],
                                                    "latent_image": ["5", 0], "seed": seed, "steps": P["steps"],
                                                    "cfg": P["cfg"], "sampler_name": "euler_ancestral",
                                                    "scheduler": "normal", "denoise": 1.0}},
        "12": {"class_type": "VAEDecode", "inputs": {"samples": ["11", 0], "vae": ["1", 2]}},
        "13": {"class_type": "SaveImage", "inputs": {"images": ["12", 0], "filename_prefix": "rt_foeart/f"}},
    }


def run(pos, neg, seed):
    pid = pd.post_job(wf_txt2img(pos, neg, seed))
    while True:
        st, im = pd.job_state(pid)
        if st == "done":
            return im
        if st in ("lost", "error"):
            pid = pd.post_job(wf_txt2img(pos, neg, seed))
        time.sleep(2)


def to_frame(big, height, flying, flip=False, colors=24):
    """1024 AI image -> 80x68 RGBA idle frame: key out the white background, crop, scale to the figure height,
    quantize, outline-dark edge kept, standing on the ground line (or hovering when flying)."""
    a = g.key_out(big.convert("RGB"), holes=True)
    bb = a.getbbox()
    if not bb:
        return None
    a = a.crop(bb)
    s = height / a.size[1]
    w = max(1, int(round(a.size[0] * s)))
    if w > W - 4:
        s = (W - 4) / a.size[0]
        w = W - 4
    h = max(1, int(round(a.size[1] * s)))
    small = a.resize((w, h), Image.BOX)
    al = np.asarray(small)[..., 3] > 110
    rgb = small.convert("RGB").quantize(colors, method=Image.Quantize.MEDIANCUT).convert("RGB")
    px = np.dstack([np.asarray(rgb), (al * 255).astype(np.uint8)])
    fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    y = H - GROUND - h - (10 if flying else 0)
    fr.paste(Image.fromarray(px, "RGBA"), ((W - w) // 2, max(0, y)))
    if flip:
        fr = fr.transpose(Image.FLIP_LEFT_RIGHT)
    return fr


def draw(keys, seed0=31, n=4):
    for key in keys:
        prompt, height, flying, _ = FOES[key]
        od = os.path.join(WORK, key)
        os.makedirs(od, exist_ok=True)
        pos = gp.STYLE.replace("standing, ", "" if flying else "standing, ") + ", " + prompt
        neg = gp.NEG + NEG_X
        tiles = []
        for k in range(n):
            big = run(pos, neg, seed0 * 100 + k)
            big.save(os.path.join(od, "big_%d.png" % k))
            fr = to_frame(big, height, flying)
            if fr:
                fr.save(os.path.join(od, "cand_%d.png" % k))
                tiles.append((k, fr))
            print(time.strftime("%H:%M"), key, "candidate", k, flush=True)
        sheet = Image.new("RGB", (W * 3 * len(tiles), H * 3 + 14), (110, 150, 110))
        d = ImageDraw.Draw(sheet)
        for i, (k, fr) in enumerate(tiles):
            f = fr.resize((W * 3, H * 3), Image.NEAREST)
            sheet.paste(f, (i * W * 3, 14), f)
            d.text((i * W * 3 + 3, 2), "%s cand %d" % (key, k), fill=(255, 255, 0))
        sheet.save(os.path.join(od, "contact.png"))


def install(key, n, flip):
    ent = next(f for f in new_foes.NEW_FOES if f[2] == key)
    ep, name = ent[1], ent[3]
    _, height, flying, scale = FOES[key]
    big = Image.open(os.path.join(WORK, key, "big_%d.png" % n))
    base = to_frame(big, height, flying, flip)
    frames = [base]
    for dy in (1, 1, 0):                                   # breathing bob, like the gen_bossart idle
        f = Image.new("RGBA", base.size, (0, 0, 0, 0))
        f.paste(base, (0, -dy), base)
        frames.append(f)
    if flying:                                             # a hover: up 1, up 2, up 1
        frames = [base] + [Image.new("RGBA", base.size, (0, 0, 0, 0)) for _ in range(3)]
        for f, dy in zip(frames[1:], (1, 2, 1)):
            f.paste(base, (0, -dy), base)
    sheet, (cols, rows), animap = ea.animate(frames)
    fname = "foe_%s.png" % key
    save_png(sheet, os.path.join(RES, "enemy_pic", fname))
    jp = os.path.join(RES, "enemy_pic.json")
    j = json.load(open(jp, encoding="utf-8"))
    e = j[ep]
    e.update({"pic3d": "/resource/enemy_pic/%s" % fname, "aniuv": [cols, rows], "animap": animap, "flipx": False,
              "scale": scale, "gndpos": [0.5, (GROUND - 1) / H], "atkpos": [0.8, 0.5], "cntpos": [0.5, 0.5],
              "memo": "AI foe art (tools/gen_foe_art.py, candidate %d%s)" % (n, ", mirrored" if flip else "")})
    tmp = jp + ".tmp"
    json.dump(j, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")
    os.replace(tmp, jp)
    print("installed", key, ep, name, fname)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "draw":
        seed = int(a[a.index("--seed") + 1]) if "--seed" in a else 31
        keys = [k for k in a[1:] if k in FOES] or list(FOES)
        draw(keys, seed)
    elif a and a[0] == "install":
        install(a[1], int(a[2]), "--flip" in a)
