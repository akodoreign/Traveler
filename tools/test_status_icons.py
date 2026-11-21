"""Screenshots of the status icons in a real battle (tools/test_status_icons.sk).
    python -E tools/test_status_icons.py        -> _art/preview/status_icons_rows.png, status_icons_pop.png"""
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
CAPS = ("rows", "pop", "hover1", "hover2")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    shots = TOOL / "tmp" / "rt_shot"
    shots.mkdir(parents=True, exist_ok=True)
    for c in CAPS:
        (shots / f"bot_icons_{c}.raw").unlink(missing_ok=True)
    log = OUT / "status_icons.log"
    args = [str(TOOL / "rpgcobo.exe"), "-testplay", "-battle", "M001", "3", "-debuglv", "20",
            "-rtparty", "P101,P102,P103", "-rtbot", "wait,600|evalf,../../tools/test_status_icons.sk|wait,3000"]
    with log.open("w") as fh:
        proc = engine_lock.launch(args, cwd=TOOL, stdout=fh, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic() + 120
            while proc.poll() is None and time.monotonic() < deadline:
                if "ICON TEST COMPLETE" in log.read_text(errors="replace"):
                    time.sleep(1.0)
                    break
                time.sleep(0.5)
        finally:
            subprocess.run(["taskkill", "/PID", str(proc.pid), "/F"], capture_output=True)
    for line in log.read_text(errors="replace").splitlines():
        if "ICON TEST" in line or "xception" in line:
            print(line[:200])
    for c in CAPS:
        raw = shots / f"bot_icons_{c}.raw"
        if raw.exists() and raw.stat().st_size > 8:
            b = raw.read_bytes()
            w, h = int.from_bytes(b[0:4], "little"), int.from_bytes(b[4:8], "little")
            a = np.frombuffer(b[8:8 + w * h * 4], np.uint8).reshape(h, w, 4)
            Image.fromarray(a[..., :3].copy()).save(OUT / f"status_icons_{c}.png")
            print("shot", OUT / f"status_icons_{c}.png")


if __name__ == "__main__":
    main()
