"""The busts a playthrough showed, on review sheets (user, 2026-11-11: keep track of bad bust art to re-queue it).
python -E tools/bustsheet.py story_0   -> _art/preview/bot/story_0/busts_K.png (24 a sheet, each labelled with the
speaker and file, in the order they first appeared). Bad ones go in tools/bad_busts.json."""
import os
import re
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
BUST = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "resource", "bust")


def main():
    name = sys.argv[1]
    out = os.path.join(HERE, "..", "_art", "preview", "bot", name)
    lines = open(os.path.join(out, "log.txt"), errors="replace").read().splitlines()
    seen, order = {}, []
    for i, ln in enumerate(lines):
        m = re.search(r"\[RT\] BUST (\S+)", ln)
        if m and m.group(1) not in seen:
            who = next((re.sub(r"^.*\[RT\] MSG ([^:]*):.*$", r"\1", x) for x in lines[i + 1:i + 3] if "[RT] MSG" in x), "")
            seen[m.group(1)] = who
            order.append(m.group(1))
    tw, th = 220, 260
    for k in range(0, len(order), 24):
        chunk = order[k:k + 24]
        sheet = Image.new("RGB", (tw * 6, th * ((len(chunk) + 5) // 6)), (40, 40, 48))
        d = ImageDraw.Draw(sheet)
        for j, f in enumerate(chunk):
            x, y = (j % 6) * tw, (j // 6) * th
            p = os.path.join(BUST, f)
            if os.path.exists(p):
                im = Image.open(p).convert("RGBA")
                im.thumbnail((tw - 10, th - 34))
                sheet.paste(im, (x + 5, y + 4), im)
            else:
                d.text((x + 8, y + 100), "MISSING", fill=(255, 80, 80))
            d.text((x + 4, y + th - 28), "%d %s\n%s" % (k + j + 1, seen[f][:30], f[:34]), fill=(255, 255, 160))
        pth = os.path.join(out, "busts_%02d.png" % (k // 24))
        sheet.save(pth)
        print(pth, len(chunk))


if __name__ == "__main__":
    main()
