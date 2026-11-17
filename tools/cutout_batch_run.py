"""One roster batch end to end: register seven cast keys with their two drawn atlases, cut the parts,
bake every sheet on the 3-D rig, install them, and write a review page.

py -3.12 -E tools\\cutout_batch_run.py cast3 cores.png limbs.png key1 ... key7
"""
import json
import shutil
import sys
from multiprocessing import Pool

import rig3d
import rig3d_sheet as sheet

RESOURCE = rig3d.ROOT / "_tools" / "rpgcobo-tool" / "project" / "resource"


def bake(key):
    m = rig3d.Mannequin(key)
    image, extra, grid = sheet.build_sheet(m)
    image.save(RESOURCE / "enemy_pic2x" / f"{key}.png", optimize=True)
    return key, extra, grid, m.size, m.ground_y


def main():
    if len(sys.argv) != 11:
        sys.exit(__doc__)
    name, cores, limbs, *keys = sys.argv[1:]
    import build_cutout_batch as build
    if any(key in batch for other, batch in build.BATCHES.items() if other != name for key in keys):
        sys.exit("A key is already in another batch")
    build.BATCHES[name] = keys
    for source, kind in ((cores, "cores"), (limbs, "limbs")):
        shutil.copyfile(source, build.SOURCE / f"{name}_{kind}.png")
    names = build.prepare_batch(name)
    with Pool(7) as pool:
        done = pool.map(bake, names, chunksize=1)
    sheet.register(names, done[0][1], done[0][2], done[0][3], done[0][4])
    models = json.loads((RESOURCE / "enemy_pic.json").read_text(encoding="utf-8"))
    installed = {entry["pic3d"].rsplit("/", 1)[-1][:-4] for entry in models.values()
                 if isinstance(entry, dict) and entry.get("aniuv") == list(done[0][2])}
    if not set(names) <= installed:
        sys.exit(f"Not installed: {sorted(set(names) - installed)}")
    build.BATCH_FILE.write_text(json.dumps(build.BATCHES, indent=1) + "\n", encoding="utf-8")
    out = rig3d.ROOT / "_art" / "preview" / "rig3d" / f"{name}.png"
    sheet.review(names, "idle8:0,fidle:0,bidle:0,walk8:2,ready:0,atk_slash:3,atk_overhead:2,talk:1".split(","), out)
    print(f"{name}: installed {', '.join(names)}; review {out}")


if __name__ == "__main__":
    main()
