"""Screenshots of the dialog busts in-engine (no keys): each case starts the game on a map with -rtbustdemo, which shows
one dialog line with its bust (tags / guess / scene look as in events), and -rtshot saves the frame.
python -E tools/testbust.py                       (the default cases; sheet _art/preview/agents/busts/ingame_sheet.png)
python -E tools/testbust.py "Hiruma Natsuko|[angry] Get away from the cart!" ...
Waits instead of killing the game when rpgcobo.exe is already running (another agent or the user)."""
import os
import subprocess
import sys
import time

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.normpath(os.path.join(HERE, "..", "_tools", "rpgcobo-tool"))
OUT = os.path.join(HERE, "..", "_art", "preview", "agents", "busts")
CASES = [
    "Hiruma Natsuko|The old quarry trail. Kiyo said the Hidden Ones camp up there.",
    "Hiruma Natsuko|[angry] Get away from the cart, or I put this yari through you!",
    "Hiruma Natsuko|Thank you. Really. I owe you a drink.",
    "Hiruma Natsuko|[bath happy] Hot water. Real hot water. I could die here.",
    "Hiruma Natsuko|[travel worried] The road's too quiet. Keep your eyes on the trees...",
    "Hiruma Natsuko|[night sad] I couldn't save him. I keep seeing the Wall.",
    "Hida Tomoe|Rest, Natsuko. That is an order, not a suggestion.",
    "|The land-bridge at low tide. Narration has no bust.",
]


def running():
    r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq rpgcobo.exe"], capture_output=True, text=True)
    return "rpgcobo.exe" in r.stdout


def shot(case, n, mapid="M101", pos="[19.5,1.5,21.5,0]", wait_ms=9000):
    while running():
        print("rpgcobo.exe is running (someone else's test?): waiting")
        time.sleep(10)
    rel = "tmp/rt_shot/bust_%d_%d.raw" % (n, int(time.time()))
    raw = os.path.join(TOOL, rel)
    os.makedirs(os.path.dirname(raw), exist_ok=True)
    log = open(os.path.join(OUT, "ingame_%d.txt" % n), "w")
    proc = subprocess.Popen([os.path.join(TOOL, "rpgcobo.exe"), "-testplay", "-map", mapid, pos, "-debuglv", "9",
                             "-rtbustdemo", case, "-rtshot", rel, str(wait_ms)],
                            cwd=TOOL, stdout=log, stderr=subprocess.STDOUT)
    t0 = time.time()
    while time.time() - t0 < 60 and not (os.path.exists(raw) and os.path.getsize(raw) > 8):
        time.sleep(1.0)
    time.sleep(1.0)
    subprocess.run(["taskkill", "/PID", str(proc.pid), "/F"], capture_output=True)
    log.close()
    if not os.path.exists(raw):
        return None
    b = open(raw, "rb").read()
    w, h = int.from_bytes(b[0:4], "little"), int.from_bytes(b[4:8], "little")
    a = np.frombuffer(b[8:8 + w * h * 4], np.uint8).reshape(h, w, 4)
    im = Image.fromarray(a[..., :3].copy(), "RGB")
    im.save(os.path.join(OUT, "ingame_%d.png" % n))
    return im


def main():
    cases = sys.argv[1:] or CASES
    ims = []
    for n, c in enumerate(cases):
        im = shot(c, n)
        print(n, c, "ok" if im else "FAILED")
        ims.append(im)
    sheet = Image.new("RGB", (640 * 2, 360 * ((len(ims) + 1) // 2)), (0, 0, 0))
    d = ImageDraw.Draw(sheet)
    for n, im in enumerate(ims):
        x, y = (n % 2) * 640, (n // 2) * 360
        if im:
            sheet.paste(im.resize((640, 360)), (x, y))
        d.text((x + 6, y + 4), cases[n][:90], fill=(255, 255, 0))
    sheet.save(os.path.join(OUT, "ingame_sheet.png"))
    print("sheet", os.path.join(OUT, "ingame_sheet.png"))


if __name__ == "__main__":
    main()
