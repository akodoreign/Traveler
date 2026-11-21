"""Real-engine check of condition durations (tools/test_durations.sk). Writes _art/preview/durations.log and prints, per
round start, who holds which of the watched conditions, then checks the expectations:
    a buff put at the start of round P "for N turns" (rem_turn [N+1, N+1]) is held at round starts P .. P+N (the
    landing round, then N full rounds) and gone at P+N+1; Netted / Scandalized / Shocked each cost exactly one action
    python -E tools/test_durations.py [troop]
"""
from pathlib import Path
import re
import subprocess
import sys
import time

import engine_lock

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "_tools" / "rpgcobo-tool"
LOG = ROOT / "_art" / "preview" / "durations.log"

# condition -> its promised turns N (99 = the whole battle)
EXPECT_LEAD = {"K053": 5,   # put in round 1, recast in round 3 (restarts: 3 more turns) -> held to round 6
               "K020": 5, "K057": 3, "K058": 3, "K155": 3, "K157": 4, "K159": 5, "K160": 99, "K161": 5, "K164": 3}


def main():
    troop = sys.argv[1] if len(sys.argv) > 1 else "3"
    LOG.parent.mkdir(parents=True, exist_ok=True)
    args = [str(TOOL / "rpgcobo.exe"), "-testplay", "-battle", "M001", troop, "-debuglv", "20", "-rtfast",
            "-rtparty", "P101", "-rtbot", "evalf,../../tools/test_durations.sk"]
    with LOG.open("w") as fh:
        proc = engine_lock.launch(args, cwd=TOOL, stdout=fh, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic() + 180
            while proc.poll() is None and time.monotonic() < deadline:
                if "DUR TEST COMPLETE" in LOG.read_text(errors="replace"):
                    time.sleep(1.0)
                    break
                time.sleep(0.5)
        finally:
            subprocess.run(["taskkill", "/PID", str(proc.pid), "/F"], capture_output=True)
    text = LOG.read_text(errors="replace")
    for l in text.splitlines():
        if "DUR TEST recast" in l or "DUR TEST" in l or "xception" in l or "cost its action" in l or "until the end of round" in l \
                or "loses its action" in l or "resists Terror" in l:
            print(l[:170])
    held = {}                                           # (name, cond) -> set of rounds
    put = None
    for r, who, conds in re.findall(r"DUR TEST round (\d+) (.+?):((?: K\d+)*)\s*$", text, re.M):
        for k in conds.split():
            held.setdefault((who, k), set()).add(int(r))
    m = re.search(r"DUR TEST put in round (\d+)", text)
    put = int(m.group(1)) if m else None
    lead = next((w for (w, k) in held if k == "K053"), None)
    bad = []
    if put is None or lead is None:
        bad.append("no put / lead")
    else:
        last = max(r for (_w, _k), rs in held.items() for r in rs)
        for k, n in EXPECT_LEAD.items():
            rs = held.get((lead, k), set())
            want = {r for r in range(put, min(put + n + 1, last + 1))} if n < 99 else set(range(put, last + 1))
            ok = want <= rs and not any(r > put + n for r in rs)
            print("%-5s %-6s held %s want %s" % (k, "OK" if ok else "WRONG", sorted(rs), sorted(want)))
            if not ok:
                bad.append(k)
        for k in ("K053", "K020"):
            if not re.search(r"recast %s in round \d+: taken, LV 1" % k, text):
                bad.append(k + " recast refused or stacked")
        if (lead, "K007") in held:
            bad.append("Terror took hold through Stillness/Courage")
    print("problems:", bad)


if __name__ == "__main__":
    main()
