"""Engine test of the Game of Masks (plugin RokuganSadane.sk) through playbot.
python -E tools/test_sadane.py rival N [--plan win|lose] [--map M581]
python -E tools/test_sadane.py stranger K [--plan win|lose] [--map M581]
Shosuro Mitsue leads; tools/test_sadane_setup.sk opens the game with a test sleeve (Half-Mask 10, Fire-Lacquer 12,
Rain 12, Clay 11) and sets the trigger: a rival "sees" her (G1653) or a stranger steps out (G1652). The duel plays
itself (-rtmini win / lose). Shots: _art/preview/bot/sadane_<kind>/ (open, turn, won / lost). Kills rpgcobo.exe first."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import playbot  # noqa: E402


def main():
    a = sys.argv[1:]
    plan, mp, lv = "win", None, ""
    if "--lv" in a:
        i = a.index("--lv"); lv = ":" + a[i + 1]; a = a[:i] + a[i + 2:]
    if "--plan" in a:
        i = a.index("--plan"); plan = a[i + 1]; a = a[:i] + a[i + 2:]
    if "--map" in a:
        i = a.index("--map"); mp = a[i + 1]; a = a[:i] + a[i + 2:]
    kind, n = a[0], int(a[1])
    if not mp:
        import json
        d = json.load(open(os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "resource", "sadane",
                                        "sadane.json"), encoding="utf-8"))
        mp = d["rivals"][n]["map"] if kind == "rival" else "M581"
    bx, bz = playbot.block(mp, 48, 34)
    if kind == "rival":                     # start beside the rival: events only spawn near the player
        import json
        m = json.load(open(os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "data", "map.json"),
                           encoding="utf-8"))
        e = next(e for e in m[mp]["event"].values() if e.get("sadane") == n)
        bx, bz = e["pos"][0] + 4, e["pos"][2] + 4
    name = "sadane_" + kind
    lines = ["wait 3500", "evalf ../../tools/test_sadane_setup.sk", "until G1231 240000", "wait 2500",
             "vars G1231 G1651 G1652 G1653 G060 MONEY", "shot after"]
    kept, timed_out = playbot.launch(name, mp, bx, bz, lines, vars_="G861", lv="20", secs=320.0, quiet=True,
                                     lead="P105", extra=["mini " + plan, "minishot " + name,
                                                         "sadane %s:%d%s" % (kind, n, lv)])
    for ln in kept:
        if any(k in ln for k in ("sadane", "SADANE", "BOT var", "rror", "xception", "mini")):
            print(ln)
    print("--", kind, n, "TIMED OUT" if timed_out else "finished", "->",
          os.path.normpath(os.path.join(HERE, "..", "_art", "preview", "bot", name)))


if __name__ == "__main__":
    main()
