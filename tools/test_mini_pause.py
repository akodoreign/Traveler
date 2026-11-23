"""Engine test: the Esc pause menu while Ide Fujio's memory game is open (user 2026-11-22: quitting the game before
finishing it soft-locked). Talks to Fujio on Kyuden Hida 3F, plays nothing (-rtmini lose), pauses 12 s, unpauses.
python -E tools/test_mini_pause.py [plan] [--quit]   -> _art/preview/bot/mini_pause/"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import playbot  # noqa: E402
import minitest  # noqa: E402


def main():
    plan = next((a for a in sys.argv[1:] if not a.startswith("--")), "lose")
    x, z, show, mp = minitest.SPOTS["memory"]
    bx, bz = playbot.block(mp, x, z)
    sx, sz = playbot.block(mp, x - 2, z)
    if "--quit" in sys.argv:          # the face-up preview, then X mid-game: "Put the cards away?" -> Stop (self-play)
        lines = ["answer 0", "talkto %.1f %.1f" % (bx, bz), "wait 4500", "shot preview", "wait 7000", "shot play",
                 "tap x", "wait 600", "shot quitpanel", "wait 4000", "vars " + " ".join(show), "shot after"]
    else:
        lines = ["answer 0", "talkto %.1f %.1f" % (bx, bz), "wait 800",
                 "evalf ../../tools/test_mini_pause.sk", "wait 60000", "vars " + " ".join(show), "shot after"]
    kept, timed_out = playbot.launch("mini_pause", mp, sx, sz, lines, vars_="G000", lv="22", secs=150.0, quiet=True,
                                     extra=["mini " + plan, "minishot mini_pause"])
    for ln in kept:
        if any(k in ln for k in ("mini", "memory", "MINI", "BOT var", "CHOICE", "rror", "xception", "stall")):
            print(ln[:220])
    print("--", "TIMED OUT" if timed_out else "finished")


if __name__ == "__main__":
    main()
