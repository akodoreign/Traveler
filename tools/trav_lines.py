"""Every line of one traveler on a path, with the line before it (for directing moods / emotes / close-ups).
python -E tools/trav_lines.py "Kakita Rensei" M200-M234 M505-M509 [--out FILE]"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import expo_audit as ea, dialog_read as dr
def main():
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]; out = None
    if "--out" in a:
        i = a.index("--out"); out = a[i + 1]; del a[i:i + 2]
    who, rng = a[0], a[1:]
    mp = json.load(open(os.path.join(dr.DATA, "map.json"), encoding="utf-8"))
    ids = []
    for x in rng:
        r = re.match(r"M(\d+)-M(\d+)$", x)
        ids += ["M%03d" % n for n in range(int(r.group(1)), int(r.group(2)) + 1)] if r else [x]
    res = []
    for mid in ids:
        m = mp.get(mid)
        if not isinstance(m, dict): continue
        for eid, e in (m.get("event") or {}).items():
            seq = []
            for pg in (e.get("page") or []) if isinstance(e, dict) else []:
                ea.lines_of(pg.get("cmdblock"), seq, "")
            for i, (k, n, t, _) in enumerate(seq):
                if k == "L" and n.split(" (")[0] == who:
                    p = seq[i - 1] if i else ("", "", "", "")
                    emo = ""
                    res.append("%s%s | %s: %s\n      => %s" % (mid, eid, p[1] or "~", p[2][:90], t))
    txt = "\n".join(res)
    if out: open(out, "w", encoding="utf-8").write(txt); print(out, len(res))
    else: print(txt)
main()
