"""Bake every traveler's equipment looks (another weapon type, or a head item) from their own rig.

py -3.12 -E tools\\rig3d_looks.py --review trav_gendo      # one row per look, nothing installed
py -3.12 -E tools\\rig3d_looks.py --install                # bake and install every reachable look
The look list is the plugin's: gen_sprites2d.look_combos, minus each traveler's own base look.
"""
import argparse
import json
from multiprocessing import Pool

from PIL import Image

import rig3d
import rig3d_sheet as sheet

RESOURCE = rig3d.ROOT / "_tools" / "rpgcobo-tool" / "project" / "resource"


def looks():
    import gen_sprites2d as sprites
    models = json.loads((RESOURCE / "enemy_pic.json").read_text(encoding="utf-8"))
    found = []
    for index, traveler in enumerate(sprites.TRAVELERS):
        own = sprites.base_look(traveler)
        for _, ep, weapon, hat in sprites.look_combos(index, traveler):
            if (weapon, hat) != own:
                name = models[ep]["pic3d"].rsplit("/", 1)[-1][:-4]
                found.append((index, name, None if weapon in (own[0], "kakita") else weapon, hat or None))
    return found


def mannequin(index, name, weapon, hat):
    import gen_sprites2d as sprites
    traveler = sprites.TRAVELERS[index]
    m = rig3d.Mannequin("trav_" + traveler["key"], weapon, hat, traveler)
    m.key = name
    return m


def bake(look):
    m = mannequin(*look)
    image, extra, grid = sheet.build_sheet(m)
    image.save(RESOURCE / "enemy_pic2x" / f"{m.key}.png", optimize=True)
    return m.key, extra, grid, m.size, m.ground_y


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--install", action="store_true")
    parser.add_argument("--review", metavar="PROFILE")
    parser.add_argument("--poses", default="idle8:0,fidle:0,bidle:0,ready:0,atk_slash:3,atk_overhead:2")
    args = parser.parse_args()
    found = looks()
    if args.review:
        import gen_sprites2d as sprites
        chosen = [look for look in found if "trav_" + sprites.TRAVELERS[look[0]]["key"] == args.review]
        counts = {name: (kind, count, view) for name, kind, count, view in sheet.plan()[0]}
        poses = args.poses.split(",")
        page = Image.new("RGB", (len(poses) * 174, len(chosen) * 170), (37, 39, 48))
        for row, look in enumerate(chosen):
            m = mannequin(*look)
            for column, pose in enumerate(poses):
                kind, count, view = counts[pose.rsplit(":", 1)[0]]
                image = sheet.frame(m, kind, int(pose.rsplit(":", 1)[1]), count, view).crop((30, 14, 204, 184))
                page.paste(image, (column * 174, row * 170), image)
        out = rig3d.ROOT / "_art" / "preview" / "rig3d" / "looks.png"
        page.save(out)
        print(f"{len(chosen)} looks ({', '.join(look[1].split('__')[1] for look in chosen)}): {out}")
    elif args.install:
        with Pool(6) as pool:
            done = pool.map(bake, found, chunksize=1)
        sheet.register([key for key, *_ in done], done[0][1], done[0][2], done[0][3], done[0][4])
        print(f"installed {len(done)} looks")
    else:
        print(f"{len(found)} looks to bake")


if __name__ == "__main__":
    main()
