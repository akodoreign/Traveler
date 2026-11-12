"""Dialog busts: painted anime head-and-shoulders portraits shown behind the dialog box (plugin/rokugan/RokuganBust.sk),
one image per emotion, made with the user's local ComfyUI (http://127.0.0.1:8188) and the Illustrious-XL anime
checkpoint already installed there (waiIllustriousSDXL_v170). Nothing is installed or downloaded.

How the set stays one person: every character has ONE base bust (txt2img, fixed seed, neutral face). The emotions are
made from that base by inpainting only the face: the face box is cropped, upscaled to 1024, re-drawn with the emotion
tags at moderate denoise (SetLatentNoiseMask), scaled back and pasted through a feathered mask. Everything outside the
face (hair, clothes, armour, colours, pose) is the same pixels in every emotion.
The background is a flat colour; it is keyed out here in Python (border flood fill + edge decontamination), since the
ComfyUI install has no background-removal model.

Stages (each one reads what the previous one wrote; _art/busts/<key>/):
  python -E tools/gen_busts.py base natsuko [--seeds 101,102,...]   candidate bases  -> cand_<seed>.png + sheet
  (pick one: set "seed" and "face" in CHARS below; "face" = x0,y0,x1,y1 of the face in the 832x1216 base)
  python -E tools/gen_busts.py emotions natsuko [--only angry,sad]   emotions from the chosen base -> <emo>.png
  python -E tools/gen_busts.py export natsuko                        key out, trim, scale -> engine resource + sheet
  python -E tools/gen_busts.py all natsuko                           base (chosen seed) + emotions + export
  python -E tools/gen_busts.py data                                  only rewrite plugin/rokugan/RokuganBustData.sk
Outputs: project/resource/bust/<key>/<emotion>.png (RGBA, BUST_H px tall), plugin/rokugan/RokuganBustData.sk (the
name -> key table the plugin reads), preview sheets in _art/preview/agents/busts/. Workflows: tools/comfy/*.json.
"""
import io
import json
import os
import random
import sys
import time
import urllib.request
import uuid

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
PROJ = os.path.join(ROOT, "_tools", "rpgcobo-tool", "project")
RES = os.path.join(PROJ, "resource", "bust")
DATA_SK = os.path.join(PROJ, "plugin", "rokugan", "RokuganBustData.sk")
WORK = os.path.join(ROOT, "_art", "busts")
PREVIEW = os.path.join(ROOT, "_art", "preview", "agents", "busts")
WF_DIR = os.path.join(HERE, "comfy")
COMFY = "http://127.0.0.1:8188"
CKPT = "waiIllustriousSDXL_v170.safetensors"
W, H = 832, 1216                      # SDXL portrait bucket
BUST_H = 600                          # in-game image height (screen is 1280x720; the plugin scales if needed)

EMOTIONS = ["neutral", "happy", "angry", "sad", "surprised", "worried", "determined", "hurt"]
# Face-only tags per emotion (Danbooru style, what Illustrious understands), plus the denoise for the face pass.
EMO = {
    "neutral":    ("expressionless, calm, closed mouth, serious", 0.0),
    "happy":      ("smile, happy, open mouth, teeth, closed eyes smile, ^_^, blush", 0.62),
    "angry":      ("angry, furious, v-shaped eyebrows, glaring, clenched teeth, open mouth, anger vein", 0.64),
    "sad":        ("sad, downcast eyes, looking down, frown, tears, teary eyes, closed mouth", 0.62),
    "surprised":  ("surprised, wide-eyed, open mouth, raised eyebrows, :o, shocked", 0.62),
    "worried":    ("worried, furrowed brow, frown, nervous, sweatdrop, closed mouth, raised inner eyebrows", 0.6),
    "determined": ("determined, serious, smirk, confident, narrowed eyes, v-shaped eyebrows, closed mouth", 0.58),
    "hurt":       ("pain, wince, one eye closed, gritted teeth, sweat, bruise, scratch on cheek, blood on face", 0.64),
}

STYLE = ("masterpiece, best quality, amazing quality, very aesthetic, absurdres, official art, "
         "jrpg character portrait, game cg, thin clean lineart, soft shading, painterly, warm lighting, "
         "upper body, portrait, three-quarter view, body turned to the right, looking to the right, head tilt, "
         "simple background, white background, solo")
NEG = ("worst quality, low quality, normal quality, lowres, bad anatomy, bad hands, extra fingers, text, watermark, "
       "signature, username, logo, frame, border, multiple views, 2koma, cropped head, head out of frame, out of frame, close-up, from side, profile, "
       "gradient background, detailed background, scenery, chibi, 3d, realistic, nsfw, cleavage, bare shoulders, off shoulder, collarbone, chest scar, modern clothes")

# Character designs (match tools/gen_sprites2d.py TRAVELERS and docs/art/cast-looks.md).
#   seed  : the chosen base seed (None until picked)     face : face box in the base, x0,y0,x1,y1 (None until picked)
#   flip  : mirror the base so the bust faces right (toward the dialog text)
#   names : dialog speaker names that use this bust (gen_maps.py FULL_NAMES labels, plus variants)
CHARS = {
    "natsuko": dict(
        colors="slate-blue kimono, red cord, rope strap", court="dark blue haori jacket with a small white family crest on the chest over a grey silk kimono", night="dark blue cotton yukata with white asanoha pattern",
        names=["Hiruma Natsuko", "Natsuko"],
        # the prompt cand_28 was made with (user's pick, 2026-11-07); kept for the inpaint passes
        prompt=("1girl, mature female, 20s, young samurai scout, light brown skin, tan, dark brown hair, long ponytail, "
                "side-swept bangs, red hachimaki headband, sharp brown eyes, thick eyebrows, scar on nose, "
                "lean athletic, slate-blue kimono, dark blue-grey lacquered lamellar "
                "armor with red lacing, one shoulder guard (sode), red cord, small crab crest on the chest, "
                "rolled scroll case strap across the chest, feudal japan, rokugan"),
        look=("1girl, mature female, 20s, light brown skin, tan, dark brown hair, long ponytail, side-swept bangs, "
              "sharp brown eyes, thick eyebrows, scar on nose, lean athletic"),
        seed=28, base_file="approved_base.png", face=(222, 335, 556, 645), neck_y=655, crown_y=360, flip=True,
        variants=["travel", "court", "bath", "night"]),
    "rensei": dict(
        vseed={"bath": 43},   # picked 2026-11-08 (review/var_*_v<seed>.png)
        look="1boy, male focus, young man, fair skin, light peach skin, long white hair, topknot, parted bangs, calm blue eyes, mole under the eye, handsome", colors="pale blue and white", court="pale blue silk kamishimo with a white crane crest over a white kimono", night="white cotton yukata with a pale blue pattern",
        names=["Kakita Rensei", "Rensei"],
        prompt=("1boy, male focus, young man, 20s, samurai duelist, fair skin, light peach skin, thick black lineart around the hair, long white hair, topknot, parted bangs, "
                "half-closed calm blue eyes, straight eyebrows, small mole under the eye, handsome, composed, "
                "pale-blue haori with a small white crane crest over a white kimono, katana hilt at the hip, "
                "feudal japan, rokugan"),
        seed=42, base_file="approved_base.png", face=(290, 365, 555, 565), neck_y=580, crown_y=395, flip=False, variants=["travel", "court", "bath", "night"], bg="white", holes=False),   # grey bg made his skin grey (user), tan made it orange: white bg, peach skin
    "gendo": dict(
        vseed={"travel": 22},   # picked 2026-11-08 (review/var_travel_v22); bath = queue redo s212 (review/var_bath_s212)
        look="1boy, male focus, young man, short black hair, ahoge, round glasses, green eyes, stern eyebrows, long face", colors="dark green kimono", court="dark green formal haori with a gold dragon crest over a sage-green kimono", night="sage-green cotton yukata",
        names=["Kitsuki Gendo", "Gendo"],
        prompt=("1boy, male focus, young man, 20s, magistrate investigator, short black hair, ahoge, round glasses, "
                "green eyes, skeptical expression, stern eyebrows, slightly tired eyes, long face, "
                "dark green haori over a pale sage-green kimono, gold trim, jitte at the belt, feudal japan, rokugan"),
        seed=3, base_file="approved_base.png", face=(230, 330, 570, 545), neck_y=560, crown_y=355, flip=False, variants=["travel", "court", "bath", "night"]),
    "shizue": dict(
        vseed={"travel": 62},   # picked 2026-11-08 (review/var_travel_v22); bath = queue redo s212 (review/var_bath_s212)
        vtags={"travel": "wearing a sugegasa on the head, wide conical woven rice-straw travel hat, plain hat, "
                         "plain gold and brown travel haori over a brown kimono, travelling clothes"},
        vneg={"travel": ["raincoat", "rain cape", "mino", "rope", "cord", "yellow coat", "bright yellow", "lion", "tiger", "cat", "animal on hat", "face on hat", "mascot", "emblem on hat", "eyes on hat", "text"]},
        look="1girl, young woman, brown bob cut hair, heavy bangs, round amber eyes, light blush", colors="golden-yellow kimono", court="golden-yellow formal silk kimono with a red obi and a small lion crest", night="pale yellow cotton yukata with a red pattern",
        names=["Akodo Shizue", "Shizue"],
        prompt=("1girl, young woman, 20s, samurai strategist, brown bob cut hair, heavy bangs, red hachimaki headband, "
                "round amber eyes, light blush, gentle smile, gold lacquered lamellar armor with red lacing over a "
                "golden-yellow kimono, war fan (gunbai) at the obi, small lion crest, feudal japan, rokugan"),
        seed=2, base_file="approved_base.png", face=(200, 440, 560, 700), neck_y=715, crown_y=470, flip=False, variants=["travel", "court", "bath", "night"]),
    "haruki": dict(
        vseed={"travel": 41},   # picked 2026-11-08 (review/var_*_v<seed>.png)
        look="1boy, male focus, young man, spiky dark brown hair, messy bangs, gentle orange-brown eyes, round face", colors="orange robe", court="orange formal silk robe with gold trim and a small phoenix crest", night="orange-and-white cotton yukata",
        names=["Isawa Haruki", "Haruki"],
        prompt=("1boy, male focus, young man, late teens, shugenja priest, spiky dark brown hair, messy bangs, "
                "gentle orange-brown eyes, worried eyebrows, round face, orange robe with a wave pattern, "
                "red-orange hakama, golden-yellow trim, small phoenix crest, "
                "feudal japan, rokugan"),
        seed=2, base_file="approved_base.png", face=(215, 360, 590, 705), neck_y=720, crown_y=390, flip=False, variants=["travel", "court", "bath", "night"],
        neg_add=["scroll", "talisman", "text", "magic circle", "window"]),
    "mitsue": dict(
        # bath redone 2026-11-11 (bust monitor): the base's red half-mask grew into a red high-necked top; picked
        # review/var_bath_v61.png (old one: review/var_bath_old_redtop.png)
        vseed={"bath": 61},
        vtags={"bath": "(pale porcelain skin, fair skin:1.3), after the bath, white towel on head, bare shoulders, bare neck, "
                       "collarbone, bare arms, white bath towel wrapped around the chest, damp hair, relaxed"},
        vneg={"bath": ["red clothes", "turtleneck", "high collar", "shirt", "sleeves", "mask", "scarf", "mouth mask",
                       "bodysuit", "red top", "kimono", "tan", "dark skin", "tanned skin", "brown skin"]},
        look="1girl, young woman, long straight black hair, swept bangs, sharp crimson eyes, red eyeshadow", colors="crimson and black kimono", court="crimson formal silk kimono with black diamond pattern and gold trim", night="black cotton yukata with a red pattern",
        names=["Shosuro Mitsue", "Mitsue"],
        prompt=("1girl, young woman, 20s, scorpion clan agent, long straight black hair, swept bangs, sharp crimson "
                "eyes, arched eyebrows, red eyeshadow, sly smirk, dark red cloth half-mask pulled down around the neck, "
                "crimson kimono with a black diamond pattern, gold trim, black obi, feudal japan, rokugan"),
        seed=3, base_file="approved_base.png", face=(220, 320, 560, 535), neck_y=550, crown_y=345, flip=False, variants=["travel", "court", "bath", "night"]),
    "tamotsu": dict(
        vseed={"travel": 41, "bath": 53},   # picked 2026-11-08 (review/var_*_v<seed>.png)
        vneg={"bath": ["pole", "stick", "staff", "bow (weapon)", "quiver", "pillar", "arrow", "wall", "white spot"]},
        look="1boy, male focus, mature man, brown hair in a topknot, full brown beard, laugh lines, strong nose, stocky", colors="purple coat with fur collar", court="purple formal silk haori with gold trim over an off-white kimono", night="purple cotton yukata",
        names=["Ide Tamotsu", "Tamotsu"],
        prompt=("1boy, male focus, mature man, 30s, jovial diplomat, brown hair in a chonmage topknot, full brown "
                "beard, smiling eyes, laugh lines, strong nose, round cheerful face, stocky, purple coat with "
                "fur-trimmed collar over an off-white kimono, gold trim, unicorn clan, quiver strap, "
                "feudal japan, rokugan"),
        seed=2, base_file="approved_base.png", face=(130, 310, 510, 690), neck_y=700, crown_y=335, flip=False, variants=["travel", "court", "bath", "night"]),
    "sayo": dict(
        look="1girl, young woman, tan skin, freckles, long brown hair, wide brown eyes", colors="worn brown kimono, green obi", court="borrowed plain brown formal kimono with a green obi", night="faded brown cotton yukata",
        names=["Sayo"],
        prompt=("1girl, young woman, 20s, ronin herbalist, tan skin, freckles, long brown hair, wide brown eyes, "
                "kind smile, jingasa woven travel hat (kasa hat), worn brown kimono with a faded wave pattern, "
                "green obi, herb basket strap, plain, poor, feudal japan, rokugan"),
        seed=1, base_file="approved_base.png", face=(236, 320, 560, 560), neck_y=575, crown_y=345, flip=False, variants=["travel", "court", "bath", "night"],
        cut_edge_hue=(24, 90)),   # green plant leaves at the frame sides (base, night): keyed out
}

# Everyone who isn't a traveler: ONE neutral bust each (user, 2026-11-07); the plugin shows it for every emotion.
# Order of work: speakers by dialog line count (map.json), the Crab path first. seed=None until a candidate is picked
# (python -E tools/gen_busts.py base <key> --seeds 1,2,3), then "export <key>".
#   designs: tools/gen_sidecast.py CAST, tools/gen_nezumi.py, docs/art/cast-looks.md
NPC = {
    "gonta": (["Gonta"], "1boy, male focus, huge sumai wrestler, ronin, very large and fat, tan skin, black hair in a sumo topknot, stubble, thick eyebrows, broad grin, bare shoulders, thick neck, red cord, plain grey kimono hanging open, feudal japan"),
    "yosai": (["Togashi Yosai"], "1boy, male focus, tattooed monk, bald head with blue ink tattoos on the scalp, tan skin, closed eyes, wide cheerful grin, round face, ochre monk robe, bare tattooed forearms, dragon tattoos, feudal japan"),
    "ryozo": (["Seppun Ryozo"], "1boy, male focus, young imperial courtier, pale skin, long messy black hair, long face, sly grin, cream silk kimono with a navy hakama, gold trim, holding a scroll, feudal japan"),
    "takakana": (["Kaiu Takakana"], "1boy, male focus, old veteran castle steward, tan skin, grey hair in a topknot, grey goatee and mustache, scar on face, frown, thick eyebrows, brown lacquered armor with blue lacing, feudal japan, samurai"),
    "goro": (["Hiruma Goro"], "1boy, male focus, young samurai scout, tan skin, short black hair, square jaw, scar on cheek, serious, dark blue-grey lamellar armor with red lacing over a slate-blue kimono, feudal japan"),
    # user: "more like Master Splinter (much younger), not Tom and Jerry" -> a grounded young ratfolk
    "squeak": (["Squeak"], "nezumi, anthropomorphic rat, ratfolk, realistic rat head, long tapered snout, (small rounded ears set back on the head:1.3),  beady dark eyes, long whiskers, short brown fur with visible fur texture, young wiry teenage rat, bright-eyed, clawed pink hands, scrappy torn red-brown cloth rags, rope belt, no humans, feudal japan, master splinter style",
               ["cartoon", "mouse", "tom and jerry", "jerry", "mickey", "chibi", "cute big ears", "round head", "grey fur", "beard", "old", "large ears", "kangaroo", "dog", "deer"]),
    "sachiko": (["Hida Sachiko"], "1girl, large muscular woman, tall and broad, tan skin, brown bob hair, red hachimaki headband, big grin, heavy dark blue armor with orange lacing, sake gourd, feudal japan, samurai"),
    "kage": (["Hiruma Kage"], "1boy, male focus, middle-aged samurai lord, tan skin, black hair in a topknot, neat mustache, narrow eyes, stern, immaculate steel-blue lacquered armor with white lacing, feudal japan"),
    "satomi": (["Seppun Satomi"], "1girl, imperial court lady, pale skin, black hair in an elegant bun, long face, narrow eyes, calm, holding a folding fan, pale green and white layered silk kimono with a dot pattern, feudal japan"),
    "michio": (["Isawa Michio"], "1boy, male focus, young shugenja, short black hair with swept bangs, long face, narrow eyes, rust-brown robe with a gold check pattern, phoenix crest, feudal japan"),
    "fujio": (["Ide Fujio"], "1boy, male focus, unicorn clan diplomat, long dark hair with a topknot, swept bangs, long face, purple haori over a white kimono, gold trim, holding a folding fan, feudal japan"),
    "tomoe": (["Hida Tomoe"], "1girl, old woman, crab clan commander, tan skin, grey hair in a ponytail, square jaw, scar on face, stern frown, wrinkles, heavy dark blue armor, feudal japan, samurai"),
    "kiyo": (["Kiyo"], "1girl, peasant woman, small, black hair in a bun under a red head cloth, round face, grin, plain tan and brown work kimono, feudal japan, villager"),
    "sakura": (["Daidoji Sakura"], "1girl, young woman, samurai, black ponytail, sharp face, serious, dark blue lamellar armor with gold lacing over an orange kimono, crane crest, feudal japan"),
    "ryoichi": (["Hiruma Ryoichi"], "1boy, male focus, young japanese peasant scout, tan skin, spiky brown hair, round face, cheerful grin, (patched brown cotton kimono with tasuki cord tying back the sleeves, short hakama:1.2), kama sickle at the obi, gourd, japanese clothing, feudal japan", ["western clothes", "suit", "jacket", "necktie", "tie", "buttons", "collared shirt", "uniform", "military uniform", "shirt", "pocket", "badge", "maid headdress", "frills", "apron (western)"]),
    # user review 2026-11-08 redos (picks from npc_picks.json removed for these keys)
    "npc_jinnai": (["Jinnai"], "1boy, male focus, man, ronin pilgrim monk of osano-wo, natural warm skin tone, healthy skin, short black hair, stubble, calm, jingasa hat pushed back on the head, dark green and brown travel robe, prayer beads, holding a shakujo staff, japanese clothing, feudal japan", ["green skin", "sickly", "pale skin", "grey skin", "zombie"]),
    "npc_nezumi_warrior": (["Nezumi Warrior"], "nezumi, anthropomorphic rat, ratfolk warrior, realistic rat head, long tapered snout, (small rounded ears set back on the head:1.3), beady eyes, long whiskers, brown fur with visible texture, red cloth headband, crude hide and leather armour, holding a bamboo spear, clawed hands, no humans, feudal japan, master splinter style", ["cartoon", "mouse", "tom and jerry", "jerry", "mickey", "chibi", "cute big ears", "round head", "wolf", "beast", "monster", "dog", "kangaroo", "large ears", "fangs"]),
    "npc_kuni_taira": (["Kuni Taira"], "1boy, male focus, middle-aged man, crab clan shugenja scholar, messy dark hair tied back, unkempt, sickly greyish pallor, dark circles under the eyes, cheerful unsettling smile, dark blue-grey robes, leather bracers, ink-stained fingers, japanese clothing, feudal japan", ["bald", "shaved head", "armor"]),
    "npc_asako_keiki": (["Asako Keiki"], "1boy, male focus, young man, idealist monk, shaved head, round face, serene gentle smile, kind eyes, orange and red monk robes with gold trim, prayer beads, japanese clothing, feudal japan", ["armor", "angry", "scowl", "old", "wrinkles"]),
    "npc_maid": (["Maid"], "1girl, young japanese woman, castle servant, black hair in a simple bun, plain indigo cotton kimono with tasuki cord tying back the sleeves, maekake (japanese work apron tied at the waist), modest, japanese clothing, feudal japan", ["western clothes", "suit", "jacket", "necktie", "tie", "buttons", "collared shirt", "uniform", "military uniform", "shirt", "pocket", "badge", "maid headdress", "frills", "apron (western)"]),
    "mai": (["Yogo Mai"], "1girl, young woman, scorpion shugenja, long black hair with center-parted bangs, round face, crimson robe with a black diamond pattern, gold trim, holding a scroll, feudal japan"),
    "takeo": (["Kitsu Takeo"], "1boy, male focus, young samurai, brown hair in a topknot, gold lacquered armor with red lacing over a golden-yellow kimono, lion crest, feudal japan"),
}
for _k, _v in NPC.items():
    CHARS[_k] = dict(names=_v[0], prompt=_v[1], seed=None, face=None, flip=False, variants=[], npc=True,
                     neg_add=_v[2] if len(_v) > 2 else [])
# the picked candidate seed per NPC (cand_<seed>_<prompt hash>.png of the CURRENT prompt)
NPC_PICK = {"gonta": 2, "yosai": 3, "ryozo": 2, "takakana": 3, "goro": 3, "sachiko": 1, "kage": 3, "satomi": 1,
            "michio": 1, "fujio": 1, "tomoe": 3, "kiyo": 2, "sakura": 3, "mai": 3, "takeo": 1, "squeak": 22}
CHARS["squeak"]["flip"] = True
NPC_PICK.update({"npc_jinnai": 103, "npc_nezumi_warrior": 101, "npc_kuni_taira": 102, "npc_asako_keiki": 101,
                 "npc_maid": 101, "ryoichi": 101})          # user-review redos, 2026-11-08
for _k, _s in NPC_PICK.items():
    CHARS[_k]["seed"] = _s
CHARS["npc_nezumi_warrior"]["flip"] = True                            # he faces left: turn him toward the text
CHARS["ryozo"]["names"].append('"Ryozo"')                  # his alias line label
CHARS["sayo"]["names"].append("Young Sayo")                # flashback label (story_7): her own face, not the herbalist stand-in
# Picks from the bulk queue (tools/queue_busts.py -> collect_busts.py -> _art/busts/<key>/review/cand_s<seed>.png):
# _art/busts/npc_picks.json {key: {names, file}}; `npc <key>` (or `npcpicks`) exports them.
_PICKS = os.path.join(WORK, "npc_picks.json")
if os.path.exists(_PICKS):
    for _k, _v in json.load(open(_PICKS, encoding="utf-8")).items():
        CHARS[_k] = dict(names=_v["names"], prompt="", seed=None, base_file=_v["file"], face=None, flip=False,
                         variants=[], npc=True)
for _k, _s in NPC_PICK.items():
    CHARS[_k]["seed"] = _s

# Maps whose whole floor plan is one scene look (the plugin uses it unless a line or a script says otherwise):
# the Winter Court floors of Kyuden Hida (Crab Ch2) and the Kyuden Doji court. Bath / inn scenes are too few and too
# mixed for whole maps: tag those lines ("[bath]") or call ::Rokugan.bustScene("bath") from the scene's cmd_script.
MAP_SCENES = {"M142": "court", "M143": "court", "M144": "court", "M145": "court", "M146": "court", "M229": "court"}

# Scene variants: the base bust re-dressed by inpainting the body below the chin (and the crown of the head where the
# variant changes headwear); the face, hair and skin stay the base's. Emotions are the same face patches pasted on.
#   regions: "body" = everything below neck_y;  "crown" = everything above crown_y (headband / hat / hair top)
VARIANTS = {
    "travel": dict(regions=["body", "crown"], denoise=0.92,
                   tags="wearing a sugegasa on the head, wide conical woven rice-straw travel hat, plain hat, woven grass rain cape (mino) over the shoulders, travelling clothes, {colors}",
                   neg_add=["drinking straw", "straw (drink)", "plastic", "cup", "holding hat", "hat in hand",
                            "eyes on hat", "mascot", "creature", "animal on head", "emblem on hat", "character on hat",
                            "hat on chest", "grass", "plants", "slime (creature)", "blob", "figure on hat", "karakasa obake",
                            "yokai", "bird", "snail"]),
    # court and night keep the base's head (headband, ponytail): repainting the crown without the headband left a
    # hard shadow band across the forehead and re-tinted the skin (user, 2026-11-07: night needed redoing)
    "court":  dict(regions=["body"], denoise=0.9,
                   tags="formal court clothes, {court}, long wide sleeves, covered shoulders, elegant",
                   neg_add=["spider web", "crab", "animal", "necklace"], seed_add=5),
    "bath":   dict(regions=["body", "crown"], denoise=0.92,
                   tags="after the bath, white towel on head, bare shoulders, collarbone, white bath towel wrapped "
                        "around the chest, damp hair, relaxed",
                   neg_drop=["bare shoulders", "off shoulder", "collarbone"], neg_add=["water", "partially submerged", "onsen", "pool", "steam", "smoke", "chair", "furniture", "wall", "bench", "tiles", "liquid", "splash", "droplets", "wet skin", "nipples", "dripping", "fluid", "drool",
                            "messy hair", "towel over face"], seed_add=1),
    "night":  dict(regions=["body"], denoise=0.9,
                   tags="sleeping yukata, {night}, loose collar, relaxed",
                   neg_add=["indoors", "shoji", "window", "room"]),
}

# ------------------------------------------------------------------------------------------------- ComfyUI client
def _req(path, data=None, ctype="application/json"):
    req = urllib.request.Request(COMFY + path, data=data, headers={"Content-Type": ctype} if data else {})
    with urllib.request.urlopen(req, timeout=600) as r:
        return r.read()


def queue(wf):
    cid = str(uuid.uuid4())
    # front: interactive stage jobs jump ahead of a bulk queue_busts.py queue
    r = json.loads(_req("/prompt", json.dumps({"prompt": wf, "client_id": cid, "front": True}).encode()))
    pid = r["prompt_id"]
    while True:
        h = json.loads(_req("/history/" + pid))
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("status_str") == "error":
                raise RuntimeError("ComfyUI error: %s" % json.dumps(st)[:2000])
            outs = h[pid]["outputs"]
            ims = []
            for node in outs.values():
                for im in node.get("images", []):
                    q = "/view?filename=%s&subfolder=%s&type=%s" % (im["filename"], im["subfolder"], im["type"])
                    ims.append(Image.open(io.BytesIO(_req(q))).convert("RGB"))
            return ims
        time.sleep(0.5)


def upload(img, name):
    """Upload a PIL image to ComfyUI's input folder (multipart form); returns the stored name."""
    buf = io.BytesIO()
    img.save(buf, "PNG")
    bnd = "----rt%s" % uuid.uuid4().hex
    body = (("--%s\r\nContent-Disposition: form-data; name=\"image\"; filename=\"%s\"\r\nContent-Type: image/png\r\n\r\n"
             % (bnd, name)).encode() + buf.getvalue() +
            ("\r\n--%s\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--%s--\r\n" % (bnd, bnd)).encode())
    r = json.loads(_req("/upload/image", body, "multipart/form-data; boundary=%s" % bnd))
    return r["name"] if not r.get("subfolder") else r["subfolder"] + "/" + r["name"]


def wf_txt2img(pos, neg, seed, w=W, h=H, steps=30, cfg=5.5):
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": pos, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}},
        "5": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0],
                                                   "latent_image": ["4", 0], "seed": seed, "steps": steps, "cfg": cfg,
                                                   "sampler_name": "euler_ancestral", "scheduler": "normal",
                                                   "denoise": 1.0}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": "rt_bust/base"}},
    }


def wf_inpaint(pos, neg, seed, image_name, mask_name, denoise, steps=30, cfg=5.5):
    """Masked img2img: only the white part of the mask is re-noised (SetLatentNoiseMask)."""
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": pos, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip": ["1", 1]}},
        "4": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "5": {"class_type": "LoadImageMask", "inputs": {"image": mask_name, "channel": "red"}},
        "6": {"class_type": "VAEEncode", "inputs": {"pixels": ["4", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SetLatentNoiseMask", "inputs": {"samples": ["6", 0], "mask": ["5", 0]}},
        "8": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0],
                                                   "latent_image": ["7", 0], "seed": seed, "steps": steps, "cfg": cfg,
                                                   "sampler_name": "euler_ancestral", "scheduler": "normal",
                                                   "denoise": denoise}},
        "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["1", 2]}},
        "10": {"class_type": "SaveImage", "inputs": {"images": ["9", 0], "filename_prefix": "rt_bust/face"}},
    }


def save_workflows():
    os.makedirs(WF_DIR, exist_ok=True)
    json.dump(wf_txt2img("<positive>", "<negative>", 0), open(os.path.join(WF_DIR, "bust_base_api.json"), "w"),
              indent=1)
    json.dump(wf_inpaint("<positive>", "<negative>", 0, "<face crop.png>", "<face mask.png>", 0.6),
              open(os.path.join(WF_DIR, "bust_face_inpaint_api.json"), "w"), indent=1)


# ------------------------------------------------------------------------------------------------- stages
def save_png(im, path):
    """Atomic (tools/atomic_io.py: temp "<name>.tmp", then os.replace, retried while the game holds the file): the user
    plays while the agents work - the game must never read a half-written bust or see a "*.tmp.png"."""
    import atomic_io
    atomic_io.save_png(im, path)


def save_text(text, path):
    """Atomic text write (faces.json, RokuganBustData.sk), same scheme as atomic_io."""
    import atomic_io
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    atomic_io._replace(tmp, path)


def cdir(key):
    d = os.path.join(WORK, key)
    os.makedirs(d, exist_ok=True)
    return d


def style_for(c):
    """White hair / white clothes on white key badly: bg="grey" asks for a flat grey background instead."""
    return STYLE.replace("white background", "%s background" % c.get("bg", "white"))


def base_prompt(c, emo="neutral"):
    return "%s, %s, %s" % (style_for(c), c["prompt"], EMO[emo][0])


def label_font(size=22):
    for f in ("arial.ttf", "segoeui.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def sheet(images, labels, out, cols=4, tw=300, bg=(40, 36, 44)):
    th = int(tw * images[0].height / images[0].width)
    rows = (len(images) + cols - 1) // cols
    sh = Image.new("RGB", (cols * tw, rows * (th + 30)), bg)
    d = ImageDraw.Draw(sh)
    f = label_font(20)
    for i, (im, lb) in enumerate(zip(images, labels)):
        x, y = (i % cols) * tw, (i // cols) * (th + 30)
        t = im.convert("RGBA").resize((tw, th), Image.LANCZOS)
        if t.mode == "RGBA":
            chk = Image.new("RGBA", t.size, bg + (255,))
            chk.alpha_composite(t)
            t = chk
        sh.paste(t.convert("RGB"), (x, y))
        d.text((x + 8, y + th + 4), lb, fill=(240, 230, 200), font=f)
    save_png(sh, out)
    print("sheet", out)


def cand_path(key, seed):
    """Candidates are cached by seed AND prompt (a prompt edit makes new files instead of reusing old ones)."""
    import hashlib
    hp = hashlib.md5((base_prompt(CHARS[key]) + NEG + CKPT).encode()).hexdigest()[:6]
    return os.path.join(cdir(key), "cand_%d_%s.png" % (seed, hp))


def stage_base(key, seeds, tag=""):
    c = CHARS[key]
    d = cdir(key)
    ims, lbs = [], []
    for s in seeds:
        out = cand_path(key, s)
        if not os.path.exists(out):
            im = queue(wf_txt2img(base_prompt(c), neg_for((), c.get("neg_add", ())), s))[0]
            im.save(out)
            print("base", key, s)
        ims.append(Image.open(out))
        lbs.append("%s seed %d" % (key, s))
    sheet(ims, lbs, os.path.join(PREVIEW, "%s_candidates%s.png" % (key, tag and "_" + tag)), cols=min(4, len(ims)))


def base_image(key):
    """The approved neutral base: base_file (a kept candidate) or the candidate of the chosen seed."""
    c = CHARS[key]
    p = os.path.join(cdir(key), c["base_file"]) if c.get("base_file") else cand_path(key, c["seed"])
    if not os.path.exists(p):
        stage_base(key, [c["seed"]])
    return Image.open(p).convert("RGB")


def face_crop_box(c, im):
    """A square around the face box with margin (the inpaint context), clamped to the image."""
    x0, y0, x1, y1 = c["face"]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    side = int(max(x1 - x0, y1 - y0) * 1.9)
    bx0 = int(min(max(0, cx - side / 2), im.width - side))
    by0 = int(min(max(0, cy - side / 2), im.height - side))
    return bx0, by0, bx0 + side, by0 + side


def face_mask(c, box, size):
    """White ellipse over the face box inside the crop (crop coordinates scaled to size)."""
    x0, y0, x1, y1 = c["face"]
    bx0, by0, bx1, by1 = box
    k = size / (bx1 - bx0)
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    pad = 0.06 * (x1 - x0)
    d.ellipse([(x0 - pad - bx0) * k, (y0 - pad - by0) * k, (x1 + pad - bx0) * k, (y1 + pad - by0) * k], fill=255)
    return m


def full_face_mask(c, im):
    """The soft face mask in full-image coordinates (what an emotion changes)."""
    box = face_crop_box(c, im)
    bw = box[2] - box[0]
    m = face_mask(c, box, 1024).filter(ImageFilter.GaussianBlur(1024 * 0.02)).resize((bw, bw), Image.LANCZOS)
    full = Image.new("L", im.size, 0)
    full.paste(m, box[:2])
    return full


def neg_for(drop=(), add=()):
    return ", ".join([t for t in NEG.split(", ") if t not in drop] + list(add))


def stage_emotions(key, only=None):
    """<emo>.png = the base with the face re-drawn (face crop upscaled to 1024, masked img2img, pasted back)."""
    c = CHARS[key]
    d = cdir(key)
    base = base_image(key)
    base.save(os.path.join(d, "neutral.png"))
    box = face_crop_box(c, base)
    S = 1024
    crop = base.crop(box).resize((S, S), Image.LANCZOS)
    mask = face_mask(c, box, S)
    cname = upload(crop, "rt_bust_%s_face.png" % key)
    mname = upload(Image.merge("RGB", (mask, mask, mask)), "rt_bust_%s_mask.png" % key)
    soft = mask.filter(ImageFilter.GaussianBlur(S * 0.02))
    look = c.get("look", c["prompt"])
    for emo in EMOTIONS[1:]:
        if only and emo not in only:
            continue
        tags, den = EMO[emo]
        pos = ("masterpiece, best quality, amazing quality, very aesthetic, official art, game cg, thin clean lineart, "
               "soft shading, warm lighting, close-up, face, %s, (%s:1.2)" % (look, tags))
        im = queue(wf_inpaint(pos, NEG, c["seed"] + 7, cname, mname, den))[0].resize((S, S), Image.LANCZOS)
        face = Image.composite(im, crop, soft)               # only the face ellipse changes
        out = base.copy()
        bw = box[2] - box[0]
        out.paste(face.resize((bw, bw), Image.LANCZOS), box[:2])
        save_png(out, os.path.join(d, "%s.png" % emo))
        print("emotion", key, emo)


def variant_mask(c, im, regions):
    m = Image.new("L", im.size, 0)
    d = ImageDraw.Draw(m)
    if "body" in regions:
        d.rectangle([0, c["neck_y"], im.width, im.height], fill=255)
    if "crown" in regions:
        d.rectangle([0, 0, im.width, c["crown_y"]], fill=255)
    if "body" in regions and "crown" in regions:           # the sides of the head too (hair, hat brim, towel)
        x0, y0, x1, y1 = c["face"]
        d.rectangle([0, 0, x0 - 10, im.height], fill=255)
        d.rectangle([x1 + 10, 0, im.width, im.height], fill=255)
    face = full_face_mask(c, im).point(lambda v: 255 if v > 30 else 0)
    m = Image.fromarray(np.minimum(np.asarray(m), 255 - np.asarray(face)).astype(np.uint8))
    return m


def stage_variants(key, only=None):
    """var_<variant>.png: the neutral base re-dressed (inpainting outside the face; the face pixels are kept)."""
    c = CHARS[key]
    d = cdir(key)
    base = base_image(key)
    bname = upload(base, "rt_bust_%s_base.png" % key)
    look = c.get("look", c["prompt"])
    for vn in c.get("variants", []):
        if only and vn not in only:
            continue
        v = VARIANTS[vn]
        m = variant_mask(c, base, v["regions"])
        mname = upload(Image.merge("RGB", (m, m, m)), "rt_bust_%s_vmask.png" % key)
        vt = v["tags"].format(colors=c.get("colors", ""), court=c.get("court", "dark formal haori with a small white "
                              "family crest over a grey silk kimono"), night=c.get("night", "plain cotton yukata"))
        vt = c.get("vtags", {}).get(vn, vt)                     # per-character look override (user review)
        pos = "%s, %s, (%s:1.2), expressionless, calm" % (style_for(c), look, vt)
        im = queue(wf_inpaint(pos, neg_for(v.get("neg_drop", ()), list(v.get("neg_add", ())) +
                                          list(c.get("vneg", {}).get(vn, ()))), c["seed"] + 101 + v.get("seed_add", 0) + c.get("vseed", {}).get(vn, 0), bname, mname, v["denoise"]))[0]
        soft = m.filter(ImageFilter.GaussianBlur(6))
        out = Image.composite(im.resize(base.size, Image.LANCZOS), base, soft)
        save_png(out, os.path.join(d, "var_%s.png" % vn))
        print("variant", key, vn)


def variant_emotion(c, d, vn, emo):
    """A variant with an emotion: the emotion's face patch pasted onto the variant bust."""
    if vn == "base":
        return Image.open(os.path.join(d, "%s.png" % emo)).convert("RGB")
    var = Image.open(os.path.join(d, "var_%s.png" % vn)).convert("RGB")
    if emo == "neutral":
        return var
    em = Image.open(os.path.join(d, "%s.png" % emo)).convert("RGB")
    return Image.composite(em, var, full_face_mask(c, var))


# ------------------------------------------------------------------------------------------------- keying + export
MASKS = os.path.join(ROOT, "_art", "busts", "_masks")


def fg_mask(im):
    """BiRefNet foreground mask (ComfyUI LoadBackgroundRemovalModel + RemoveBackground, models/background_removal/
    birefnet.safetensors), cached by the image's content: user 2026-11-11 'see through eyes and hair ... clean up edges
    that are white when they should be cut out' - colour keying can't tell a white kimono from a white background."""
    import hashlib
    rgb = im.convert("RGB")
    key = hashlib.md5(rgb.tobytes()).hexdigest()
    p = os.path.join(MASKS, key + ".png")
    if not os.path.exists(p):
        os.makedirs(MASKS, exist_ok=True)
        name = upload(rgb, "bustmask_%s.png" % key[:12])
        wf = {"1": {"class_type": "LoadImage", "inputs": {"image": name}},
              "2": {"class_type": "LoadBackgroundRemovalModel", "inputs": {"bg_removal_name": "birefnet.safetensors"}},
              "3": {"class_type": "RemoveBackground", "inputs": {"bg_removal_model": ["2", 0], "image": ["1", 0]}},
              "4": {"class_type": "MaskToImage", "inputs": {"mask": ["3", 0]}},
              "5": {"class_type": "SaveImage", "inputs": {"images": ["4", 0], "filename_prefix": "bustmask"}}}
        out = queue(wf)
        out[0].convert("L").resize(rgb.size, Image.LANCZOS).save(p)
    return Image.open(p).convert("L")


def repair_holes(bg, dist, h, w, hair_y, prot, cv2):
    """(user, 2026-11-11: "see through eyes, and hair ... the mirumoto's neck was all fucked up for bath busts") The
    background pass also took pale parts of the figure: eye whites, white kimono and fur, Gendo's towel and neck (the
    border flood leaked in through a pale edge). Give back (1) every transparent island the outside can't reach,
    unless it is pure background colour (a real gap between arm and body) or a thin sliver between hair strands
    above the neck; (2) below the neck, every bite a 15 px closing of the figure seals that isn't pure background."""
    neck = int(hair_y or 0.62 * h)
    fig = ~bg
    n, lab, st, _ = cv2.connectedComponentsWithStats(bg.astype(np.uint8), 8)
    for i in range(1, n):
        x0, y0, bw, bh, area = st[i]
        if x0 == 0 or y0 == 0 or x0 + bw >= w or y0 + bh >= h:
            continue                                              # the outside
        isl = lab == i
        md = np.median(dist[isl])                                 # (pure white can be cloth as well as a gap:
        sliver = min(bw, bh) <= 6 or max(bw, bh) >= 4 * min(bw, bh) or area < 0.35 * bw * bh
        if sliver and md <= 10 and not isl[prot].any() and (
                (y0 + bh < neck and area < 6000) or min(bw, bh) <= 6):
            continue                                              # between hair strands: stays cut (user)
        # busts are cropped at the chest: an arm-body gap is rare, a white kimono or fur collar is not)
        fig |= isl
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    closed = cv2.morphologyEx(fig.astype(np.uint8), cv2.MORPH_CLOSE, k).astype(bool)
    bite = closed & ~fig
    bite[:neck] = False
    bite &= dist > 3                                              # pale cloth, not the pure background colour
    fig |= bite
    return ~fig


def cut_enclosed_bg(m, dist, prot, hair_y, flood, cv2, lum=None):
    """BiRefNet sometimes keeps a patch of the flat background enclosed between hair and face (npc_akodo_rin): cut
    kept regions of the pure background colour that are big and flat (eye whites, teeth and highlights are small or
    shaded), above the shoulders, not in the face core, and - what tells it from a white towel or hat top (pure white
    cloth too; Gendo's bath and travel busts) - reached by the colour key's border flood, which the lineart stops.
    The patch's rim (the anti-aliased band) goes too."""
    h, w = m.shape
    lim = int(hair_y or 0.58 * h)                                 # (NPCs have no neck line: Rin's collar starts at .62)
    cand = (m > 0.5) & (dist <= 5)
    n, lab, st, _ = cv2.connectedComponentsWithStats(cand.astype(np.uint8), 8)
    cut = np.zeros((h, w), bool)
    for i in range(1, n):
        x0, y0, bw, bh, area = st[i]
        if area >= 900 and y0 + bh >= h - 2:
            # vignette busts: the art fades out above the frame bottom and BiRefNet keeps the white below it as a white
            # bib (Doji Sanae, Maho Puppet, Naohida): exact background colour (median 0-1 from it; white cloth cut by
            # the frame has shading, 3-5)
            isl = lab == i
            if np.median(dist[isl]) <= 1 and not (prot.any() and isl[prot].any()):
                cut |= isl
                print("  cut kept background (bottom) %d px at %d,%d %dx%d" % (area, x0, y0, bw, bh))
            continue
        if area < 900 or min(bw, bh) < 12 or y0 >= lim:          # starts above the shoulders (may reach below)
            continue
        isl = lab == i
        if prot.any() and isl[prot].any():
            continue
        if np.median(dist[isl]) > 2:
            continue
        if flood[isl].mean() < 0.5:
            # enclosed (the flood can't get in): a gap between hair strands and the neck (Natsuko's ponytail, Rensei,
            # Shizue's bath hair) is ringed by dark hair/lineart; a towel or hat top by light cloth shading. Only with
            # a face box: its core protects the eye whites, which are ringed by dark lashes too (NPCs: flood rule only)
            if not prot.any():
                continue
            ring = cv2.dilate(isl.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool) & ~isl & (m > 0.5)
            rl = lum[ring]
            if not rl.size or np.median(rl) > 140 or (rl < 100).mean() < 0.3:
                continue
        cut |= isl
        print("  cut kept background %d px at %d,%d %dx%d" % (area, x0, y0, bw, bh))
    if cut.any():
        grow = cv2.dilate(cut.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & (dist < 40)
        m = m.copy()
        m[grow] = 0
    # white fringe: background kept along the silhouette, outside the lineart (the flood got there, BiRefNet didn't
    # cut it): a 4 px band next to the cut-out
    band = cv2.dilate((m < 0.5).astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
    fr = band & flood & (dist <= 8) & (m >= 0.5)
    if fr.any():
        m = m.copy()
        m[fr] = 0
    return m


def cut_edge_hue(m, a, dist, prot, hue, cv2):
    """Scenery the source art kept at the frame's sides (Sayo's base and night busts: green plant leaves left and right;
    BiRefNet counts them as foreground). CHARS[key]["cut_edge_hue"] = (h0, h1) in OpenCV hue (0-180): cut regions of
    that hue near the left or right frame edge (outer 8%), with their dark outlines, and any opaque bits left loose."""
    h, w = m.shape
    hsv = cv2.cvtColor(a.astype(np.uint8), cv2.COLOR_RGB2HSV)
    g = (hsv[..., 0] >= hue[0]) & (hsv[..., 0] <= hue[1]) & (hsv[..., 1] > 50) & (hsv[..., 2] > 40) & (m > 0.5)
    n, lab, st, _ = cv2.connectedComponentsWithStats(g.astype(np.uint8), 8)
    leaf = np.zeros((h, w), bool)
    for i in range(1, n):
        x0, y0, bw, bh, area = st[i]
        if area >= 150 and (x0 <= 0.08 * w or x0 + bw >= 0.92 * w):    # at the sides (the obi is central)
            leaf |= lab == i
    if not leaf.any():
        return m
    lum = a.mean(axis=2)
    for _ in range(3):                                            # grow over the leaves' lineart and the white between
        leaf |= cv2.dilate(leaf.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & (g | (lum < 70) | (dist < 40))
    leaf &= ~prot
    m = m.copy()
    m[leaf] = 0
    n, lab, st, _ = cv2.connectedComponentsWithStats((m > 0.5).astype(np.uint8), 8)
    if n > 2:                                                     # leaf bits cut loose from the figure
        big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        for i in range(1, n):
            if i != big and st[i, cv2.CC_STAT_AREA] < 0.02 * h * w:
                m[lab == i] = 0
    print("  cut edge scenery %d px" % int(leaf.sum()))
    return m


def key_out(im, tol=12, protect=None, hair_y=None, holes=True, repair=False, fixed_alpha=None, edge_hue=None):
    """Flat background -> alpha. Flood fill from the border through pixels close to the corner colour, then soften the
    edge by one pixel and pull the background tint out of the semi-transparent rim."""
    a = np.asarray(im.convert("RGB")).astype(np.int16)
    h, w = a.shape[:2]
    border = np.concatenate([a[1:4].reshape(-1, 3), a[:, 1:4].reshape(-1, 3), a[:, -4:-1].reshape(-1, 3)])
    q = (border // 8).astype(np.int32)                          # the most common border colour, not the median:
    code = q[:, 0] * 1024 + q[:, 1] * 32 + q[:, 2]                # a hat / staff along the top row skewed the median
    top = np.bincount(code).argmax()
    bgc = np.median(border[code == top], axis=0)
    near = np.abs(a - bgc).max(axis=2) <= tol
    import cv2
    ff = near.astype(np.uint8)
    seed_mask = np.zeros((h + 2, w + 2), np.uint8)
    filled = np.zeros((h, w), np.uint8)
    # busts (repair): seed only along the top and the sides above the neck - the frame cuts a white kimono or towel at
    # the bottom/lower sides, and a flood started there ran into it (Sayo's court kimono, Gendo's bath towel)
    side_to = int((hair_y or 0.5 * h)) if repair else h
    seeds = [(0, 0), (0, w - 1)] + ([] if repair else [(h - 1, 0), (h - 1, w - 1)]) + \
        [(0, xx) for xx in range(0, w, 16)] + [(yy, 0) for yy in range(0, side_to, 16)] + \
        [(yy, w - 1) for yy in range(0, side_to, 16)]
    for (y, x) in seeds:
        if ff[y, x] and not filled[y, x]:
            tmp = ff.copy()
            seed_mask[:] = 0
            cv2.floodFill(tmp, seed_mask, (x, y), 2)
            filled |= (tmp == 2)
    bg = filled.astype(bool)
    flood = bg.copy()
    # holes inside the figure that are background (between arm and body): big enough near-bg islands
    # small ones too between hair strands: pure background colour, above the neck (hair_y), not in the face core
    # (eye whites, teeth); below the neck white is cloth / armour shine and stays
    prot = np.zeros((h, w), bool) if protect is None else np.asarray(protect) > 200
    if prot.any():                       # only the face's core (eyes, mouth): its rim is where the hair slivers are
        ys, xs = np.nonzero(prot)
        k = max(3, int((xs.max() - xs.min()) * 0.22)) | 1
        prot = cv2.erode(prot.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    dist = np.abs(a - bgc).max(axis=2)
    n, lab, stats, _ = cv2.connectedComponentsWithStats((near & ~bg).astype(np.uint8))
    for i in range(1, n):
        isl = lab == i
        area = stats[i, cv2.CC_STAT_AREA]
        bw, bh = stats[i, cv2.CC_STAT_WIDTH], stats[i, cv2.CC_STAT_HEIGHT]
        top = stats[i, cv2.CC_STAT_TOP] + bh
        if isl[prot].any() if prot.any() else False:
            continue
        flat = np.median(dist[isl]) <= 10
        # white slivers between hair strands (user): thin or long islands of the background colour, anywhere above
        # the neck; compact ones (eye whites, teeth, highlights) stay unless the face data says it's hair
        sliver = area > 12 and flat and (min(bw, bh) <= 6 or max(bw, bh) >= 4 * min(bw, bh)
                                         or area < 0.35 * bw * bh)
        if (holes and area > 2500 and np.median(dist[isl]) <= 4) or                 (sliver and top < (hair_y or 0.62 * h)) or                 (hair_y and area > 25 and top < hair_y and flat):
            bg |= isl
    # the light anti-aliased halo the flood fill stopped at: grow the background into near-white (2 px), and drop
    # loose bits that aren't attached to the figure (steam puffs, a hat brim cut by the frame)
    for _ in range(2):
        grow = cv2.dilate(bg.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        bg |= grow & (dist < 48) & ~prot
    n, lab, stats, _ = cv2.connectedComponentsWithStats((~bg).astype(np.uint8))
    if n > 2:
        big = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        for i in range(1, n):
            if i != big and stats[i, cv2.CC_STAT_AREA] < 0.02 * h * w:
                bg |= lab == i
    if repair:                                                    # busts only (sprites keep their leg gaps)
        bg = repair_holes(bg, dist, h, w, hair_y, prot, cv2)
    alpha = (~bg).astype(np.float32)
    alpha = cv2.GaussianBlur(cv2.erode(alpha, np.ones((3, 3), np.uint8)), (5, 5), 0)
    alpha = np.clip(alpha, 0, 1)
    if fixed_alpha is not None:                                   # the variant's silhouette (stage_export: one BiRefNet
        alpha = np.asarray(fixed_alpha).astype(np.float32) / 255.0  # pass per variant, the emotions only re-colour)
    elif repair:                                                  # busts: BiRefNet's mask is the cut-out (holes,
        try:                                                      # eye whites, white kimono, hair, white fringes)
            m = np.asarray(fg_mask(im)).astype(np.float32) / 255.0
            m = np.clip((m - 0.08) / 0.84, 0, 1)                  # firm up the soft band a little
            m = cut_enclosed_bg(m, dist, prot, hair_y, flood, cv2, lum=a.mean(axis=2))
            if edge_hue:
                m = cut_edge_hue(m, a, dist, prot, edge_hue, cv2)
            if prot.any():
                m = np.maximum(m, prot.astype(np.float32))        # the face core never goes see-through
            alpha = m
        except Exception as ex:                                   # ComfyUI down: the colour key stands
            print("bust mask unavailable (%s): colour key used" % ex)
    rgb = a.astype(np.float32)
    # decontaminate: c = alpha*f + (1-alpha)*bg  ->  f = (c - (1-alpha)*bg)/alpha on the rim
    rim = (alpha > 0.02) & (alpha < 0.98)
    f = rgb.copy()
    f[rim] = (rgb[rim] - (1 - alpha[rim, None]) * bgc) / alpha[rim, None]
    f = np.clip(f, 0, 255)
    out = np.dstack([f, alpha * 255]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def estimate_chin(rgba):
    """NPC busts have no face box: guess the chin from the silhouette (the neck is the narrowest row between the head
    and the shoulders). Returns the chin as a fraction of the height, or None. Override per key in CHIN_FIX."""
    a = np.asarray(rgba.getchannel("A")) > 128
    h = a.shape[0]
    w = a.sum(axis=1).astype(float)
    if not w.any():
        return None
    w = np.convolve(w, np.ones(9) / 9, mode="same")
    y0, y1 = int(0.30 * h), int(0.68 * h)
    head = w[int(0.12 * h):int(0.45 * h)].max()
    ys = [y for y in range(y0, y1) if w[y] < 0.8 * head]
    if not ys:
        return None
    y = min(ys, key=lambda yy: w[yy])
    return round(max(0.40, min(0.66, y / h - 0.02)), 4)


# chin height (fraction of the exported image) where the silhouette guess is wrong (checked on chin sheets)
CHIN_FIX = {"npc_mamoru": 0.4, "npc_abbot_of_osano_wo": 0.42, "npc_herald": 0.5, "npc_oyuki": 0.5, "npc_yoritomo_rui": 0.46, "npc_seppun_ushimo": 0.42, "npc_beggar": 0.52, "npc_imuro": 0.4, "npc_isawa_hoju": 0.38, "npc_bayushi_shiruko": 0.44, "npc_shosuro_noburo": 0.48, "npc_doji_himeko": 0.4, "npc_hostess": 0.42, "npc_mirumoto_koshi": 0.46, "npc_ronin_yojimbo": 0.4, "npc_bandit": 0.46, "npc_sariko": 0.32, "npc_village_herbalist": 0.32, "ryoichi": 0.29, "npc_kakita_sensei": 0.56, "npc_matsu_kiku": 0.43, "npc_wall_veteran": 0.5, "npc_hida_kisada": 0.45, "npc_fishwife": 0.43, "fujio": 0.4, "gonta": 0.53, "goro": 0.4, "kage": 0.43, "kiyo": 0.47, "mai": 0.4, "michio": 0.43, "npc_akodo_hiruto": 0.48, "npc_akodo_rin": 0.45, "npc_akodo_shogen": 0.45, "npc_asako_keiki": 0.5, "npc_asako_kuhime": 0.37, "npc_ashigaru_archer": 0.43, "npc_cart_driver": 0.5, "npc_child": 0.57, "npc_crab_bushi": 0.57, "npc_doji_nashiko": 0.48, "npc_doji_sanae": 0.45, "npc_gate_guard": 0.51, "npc_goblin_prisoner": 0.51, "npc_gonbei": 0.5, "npc_hida_taneo": 0.5, "npc_hida_veteran": 0.51, "npc_hiruma_kenzo": 0.5, "npc_hiruma_messenger": 0.5, "npc_hiruma_scout": 0.5, "npc_hoshi_fisherman": 0.44, "npc_ide_keiyomi": 0.37, "npc_innkeeper": 0.45, "npc_isawa_akiko": 0.5, "npc_isawa_kamasari": 0.53, "npc_isawa_mieko": 0.53, "npc_isawa_mutsuye": 0.53, "npc_kaiu_engineer": 0.5, "npc_kaiu_sapper": 0.54, "npc_kaiu_smith": 0.43, "npc_kitsuki_seigen": 0.48, "npc_kuni_shugenja": 0.4, "npc_kuni_taira": 0.45, "npc_kuni_witch_hunter": 0.43, "npc_maho_puppet": 0.45, "npc_merchant": 0.45, "npc_naohida": 0.48, "npc_oni_no_kommei": 0.48, "npc_runner": 0.51, "npc_sentry": 0.54, "npc_shiba_ashimita": 0.56, "npc_shinjo_o_shito": 0.45, "npc_shosuro_norie": 0.54, "npc_shosuro_shiko": 0.5, "npc_soshi_nihime": 0.45, "npc_troll": 0.57, "npc_yasuki_kanbe": 0.51, "npc_yasuki_kurako": 0.45, "npc_yogo_scribe": 0.43, "npc_yogo_shigeru": 0.48, "ryozo": 0.4, "sachiko": 0.4, "sakura": 0.4, "satomi": 0.36, "squeak": 0.42, "takakana": 0.52, "takeo": 0.45, "tomoe": 0.45, "yosai": 0.53, "npc_guard_sergeant": 0.43, "npc_broken_guard": 0.4, "npc_gonta_s_boy": 0.5, "npc_nezumi_shaman": 0.36, "npc_servant": 0.42, "npc_crab_guard": 0.4, "npc_kitchen_servant": 0.52, "npc_nezumi_warrior": 0.38, "npc_akodo_ijako": 0.4, "npc_jinnai": 0.4, "npc_shinjo_tsune": 0.42, "npc_akodo_gusai": 0.48, "npc_iuchi_karasu": 0.4, "npc_iuchi_daiyu": 0.45, "npc_akodo_kafu": 0.45, "npc_maid": 0.37, "npc_akodo_toturi": 0.4, "npc_hantei_kusada": 0.38, "npc_kakita_masanori": 0.47, "npc_kitsuki_oharu": 0.42, "npc_kitsune_hana": 0.45, "npc_lion_sergeant": 0.45, "npc_masked_citizen": 0.45, "npc_ship_s_master": 0.52, "npc_shosuro_osuko": 0.42, "npc_stich_kik": 0.48}


def stage_export(key):
    """Every variant x emotion: key out the background (one silhouette per variant), trim, scale to BUST_H, write
    resource/bust/<key>/<emotion>.png (base) and <variant>_<emotion>.png, and the preview sheets."""
    c = CHARS[key]
    d = cdir(key)
    os.makedirs(os.path.join(RES, key), exist_ok=True)
    emos = [e for e in EMOTIONS if os.path.exists(os.path.join(d, "%s.png" % e))]
    allims, alllbs, faces, out_base = [], [], {}, None
    for vn in ["base"] + [v for v in c.get("variants", []) if os.path.exists(os.path.join(d, "var_%s.png" % v))]:
        base_alpha, bb, out_ims = None, None, []
        for emo in emos:
            im = variant_emotion(c, d, vn, emo)
            if c.get("flip"):
                im = im.transpose(Image.FLIP_LEFT_RIGHT)
            fm = full_face_mask(c, im) if c.get("face") else None
            if fm is not None and c.get("flip"):
                fm = fm.transpose(Image.FLIP_LEFT_RIGHT)
            rgba = key_out(im, protect=fm, hair_y=c.get("neck_y"), holes=c.get("holes", c.get("bg", "white") == "white"),
                           repair=True, fixed_alpha=base_alpha, edge_hue=c.get("cut_edge_hue"))
            if base_alpha is None:                            # one silhouette per variant (the face pass is inside)
                base_alpha = rgba.getchannel("A")
                bb = base_alpha.point(lambda v: 255 if v > 8 else 0).getbbox()
            t = rgba.crop((bb[0], bb[1], bb[2], rgba.height))   # trim the sides and top; keep the bottom edge
            if emo == emos[0] and c.get("face"):                # where the face sits in the exported image (0..1)
                fx0, fy0, fx1, fy1 = c["face"]
                if c.get("flip"):
                    fx0, fx1 = im.width - fx1, im.width - fx0
                faces[vn] = [round((fx0 + fx1) / 2 - bb[0], 1) / t.width, round(fy0 - bb[1], 1) / t.height,
                             round(fy1 - bb[1], 1) / t.height]
            k = BUST_H / t.height
            t = t.resize((max(1, int(t.width * k)), BUST_H), Image.LANCZOS)
            save_png(t, os.path.join(RES, key, ("%s.png" % emo) if vn == "base" else ("%s_%s.png" % (vn, emo))))
            out_ims.append(t)
        sheet(out_ims, ["%s %s: %s" % (key, vn, e) for e in emos],
              os.path.join(PREVIEW, "%s_%s_emotions.png" % (key, vn)), cols=4, tw=280)
        allims += out_ims[:1]
        if vn == "base":
            out_base = out_ims[0]
        alllbs.append("%s: %s" % (key, vn))
    if "base" not in faces and out_base is not None:            # NPC: no face box, guess the chin
        ch = CHIN_FIX.get(key) or estimate_chin(out_base)
        if ch:
            faces["base"] = [0.5, round(ch - 0.25, 4), ch]
    save_text(json.dumps(faces, indent=1), os.path.join(RES, key, "faces.json"))
    if len(allims) > 1:
        sheet(allims, alllbs, os.path.join(PREVIEW, "%s_variants.png" % key), cols=len(allims), tw=280)
    write_data()


def write_data():
    """plugin/rokugan/RokuganBustData.sk: speaker name -> bust key, and each key's emotions (only exported files)."""
    lines = ["//\tGenerated by tools/gen_busts.py (do not edit): dialog busts in resource/bust/<key>/<emotion>.png.",
             "::Rokugan.bustnames <- {"]
    keys, vars_ = {}, {}
    for key, c in CHARS.items():
        rd = os.path.join(RES, key)
        if not os.path.isdir(rd):
            continue
        emos = [e for e in EMOTIONS if os.path.exists(os.path.join(rd, "%s.png" % e))]
        if not emos:
            continue
        keys[key] = emos
        vars_[key] = [v for v in c.get("variants", []) if os.path.exists(os.path.join(rd, "%s_neutral.png" % v))]
        for n in c["names"]:
            lines.append('\t[%s] = "%s",' % (json.dumps(n), key))    # names may hold quotes ('"Ryozo"')
    lines.append("};")
    lines.append("::Rokugan.bustemos <- {")
    for key, emos in keys.items():
        lines.append('\t["%s"] = [%s],' % (key, ", ".join('"%s"' % e for e in emos)))
    lines.append("};")
    # face centre x, face top y, chin y (fractions of the image) per look ("base" + variants): the plugin places the
    # bust so the chin clears the dialog box and its name tab
    lines.append("::Rokugan.bustfaces <- {")
    for key in keys:
        fp = os.path.join(RES, key, "faces.json")
        if os.path.exists(fp):
            fc = json.load(open(fp))
            lines.append('	["%s"] = { %s },' % (key, ", ".join('["%s"] = [%.4f, %.4f, %.4f]' % (v, *f)
                                                               for v, f in fc.items())))
    lines.append("};")
    lines.append("::Rokugan.bustmapscene <- { %s };" % ", ".join('["%s"] = "%s"' % kv for kv in MAP_SCENES.items()))
    lines.append("::Rokugan.bustvars <- {")
    for key, vs in vars_.items():
        lines.append('\t["%s"] = [%s],' % (key, ", ".join('"%s"' % v for v in vs)))
    lines.append("};")
    save_text("\n".join(lines) + "\n", DATA_SK)
    print("wrote", DATA_SK, list(keys))


def main():
    os.makedirs(PREVIEW, exist_ok=True)
    save_workflows()
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    st = args[0]
    if st == "data":
        write_data()
        return
    if st == "npcpicks":                                # export every NPC with a pick (resource/bust/<key>)
        for k, c in CHARS.items():
            if c.get("npc") and (c.get("seed") or c.get("base_file")):
                save_png(base_image(k), os.path.join(cdir(k), "neutral.png"))
                stage_export(k)
        return
    key = args[1]
    opt = dict(zip(args[2::2], args[3::2]))
    if st == "base":
        seeds = [int(s) for s in opt.get("--seeds", "").split(",") if s] or \
                [random.Random(key).randrange(1, 10 ** 6) + i for i in range(8)]
        stage_base(key, seeds, opt.get("--tag", ""))
    elif st == "emotions":
        stage_emotions(key, opt.get("--only", "").split(",") if "--only" in opt else None)
    elif st == "variants":
        stage_variants(key, opt.get("--only", "").split(",") if "--only" in opt else None)
    elif st == "npc":                                   # one neutral bust: the picked candidate, keyed and exported
        save_png(base_image(key), os.path.join(cdir(key), "neutral.png"))
        stage_export(key)
    elif st == "export":
        stage_export(key)
    elif st == "all":
        stage_emotions(key)
        stage_variants(key)
        stage_export(key)


if __name__ == "__main__":
    main()
