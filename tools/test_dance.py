"""Engine test: the Winter Court dance contest (plugin RokuganDance.sk, gen_maps hida_hall). Starts on Kyuden Hida's
keep 1F with the four court threads done, walks into the contest (or, with --practice, the night after: the musician by
the stage), picks Easy or Hard, and lets the dance play itself (-rtmini win / ok / lose).
python -E tools/test_dance.py [win|ok|lose] [--hard] [--practice] | --anim   -> _art/preview/bot/dance/ (log + shots)"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import playbot  # noqa: E402

MAP = "M501"
DANCE_SPOT = (48, 21)


def main():
    plan = next((a for a in sys.argv[1:] if not a.startswith("--")), "win")
    pick = "1" if "--hard" in sys.argv else "0"
    hub = ["G202", "G203", "G204", "G205"]
    if "--anim" in sys.argv:                                    # just the clips, one by one (test_dance_anim.sk)
        bx, bz = playbot.block(MAP, *DANCE_SPOT)
        kept, _ = playbot.launch("dance", MAP, bx, bz, ["wait 1500", "evalf ../../tools/test_dance_anim.sk",
                                                           "wait 16000"], vars_=",".join(hub) if "--court" in sys.argv else "G209", lv="22", secs=90.0, quiet=True)
        for ln in kept:
            if "DANCE" in ln or "rror" in ln or "xception" in ln:
                print(ln[:240])
        playbot.convert_shots("dance", os.path.join(HERE, "..", "_art", "preview", "bot", "dance"))
        return
    if "--practice" in sys.argv:
        vars_ = ",".join(hub + ["G209"])
        bx, bz = playbot.block(MAP, 53, 30)
        sx, sz = playbot.block(MAP, 50, 32)
        lines = ["shot hall", "talkto %.1f %.1f" % (bx, bz)]
    else:
        vars_ = ",".join(hub)
        bx, bz = playbot.block(MAP, 48, 9)
        sx, sz = playbot.block(MAP, 48, 12)
        lines = ["shot hall", "talkto %.1f %.1f" % (bx, bz)]
    lines += ["wait 9000", "shot stage", "until G1231 200000", "wait 4000", "shot after",
              "vars G1231 G1643 G1642 G209"]
    kept, timed_out = playbot.launch("dance", MAP, sx, sz, lines, vars_=vars_, lv="22", secs=260.0, quiet=True,
                                     choice=pick,                 # (the first menu: Easy / Hard)
                                     extra=["mini " + plan, "minishot dance"])
    for ln in kept:
        if any(k in ln for k in ("dance", "mini", "MINI", "BOT var", "CHOICE", "rror", "xception", "stall", "BGM")):
            print(ln[:240])
    print("--", "TIMED OUT" if timed_out else "finished")
    playbot.convert_shots("dance", os.path.join(HERE, "..", "_art", "preview", "bot", "dance"))


if __name__ == "__main__":
    main()
