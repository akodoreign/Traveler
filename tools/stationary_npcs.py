"""Which NPC sheets never move (user 2026-11-15: the head transplant "is good for stationary NPCs").
A sheet is stationary when every map event that wears it stands still (moveaction "stop"), no cutscene walks it
(cmd_move / any command naming its event), and no party member, guest, follower or battle foe uses it.
Writes _art/preview/fixsheet/stationary.txt (one sheet key per line) and prints the counts.
Run: python -E tools/stationary_npcs.py"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project")
OUT = os.path.join(HERE, "..", "_art", "preview", "fixsheet", "stationary.txt")


def walk(o, fn):
    if isinstance(o, dict):
        fn(o)
        for v in o.values():
            walk(v, fn)
    elif isinstance(o, list):
        for v in o:
            walk(v, fn)


def main():
    pics = json.load(open(os.path.join(PROJ, "resource", "enemy_pic.json"), encoding="utf-8"))
    sheet = {k: os.path.basename(v["pic3d"])[:-4] for k, v in pics.items()
             if isinstance(v, dict) and v.get("pic3d", "").split("/")[-1].startswith(("side_", "npc_"))}
    maps = json.load(open(os.path.join(PROJ, "data", "map.json"), encoding="utf-8"))
    used, moving = set(), set()
    for mid, m in maps.items():
        evs = m.get("event") or {}
        named = set()                                       # event ids some command acts on (walks, turns, jumps)

        def cmds(d):
            if str(d.get("cmd", "")).startswith("cmd_") and "who" in d:
                named.add(str(d["who"]))
        walk(evs, cmds)
        for evid, ev in evs.items():
            if not isinstance(ev, dict):
                continue
            mdls, acts = set(), set()

            def grab(d):
                if isinstance(d.get("mdlid"), str):
                    mdls.add(d["mdlid"])
                if "moveaction" in d:
                    acts.add(d["moveaction"])
            walk(ev, grab)
            ids = {evid, evid.strip("#")}
            for mdl in mdls & set(sheet):
                used.add(mdl)
                if acts - {"stop"} or ids & named:
                    moving.add(mdl)
    # party members, guests and battle foes walk / fight in the sheet's other frames
    for f in ("player.json", "enemy.json"):
        s = open(os.path.join(PROJ, "data", f), encoding="utf-8").read()
        moving |= set(re.findall(r"EP\d+", s)) & set(sheet)
    for f in os.listdir(os.path.join(PROJ, "plugin", "rokugan")):
        if f.endswith(".sk"):
            for ln in open(os.path.join(PROJ, "plugin", "rokugan", f), encoding="utf-8", errors="ignore"):
                if "sumaiFoe" in ln:                        # the every-cast-member lookup for foe twins: not a walker
                    continue
                moving |= set(re.findall(r"EP\d+", ln)) & set(sheet)
    still_keys = {sheet[e] for e in used - moving}
    moving_keys = {sheet[e] for e in moving}
    keys = sorted(still_keys - moving_keys)                 # a sheet shared by a walker is not stationary
    open(OUT, "w").write("\n".join(keys))
    print("sheets", len(set(sheet.values())), "on maps", len({sheet[e] for e in used}), "moving", len(moving_keys),
          "stationary", len(keys))


if __name__ == "__main__":
    main()
