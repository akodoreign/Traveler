"""Run test_companion_void.py for every companion with a prelude and build a review sheet:
_art/preview/companion_void/review.png (per companion: mid-gesture | ward lit, cropped to the party side).
    python -E tools/test_companion_void_all.py [P120 ...]"""
from pathlib import Path
import re
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
PLUG = ROOT / "_tools" / "rpgcobo-tool" / "project" / "plugin" / "rokugan" / "RokuganCompanionVoid.sk"
OUT = ROOT / "_art" / "preview" / "companion_void"
CROP = (640, 20, 1120, 330)


def main():
    pids = sys.argv[1:] or re.findall(r"^\t(P\d+) = E\(", PLUG.read_text(encoding="utf-8"), re.M)
    rows, bad = [], []
    for pid in pids:
        r = subprocess.run([sys.executable, "-E", str(ROOT / "tools" / "test_companion_void.py"), pid],
                           capture_output=True, text=True, cwd=ROOT / "tools")
        ok = r.returncode == 0
        print(pid, "PASS" if ok else "FAIL")
        if not ok:
            bad.append(pid)
            print(r.stdout[-600:])
        shots = []
        for c in ("rally", "icons"):
            src = OUT / f"compvoid_{c}.png"
            if src.exists():
                dst = OUT / f"{pid}_{c}.png"
                shutil.copy(src, dst)
                shots.append(Image.open(dst).crop(CROP))
        rows.append((pid, shots))
    w, h = CROP[2] - CROP[0], CROP[3] - CROP[1]
    sheet = Image.new("RGB", (w * 2, (h + 18) * len(rows)), (20, 20, 24))
    d = ImageDraw.Draw(sheet)
    for i, (pid, shots) in enumerate(rows):
        d.text((4, i * (h + 18) + 2), pid, fill=(255, 220, 120))
        for j, s in enumerate(shots):
            sheet.paste(s, (j * w, i * (h + 18) + 18))
    sheet.save(OUT / "review.png")
    print("review", OUT / "review.png", "failed:", bad)


if __name__ == "__main__":
    main()
