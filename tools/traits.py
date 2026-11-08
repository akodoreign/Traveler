"""Per-traveler growth from docs/rules/stats.md: Lv 1 traits + trait schedules -> traits / rings at any level ->
engine level curves. The template curve (data_orig P000) stays the "average traveler" (enemy stats are fitted to
it, gen_data.foe_stats); each traveler is the template scaled by their own trait formula relative to the average.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
STATS_MD = os.path.join(HERE, "..", "docs", "rules", "stats.md")
ORDER = ["Sta", "Wil", "Str", "Per", "Agi", "Int", "Ref", "Awa", "Void"]
KEYS = {"natsuko": "P100", "rensei": "P101", "gendo": "P102", "shizue": "P103", "haruki": "P104", "mitsue": "P105",
        "tamotsu": "P106", "sayo": "P107"}
SHUGENJA = {"P104"}
# Clan roles on top of the traits (user, 2026-10-20): Crab the most HP, Lion next and the hardest hitter; shugenja
# cast, they don't swing. (Mirumoto multi-hit and shugenja Void are battle-plugin rules: RokuganBattle.sk.)
# Crane (Rensei) and Scorpion (Mitsue) are the fastest and vie for who acts first.
ROLE = {"P100": {"MAXHP": 1.12}, "P103": {"MAXHP": 1.18, "PATK": 1.12}, "P104": {"PATK": 0.8},
        "P101": {"AGI": 1.16}, "P105": {"AGI": 1.17}}


def parse():
    txt = open(STATS_MD, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r"^\| \*\*(\w+)\*\*[^|]*\| ([0-9 ·]+?) →[^|]*\| ([^|]+)\|", txt, re.M):
        name, base, sched = m.group(1).lower(), m.group(2), m.group(3)
        if name not in KEYS:
            continue
        vals = [int(v) for v in re.findall(r"\d", base)]
        traits = dict(zip(ORDER, vals))
        steps = [(int(lv), t) for lv, t in re.findall(r"(\d+) (Sta|Wil|Str|Per|Agi|Int|Ref|Awa|Void)\b", sched)]
        out[KEYS[name]] = (traits, steps)
    return out


def traits_at(base, steps, lv):
    t = dict(base)
    for slv, tr in steps:
        if slv <= lv:
            t[tr] += 1
    return t


def rings(t):
    return {"Air": min(t["Ref"], t["Awa"]), "Earth": min(t["Sta"], t["Wil"]), "Fire": min(t["Agi"], t["Int"]),
            "Water": min(t["Str"], t["Per"]), "Void": t["Void"]}


def rank(lv):
    return 1 + (lv >= 21) + (lv >= 41) + (lv >= 51) + (lv >= 61)


def raw(t, lv, shug=False):
    r = rings(t)
    return {"MAXHP": 60 + 30 * t["Sta"] + 20 * r["Earth"],
            "MAXMP": (20 + 12 * t["Void"] + 6 * t["Wil"]) * (1.4 if shug else 1.0),
            "PATK": 10 + 9 * t["Str"], "PDEF": 8 + 8 * t["Sta"], "MATK": 10 + 9 * t["Int"],
            "MDEF": 8 + 8 * t["Wil"], "AGI": 20 + 12 * t["Ref"] + 3 * rank(lv)}


def curves(template):
    """template: the engine lvcurve dict (lists by level index). Returns {pid: lvcurve}."""
    data = parse()
    n = len(template["MAXHP"])
    per = {pid: [raw(traits_at(b, s, lv), lv, pid in SHUGENJA) for lv in range(n)] for pid, (b, s) in data.items()}
    out = {}
    for pid in data:
        lc = {k: list(v) for k, v in template.items()}
        for lv in range(n):
            mine = per[pid][lv]
            mean = {k: sum(per[q][lv][k] for q in per) / len(per) for k in mine}
            shug_int = per["P104"][lv]["MATK"]
            for k in ("MAXHP", "MAXMP", "PATK", "PDEF", "MDEF", "AGI"):
                lc[k][lv] = max(1, int(round(template[k][lv] * mine[k] / mean[k] * ROLE.get(pid, {}).get(k, 1.0))))
            # magic: the shugenja reference is the template's bushi attack curve (ATK); others train it far less
            lc["MATK"][lv] = max(1, int(round(template["ATK"][lv] * mine["MATK"] / shug_int *
                                              (1.0 if pid in SHUGENJA else 0.55))))
        out[pid] = lc
    return out


if __name__ == "__main__":
    import json
    tpl = json.load(open(os.path.join(HERE, "..", "_tools", "data_orig", "player.json"), encoding="utf-8"))["P000"]
    c = curves(tpl["lvcurve"])
    for pid, lc in c.items():
        print(pid, " | ".join("L%d HP%d SP%d PA%d PD%d MA%d MD%d AG%d" % (
            lv, lc["MAXHP"][lv], lc["MAXMP"][lv], lc["PATK"][lv], lc["PDEF"][lv], lc["MATK"][lv], lc["MDEF"][lv],
            lc["AGI"][lv]) for lv in (1, 20, 40)))
