"""Copy finished AI sprite sheets into the game (user, 2026-11-08: for demos). Safe to rerun as more sheets finish.
Each frame the AI drew replaces that frame of the game's sheet; originals are kept once in pixelai/game_sheets_orig.
python -E tools/install_aisheets.py [--started] [key ...]     (--started: unfinished sheets too)
python -E tools/install_aisheets.py --restore                 (put every original back)"""
import json
import os
import re
import shutil
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PX = os.path.normpath(os.path.join(HERE, "..", "_art", "preview", "agents", "pixelai"))
PIC = os.path.normpath(os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "resource", "enemy_pic"))
SPECS, ORIG = os.path.join(HERE, "pixelai_specs"), os.path.join(PX, "game_sheets_orig")
FW, FH, COLS = 80, 68, 14


def main():
    a = sys.argv[1:]
    os.makedirs(ORIG, exist_ok=True)
    if "--restore" in a:
        for f in os.listdir(ORIG):
            shutil.copy(os.path.join(ORIG, f), os.path.join(PIC, f))
            print("restored", f)
        return
    want = [x for x in a if not x.startswith("--")]
    for key in sorted(os.listdir(os.path.join(PX, "sheets"))):
        d = os.path.join(PX, "sheets", key)
        spec = os.path.join(SPECS, key + ".json")
        if not os.path.isdir(d) or not os.path.exists(spec) or (want and key not in want):
            continue
        if not (os.path.exists(os.path.join(d, "complete")) or "--started" in a or key in want):
            continue
        sheet = json.load(open(spec, encoding="utf-8"))["sheet"]
        if not os.path.exists(os.path.join(ORIG, sheet)):
            shutil.copy(os.path.join(PIC, sheet), os.path.join(ORIG, sheet))
        im = Image.open(os.path.join(ORIG, sheet)).convert("RGBA")
        n = 0
        for f in os.listdir(d):
            if re.fullmatch(r"f\d{3}\.png", f):
                i = int(f[1:4])
                xy = ((i % COLS) * FW, (i // COLS) * FH)
                im.paste((0, 0, 0, 0), (xy[0], xy[1], xy[0] + FW, xy[1] + FH))
                im.alpha_composite(Image.open(os.path.join(d, f)).convert("RGBA"), xy)
                n += 1
        im.save(os.path.join(PIC, sheet))
        print("installed", key, n, "frames ->", sheet)
        # anim_harmonize.py (2026-11-11): its harmonized sheet replaces this one while the AI frames are unchanged
        hz = os.path.normpath(os.path.join(HERE, "..", "_art", "preview", "agents", "anim_harmonize"))
        st = json.load(open(os.path.join(hz, "state.json"))) if os.path.exists(os.path.join(hz, "state.json")) else {}
        if st.get(key, {}).get("status") == "installed" and os.path.exists(os.path.join(hz, "out", sheet)):
            import hashlib                                # same fingerprint as anim_harmonize.ai_fp
            h = hashlib.sha1()
            for f in sorted(os.listdir(d)):
                if len(f) == 8 and f.startswith("f") and f.endswith(".png"):
                    s_ = os.stat(os.path.join(d, f))
                    h.update(("%s %d %d;" % (f, s_.st_size, int(s_.st_mtime))).encode())
            if h.hexdigest() == st[key]["ai_fp"]:
                shutil.copy(os.path.join(hz, "out", sheet), os.path.join(PIC, sheet))
                print("  harmonized sheet re-applied")


if __name__ == "__main__":
    main()
