"""Exposition audit (user 2026-11-22: "you are responsible now for conversational exposition"; "theres 7 more paths,
and none of them were good past crab"). Walks every story scene of a path's maps in play order and flags:
  INTRO   a speaker's first line on the path with no narration naming them in the 4 lines before, and no
          self-introduction in their first two lines (the player meets a stranger with no who / why)
  BOSS    a battle preceded by fewer than 2 lines from anyone but the traveler (no threat, no monologue)
  OPEN    each chapter's first 6 lines (CHAPTER n cards), to check who / where / why / stakes
Generic speakers (guards, villagers, "Sailor", hirelings) are skipped.
  python -E tools/expo_audit.py M200-M234 M505-M509 [--trav "Kakita Rensei"]"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dialog_read as dr  # noqa: E402

GENERIC = re.compile(r"(guard|villager|sentry|sailor|servant|clerk|youth|runner|merchant|priest|soldier|bushi|"
                     r"fishwife|farmer|monk|child|maid|messenger|innkeeper|smith|veteran|engineer|sapper|archer|"
                     r"scout|ship's master|general|headman|attendant|boy|girl|woman|man|elder|bandit|pirate|"
                     r"courtier|student|sensei|crowd|voice|hireling|ronin|nezumi|goblin|oni|ghost|spirit|wife|"
                     r"captain|kitchen|stable|groom|porter|ferryman|fisher|cook|drunk|net-mender|lookout|"
                     r"togashi yosai|^\?|teacher|pilgrim|healer|official|magistrate's|samurai|warrior|shaman)", re.I)
TRAV = {"Hiruma Natsuko", "Kakita Rensei", "Kitsuki Gendo", "Akodo Shizue", "Isawa Haruki", "Shosuro Mitsue",
        "Ide Tamotsu", "Sayo"}


def lines_of(block, out, ctx):
    for c in block or []:
        if not isinstance(c, dict):
            continue
        k = c.get("cmd")
        if k == "cmd_showmsg" and c.get("key") == "message_talk":
            out.append(("L", c.get("name") or "", c.get("text") or "", ctx))
        elif k == "cmd_if":
            for b in c.get("cmdblocks") or []:
                lines_of(b, out, ctx)
        elif k == "cmd_choices":
            for b in c.get("cmdblocks") or []:
                lines_of(b, out, ctx)
        elif k == "cmd_battle1":
            out.append(("B", "", "group %s" % c.get("gid"), ctx))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    trav = None
    if "--trav" in args:
        i = args.index("--trav")
        trav = args[i + 1]
        del args[i:i + 2]
    mp = json.load(open(os.path.join(dr.DATA, "map.json"), encoding="utf-8"))
    ids = []
    for a in args:
        r = re.match(r"M(\d+)-M(\d+)$", a)
        ids += ["M%03d" % n for n in range(int(r.group(1)), int(r.group(2)) + 1)] if r else [a]
    seq = []
    for mid in ids:
        m = mp.get(mid)
        if not isinstance(m, dict):
            continue
        for eid, e in (m.get("event") or {}).items():
            if not isinstance(e, dict):
                continue
            for pg in e.get("page") or []:
                if pg.get("trigger") in (5, 6) or "CHAPTER" in json.dumps(pg, ensure_ascii=False):
                    lines_of(pg.get("cmdblock"), seq, "%s %s" % (mid, eid))
    seen = set()
    for i, (kind, name, text, ctx) in enumerate(seq):
        if kind == "L" and text.startswith("CHAPTER "):
            print("\nOPEN  %s  %s" % (ctx, text))
            for k2, n2, t2, _ in seq[i + 1:i + 7]:
                print("        %s: %s" % (n2 or "~", t2[:150]))
        if kind == "B":
            before = [x for x in seq[max(0, i - 6):i] if x[0] == "L" and x[1] and x[1] not in TRAV]
            if len(before) < 2:
                print("BOSS? %s  %s  (lines before: %s)" % (ctx, text, "; ".join("%s: %s" % (x[1], x[2][:50])
                                                                                    for x in seq[max(0, i - 3):i])))
        if kind == "L" and name and name not in TRAV and name not in seen and not GENERIC.search(name):
            seen.add(name)
            given = name.split(" ")[-1]
            near = " ".join(x[2] for x in seq[max(0, i - 4):i] if x[0] == "L" and not x[1])
            own = " ".join(x[2] for x in seq[i:i + 6] if x[1] == name)[:400]
            if name not in near and given not in near and not re.search(r"\b(I'm|I am|my name|call me)\b", own) \
                    and given not in own:
                print("INTRO %s  %s: %s" % (ctx, name, text[:110]))


if __name__ == "__main__":
    main()
