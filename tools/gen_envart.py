"""Environment art queue (user 2026-11-15: "que up on my graphics card to generate all the various terrain, house
(japanese house / castles), Animated grass, animated water, More fit together peices to get rid of the block style
building look, walking paths, Inside house furnashings and set parts. Set that up to que next after the current
items").

The maps are voxel BlockWorlds (palette-coloured blocks, not image textures), so painted art goes into them the HD-2D
way: pixel-art sprites standing in the 3D scene, like the characters and the existing props. Every CATALOG item is
drawn as 4 txt2img candidates (ComfyUI, the same pixel-art preset as the sprite sheets), keyed out, cropped, scaled to
its in-game height (the travelers are ~60 px tall) and quantized. Animated items get a 4-frame strip built from the
drawn base, so every frame is the same drawing: sway (grass, reeds, banners), shimmer (still water), flow (falls,
streams), flicker (fire, lamps), bob (floating things).

  python -E tools/gen_envart.py run [--log FILE] [--now]   wait until the sprite-sheet queues (gen_pixeldrive,
                                                              pixelai_redo) are finished, then draw every item not
                                                              drawn yet (resumable: finished candidates are skipped)
  python -E tools/gen_envart.py draw KEY [KEY ...]           draw those items now (no waiting)
  python -E tools/gen_envart.py contact                      rebuild the per-category contact sheets
Output: _art/envart/<category>/<key>/cand_<n>.png (+ anim_<n>.png strip and anim_<n>.gif), contact_<category>.png,
DONE marker _art/envart/<category>/<key>/done. Picking candidates and placing them in maps is a later, by-eye step."""
import glob
import os
import sys
import time
import zlib

import numpy as np
import psutil
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv, sys.argv = sys.argv, [sys.argv[0]]
import gen_pixeldrive as pd  # noqa: E402
sys.argv = _argv

g, gp = pd.g, pd.gp
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "_art", "envart")
N_CAND = 4
GATE = ("gen_pixeldrive.py", "pixelai_redo.py")          # the queues this one runs after

STYLE = ("pixel art, 16-bit JRPG game asset, HD-2D style, a single isolated object, centered, whole object in view, "
         "plain white background, three-quarter view from slightly above, feudal Japan, clean dark outline, "
         "detailed pixel shading, crisp pixels")
NEG = ("person, people, character, human, animal, text, letters, watermark, signature, frame, border, cropped, "
       "multiple objects, scenery, landscape, horizon, sky, ground plane, floor, shadow on wall, photo, photorealistic, "
       "3d render, blurry, jpeg artifacts, modern, western, chinese")

# (key, prompt, in-game height px, animation or None)   heights: a traveler ~60 px = ~1.7 m (~35 px per metre)
CATALOG = {
    "terrain": [
        ("boulder", "a large weathered grey granite boulder with moss patches", 40, None),
        ("rock_cluster", "a cluster of three mossy grey rocks of different sizes", 26, None),
        ("pebbles", "a small scatter of smooth river pebbles", 10, None),
        ("cliff_face", "a tall jagged rocky cliff face section, layered grey stone", 120, None),
        ("stump", "an old cut tree stump with roots and moss", 22, None),
        ("fallen_log", "a fallen mossy log lying horizontally", 20, None),
        ("roots", "gnarled exposed tree roots", 16, None),
        ("fern", "a lush green fern clump", 22, None),
        ("chrysanthemums", "a clump of wild yellow and white chrysanthemum flowers", 18, None),
        ("azalea", "a round azalea bush with pink flowers", 30, None),
        ("hydrangea", "a hydrangea bush with blue and purple flower heads", 30, None),
        ("pine_sapling", "a small japanese black pine sapling", 50, None),
        ("bonsai_pine", "a windswept japanese pine tree, twisted trunk, layered needle clouds", 140, None),
        ("maple_tree", "a japanese maple tree with red autumn leaves", 130, None),
        ("cherry_tree", "a sakura cherry blossom tree in full pink bloom", 140, None),
        ("dead_tree", "a twisted dead leafless tree, grey bark", 120, None),
        ("tainted_rock", "a cracked black rock oozing purple-green corruption, shadowlands taint", 34, None),
        ("tainted_tree", "a withered black thorny tree with sickly green glow, shadowlands", 120, None),
        ("snow_rock", "a grey rock capped with thick snow", 30, None),
        ("snow_drift", "a soft white snow drift mound", 16, None),
        ("puddle", "a small muddy rain puddle, top-down oval", 8, None),
        ("mushrooms", "a cluster of brown forest mushrooms", 12, None),
        ("rubble", "a pile of broken grey stone blocks and rubble", 22, None),
        ("beach_rocks", "dark wet sea rocks with barnacles", 24, None),
        ("cave_stalagmite", "a cave stalagmite, wet grey-brown limestone", 46, None),
        ("crystal_jade", "a cluster of glowing green jade crystals growing from rock", 30, None),
    ],
    "grass_anim": [
        ("tall_grass", "a tuft of tall green grass blades", 22, "sway"),
        ("susuki", "japanese pampas grass susuki with silver feathery plumes", 40, "sway"),
        ("reeds", "a clump of water reeds and cattails", 40, "sway"),
        ("bamboo", "a clump of three tall thin green bamboo stalks with leaves", 120, "sway"),
        ("rice_plants", "a bunch of green rice plants with drooping golden grain heads", 24, "sway"),
        ("flower_grass", "grass tuft with small white and purple wildflowers", 18, "sway"),
        ("snow_grass", "a tuft of frosty dry grass poking through snow", 18, "sway"),
        ("blight_grass", "a tuft of withered black-purple sickly grass, tainted", 18, "sway"),
        ("cherry_petals", "a branch of pink cherry blossoms hanging down", 30, "sway"),
        ("willow", "a weeping willow tree with long hanging green branches", 140, "sway"),
    ],
    "water_anim": [
        ("pond_ripples", "a small round pond of clear blue water with ripples, top-down", 24, "shimmer"),
        ("koi_pond", "a garden koi pond with orange koi fish and stones around the edge, top-down", 30, "shimmer"),
        ("lily_pads", "a cluster of green lily pads with one pink lotus flower on water", 12, "bob"),
        ("waterfall", "a narrow waterfall falling over a rock ledge into foam", 110, "flow"),
        ("stream", "a short section of a flowing blue stream with white foam, top-down", 20, "flow"),
        ("shore_foam", "a strip of white sea foam and small waves on a sandy shore edge", 12, "shimmer"),
        ("sea_wave", "a curling blue ocean wave crest with white foam, ukiyo-e style", 36, "shimmer"),
        ("shishi_odoshi", "a bamboo water fountain spout pouring into a stone basin, japanese garden", 34, "flow"),
        ("well", "a stone village well with a wooden roof and a bucket, water inside", 56, None),
    ],
    "buildings": [
        ("minka", "a japanese farmhouse minka with a thick thatched roof and wooden walls", 150, None),
        ("machiya", "a japanese wooden townhouse machiya with a dark tile roof and lattice front", 140, None),
        ("shop", "a japanese merchant shop front with a blue noren curtain and goods outside, tile roof", 140, None),
        ("ryokan", "a two-storey japanese inn ryokan with paper lanterns and a tile roof", 190, None),
        ("teahouse", "a small japanese teahouse with a red umbrella and bench outside", 120, None),
        ("brewery", "a japanese sake brewery building with a cedar ball sugidama hanging at the eave", 150, None),
        ("forge", "a japanese blacksmith forge with an open front, anvil and glowing hearth", 130, None),
        ("kura", "a japanese storehouse kura with thick white plaster walls and black tile roof", 150, None),
        ("fishing_hut", "a fishing hut on wooden stilts with nets hung to dry", 120, None),
        ("rice_store", "a raised rice granary on stilts with a thatched roof", 120, None),
        ("shrine", "a small shinto shrine honden building with a sweeping roof and a rope shimenawa", 150, None),
        ("torii_red", "a large vermilion red torii gate", 130, None),
        ("torii_stone", "a weathered grey stone torii gate", 110, None),
        ("temple_hall", "a large buddhist temple main hall with a huge curved tile roof", 220, None),
        ("pagoda", "a five-storey japanese pagoda, dark wood and tile roofs", 300, None),
        ("temple_gate", "a japanese temple gate sanmon, two-storey wooden gate", 200, None),
        ("bell_tower", "a japanese temple bell tower with a big bronze bell", 150, None),
        ("castle_keep", "a japanese castle keep tenshu, white walls, layered black tile roofs, stone base", 380, None),
        ("castle_gate", "a japanese castle gate yaguramon with a gatehouse over it, stone walls", 200, None),
        ("castle_turret", "a japanese castle corner turret yagura on a stone base", 200, None),
        ("castle_wall", "a section of a sloped japanese castle stone wall with a white plastered wall on top", 120,
         None),
        ("samurai_gate", "a samurai mansion gate with a tile roof and heavy wooden doors", 130, None),
        ("kaiu_wall", "a section of a colossal grey fortress wall of huge stone blocks with a watchtower, crab clan",
         300, None),
        ("watchtower", "a tall wooden lookout watchtower with a ladder and a small roof", 200, None),
        ("bridge_arched", "an arched red-lacquered wooden japanese bridge", 70, None),
        ("bridge_plank", "a simple flat wooden plank footbridge with rope rails", 40, None),
        ("pier", "a wooden boat pier with posts and a moored small boat", 50, None),
        ("palisade_gate", "a wooden palisade fort gate of sharpened logs", 120, None),
        ("dojo", "a japanese martial arts dojo hall with a wooden sign over the door", 160, None),
        ("geisha_house", "an elegant japanese okiya house with red lanterns and lattice windows", 150, None),
    ],
    "modular": [
        ("roof_tile_ridge", "a straight section of a japanese grey kawara tile roof with a ridge cap", 50, None),
        ("roof_eave_corner", "an upswept corner of a japanese tile roof eave with an ornamental end tile", 50, None),
        ("roof_thatch", "a section of a thick straw thatched roof", 50, None),
        ("wall_plaster_beam", "a wall panel of white plaster with dark wooden beams and posts", 70, None),
        ("wall_shoji", "a wall section of white paper shoji screens in a wooden frame", 70, None),
        ("wall_plank", "a weathered dark wooden plank wall section", 70, None),
        ("wall_stone_base", "a low foundation course of fitted grey stones", 24, None),
        ("engawa", "a wooden veranda engawa section with posts", 30, None),
        ("fence_wood", "a section of a low wooden fence", 26, None),
        ("fence_bamboo", "a section of a japanese bamboo fence kenninji-gaki tied with black rope", 40, None),
        ("tsuiji_wall", "a section of a japanese earthen garden wall with a small tile roof cap", 50, None),
        ("stone_lantern", "a japanese stone garden lantern toro", 46, None),
        ("lantern_string", "a string of red and white paper lanterns hanging from a rope", 26, None),
        ("noren", "a blue fabric noren door curtain hanging from a rod", 30, "sway"),
        ("nobori", "a tall vertical nobori banner on a bamboo pole, white with a red mon", 90, "sway"),
        ("signboard", "a wooden japanese shop signboard kanban on a stand", 40, None),
        ("stairs_wood", "a short flight of wooden steps", 30, None),
        ("cart", "a two-wheeled wooden handcart", 34, None),
        ("barrels", "a stack of wooden sake barrels with straw wrapping", 34, None),
        ("crates", "a stack of wooden crates and rope", 30, None),
        ("rice_bales", "a stack of straw rice bales tawara", 28, None),
        ("water_barrel", "a wooden rain water barrel with a ladle", 26, None),
        ("gate_posts", "a pair of wooden gate posts with a crossbar", 70, None),
        ("bonfire", "a campfire of crossed logs with flames", 26, "flicker"),
        ("brazier_outdoor", "a tall iron brazier on legs with burning fire", 44, "flicker"),
        ("market_stall", "a japanese market stall with a cloth awning and baskets of vegetables", 60, None),
    ],
    "paths": [
        ("stepping_stones", "a row of flat stepping stones, top-down", 10, None),
        ("gravel_raked", "a patch of raked white gravel with wave lines, top-down", 10, None),
        ("cobbles", "a patch of grey cobblestone path, top-down", 10, None),
        ("boardwalk", "a section of wooden boardwalk planks, top-down", 10, None),
        ("dirt_ruts", "a patch of dirt road with cart ruts, top-down", 10, None),
        ("stone_stairs", "a flight of mossy stone stairs going up a slope", 60, None),
        ("path_edge", "a line of small edging stones with moss", 8, None),
        ("mossy_path", "a patch of path stones with moss between them, top-down", 10, None),
    ],
    "interior": [
        ("tatami", "a japanese tatami mat floor section with dark cloth borders, top-down", 12, None),
        ("fusuma", "a painted fusuma sliding door panel with a pine tree and gold clouds", 66, None),
        ("shoji", "a white paper shoji sliding screen", 66, None),
        ("tokonoma", "a tokonoma alcove with a hanging calligraphy scroll and an ikebana flower vase", 70, None),
        ("kamidana", "a small shinto kamidana household shrine shelf on a wall", 30, None),
        ("irori", "a sunken irori hearth with a hanging iron kettle over burning charcoal", 30, "flicker"),
        ("chabudai", "a low round japanese wooden table with a tea set", 16, None),
        ("zabuton", "two square zabuton floor cushions", 8, None),
        ("futon", "a japanese futon bed with a folded quilt", 12, None),
        ("tansu", "a japanese tansu chest of drawers with iron fittings", 40, None),
        ("byobu", "a folding byobu screen painted with cranes and gold leaf", 56, None),
        ("andon", "an andon paper floor lamp glowing warm", 34, "flicker"),
        ("armor_stand", "a samurai armor o-yoroi displayed on a stand with a helmet", 60, None),
        ("katana_rack", "a lacquered sword rack holding a katana and wakizashi", 26, None),
        ("spear_rack", "a wooden weapon rack holding yari spears and naginata", 70, None),
        ("scroll_shelf", "a wooden bookshelf full of rolled scrolls and books", 60, None),
        ("writing_desk", "a low writing desk with brushes, ink stone and paper", 18, None),
        ("kamado", "a japanese clay kitchen stove kamado with pots and fire", 34, "flicker"),
        ("hanging_pots", "iron pots and utensils hanging from a wooden beam", 30, None),
        ("shop_counter", "a wooden shop counter with goods, scales and an abacus", 34, None),
        ("tea_set", "a japanese tea set: kettle, tea bowls and whisk on a tray", 10, None),
        ("hibachi", "a ceramic hibachi brazier with glowing charcoal", 18, "flicker"),
        ("dais", "a lord's raised wooden dais with a gold folding screen behind it", 70, None),
        ("altar", "a buddhist altar with candles, incense and offerings", 50, "flicker"),
        ("go_board", "a wooden go board with black and white stones", 12, None),
        ("training_dummy", "a straw training dummy on a wooden post", 56, None),
        ("ofuda_wall", "paper ofuda prayer charms pinned on a wooden wall", 34, None),
        ("medicine_chest", "a wooden medicine chest with many small drawers", 44, None),
        ("lacquer_box", "a black lacquer box with gold maki-e decoration", 10, None),
        ("bonsai_stand", "a bonsai tree in a pot on a small wooden stand", 30, None),
        ("sake_shelf", "shelves of sake bottles and ceramic jars", 56, None),
        ("bath_tub", "a round wooden ofuro bath tub with steaming water", 30, "shimmer"),
    ],
}


def log(*a):
    print(time.strftime("%m-%d %H:%M"), *a, flush=True)


def wf(pos, neg, seed):
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
        "13": {"class_type": "SaveImage", "inputs": {"images": ["12", 0], "filename_prefix": "rt_envart/e"}},
    }


def gen(pos, neg, seed):
    pid = pd.post_job(wf(pos, neg, seed))
    while True:
        st, im = pd.job_state(pid)
        if st == "done":
            return im
        if st in ("lost", "error"):
            pid = pd.post_job(wf(pos, neg, seed))
        time.sleep(2)


def to_sprite(big, height, colors=32):
    """1024 image -> RGBA sprite of the in-game height: white keyed out, the main object kept, quantized."""
    a = g.key_out(big.convert("RGB"), holes=True)
    arr = np.asarray(a).copy()
    import cv2
    al = (arr[..., 3] > 40).astype(np.uint8)
    n, lbl, st, _ = cv2.connectedComponentsWithStats(cv2.dilate(al, np.ones((9, 9), np.uint8)), connectivity=8)
    if n > 2:                                              # keep the main object and anything big next to it
        big_k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        keep = np.isin(lbl, [k for k in range(1, n) if k == big_k or st[k, cv2.CC_STAT_AREA] >
                             0.25 * st[big_k, cv2.CC_STAT_AREA]])
        arr[~(keep & (al > 0))] = 0
    a = Image.fromarray(arr, "RGBA")
    bb = a.getbbox()
    if not bb:
        return None
    a = a.crop(bb)
    s = max(4, height) / a.size[1]
    w, h = max(1, int(round(a.size[0] * s))), max(1, int(round(a.size[1] * s)))
    small = a.resize((w, h), Image.BOX)
    alpha = np.asarray(small)[..., 3] > 110
    rgb = small.convert("RGB").quantize(colors, method=Image.Quantize.MEDIANCUT).convert("RGB")
    return Image.fromarray(np.dstack([np.asarray(rgb), (alpha * 255).astype(np.uint8)]), "RGBA")


def animate(sp, mode, n=4):
    """4 frames of one drawing (the frames can't drift apart: they are the same pixels moved / relit)."""
    base = np.asarray(sp).astype(np.int32)
    h, w = base.shape[:2]
    pad = 3 if mode == "sway" else 0
    frames = []
    rgb = base[..., :3]
    mx, mn = rgb.max(-1), rgb.min(-1)
    blue = (base[..., 3] > 0) & (rgb[..., 2] >= rgb[..., 0] + 15) & (rgb[..., 2] >= rgb[..., 1] - 10)
    white = (base[..., 3] > 0) & (mn > 200)
    fire = (base[..., 3] > 0) & (rgb[..., 0] > 190) & (rgb[..., 1] > 90) & (rgb[..., 2] < 140) & (mx - mn > 70)
    yy, xx = np.mgrid[0:h, 0:w]
    for f in range(n):
        ph = 2 * np.pi * f / n
        out = np.zeros((h, w + 2 * pad, 4), np.int32)
        if mode == "sway":                                 # the top bends most, the base stays put
            for y in range(h):
                dx = int(round(2.0 * np.sin(ph) * ((h - 1 - y) / max(1, h - 1)) ** 1.5))
                out[y, pad + dx:pad + dx + w] = base[y]
        elif mode == "bob":
            dy = (0, 1, 0, -1)[f % 4]
            out[max(0, dy):h + min(0, dy), :] = base[max(0, -dy):h - max(0, dy)]
        else:
            out[:, :] = base
            if mode in ("shimmer", "flow"):
                m = blue | white
                if mode == "flow":                         # the water texture runs down (falls) / along (streams)
                    rolled = np.roll(base, f * 2, axis=0 if h > w else 1)
                    take = m & np.roll(m, f * 2, axis=0 if h > w else 1)
                    out[take] = rolled[take]
                wave = 1 + 0.14 * np.sin(xx * 0.55 + yy * 0.35 + ph)
                out[..., :3][m] = np.clip(out[..., :3][m] * wave[m][:, None], 0, 255)
            if mode == "flicker" or fire.any():
                k = (1.0, 1.16, 0.9, 1.08)[f % 4]
                out[..., :3][fire] = np.clip(base[..., :3][fire] * k, 0, 255)
        frames.append(Image.fromarray(out.astype(np.uint8), "RGBA"))
    return frames


def item_dir(cat, key):
    return os.path.join(OUT, cat, key)


def draw_item(cat, key, prompt, height, anim, seed0=1):
    d = item_dir(cat, key)
    os.makedirs(d, exist_ok=True)
    if os.path.exists(os.path.join(d, "done")):
        return
    pos = STYLE + ", " + prompt
    for k in range(N_CAND):
        if os.path.exists(os.path.join(d, "cand_%d.png" % k)):
            continue                                       # (resume: finished candidates stay)
        seed = (zlib.crc32(key.encode()) % 9000 + seed0) * 100 + k
        big = gen(pos, NEG, seed)
        big.save(os.path.join(d, "big_%d.png" % k))
        sp = to_sprite(big, height)
        if sp is None:
            continue
        if anim:
            fr = animate(sp, anim)
            strip = Image.new("RGBA", (fr[0].width * len(fr), fr[0].height))
            for i, f in enumerate(fr):
                strip.alpha_composite(f, (i * f.width, 0))
            strip.save(os.path.join(d, "anim_%d.png" % k))
            z = max(1, 120 // max(1, f.height))
            gif = [Image.alpha_composite(Image.new("RGBA", f.size, (70, 110, 70, 255)), f)
                   .resize((f.width * z, f.height * z), Image.NEAREST).convert("P", palette=Image.ADAPTIVE)
                   for f in fr]
            gif[0].save(os.path.join(d, "anim_%d.gif" % k), save_all=True, append_images=gif[1:], duration=160,
                        loop=0)
        sp.save(os.path.join(d, "cand_%d.png" % k))       # last: its presence marks the candidate finished
        log(cat, key, "candidate", k)
    open(os.path.join(d, "done"), "w").write("1")


def contact():
    for cat in CATALOG:
        tiles = []
        for key, _p, _h, _a in CATALOG[cat]:
            for c in sorted(glob.glob(os.path.join(item_dir(cat, key), "cand_*.png"))):
                tiles.append((key + " " + c[-5], Image.open(c).convert("RGBA")))
        if not tiles:
            continue
        cell = 140
        cols = 8
        rows = (len(tiles) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * cell, rows * (cell + 12)), (70, 110, 70))
        dr = ImageDraw.Draw(sheet)
        for i, (name, im) in enumerate(tiles):
            s = min(1.0 * (cell - 4) / im.width, 1.0 * (cell - 4) / im.height, 3.0)
            im2 = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.NEAREST)
            x, y = (i % cols) * cell, (i // cols) * (cell + 12)
            sheet.paste(im2, (x + (cell - im2.width) // 2, y + 12 + cell - im2.height), im2)
            dr.text((x + 2, y), name, fill=(255, 255, 0))
        sheet.save(os.path.join(OUT, "contact_%s.png" % cat))


def gate_busy():
    me = {os.getpid(), os.getppid()}
    for p in psutil.process_iter(["pid", "cmdline"]):
        try:
            cl = " ".join(p.info["cmdline"] or [])
        except Exception:
            continue
        if p.info["pid"] not in me and any(s in cl for s in GATE):
            return True
    return False


def another_runner():
    me = {os.getpid(), os.getppid()}
    for p in psutil.process_iter(["pid", "cmdline"]):
        try:
            cl = p.info["cmdline"] or []
        except Exception:
            continue
        if p.info["pid"] not in me and any(c.endswith("gen_envart.py") for c in cl) and "run" in cl:
            try:
                if p.parent() and p.parent().pid in me:
                    continue
            except Exception:
                pass
            return True
    return False


def run(now=False):
    if another_runner():
        log("another envart runner is going; exiting")
        return
    if not now:
        log("waiting for the sprite-sheet queues to finish:", ", ".join(GATE))
        while gate_busy():
            time.sleep(300)
    total = sum(len(v) for v in CATALOG.values())
    i = 0
    for cat, items in CATALOG.items():
        for key, prompt, height, anim in items:
            i += 1
            if not os.path.exists(os.path.join(item_dir(cat, key), "done")):
                log("item %d of %d: %s/%s" % (i, total, cat, key))
                draw_item(cat, key, prompt, height, anim)
        contact()
    open(os.path.join(OUT, "ALL_DONE"), "w").write(time.strftime("%Y-%m-%d %H:%M"))
    log("all environment art drawn")


def main():
    a = sys.argv[1:]
    if "--log" in a:
        i = a.index("--log")
        os.makedirs(os.path.dirname(a[i + 1]), exist_ok=True)
        sys.stdout = sys.stderr = open(a[i + 1], "a", encoding="utf-8", buffering=1)
        a = a[:i] + a[i + 2:]
    os.makedirs(OUT, exist_ok=True)
    if not a or a[0] == "run":
        run(now="--now" in a)
    elif a[0] == "draw":
        for key in a[1:]:
            for cat, items in CATALOG.items():
                for it in items:
                    if it[0] == key:
                        draw_item(cat, *it)
        contact()
    elif a[0] == "contact":
        contact()


if __name__ == "__main__":
    main()
