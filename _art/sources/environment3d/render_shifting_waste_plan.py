"""Draw the six compiled Shifting Waste terrain layouts from the world generator."""

from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont


root = Path(sys.argv[1])
sys.path.insert(0, str(root / "tools"))
import gen_maps as maps


def render(out):
    page = Image.new("RGB", (2160, 1160), "#151319")
    draw = ImageDraw.Draw(page)
    fonts = Path("C:/Windows/Fonts")
    title = ImageFont.truetype(str(fonts / "georgia.ttf"), 62)
    label = ImageFont.truetype(str(fonts / "segoeui.ttf"), 26)
    detail = ImageFont.truetype(str(fonts / "segoeui.ttf"), 22)
    draw.text((62, 30), "The Shifting Waste", fill="#f3e5d7", font=title)
    draw.text((65, 115), "Six terrain layouts from the game map generator", fill="#c3acaa", font=label)
    colors = {
        maps.ROAD: (157, 111, 87),
        maps.SL_GROUND: (76, 64, 80),
        maps.SL_ASH: (104, 92, 103),
        maps.STONE: (52, 47, 63),
        maps.TARSTAIN: (119, 50, 66),
        maps.POPPYF: (119, 50, 66),
        maps.EMBER: (119, 50, 66),
    }
    terrain = slice(maps.PAD_BOTTOM, maps.PAD_BOTTOM + 48), slice(maps.PAD_X, maps.PAD_X + 72)
    for index, mid in enumerate(maps.MAZE):
        world, _ = maps.make(mid)
        blocks, height = world.blk[terrain], world.hgt[terrain]
        rgb = np.full((48, 72, 3), (56, 48, 58), dtype=float)
        for material, color in colors.items():
            rgb[blocks == material] = color
        west = np.column_stack((height[:, 0], height[:, :-1]))
        north = np.vstack((height[0], height[:-1]))
        shade = np.clip((height - west) * 0.07 + (height - north) * 0.10, -0.32, 0.40)
        rgb *= 1 + shade[..., None]
        panel = Image.fromarray(np.uint8(rgb.clip(0, 255))[::-1]).resize((576, 384), Image.Resampling.NEAREST)
        x, y = 84 + index % 3 * 706, 196 + index // 3 * 462
        page.paste(panel, (x, y))
        draw.rectangle((x - 1, y - 1, x + panel.width, y + panel.height), outline="#6b575f", width=2)
        draw.text((x, y - 34), f"{mid}   |   Maze state {index + 1}", fill="#ead9ce", font=label)
        for pos, tag, anchor in (
            ((x-8,y+180),"W","ra"), ((x+584,y+180),"E","la"),
            ((x+284,y-3),"N","ms"), ((x+284,y+385),"S","ma"),
        ):
            draw.text(pos, tag, anchor=anchor, fill="#ffdfb0", font=detail)
        if index in (2, 4):
            chest_x, chest_z = (54, 34) if index == 2 else (18, 12)
            cx, cz = x + chest_x * 8 + 4, y + (47-chest_z) * 8 + 4
            draw.rectangle((cx-5,cz-5,cx+5,cz+5), fill="#ffe7a1", outline="#33231d", width=2)

    legend = (
        ((157, 111, 87), "Walkable trail"), ((52, 47, 63), "Shale ridge"),
        ((119, 50, 66), "Tainted ground"), ((255, 231, 161), "Side chest"),
    )
    for index, (swatch, text) in enumerate(legend):
        x = 85 + index * 285
        draw.rectangle((x,1118,x+21,1139),fill=swatch)
        draw.text((x+30,1113),text,fill="#d9c8c1",font=detail)
    page.save(out, quality=93)


if __name__ == "__main__":
    render(Path(sys.argv[2]))
