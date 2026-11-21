"""Screenshots: a guest's call (name over them in the back row) and the field message when a guest leaves.
    python -E tools/test_guest_visual.py   -> _art/preview/guest_call.png, guest_field.png"""
from pathlib import Path
import subprocess
import time

import numpy as np
from PIL import Image

import engine_lock

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "_tools" / "rpgcobo-tool"
OUT = ROOT / "_art" / "preview"
VARS = "G233,G234,G235,G236,G293=1,G294=3"
RUNS = (("guestcall", ["-battle", "M001", "3", "-rtparty", "P101"]),
        ("guestfield", ["-map", "M202", "[37.5,2.00,9.5,0.0]"]))


def main():
    shots = TOOL / "tmp" / "rt_shot"
    shots.mkdir(parents=True, exist_ok=True)
    for cap, extra in RUNS:
        raw = shots / f"bot_{cap}.raw"
        raw.unlink(missing_ok=True)
        log = OUT / f"{cap}.log"
        args = [str(TOOL / "rpgcobo.exe"), "-testplay", *extra, "-debuglv", "20", "-rtvar", VARS,
                "-rtbot", "wait,600|evalf,../../tools/test_guest_visual.sk|wait,3000"]
        with log.open("w") as fh:
            proc = engine_lock.launch(args, cwd=TOOL, stdout=fh, stderr=subprocess.STDOUT)
            try:
                deadline = time.monotonic() + 120
                while proc.poll() is None and time.monotonic() < deadline:
                    if "GUESTVIS COMPLETE" in log.read_text(errors="replace"):
                        time.sleep(1.0)
                        break
                    time.sleep(0.5)
            finally:
                subprocess.run(["taskkill", "/PID", str(proc.pid), "/F"], capture_output=True)
        for line in log.read_text(errors="replace").splitlines():
            if "GUESTVIS" in line or "xception" in line or "parts ways" in line or "guest roster" in line:
                print(cap, line[:200])
        if raw.exists() and raw.stat().st_size > 8:
            b = raw.read_bytes()
            w, h = int.from_bytes(b[0:4], "little"), int.from_bytes(b[4:8], "little")
            a = np.frombuffer(b[8:8 + w * h * 4], np.uint8).reshape(h, w, 4)
            out = OUT / f"{cap.replace('guest', 'guest_')}.png"
            Image.fromarray(a[..., :3].copy()).save(out)
            print("shot", out)


if __name__ == "__main__":
    main()
