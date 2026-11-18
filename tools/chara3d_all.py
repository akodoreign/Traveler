"""Rebuild the whole roster as 3-D-backed pixel art, in parallel on this machine's CPU.

py -3.12 -E tools\\chara3d_all.py                       # bake every character into _art\\preview\\chara3d\\sheets
py -3.12 -E tools\\chara3d_all.py --install             # ...and install each finished sheet into the game
py -3.12 -E tools\\chara3d_all.py --install --release 20   # ...and push a new game version every 20 characters
py -3.12 -E tools\\chara3d_all.py --only trav_natsuko side_goro --force
py -3.12 -E tools\\chara3d_all.py --list                # what is done and what is left

Order: travelers, then companions, hirelings, then the rest of the cast (NPCs and human foes).
Progress is kept in tools\\chara3d_done.json, keyed by a hash of the builder scripts, so a run can be stopped
and resumed, and an improved builder re-bakes everything on the next run. A character that fails is logged
and skipped; the run carries on.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

from PIL import Image

import chara3d_sheet as c3
import rig3d
import rig3d_sheet as sheet

TOOLS = rig3d.ROOT / "tools"
DONE = TOOLS / "chara3d_done.json"
RESOURCE = rig3d.ROOT / "_tools" / "rpgcobo-tool" / "project" / "resource"
SHEETS = rig3d.ROOT / "_art" / "preview" / "chara3d" / "sheets"
SOURCES = ("blender/chara3d.py", "chara3d_sheet.py", "rig3d_poses.py")


def version():
    """Changes whenever the model builder, the pixel pass or the pose library changes."""
    digest = hashlib.sha1()
    for name in SOURCES:
        digest.update((TOOLS / name).read_bytes())
    return digest.hexdigest()[:12]


def roster():
    """Every registered human sheet that has a look spec: (sheet name, group), in rollout order."""
    import gen_sidecast as cast
    import gen_sprites2d as sprites
    import hirelings
    models = json.loads((RESOURCE / "enemy_pic.json").read_text(encoding="utf-8"))
    registered = {entry["pic3d"].rsplit("/", 1)[-1][:-4] for entry in models.values()
                  if isinstance(entry, dict) and entry.get("pic3d")}
    companions = [line.split('SC_EP["')[1].split('"')[0] for line in
                  (TOOLS / "gen_data.py").read_text(encoding="utf-8").splitlines()
                  if line.lstrip().startswith('("P1') and 'SC_EP["' in line]
    order = [("trav_" + t["key"], "traveler") for t in sprites.TRAVELERS]
    order += [("side_" + key, "companion") for key in companions]
    order += [("side_" + h["key"], "hireling") for h in hirelings.HIRELINGS]
    order += [("side_" + c["key"], "cast") for c in cast.CAST]
    seen, out = set(), []
    for name, group in order:
        if name in registered and name not in seen:
            seen.add(name)
            out.append((name, group))
    return out


def bake(key):
    """One character: Blender renders every frame, the pixel pass assembles the sheet. Runs in a worker."""
    started = time.time()
    clips, cols = sheet.plan()
    folder = c3.render(key, [(kind, index, count, view) for _, kind, count, view in clips for index in range(count)])
    palette = json.loads((folder / "meta.json").read_text())["palette"]
    total = sum(count for _, _, count, _ in clips)
    grid = (cols, -(-total // cols))
    image = Image.new("RGBA", (c3.SIZE[0] * grid[0], c3.SIZE[1] * grid[1]))
    for i in range(total):
        image.alpha_composite(c3.pixelize(folder, i, palette), ((i % cols) * c3.SIZE[0], (i // cols) * c3.SIZE[1]))
    SHEETS.mkdir(parents=True, exist_ok=True)
    image.save(SHEETS / f"{key}.png", optimize=True)
    for raw in folder.glob("*.png"):            # the raw passes are large and only needed once
        raw.unlink()
    return key, grid, round(time.time() - started)


def install(keys, grid):
    """Copy finished sheets into the game and point their registrations at them, keeping each world size."""
    path = RESOURCE / "enemy_pic.json"
    models = json.loads(path.read_text(encoding="utf-8"))
    extra = c3.extra_clips()
    for key in keys:
        (RESOURCE / "enemy_pic2x" / f"{key}.png").write_bytes((SHEETS / f"{key}.png").read_bytes())
    for entry in models.values():
        name = entry.get("pic3d", "").rsplit("/", 1)[-1][:-4] if isinstance(entry, dict) else None
        if name not in keys:
            continue
        if "/enemy_pic2x/" not in entry["pic3d"]:
            entry["scale1x"] = entry["scale"]
            entry["scale"] /= 2
        half = entry.get("scale1x", entry["scale"] * 2) / 2      # world units per pixel of the 2x sheets
        entry["scale"] = half / c3.SCALE                         # these sheets are SCALE times finer again
        entry["pic3d"] = f"/resource/enemy_pic2x/{name}.png"
        entry["aniuv"] = list(grid)
        entry["gndpos"] = [.5, (c3.SIZE[1] - c3.ORIGIN[1] - 1) / c3.SIZE[1]]
        entry["animap"] = [clip for clip in entry["animap"] if clip["id"] not in extra] + list(extra.values())
    path.write_text(json.dumps(models, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def battle_ok():
    """A real engine battle with rebuilt sprites must still run to its end."""
    done = subprocess.run([sys.executable, "-E", str(TOOLS / "testbattle.py"), "3", "--lv", "60", "--rt",
                           "party P101;party P132", "--wait", "150"], capture_output=True, text=True, cwd=rig3d.ROOT)
    text = done.stdout + done.stderr
    return "won/ended" in text and "Exception in thread" not in text


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--install", action="store_true", help="install finished sheets into the game")
    parser.add_argument("--release", type=int, metavar="N", help="with --install: test and push a version every N")
    parser.add_argument("--only", nargs="+", metavar="KEY", help="just these sheet names")
    parser.add_argument("--group", choices=("traveler", "companion", "hireling", "cast"))
    parser.add_argument("--limit", type=int, help="stop after this many characters")
    parser.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 4) - 2))
    parser.add_argument("--force", action="store_true", help="re-bake even if already done at this version")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    if args.release and not args.install:
        parser.error("--release needs --install")
    stamp = version()
    done = json.loads(DONE.read_text(encoding="utf-8")) if DONE.is_file() else {}
    wanted = [(name, group) for name, group in roster()
              if (not args.only or name in args.only) and (not args.group or group == args.group)]
    todo = [name for name, _ in wanted if args.force or done.get(name, {}).get("version") != stamp
            or (args.install and not done[name].get("installed"))]
    if args.list:
        print(f"builder {stamp}: {len(wanted) - len(todo)} done, {len(todo)} to do of {len(wanted)}")
        print(" ".join(todo))
        return
    todo = todo[:args.limit] if args.limit else todo
    print(f"builder {stamp}: baking {len(todo)} characters on {args.workers} workers")
    pending, failed, started = [], [], time.time()

    def flush(final=False):
        if not pending or not args.install:
            return
        if args.release and (len(pending) >= args.release or final):
            if not battle_ok():
                sys.exit("battle check failed after installing; nothing was pushed (git checkout to undo)")
            message = f"3-D-backed pixel art: {len(pending)} characters ({pending[0]} ... {pending[-1]})"
            subprocess.run([sys.executable, "-E", str(TOOLS / "release_here.py"), message, str(DONE)],
                           check=True, cwd=rig3d.ROOT)
            pending.clear()

    with ProcessPoolExecutor(args.workers) as pool:
        jobs = {pool.submit(bake, name): name for name in todo}
        for number, job in enumerate(as_completed(jobs), 1):
            name = jobs[job]
            try:
                key, grid, seconds = job.result()
            except Exception as exc:                              # one bad character must not stop the run
                failed.append(name)
                print(f"[{number}/{len(todo)}] {name}: FAILED {str(exc).strip().splitlines()[-1][:200]}")
                continue
            done[key] = {"version": stamp, "installed": bool(args.install)}
            if args.install:
                install([key], grid)
                pending.append(key)
            DONE.write_text(json.dumps(done, indent=1, sort_keys=True) + "\n", encoding="utf-8")
            print(f"[{number}/{len(todo)}] {key}: {seconds}s", flush=True)
            flush()
    flush(final=True)
    print(f"finished {len(todo) - len(failed)} of {len(todo)} in {round((time.time() - started) / 60)} min"
          + (f"; failed: {' '.join(failed)}" if failed else ""))


if __name__ == "__main__":
    main()
