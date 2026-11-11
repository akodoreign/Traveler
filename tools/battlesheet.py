"""Contact sheets of the story player's battle shots (user, 2026-11-11: watch for backwards sprites and bad frames).
python -E tools/battlesheet.py story_0 [--from N]  -> _art/preview/bot/story_0/battles_K.png (6 battles a sheet,
frame 0 of each burst, labelled with the enemies from the log)."""
import os
import re
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_maps as gm  # noqa: E402

SHOTS = os.path.join(gm.TOOL, "tmp", "rt_shot")


def raw(path):
    b = open(path, "rb").read()
    w, h = int.from_bytes(b[0:4], "little"), int.from_bytes(b[4:8], "little")
    return Image.fromarray(np.frombuffer(b[8:8 + w * h * 4], np.uint8).reshape(h, w, 4)[..., :3].copy())


def main():
    name = sys.argv[1]
    start = int(sys.argv[sys.argv.index("--from") + 1]) if "--from" in sys.argv else 1
    out = os.path.join(HERE, "..", "_art", "preview", "bot", name)
    log = open(os.path.join(out, "log.txt"), errors="replace").read()
    names = {int(n): (m, en) for n, m, en in re.findall(r"BOT battle shot (\d+) (M\d+): ([^\n]*)", log)}
    nums = sorted(n for n in names if n >= start and os.path.exists(
        os.path.join(SHOTS, "bot_%s_battle_%03d_0.raw" % (name, n))))
    for k in range(0, len(nums), 6):
        chunk = nums[k:k + 6]
        tiles = []
        for n in chunk:
            im = raw(os.path.join(SHOTS, "bot_%s_battle_%03d_0.raw" % (name, n))).resize((640, 360))
            d = ImageDraw.Draw(im)
            d.rectangle((0, 0, 640, 18), fill=(0, 0, 0))
            d.text((4, 3), "#%d %s: %s" % (n, names[n][0], names[n][1][:80]), fill=(255, 255, 0))
            tiles.append(im)
        sheet = Image.new("RGB", (1280, 360 * ((len(tiles) + 1) // 2)))
        for i, t in enumerate(tiles):
            sheet.paste(t, ((i % 2) * 640, (i // 2) * 360))
        p = os.path.join(out, "battles_%03d.png" % chunk[0])
        sheet.save(p)
        print(p)


if __name__ == "__main__":
    main()
