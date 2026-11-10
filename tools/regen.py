"""Rebuild the game data in the right order (NOTES: "gen_render LAST"; gen_data re-registers every map, which drops
gen_render's battle cameras, lighting presets and weather until gen_render runs again).
python -E tools/regen.py [--maps] [MAP ...]
  --maps      rebuild map geometry first (gen_maps.py; all maps, or only the MAP ids given)
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run(script, *args):
    print("==", script, " ".join(args))
    r = subprocess.run([sys.executable, "-E", os.path.join(HERE, script), *args])
    if r.returncode:
        sys.exit(r.returncode)


def main():
    a = sys.argv[1:]
    if "--maps" in a:
        a.remove("--maps")
        run("gen_maps.py", *a)
    run("gen_data.py")
    run("gen_render.py")
    run("apply_bust_emotions.py")
    run("apply_dialog_fixes.py")


if __name__ == "__main__":
    main()
