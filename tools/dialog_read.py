"""Reading copy of the game's conversations, every branch shown (user 2026-11-22: "you are responsible now for
conversational exposition"; "conversations often have a long backwards and forwards ... multiple ways something
unfolds").

Walks map.json event -> page -> cmdblock like the engine does and prints each line with its direction:
    <mood>        the bust expression (emo field; travelers only have all 8 - others show neutral whatever is set)
    {emote}       the 3D emote the speaker plays (act field, RokuganCloseup.sk)
    ^zoom         the camera closes on the speaker for that line (zoom field)
Branches: IF / ELSE / CHOICE "option" are indented; flags set are shown as `G123 = 1`.

  python -E tools/dialog_read.py M100 M101 ...           those maps
  python -E tools/dialog_read.py M100-M110               a range
  python -E tools/dialog_read.py --grep "Seppun Satomi"  maps where that text or speaker appears
  python -E tools/dialog_read.py ... --story          story scenes only (no odd jobs, hirelings, shrines, signs)
  python -E tools/dialog_read.py ... --out FILE          write to FILE (utf-8) instead of stdout
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "data"))
TRIGGER = {0: "touch", 1: "talk", 2: "talk", 3: "touch", 6: "autorun", 7: "parallel"}


def req_str(reqs):
    if not reqs:
        return ""
    out = []
    for r in reqs:
        if isinstance(r, dict):
            out.append("%s %s %s" % (r.get("lvar"), r.get("op"), r.get("rvar")))
    return " and ".join(out)


def line_of(c):
    n = c.get("name") or ""
    tag = ""
    if c.get("emo"):
        tag += " <%s>" % c["emo"]
    if c.get("act"):
        tag += " {%s}" % c["act"]
    if c.get("zoom"):
        tag += " ^zoom"
    return ("%s%s: %s" % (n, tag, c.get("text", ""))) if n else ("~ %s%s" % (c.get("text", ""), tag))


def walk(block, ind, out):
    for c in block or []:
        if not isinstance(c, dict):
            continue
        k = c.get("cmd")
        p = "  " * ind
        if k == "cmd_showmsg" and c.get("key") == "message_talk":
            out.append(p + line_of(c))
        elif k == "cmd_showmsg":
            out.append(p + "[%s] %s" % (c.get("key"), c.get("text", "")))
        elif k == "cmd_if":
            bl = c.get("cmdblocks") or []
            out.append(p + "IF %s" % req_str(c.get("reqs")))
            walk(bl[0] if bl else [], ind + 1, out)
            if len(bl) > 1 and bl[1]:
                out.append(p + "ELSE")
                walk(bl[1], ind + 1, out)
            out.append(p + "END")
        elif k == "cmd_choices":
            bl = c.get("cmdblocks") or []
            i = 0
            while "text%d" % i in c:
                out.append(p + 'CHOICE "%s"' % c["text%d" % i])
                walk(bl[i] if i < len(bl) else [], ind + 1, out)
                i += 1
        elif k == "cmd_compute" and str(c.get("lvar", "")).startswith("G"):
            out.append(p + "`%s %s %s`" % (c.get("lvar"), c.get("op"), c.get("rvar")))
        elif k == "cmd_battle1":
            out.append(p + "[BATTLE group %s]" % c.get("gid"))
        elif k == "cmd_mapmove":
            out.append(p + "[-> %s]" % ((c.get("dest") or {}).get("mapid")))
        elif k == "cmd_anime":
            out.append(p + "{%s %s}" % ("player" if c.get("who") == 1 else "this", (c.get("ani") or {}).get("id")))
        elif k == "cmd_script" and "closeup" in str(c.get("code", "")):
            out.append(p + "{%s}" % c["code"])
        elif k == "cmd_loop":
            walk(c.get("cmdblock") or (c.get("cmdblocks") or [[]])[0], ind, out)


NOISE = ("Odd job", "Busy, busy", "Hire (", "Sumai match to recruit", "Rest and save", "Stairs up", "Stairs down",
         "A road map, painted", "Thanks again, traveler", "Word on the road", "Exit to the")
STORY = False                                   # --story: drop odd jobs, hirelings, shrines, signs, one-liners


def dump_map(mid, m, out):
    out.append("=" * 100)
    out.append("%s  %s" % (mid, m.get("name", "")))
    for eid, e in (m.get("event") or {}).items():
        if not isinstance(e, dict):
            continue
        pages = e.get("page") or []
        if not any(json.dumps(pg, ensure_ascii=False).find('"message_talk"') >= 0 for pg in pages):
            continue
        if STORY:
            js = json.dumps(pages, ensure_ascii=False)
            scene = any(pg.get("trigger") in (5, 6) for pg in pages) and js.count('"message_talk"') >= 4
            if not scene and (any(k in js for k in NOISE) or js.count('"message_talk"') < 4):
                continue
        out.append("-" * 60)
        out.append("EVENT %s %s %s  appears if: %s" % (eid, e.get("name", ""), e.get("mdlid", ""), req_str(e.get("reqs0")) or "always"))
        for i, pg in enumerate(pages):
            out.append(" PAGE %d (%s) if: %s" % (i, TRIGGER.get(pg.get("trigger"), pg.get("trigger")), req_str(pg.get("reqs")) or "always"))
            walk(pg.get("cmdblock"), 2, out)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    global STORY
    outfile = None
    if "--story" in args:
        STORY = True
        args.remove("--story")
    if "--out" in args:
        i = args.index("--out")
        outfile = args[i + 1]
        del args[i:i + 2]
    mp = json.load(open(os.path.join(DATA, "map.json"), encoding="utf-8"))
    ids = []
    if args and args[0] == "--grep":
        pat = args[1]
        ids = [k for k, v in mp.items() if isinstance(v, dict) and pat in json.dumps(v, ensure_ascii=False)]
    else:
        for a in args:
            r = re.match(r"M(\d+)-M(\d+)$", a)
            if r:
                ids += ["M%03d" % n for n in range(int(r.group(1)), int(r.group(2)) + 1)]
            else:
                ids.append(a)
    out = []
    for mid in ids:
        if isinstance(mp.get(mid), dict):
            dump_map(mid, mp[mid], out)
    text = "\n".join(out)
    if outfile:
        open(outfile, "w", encoding="utf-8").write(text)
        print("wrote", outfile, len(out), "lines")
    else:
        print(text)


if __name__ == "__main__":
    main()
