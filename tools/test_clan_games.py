"""Engine test of the castles' clan games (plugin RokuganCastleGames.sk; gen_maps CLAN_GAMES) through playbot.
python -E tools/test_clan_games.py ink|kitsuki|rings|yabusame|go|all [--plan lose,win]
Talks to the game's NPC in its castle district, answers "Play.", lets the game play itself (-rtmini), and prints the
result, the first-win flag and the zeni. Shots: _art/preview/bot/clan_<kind>/. Kills rpgcobo.exe first (playbot)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import playbot  # noqa: E402

GAMES = {"ink": ("M619", "Togashi Kaito", "G1654"), "kitsuki": ("M595", "Kitsuki Ohana", "G1655"),
         "rings": ("M575", "Isawa Tsumari", "G1656"), "yabusame": ("M603", "Iuchi Batu", "G1657"),
         "go": ("M512", "Akodo Nishi", "G1658", 1)}   # (Nishi: the full game is her second choice)


def run(kind, plan):
    mp, who, gflag = GAMES[kind][:3]
    answer = GAMES[kind][3] if len(GAMES[kind]) > 3 else 0
    m = json.load(open(os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "data", "map.json"),
                       encoding="utf-8"))
    e = next(e for e in m[mp]["event"].values() if who in json.dumps(e))
    x, z = e["pos"][0], e["pos"][2]
    name = "clan_" + kind
    lines = ["answer %d" % answer, "talkto %.1f %.1f" % (x, z), "wait 1500", "until G1231 300000", "wait 3000",
             "vars G1231 %s MONEY" % gflag, "shot after"]
    kept, timed_out = playbot.launch(name, mp, x + 3, z + 2, lines, lv="30", secs=420.0, quiet=True,
                                     extra=["mini " + plan, "minishot " + name])
    for ln in kept:
        if any(k in ln for k in (kind + ":", "mini-game", "BOT var", "rror", "xception", "Got ")):
            print(ln[:180])
    print("--", kind, "TIMED OUT" if timed_out else "finished", "->",
          os.path.normpath(os.path.join(HERE, "..", "_art", "preview", "bot", name)))


def main():
    a = sys.argv[1:]
    plan = "lose,win"
    if "--plan" in a:
        i = a.index("--plan"); plan = a[i + 1]; a = a[:i] + a[i + 2:]
    for k in (list(GAMES) if a[0] == "all" else [a[0]]):
        run(k, plan)


if __name__ == "__main__":
    main()
