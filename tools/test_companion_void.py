"""Real-engine check of a companion Void critical prelude (RokuganCompanionVoid.sk): training dummy battle with the
companion in the party, one forced Void critical, screenshots of the rally and the icons over the party.
    python -E tools/test_companion_void.py [P120]
Output: _art/preview/companion_void/*.png + engine.log"""
from pathlib import Path
import subprocess
import sys
import time

import engine_lock
from PIL import Image
import numpy as np


def main():
    pid = sys.argv[1] if len(sys.argv) > 1 else "P120"
    root = Path(__file__).resolve().parent.parent
    tool = root / "_tools" / "rpgcobo-tool"
    out = root / "_art" / "preview" / "companion_void"
    out.mkdir(parents=True, exist_ok=True)
    shots = tool / "tmp" / "rt_shot"
    shots.mkdir(parents=True, exist_ok=True)
    caps = ("rally", "icons")
    for c in caps:
        (shots / f"bot_compvoid_{c}.raw").unlink(missing_ok=True)
    log = out / "engine.log"
    args = [str(tool / "rpgcobo.exe"), "-testplay", "-battle", "M001", "3", "-debuglv", "20", "-rtfast",
            "-rtparty", pid, "-rtcv", pid, "-rtbot", "evalf,../../tools/test_companion_void.sk"]
    with log.open("w") as fh:
        proc = engine_lock.launch(args, cwd=tool, stdout=fh, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic() + 120
            while proc.poll() is None and time.monotonic() < deadline:
                text = log.read_text(errors="replace")
                if "COMPVOID TEST COMPLETE" in text or "COMPVOID TEST FAIL" in text:
                    time.sleep(1.0)
                    break
                time.sleep(0.5)
        finally:
            subprocess.run(["taskkill", "/PID", str(proc.pid), "/F"], capture_output=True)
    text = log.read_text(errors="replace")
    for line in text.splitlines():
        if "COMPVOID" in line or "COMP VOID" in line or "CRIT PRESENT" in line or "ERROR" in line:
            print(line[:200])
    for c in caps:
        raw = shots / f"bot_compvoid_{c}.raw"
        if raw.exists() and raw.stat().st_size > 8:
            b = raw.read_bytes()
            w, h = int.from_bytes(b[0:4], "little"), int.from_bytes(b[4:8], "little")
            a = np.frombuffer(b[8:8 + w * h * 4], np.uint8).reshape(h, w, 4)
            Image.fromarray(a[..., :3].copy()).save(out / f"compvoid_{c}.png")
            print("shot", out / f"compvoid_{c}.png")
    sys.exit(0 if "COMPVOID TEST COMPLETE" in text else 1)


if __name__ == "__main__":
    main()
