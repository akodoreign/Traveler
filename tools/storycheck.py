"""Story reachability (user, 2026-11-10: "simulate each path ... see if its even possible for a player to do").
Reads the built game data (map.json) and plays every path symbolically from New Game: maps are reached through
portals, map moves and the road-map travel table; an event can run when its map is reached and its conditions can be
true; running it sets what its commands set (every choice, both sides of every if, battles won and lost). Each
variable keeps the SET of values it can have, so the answer is "possible / impossible", not one playthrough.
python -E tools/storycheck.py [--path N]   N = the prologue choice (0 Crab ... 7 Ronin); default: every path at once.
Reports: maps never reached, portals never open, event pages whose conditions can never hold (with the variable
that blocks them), and the chapter-complete flags each path reaches."""
import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project")
PATHS = ["Crab", "Crane", "Lion", "Phoenix", "Dragon", "Scorpion", "Unicorn", "Ronin"]
CAP = 40                                         # counters stop growing here (enough for every check in the game)


def load():
    mp = json.load(open(os.path.join(PROJ, "data", "map.json"), encoding="utf-8"))
    plug = ""
    for f in os.listdir(os.path.join(PROJ, "plugin", "rokugan")):
        if f.endswith(".sk"):
            plug += open(os.path.join(PROJ, "plugin", "rokugan", f), encoding="utf-8", errors="replace").read()
    return mp, plug


class Sim:
    def __init__(self, mp, plug, path=None):
        self.mp, self.path = mp, path
        self.vals = defaultdict(lambda: {False})          # every variable starts false / 0 ...
        gv = json.load(open(os.path.join(PROJ, "data", "gvar.json"), encoding="utf-8"))
        for k, v in gv.items():                            # ... unless the variable table gives it a start value
            if isinstance(v, dict) and v.get("defval") not in (None, False, 0):
                self.vals[k] = {v["defval"]}
        self.free = set(re.findall(r'rpgvar\[\s*"(G\d+)"\s*\]\s*=', plug))   # the plugin sets these at runtime
        self.maps = set()
        self.ran = set()
        self.changed = True

    # ---------------------------------------------------------------- values
    def get(self, v):
        if not isinstance(v, str) or not re.match(r"^G\d+$", v) or v in self.free:
            return None                                    # anything (items, money, script temporaries, plugin vars)
        return self.vals[v]

    def add(self, var, vs):
        if not isinstance(var, str) or not re.match(r"^G\d+$", var):
            return
        cur = self.vals[var]
        new = {min(v, CAP) if isinstance(v, (int, float)) and not isinstance(v, bool) else v for v in vs} - cur
        if new:
            cur |= new
            self.changed = True

    @staticmethod
    def test(a, op, b):
        try:
            if op == "==":
                return a == b or (a is False and b == 0) or (a == 0 and b is False)
            if op == "!=":
                return not Sim.test(a, "==", b)
            a, b = (0 if x is False else 1 if x is True else x for x in (a, b))
            return {">=": a >= b, "<=": a <= b, ">": a > b, "<": a < b}[op]
        except (TypeError, KeyError):
            return True

    def can(self, req, want=True):
        vs = self.get(req.get("lvar"))
        if vs is None:
            return True
        rv = req.get("rvar")
        r2 = self.get(rv) if isinstance(rv, str) and re.match(r"^G\d+$", str(rv)) else None
        rvs = r2 if r2 is not None else ([rv] if not (isinstance(rv, str) and re.match(r"^G\d+$", rv)) else [True, False, 0, 1])
        return any(self.test(a, req.get("op", "=="), b) == want for a in vs for b in rvs)

    def sat(self, reqs):
        return all(self.can(r) for r in (reqs or []))

    def unsat_var(self, reqs):
        for r in reqs or []:
            if not self.can(r):
                return "%s %s %s (can be %s)" % (r.get("lvar"), r.get("op"), r.get("rvar"),
                                                 sorted(map(str, self.vals[r.get("lvar")]))[:6])
        return None

    # ---------------------------------------------------------------- commands
    def run(self, cmds, here):
        for c in cmds or []:
            if not isinstance(c, dict):
                continue
            k = c.get("cmd")
            if k == "cmd_compute":
                var, op, rv = c.get("lvar"), c.get("op", "="), c.get("rvar")
                rvs = self.get(rv) if isinstance(rv, str) and re.match(r"^G\d+$", rv) else {rv}
                if rvs is None:
                    rvs = {True, False, 0, 1, 2, 3}
                if op == "=":
                    self.add(var, rvs)
                else:
                    cur = self.vals[var] if isinstance(var, str) else {0}
                    out = set()
                    for a in cur:
                        for b in rvs:
                            a1 = 0 if a is False else 1 if a is True else a
                            b1 = 0 if b is False else 1 if b is True else b
                            try:
                                out.add({"+=": a1 + b1, "-=": a1 - b1, "*=": a1 * b1}.get(op, a1))
                            except TypeError:
                                pass
                    self.add(var, out)
            elif k == "cmd_if":
                blocks = c.get("cmdblocks") or []
                reqs = c.get("reqs") or []
                if self.sat(reqs) and blocks:
                    self.run(blocks[0], here)
                if len(blocks) > 1 and (not reqs or any(self.can(r, False) for r in reqs)):
                    self.run(blocks[1], here)
            elif k == "cmd_choices":
                for b in c.get("cmdblocks") or []:
                    self.run(b, here)
            elif k == "cmd_mapmove":
                self.reach((c.get("dest") or {}).get("mapid"))
            elif k == "cmd_script":
                s = c.get("code") or ""
                for g in re.findall(r'rpgvar\[\s*"(G\d+)"\s*\]\s*=', s):
                    self.add(g, {True, False, 0, 1, 2, 3})
                if "::Rokugan.travel" in s:
                    for fl, mid, af, am in re.findall(
                            r'flag="(G\d+)", mapid="(M\d+)"[^}]*?(?:altflag="(G\d+)", altmap="(M\d+)")?[^}]*}', s):
                        if self.vals[fl] & {True}:
                            self.reach(mid)
                            if am and self.vals[af] & {True}:
                                self.reach(am)
            elif k == "cmd_loop":
                self.run(c.get("cmdblock") or c.get("cmdblocks"), here)
            for key in ("cmdblock",):
                if key in c and k not in ("cmd_if", "cmd_choices", "cmd_loop"):
                    self.run(c[key], here)

    def reach(self, mid):
        if mid and mid in self.mp and mid not in self.maps:
            self.maps.add(mid)
            self.changed = True

    # ---------------------------------------------------------------- fixed point
    def step(self):
        for mid in list(self.maps):
            for key, e in (self.mp[mid].get("event") or {}).items():
                if not self.sat(e.get("reqs0")):
                    continue
                if e.get("role") == "portal" or e.get("dest"):
                    self.reach((e.get("dest") or {}).get("mapid"))
                for n, pg in enumerate(e.get("page") or []):
                    if pg.get("trigger") == 0 or not self.sat(pg.get("reqs")):
                        continue
                    self.ran.add((mid, key, n))
                    self.run(pg.get("cmdblock"), mid)

    def solve(self, start="M099"):
        self.reach(start)
        if self.path is not None:                                 # force the prologue choice
            self.force = self.path
        n = 0
        while self.changed and n < 60:
            self.changed = False
            self.step()
            n += 1
        return n


def prologue_choice_patch(mp, path):
    """Keep only branch `path` of the prologue's 'Whose journey begins?' choice."""
    def walk(x):
        if isinstance(x, list):
            for c in x:
                walk(c)
        elif isinstance(x, dict):
            if x.get("cmd") == "cmd_choices" and "Hiruma Natsuko (Crab)" in json.dumps({k: v for k, v in x.items()
                                                                                         if k.startswith("text")}):
                x["cmdblocks"] = [b if i == path else [] for i, b in enumerate(x["cmdblocks"])]
            for v in x.values():
                walk(v)
    walk(mp["M099"]["event"])


def main():
    mp, plug = load()
    path = None
    if "--path" in sys.argv:
        path = int(sys.argv[sys.argv.index("--path") + 1])
        prologue_choice_patch(mp, path)
    sim = Sim(mp, plug, path)
    rounds = sim.solve()
    field = [k for k in mp if re.match(r"^M[1-7]\d\d$", k)]
    print("== %s: %d rounds, %d of %d field maps reached" % (PATHS[path] if path is not None else "all paths", rounds,
                                                          len([k for k in field if k in sim.maps]), len(field)))
    print("maps never reached:", " ".join(sorted(k for k in field if k not in sim.maps)))
    dead = defaultdict(list)
    for mid in sorted(sim.maps):
        for key, e in (mp[mid].get("event") or {}).items():
            why = sim.unsat_var(e.get("reqs0"))
            if why:
                dead[mid].append("%s %s (%s) never appears: %s" % (key, e.get("role"), e.get("name", ""), why))
                continue
            for n, pg in enumerate(e.get("page") or []):
                why = sim.unsat_var(pg.get("reqs"))
                if why and pg.get("trigger") != 0:
                    text = re.findall(r'"text": "([^"]{0,60})', json.dumps(pg.get("cmdblock")))
                    dead[mid].append("%s page %d never runs: %s | %s" % (key, n, why, text[:1]))
    nd = sum(len(v) for v in dead.values())
    print("event pages that can never run: %d" % nd)
    for mid, rows in dead.items():
        print(" ", mid, mp[mid].get("name"))
        for r in rows[:12]:
            print("     ", r)
    marks = set()

    def walk(x):
        if isinstance(x, list):
            for c in x:
                walk(c)
        elif isinstance(x, dict):
            t = x.get("text")
            if isinstance(t, str) and t.endswith("- complete."):
                marks.add(t)
            for v in x.values():
                walk(v)
    for mid, key, n in sim.ran:
        walk(mp[mid]["event"][key]["page"][n])
    print("chapter marks reachable (%d):" % len(marks))
    for t in sorted(marks):
        print("   ", t)
    return sim


if __name__ == "__main__":
    main()
