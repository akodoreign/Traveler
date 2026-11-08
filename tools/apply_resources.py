"""The MP/TP split (user, 2026-11-08). Runs at the end of gen_data and can be run alone; safe to repeat.
MP pays for spells and kiho, TP for school techniques and kata.
MP: shugenja (full) > monks > other > samurai (0).   TP: samurai > other > monks > shugenja (0).
Max Void lives in the plugin (RokuganBattle vpMax): shugenja 6, monk 5, other 3, samurai 2, from each player's rt_class.
python -E tools/apply_resources.py"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "data"))

SHUGENJA = {"P104", "P124", "P135", "P137", "P139"}
MONK = {"P132"}
OTHER = {"P105", "P106", "P107", "P122", "P125", "P136"}     # shinobi, courtiers, ronin healer, nezumi, a heimin wrestler
#                  MP share, TP share of each character's old magic curve
SHARES = {"shugenja": (1.0, 0.0), "monk": (0.8, 0.4), "other": (0.45, 0.75), "samurai": (0.0, 1.0)}

CLAN = {"Hiruma": "crab", "Hida": "crab", "Kaiu": "crab", "Kuni": "crab", "Yasuki": "crab", "Akodo": "lion", "Matsu": "lion", "Ikoma": "lion", "Kitsu": "lion",
        "Kakita": "crane", "Doji": "crane", "Daidoji": "crane", "Asahina": "crane", "Mirumoto": "dragon", "Kitsuki": "dragon", "Togashi": "dragon", "Tamori": "dragon",
        "Agasha": "dragon", "Isawa": "phoenix", "Shiba": "phoenix", "Asako": "phoenix", "Bayushi": "scorpion", "Shosuro": "scorpion", "Soshi": "scorpion", "Yogo": "scorpion",
        "Ide": "unicorn", "Shinjo": "unicorn", "Iuchi": "unicorn", "Moto": "unicorn", "Yoritomo": "mantis", "Moshi": "mantis", "Tsuruchi": "mantis", "Seppun": "imperial",
        "Otomo": "imperial", "Miya": "imperial"}    # anyone else (ronin, Squeak, the Lion rider below) by name or light brown

COIN = ("bandit", "brigand", "ronin", "gaki", "thug", "ruffian", "pirate", "corsair", "wako", "sword-for-hire", "wave-man", "masterless")

RESTORATIVES = [("I445", "Sakaki Incense", 4, 0.25, 6, 50, "Burned before a prayer. Restores some MP."),
                ("I446", "Temple Incense", 4, 0.5, 12, 150, "Blessed at a great shrine. Restores a good deal of MP."),
                ("I447", "Bitter Green Tea", 6, 0.25, 6, 40, "Strong enough to stand a spoon in. Restores some TP."),
                ("I448", "Warrior's Sake", 6, 0.5, 12, 130, "One cup before the charge. Restores a good deal of TP.")]

MP_SKILLS = {"S111", "S131", "S138", "S154", "S155", "S156", "S157", "S158", "S159", "S460", "S461", "S499", "S537", "S538"}
TP_SKILLS = {"S132", "S139", "S140", "S141", "S142", "S169", "S172", "S426", "S476", "S481", "S482", "S489", "S506", "S507",
             "S526", "S527", "S542", "S543", "S544", "S545", "S546", "S547", "S566", "S580", "S581", "S583", "S584", "S607", "S608"}
FREE_SCHOOL = {"S110", "S147", "S148"}                        # costless techniques still belong on the School command


def is_spell(sid):
    return "S300" <= sid <= "S395" or sid in MP_SKILLS


def load(name):
    return json.load(open(os.path.join(DATA, name + ".json"), encoding="utf-8"))


def save(name, d):
    json.dump(d, open(os.path.join(DATA, name + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent="\t")


def classify(pid):
    return "shugenja" if pid in SHUGENJA else "monk" if pid in MONK else "other" if pid in OTHER else "samurai"


def main():
    sk = load("skill")
    unsorted_ = []
    for sid, v in sk.items():
        if not (isinstance(v, dict) and sid >= "S100"):
            continue
        if sid in TP_SKILLS:
            v["consume"] = [1, v["consume"][1]]
            v["rt_school"] = True
        elif sid in FREE_SCHOOL:
            v["rt_school"] = True
        elif v.get("consume", [0, 0])[1] > 0 and v.get("addlist") and not is_spell(sid):
            unsorted_.append("%s %s" % (sid, v.get("name")))
    save("skill", sk)
    pl = load("player")
    for pid, x in pl.items():
        if not (pid >= "P100" and isinstance(x, dict) and x.get("lvcurve")):
            continue
        cls = classify(pid)
        x["rt_class"] = cls
        x["rt_clan"] = "lion" if x["name"] == "Lion rider" else CLAN.get(x["name"].split()[0], "ronin")
        ref = x.setdefault("rt_mpref", x["lvcurve"]["MAXMP"])
        mp, tp = SHARES[cls]
        x["lvcurve"]["MAXMP"] = [int(round(v * mp)) for v in ref]
        x["lvcurve"]["MAXTP"] = [int(round(v * tp)) for v in ref]
        text = json.dumps({k: x[k] for k in x if k != "lvcurve"})        # (user) everyone can pay for their cheapest technique at least once
        for pool, kind, share in (("MAXMP", 0, mp), ("MAXTP", 1, tp)):
            costs = [v["consume"][1] for sid, v in sk.items() if isinstance(v, dict) and sid >= "S100" and '"%s"' % sid in text
                     and isinstance(v.get("consume"), list) and v["consume"][0] == kind and v["consume"][1] > 0]
            if costs and share > 0:
                x["lvcurve"][pool] = [max(v, min(costs)) for v in x["lvcurve"][pool]]
    save("player", pl)
    en = load("enemy")                                               # (user) those who carry coin pay more; everyone else as before
    for x in en.values():
        if isinstance(x, dict) and any(w in (x.get("name") or "").lower() for w in COIN):
            x["money"] = int(round(x.setdefault("rt_money0", x.get("money") or 0) * 1.5))
    save("enemy", en)
    it = load("item")                                                 # (user) restoratives: dmgtype 4 restores MP, 6 restores TP
    for iid, name, kind, pct, flat, price, desc in RESTORATIVES:
        x = json.loads(json.dumps(it["I001"]))
        pool = "MAXMP" if kind == 4 else "MAXTP"
        x.update({"name": name, "desc": desc, "price": price, "dmgtype": kind, "atkform": "dst.%s*%s+%d" % (pool, pct, flat)})
        it[iid] = x
    save("item", it)
    sto = load("store")
    for sid, v in sto.items():
        if not isinstance(v, dict) or not v.get("items"):
            continue
        have = {i["dataid"] for i in v["items"]}
        if have & {"I100", "I101", "I104", "I125", "I131"}:             # anyone selling food or medicine
            for iid in ("I445", "I447") + (("I446", "I448") if "I101" in have or "I104" in have else ()):
                if iid not in have:
                    v["items"].append({"dataid": iid, "price": None, "reqfail": 0, "reqs": None})
    save("store", sto)
    st = load("setting")
    st["battlecmd2"] = "spell"
    save("setting", st)
    for pid, x in pl.items():
        if pid < "P100" or not isinstance(x, dict) or not x.get("rt_class"):
            continue
        text = json.dumps(x)
        for sid, v in sk.items():
            if isinstance(v, dict) and sid >= "S100" and '"%s"' % sid in text and v.get("consume", [0, 0])[1] > 0:
                if (x["rt_class"] == "samurai" and v["consume"][0] == 0) or (x["rt_class"] == "shugenja" and v["consume"][0] == 1):
                    print("WARNING: %s (%s) owns %s %s, which it cannot pay for" % (x["name"], x["rt_class"], sid, v["name"]))
    if unsorted_:
        print("WARNING: paid skills not sorted into MP or TP:", ", ".join(unsorted_))
    print("resources applied")


if __name__ == "__main__":
    sys.exit(main())
