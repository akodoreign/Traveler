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

import cv2
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
    "zokujin_miner": ("1boy, male, short stout dwarf-like creature, chibi proportions, broad shoulders, big head, "
                      "big hands, craggy cracked grey stone skin like granite, glowing amber eyes, bald, short thick "
                      "legs, holding a stone pickaxe, loincloth, cave dweller", 40, False, 0.55),
    "zokujin_hunter": ("stone golem dwarf, 1boy, male, short stout dwarf-like hunter, grey granite body, no flesh, chibi proportions, broad shoulders, big head, "
                       "craggy cracked grey stone skin like granite, glowing amber eyes, holding a stone-tipped spear, "
                       "crouching, fur loincloth", 40, False, 0.55),
    "monkeys": ("japanese macaque monkey, small, long thin limbs, pink red face, grey-brown fur, short tail, "
                "crouching on all fours, holding a stolen rice ball, animal, not a bear",
                34, False, 0.5),
    "ningyo": ("feral ningyo merfolk, human torso and fish tail, pale blue-green scales, wild seaweed hair, "
               "sharp teeth, clawed hands, rising from the water on its tail", 54, False, 0.65),
    "tsuno": ("tsuno ravager, muscular horned demon beast-man warrior, two long curved horns, dark red-brown skin, "
              "bestial face with fangs, crude black armor, holding a heavy curved blade", 60, False, 0.7),
    "nukekubi": ("nukekubi, a large disembodied human head seen from the side, big pale white face clearly "
                 "visible, red glowing eyes, bared teeth, long black hair streaming behind it, no body, no neck, "
                 "floating", 34, True, 0.5),
    "onibaba": ("onibaba, a demon crone, hunched old woman with grey-blue skin, wild white hair, small horns, "
                "fangs, ragged dark kimono, holding a large kitchen knife", 54, False, 0.68),
    "hyakuhei": ("hyakuhei, a hulking mass of many dead samurai soldiers fused into one body, many arms holding "
                 "rusty spears and swords, rotten armor plates, several skull faces, undead", 62, False, 0.75),
}
FOES.update({
    "aoizame": ("a blue shark swimming, side view, fins, open jaws, fish, animal, no legs", 36, True, 0.6),
    "mujina": ("mujina, a badger spirit with a featureless smooth blank face, standing upright in a ragged brown "
               "kimono, badger tail, yokai", 52, False, 0.6),
    "ape": ("ozaru, a huge grey-furred mountain ape, gorilla-like, knuckles on the ground, red face, angry, animal",
            56, False, 0.75),
    "muck_monster": ("a shapeless swamp mud monster, dripping brown-green muck body, two glowing eyes, mud arms, "
                     "rotting reeds sticking out", 50, False, 0.7),
    "tanglevines": ("a mass of thorny writhing tangled vines and roots shaped like a monster, plant creature, no face",
                    48, False, 0.65),
    "heart_grubs": ("a cluster of fat pale red parasite grubs, maggots, worm creature, wet", 28, False, 0.5),
    "goblin_berserker": ("a frenzied green goblin berserker, big axe raised, foaming mouth, war paint, muscular "
                         "small goblin", 46, False, 0.55),
    "stinger_plant": ("a carnivorous bamboo-like plant monster with long sharp stinger spikes, plant creature",
                      52, False, 0.65),
})
NEG_PER2 = {"aoizame": ", legs, standing, anthropomorphic", "mujina": ", eyes, mouth, nose",
            "ape": ", human, clothes", "tanglevines": ", goblin, humanoid, face",
            "stinger_plant": ", lizard, animal", "muck_monster": ", lizard, pink"}
NEG_X = (", facing left, from behind, back view, multiple characters, background scenery, text, slender, "
         "tall, thin, alien")
NEG_PER = {"zokujin_miner": ", 1girl, woman, female, breasts, goblin, green skin",
           "zokujin_hunter": ", 1girl, woman, female, breasts, goblin, green skin",
           "tsuno": ", 1girl, woman", "hyakuhei": ", 1girl, woman", "ningyo": ", legs, feet"}


HUMAN_BASES = ("hum_",)          # human-rig foes: drawn through gen_human_enemies + pixeldrive, not here


def foe_def(key):
    """FOES entry, or one derived from tools/new_foes.py (name + description; size and scale from the base sheet)."""
    if key in FOES:
        return FOES[key]
    ent = next(f for f in new_foes.NEW_FOES if f[2] == key)
    j = json.load(open(os.path.join(RES, "enemy_pic.json"), encoding="utf-8"))
    base = j[ent[4]]
    sc = float(base.get("scale", 0.6))
    height = int(min(62, max(30, 62 * sc / 0.75)))
    flying = any(w in ent[13].lower() for w in ("flies", "flying", "wings", "hover"))
    return ("%s, %s, monster, creature" % (ent[3], ent[13]), height, flying, sc)


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
    al_ = (np.asarray(a)[..., 3] > 40).astype(np.uint8)        # keep the main figure: drop stray small sprites
    n_, lbl, st_, _ = cv2.connectedComponentsWithStats(cv2.dilate(al_, np.ones((9, 9), np.uint8)), connectivity=8)
    if n_ > 2:
        big_k = 1 + int(np.argmax(st_[1:, cv2.CC_STAT_AREA]))
        keep = (lbl == big_k) & (al_ > 0)
        arr = np.asarray(a).copy()
        arr[~keep] = 0
        a = Image.fromarray(arr, "RGBA")
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
        prompt, height, flying, _ = foe_def(key)
        od = os.path.join(WORK, key)
        os.makedirs(od, exist_ok=True)
        pos = gp.STYLE.replace("standing, ", "" if flying else "standing, ") + ", " + prompt
        neg = gp.NEG + NEG_X + NEG_PER.get(key, "") + NEG_PER2.get(key, "")
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
    _, height, flying, scale = foe_def(key)
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


# ---- silhouette + img2img (lead 2026-11-15): for foes text-to-image keeps drawing as something else (Nukekubi as a
# head on a stick, the plant monsters as girls / lizards): a rough shape drawn here fixes the composition, the model
# only paints it (init = the blurred shape, canny control from it, denoise 0.55-0.7).
def sil_nukekubi():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k in range(9):                                    # hair streaming back (left) in long strands
        y = 22 + k * 3
        d.line([(38, y - 4), (24, y), (10, y + 2 + (k % 3)), (2, y + 6)], fill=(20, 18, 24, 255), width=2)
    d.ellipse([30, 14, 58, 44], fill=(232, 226, 214, 255))     # big pale face, side view, looking right
    d.ellipse([28, 12, 50, 30], fill=(24, 20, 26, 255))        # hair cap
    d.ellipse([46, 24, 51, 28], fill=(220, 40, 40, 255))       # red eye
    d.polygon([(50, 36), (58, 34), (55, 40)], fill=(150, 30, 30, 255))   # open mouth
    d.line([(51, 37), (56, 36)], fill=(250, 250, 250, 255))   # teeth
    return im


def sil_plant(stingers):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    gx = H - GROUND
    d.ellipse([22, gx - 8, 58, gx + 1], fill=(70, 50, 30, 255))          # root mound
    if stingers:                                            # bamboo-like stalks with stinger tips, leaning right
        for x0, h_, lean in ((30, 50, 6), (38, 58, 10), (46, 46, 14), (34, 36, 4), (52, 34, 12)):
            d.line([(x0, gx - 4), (x0 + lean, gx - h_)], fill=(110, 140, 60, 255), width=3)
            for t in range(1, 4):
                y = gx - 4 - h_ * t // 4
                d.line([(x0 + lean * t // 4 - 2, y), (x0 + lean * t // 4 + 2, y)], fill=(70, 90, 40, 255))
            tx, ty = x0 + lean, gx - h_
            d.polygon([(tx - 2, ty + 2), (tx + 6, ty - 6), (tx + 2, ty + 3)], fill=(220, 210, 160, 255))
    else:                                                   # a writhing knot of thorny vines, reaching right
        import math
        for k in range(7):
            pts = []
            for t in range(14):
                a = t / 13.0
                x = 26 + a * 34 + 6 * math.sin(a * 6 + k)
                y = gx - 6 - a * (20 + 4 * k) * 0.9 + 5 * math.cos(a * 5 + k * 1.3)
                pts.append((x, y))
            d.line(pts, fill=(60 + 8 * k, 90 + 6 * k, 40, 255), width=3)
            for (x, y) in pts[3::3]:
                d.line([(x, y), (x + 3, y - 3)], fill=(190, 170, 120, 255))
    return im


SILS = {"nukekubi": sil_nukekubi, "tanglevines": lambda: sil_plant(False), "stinger_plant": lambda: sil_plant(True)}
SIL_PROMPT = {"nukekubi": "nukekubi, a floating disembodied human head in side view, pale face, red eyes, open mouth "
                          "with teeth, long black hair streaming behind it, yokai, no body",
              "tanglevines": "fudoshi, a monster made of a writhing knot of thorny green vines and roots, plant creature, "
                             "no face, no human",
              "stinger_plant": "takesasu, a monstrous bamboo plant with sharp stinger spikes at the tips of its stalks, "
                               "plant creature, no face, no animal"}


def draw_sil(key, seed0=71, n=4):
    _, height, flying, _ = foe_def(key)
    od = os.path.join(WORK, key)
    os.makedirs(od, exist_ok=True)
    s = SILS[key]()
    s.save(os.path.join(od, "silhouette.png"))
    white = Image.new("RGBA", s.size, (255, 255, 255, 255))
    white.alpha_composite(s)
    from PIL import ImageFilter
    init = pd.pa.up(white.convert("RGB")).filter(ImageFilter.GaussianBlur(3))
    ctrl = pd.pa.control(s)
    pos = gp.STYLE.replace("standing, ", "") + ", " + SIL_PROMPT[key]
    neg = gp.NEG + NEG_X + NEG_PER.get(key, "") + NEG_PER2.get(key, "") + ", girl, woman, person, lizard"
    tiles = []
    for k in range(n):
        den = (0.55, 0.62, 0.68, 0.72)[k % 4]
        big = pd.submit_wait(pos, neg, [seed0 * 100 + k], init, ctrl, den, "foesil_%s_%d" % (key, k))[0]
        big.save(os.path.join(od, "big_%d.png" % k))
        fr = to_frame(big, height, flying)
        if fr:
            fr.save(os.path.join(od, "cand_%d.png" % k))
            tiles.append((k, fr))
        print(time.strftime("%H:%M"), key, "silhouette candidate", k, flush=True)
    sheet = Image.new("RGB", (W * 3 * (len(tiles) + 1), H * 3 + 14), (110, 150, 110))
    d = ImageDraw.Draw(sheet)
    f = s.resize((W * 3, H * 3), Image.NEAREST)
    sheet.paste(f, (0, 14), f)
    d.text((3, 2), "silhouette", fill=(255, 255, 0))
    for i, (k, fr) in enumerate(tiles):
        f = fr.resize((W * 3, H * 3), Image.NEAREST)
        sheet.paste(f, ((i + 1) * W * 3, 14), f)
        d.text(((i + 1) * W * 3 + 3, 2), "%s cand %d" % (key, k), fill=(255, 255, 0))
    sheet.save(os.path.join(od, "contact.png"))

if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "draw":
        seed = int(a[a.index("--seed") + 1]) if "--seed" in a else 31
        allk = [f[2] for f in new_foes.NEW_FOES]
        keys = [k for k in a[1:] if k in allk] or list(FOES)
        draw(keys, seed)
    elif a and a[0] == "sil":
        for k in [k for k in a[1:] if k in SILS] or list(SILS):
            draw_sil(k)
    elif a and a[0] == "install":
        install(a[1], int(a[2]), "--flip" in a)
