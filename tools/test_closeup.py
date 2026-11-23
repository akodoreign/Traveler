"""Engine test: conversation emotes + close-ups (RokuganCloseup.sk; act / zoom fields from apply_dialog_fixes "dir").
Plays a directed scene and prints each [RT] CLOSEUP line (found=0 is the player, #n# an event, no = nobody matched).
python -E tools/test_closeup.py [barrel|hearing]   -> _art/preview/bot/closeup/ (log + shots)"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import playbot  # noqa: E402
import test_siege as ts  # noqa: E402

CASES = {   # map, builder x, z, flags on
    # Crab Ch4 S03: the barrel in the cellars (autoruns on G274 and not G275); Sachiko + Goro are along
    "barrel": ("M153", 20, 20, ["G270", "G271", "G272", "G273", "G274", "G1644"]),
    # Crab Ch2 S04: the hearing in the audience hall (autoruns on G210 and not G230)
    "hearing": ("M504", 40, 20, ["G200", "G201", "G202", "G203", "G204", "G205", "G208", "G209", "G210"]),
}


def main():
    case = next((a for a in sys.argv[1:] if not a.startswith("--")), "barrel")
    mp, x, z, flags = CASES[case]
    bx, bz = playbot.block(mp, x, z)
    base = [v for v in ts.CH2 if v not in flags and not v.startswith("G23") and v not in ("G230", "G211")] \
        if case == "barrel" else []
    vars_ = ",".join(base + flags)
    warp = {"barrel": ["warp M153 84 18"]}.get(case, [])            # the barrel is a step-on trigger (event #10)
    lines = ["wait 1500"] + warp + ["wait 1200", "shot closeup_%s_a" % case, "wait 1500", "shot closeup_%s_b" % case, "wait 1500",
             "shot closeup_%s_c" % case, "wait 3000", "vars G275 G230 G211"]
    kept, timed = playbot.launch("closeup", mp, bx, bz, lines, vars_=vars_, lv="34", secs=60.0, quiet=True, extra=["closeshot"])
    for ln in kept:
        if any(k in ln for k in ("CLOSEUP", "BOT var", "rror", "xception", "Closeup")):
            print(ln[:220])
    print("--", "TIMED OUT" if timed else "finished")
    playbot.convert_shots("closeup", os.path.join(HERE, "..", "_art", "preview", "bot", "closeup"))


if __name__ == "__main__":
    main()
