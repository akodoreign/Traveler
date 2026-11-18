"""Sample native body skin colors from dedicated neutral dialogue busts."""
import json
import re
from functools import cache

import numpy as np
from PIL import Image


# Face boxes for these portraits include hats, tattoos, or heavy shadows.
CHEEK = {"natsuko": (0.56, 0.42), "goro": (0.54, 0.40), "yosai": (0.46, 0.29)}
FACE_BOX = {"npc_isawa_sanro": (0.49, 0.20, 0.43)}


@cache
def speaker_busts(resource):
    source = (resource.parent / "plugin" / "rokugan" / "RokuganBustData.sk").read_text(encoding="utf-8")
    return dict(re.findall(r'\["([^"]+)"\] = "([^"]+)"', source.split("};", 1)[0]))


def sample_skin(image, face):
    """Estimate cheek midtones, not the darkest shadow or brightest highlight."""
    x, top, chin = face
    span = chin - top
    if span <= 0:
        return None
    w, h = image.size
    half = min(w * 0.21, h * span * 0.34)
    if half < 3:
        return None
    crop = image.crop((round(x * w - half), round(h * (top + 0.43 * span)),
                       round(x * w + half), round(h * (top + 0.72 * span))))
    pixels = np.asarray(crop.convert("RGBA"), dtype=np.int16).reshape(-1, 4)
    r, g, b, a = pixels.T
    # Reject background, hair, eyes, strongly colored accessories and specular highlights.
    rgb = pixels[(a >= 245) & (r >= 68) & (r - g >= 5) & (r - g <= 100)
                 & (g - b >= -3) & (g - b <= 85) & (r - b >= 10) & (r - b <= 150), :3]
    if len(rgb) < max(30, len(pixels) * 0.36):
        return None
    light = rgb @ [0.2126, 0.7152, 0.0722]
    lo, hi = np.percentile(light, [55, 85])
    return [int(round(c)) for c in np.median(rgb[(light >= lo) & (light <= hi)], axis=0)]


@cache
def portrait_skin(resource, bust):
    folder = resource / "bust" / bust
    anchor = folder / "faces.json"
    neutral = folder / "neutral.png"
    if not neutral.is_file():
        return None
    with Image.open(neutral) as image:
        if bust in CHEEK:
            x, y = CHEEK[bust]
            cx, cy = round(x * image.width), round(y * image.height)
            crop = image.crop((cx - 4, cy - 4, cx + 5, cy + 5)).convert("RGB")
            return [int(c) for c in np.median(np.asarray(crop).reshape(-1, 3), axis=0)]
        face = FACE_BOX.get(bust)
        if face is None and anchor.is_file():
            face = json.loads(anchor.read_text(encoding="utf-8")).get("base")
        return sample_skin(image, face) if face else None


def native_skin(resource, key, spec):
    bust = key.removeprefix("trav_") if key.startswith("trav_") else speaker_busts(resource).get(spec.get("name"))
    tone = portrait_skin(resource, bust) if bust else None
    if tone is None:
        return None
    # Keep some of the authored color to temper the bust's directional lighting.
    return [round(0.75 * sampled + 0.25 * base) for sampled, base in zip(tone, spec["skin"])]
