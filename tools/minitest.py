"""Engine test of the Winter Court mini-games (plugin RokuganMini.sk), unattended through playbot.

python -E tools/minitest.py yumi|race|both [--plan lose,win] [--vars G210,...]
- yumi: Kyuden Hida 1F (M142), talk to Yasuki Kurako, "Shoot to win." -> the archery mini-game.
- race: the same floor, Kitsu Takeo's side story, "Ride with him." -> the horse race (then the Matsu battle).
--plan: one self-play mode per round (-rtmini): "lose" idles, "win" plays; "Try again?" -> Yes while entries remain.
Screenshots: _art/preview/bot/mini_<game>/ (intro, play/run, won/lost panels). Kills rpgcobo.exe first (playbot)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import playbot  # noqa: E402

SPOTS = {"yumi": (30, 10, ["G1231", "G219", "G205", "G1232"]),
         "race": (21, 9, ["G1231", "G1233", "G233", "G232"]),
         "memory": (12, 9, ["G1231", "G235", "G232"], "M144")}   # Ide Fujio, 3F (Faces of the Court)


def run(game, plan, vars_):
    x, z, show = SPOTS[game][:3]
    mp = SPOTS[game][3] if len(SPOTS[game]) > 3 else "M142"
    bx, bz = playbot.block(mp, x, z)
    sx, sz = playbot.block(mp, x - 2, z)
    name = "mini_" + game
    lines = ["answer 0", "talkto %.1f %.1f" % (bx, bz), "wait 1500", "until G1231 240000", "wait 3000",
             "vars " + " ".join(show), "shot after"]
    kept, timed_out = playbot.launch(name, mp, sx, sz, lines, vars_=vars_, lv="22", secs=400.0, quiet=True,
                                     extra=["mini " + plan, "minishot " + name])
    for ln in kept:
        if any(k in ln for k in ("mini", "yumi", "race", "BOT var", "CHOICE", "rror", "xception", "BOT flag")):
            print(ln)
    print("--", game, "TIMED OUT" if timed_out else "finished", "->", os.path.normpath(
        os.path.join(HERE, "..", "_art", "preview", "bot", name)))


def main():
    a = sys.argv[1:]
    plan, vars_ = "lose,win", "G000"
    if "--plan" in a:
        i = a.index("--plan"); plan = a[i + 1]; a = a[:i] + a[i + 2:]
    if "--vars" in a:
        i = a.index("--vars"); vars_ = a[i + 1]; a = a[:i] + a[i + 2:]
    for g in (["yumi", "race"] if a[0] == "both" else [a[0]]):
        run(g, plan, vars_)


if __name__ == "__main__":
    main()
