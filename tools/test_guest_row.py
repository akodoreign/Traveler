"""Guests in the third row (tools/test_guest_row.sk): the last three guests met, beside the hireling.
    python -E tools/test_guest_row.py        -> _art/preview/guest_row.png"""
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
from PIL import Image

import engine_lock

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "_tools" / "rpgcobo-tool"
OUT = ROOT / "_art" / "preview"
CAPS = ("guestrow",)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    shots = TOOL / "tmp" / "rt_shot"
    shots.mkdir(parents=True, exist_ok=True)
    for c in CAPS:
        (shots / f"bot_{c}.raw").unlink(missing_ok=True)
    log = OUT / "guest_row.log"
    args = [str(TOOL / "rpgcobo.exe"), "-testplay", "-battle", "M001", "3", "-debuglv", "20",
            "-rtparty", "P101", "-rtvar", "G233,G234,G235,G236,G293=1,G294=3", "-rtbot", "wait,600|evalf,../../tools/test_guest_row.sk|wait,3000"]
    with log.open("w") as fh:
        proc = engine_lock.launch(args, cwd=TOOL, stdout=fh, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic() + 120
            while proc.poll() is None and time.monotonic() < deadline:
                if "GUEST TEST COMPLETE" in log.read_text(errors="replace"):
                    time.sleep(1.0)
                    break
                time.sleep(0.5)
        finally:
            subprocess.run(["taskkill", "/PID", str(proc.pid), "/F"], capture_output=True)
    for line in log.read_text(errors="replace").splitlines():
        if "GUEST TEST" in line or "xception" in line:
            print(line[:200])
    for c in CAPS:
        raw = shots / f"bot_{c}.raw"
        if raw.exists() and raw.stat().st_size > 8:
            b = raw.read_bytes()
            w, h = int.from_bytes(b[0:4], "little"), int.from_bytes(b[4:8], "little")
            a = np.frombuffer(b[8:8 + w * h * 4], np.uint8).reshape(h, w, 4)
            Image.fromarray(a[..., :3].copy()).save(OUT / f"guest_row.png")
            print("shot", OUT / f"guest_row.png")


if __name__ == "__main__":
    main()
