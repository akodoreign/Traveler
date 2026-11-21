"""Real-engine check that a companion's Void-critical gift reaches the party and stays for its turns.
    python -E tools/test_void_gift.py [P120 ...]      (default: every companion in VOID_SHOUT_PC)
Expectation (gen_data rem_turn [3, 3]): every living ally holds the gift in the round it lands and the next two."""
from pathlib import Path
import re
import subprocess
import sys
import time

import engine_lock

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "_tools" / "rpgcobo-tool"
PLUG = TOOL / "project" / "plugin" / "rokugan" / "RokuganCompanionVoid.sk"
OUT = ROOT / "_art" / "preview" / "companion_void"


def run(pid):
    log = OUT / f"gift_{pid}.log"
    args = [str(TOOL / "rpgcobo.exe"), "-testplay", "-battle", "M001", "3", "-debuglv", "20", "-rtfast",
            "-rtparty", pid, "-rtcv", pid, "-rtbot", "evalf,../../tools/test_void_gift.sk"]
    with log.open("w") as fh:
        proc = engine_lock.launch(args, cwd=TOOL, stdout=fh, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic() + 150
            while proc.poll() is None and time.monotonic() < deadline:
                if "GIFT TEST COMPLETE" in log.read_text(errors="replace"):
                    break
                time.sleep(0.5)
        finally:
            subprocess.run(["taskkill", "/PID", str(proc.pid), "/F"], capture_output=True)
    text = log.read_text(errors="replace")
    lines = [l for l in text.splitlines() if "GIFT TEST" in l or "xception" in l]
    fired = re.search(r"shout fired in round (\d+)", text)
    rounds = {int(r): h for r, h in re.findall(r"round (\d+) holders \[(.*)\]", text)}
    ok = bool(fired)
    if fired:
        # (the round counter ticks at the first living member's turn start; an attack logged in round f lands in
        # round f + 1 when the striker acts first) held for the round it lands and the two after, gone by the next
        land = max(1, int(fired.group(1)))
        if int(fired.group(1)) == 0:
            land = 1
        held = [rounds.get(land + k, "") for k in (0, 1, 2)]
        gone = rounds.get(land + 3)
        ok = all(h.strip() for h in held) and gone is not None and not gone.strip()
    return ok, lines


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pids = sys.argv[1:] or re.findall(r"^\t(P\d+) = \[", PLUG.read_text(encoding="utf-8"), re.M)
    bad = []
    for pid in pids:
        ok, lines = run(pid)
        print(pid, "OK" if ok else "PROBLEM")
        if not ok:
            bad.append(pid)
        for l in lines:
            print("   ", l[:160])
    print("problems:", bad)


if __name__ == "__main__":
    main()
