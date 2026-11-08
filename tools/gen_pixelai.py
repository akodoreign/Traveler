"""Pixel-art sprites with ComfyUI: the locked "s11" style (user, 2026-11-08: "i like waillustrioussdxl_s11").
Preset: checkpoint waiIllustriousSDXL_v170 + LoRA pixel-art-xl (nerijs, strength 1.0 model/clip), euler_ancestral,
normal scheduler, 28 steps, CFG 6.0, 1024x1024, prompt = STYLE + character description, NEG below; post: key out the
white background, crop, BOX-downscale to the sprite height, 24-colour median-cut palette, hard alpha
(pixelai_test.to_sprite). Seed 11 was the user's pick; other seeds are tried per character and the best is picked.
python -E tools/gen_pixelai.py [key ...] [--seeds 11,12,13]   -> _art/preview/agents/pixelai/cast/<key>_s<seed>.png
python -E tools/gen_pixelai.py --sheet "natsuko:13,rensei:11,..."   -> cast_s11.png (ours vs AI, 1x and 4x)
Nothing in the game is changed.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv, sys.argv = sys.argv, [sys.argv[0]]
import pixelai_test as px  # noqa: E402
g = px.g
sys.argv = _argv
from PIL import Image, ImageDraw  # noqa: E402

PRESET = dict(ckpt="waiIllustriousSDXL_v170.safetensors", lora=1.0, steps=28, cfg=6.0, size=1024, colors=24)
STYLE = px.STYLE
NEG = px.NEG + ", nude, topless, extra people, two people, duplicate"
OUT = os.path.join(px.OUT, "cast")

# key: (description, our sheet in enemy_pic for the comparison, sprite height)
CAST = {
    "natsuko": ("1girl, young woman samurai scout, (dark skin, brown skin:1.2), dark brown hair, long ponytail, red "
                "hachimaki headband, (full dark blue-grey lacquered samurai armor:1.3), lamellar do chest armor with "
                "red lacing, sode shoulder plates, kote armored sleeves, suneate shin guards, holding a long yari "
                "spear, feudal japan", "trav_natsuko.png", 56),
    "rensei": ("1boy, young samurai duelist, fair skin, long white hair with a topknot, pale blue haori over a white "
               "kimono, hakama, katana at the hip, hand on the sword hilt, feudal japan", "trav_rensei.png", 58),
    "gendo": ("1boy, young magistrate, short black hair, round glasses, dark green haori over a sage-green kimono, "
              "hakama, holding a long wooden bo staff, jitte at the belt, feudal japan", "trav_gendo.png", 58),
    "shizue": ("1girl, young woman samurai strategist, brown bob hair, red hachimaki headband, gold lacquered "
               "lamellar armor with red lacing over a golden-yellow kimono, war fan at the belt, katana, feudal japan",
               "trav_shizue.png", 54),
    "haruki": ("1boy, young shugenja priest, spiky dark brown hair, orange robe with a wave pattern, red-orange hakama, "
               "holding a shakujo staff with rings, feudal japan", "trav_haruki.png", 52),
    "mitsue": ("1girl, young woman ninja agent, long black hair, crimson kimono with a black diamond pattern, dark red "
               "cloth half-mask over the mouth, holding a tanto dagger in reverse grip, feudal japan",
               "trav_mitsue.png", 54),
    "tamotsu": ("1boy, stocky jovial man, brown hair topknot, full brown beard, purple coat with a white fur collar "
                "over an off-white kimono, yumi longbow, quiver of arrows, feudal japan", "trav_tamotsu.png", 56),
    "sayo": ("1girl, young woman ronin herbalist, tan skin, freckles, long brown hair, jingasa travel hat, worn brown "
             "kimono, green obi, herb basket on the back, plain katana, feudal japan", "trav_sayo.png", 52),
    "bandit": ("1boy, road bandit, scruffy black hair, headband, stubble, ragged brown clothes, rope belt, holding a "
               "rusty katana, mean grin, feudal japan", "hum_road_bandit.png", 54),
    "ronin": ("1boy, hungry ronin, unkempt topknot, thin gaunt face, stubble, worn faded grey kimono and hakama, "
              "holding a katana, feudal japan", "hum_hungry_ronin.png", 56),
    "nezumi": ("nezumi, anthropomorphic rat warrior, realistic rat head, long snout, small rounded ears, brown fur, "
               "red headband, crude hide armor, holding a bamboo spear, long tail, no humans, feudal japan",
               "nezumi_warrior.png", 46),
}
EXTRA_NEG = {"nezumi": ", cartoon, mouse, mickey, chibi, human"}


def gen(key, seeds):
    os.makedirs(OUT, exist_ok=True)
    desc, _, hgt = CAST[key]
    for s in seeds:
        out = os.path.join(OUT, "%s_s%d.png" % (key, s))
        if os.path.exists(out):
            continue
        t0 = time.time()
        big = g.queue(px.wf("%s, %s" % (STYLE, desc), NEG + EXTRA_NEG.get(key, ""), s, PRESET["ckpt"],
                            lora=PRESET["lora"], steps=PRESET["steps"], cfg=PRESET["cfg"]))[0]
        big.save(os.path.join(OUT, "big_%s_s%d.png" % (key, s)))
        sp, _ = px.to_sprite(big, hgt, colors=PRESET["colors"])
        sp.save(out)
        print(key, s, "%.1fs" % (time.time() - t0))


def ours_frame(sheet):
    p = os.path.join(px.RES, sheet)
    if not os.path.exists(p):
        return None
    return px.in_frame(px.ours(sheet).crop(px.ours(sheet).getbbox() or (0, 0, px.FW, px.FH)))


def candidates_sheet(keys, seeds):
    """All candidates per character in a row (4x), for picking."""
    rows = [(k, [Image.open(os.path.join(OUT, "%s_s%d.png" % (k, s))) for s in seeds]) for k in keys]
    sh = Image.new("RGB", (len(seeds) * px.FW * 3 + 120, len(rows) * px.FH * 3), (30, 28, 34))
    d = ImageDraw.Draw(sh)
    for r, (k, ims) in enumerate(rows):
        d.text((4, r * px.FH * 3 + 4), k, fill=(255, 255, 0))
        for i, im in enumerate(ims):
            sh.paste(px.on_bg(px.in_frame(im), 3), (120 + i * px.FW * 3, r * px.FH * 3))
            d.text((124 + i * px.FW * 3, r * px.FH * 3 + 4), "s%d" % seeds[i], fill=(255, 80, 80))
    sh.save(os.path.join(px.OUT, "cast_candidates.png"))


def final_sheet(picks):
    """picks {key: file}: ours vs AI, 1x and 4x, 3 characters per row."""
    cells = []
    for k, f in picks.items():
        cells.append((k, ours_frame(CAST[k][1]), px.in_frame(Image.open(f))))
    cw = (px.FW * 4 + px.FW + 20) * 2 + 20
    cols = 2
    rows = (len(cells) + cols - 1) // cols
    sh = Image.new("RGB", (cw * cols, rows * (px.FH * 4 + 30)), (30, 28, 34))
    d = ImageDraw.Draw(sh)
    f = g.label_font(16)
    for i, (k, o, a) in enumerate(cells):
        x, y = (i % cols) * cw, (i // cols) * (px.FH * 4 + 30)
        for j, fr in enumerate((o, a)):
            if fr is None:
                continue
            xx = x + j * (px.FW * 5 + 20)
            sh.paste(px.on_bg(fr, 1), (xx + 4, y + 4))
            sh.paste(px.on_bg(fr, 4), (xx + px.FW + 10, y + 4))
        d.text((x + 4, y + px.FH * 4 + 8), "%s: ours | AI s11 style" % k, fill=(240, 230, 200), font=f)
    sh.save(os.path.join(px.OUT, "cast_s11.png"))
    print("cast_s11.png")


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--sheet" in a:
        spec = a[a.index("--sheet") + 1]
        picks = {}
        for part in spec.split(","):
            k, v = part.split(":")
            picks[k] = v if os.path.sep in v or "/" in v else os.path.join(OUT, "%s_s%s.png" % (k, v))
        final_sheet(picks)
    else:
        seeds = [int(s) for s in a[a.index("--seeds") + 1].split(",")] if "--seeds" in a else [11, 12, 13]
        keys = [k for k in a if k in CAST] or list(CAST)
        for k in keys:
            gen(k, seeds)
        candidates_sheet(keys, seeds)
