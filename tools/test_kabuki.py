"""Engine test: the kabuki rehearsal (Crane Ch4 S03 on Kyuden Doji's north-garden stage; plugin RokuganKabuki.sk).
python -E tools/test_kabuki.py [win|ok|lose] [--hard]   -> _art/preview/bot/kabuki/ (log + shots)"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import playbot  # noqa: E402

MAP = "M555"


def main():
    plan = next((a for a in sys.argv[1:] if not a.startswith("--")), "win")
    flags = ["G403", "G417", "G418", "G419", "G420", "G425"]
    sx, sz = playbot.block(MAP, 48, 42)
    bx, bz = playbot.block(MAP, 48, 47)
    lines = ["wait 2000", "shot kabuki_stage", "talkto %.1f %.1f" % (bx, bz), "wait 330000", "wait 5000",
             "shot kabuki_after", "vars G1231 G1645 G438 G427 G426"]
    kept, timed = playbot.launch("kabuki", MAP, sx, sz, lines, vars_=",".join(flags), lv="44", secs=480.0,
                                 quiet=True, lead="P101", choice="0,0," + ("1" if "--hard" in sys.argv else "0"),
                                 extra=["mini " + plan, "minishot kabuki"])
    for ln in kept:
        if any(k in ln for k in ("kabuki", "mini", "BOT var", "CHOICE", "rror", "xception", "MSG")):
            print(ln[:200])
    print("--", "TIMED OUT" if timed else "finished")
    playbot.convert_shots("kabuki", os.path.join(HERE, "..", "_art", "preview", "bot", "kabuki"))


if __name__ == "__main__":
    main()
