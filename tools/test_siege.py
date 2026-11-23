"""Engine test: Crab Ch4's siege night in the roamable Kyuden Hida (gen_maps siege_*, plugin RokuganCastleSiege.sk).
python -E tools/test_siege.py [yard|keep1|keep2|keep3|approach]   -> _art/preview/bot/siege/ (log + shots)"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import playbot  # noqa: E402

import json  # noqa: E402
_GV = json.load(open(os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "data", "gvar.json"), encoding="utf-8"))
CH2 = [g for g in ["G2%02d" % k for k in range(1, 40)] + ["G248", "G255"]       # the Winter Court and Ch3 behind
       if g in _GV and _GV[g].get("type") == 1]                                    # her (the true / false flags)
CASES = {   # map, builder x, z, padded, extra flags
    "yard": ("M500", 48, 8, ["G270", "G271"]),
    "approach": ("M541", 70, 20, ["G270", "G271", "G272", "G273"]),
    "keep1": ("M501", 12, 30, ["G270", "G271", "G272", "G273", "G274", "G275"]),
    "keep2": ("M502", 9, 14, ["G270", "G271", "G272", "G273", "G274", "G275", "G276"]),
    "keep3": ("M503", 9, 14, ["G270", "G271", "G272", "G273", "G274", "G275", "G276", "G277", "G278"]),
}


def main():
    case = next((a for a in sys.argv[1:] if not a.startswith("--")), "yard")
    mp, x, z, flags = CASES[case]
    bx, bz = playbot.block(mp, x, z)
    # (G1644 too: -rtvar is applied inside the launch, after RokuganCastleSiege.sk has worked it out from G271 / G286)
    vars_ = ",".join([v for v in CH2 if v not in ("G209",)] + ["G209"] + flags + ["G1644"])
    lines = ["wait 2500", "shot siege_%s_a" % case, "evalf ../../tools/test_marker_here.sk", "wait 9000",
             "shot siege_%s_b" % case, "vars G1644 G272 G273 G1229"]
    kept, timed = playbot.launch("siege", mp, bx, bz, lines, vars_=vars_, lv="34", secs=90.0, quiet=True)
    for ln in kept:
        if any(k in ln for k in ("MARKER", "siege", "BOT var", "MSG", "rror", "xception")):
            print(ln[:220])
    print("--", "TIMED OUT" if timed else "finished")
    playbot.convert_shots("siege", os.path.join(HERE, "..", "_art", "preview", "bot", "siege"))


if __name__ == "__main__":
    main()
