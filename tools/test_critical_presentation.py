"""Run deterministic crit-presentation checks in the real engine; capture title/action/cleanup.

py -3.12 -E tools\\test_critical_presentation.py
Uses fixture-only animation aliases, not generated/replacement art or changed production crit chances.
Pass --cutout to exercise the installed pilot artwork without aliases.
"""
import argparse
from pathlib import Path
import subprocess
import time

import engine_lock
import playbot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cutout", action="store_true")
    options = parser.parse_args()
    name = "cutout" if options.cutout else "critical"
    label = "CUTOUT" if options.cutout else "CRIT"
    script = "test_cutout_ingame.sk" if options.cutout else "test_critical_presentation.sk"
    captures = (tuple(f"{key}_{pose}" for key in ("natsuko", "rensei")
                      for pose in ("gesture", "critical", "void"))
                if options.cutout else ("title", "action", "cleared"))
    root = Path(__file__).resolve().parent.parent
    tool = root / "_tools" / "rpgcobo-tool"
    out = root / "_art" / "preview" / f"{name}_presentation"
    out.mkdir(parents=True, exist_ok=True)
    shots = tool / "tmp" / "rt_shot"
    shots.mkdir(parents=True, exist_ok=True)
    for capture in captures:
        (shots / f"bot_{name}_{capture}.raw").unlink(missing_ok=True)
        (out / f"{name}_{capture}.png").unlink(missing_ok=True)
    log = out / "engine.log"
    args = [str(tool / "rpgcobo.exe"), "-testplay", "-battle", "M001", "3", "-debuglv", "20",
            "-rtfast", "-rtbot", f"evalf,../../tools/{script}"]
    if options.cutout:
        args += ["-rtparty", "P101"]
    with log.open("w") as output:
        proc = engine_lock.launch(args, cwd=tool, stdout=output, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic() + 100
            while proc.poll() is None and time.monotonic() < deadline:
                text = log.read_text(errors="replace")
                if f"[RT] {label} TEST COMPLETE" in text or "TEST FAIL" in text or "Exception in thread" in text:
                    break
                time.sleep(0.25)
        finally:
            engine_lock.stop(proc)
            proc.wait(timeout=10)
    text = log.read_text(errors="replace")
    for line in text.splitlines():
        if label + " " in line or "Exception in thread" in line or "ERROR" in line:
            print(line)
    if f"[RT] {label} TEST COMPLETE" not in text or "TEST FAIL" in text or "Exception in thread" in text:
        raise RuntimeError(f"{name} presentation checks failed; see {log}")
    playbot.convert_shots(name, str(out))
    for capture in captures:
        if not (out / f"{name}_{capture}.png").is_file():
            raise RuntimeError(f"Missing {capture} screenshot")
    print(f"Passed; screenshots and engine log: {out}")


if __name__ == "__main__":
    main()
