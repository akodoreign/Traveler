"""Fast travel on every road: each listed town loads beside its clan post; the log shows what the menu offers.
    python -E tools/test_travel.py [M349 M202 ...]   -> _art/preview/travel_<map>.png + .log"""
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine_lock  # noqa: E402
import gen_maps as gm  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "_tools" / "rpgcobo-tool"
OUT = ROOT / "_art" / "preview"
LEAD = {"P101": "P101", "P102": "P102", "P103": "P103", "P104": "P104", "P105": "P105", "P106": "P106", "P107": "P107"}


def run(mid):
    code, name, _m, pids = gm.TRAVEL_AUTO_MAP[mid]
    gm.make(mid)
    x, z = gm.TRAVEL_SPOT[mid]
    mm, _ = gm.make(mid)
    y = (int(mm.hgt[z, x]) + 1) / 2.0
    shots = TOOL / "tmp" / "rt_shot"
    shots.mkdir(parents=True, exist_ok=True)
    raw = shots / "bot_travel.raw"
    raw.unlink(missing_ok=True)
    log = OUT / ("travel_%s.log" % mid)
    args = [str(TOOL / "rpgcobo.exe"), "-testplay", "-map", mid, "[%.2f,%.2f,%.2f,180.0]" % (x / 2.0, y, (z - 4) / 2.0),
            "-rtparty", pids[0], "-debuglv", "20",
            "-rtbot", "wait,800|evalf,../../tools/test_travel.sk|wait,3000"]
    with log.open("w") as fh:
        proc = engine_lock.launch(args, cwd=TOOL, stdout=fh, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic() + 120
            while proc.poll() is None and time.monotonic() < deadline:
                if "TRAVEL TEST COMPLETE" in log.read_text(errors="replace"):
                    time.sleep(1.0)
                    break
                time.sleep(0.5)
        finally:
            subprocess.run(["taskkill", "/PID", str(proc.pid), "/F"], capture_output=True)
    for line in log.read_text(errors="replace").splitlines():
        if "TRAVEL" in line or "xception" in line or "travel:" in line:
            print(mid, line[:240])
    if raw.exists() and raw.stat().st_size > 8:
        b = raw.read_bytes()
        w, h = int.from_bytes(b[0:4], "little"), int.from_bytes(b[4:8], "little")
        a = np.frombuffer(b[8:8 + w * h * 4], np.uint8).reshape(h, w, 4)
        out = OUT / ("travel_%s.png" % mid)
        Image.fromarray(a[..., :3].copy()).save(out)
        print("shot", out)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for mid in sys.argv[1:] or ["M202", "M304", "M255", "M282", "M349", "M396", "M416"]:
        run(mid)
