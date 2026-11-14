"""Turn the RPG-Cobo sample project into the Rokugan Traveler battle test bed (idempotent).

Writes into _tools/rpgcobo-tool/project/data (originals backed up once to _tools/data_orig/):
- type.json   : the 12 attribute bits = 6 weapon types + 6 elements (docs/rules/weapons.md, OCTOPATH-FIT §5)
- cond.json   : K030 "Suki" (uncommandable; removed after 2 turn-ends; cleared at battle end)
- skill.json  : S100-S105 weapon attacks (one bit each), S110 Razor's Edge (taunt-defend), S111 Jade Strike (spell)
- weapon.json : W100-W105 T1 weapons (equipment.md A)
- enemy.json  : E100-E106 Crab Ch1 / Hoshi-no-Ichi foes (bestiary.md A1, B1, B4, C; bosses.md §1)
- player.json : P100-P107 the eight travelers (models CV100-CV107 from gen_travelers.py)
- setting.json: title, start party, "boost" battle command
- plugin.json : enable the "rokugan" plugin
Run: python -E tools/gen_data.py
"""
import copy
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project")
DATA = os.path.join(PROJ, "data")
BACKUP = os.path.join(HERE, "..", "_tools", "data_orig")

ELEMS = ["Katana", "Yari", "Tanto", "Tetsubo", "Yumi", "Bo", "Fire", "Water", "Air", "Earth", "Void", "Jade",
         "Unarmed", "Crystal"]  # Unarmed = Sumai throws / kiho strikes; Crystal: Kansen (EDR has 16 slots)
B = {n: 1 << i for i, n in enumerate(ELEMS)}
import sys  # noqa: E402
sys.path.insert(0, HERE)
import hirelings as _hire  # noqa: E402  the hireables roster (shared with gen_maps / gen_sidecast)
import kata_data as _kata  # noqa: E402  kata / kiho / tattoos learned on level-up (progression-v2.md)
import jobs_data as _jobs  # noqa: E402  jobs and traits (progression-v2.md)


def _sc_epid(key):
    """A side-cast sprite's EP id (gen_sidecast order)."""
    import gen_sidecast as sc
    return sc.epid(next(i for i, c in enumerate(sc.CAST) if c["key"] == key))


def load(name):
    p = os.path.join(DATA, name + ".json")
    os.makedirs(BACKUP, exist_ok=True)
    bp = os.path.join(BACKUP, name + ".json")
    if not os.path.exists(bp):
        shutil.copy(p, bp)
    return json.load(open(bp, encoding="utf-8"))   # always rebuild from the original


def save(name, d):
    json.dump(d, open(os.path.join(DATA, name + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent="\t")


def load_built(name):
    """The table as built so far this run (load() always starts again from the engine's original)."""
    return json.load(open(os.path.join(DATA, name + ".json"), encoding="utf-8"))


TYPED_ATK = (("atk_draw", ("Iaijutsu", "Draw", "Iai")), ("atk_thrust", ("Thrust", "Lunge", "Stab", "Pierce")),
             ("atk_overhead", ("Smash", "Cleave", "Crush", "Hammer", "Overhead", "Quake")),
             ("atk_slash", ("Sweep", "Cut", "Slash", "Strike")))


def party_typed_attacks(players):
    """v4 sprites (gen_sprites2d animap_for): weapon arts the party learns play a typed attack (draw-cut, thrust,
    overhead, slash) by the skill's name instead of the generic slash1/punch1. Only skills learned by party members
    (all picture models; RokuganLook.sk falls back to slash1/punch1 on older sheets)."""
    learned = set()
    for pid, x in players.items():
        if pid.startswith("P1") and isinstance(x, dict):
            for o in x.get("lvoption") or []:
                if o.get("opttype") == "opt_getskill" and o.get("skillid"):
                    learned.add(o["skillid"])
    path = os.path.join(DATA, "skill.json")
    sk = json.load(open(path, encoding="utf-8"))
    n = 0
    for sid in sorted(learned):
        v = sk.get(sid)
        ani = ((v or {}).get("atkact") or {}).get("atkani") or {}
        if ani.get("id") not in ("slash1", "punch1", "stick1"):
            continue
        for aid, words in TYPED_ATK:
            if any(w in v.get("name", "") for w in words):
                ani["id"] = aid
                n += 1
                break
    json.dump(sk, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")
    print("typed attack animations:", n, "party skills")


def weak_opt(*names, rate=-50):
    o = {"opttype": "opt_elemdef"}
    for n in names:
        o["EDR.%d" % ELEMS.index(n)] = rate
    return o


TOWNSFOLK = ["Kiyo", "Gonbei", "Kanbe", "Satomi", "Fishwife", "Wall veteran", "Kite child", "Taneo"]


# English names for template entries the player actually sees (jobs, basic items, status conditions)
LOCAL = {
    "job": {"J000": "Traveler", "J001": "Champion", "J100": "Righteous Heart", "J101": "Iron Will", "J102": "Bushido",
            "J103": "Light Fingers", "J104": "Wind Step", "J105": "Strike First"},
    "item": {"I000": "Pebble", "I001": "Healing Herb", "I004": "Travel Tent", "I010": "Tonic", "I011": "Strong Tonic",
             "I016": "Revival Draught", "I018": "Antidote", "I019": "Panacea", "I020": "Waking Bell"},
    "cond": {"K000": "Down", "K001": "Poison", "K002": "Blind", "K003": "Silence", "K004": "Confuse", "K005": "Sleep",
             "K006": "Paralysis", "K007": "Fear", "K008": "Charm", "K009": "Sealed", "K010": "Curse", "K011": "Stone",
             "K012": "Undead", "K020": "ATK Up", "K021": "ATK Down", "K022": "DEF Up", "K023": "DEF Down",
             "K040": "Regen", "K041": "Berserk", "K042": "Auto-Revive", "K043": "Reflect"},
}


# School ranks R2-R5 (docs/rules/progression-v2.md; user 2026-11-11: "min levels for each rank should be 0, 15, 30, 45,
# 60"). Each traveler's own school (schools.md); the battle effects are in plugin RokuganRanks.sk.
RANK_LEVELS = (15, 30, 45, 60)
RANK_PIDS = {"P100": 700, "P101": 704, "P102": 708, "P103": 712, "P104": 716, "P105": 720, "P106": 724,
             "P107": 728}
_R = [
    # Hiruma Natsuko (Hiruma Scout)
    ("Strike Like the Wind", "+25% damage against a foe that hasn't hit her yet this battle. Every miss against her "
     "makes her harder to hit (up to +25% evasion)."),
    ("Fire and Shadow", "+15% evasion. +25% damage against Shadowlands creatures."),
    ("Harness the Wind", "Her weapon attack strikes twice."),
    ("Veil of Spirits", "15% more critical hits; 30% against Shadowlands creatures."),
    # Kakita Rensei (Kakita Bushi)
    ("The Sudden Strike", "+10% damage for every place he acts ahead of his target (up to +50%)."),
    ("Strike from the Void", "Against a lone foe he starts with +1 VP. A slower foe he has cut has a harder time "
     "hitting him (+20% evasion against it)."),
    ("One Strike, Two Cuts", "Iaijutsu: Strike hits twice."),
    ("Strike with No Thought", "If he acts first, his first blow of the battle is a certain critical."),
    # Kitsuki Gendo (Kitsuki Investigator)
    ("Wisdom the Wind Brings", "Charm, fear and confusion can't take hold of him."),
    ("Finding the Path", "Deduce also shows what the foe will do next."),
    ("Know the Rhythm of the Heart", "+20% damage against a foe whose weakness is known; the party gets +10%."),
    ("Kitsuki's Eyes", "A foe that reaches for charm, fear or confusion gives Gendo 1 VP."),
    # Akodo Shizue (Akodo Bushi)
    ("Strength of Purity", "+4% damage for every point of Honor (up to +40%)."),
    ("Strength of My Ancestors", "Her weapon attack strikes twice."),
    ("Triumph Before Battle", "+10% damage, and her blows strip a foe's DEF Up."),
    ("Akodo's Final Lesson", "Her blows never miss, and hit 25% harder."),
    # Isawa Haruki (Isawa Shugenja) - user 2026-11-12: "shugenja just get more spells at rank until advanced school":
    # each rank brings the next mastery's spells at once (haruki_spells batches them), no other effect
    ("Mastery 2 Spells", "New spells: the second mastery opens to him."),
    ("Mastery 3 Spells", "New spells: the third mastery opens to him."),
    ("Mastery 4 Spells", "New spells: the fourth mastery opens to him."),
    ("Mastery 5 Spells", "New spells: the fifth mastery opens to him."),
    # Shosuro Mitsue (Shosuro Shinobi)
    ("The Shadow Has No Mercy", "+50% damage against a foe that hasn't acted yet, or one left open (Suki)."),
    ("The Shadow Has No Form", "+20% evasion."),
    ("The Shadow Has No Substance", "Her weapon attack strikes twice, and the first blow that would hit her each "
     "battle passes through."),
    ("The Shadow Has No Soul", "30% more critical hits against a foe that hasn't acted yet or is open."),
    # Ide Tamotsu (Ide Emissary)
    ("The Heart Listens", "At the start of a battle he reads every foe: their weaknesses are known."),
    ("When the Veil Moves", "Once a battle, a heavy blow on anyone in the party is halved."),
    ("Piercing the Veils", "While he stands, the party takes 10% less damage."),
    ("The Immovable Hand of Peace", "Once a battle (Support): a foe can't act against him while he doesn't attack."),
    # Sayo (user 2026-11-12): R1 her ronin pick; R2-R4 the Forest Killers (Fealty & Freedom p.148-150: Fool's Harvest,
    # Canopy of Knives; the third is ours), R5 Ronin Duelist R1 (The Wind Technique)
    ("Forest Killer: Fool's Harvest", "From the trees: +50% damage against a foe that hasn't acted yet, and she moves "
     "faster after striking it."),
    ("Forest Killer: Canopy of Knives", "Her weapon attack strikes twice, and her first blow each battle is a sure "
     "critical against a slower foe."),
    ("Forest Killer: Ghost of the Shinomen", "+20% evasion; a foe she has cut has a harder time hitting her (+20% "
     "evasion against it)."),
    ("Ronin Duelist: The Wind Technique", "Twice as quick to act: Speed +30% for the whole battle."),
]
# Advanced schools (user 2026-11-12: "For level 75, 90, 100 lets add an advanced school for each of the travelers to
# unlock and gain, If they have level passed it have it apply the schools retroactively" - lvoption by level is
# retroactive by nature). Skills S800-S823; effects RokuganRanks.sk ADV (tier I damage, II evasion, III crit + a hit).
ADV_LEVELS = (75, 90, 100)
# (user: "advanced schools are real schools listed in books") 3e advanced schools and their technique names: The Four
# Winds (Hida Avenger p.7, Kenshinzen p.7, Student of the Tao p.8, Shadow-Hunters p.12, Master of the Courts p.13,
# Master of the Elements p.14) and the 3e supplement index (Master General, The Machi-Kanshisha) -
# _research/books_txt/1592510476074.txt "Index of the Advanced Schools". Effects are our Octopath translation.
ADV_SCHOOLS = {
    "P100": ("Hida Avenger", ["Wrath of the Crab", "Be the Wall", "Hida's Technique"]),
    "P101": ("Kenshinzen", ["Drawing the Void", "A Single Moment", "Kakita's Technique"]),
    "P102": ("Student of the Tao", ["Path of Wisdom", "Seek the Path", "Defining the Essence"]),
    "P103": ("Master General", ["Eyes of the Army", "Arms of the Army", "Heart of the Army"]),
    "P104": ("Master of the Elements", ["Stone Among the Flames", "Wind Among the Waves", "The Secrets Between All "
                                                                                         "Things"]),
    "P105": ("Shadow-Hunters", ["Strike of the Righteous", "Scent of the Prey", "Strike from the Darkness"]),
    "P106": ("Master of the Courts", ["The Emperor's Grace", "Favored Among the Heavens", "Voice of the Sun and Moon"]),
    "P107": ("The Machi-Kanshisha", ["Smoke and Mirrors", "Clouded Mind", "Wear Them Down"]),
}
ADV_EFFECT = ["+15% damage.", "+15% evasion and +10% damage.", "20% more critical hits; the weapon attack strikes "
              "once more."]
ADV_SKILLS, ADV_FIRST = {}, 800
for _k, (_pid, (_school, _techs)) in enumerate(sorted(ADV_SCHOOLS.items())):
    for _i, _t in enumerate(_techs):
        ADV_SKILLS["S%03d" % (ADV_FIRST + 3 * _k + _i)] = (
            _pid, ADV_LEVELS[_i], "%s %s: %s" % (_school, "I" * (_i + 1), _t),
            "Advanced school technique (Lv %d). %s" % (ADV_LEVELS[_i], ADV_EFFECT[_i]))
# Companions' school ranks (user 2026-11-12: "make sure all the companions got the new school rank up techniques at the
# right levels as well"): their own schools' 3e technique names (core: Hida, Matsu Berserker, Yoritomo, Seppun
# Guardsman, Shiba; The Four Winds: Shinjo, Doji Magistrate; Hiruma / Akodo as the travelers'). Shugenja companions get
# two spells per rank instead (3e core). Effects: plugin RokuganVoidCrit.sk COMP_FX (cumulative per rank).
COMP_SCHOOLS = {
    "P120": ("hida", ["The Mountain Does Not Move", "Two Pincers, One Mind", "Fury of Hida",
                      "The Mountain Does Not Fall"]),
    "P121": ("hiruma", ["Strike Like the Wind", "Fire and Shadow", "Harness the Wind", "Veil of Spirits"]),
    "P123": ("hiruma", ["Strike Like the Wind", "Fire and Shadow", "Harness the Wind", "Veil of Spirits"]),
    "P126": ("hiruma", ["Strike Like the Wind", "Fire and Shadow", "Harness the Wind", "Veil of Spirits"]),
    "P127": ("akodo", ["Strength of Purity", "Strength of My Ancestors", "Triumph Before Battle",
                       "Akodo's Final Lesson"]),
    "P129": ("akodo", ["Strength of Purity", "Strength of My Ancestors", "Triumph Before Battle",
                       "Akodo's Final Lesson"]),
    "P130": ("akodo", ["Strength of Purity", "Strength of My Ancestors", "Triumph Before Battle",
                       "Akodo's Final Lesson"]),
    "P138": ("akodo", ["Strength of Purity", "Strength of My Ancestors", "Triumph Before Battle",
                       "Akodo's Final Lesson"]),
    "P128": ("matsu", ["Matsu's Fury", "The Lion's Charge", "Matsu's Courage", "The Lion's Victory"]),
    "P141": ("matsu", ["Matsu's Fury", "The Lion's Charge", "Matsu's Courage", "The Lion's Victory"]),
    "P131": ("shiba", ["Dancing with the Elements", "One with the Void", "Move with the World", "Touch of the Void"]),
    "P133": ("doji", ["The Eyes of Doji", "Strike of the Just", "Judgment's Swift Blade", "Eternal Justice"]),
    "P134": ("seppun", ["The Clouds Part", "With Heaven's Speed", "The Sun's Light Reveals", "Heaven Never Falls"]),
    "P136": ("yoritomo", ["Voice of the Storm", "Strike of the Mantis", "The Rolling Wave", "Hand of Osano-Wo"]),
    "P140": ("shinjo", ["Dance of the Blade", "The Four Winds Strike", "Spirit of Our Lady",
                        "Dancing with the Fortunes"]),
    "P124": ("isawa", None), "P135": ("isawa", None), "P137": ("isawa", None), "P139": ("tamori", None),
}
# the school each player fights as (Void-crit shouts and companion effects in RokuganVoidCrit.sk)
SCHOOL_KEY = {"P100": "hiruma", "P101": "kakita", "P102": "kitsuki", "P103": "akodo", "P104": "isawa",
              "P105": "shosuro", "P106": "ide", "P107": "ronin", "P132": "togashi",
              **{k: v[0] for k, v in COMP_SCHOOLS.items()}}
# per-rank effect text for the companion schools (the plugin's COMP_FX in the same order: Rank 2, 3, 4, 5)
COMP_FX_TEXT = {
    "hida": ["Takes 15% less damage.", "The weapon attack strikes twice.", "+20% damage.", "Takes 20% less damage."],
    "hiruma": ["+15% damage.", "+15% evasion.", "The weapon attack strikes twice.", "+15% critical hits."],
    "akodo": ["+15% damage.", "The weapon attack strikes twice.", "+10% damage.", "+20% critical hits."],
    "matsu": ["+20% damage.", "The weapon attack strikes twice.", "Takes 10% less damage.", "+20% damage."],
    "shiba": ["+15% evasion.", "Takes 10% less damage.", "+15% damage.", "The weapon attack strikes twice."],
    "doji": ["Every foe's weaknesses are read at the start of a battle.", "+20% damage.",
             "The weapon attack strikes twice.", "+20% critical hits."],
    "seppun": ["+15% evasion.", "Speed up for the whole battle.", "+20% critical hits.", "Takes 15% less damage."],
    "yoritomo": ["+15% damage.", "The weapon attack strikes twice.", "+15% evasion.", "+20% critical hits."],
    "shinjo": ["Speed up for the whole battle.", "The weapon attack strikes twice.", "+15% evasion.", "+20% damage."],
}
COMP_RANK_FIRST = 830
COMP_RANK_SKILLS = {}                                      # sid -> (pid, level, name, desc)
for _k, (_pid, (_school, _techs)) in enumerate(sorted(COMP_SCHOOLS.items())):
    for _i in range(4):
        _sid = "S%03d" % (COMP_RANK_FIRST + 4 * _k + _i)
        if _techs:
            COMP_RANK_SKILLS[_sid] = (_pid, RANK_LEVELS[_i], "Insight Rank %d: %s" % (_i + 2, _techs[_i]),
                                      "School technique (Rank %d, Lv %d). %s" % (_i + 2, RANK_LEVELS[_i],
                                                                                COMP_FX_TEXT[_school][_i]))
        else:
            COMP_RANK_SKILLS[_sid] = (_pid, RANK_LEVELS[_i], "Insight Rank %d: Mastery %d Spells" % (_i + 2, _i + 2),
                                      "Two new spells (3e: two per Insight Rank).")
RANK_SKILLS = {}
for _pid, _base in RANK_PIDS.items():
    for _i in range(4):
        _n, _d = _R[(_base - 700) + _i]
        RANK_SKILLS["S%03d" % (_base + _i)] = ("Insight Rank %d: %s" % (_i + 2, _n), "School technique (Rank %d, "
                                               "Lv %d). %s" % (_i + 2, RANK_LEVELS[_i], _d))


def rank_options(pid):
    base = RANK_PIDS.get(pid)
    if base is None:                           # a companion: their school's ranks (shugenja: + two spells per rank)
        o = [{"LV": lv, "opttype": "opt_getskill", "skillid": sid}
             for sid, (p_, lv, _n, _d) in sorted(COMP_RANK_SKILLS.items()) if p_ == pid]
        return o                               # (shugenja companions' spells: rank_spells, added with their kit)
    o = [{"LV": lv, "opttype": "opt_getskill", "skillid": "S%03d" % (base + i)} for i, lv in enumerate(RANK_LEVELS)]
    if pid == "P102":                          # Gendo R2 Wisdom the Wind Brings: confuse, fear, charm can't take hold
        o.append({"LV": RANK_LEVELS[0], "opttype": "opt_conddef", "CDR.4": 100, "CDR.7": 100, "CDR.8": 100})
    o += [{"LV": lv, "opttype": "opt_getskill", "skillid": sid} for sid, (p_, lv, _n, _d) in sorted(ADV_SKILLS.items())
          if p_ == pid]
    return o


def localise(kind, d):
    for k, en in LOCAL[kind].items():
        if k in d:
            d[k]["name"] = en          # these tables take a plain string (a {ja,en} dict prints as "table:...")


SPELL_CONDS = [  # (kind, regex, cond)  status effects mapped from spell descriptions
    ("buff", r"\bdef\b|e\.def|damage taken|armou?r|physical damage", "K022"),
    ("buff", r"\batk\b|steel|blade|crit|weapon", "K020"),
    ("buff", r"reflect", "K043"), ("buff", r"lethal|endure|survives", "K042"),
    ("heal", r"every turn|regrow|hot\b", "K040"),
    ("debuff", r"sleep|slumber", "K005"), ("debuff", r"blind|accuracy", "K002"),
    ("debuff", r"silence|deafen", "K003"), ("debuff", r"poison", "K001"), ("debuff", r"terror", "K007"),
    ("debuff", r"loses its turn|skips|rooted|paraly|down", "K006"), ("debuff", r"confus", "K004"),
    ("debuff", r"def −|e\.def −|def and e\.def", "K023"), ("debuff", r"atk −|atk and|e\.atk", "K021"),
    ("debuff", r"speed", "K021"),
]


def spell_atk(power):
    """Magic damage (dmgform 1: atk - dst.MDEF): mirrors physical 2.1 x PATK."""
    return "src.MATK*2.0+%d" % power


def heal_atk(power):
    """Heals (dmgform 7, def 0): caster's MATK + power + a share of the target's max HP (scales with both levels)."""
    return "src.MATK*0.9+%d+dst.MAXHP*%d/300.0" % (power, power)


def spell_skills(s):
    """Skills S300+ from data/rt_spells.json (tools/gen_spellfx.py): one per battle spell, with its own cast pose
    (useani cast_<cat>) and its own hit effect (FX400+)."""
    import re
    mpath = os.path.join(DATA, "rt_spells.json")
    if not os.path.exists(mpath):
        return
    s["_meta"] = dict(s.get("_meta", {}), caps=999)
    spells = json.load(open(mpath, encoding="utf-8"))
    for sp in spells:
        kind = sp["kind"]
        tmpl = {"attack": "S111", "heal": "S035", "buff": "S045", "debuff": "S045"}[kind]
        k = copy.deepcopy(s[tmpl])
        cost = max(1, sp["sp"])
        k.update({"name": sp["name"], "desc": "%s (%s %d). %s" % (sp["name"], sp["elem"], sp["ml"], sp["effect"]),
                  "addlist": True, "enemyuse": False, "consume": [0, cost], "cmdtgt": sp["tgt"],
                  "elembits": B[sp["elem"]], "eqtypebits": 2047, "occasion": 3 if kind == "heal" else 1})
        if kind == "attack":
            k.update({"dmgform": 1, "atkform": spell_atk(int(20 + cost * 2.5))})
        elif kind == "heal":
            k.update({"dmgform": 7, "atkform": heal_atk(int(30 + cost * 3))})
        else:
            k["skilltype"] = kind
            k.pop("dmgform", None)
        en = (sp["name"] + " " + sp["effect"]).lower()
        bits, by_id = 0, None
        for kd, rx, cid in SPELL_CONDS:
            if kd == kind and re.search(rx, en):
                if int(cid[1:]) > 30:                  # a high bit decodes as the wrong condition (Regen bit 40 spammed
                    by_id = cid                        # the party with statuses until it crashed): put it by id
                else:
                    bits |= 1 << int(cid[1:])
                break
        if kind in ("buff", "debuff"):
            k["putconds"] = bits                       # never inherit the template's Guard Up
        elif kind == "heal" and bits:
            k["putconds"] = bits
        if by_id:
            k["putconds"] = 0
            k["option"] = [o for o in (k.get("option") or []) if o.get("opttype") != "opt_putcond"] + [
                {"condid": by_id, "efx_start": None, "opttype": "opt_putcond", "rate": 1.0, "showmiss": False,
                 "when": 0, "whom": 0}]
        if sp["elem"] == "Void":                       # Void spells cost VP, not SP (haruki-spells.md §1)
            k["consume"] = [0, 0]
            k["rt_vp"] = 0 if sp["name"] == "Drawing the Void" else (1 if sp["ml"] <= 2 else 2 if sp["ml"] <= 4 else 3)
        if "cure poison" in en or "cleanse" in en:
            k["remconds"] = 1 << 1
        ua = k.setdefault("useact", {"id": "use_charge", "scp": None})
        ua["id"] = "use_charge"
        ua["useani"] = {"id": "cast_" + sp["cat"], "mdlid": "CV000", "part": 0, "spd": 1.0}
        ua["useefx"] = None
        ua["usesnd"] = "SE229"                       # use_charge needs useani/usesnd/useefx
        ha = k.setdefault("hitact", {"id": "hit_normal", "scp": None, "hitdelay": 100, "hitsnd": "SE220"})
        ha["hitefx"] = sp["fx"]
        k["aimani"] = {"id": "cast_" + sp["cat"], "mdlid": "CV000", "part": 0, "spd": 1.0}
        s[sp["skill"]] = k


def haruki_spells():
    """Haruki's spell learning: starting kit at Lv 1, then the haruki-spells.md §4 curve."""
    import re
    mpath = os.path.join(DATA, "rt_spells.json")
    if not os.path.exists(mpath):
        return []
    by_name = {sp["name"].lower(): sp["skill"] for sp in json.load(open(mpath, encoding="utf-8"))}
    doc = open(os.path.join(HERE, "..", "docs", "rules", "haruki-spells.md"), encoding="utf-8").read()
    opts = []
    for nm in ("Path to Inner Peace", "Bo of Water", "Drawing the Void", "The Fury of Osano-wo", "Tempest of Air",
               "Earth's Touch", "Counterspell"):
        if nm.lower() in by_name:
            opts.append({"LV": 1, "opttype": "opt_getskill", "skillid": by_name[nm.lower()]})
    sec = doc[doc.index("## 4."):doc.index("## 5.")]
    for m in re.finditer(r"^\| (\d+)[^|]*\| ([^|]+)\|", sec, re.M):
        lv = int(m.group(1))
        # (user 2026-11-12: "shugenja just get more spells at rank until advanced school ... how many of each they get
        # per rank in the books") 3e core: "When your shugenja increases in Insight Rank, you may select any two
        # spells that you could now potentially cast." Below Rank 2 the school's gifts stay (Lv 5, 10); from Rank 2
        # on, only the two spells of each rank level (15 / 30 / 45 / 60) are learned.
        if lv >= RANK_LEVELS[0]:
            continue                                   # (rank spells: HARUKI_RANK_SPELLS below)
        for nm in m.group(2).split(","):
            nm = re.sub(r"\*+", "", nm).strip().lower()
            if nm in by_name:
                opts.append({"LV": lv, "opttype": "opt_getskill", "skillid": by_name[nm]})
    return opts + rank_spells("P104", {o["skillid"] for o in opts})


# The shugenja's elements (user 2026-11-12: rank spells "should match the element of the shugenja"): Haruki's affinity
# Water (+ his Void spell each rank: "2 per rank plus one void spell"); the companions by their kits.
SHUGENJA_ELEM = {"P104": "Water", "P124": "Fire", "P135": "Earth", "P137": "Air", "P139": "Fire"}


def rank_spells(pid, known):
    """Rank 2-5 spells (3e core: two new spells per Insight Rank, Mastery up to the rank): two of the shugenja's
    element - the highest mastery they can now cast first - and for Haruki one Void spell more."""
    mpath = os.path.join(DATA, "rt_spells.json")
    if not os.path.exists(mpath) or pid not in SHUGENJA_ELEM:
        return []
    spells = json.load(open(mpath, encoding="utf-8"))
    known, opts = set(known), []
    for i, lv in enumerate(RANK_LEVELS):
        rank = i + 2
        for elem, n in ((SHUGENJA_ELEM[pid], 2),) + ((("Void", 1),) if pid == "P104" else ()):
            pool = sorted((sp for sp in spells if sp["elem"] == elem and sp["ml"] <= rank and sp["skill"] not in known),
                          key=lambda sp: (-sp["ml"], sp["name"]))
            if elem == "Water" and rank == 2 and "S799" not in known:      # Stand Against the Waves first (Water 2)
                pool = [{"skill": "S799", "ml": 2, "name": "Stand Against the Waves"}] + pool
            for sp in pool[:n]:
                known.add(sp["skill"])
                opts.append({"LV": lv, "opttype": "opt_getskill", "skillid": sp["skill"]})
    return opts


def crab_items(it):
    """Crab Ch1 consumables (rules/equipment.md: Rice Ball 20 zeni, Salt Herring, Eye Drops, Jade Dust...)."""
    def heal(iid, name, pct, price, desc):
        x = copy.deepcopy(it["I001"])
        x.update({"name": name, "atkform": str(pct), "price": price, "desc": desc})
        it[iid] = x
    heal("I100", "Rice Ball", 20, 20, "A Wall ration wrapped in leaves. Restores some HP.")
    heal("I101", "Herbal Salve", 40, 60, "Bitter green paste. Restores a good deal of HP.")
    heal("I102", "Salt Herring", 15, 2, "Two zeni, or one if you smile.")
    eye = copy.deepcopy(it["I018"])
    eye.update({"name": "Eye Drops", "desc": "Cures Blind.", "remconds": 1 << 2, "price": 15})
    it["I103"] = eye
    it["I018"]["name"] = "Antidote"
    it["I018"]["desc"] = "Cures Poison."
    jade = copy.deepcopy(it["I001"])
    sk = json.load(open(os.path.join(BACKUP, "skill.json"), encoding="utf-8"))
    jade.update({"name": "Jade Dust", "desc": "A pinch of powdered jade. Burns the Tainted (Jade damage).", "price": 80,
                 "skilltype": "attack", "cmdtgt": 1, "dmgform": 1, "atkform": "45", "dmgtype": 1,
                 "elembits": B["Jade"], "occasion": 1})
    jade["hitact"] = dict(jade.get("hitact") or {}, hitefx="FX016")
    it["I104"] = jade
    for iid, name, desc in (
            ("I110", "Kite Mirror", "A child's signal mirror, found in the Egg Caves. Return it in Hoshi-no-Ichi."),
            ("I111", "Wooden Fish", "A carved fish with careful fins. Gonta's boy made it."),
            ("I112", "Pearl Hairpin", "A cheap, pretty hairpin. Kiyo's, by the look of it."),
            ("I113", "Scroll: Summon Fog", "A shugenja's field scroll (Water). Haruki can learn it.")):
        k = copy.deepcopy(it["I000"])
        k.update({"name": name, "desc": desc, "itemtype": 1, "price": 0, "occasion": 0})
        it[iid] = k
    egg = copy.deepcopy(it["I018"])
    egg.update({"name": "Painted Egg", "desc": "Daubed with a child's nightmare. Cracking it cures Silence. (Ryozo's)",
                "remconds": 1 << 3, "price": 30})
    it["I114"] = egg
    heal("I190", "Ginseng Tonic", 70, 400, "A bitter root tonic from the year-400 market. Restores most of your HP.")
    heal("I115", "Drop Soup", 30, 0, "No egg. Just the drop. Very pure. Very Crab. Kiyo's thank-you.")
    k = copy.deepcopy(it["I000"])
    k.update({"name": "Hidden Ones' Thanks", "itemtype": 1, "price": 0, "occasion": 0,
              "desc": "A carved fish, the twin of the one you returned. Gonta will come once if you ask (Crab Ch2)."})
    it["I116"] = k
    k = copy.deepcopy(it["I000"])
    k.update({"name": "Crow Feather", "price": 30, "occasion": 0,
              "desc": "Glossy and black. The kite child swears it brings luck. Merchants pay a little."})
    it["I117"] = k
    for iid, name, desc in (
            ("I120", "Blue Flare", "Takakana's third flare. Blue: something none of us has seen before."),
            ("I121", "Filed Chain Link", "From the troll's chains. The cut is clean and bright: a rasp, not a "
                                         "struggle."),
            ("I122", "Blue-Silk Veil Thread", "From Kuhime's room. Silk from the Crane coast, not the Phoenix."),
            ("I123", "Unicorn Dance Ribbon", "Keiyomi's ribbon from the Tunnel of Quiescent Flame."),
            ("I124", "Kaiu Tetsubo Blueprint", "A forge-master's plan. Sells for a fortune, or trade it at a Kaiu "
                                               "forge."),
            # Crane Ch1 (production/crane-ch1.md)
            ("I140", "Heaven's Glory", "Heaven's Glory Reflected in the Soul's Steel: a Kakita wakizashi. Look at it "
                                       "and you measure yourself against the ideal samurai. (Key item)"),
            ("I141", "Pleasant Eaves Tax Ledger", "Lord Goroso's taxes on the village, year by year. They have tripled."),
            ("I142", "Morishu's Inro", "A letter inside, to his mother. Never sent."),
            ("I143", "Tide Chart", "The harbour master's chart: the land-bridge is open at low tide, dawn and dusk."),
            # Crane Ch3 (production/crane-ch3.md)
            ("I144", "Tadanobu's Letters", "From Chihaya's sash: a Lion patron pays the White Squid to bleed the Crane "
                                           "coast. Signed Matsu Tadanobu."),
            ("I145", "The Emperor's Screen", "The stolen tribute: a lacquered screen for the Emperor's winter palace. "
                                             "Slightly damp."),
            # Crane Ch4 (production/crane-ch4.md)
            ("I147", "The Empress of Nothing", "A noh play, banned four hundred years. Written by \"a survivor of the court "
                                               "of Komatsu\". It knows Doji Nashiko's weaknesses. (Key item)"),
            ("I149", "Komatsu's Steward's Diary", "Misfiled for four centuries. It mentions \"the bride who never "
                                                  "blinked\"."),
            # Lion Ch1
            ("I151", "Crane Spy's Note", "From the tea house's back room: troop counts on Lord Hiruto's border, in a "
                                         "Crane hand."),
            ("I152", "Jade Chains", "Isawa Hoju forged them to bind O-Tamai. The lock grows cold when it faces the "
                                    "spirit. (Key item: a compass)"),
            ("I155", "Bloodspeaker's Ring", "O-Tamai's ring, slid off a borrowed finger. Cold, and it hums. "
                                            "(Lore)"),
            ("I157", "Scroll of Acclaim", "The painting contest's prize: a scroll in a judge's hand, praising a "
                                          "snowflake on a sword blade."),
            ("I158", "Kafu's Love Letters", "Letters between Akodo Kafu and Akodo Nishi. The oni read them aloud in "
                                            "his own voice."),
            ("I159", "The Lacquered Tube", "Toturi's message for the old man of Kaze-no-Tani, sealed with the "
                                           "Champion's mon. Cracked by the cold. \"Kill these messengers.\""),
            ("I160", "Miya Letters", "A Miya travel writ, and a letter to a Crane general in the same hand: \"the "
                                     "Lion will attack at the river by the next moon\". The Lion have no such plan."),
            ("I164", "Rokuro's Gratitude", "Matsu Rokuro's own sword-knot, given in the shallows. \"I was so "
                                           "frightened. Thank you.\""),
            ("I165", "Stamped Crate Lid", "A charred crate lid from the Magonojo warehouses, stamped with Crane army "
                                          "supply marks. The Phoenix were feeding the Crane."),
            ("I166", "Hoju's History", "Isawa Hoju's unfinished history of a family that doesn't want one. \"In the "
                                       "third year, the family's shugenja bound a grave evil in the west.\""),
            ("I167", "A Folded Note", "A child's folded note from under the Jade Chains, in Haruki's own "
                                      "handwriting. He hasn't unfolded it."),
            ("I169", "\"The Consumer\"", "Ikoma Sadahisa's scroll: an undying dark side of the Phoenix, reborn in its "
                                         "greatest shugenja. Written in fear, by a gentle hand: Mieko's."),
            ("I171", "Scroll: Tremor", "An Isawa field scroll from the treaty archive: Tremor shakes loose what is "
                                       "stuck in stone. (Field spell)"),
            ("I172", "Scroll: Courage of the Seven Thunders", "From the Silent Court's masters, for the boy who "
                                                              "refused to forget. Haruki knows the spell now."),
            ("I173", "Scroll: Hand of Jurojin", "A dying healer's scroll. \"It won't cure this. It'll teach you what "
                                                "cure means.\" Haruki knows the spell now."),
            ("I174", "Scroll: Dreamwalker", "A secret of Air from Isawa Uona: walking in another's dreams. \"I think "
                                            "you'll need it soon.\""),
            ("I176", "A Child's Go Stone", "A black go stone from Mieko's childhood room. A captured stone, once."),
            ("I178", "Oharu's Seal", "Kitsuki Oharu's magistrate seal, pressed into a junior yoriki's hand. \"They won't "
                                     "respect it in your hands. Use it anyway.\""),
            ("I179", "Tortoise Ferry Token", "A ferry token for Tortoise Island, from the beach. Kumpei's sail went "
                                             "that way."),
            ("I180", "The Monks' Notes", "Oiled paper from the hollow in the Gusai wall: \"Ayaru. Then Jotaro. Then "
                                         "Nobue. Each of us has followed the old man.\" Togashi Akuro."),
            ("I181", "Rare Blue Pigment", "From Kakita Kumpei's paint box: the same rare blue as the stolen tattoos' "
                                          "ink."),
            ("I182", "Tamori Alembic", "Dragon work, Tamori-style: an alembic from the new house on Tortoise "
                                       "Island. Our own clan's tools, in a murderer's kitchen."),
            ("I183", "Brass Star-chart", "A Dragon star-chart from the new house, marked in an old man's hand: dates, "
                                         "not stars. A map of when."),
            ("I184", "Kumpei's Ink Pot", "From the paint scraps in the cove: a pot of the same rare blue, still wet. "
                                         "It moves when you aren't looking."),
            ("I187", "Koshi's Wakizashi", "The old Mirumoto's short blade. \"Clerks know the second stroke corrects "
                                          "the first.\" (Daisho Technique)"),
            ("I188", "Three Invitations", "Three lacquered invitations from three gozoku lords. Three dinners, all at "
                                          "the same hour."),
            ("I189", "Gaijin Mirrors", "Small silvered mirrors, bought back from Kakita Miyoshi. They won't exist here "
                                       "for two hundred years. (She kept one.)"),
            ("I191", "Crane Ward Fan", "Doji Tomeko's gift: a fan painted with the Crane's first wards. Lore, and worth "
                                       "a great deal to a collector."),
            ("I193", "The Scorched Map", "Gendo's copy of the coast burned into Shiro Izumida's floor: landing points, "
                                         "dates, arrows. An invasion plan."),
            ("I194", "The Kami-ichor Vial", "The last vial of kami-ichor (Togashi's blood), saved from Kumpei's hip "
                                            "before it went over the rail."),
            # Scorpion Ch1 "Blood and Iron" (production scorpion-ch1 S08): the cursed box, Norie's favour
            ("I195", "The Iron Box", "Iron. Plain. A finger long. It once held the heart of Iuchiban, and it hums like "
                                     "a heartbeat through a wall. No tool we own can break it. (Cursed: Mitsue starts "
                                     "every battle with no Void)"),
            ("I196", "Scorpion \"Favor\"", "A blood-red jasper scorpion. Shosuro Norie owes the bearer one "
                                           "impossible thing. Forgeries shorten lives."),
            # Scorpion Ch2 "City of Masks"
            ("I401", "Hatomu's Map", "Miya Hatomu's map of a city that didn't exist. Every street. Every one."),
            ("I402", "Antique Travel Papers", "Rolled up inside Giseiki's mask: travel papers under the chop of a "
                                              "Scorpion lord three hundred years dead."),
            # Scorpion Ch3 = Unicorn Ch2 "Fortunes Lost"
            ("I403", "The Clapperless Bell", "A ceramic bell the size of a baby's fist, with no clapper. Gochu was "
                                             "paid five koku to shake it whenever Akodo Rin was alone."),
            ("I404", "General Furayaru's Letter", "Folded very small. \"...the war was set moving from Kyuden "
                                                  "Bayushi. By the Champion's own hand. A distraction.\" Tell no "
                                                  "one."),
            ("I405", "Wax Earplugs", "Beeswax, warmed in the hand. Whatever you don't hear can't get into you. "
                                     "(Covered Ears)"),
            # Scorpion Ch4 "The Eve" (production scorpion-ch4 S08): Mitsue's own Favors
            ("I406", "Jasper Scorpions", "Small blood-red jasper scorpions: Mitsue's own Favors. One impossible thing "
                                         "each, from a nobody. Don't waste them on dinner."),
            # Unicorn Ch1 "Fault Lines"
            ("I407", "A Grey Pebble", "Smooth from twenty years in a pocket. Naohida paid for rice cakes with it when "
                                      "they were nine. Tamotsu took it."),
            ("I408", "The Case Notes", "The tribunal's strongbox notes on eight grievances, in three hands. Tsune's "
                                       "says \"Scorpion\" in the margin of every page."),
            # Unicorn Ch3 "The Noblest Blood"
            ("I413", "The Foreman's Ledger", "The jade mine's last ledger. The final page is an order to close the "
                                             "mine to everyone but the old master's men, in Kurosho's own hand."),
            ("I414", "Nihime's Note", "\"My son goes to the castle. Bring him home, if there is a home.\" Folded small, "
                                      "next to the pebble."),
            # Unicorn Ch4 "Regret"
            ("I416", "Karasu's Tuning Fork", "An iron fork that hums one note forever. Karasu says a song sung "
                                             "backwards against it comes out the right way round."),
            ("I417", "The Pigeon's Letter", "A letter for Kurosho, in a courtesan's perfect hand, carried by a Yotomo "
                                            "pigeon. Three words: Look at me."),
            # Ronin Ch1 "What's Eating the Eta"
            ("I425", "The Sono Chit", "\"Payment, Daigoro's band.\" Stamped with a Sono household seal. The judge's "
                                      "family is paying the murderer's friends."),
            ("I426", "Ieko's Love Poem", "A love poem from Mibu Ieko to the poet O-Sode, never delivered. The brushwork "
                                         "is terrible. The feeling isn't."),
            ("I427", "The Pilgrims' Loot", "Four goblin baskets: offering coins, paper prayers, a bronze bell, a biwa, "
                                           "two large radishes."),
            # Ronin Ch2 "The Noble and the Ronin"
            ("I430", "Snake Beads", "Jinnai's prayer beads. One bead is a tiny carved snake. \"The mountain is "
                                    "yours.\" The Mountain of the White Snow."),
            ("I431", "Snake Ring", "An iron ring from an enforcer's pack, a snake swallowing its tail. Inside the band, "
                                   "very small: \"The line must stay true.\""),
            ("I432", "Sadanobu's Travel Writ", "An Ikoma travel writ, sealed in gold wax, fluttered off a young "
                                               "lord's saddle. Lion checkpoints wave its bearer through."),
            ("I435", "Kanemori's Discount", "A Yasuki chit, signed with a flourish: \"Ten off, for the matchmaker.\" "
                                            "Floating Flowers shops sell for less."),
            # Ronin Ch3 "The Village of the Wounded Lion"
            ("I437", "Climbing Spikes", "Iron spikes that strap to straw sandals. Pilfered from an outfitter who "
                                        "charges pilgrims double. The ice ledges hold for them."),
            ("I438", "Silver Rattle", "A baby's rattle of silver, chrysanthemums worked into it, from a frozen "
                                      "nursery. It has not been shaken in three hundred years."),
            ("I440", "Hikaru's Kata Scroll", "Two swords, drawn in a few strokes of ink, moving like a storm. Hikaru "
                                             "left it in the snow. Someday a Mirumoto student might read it."),
            # Ronin Ch4 "The Oracle's Choice"
            ("I441", "The Cipher Letter", "Lifted from a pilgrim's sleeve. Under the cipher, in a careless hand: "
                                          "\"Poison the eta well before the ascension.\""),
            ("I442", "Back-gate Key", "An iron key as long as a hand, from the old priest who sweeps the lower shrine. "
                                      "The crater shrine's back gate, above the last switchback."),
            # The finale, Act 2 (F07: the glade)
            ("I443", "\"Duty\" Plaque", "Old Lion work, a single word cut deep: DUTY. Stolen from Shiro Akodo and "
                                        "nailed to a tree in the Shinomen to be laughed at. Shizue carries it now."),
            ("I177", "\"Against the Bloodspeakers\"", "The Phoenix book of every ward against the Bloodspeakers, a "
                                                      "hundred years in the writing. One page is marked with a dried "
                                                      "camellia petal: \"On the Bride of Fu Leng, who wears the faces "
                                                      "of the beloved...\"")):
        k = copy.deepcopy(it["I000"])
        k.update({"name": name, "desc": desc, "itemtype": 1, "price": 1500 if iid == "I124" else 0, "occasion": 0})
        it[iid] = k
    for iid, name, pct, price, desc in (("I125", "Fine Sake", 30, 120, "Restores SP. (Confuse chance 5%)"),
                                        ("I126", "Incense Stick", 0, 90, "A temple stick. +1 VP now."),
                                        ("I127", "Calming Tea", 0, 40, "Cures Terror.")):
        k = copy.deepcopy(it["I018"])
        k.update({"name": name, "desc": desc, "price": price})
        it[iid] = k
    it["I127"]["remconds"] = 1 << 7
    for iid, name, pct, price, desc in (("I125", "Fine Sake", 30, 120, "Restores SP."),
                                        ("I168", "Rejuvenating Tea", 25, 50, "A Phoenix temple tea. Restores some SP.")):
        k = copy.deepcopy(it["I001"])                   # heal template, dmgtype 4: SP (engine DamageTypePID)
        k.update({"name": name, "desc": desc, "price": price, "atkform": str(pct), "dmgtype": 4})
        it[iid] = k
    caltrop = copy.deepcopy(it["I104"])
    caltrop.update({"name": "Kaiu Iron Caltrops", "desc": "Scattered underfoot: every enemy slows.", "price": 150,
                    "cmdtgt": 3, "atkform": "10", "elembits": 0})
    it["I128"] = caltrop
    ward = copy.deepcopy(caltrop)                     # Crane Ch3: the Temples of the Sun sell the one-battle version
    ward.update({"name": "Ward-paper Strip", "desc": "An Asahina ward on a paper strip. Burns the false charms off "
                 "every enemy.", "price": 180, "atkform": "1", "remconds": sum(1 << n for n in range(44, 50))})
    it["I146"] = ward
    k = copy.deepcopy(it["I000"])                       # Crane Ch4: the castle town's C chest (sell)
    k.update({"name": "Doji Mon Charm", "price": 500, "occasion": 0, "desc": "A Doji crest in silver thread. Sells."})
    it["I148"] = k
    k = copy.deepcopy(it["I104"])                       # Lion Ch1 C3: Hojiki's real jade (bosses.md: usable as an item)
    k.update({"name": "Hojiki's Jade Stone", "price": 0, "elembits": B["Jade"], "atkform": "90", "desc": "The real jade stone Hojiki "
              "bound to his wound, found on the bathhouse floor. Thrown, it burns what possesses the living. (Jade)"})
    it["I150"] = k
    k = copy.deepcopy(it["I000"])                       # Lion Ch1: Hoju's storeroom at Kamatori (sell)
    k.update({"name": "Hoju's Tea Set", "price": 500, "occasion": 0, "desc": "Isawa Hoju's tea set. He kept it with "
              "his histories. Sells; or a cook in Kamatori might like it back."})
    it["I153"] = k
    k = copy.deepcopy(it["I000"])                       # b_boss_otamai drop (bosses.md: a Jade weapon mod, later)
    k.update({"name": "Jade Chain Fragment", "price": 800, "occasion": 0, "desc": "A link of Hoju's jade chain, "
              "cracked in the binding. A smith could set it in a blade. (Sells)"})
    it["I154"] = k
    k = copy.deepcopy(it["I000"])                       # the finale, Shinomen: the Naga shrine (storyboard D)
    k.update({"name": "Spawn Pearl", "price": 1200, "occasion": 0, "desc": "A pearl black as deep water, left in a "
              "Naga shrine by someone who once lowered a spear. It remembers the sea. (Sells)"})
    it["I444"] = k
    k = copy.deepcopy(it["I104"])                       # Lion Ch2 Beat 2 prize: a Barbed Shot with Jade element
    k.update({"name": "Jade Flesh-cutter Arrow", "price": 0, "elembits": B["Jade"] | B["Yumi"], "atkform": "220",
              "desc": "A jade-headed flesh-cutter arrow, the history dinner's prize. Thrown by hand if you must. "
                      "(Jade)"})
    it["I156"] = k
    # Crab Ch3 (storyboard crab-ch3; equipment.md: Jade Pouch cleanses Taint)
    pouch = copy.deepcopy(it["I018"])
    pouch.update({"name": "Jade Pouch", "desc": "A pinch of jade rubbed into the skin. Cleanses all Taint from one "
                  "ally.", "remconds": 1 << 26, "price": 120})
    it["I130"] = pouch
    heal("I131", "Ginseng Tonic", 60, 240, "A Kaiu field tonic. Restores a great deal of HP.")
    inro = copy.deepcopy(it["I131"])                    # the Seppun duelist's steal: a good medicine case
    inro.update({"name": "Duelist's Inro", "price": 300, "desc": "A Seppun duelist's medicine case. Restores a great "
                 "deal of HP."})
    it["I161"] = inro
    k = copy.deepcopy(it["I104"])                       # Lion Ch4 S04: Gusai's obsidian blade (a battle item, reusable)
    k.update({"name": "Obsidian Blade", "price": 0, "consume": 0, "elembits": 0, "atkform": "260", "rt_obsidian": True,
              "desc": "A black, glassy blade a \"Crane deserter\" sold Gusai. It strips a Fear-demon's guard (3 "
                      "shields). It eats the hand that holds it: every strike Taints the user. (The Jade Finger "
                      "wards it.)"})
    it["I162"] = k
    k = copy.deepcopy(it["I000"])                       # Lion Ch4: Yachiko's baggage (lore; sells)
    k.update({"name": "Miya Seal Wax", "price": 300, "occasion": 0, "desc": "Imperial seal wax, lifted and pressed "
              "again more than once. Yachiko's. (Sells)"})
    it["I163"] = k
    k = copy.deepcopy(it["I104"])                       # Phoenix Ch2: stolen from Hioninmaru - a Fire throw
    k.update({"name": "Bloodspeaker Tattoo-ink", "price": 400, "elembits": B["Fire"], "atkform": "180", "desc": "A "
              "bottle of Hioninmaru's tattoo-ink. It burns like oil when thrown, and smells worse. (Fire, one enemy)"})
    it["I170"] = k
    k = copy.deepcopy(it["I104"])                       # b_boss_oni_no_kuzushi steal: a poison throw
    k.update({"name": "Fever-black Pearl", "price": 600, "elembits": B["Void"], "atkform": "220", "desc": "A black "
              "pearl from the oni's heart, warm as a fever. Crushed and thrown, it sickens what it hits. (Void, one "
              "enemy)"})
    it["I175"] = k
    for iid, name, price, desc in (("I132", "Signal Horn", 300, "An old Hiruma patrol horn. Sells well to "
                                                                 "collectors."),
                                   ("I133", "Old Whetstone", 60, "A patrol's whetstone, worn hollow. Sells."),
                                   ("I134", "Hida Mon Charm", 500, "A Hida banner's crab mon, cut free on the road "
                                                                   "home. Sells.")):
        k = copy.deepcopy(it["I000"])
        k.update({"name": name, "desc": desc, "price": price, "occasion": 0})
        it[iid] = k
    for iid, name, el, desc in (("I135", "Kansen Mist", "Air", "A breath of bottled storm spirit. Air damage to one "
                                                              "enemy."),
                                ("I136", "Oni Ichor", "Fire", "It smokes in the jar. Fire damage to one enemy.")):
        k = copy.deepcopy(it["I104"])
        k.update({"name": name, "desc": desc, "price": 200, "atkform": "70", "elembits": B[el]})
        it[iid] = k
    # Scorpion Ch1: the Miya caravan's crystal (the Kansen counter), the Inari shrine's spring water, smoke pellets
    for iid, name, el, atk, price, desc in (("I197", "Crystal Shard", "Crystal", "110", 0, "A shard of Miya relic "
                                             "crystal. Crystal cuts what steel only annoys: a Kansen, a spirit. "
                                             "(Crystal damage to one enemy)"),
                                            ("I199", "Inari Spring Water", "Water", "45", 60, "Spring water blessed "
                                             "at Kudo's Inari shrine. Corrupted kami hate clean water. (Water damage "
                                             "to one enemy)")):
        k = copy.deepcopy(it["I104"])
        k.update({"name": name, "desc": desc, "price": price, "atkform": atk, "elembits": B[el]})
        it[iid] = k
    k = copy.deepcopy(it["I104"])                       # Unicorn Ch3: the mines' raw jade (production battle note)
    k.update({"name": "Raw Jade", "price": 0, "atkform": "220", "elembits": B["Jade"],
              "desc": "A lump of uncut jade from the Iuchi mines, still gritty. Thrown hard, it burns the dead and the "
                      "Tainted. (Jade damage, one enemy)"})
    it["I410"] = k
    heal("I412", "Carrot", 25, 10, "A carrot from a woodchuck's hoard. The woodchuck has been informed. Restores a "
                                   "little HP.")
    heal("I415", "Spare Wax", 0, 30, "A twist of beeswax. In battle: put the wax back in an ally's ears (Covered "
                                     "Ears again).")
    # Ronin Ch1: Sayo's Remedy ingredients (sayo-remedy.md: a base + a catalyst; the Remedy talent spends them)
    for iid, name, price, desc in (("I418", "Ginseng Root", 30, "Remedy base (Earth): heal. It smells like dirt because "
                                                                 "it remembers the dirt."),
                                   ("I419", "Rhubarb", 20, "Remedy base (Water): purge. Cures what's in the blood."),
                                   ("I420", "Hanabi Powder", 40, "Remedy base (Fire): burst. Firework powder, native "
                                                                 "herbs, quite legal."),
                                   ("I421", "Rice Wine", 15, "Remedy catalyst (Water): stronger."),
                                   ("I422", "Moxa", 25, "Remedy catalyst (Fire): it spreads - to every ally, or every "
                                                        "enemy."),
                                   ("I423", "Willow Bark", 15, "Remedy catalyst (Earth): and a guard (DEF up).")):
        x = copy.deepcopy(it["I000"])
        x.update({"name": name, "price": price, "desc": desc, "occasion": 0, "itemtype": 0})
        it[iid] = x
    k = copy.deepcopy(it["I104"])                       # Ronin Ch1: a brand from Tomie Cho's own fire pit
    k.update({"name": "Firebrand", "price": 0, "atkform": "30", "elembits": B["Fire"],
              "desc": "A burning stick from the fire pit. Thrown, it sets things alight. (Fire damage, one enemy)"})
    it["I428"] = k
    heal("I424", "Old Woman's Tea", 100, 0, "Tomie Cho's tea. It really is very good tea. Restores all HP.")
    heal("I439", "Rice Cake", 35, 40, "A pounded rice cake from the Village of the Wounded Lion. The villagers leave "
                                      "them on the snow mounds and won't say why. Restores some HP.")
    # Ronin Ch2: Snow-Lotus (sayo-remedy.md catalyst: + regen), the den's shadow-scales and fangs (bosses.md steal,
    # storyboard chests: sell-only trophies)
    for iid, name, price, desc in (("I429", "Snow-Lotus", 60, "Remedy catalyst (Water): it keeps on healing (Regen). "
                                                              "From the Phoenix mountains, by way of a Yasuki."),
                                   ("I433", "Shadow Scale", 300, "A scale of solid shadow from the snake den. Cold. "
                                                                 "A Yasuki will pay well, and ask nothing."),
                                   ("I434", "Shadow-snake Fang", 400, "A fang still wet with shadow-venom. Sell it. "
                                                                      "Don't lick it."),
                                   ("I436", "Wild Honey", 30, "Mountain honey in a stoppered gourd. With willow bark, "
                                                              "Ume-baa's cure for a cough that won't go.")):
        x = copy.deepcopy(it["I000"])
        x.update({"name": name, "price": price, "desc": desc, "occasion": 0, "itemtype": 0})
        it[iid] = x
    k = copy.deepcopy(it["I104"])                       # Unicorn Ch1: Naohida's powder (bosses.md steal)
    k.update({"name": "Powder Bomb", "price": 0, "atkform": "90", "elembits": B["Fire"], "cmdtgt": 7,
              "desc": "Gaijin pepper in a clay pot, a fuse in the neck. Forbidden by the Emperor. (Fire damage, all "
                      "enemies)"})
    it["I409"] = k
    k = copy.deepcopy(it["I104"])                       # Scorpion Ch2: Osuko's hunters (storyboard F-1)
    k.update({"name": "Crystal Rosary", "price": 1500, "atkform": "160", "elembits": B["Crystal"], "cmdtgt": 7,
              "desc": "A shadow hunter's rosary of crystal beads, flung apart. (Crystal damage, all enemies)"})
    it["I400"] = k
    it["I197"]["price"] = 400                           # (Ch1: found free in the marsh; Ch2: Osuko sells it)
    k = copy.deepcopy(it["I104"])
    k.update({"name": "Smoke Pellet", "price": 50, "atkform": "1", "elembits": 0, "cmdtgt": 7,
              "desc": "A Shosuro clay pellet of soot and pepper. (Blind chance, all enemies)",
              "option": [{"condid": "K002", "efx_start": None, "opttype": "opt_putcond", "rate": 0.5,
                          "showmiss": True, "when": 0, "whom": 0}]})
    it["I198"] = k
    for iid, name, price, desc in (("I185", "Actor's Mask", 150, "A lacquered theatre mask from the Kyuden Bayushi "
                                    "mask-maker. Sells well anywhere there is a stage."),
                                   ("I186", "Bandit's Purse", 60, "Somebody's purse, stolen by a bandit, stolen "
                                    "back. Sells.")):
        k = copy.deepcopy(it["I000"])
        k.update({"name": name, "desc": desc, "price": price, "occasion": 0})
        it[iid] = k
    k = copy.deepcopy(it["I000"])
    k.update({"name": "Map of the Road Home", "itemtype": 1, "price": 0, "occasion": 0,
              "desc": "Her father's map, the first leg marked in charcoal. Kage carries it now."})
    it["I137"] = k
    k = copy.deepcopy(it["I000"])                     # Crab Ch4 boss drop (bosses.md: Tetsubo upgrade material)
    k.update({"name": "Bone-cage Fragment", "price": 2000, "occasion": 0,
              "desc": "A rib from Oni no Tsukakoro's cage, still warm. Kaiu smiths pay well for it."})
    it["I138"] = k


# Enemy stats from the travelers' growth (measured in-engine: Lv5 HP140 PATK68 PDEF27 AGI22; Lv22 HP446 PATK170
# PDEF92 AGI77). Physical damage = 2.1 x PATK - PDEF (type.json dmgform 0). Targets: a regular enemy hit takes ~14% of
# a traveler's HP; a traveler's hit does 1.5 x PATK, so a regular foe falls to ~2 party actions (HPx 1).
def player_curve(lv):
    return {"HP": 50 + 18 * lv, "PATK": 38 + 6 * lv, "PDEF": 8 + 3.8 * lv, "AGI": 6 + 3.2 * lv}


# Who the foe is tuned to hit: (HP x, PDEF x, share of that HP per hit). "crab" = Natsuko solo (measured in-engine at
# Lv 5-7: HP 1.6x, PDEF 1.5x the average traveler). Damage is subtractive, so foes tuned to "avg" bounce off a Crab
# from about Lv 5 (the Ch1 cave fights did 0-4 damage).
# "crane" = Rensei solo in his Ch1 (measured: HP 0.8x / PDEF 0.83x the average traveler at Lv 2, PDEF 0.93x by Lv 5;
# 0.95 errs toward hits landing, since a few points of DEF over the estimate zero a subtractive hit); a solo Ch1 fight
# should cost 20-40% of his HP, so a hit takes ~8%.
DEFENDER = {"avg": (1.0, 1.0, 0.14), "crab": (1.6, 1.5, 0.10), "crane": (0.8, 0.95, 0.08)}


def foe_stats(lv, hpx=1.0, atkx=1.0, vs="avg"):
    pc = player_curve(lv)
    dhp, ddef, share = DEFENDER[vs]
    hit_taken = 1.5 * pc["PATK"]
    return {"MAXHP": int(round(hpx * 2.2 * hit_taken)),
            "PATK": int(round((share * dhp * pc["HP"] * atkx + ddef * pc["PDEF"]) / 2.1)),
            "PDEF": int(round(0.6 * pc["PATK"])), "MDEF": int(round(0.55 * pc["PATK"])),
            "AGI": int(round(0.9 * pc["AGI"]))}


TIER_PRICE = {"I": 30, "II": 120, "III": 300, "IV": 600, "V": 1200}
FOOD = {"Crab Meat": 15, "Boar Meat": 25, "Fish Stew": 25, "Eel": 30, "Cucumber": 25, "Hornet Honey": 30}


def bestiary_drops(e, it):
    """Drop / steal for every regular foe from docs/rules/bestiary.md (rows "| Tier | Name | ... | Drop / Steal |").
    Known consumables are reused; food heals a little; everything else becomes a sell-only item (I200+, priced by
    tier). Enemies are matched by name; nezumi (not in the bestiary) drop Rice Balls and carry a Shiny Trinket."""
    import re
    txt = open(os.path.join(HERE, "..", "docs", "rules", "bestiary.md"), encoding="utf-8").read()
    rows = {}
    for m in re.finditer(r"^\| (I{1,3}|IV|V) \| ([^|]+?) \|(?:[^|]*\|){6} ([^|]+?) \|\s*$", txt, re.M):
        tier, name, ds = m.group(1), m.group(2).replace("*", "").strip(), m.group(3)
        name = re.sub(r"\s*\(.*?\)", "", name).strip()
        parts = [re.sub(r"\s*\(.*?\)", "", x).strip() for x in ds.split("/")]
        rows[name] = (tier, parts[0] if parts else "—", parts[1] if len(parts) > 1 else "—")
    by_name = {v["name"]: k for k, v in it.items() if isinstance(v, dict) and "name" in v}
    nxt = [200]

    def item_for(name, tier):
        if not name or name in ("—", "-") or name.lower().startswith("zeni"):
            return None
        if name in by_name:
            return by_name[name]
        iid = "I%03d" % nxt[0]
        nxt[0] += 1
        if name in FOOD:
            x = copy.deepcopy(it["I100"])
            x.update({"name": name, "atkform": str(FOOD[name]), "price": TIER_PRICE[tier] // 2,
                      "desc": "Food. Restores a little HP."})
        else:
            x = copy.deepcopy(it["I000"])
            x.update({"name": name, "desc": "Worth something to a merchant.", "price": TIER_PRICE[tier],
                      "occasion": 0, "itemtype": 0})
        it[iid] = x
        by_name[name] = iid
        return iid
    rows["Nezumi Warrior"] = ("I", "Rice Ball", "Shiny Trinket")
    rows["Goblin in a Hat"] = ("I",) + rows.get("Goblin", ("I", "Goblin Knife", "Shiny Trinket"))[1:]
    done = 0
    for eid, x in e.items():
        if not isinstance(x, dict) or x.get("name") not in rows or eid in ("E106", "E120", "E121", "E190"):
            continue
        tier, drop, steal = rows[x["name"]]
        x["item0"] = {"issteal": False, "itemid": item_for(drop, tier), "rate": 50.0}
        x["item1"] = {"issteal": True, "itemid": item_for(steal, tier), "rate": 100.0}
        done += 1
    for eid in ("E120", "E121", "E190"):                   # Gonta's bout, Ryozo, the training dummy: no loot
        if eid in e:
            e[eid]["item0"]["itemid"] = e[eid]["item1"]["itemid"] = None
    return done


def crab_armor(ar):
    def body(aid, src, name, pdef, price, eqtype=None):
        x = copy.deepcopy(ar[src])
        x.update({"name": name, "PDEF": pdef, "price": price})
        if eqtype:
            x["eqtype"] = eqtype
        ar[aid] = x
    body("A100", "A020", "Travelling Clothes", 8, 80)
    body("A101", "A022", "Ashigaru Lamellar", 14, 220)
    body("A102", "A040", "Jingasa", 3, 60)
    ar["A100"]["desc"] = "Sturdy hemp and a good cloak. Light; no penalty to speed."
    ar["A101"]["desc"] = "Laced iron scales of the Wall's foot soldiers. Heavy but honest."
    ar["A102"]["desc"] = "A lacquered conical hat. Keeps off rain, sun and the occasional arrow."
    body("A103", "A040", "Seppun Guard's Jingasa", 7, 300)
    ar["A103"]["desc"] = "An Imperial guard's hat, polished every day. Ryozo kept it. DEF +4 over a plain jingasa."
    body("A104", "A055", "Squeak's Charm", 0, 0)
    ar["A104"]["desc"] = "A knot of string, a bead and a whisker. Squeak says it finds things. It does."
    body("A107", "A055", "Torn Veil", 1, 60)
    ar["A107"]["desc"] = "A strip of the puppet's veil. Somehow you dodge women better. (A joke item.)"
    body("A108", "A027", "Crab Plate", 32, 900)
    body("A110", "A041", "Kabuto", 6, 360)
    ar["A110"]["desc"] = "A ridged iron helmet with a neck guard. Def +6."
    body("A111", "A021", "Shugenja's Haori", 10, 520)
    ar["A111"]["desc"] = "A priest's over-robe, ofuda sewn into the lining. E.Def and SP up."
    ar["A108"]["desc"] = "Heavy laced plate of the Hida. Built for the Wall, not for court."
    body("A109", "A025", "Lacquered Do-maru", 20, 700)
    ar["A109"]["desc"] = "O-Shito's spare: black lacquer, purple cords. Light for its strength."
    body("A106", "A055", "Old Jade Bead", 1, 200)
    ar["A106"]["desc"] = "A Wall veteran's jade bead, worn smooth. Taint finds it harder to take hold."
    body("A105", "A055", "Nezumi Bone Charm", 2, 120)
    body("A112", "A027", "Hida Heavy Plate", 46, 1600)
    ar["A112"]["desc"] = "The Hida's thickest laced plate. A Wall in a suit."
    body("A113", "A041", "Hiruma Scout's Jingasa", 9, 0)
    ar["A113"]["desc"] = "A fallen scout's hat, lined with jade grit. Taint takes hold half as often."
    body("A115", "A055", "Jade Finger", 2, 1500)
    ar["A115"]["desc"] = "A finger of carved jade on a cord, the Crab's old ward. Its wearer can't be Tainted."
    body("A116", "A027", "Kaiu Lamellar", 60, 2600)
    ar["A116"]["desc"] = "Kaiu-forged scales laced in Hida blue. The Wall's best, sold to its best."
    body("A114", "A055", "Kommei Mask", 4, 0)
    ar["A114"]["desc"] = "The oni's second face, dried. Whoever wears it can't be swapped with anyone."
    body("A117", "A055", "Yasurugi's Spare Hilt-wrap", 1, 0)              # Crane Ch1 boss steal (+critical)
    ar["A117"]["desc"] = "Silk hilt-wrap, wound tight and never used. Critical hits come a little easier."
    body("A118", "A055", "Daidoji War Fan", 3, 0)                         # Crane Ch2: all three generals freed
    ar["A118"]["desc"] = "An iron war fan, dropped by a general who woke up. Def +3; a Daidoji's guard."
    ar["A117"].setdefault("option", []).append({"LV": 1, "opttype": "opt_status", "propid": "CRI", "val": 10,
                                                "valtype": "supply"})
    ar["A105"]["desc"] = "The shaman's rattle of tiny bones. It still clicks when something is hidden nearby."
    # Crane Ch3 "The White Squid"
    def opt(aid, **o):
        ar[aid].setdefault("option", []).append(dict({"LV": 1}, **o))
    body("A119", "A055", "Asahina Ward-paper", 1, 0)
    ar["A119"]["desc"] = "Sun-script on mulberry paper, from the Temples of the Sun. False charms on nearby enemies " \
                         "work at half strength."
    body("A120", "A025", "Scorpion Silk Armour", 34, 1500)
    ar["A120"]["desc"] = "Imported: lacquered plates sewn onto heavy silk. Light, and nearly as good as steel."
    body("A121", "A055", "Chihaya's Charm", 1, 0)
    ar["A121"]["desc"] = "A pirate charm, false and Bloodspeaker-made. It works anyway. (Evasion +10)"
    opt("A121", opttype="opt_status", propid="PEVA", val=10, valtype="supply")
    body("A122", "A055", "White Squid Pearl", 3, 0)
    ar["A122"]["desc"] = "From the deep pool under Katsuo's shrine. Cold, and it hums. (Water damage halved)"
    opt("A122", opttype="opt_elemdef", **{"EDR.%d" % ELEMS.index("Water"): 50})
    body("A123", "A055", "Blood-ink Brush", 0, 0)
    ar["A123"]["desc"] = "Katsuo's brush. The bristles are stiff and brown. (E.Atk +15%)"
    opt("A123", opttype="opt_status", propid="MATK", val=15, valtype="totalrate")
    body("A124", "A021", "Asahina Robes", 22, 1300)
    ar["A124"]["desc"] = "White and gold temple robes, ofuda in the hems. E.Def and SP up."
    body("A125", "A055", "Sailor's Oilskin", 2, 600)
    ar["A125"]["desc"] = "A ship's master's oiled cape. The sea gets in less. (Water damage -25%)"
    opt("A125", opttype="opt_elemdef", **{"EDR.%d" % ELEMS.index("Water"): 25})
    # Crane Ch4 (storyboard: Kyuden Doji is the T4 / expensive-accessory hub)
    body("A126", "A055", "Father's Hilt-wrap", 2, 0)
    ar["A126"]["desc"] = "New white silk, wound by someone who knows how. There was no note. (Critical +15)"
    opt("A126", opttype="opt_status", propid="CRI", val=15, valtype="supply")
    body("A127", "A025", "Shadow Cloth", 44, 2600)
    ar["A127"]["desc"] = "Dark silk over thin lacquered plates. A courtier's armour that looks like a robe."
    body("A128", "A021", "Elemental Master's Mantle", 30, 0)
    ar["A128"]["desc"] = "A shugenja's mantle, misfiled in the sealed stacks. E.Def and SP up."
    body("A129", "A055", "Hiruto's Go Stones", 1, 0)                     # Lion Ch1 reward (production: +1 Command use;
    ar["A129"]["desc"] = "Lord Hiruto's own go stones, worn smooth. The black ones. You see the whole board. (Speed " \
                         "+10%)"                                         # Command is unlimited here, so: speed)
    opt("A129", opttype="opt_status", propid="AGI", val=10, valtype="totalrate")
    # Lion Ch2 (Shiro Akodo's festival prizes)
    body("A130", "A055", "Akodo's Leadership", 1, 0)
    ar["A130"]["desc"] = "An illuminated copy of Akodo's Leadership, the debate's prize. (ATK +6%, Critical +5)"
    opt("A130", opttype="opt_status", propid="PATK", val=6, valtype="totalrate")
    opt("A130", opttype="opt_status", propid="CRI", val=5, valtype="supply")
    body("A131", "A055", "Jade-inlaid War Fans", 3, 0)
    ar["A131"]["desc"] = "The dance contest's prize: war fans with jade in the ribs. Terror finds it hard to take " \
                         "hold of you (60%). (Jade)"
    body("A132", "A055", "Coward's Tooth", 1, 0)
    ar["A132"]["desc"] = "A tooth from Oni no Ianwa's ring of teeth. Running away is easier with it. (Speed +8%)"
    opt("A132", opttype="opt_status", propid="AGI", val=8, valtype="totalrate")
    body("A133", "A055", "Strategist's Eye", 1, 0)                       # Lion Ch3 route A: Shogen's teaching
    ar["A133"]["desc"] = "Shogen's teaching, folded into a go-stone pouch: see the board before the stones fall. " \
                         "(Speed +8%, Critical +8)"
    opt("A133", opttype="opt_status", propid="AGI", val=8, valtype="totalrate")
    opt("A133", opttype="opt_status", propid="CRI", val=8, valtype="supply")
    body("A134", "A055", "Demon's Shadow", 1, 0)                         # Lion Ch4: stolen from Rokuro's demon
    ar["A134"]["desc"] = "A scrap of the Fear-demon's shadow, caught in a cord. Its wearer can't be Terrified. It " \
                         "drinks a little of you in return. (Terror immunity; max HP -10%)"
    opt("A134", opttype="opt_status", propid="MAXHP", val=-10, valtype="totalrate")
    body("A135", "A116", "Matsu Lamellar", 64, 2800)
    body("A139", "A055", "Orochi Scale", 3, 0)
    body("A140", "A021", "Isawa Robe", 24, 0)                           # Dragon Ch3: the Shiba storeroom
    ar["A140"]["desc"] = "An Isawa robe from Shiba Katsutoshi's storeroom, the kind the page Sanro will grow into. " \
        "(SP +15)"
    opt("A140", opttype="opt_status", propid="MAXMP", val=15, valtype="supply")
    body("A141", "A025", "Antique Do-maru", 36, 1800)                   # Dragon Ch3: year-400 T3
    body("A142", "A055", "Pressed Cherry Blossom", 2, 0)                # Dragon Ch4 reward (equipment.md)
    ar["A142"]["desc"] = "A cherry blossom from the year 400, pressed in Gendo's notebook. It shouldn't exist. (ATK, " \
        "Magic +5%)"
    opt("A142", opttype="opt_status", propid="PATK", val=5, valtype="totalrate")
    opt("A142", opttype="opt_status", propid="MATK", val=5, valtype="totalrate")
    body("A143", "A055", "Seikidera's Hachimaki", 2, 0)                 # Dragon Ch4: the Champion's chest
    ar["A143"]["desc"] = "Doji Seikidera's headband, from the Champion's chest. It still smells of incense. " \
        "(Critical +10%)"
    opt("A143", opttype="opt_status", propid="CRI", val=10, valtype="supply")
    body("A144", "A055", "Fox Charm", 2, 0)                             # Scorpion Ch1: the Kitsune charm in the mud
    ar["A144"]["desc"] = "A Kitsune charm-box left in the river mud when the oni dissolved. Fox magic turns aside " \
        "the unseen. (Magic DEF +15%)"
    opt("A144", opttype="opt_status", propid="MDEF", val=15, valtype="totalrate")
    # Scorpion Ch2: the City of Masks. The citizens only answer the masked; each mask's material matters (research
    # Appendix A). Worn in the city they drain SP (plugin RokuganField MASK_MAPS); a district shrine takes them off.
    for aid, name, desc, prop, val in (
            ("A145", "Iron Mask", "Kaiu Naname's mask, beaten from a hot sheet while you waited. Metal: wood fears "
                                  "it, fire melts it.", "PDEF", 10),
            ("A146", "Cedar Mask", "Ichiro Itami's carving, light and fragrant. Wood: earth fears it, metal cuts it.",
             "PATK", 6),
            ("A147", "Ink Mask", "Togashi Sumi's tattoo-ink mask, painted on and lacquered. Water: fire fears it, "
                                 "earth drinks it. It washes off. Mostly.", "MDEF", 10),
            ("A148", "Silk Mask", "Bayushi Shiruko's silk, soft as breath. Stone fears it. It fears nothing but "
                                  "stone.", "AGI", 8),
            ("A149", "Jade Mask", "Yasuki Kasamashi's own mask, carved from one piece of real jade. \"That's why I "
                                  "still remember my name.\" (Taint resist)", "MDEF", 15),
            ("A150", "Giseiki's Mask", "Red and black, warm like skin. Soshi Giseiki is inside it, apologising.",
             "MATK", 15),
            ("A151", "Munashii's Mask", "The abbot's plain wooden mask, worn smooth. No more having to choose who. "
                                       "(It remembers your courage.)", "PATK", 10)):
        body(aid, "A055", name, 1, 0)
        ar[aid]["desc"] = desc
        opt(aid, opttype="opt_status", propid=prop, val=val, valtype="totalrate")
    # Unicorn Ch3: the mine guardian's lantern (bosses.md steal: "Guardian's Lantern (Fire accessory)")
    body("A156", "A055", "Guardian's Lantern", 1, 0)
    ar["A156"]["desc"] = "An iron mine-lantern three hundred years old. Its flame never goes out. (Fire resist 30%)"
    opt("A156", opttype="opt_elemdef", **{"EDR.%d" % ELEMS.index("Fire"): 30})
    # Ronin Ch1 (bosses.md: b_tengu_bridge drop Tengu Feather (+Speed), b_boss_tomie_cho drop Tiger's Fang (+crit))
    body("A161", "A055", "Tengu Feather", 1, 0)
    ar["A161"]["desc"] = "A long black feather, dropped by a sulking crow-tengu. It still wants to be somewhere else. " \
                         "(Speed +8)"
    opt("A161", opttype="opt_status", propid="AGI", val=8, valtype="supply")
    body("A163", "A055", "Bloodstone Shard", 1, 0)                 # Ronin Ch3 (bosses.md drop; equipment.md Void,
    ar["A163"]["desc"] = "A red stone from the broken basin, gone grey and cold. It remembers what it was made " \
                         "of. (Its wearer starts every battle with 1 more VP)"           # +1 VP: plugin RokuganBattle
    body("A164", "A055", "Ember Charm", 1, 0)                     # Ronin Ch4 (equipment.md: once per battle, a small
    ar["A164"]["desc"] = "An ember from the crater, caught in a twist of iron. It won't make you anything. It'll just "                          "keep you warm. (Once a battle: Spark, a small Fire hit, or Rekindle, a small revive)"   # Fire
    opt("A164", opttype="opt_getskill", skillid="S615")           # hit or a revive; user rule: modest. The two share
    opt("A164", opttype="opt_getskill", skillid="S616")           # one use: plugin rt_usekey)
    body("A165", "A055", "Naga Pearl", 2, 0)                      # Ronin Ch4 boss drop (equipment.md: Water +)
    ar["A165"]["desc"] = "A pearl the size of a quail's egg, cool as deep water, left on the stair where the champion "                          "coiled aside. (Water damage halved)"
    opt("A165", opttype="opt_elemdef", **{"EDR.%d" % ELEMS.index("Water"): 50})
    body("A169", "A055", "Kumo Silk", 1, 2400)                    # the finale's Shinomen (equipment.md: evasion +)
    ar["A169"]["desc"] = "Grey spider silk, woven fine as smoke by something with too many legs. Things slide off " \
                         "it. (Evasion +12)"
    opt("A169", opttype="opt_status", propid="PEVA", val=12, valtype="supply")
    # the finale: the shrine smith of Osano-Wo (storyboard T: Crab Champion Plate, Robe of the Five Rings; T5)
    body("A166", "A116", "Crab Champion Plate", 84, 4200)
    ar["A166"]["desc"] = "Hida plate with a champion's crest, walked up from the Wall with the jade carts. Heavy " \
                         "enough to stand in a gate with. (T5)"
    body("A167", "A021", "Robe of the Five Rings", 42, 3800)
    ar["A167"]["desc"] = "A shugenja's robe embroidered with the five elements in five threads. The kami like the " \
                         "look of it. (T5; MP +25)"
    opt("A167", opttype="opt_status", propid="MAXMP", val=25, valtype="supply")
    body("A168", "A025", "Thunder-plain Lamellar", 70, 3600)
    ar["A168"]["desc"] = "Light lacquered scales of the Osano-Wo lay guard, made for running along a stockade. (T5)"
    body("A162", "A055", "Tiger's Fang", 1, 0)
    ar["A162"]["desc"] = "A fang the length of a finger, tied with grass. The old woman was very hungry. (Critical +10)"
    opt("A162", opttype="opt_status", propid="CRI", val=10, valtype="supply")
    # Unicorn Ch4 (equipment.md: Persimmon's Saddle, Regret's Silence; storyboard: the wind-ledge Riding Armour T4,
    # a dead officer's Kabuto T4)
    body("A157", "A055", "Persimmon's Saddle", 1, 0)
    ar["A157"]["desc"] = "A refugee grandmother's gift: the saddle Persimmon will tolerate. Tamotsu rides lighter. (Speed " \
                         "+12)"
    opt("A157", opttype="opt_status", propid="AGI", val=12, valtype="supply")
    body("A158", "A055", "Regret's Silence", 1, 0)
    ar["A158"]["desc"] = "A shard of the stillness the Shuten Doji left behind. Nothing can make its wearer silent, or " \
                         "make them someone else. (Immune to Silence and possession)"
    body("A159", "A025", "Unicorn Lamellar", 52, 3200)
    ar["A159"]["desc"] = "Riding armour, lacquered purple, cut for the saddle. Unicorn T4."
    body("A160", "A055", "Legion Kabuto", 1, 0)
    ar["A160"]["desc"] = "An Emerald Legion officer's helmet, green-laced. Its owner won't need it. (DEF +10%)"
    opt("A160", opttype="opt_status", propid="PDEF", val=10, valtype="totalrate")
    # Unicorn Ch1 (storyboard: the Unicorn trader, T1)
    body("A155", "A025", "Unicorn Riding Armour", 12, 320)
    ar["A155"]["desc"] = "Lacquered leather in Unicorn purple, cut for the saddle. Light; it doesn't slow you down."
    # Scorpion Ch4 "The Eve" (storyboard: the town's heat-ward C; the Furnace's lava-step c*; bosses.md steal)
    body("A152", "A055", "Tamori Heat-Ward", 2, 1800)
    ar["A152"]["desc"] = "A Tamori ward-paper sewn into a cord of red hemp. Its wearer walks Tamori's Furnace without " \
                         "burning. (No heat damage; Fire damage taken -50%)"
    opt("A152", opttype="opt_elemdef", **{"EDR.%d" % ELEMS.index("Fire"): 50})
    body("A153", "A025", "Tamori Ward-Robe", 52, 0)
    ar["A153"]["desc"] = "A Tamori monk's heavy robe, ward-script in every seam, left on a ledge over the lava. " \
                         "(No heat damage; Fire damage taken -25%)"
    opt("A153", opttype="opt_elemdef", **{"EDR.%d" % ELEMS.index("Fire"): 25})
    body("A154", "A055", "Bloodspeaker's Mirror", 1, 0)
    ar["A154"]["desc"] = "A hand mirror of black glass. Whatever face looks into it, it shows Mitsue's. (E.Def +12%)"
    opt("A154", opttype="opt_status", propid="MDEF", val=12, valtype="totalrate")                          # Phoenix Ch4: the drowned sailor's box
    ar["A139"]["desc"] = "A sea-serpent's scale from a drowned sailor's box. Water gathers to it. (Water: Magic +10%, " \
                         "Water damage taken -50%)"
    opt("A139", opttype="opt_status", propid="MATK", val=10, valtype="totalrate")
    opt("A139", opttype="opt_elemdef", **{"EDR.%d" % ELEMS.index("Water"): 50})
    body("A137", "A055", "Mountain's-Feet Charm", 2, 900)               # Phoenix Ch3: the Off-Balance counter
    ar["A137"]["desc"] = "An Earth charm of mountain stone, for pilgrims on steep roads. Its wearer can't be knocked " \
                         "Off-Balance. (Oni no Kuzushi's Unbalancing Breath)"
    body("A138", "A055", "Cracked Seal Shard", 2, 0)                    # b_boss_oni_no_kuzushi drop (bosses.md)
    ar["A138"]["desc"] = "A shard of the cellar's jade seal, whole again in Haruki's hand. (Earth: Defence +10%)"
    opt("A138", opttype="opt_status", propid="PDEF", val=10, valtype="totalrate")
    body("A136", "A055", "Hurricane Bead", 2, 0)                          # b_ashimoshi drop (bosses.md: Air)
    ar["A136"]["desc"] = "A bead of grey glass from the silent hurricane. The wind still turns inside it. (Air: " \
                         "Speed +8%, Air damage taken -25%)"
    opt("A136", opttype="opt_status", propid="AGI", val=8, valtype="totalrate")
    opt("A136", opttype="opt_elemdef", **{"EDR.%d" % ELEMS.index("Air"): 25})
    # Head items you can see (tools/gen_sprites2d look_variant + plugin RokuganLook.sk): rt_look = the drawn hat
    body("A170", "A040", "Straw Kasa", 2, 40)
    ar["A170"]["desc"] = "A wide sandogasa of woven straw. Pilgrims, peddlers and ronin hide under it from sun and rain."
    body("A171", "A040", "Eboshi", 1, 160)
    ar["A171"]["desc"] = "A courtier's tall black lacquered cap. Nobody hits a man in an eboshi first. (E.Def +5%)"
    opt("A171", opttype="opt_status", propid="MDEF", val=5, valtype="totalrate")
    body("A172", "A040", "Hachimaki", 1, 50)
    ar["A172"]["desc"] = "A plain white headband, tied tight before a hard day. (Critical +3)"
    opt("A172", opttype="opt_status", propid="CRI", val=3, valtype="supply")
    for aid, look in (("A102", "jingasa"), ("A103", "jingasa"), ("A113", "jingasa"), ("A110", "kabuto"),
                      ("A170", "jingasa"), ("A171", "eboshi")):   # (user) similar hats share a sheet; the Hachimaki is not drawn
        ar[aid]["rt_look"] = look


def crab_stores(st):
    def store(rid, name, items):
        st[rid] = {"desc": "", "icon": "", "name": name, "type": 0,
                   "items": [{"dataid": d, "price": None, "reqfail": 0, "reqs": None} for d in items]}
    store("R100", "Garrison Armoury", ["W101", "W103", "A100", "A101", "A102"])
    store("R101", "Jade Store", ["I100", "I018", "I104"])
    store("R102", "Hoshi-no-Ichi Arms", ["W100", "W101", "W102", "W104", "W105", "A100", "A102"])
    store("R103", "Hoshi-no-Ichi Goods", ["I100", "I018", "I103", "I102"])
    store("R110", "Kaiu Forge", ["W110", "W111", "W112", "W113", "W114", "W115", "W116", "W117"])
    store("R111", "Hida Armoury", ["A108", "A109", "A110", "A111", "A101", "A102"])
    store("R112", "Jade Merchant", ["I104", "I101", "I126", "I127", "I018", "I103"])
    store("R118", "Yasuki Market (Crab T2)", ["W113", "W111", "A108", "A110", "I104", "I101"])
    # Crane Ch3 (storyboard crane-ch3): the Crane port, the ship's master, the Asahina charm-house
    store("R119", "Crane Port Armoury (Crane T3)", ["W121", "W131", "W132", "A120", "A110"])
    store("R120", "Crane Port Chandler", ["I131", "I125", "I126", "I018", "I101"])
    store("R121", "Ship's Master (sea gear)", ["A125", "I237", "I131", "I125", "I101"])
    store("R122", "Asahina Charm-house", ["A124", "I146", "I130", "I126", "I127"])
    # Crane Ch4 (Kyuden Doji, T4): the silk house, the Kakita sword gallery, the apothecary (Oni Ichor: Fire, the
    # told-and-buyable counter to the archives' paper-spirits)
    store("R123", "Doji Silk House (Crane T4)", ["A127", "A124", "A110", "A125"])
    store("R124", "Kakita Sword Gallery (Crane T4)", ["W134", "W133", "W135", "W131"])
    store("R125", "Kyuden Doji Apothecary", ["I131", "I125", "I136", "I130", "I127", "I018"])
    # Lion Ch1 (Hiruto's castle town, Lion T1): spears for the Lion duelists (weak Yari)
    store("R126", "Lord Hiruto's Armoury (Lion T1)", ["W101", "W100", "A101", "A102", "A100"])
    store("R127", "Rice Merchant", ["I100", "I018", "I101", "I102"])
    store("R128", "Kamatori Temple-smith (Phoenix T1)", ["W105", "A100", "A111", "I100", "I168", "I018", "I101"])
    # Lion Ch2 (Shiro Akodo, Lion T2; Calming Tea = the Terror cure for S06 and the boss)
    store("R129", "Shiro Akodo Armoury (Lion T2)", ["W111", "W110", "A108", "A110", "A109"])
    store("R130", "Shiro Akodo Apothecary", ["I101", "I127", "I131", "I018", "I100"])
    store("R131", "Refugee Market", ["I100", "I101", "I131", "I127"])
    store("R132", "Lion Camp Quartermaster (Lion T4)", ["W138", "W134", "W126", "A135", "A110"])
    store("R133", "Camp Sutler", ["I127", "I104", "I131", "I130", "I125"])
    store("R134", "Zumiki Village Store (Phoenix T2)", ["A111", "W115", "I101", "I168", "I127"])
    store("R135", "Treaty City Market (Lion + Phoenix T2)", ["W111", "A111", "A110", "I126", "I168", "I101"])
    store("R136", "Kyuden Isawa Temple-smith (Phoenix T3)", ["A137", "W115", "A111", "I131", "I018", "I168"])
    store("R137", "Coast Outfitter (Phoenix T4)", ["A128", "W115", "W123", "A137", "I131", "I168"])
    store("R138", "Silk Chandler (Mantis isles T1)", ["W104", "W105", "A100", "A102", "I100", "I101", "I018"])
    store("R139", "Tortoise Net Shop (Mantis T2)", ["W111", "W114", "W115", "A109", "I101", "I126", "I168"])
    store("R142", "War Camp Quartermaster (year 400, T4)", ["W134", "W131", "W143", "A135", "A127", "I190", "I168"])
    store("R143", "Kitsuki Outfitter (Dragon T4)", ["W159", "W144", "W115", "A124", "A111", "I126", "I190", "I168"])
    store("R144", "Kyuden Bayushi Outfitter (Scorpion T1)", ["W102", "W104", "W112", "A100", "A102", "I198"])
    store("R145", "Kyuden Bayushi Apothecary", ["I018", "I101", "I100", "I198"])
    store("R146", "Shutai General Store", ["I100", "I101", "I018", "W101", "A101"])
    store("R147", "Kudo Fishmonger", ["I102", "I100", "I101", "I018"])
    store("R148", "Kudo Inari Shrine", ["I199", "I130", "I131", "I018"])
    store("R149", "Hisatu Kensu Unicorn Trader (Unicorn T2)", ["W114", "W111", "A109", "A101", "I101", "I168"])
    store("R150", "The Sweet Cup's Back Room (Osuko's hunters)", ["I197", "I400", "I198", "I168"])
    store("R151", "Akodo Tadoshi's Weapons (the Crab forge)", ["W137", "W114", "W110", "A120", "A109"])
    store("R152", "Buried Leaves Scorpion Trader (Scorpion T3)", ["W140", "W133", "A120", "A127", "I198", "I168"])
    store("R153", "Buried Leaves Unicorn Trader (Unicorn T3)", ["W132", "W121", "A141", "I101", "I131", "I190"])
    # Scorpion Ch4: the Dragon mountain town (Dragon T4; storyboard "Togashi outfitter W/A", "incense-seller S")
    store("R154", "Togashi Outfitter (Dragon T4)", ["W159", "W147", "W144", "W137", "A152", "A124", "A127"])
    store("R155", "Incense-seller", ["I126", "I168", "I127", "I131", "I130", "I101"])
    # Unicorn Ch1: the Town of Buried Leaves in autumn (Unicorn T1) and the camps' rice merchant
    store("R156", "Buried Leaves Unicorn Trader (Unicorn T1)", ["W104", "W101", "A100", "A155", "I100", "I101"])
    store("R157", "Rice Merchant (triple prices)", ["I100", "I101", "I018"])
    # Unicorn Ch3: the Mirumoto war-camp's quartermaster (storyboard: Dragon T3, jade T3)
    store("R158", "Mirumoto Quartermaster (Dragon T3)", ["W159", "W121", "W123", "W137", "W115", "A141", "I131", "I104",
                                                         "I127"])
    # Unicorn Ch4: the siege camp (storyboard: Unicorn + Dragon T4) and, after the chapter, the Jade Toll (production
    # S05: mirumoto_terms jade -> jade-variant prices +25% in the valley shops)
    # Ronin Ch1: Cakon (storyboard: Crane T1; the herb seller has Remedy bases and catalysts)
    store("R161", "Cakon Herb Seller (Remedy)", ["I418", "I419", "I420", "I421", "I422", "I423", "I100", "I018"])
    store("R162", "Cakon Crane Armoury (Crane T1)", ["W100", "W104", "A100", "A102", "A101"])
    store("R163", "Cakon Chandler", ["I100", "I101", "I018", "I103", "I421"])
    # Ronin Ch2: Floating Flowers (storyboard T2: Lacquered Yari, Rattan Yumi, Herbal Salve, Antidote; the Yasuki goods:
    # Remedy catalysts, Snow-Lotus, Wild Honey for Oyuki's cough). Kanemori's Discount (G1082, the sub-story): every
    # line is listed twice, at full price without the discount and at 90% with it (reqfail 0 = the other is hidden).
    live = {k[0].upper(): json.load(open(os.path.join(DATA, k + ".json"), encoding="utf-8"))   # this build's prices
            for k in ("item", "weapon", "armor")}                         # (items and armour are saved by now)

    def disc_store(rid, name, items, f="G1082"):
        rows = []
        for d in items:
            src = live[d[0]][d]
            rows.append({"dataid": d, "price": None, "reqfail": 0,
                         "reqs": [{"lvar": f, "op": "==", "rvar": False}]})
            rows.append({"dataid": d, "price": max(1, int(src["price"] * 0.9)), "reqfail": 0,
                         "reqs": [{"lvar": f, "op": "==", "rvar": True}]})
        st[rid] = {"desc": "", "icon": "", "name": name, "type": 0, "items": rows}
    disc_store("R164", "Floating Flowers Market (T2)", ["W111", "W114", "W100", "A109", "A101", "I101", "I018", "I100"])
    store("R166", "Wounded Lion Outfitter (Lion T3, climbing gear)", ["W134", "W115", "W144", "A141", "A135", "A137",
                                                                       "I131", "I104", "I018"])
    store("R167", "Old Mosuke's Rice Cakes", ["I439"])
    # Ronin Ch4: the Oracle's shrine town (storyboard T: the temple outfitter W/A/S, T4 + Jade; the pilgrim herb stall
    # for Sayo's Remedy - the well's brew is Rhubarb + Moxa)
    # The finale: the shrine smith of Osano-Wo (storyboard T: T5 W/A) and the pilgrim hall's stores (jade, remedies)
    store("R170", "Shrine Smith of Osano-Wo (T5)", ["W160", "W151", "W156", "W152", "W154", "W155", "A166", "A167", "A168",
                                                     "A159"])
    store("R171", "Pilgrim Hall Stores (jade)", ["I130", "I190", "I131", "I104", "I018"])
    store("R168", "Crater Temple Outfitter (T4, jade)",["W147", "W134", "W138", "W135", "W144", "A152", "A127",
                                                          "A141", "I190", "I131", "I104", "I018"])
    store("R169", "Pilgrim Herb Stall (Remedy)", ["I418", "I419", "I420", "I421", "I422", "I423", "I429", "I101"])
    disc_store("R165", "Kanemori's Yasuki Goods", ["I418", "I419", "I420", "I421", "I422", "I423", "I429", "I436"])
    store("R159", "Siege Camp Quartermaster (Unicorn + Dragon T4)", ["W135", "A159", "W144", "W128", "I415", "I131",
                                                                     "I190", "I104"])
    store("R160", "Mirumoto Quartermaster (Dragon T3; the Jade Toll)", ["W121", "W123", "W137", "W115", "A141", "I131",
                                                                         "I104", "I127"])
    for it_ in st["R160"]["items"]:
        if it_["dataid"] in ("W123", "W137", "I104"):
            it_["price"] = {"W123": 950, "W137": 875, "I104": 100}[it_["dataid"]]
    store("R141", "Year-400 Armourer (T3)", ["W143", "W140", "A141", "W132", "I190", "I101", "I168"])
    store("R140", "Antique Market (the year 400)", ["W139", "W111", "W115", "A109", "I101", "I126", "I168"])
    store("R116", "Daidoji Armoury (Crane T2)", ["W110", "W102", "A109", "A110", "W114"])
    store("R117", "Garden Under Shadow Fish Market", ["I101", "I125", "I131", "I126", "I018"])
    store("R115", "Pleasant Eaves Peddler (Lion goods)", ["W101", "W100", "W102", "A101", "I100", "I018"])
    store("R114", "Kyuden Hida Arms (T4)", ["W158", "W127", "W128", "W125", "W126", "A116", "A115", "I130", "I131", "I104"])
    store("R113", "Wall Quartermaster (T3)", ["A115", "I130", "W120", "W122", "W123", "A112", "I131", "I104", "I128"])
    for rid, extra in (("R102", ["A170"]), ("R162", ["A170"]), ("R156", ["A170"]), ("R138", ["A170"]),
                       ("R100", ["A172"]), ("R126", ["A172"]), ("R128", ["A172"]),
                       ("R123", ["A171"]), ("R144", ["A171"])):          # the head items you can see
        st[rid]["items"] += [{"dataid": d, "price": None, "reqfail": 0, "reqs": None} for d in extra]


MACRO_TEXT = [  # (macro id, path in the macro, English line)
    ("X004", "cmdblock.0.cmdblocks.1.0.text", "Couldn't get away!"),
    ("X013", "cmdblock.3.text", "Welcome, welcome! Take a look - honest goods at honest prices."),
    ("X013", "cmdblock.6.text", "Come again! May the Fortunes smile on your road."),
    ("X014", "cmdblock.3.text", "Welcome, traveler. A night's rest is [b]$W$T.money[n]. Will you stay?"),
    ("X014", "cmdblock.4.cmdblocks.0.1.text", "Then rest well. The bath is hot and the futon is clean."),
    ("X014", "cmdblock.4.cmdblocks.0.15.text", "Good morning! Safe travels - and do come back."),
    ("X015", "cmdblock.1.text", "Next, please.\nNow then, let me have a look at you."),
    ("X015", "cmdblock.5.cmdblocks.0.0.text", "Nothing wrong with you that I can see.\nTake care of yourself."),
    ("X015", "cmdblock.6.text", "That comes to $X $T.money, please."),
    ("X015", "cmdblock.7.cmdblocks.1.0.text", "Don't push yourself too hard."),
    ("X017", "cmdblock.1.text0", "Rest in the tent"),
    ("X017", "cmdblock.1.text1", "Back"),
    ("X017", "cmdblock.16.text", "(You rested well in the tent.)"),
]


def title_update_entry(ev):
    """Title menu (map M000 *autoexec): an "Update / Verify" entry before Exit (user 2026-11-12: "add a new box on
    start screen ... Update ... and verify files (against Git)"). It calls ::Rokugan.updateMenu (RokuganUpdate.sk)."""
    cb = ev["page"][0]["cmdblock"]
    if any("m5" in str(c.get("rvar", "")) for c in cb):
        return
    i = next(k for k, c in enumerate(cb) if c.get("cmd") == "cmd_arrayop" and '"m4"' in str(c.get("rvar", "")))
    item = dict(cb[i])
    item["rvar"] = '\t({_name="m5",lbl="Update / Verify"})'
    cb.insert(i, item)
    loop = next(c for c in cb if c.get("cmd") == "cmd_loop")
    handlers = next(c for c in loop["cmdblocks"][0] if c.get("cmd") == "cmd_if")["cmdblocks"][0]
    handlers.append({"cmd": "cmd_if", "reqs": [{"key": "varcmp", "lvar": "X", "op": "==", "rvar": "'m5"}], "cmdblocks": [[
        {"ch": 0, "cmd": "cmd_snd", "sndid": "SE001", "vol": 100, "who": 0},
        {"action": "darken", "cmd": "cmd_customui", "idx": 0, "op": "action", "wait": False},
        {"cmd": "cmd_script", "code": "::Rokugan.updateMenu( this);", "desc": "SCRIPT"},
        {"action": "lighten", "cmd": "cmd_customui", "idx": 0, "op": "action", "wait": False},
        {"cmd": "cmd_focusui", "focusto": "m5", "wait": True}]]})


def main():
    # ---- type.json
    t = load("type")
    t["elem"] = [{"icon": "", "name": n} for n in ELEMS]
    # dmgform 7 "Rokugan heal": grows with the caster (MATK) and the target (a share of max HP set by the spell's power),
    # so a heal stays meaningful at every level (user: Path to Inner Peace must scale). pow 48 -> ~16% max HP + MATK.
    while len(t["dmgform"]) < 8:
        t["dmgform"].append({})
    t["dmgform"][7] = {"name": "Rokugan heal", "icon": "",
                       "formula": "atk:@() src.MATK*1.2+pow+dst.MAXHP*pow/300.0\ndef:@() 0\neva:@() 1.0"}
    save("type", t)

    # ---- cond.json
    c = load("cond")
    suki = copy.deepcopy(c["K002"])
    suki.update({
        "name": "Suki", "desc": "Off balance: loses its actions and takes extra damage until its Resolve returns.",
        "option": [], "uncommandable": True, "rem_turn": [2, 2], "rem_battle": True, "rem_die": True,
        "showpop": True, "showstat": True, "resistg": 0, "efx_start": "FX005",
    })
    c["K030"] = suki
    vg = copy.deepcopy(c["K022"])                    # Daidoji Sakura's Blank Scroll (story/04 B3 #9: Void guard)
    vg.update({"name": "Void Guard", "desc": "A blank scroll held up against the kami: E.DEF up.", "revcondid": None,
               "option": [dict(o, propid="MDEF") for o in vg["option"]]})
    c["K024"] = vg
    sc_ = copy.deepcopy(suki)                         # Ide Fujio's Scandalous Letter (B3 #8: enemy skips a turn)
    sc_.update({"name": "Scandalized", "desc": "Reading a scandalous letter about itself. Too shocked to act.",
                "efx_start": None, "uncommandable": False})   # the plugin skips its actions (uncommandable = confused)
    c["K025"] = sc_
    nt = copy.deepcopy(sc_)                           # Hoshi Fisherman's net (hireable): loses its next actions
    nt.update({"name": "Netted", "desc": "Tangled in a fishing net. It spends its turn getting out.",
               "rem_turn": [1, 1]})
    c["K028"] = nt
    pr = copy.deepcopy(c["K023"])                     # Earth Becomes Sky (5e: Prone): DEF down; the next boulder x2
    pr.update({"name": "Prone", "desc": "Knocked flat by the earth kami: DEF down, and a boulder hits it twice as "
               "hard.", "revcondid": None, "rem_turn": [2, 2], "MAXLV": 1})
    c["K029"] = pr
    tn = copy.deepcopy(c["K001"])                     # Taint: persists after battle like Poison (rules/enemies.md)
    tn.update({"name": "Taint", "MAXLV": 5, "revcondid": None, "rem_turn": [0, 0], "rem_walk": [0, 0],
               "rem_battle": False, "rem_die": False, "showpop": True, "showstat": True, "efx_start": None,
               "desc": "Shadowlands corruption. Max HP -6% per stack (to 5). At 4 stacks the bearer is weak to Jade. "
                       "Cleansed by a Jade Pouch or a shrine.",
               "option": [{"LV": n, "opttype": "opt_status", "propid": "MAXHP", "val": -6, "valtype": "totalrate"}
                          for n in range(1, 6)] + [{"LV": 4, "opttype": "opt_elemdef", "EDR.%d" % ELEMS.index("Jade"):
                                                    -50}]})
    c["K026"] = tn
    mt = copy.deepcopy(c["K022"])                    # Hida Bushi R2 (3e core): RokuganHazard halves hits taken
    mt.update({"name": "The Mountain", "desc": "The Mountain Does Not Move: braced, she takes half damage.",
               "option": [], "revcondid": None, "rem_turn": [3, 3], "MAXLV": 1})
    c["K027"] = mt
    # Crane Ch3 false charms (Katsuo's Bloodspeaker work; plugin RokuganHazard hands them out and shatters them on
    # Suki). Each lasts until broken. The warded halves apply when anyone in the party wears the Asahina Ward-paper.
    for kid, wid, nm, o, half in (
            ("K044", "K047", "Evasion", {"opttype": "opt_status", "propid": "PEVA", "valtype": "supply"}, 30),
            ("K045", "K048", "Fury", {"opttype": "opt_status", "propid": "PATK", "valtype": "totalrate"}, 16)):
        # (Fury is small on purpose: damage is 2.1 x ATK - DEF, so +16% ATK is about +30% damage)
        for cid, v, tag in ((kid, half, ""), (wid, half // 2, " (warded)")):
            x = copy.deepcopy(c["K020"])
            x.update({"name": "Charm: %s%s" % (nm, tag), "MAXLV": 1, "revcondid": None, "rem_turn": [0, 0],
                      "resistg": 0, "desc": "A false White Squid charm. Break the wearer (Suki) to shatter it.",
                      "option": [dict(o, LV=1, val=v)]})
            c[cid] = x
    for cid, v, tag in (("K046", 8, ""), ("K049", 4, " (warded)")):
        x = copy.deepcopy(c["K040"])
        x.update({"name": "Charm: Mending%s" % tag, "MAXLV": 1, "desc": "A false White Squid charm. Break the wearer "
                  "(Suki) to shatter it."})
        x["option"] = [dict(x["option"][0], dmgval=v)]
        c[cid] = x
    sh = copy.deepcopy(c["K028"])                     # a shattered charm stuns: one turn past Suki's two
    sh.update({"name": "Shattered", "desc": "The charm broke, and its wearer's nerve with it. Loses its actions.",
               "rem_turn": [3, 3]})
    c["K050"] = sh
    sl = copy.deepcopy(c["K021"])                     # Umibozu Shade: Wave Wall (bestiary B5: party Speed -)
    sl.update({"name": "Slowed", "desc": "Soaked and battered by the sea. Speed down.", "MAXLV": 1,
               "revcondid": None, "rem_turn": [3, 3],
               "option": [{"LV": 1, "opttype": "opt_status", "propid": "AGI", "val": -30, "valtype": "totalrate"}]})
    c["K051"] = sl
    sk_ = copy.deepcopy(c["K005"])                    # Sea Serpent Eel: Electric Coil. Not K006 Paralysis: that one
    sk_.update({"name": "Shocked", "desc": "The eel's shock. Loses the next turn.", "rem_turn": [1, 1],  # counts as
                "MAXLV": 1})                                                # defeated, so a solo traveler would lose
    c["K052"] = sk_
    fe = copy.deepcopy(c["K020"])                      # Watchful Falcon (kata.md Kakita 2): accuracy, and an eye for
    fe.update({"name": "Watchful Falcon", "desc": "The falcon's eye: accuracy and critical hits up.",  # the opening
               "MAXLV": 1, "revcondid": None, "rem_turn": [3, 3], "resistg": 0,
               "option": [{"LV": 1, "opttype": "opt_status", "propid": "PHIT", "val": 15, "valtype": "supply"},
                          {"LV": 1, "opttype": "opt_status", "propid": "CRI", "val": 15, "valtype": "supply"}]})
    c["K053"] = fe
    dz = copy.deepcopy(c["K004"])                      # Lantern Spirit: Lick. Not K004 Confuse (3-5 turns, brutal solo)
    dz.update({"name": "Dazed", "desc": "Licked by a lantern. Confused for a moment.", "rem_turn": [1, 2]})
    c["K054"] = dz
    bl = copy.deepcopy(c["K001"])                      # Paper-spirit: Paper Cut. Not K001 Poison (10% a turn, forever,
    bl.update({"name": "Bleeding", "desc": "Paper cuts. A little HP lost each turn, for three turns.",  # even after the
               "rem_turn": [3, 3], "rem_battle": True, "revcondid": None})                               # battle)
    bl["option"] = [dict(bl["option"][0], dmgval=5.0)]
    c["K055"] = bl
    c["K007"]["name"] = "Terror"                       # (the plugin: a Terrified traveler may freeze, and can't Boost)
    c["K007"]["desc"] = "Terror: may lose the turn, and can't use Void. Jade gear and courage resist it."
    dt = copy.deepcopy(c["K022"])                      # Moto Benjiro's Death Trance: no fear, no charm (1 round)
    dt.update({"name": "Death Trance", "desc": "A Moto's death-mask calm: immune to Terror and charm.", "option": [],
               "revcondid": None, "rem_turn": [2, 2], "MAXLV": 1})
    c["K056"] = dt
    hw = copy.deepcopy(c["K022"])                      # Scorpion Ch4: Tamori Haku's Heat-Ward (Fire damage halved)
    hw.update({"name": "Heat-Ward", "desc": "A Tamori ward against fire: Fire damage halved.", "revcondid": None,
               "rem_turn": [3, 3], "MAXLV": 1, "option": [{"LV": 1, "opttype": "opt_elemdef", "EDR.6": 50}]})
    c["K057"] = hw
    cg = copy.deepcopy(c["K056"])                      # Courage of the Seven Thunders / Stillness of the Void: no
    cg.update({"name": "Courage", "desc": "The heart is still: immune to Terror.", "rem_turn": [4, 4]})   # Terror,
    c["K058"] = cg                                     # 4 turns (the plugin's Terror check, RokuganHazard)
    c["K040"]["MAXLV"] = 1                             # Regen: one stack (recasting Regrow refreshes, doesn't pile up)
    vl = copy.deepcopy(c["K022"])                      # Unicorn Ch4: Tamotsu's R3 When the Veil Moves (the Wail and the
    vl.update({"name": "Veiled", "desc": "Tamotsu saw it coming. The next Wail or song can't take you; DEF up.",  # Hum
               "revcondid": None, "rem_turn": [3, 3], "MAXLV": 1})                                 # pass you by)
    c["K058"] = vl
    wt = copy.deepcopy(c["K022"])                      # Ronin Duelist R1 The Wind Technique: she acts early
    wt.update({"name": "Wind Technique", "desc": "Faster than the current: Speed up.", "revcondid": None,
               "rem_turn": [99, 99], "MAXLV": 1,
               "option": [{"LV": 1, "opttype": "opt_status", "propid": "AGI", "val": 25, "valtype": "totalrate"}]})
    c["K059"] = wt
    sg = copy.deepcopy(c["K022"])                      # Ronin Yojimbo R1 The Way of Sacrifice: her Defend, shared
    sg.update({"name": "Shared Guard", "desc": "Sayo stands in front of you: DEF up for a turn.", "revcondid": None,
               "rem_turn": [1, 1], "MAXLV": 1})
    c["K060"] = sg
    cn = copy.deepcopy(c["K005"])                      # b_tengu_bridge: knocked off the log (like Shocked, two turns)
    cn.update({"name": "In the Canal", "desc": "Knocked off the log, soaked, climbing out. Loses two turns.",
               "rem_turn": [2, 2], "MAXLV": 1})
    c["K061"] = cn
    hb = copy.deepcopy(wt)                             # Ronin Yojimbo R3 Hasten the Blade: after a Defend turn, fast
    hb.update({"name": "Hasten the Blade", "desc": "Out of her guard like a released spring: Speed up for a turn.",
               "rem_turn": [2, 2], "option": [{"LV": 1, "opttype": "opt_status", "propid": "AGI", "val": 60,
                                               "valtype": "totalrate"}]})
    c["K062"] = hb
    for e in _kata.KATA:                               # kata / kiho / tattoo stances K070-K124 (tools/kata_data.py)
        c[e[1]] = _kata.cond_for(e, copy.deepcopy(c["K020"]))
    # Stand Against the Waves (Prayers & Treasures, Water ML 2: one more attack per caster's Insight Rank on the
    # target's next turn, +5 TN to hit -> -10% accuracy); the plugin adds the hits (RokuganRanks.sk)
    sw = copy.deepcopy(c["K020"])
    sw.update({"name": "Stand Against the Waves", "desc": "More attacks on the next turn (one per the caster's Insight "
               "Rank); accuracy -10%.", "MAXLV": 1, "rem_turn": [2, 2], "revcondid": None, "rt_waves": True,
               "option": [{"LV": 1, "opttype": "opt_status", "propid": "PHIT", "val": -10, "valtype": "supply"}]})
    c["K136"] = sw
    # Void-critical party buffs (user 2026-11-12: "when a void spent crit happens have the bust of the char pop up with
    # text ... Hiruma ... 20% avoid for 2 turns, for the Hida ... 75 damage reduction for 2 turns etc."). 2 turns after
    # the one it lands in. rt_dmgtaken: the plugin scales damage taken (RokuganVoidCrit.sk).
    for cid, name, opts, extra in (
            ("K125", "Razor's Edge (party)", [("PEVA", 20, "supply")], {}),
            ("K126", "The Mountain Does Not Fall", [], {"rt_dmgtaken": 0.25}),
            ("K127", "Void Focus (criticals)", [("CRI", 20, "supply")], {}),
            ("K128", "Void Fury (ATK)", [("PATK", 30, "totalrate")], {}),
            ("K129", "Touch of the Void (MDEF)", [("MDEF", 30, "totalrate")], {}),
            ("K130", "The Wind (Speed)", [("AGI", 40, "totalrate")], {}),
            ("K131", "Clear Sight (accuracy)", [("PHIT", 20, "supply")], {})):
        vb = copy.deepcopy(c["K020"])
        vb.update({"name": name, "desc": name + ": a Void critical's gift to the party.", "MAXLV": 1,
                   "rem_turn": [3, 3], "revcondid": None,
                   "option": [{"LV": 1, "opttype": "opt_status", "propid": p_, "val": v_, "valtype": t_}
                              for p_, v_, t_ in opts]})
        vb.update(extra)
        c[cid] = vb
    localise("cond", c)
    save("cond", c)
    dc = load("dict")                                     # term overrides (engine T[] dictionary)
    dc.update({"money": {"en": " zeni", "ja": " zeni"},
               "stealok": {"en": "Stole $v!", "ja": "Stole $v!"},
               "stealfail": {"en": "Couldn't steal anything...", "ja": "Couldn't steal anything..."},
               "noitems": {"en": "Nothing to take!", "ja": "Nothing to take!"}})
    save("dict", dc)
    mc = load("macro")                                    # English for the template's service scripts
    for mid, path, text in MACRO_TEXT:
        node = mc[mid]
        keys = path.replace("]", "").replace("[", ".").split(".")
        for k in keys[:-1]:
            node = node[int(k)] if k.isdigit() else node[k]
        node[keys[-1]] = text
    stay = mc["X014"]["cmdblock"][4]["cmdblocks"][0]      # the inn also rests whoever waits in the finale's Party B
    code = ("foreach( p in ::Rokugan.fReserve()){ p.removeCondition( \"K000\"); p.HP = p.MAXHP; "
            "p.MP = p.MAXMP; }")                          # (the fallen get up too: tester 2026-11-11)
    stay[:] = [c for c in stay if c.get("desc") != "RT reserve rest"]             # (G1160; empty outside the finale)
    stay.append({"cmd": "cmd_script", "desc": "RT reserve rest", "code": code})
    # Flee (X004): the Herbalist's Wave-woman trait (G1226, set by RokuganJobs.sk) skips the 50% roll where fleeing
    # is allowed (jobs_data.py J132)
    fl = mc["X004"]["cmdblock"]
    if not (fl and fl[0].get("desc") == "RT wave-woman"):
        roll = fl.pop(0)
        fl.insert(0, {"cmd": "cmd_if", "desc": "RT wave-woman", "cmdblocks": [[], [roll]],
                      "reqs": [{"key": "varcmp", "lvar": "G1226", "op": "==", "rvar": True},
                               {"key": "varcmp", "lvar": "ESCAPABLE", "op": "==", "rvar": True}]})
    save("macro", mc)
    gv = load("gvar")                                     # story flags (Crab Ch1)
    for gid, nm in (("G010", "S01 watchtower opening done"), ("G011", "S02 leave ordered"),
                    ("G012", "S03 Hoshi-no-Ichi arrival"), ("G013", "S03 drop soup (noodle stall)"),
                    ("G014", "S04 quarry arrival"), ("G015", "hidden_ones_cleared"), ("G016", "quarry_left"),
                    ("G017", "talked_satomi"), ("G018", "S03b Satomi first talk"),
                    ("G021", "S04 resolved (Sumai won or left)"), ("G022", "S05 night theft at the inn"),
                    ("G024", "S05 Squeak at the cave mouth"), ("G025", "S05 P1 prints"), ("G026", "S05 P2 hairpin"),
                    ("G027", "S05 P3 smell"),
                    ("G040", "S06 cave 1 stolen things"), ("G041", "b_cave_nezumi_a won"),
                    ("G042", "b_cave_beetles won"), ("G043", "S06 cave 3 armour"), ("G044", "b_cave_nezumi_b won"),
                    ("G045", "S07 altar scene"), ("G046", "ryo_a"), ("G047", "ryo_b"),
                    ("G048", "ryozo_talked_down"), ("G049", "S08 boss won"), ("G050", "oni_named_ryozo"),
                    ("G051", "nezumi_friends"), ("G052", "seppun_tanto_taken"), ("G053", "S09 done"),
                    ("G054", "S10 chapter complete"), ("G056", "C2 Tremor wall chest"),
                    ("G057", "S06 cave 1 entry"), ("G058", "S06 cave 2 entry"),
                    *[("G%03d" % (30 + i), "Hoshi townsfolk talked: " + n) for i, n in enumerate(TOWNSFOLK)]):
        gv[gid] = {"defval": False, "name": nm, "type": 1}
    gv["G019"] = {"defval": 0, "name": "Hoshi townsfolk talked (count; 3 opens the quarry)", "type": 2}
    gv["G055"] = {"defval": 0, "name": "S07 tries to reach Ryozo (count)", "type": 2}
    gv["G060"] = {"defval": 0, "name": "Honor (story changes, +/-)", "type": 2}
    for gid, nm in (("G200", "Crab Ch2 started (chapter icon)"), ("G201", "S01 audience + flares"),
                    ("G202", "S02 Mutsuye"), ("G203", "S02 Kuhime"), ("G204", "S02 Keiyomi"),
                    ("G205", "S02 archery"), ("G206", "S02 Akiko"), ("G207", "S02 Shiko rumour"),
                    ("G208", "wall_crab_trust"), ("G209", "S02b the dance"), ("G210", "S03 wall_mud_clue"),
                    ("G212", "S05 donjon"), ("G213", "b_donjon_goblins won"), ("G214", "S06 boss won"),
                    ("G215", "puppet_spared"), ("G216", "S07 Crab Ch2 complete"), ("G217", "blue_flare_held"),
                    ("G218", "Squeak's rat-way"), ("G221", "S02 Shigeru & Taira"), ("G222", "S02 Kage"),
                    ("G223", "Wall-stair Crab Plate"), ("G224", "S05 donjon entry scene"),
                    ("G225", "trap catacombs roller"), ("G226", "trap catacombs jade line"),
                    ("G227", "S06 boss scene"), ("G228", "Keiyomi's ribbon returned"), ("G229", "S03 shrine scene"),
                    ("G230", "S04 accusation scene"), ("G231", "Keiyomi gave Natsuko her ribbon"),
                    ("G232", "current guest (0 none, 1 Kitsu Takeo, 2 Yogo Mai, 3 Ide Fujio, 4 Daidoji Sakura)"),
                    ("G233", "SS Takeo 'The Silent Ancestors' done"), ("G234", "SS Mai 'The Sweet Yogo' done"),
                    ("G235", "SS Fujio 'Letters to Everyone' done"), ("G236", "SS Sakura 'The Deserter' done"),
                    # Crab Ch3 "Beyond the Wall" (production/crab-ch3.md)
                    ("G240", "Crab Ch3 started (S01 at the Wall gate)"), ("G241", "S02 trap tunnels' far mouth"),
                    ("G242", "S03 landmark 1 (tar chasm)"), ("G243", "S03 landmark 2 (lava trees)"),
                    ("G244", "S03 b_sl_goblins won"), ("G245", "S03 b_sl_onikage won"),
                    ("G246", "S03 the ridge: map marked"), ("G247", "S04 the broken guard"),
                    ("G248", "guard_rescued"), ("G249", "S05 Kage found (follows)"), ("G250", "S06 the plain"),
                    ("G251", "S06 hide failed (b_sl_akutsukai)"), ("G252", "S06 the Ryozo rider"),
                    ("G253", "kage_fought"), ("G254", "S07 Kommei defeated"), ("G255", "S08 Crab Ch3 complete"),
                    ("G256", "Squeak joined (Ch3)"), ("G257", "Gonta joined (Ch3)"), ("G258", "SL2 scout's bones"),
                    ("G259", "Ch3 point of no return crossed"),
                    ("G260", "S02 the traps (Natsuko's line)"), ("G261", "SL2 hanging root climbed (Fine Katana)"),
                    # Crab Ch4 "The Fairest One of All" (production/crab-ch4.md)
                    ("G270", "Crab Ch4 started"), ("G271", "S01 the wedding"), ("G272", "S02 the siege begins"),
                    ("G273", "b_siege_breach_a won"), ("G274", "b_siege_breach_b fought"), ("G275", "S03 the barrel"),
                    ("G276", "F1 maid passed"), ("G277", "F2 guard passed"), ("G278", "F2 Akiko passed"),
                    ("G279", "nashiko_unmasked"), ("G280", "S05 the chase"), ("G281", "flare_fired"),
                    ("G284", "S06 Tsukakoro defeated"), ("G285", "kage_told_truth"), ("G286", "Crab Ch4 complete"),
                    ("G287", "split up on F1"), ("G288", "split up on F2"), ("G289", "split up on F3"),
                    ("G290", "test made on the current stalk NPC"), ("G292", "Goro SS2 The Bent Sword done"),
                    ("G295", "boar hollow found (Crab Ch1 coast road, Hunting)"),
                    ("G296", "beach ledge climbed (Crab Ch1 coast road, Athletics)"),
                    ("G297", "Hoshi storehouse lacquer box opened"),
                    ("G298", "Toshi no Kijo troll's hoard taken (Crab Ch3)"),
                    # Crane Ch1 "Heaven's Glory" (production/crane-ch1.md; Kakita Rensei)
                    ("G300", "Crane Ch1 started (Rensei chosen as the starter)"), ("G301", "S01 graduation done"),
                    ("G302", "S02 road_west done (Seigen joined)"), ("G303", "S03 Ebisu scene done"),
                    ("G305", "Matsu Kiku joined"), ("G306", "S04 forest: the ghost maiden"),
                    ("G307", "rope R1 cut"), ("G308", "rope R2 cut (the pit revealed)"),
                    ("G309", "rope R3 cut (the ghost maiden)"), ("G310", "b_forest_bandits_a won"),
                    ("G311", "forest_village_spared"), ("G312", "S04 clearing: the death letter"),
                    ("G313", "S05 the Green Ronin's village"), ("G314", "b_forest_bandits_b won"),
                    ("G315", "S06 castle hall"), ("G316", "depura_seen"), ("G317", "seoko_charmed"),
                    ("G318", "tatanko_charmed"), ("G320", "S08 Yasurugi defeated"),
                    ("G321", "Crane Ch1 complete"), ("G322", "waterfall glade found (Ebisu leads)"),
                    ("G323", "boar hollow (road_west, Hunting)"), ("G324", "headman's storehouse box opened"),
                    ("G325", "bruised youth apologised"), ("G326", "old woman follows (Green Ronin's Blessing)"),
                    ("G327", "TB-crane1-a Spilled Tea seen"), ("G328", "fell into the pit chamber"),
                    ("G329", "S07 the dawn choice made"), ("G331", "prologue: starter chosen"),
                    ("G332", "S01 graduation scene started"), ("G333", "S02 road scene started"),
                    ("G334", "road_west: four days of road"), ("G335", "S03 Pleasant Eaves scene started"),
                    ("G336", "a forest bandit was killed (not spared)"), ("G337", "waterfall glade: Morishu's inro"),
                    ("G338", "S04 forest scene started"), ("G339", "S04 clearing scene started"),
                    ("G340", "forest_2 training post: the Kozuka"), ("G341", "S05 village scene started"),
                    ("G343", "S06 castle hall scene"), ("G344", "S06 corridor: Depura"),
                    ("G345", "S08 the boss scene started"),
                    # Crane Ch2 "The Iron Cranes" (production/crane-ch2.md; crossroads with Natsuko / Goro)
                    ("G346", "Crane Ch2 started"), ("G347", "S01 the lantern garden"), ("G348", "tadaka_lie_heard"),
                    ("G349", "eriko_close"), ("G350", "Kakita Yumi charmed (info)"), ("G351", "S02 Yasuki Yashiki"),
                    ("G352", "S03 same method twice"), ("G354", "b_camp_sentries_a won"),
                    ("G355", "b_camp_sentries_b won"), ("G357", "S04 Uji and Yakamo"), ("G358", "S05 the Iron Cranes"),
                    ("G359", "an Iron Crane general was killed (worse epilogue)"), ("G361", "S06 same_woman_proven"),
                    ("G362", "Crane Ch2 complete"), ("G363", "Tide Chart"), ("G364", "land_bridge tide pool"),
                    ("G365", "harbour office box"), ("G366", "Yasuki warehouse"), ("G367", "TB-crossroads1 seen"),
                    ("G368", "Hiruma Goro on the guest roster"), ("G369", "Rensei: Rank 2"),
                    ("G371", "S01 garden intro played"), ("G372", "harbour office box opened"),
                    ("G373", "GS docks chest"), ("G374", "Tadaka scene played"), ("G376", "low tide now"),
                    ("G377", "S02 the land-bridge"), ("G378", "S02 the Yasuki hall"),
                    ("G379", "S03 Sanae's rooms scene"), ("G380", "S04 camp entry"), ("G381", "S05 boss scene"),
                    ("G382", "the Daidoji War Fan picked up"), ("G383", "S06 the six doors"),
                    ("G384", "S07 the ending"),
                    # Crane Ch3 "The White Squid" (production/crane-ch3.md)
                    ("G385", "Crane Ch3 started (S01)"), ("G386", "S01 first sailing"), ("G387", "tessai_ally"),
                    ("G388", "S02 Tessai choice made"), ("G389", "sea: Cove Fort revealed"),
                    ("G390", "S03 Chihaya defeated"), ("G391", "tadanobu_letters"),
                    ("G392", "sea: Temples of the Sun revealed"), ("G393", "S04 the Asahina ward-paper"),
                    ("G394", "sea: the south isles revealed"), ("G395", "S05 Yosuke defeated"),
                    ("G396", "S06 Ryohei met"), ("G397", "ryohei_released"), ("G398", "the Emperor's screen found"),
                    ("G399", "S07 shrine entered"), ("G400", "S08 Katsuo defeated"), ("G401", "katsuo_alive"),
                    ("G402", "S09 the ending"), ("G403", "Crane Ch3 complete"),
                    ("G405", "Shinken's clerk charmed (info)"), ("G406", "Crane port docks chest"),
                    ("G407", "Crane port customs-house crates"), ("G408", "Cove Fort lookout (Athletics)"),
                    ("G409", "S07 the deep water"), ("G410", "shrine: Tessai's chest 1"),
                    ("G411", "shrine: Tessai's chest 2"), ("G412", "Katsuo's paint box"),
                    ("G413", "S05 storm scene played"), ("G414", "S08 boss scene played"),
                    ("G415", "S09 port scene played"),
                    # Crane Ch4 "The Play No One Performs" (production/crane-ch4.md; play_known_scenes = G421, numeric)
                    ("G417", "Crane Ch4 started (S01)"), ("G418", "S02 censor-monk passed"),
                    ("G419", "b_archive_spirits won"), ("G420", "b_archive_guardian won"),
                    ("G422", "Scene 1 read (the Mirror)"), ("G423", "Scene 2 read (the Blade)"),
                    ("G424", "Scene 3 read (the Title + margin note)"), ("G425", "the play found"),
                    ("G426", "S03 rehearsal done"), ("G427", "rehearsal_quality good"), ("G428", "S04 father's answer"),
                    ("G429", "play_handed_over"), ("G430", "S05 the duel fought"), ("G431", "duel_won"),
                    ("G432", "S06 sanae_answer given"), ("G433", "sanae_answer: the Empire"),
                    ("G434", "Crane Ch4 complete"), ("G435", "archives 1 misfiled box"),
                    ("G436", "archives 2 steward's diary"), ("G437", "the night-before save offered"),
                    ("G439", "S06 court scene played"), ("G440", "S04 scene played"),
                    # Lion Ch1 "The Blood of Family" (production/lion-ch1.md)
                    ("G441", "Shizue chosen (Lion path)"), ("G442", "S01 the raid played"), ("G443", "shrine_broken"),
                    ("G444", "S02 the Phoenix arrive"), ("G445", "Haruki recruited (Phoenix traveler)"),
                    ("G446", "S02 scene played"),
                    ("G447", "C1 Hoju's ghost"), ("G448", "C2 the lying ghost"), ("G449", "C3 the real jade"),
                    ("G450", "C4 Ozaki's statue"), ("G451", "C5 Ryuzoji's wound"), ("G452", "C6 Yachiko's cipher"),
                    ("G454", "escalation 2: Crane banners"), ("G455", "escalation 3: Togawa"),
                    ("G456", "Ijako met (guest)"), ("G457", "escalation 4: Nagai + the Ashimita duel"),
                    ("G458", "night (the ghost walks)"), ("G460", "Ozaki dueled"), ("G461", "Gusai dueled"),
                    ("G462", "Ashimita on the guest roster"), ("G463", "five clues"), ("G464", "S03a Ijako scene"),
                    ("G465", "tea house back room"), ("G466", "castle town well"),
                    ("G467", "the road east open (after S05)"), ("G468", "S05 Hojiki's custody decided"),
                    ("G469", "hojiki_custody: phoenix"), ("G470", "S06 the Jade Chains"),
                    ("G471", "compass S1"), ("G472", "compass S2"), ("G473", "compass S3"),
                    ("G474", "compass S4: Ice (the west tower)"), ("G475", "Kamatori: the Shiba guard dueled"),
                    ("G476", "road: Hoju's waystone"), ("G477", "road: river bank (Athletics)"),
                    ("G478", "Kamatori: Hoju's storeroom"), ("G479", "S06 study scene played"),
                    ("G480", "S07 played"), ("G481", "climax_route A (bind)"), ("G482", "climax_route B (duel)"),
                    ("G483", "climax_route C (protect)"), ("G484", "S08 O-Tamai bound"), ("G485", "yachiko_suspected"),
                    ("G486", "Lion Ch1 complete"), ("G487", "S07 scene flag"), ("G488", "S09 scene flag"),
                    # Lion Ch2 "Shadow of a Doubt" (production/lion-ch2.md; painting_answer G492 / bracket G494 /
                    # atsuko_promise G505 are numeric)
                    ("G489", "S01 arrival played"), ("G490", "met_nishi"), ("G491", "Beat 1 done"),
                    ("G493", "escalation 1: the Duty plaque"), ("G495", "Beat 2 done"), ("G496", "heard_history"),
                    ("G497", "escalation 2: the banner"), ("G498", "Beat 3 done"), ("G499", "toturi_knows_name"),
                    ("G500", "the sword clue (swordsmith)"), ("G501", "S06 the South Dojo at night"),
                    ("G502", "b_fear_shades won"), ("G503", "Beat 4 done"), ("G504", "escalation 4: the seal"),
                    ("G506", "S07 Atsuko in the cells"), ("G507", "S08 Benjiro on the guest roster"),
                    ("G508", "kafu_joins"), ("G509", "S09 Ianwa fled"), ("G510", "Lion Ch2 complete"),
                    ("G511", "under-dojo chest 1"), ("G512", "under-dojo chest 2"), ("G513", "S06 voices heard"),
                    ("G514", "S09 scene flag"), ("G515", "S10 scene flag"), ("G516", "winter road bear den"),
                    ("G517", "Nishi's go game"), ("G518", "sake house cellar"),
                    # Lion Ch3 "The Deadly Message" (message_route G527 numeric: 1 deliver, 2 ask the karo)
                    ("G519", "Lion Ch3 started (S01)"), ("G520", "S02 the ford duel won"),
                    ("G521", "S02 the ford crossed"), ("G522", "S02 the inspector"), ("G523", "Ijako joins (Ch3)"),
                    ("G524", "the toll box decided"), ("G525", "S03 the tube cracked"), ("G526", "S03 scene flag"),
                    ("G528", "S05B the karo's answer"), ("G529", "S04 b_pass_ronin won"), ("G530", "yachiko_letters"),
                    ("G531", "S05A Shogen's test"), ("G532", "shogen_joined"), ("G533", "S06 the killers beaten"),
                    ("G534", "duelist_spared"), ("G535", "route B: the hermitage coda"), ("G536", "S07 Toturi"),
                    ("G537", "Lion Ch3 complete"), ("G538", "west road: granary loft"), ("G539", "pass: hunter's "
                    "cache"), ("G540", "pass: frozen courier"), ("G541", "Shogen's plum wine"),
                    ("G542", "S01 scene flag"), ("G543", "S06 scene flag"), ("G544", "S05B scene flag"),
                    ("G545", "S07 scene flag (route A)"), ("G546", "S02 Ijako scene flag"),
                    # Lion Ch4 "Sorrow's Path" (go_between G556 numeric: 1 Rensei, 2 Atsuko, 3 Shizue herself)
                    ("G547", "Lion Ch4 started (S01)"), ("G548", "Old Lion's Counsel (+10% damage)"),
                    ("G549", "the victory stone read (wave 1)"), ("G550", "road: the watchtower yari"),
                    ("G551", "S02 night at the camp"), ("G552", "S02 the courier"), ("G553", "S02 the sentry"),
                    ("G554", "Yachiko's tent"), ("G555", "S02 same method twice"),
                    ("G557", "rensei_recruited (the crossroads; not built)"), ("G558", "S03 the go-between"),
                    ("G559", "gusai_held"), ("G560", "obsidian_blade_taken"), ("G561", "S04 dawn"),
                    ("G562", "wave 1 held"), ("G563", "wave 2 held"), ("G564", "wave 3 held"), ("G565", "wave 4 held"),
                    ("G566", "wave 5 held"), ("G567", "the mist lifts (save)"), ("G568", "S06 Rokuro freed"),
                    ("G569", "report_truth"), ("G570", "three_clan_truce"),
                    ("G571", "phoenix_supply_proof (Phoenix Ch1; not built)"), ("G572", "the courtier's tent"),
                    ("G573", "Lion Ch4 complete"), ("G574", "camp: the berserker's duel"),
                    ("G575", "camp: Yachiko's baggage"), ("G576", "camp: the chest"),
                    ("G577", "a berserker killed"), ("G578", "riverbank: the scout's kit"),
                    ("G579", "S04 Rokuro at night (scene)"), ("G580", "S01 scene flag"), ("G581", "S02 scene flag"),
                    ("G582", "S06 scene flag"), ("G583", "S07 tent scene flag"), ("G584", "the shield-line (Hold)"),
                    # Phoenix Ch1 "The Silent Kami" (Haruki the starter; G470 the Jade Chains and G484 O-Tamai bound
                    # are shared with Lion Ch1; G571 phoenix_supply_proof)
                    ("G585", "Phoenix start: Haruki"), ("G586", "S01 scene"), ("G587", "apology_note_found"),
                    ("G588", "spirit wasteland (spells -25%)"), ("G589", "shrine_spirit_blessed"),
                    ("G590", "S02 Hoju dies"), ("G591", "S03 the embassy musters"), ("G593", "garden: Commune"),
                    ("G594", "hall: Summon"), ("G595", "study: Sense"), ("G597", "S05 the Magonojo ruins"),
                    ("G598", "S06 the broken shrine"), ("G600", "Phoenix at Hiruto's castle"),
                    ("G601", "S07 Ashimoshi freed"), ("G602", "S08 O-Tamai (Phoenix)"), ("G603", "S09 the note"),
                    ("G604", "Phoenix Ch1 complete"), ("G605", "Kamatori: the old nun blessed"),
                    ("G606", "west tower: the blade rack"),
                    ("G607", "Togashi Yosai met"), ("G608", "Togashi Yosai in the party"),
                    ("G609", "Togashi Yosai stepped aside for a duel"),
                    # Phoenix Ch2 "The Silent Court" (G626 numeric: strong debate answers)
                    ("G610", "Phoenix Ch2 started (S01)"), ("G611", "Matsu Hisae answered"), ("G612", "Hisae blessed"),
                    ("G613", "memory_ritual_refused"), ("G614", "S02 b_pass_cultists won"), ("G615", "Yosai cameo"),
                    ("G616", "S03 Treaty City"), ("G617", "Mieko met"), ("G618", "the murder"),
                    ("G619", "the historian's ghost blessed"), ("G620", "the scroll under the floor"),
                    ("G621", "the handwriting matched"), ("G622", "mieko_midnight_seen"), ("G623", "told_keiki"),
                    ("G624", "S05 the debate"), ("G625", "torii_saved"), ("G627", "rested until night (S06)"),
                    ("G628", "S06 Hioninmaru beaten"), ("G629", "consumer_scroll_kept"), ("G630", "Phoenix Ch2 complete"),
                    ("G631", "sub-story: the same dojo"), ("G632", "sub-story: the archive at night"),
                    ("G633", "sub-story: sober by dusk"), ("G634", "Zumiki: the chest"), ("G635", "Zumiki: watchtower"),
                    ("G636", "pass: the avalanche shelf"), ("G637", "pass: the wolf den"),
                    ("G638", "Courage of the Seven Thunders taught (story skill)"), ("G639", "S04 scene"),
                    ("G640", "S05 scene"), ("G641", "S06 scene"), ("G642", "S07 scene"), ("G643", "dojo: Hida spoken"),
                    ("G644", "dojo: Shiba spoken"), ("G645", "S03 scene"), ("G646", "the magistrates"),
                    # Phoenix Ch3 "The Darkfever" (G650 numeric: sick_treated)
                    ("G651", "Phoenix Ch3 started (S01)"), ("G652", "sick: Goemon's wife"), ("G653", "sick: Hana"),
                    ("G654", "sick: the charcoal-burner"), ("G655", "sick: the priestess"),
                    ("G656", "Hand of Jurojin taught (story skill)"), ("G657", "sick: the Lion deserter"),
                    ("G658", "sick: the twins"), ("G659", "sick: the ronin bodyguard"), ("G660", "the leave choice"),
                    ("G661", "stayed_extra_day"), ("G662", "S03 the Council"), ("G663", "the refugee blessed"),
                    ("G664", "S04 the circle"), ("G665", "S05 forest spirits"), ("G666", "estate: the go board"),
                    ("G667", "estate: the screen"), ("G668", "estate: the courtyard"), ("G669", "S05 dark Mieko"),
                    ("G670", "showed_scroll"), ("G671", "S06 Kuzushi beaten"), ("G672", "S07 the sealed library"),
                    ("G673", "Phoenix Ch3 complete"), ("G674", "the hospital rest used"), ("G675", "road chests"),
                    ("G676", "forest: woodcutter's hut"), ("G677", "forest: web shrine"), ("G678", "forest: fever "
                    "shrine"), ("G679", "estate: Mieko's room"), ("G680", "Kyuden Isawa chest"),
                    ("G681", "the dying healer"), ("G682", "sick: the ferryman (Remedy)"),
                    # Phoenix Ch4 "Howl" (numeric: G684 echoes_blessed, G691 dream_keys, G697 mieko_answer 1 yet 2 eight)
                    ("G683", "Phoenix Ch4 started (S01)"), ("G685", "echo: the camellias"),
                    ("G686", "echo: the counting song"), ("G687", "echo: the Consumer"), ("G688", "shadows a"),
                    ("G689", "shadows b"), ("G690", "S03 the last shrine"), ("G692", "dream key 1"),
                    ("G693", "dream key 2"), ("G694", "dream key 3 (wake)"), ("G695", "S04 the dark half beaten"),
                    ("G696", "whole (Void -1, passive Whole)"), ("G698", "Phoenix Ch4 complete"),
                    ("G699", "the drowned sailor blessed"), ("G700", "the jetty box"), ("G701", "S06 scene"),
                    ("G702", "the dream (arrival)"), ("G703", "cliff: wrecked shrine-boat"), ("G704", "S04 scene"),
                    ("G705", "S05 scene"),
                    # Dragon Ch1 "Under the Skin" (Gendo the starter)
                    ("G706", "Dragon start: Gendo"), ("G707", "S01 scene"), ("G708", "S01 Discern the captain"),
                    ("G709", "S01 the dock brawl"), ("G710", "S02 the hall"), ("G711", "oharu_poisoned"),
                    ("G712", "S03 the dump (Yosai)"), ("G713", "S04 the school"), ("G714", "riichi_trusts"),
                    ("G715", "momo_joined"), ("G716", "ruins: the fourth step"), ("G717", "ruins: stone 1"),
                    ("G718", "ruins: stone 2"), ("G719", "ruins: stone 3"), ("G720", "thugs a"), ("G721", "thugs b"),
                    ("G722", "S05 the notes"), ("G723", "S06 Kumpei"), ("G724", "kumpei_accused"),
                    ("G725", "kumpei_watched"), ("G726", "S07 the tide"), ("G727", "Dragon Ch1 complete"),
                    ("G728", "Discern: the net-mender"), ("G729", "Discern: Kosai"), ("G730", "Discern: Muika"),
                    ("G731", "Discern: the Storm Legion thug"), ("G732", "pier crate"), ("G733", "the tax shed"),
                    ("G734", "ruins: the Gusai banner"), ("G735", "hill path: the viper nest"),
                    ("G736", "the paint box"), ("G737", "S08 scene"), ("G738", "ruins: the fallen pillar"),
                    ("G739", "ruins: the hostage's cell"),
                    # Dragon Ch2 "The Painting" (numeric: G748 History, 100 at the start)
                    ("G740", "Dragon Ch2 started (Tortoise Island)"), ("G741", "S01 the house (the quake)"),
                    ("G742", "mirumoto_school (S02)"), ("G743", "cove: the crabs"), ("G744", "cove: the guards"),
                    ("G745", "S03 the portal (crossed)"), ("G746", "jumped_first"),
                    ("G747", "S04 the orchard (History shown)"), ("G749", "S05 Ushimo subdued"),
                    ("G750", "ushimo_lead"), ("G751", "S06 the court (invitations)"),
                    ("G752", "Dragon Ch2 complete (the Ink Door)"), ("G753", "Discern: the villager"),
                    ("G754", "cove: the ledge"), ("G755", "cove: Kumpei's paint scraps"),
                    ("G756", "cove: the clay city"), ("G757", "cove: the Bow"), ("G758", "house: the cat"),
                    ("G759", "Togashi Yosai lost in the ink (Dragon Ch2-4)"), ("G760", "the Tortoise ferry"),
                    ("G761", "S04 limbo"), ("G762", "S05 scene"), ("G763", "dojo: the sparring post"),
                    ("G764", "TB-dragon2-b (the window)"), ("G765", "the Ink Door scene"),
                    ("G766", "S06 the orchard"), ("G767", "cove 2 scene"), ("G768", "house: the study"),
                    # Dragon Ch3 "Past Mistakes" (numeric: G770 dinner 1 Bayushi, 2 Doji, 3 Shiba)
                    ("G769", "Dragon Ch3 started (S01 the garden)"), ("G771", "S02 the dinner held"),
                    ("G772", "the guard's tip (Ushimo's house)"), ("G773", "tsuhime_helped"),
                    ("G774", "mirrors_recovered"), ("G775", "S03 Ushimo's house"), ("G776", "Miyoshi met"),
                    ("G777", "road: the scout camp"), ("G778", "Izumida: the musketeers"),
                    ("G779", "S04 the scorched map"), ("G780", "Izumida: a musket taken"),
                    ("G781", "Izumida: the powder store taken"), ("G782", "S05 the war council"),
                    ("G783", "S06 the parley"), ("G784", "Dragon Ch3 complete"), ("G785", "Bayushi: refused"),
                    ("G786", "Bayushi: agreed"), ("G787", "the bad future seen"), ("G789", "the gaijin trader: glass"),
                    ("G790", "Discern: the gaijin trader"), ("G791", "Discern: the scorched map's dates"),
                    ("G792", "TB-dragon3-b (Sanro, the window)"), ("G793", "Seppun Ushimo travels with Gendo"),
                    ("G794", "S04 the ridge"), ("G795", "Izumida: the musket balls"), ("G796", "S07 scene"),
                    ("G797", "road: the burned waystation"),
                    # Dragon Ch4 "The Battle of the White Stag" (numeric: G807 fronts_won 0-3)
                    ("G798", "Dragon Ch4 started (S01 the war camp)"), ("G800", "Discern: the Crane veteran"),
                    ("G801", "the land front fought"), ("G802", "the land front won"),
                    ("G803", "the Mantis front settled"), ("G804", "the Mantis front won"),
                    ("G805", "the lighthouse front fought"), ("G806", "the lighthouse front won"),
                    ("G808", "Sanro fell"), ("G809", "S03 the tunnels"), ("G810", "tunnels: the musketeers"),
                    ("G811", "tunnels: a barrel used"), ("G812", "tunnels: the smuggler's cache"),
                    ("G813", "S04 the flagship"), ("G814", "kumpei_spared"), ("G815", "vial_saved"),
                    ("G816", "the vial thrown"), ("G817", "S05 the offer"), ("G818", "glory_refused"),
                    ("G819", "history_final: saviour (accepted)"), ("G820", "S06 home (the cove)"),
                    ("G821", "S06 Kitsuki Yasu's hall"), ("G823", "S06 the prophecy"),
                    ("G824", "Ushimo leads the relief"), ("G825", "TB-dragon4-b"), ("G826", "the gangway save"),
                    ("G830", "Dragon Ch4 complete (the Ink Door closed)"),
                    # Scorpion Ch1 "Blood and Iron" (Mitsue the starter; numeric: G833 rumours_found, G851 suspects)
                    ("G831", "Scorpion start: Mitsue"), ("G832", "S01 the memorial"),
                    ("G834", "eavesdrop: the koi-pond courtiers"), ("G835", "eavesdrop: the Mantis envoy"),
                    ("G836", "eavesdrop: the pale courtier"), ("G837", "S01 the incense burns down"),
                    ("G838", "S02 the willow teahouse"), ("G839", "the servants' gate"),
                    ("G840", "S03 the grove bandits"), ("G841", "grove: the traitor's purse"),
                    ("G842", "Shutai: Noburo"), ("G843", "Shutai: Megu's room"),
                    ("G844", "eavesdrop: the Shutai innkeeper"), ("G845", "S04 Kudo (Rui)"),
                    ("G846", "eavesdrop: Suzume Rika"), ("G847", "eavesdrop: Kasuga Yodo"),
                    ("G848", "eavesdrop: the governor at night"), ("G849", "governor_fake (S04b)"),
                    ("G850", "the dock-hand (the iron box)"), ("G852", "Kitsune Hana (not himself)"),
                    ("G853", "S05 the nudge"), ("G854", "S05 the Kommei brood"), ("G855", "S06 the barge"),
                    ("G856", "S06 the leeches"), ("G857", "the Miya relics (crystal)"), ("G859", "hana_saved"),
                    ("G860", "iron_box_held"), ("G861", "Scorpion Ch1 complete"),
                    ("G862", "Kudo: the beating stopped"), ("G863", "Kudo: the old women"),
                    ("G864", "Kudo: the Kitsune boy"), ("G865", "Yoritomo Rui travels with Mitsue"),
                    ("G866", "the box dropped (Hana broken)"), ("G867", "the box stolen in battle"),
                    ("G868", "the Oracle rose (ritual 10)"), ("G869", "grove: the posts counted"),
                    ("G870", "castle town: the beggar"), ("G874", "Shutai: the priest"),
                    ("G875", "Kudo: the Inari priestess (the Kansen counter)"),
                    ("G876", "Kudo: Rui's briefing"), ("G877", "S08 dawn"),
                    ("G873", "marsh: the dead tree"), ("G878", "suspect: Rui's briefing"),
                    # Scorpion Ch2 "City of Masks" (numeric: G883 masks_got 0-4, G905 souls freed 0-3)
                    ("G879", "Scorpion Ch2 started (the plains road)"), ("G880", "Hisatu Kensu: the mask dream"),
                    ("G881", "giseiki_mask_held (S02 the dying scout)"), ("G882", "S03 the city gate"),
                    ("G884", "mask: iron"), ("G885", "mask: cedar"), ("G886", "mask: ink"), ("G887", "mask: silk"),
                    ("G888", "the sake-seller (iron)"), ("G889", "Kakita Yuko (ink)"), ("G890", "Miya Hatomu (cedar)"),
                    ("G891", "the temple gatekeeper (silk): the Temple District open"),
                    ("G892", "history: pair 1"), ("G894", "history: pair 2"), ("G895", "history: pair 3"),
                    ("G893", "S05 the shadow hunters (Kasiko joins)"), ("G896", "Giseiki's mask given to Osuko"),
                    ("G897", "mitsue_wore_giseiki"), ("G898", "Doji Siko's ambush"), ("G899", "the market collapse"),
                    ("G900", "Kitsu Kenshai"), ("G901", "Kasamashi: the jade mask"), ("G902", "Togashi Sumi's riddle"),
                    ("G903", "S06 b_stitched_monks_a"), ("G904", "S06 b_stitched_monks_b"),
                    ("G906", "S07 Munashii"), ("G907", "city_freed"), ("G908", "city_sealed"),
                    ("G909", "Scorpion Ch2 complete"), ("G910", "eavesdrop: the bath attendant"),
                    ("G911", "Ide Xue"), ("G912", "temple: the cracked wall"), ("G913", "temple: the scriptorium"),
                    ("G914", "Giseiki's counter-word used"), ("G915", "eavesdrop: Agasha Kusuri"),
                    ("G916", "Giseiki: \"I did\" (the history)"), ("G917", "S07 the monastery"),
                    # Scorpion Ch3 = Unicorn Ch2 "Fortunes Lost" (Mitsue's view; numeric G924 grievances 0-4)
                    ("G918", "Scorpion Ch3 started (the Ojatara road)"), ("G919", "S01 the tribunal (Rin joins)"),
                    ("G920", "grievance: the Jiochi well"), ("G921", "grievance: the Shosuro troupe"),
                    ("G922", "grievance: Katsu's funeral"), ("G923", "grievance: the padded armies"),
                    ("G925", "mitsue_knows_shoju_war (the seppuku letter)"), ("G926", "S02 Rin is followed"),
                    ("G927", "S02 Gochu and the bell"), ("G928", "gochu_family_fed"), ("G929", "S03 Nihime"),
                    ("G930", "nihime_told"), ("G931", "the grave path: the sealed mine gate"),
                    ("G932", "S04 the hit squad"), ("G933", "S05 the verdict"), ("G934", "verdict: both"),
                    ("G935", "verdict: soshi"), ("G936", "Scorpion Ch3 complete"), ("G937", "Shosuro Mayumi"),
                    ("G938", "eavesdrop: the Soshi officers"), ("G939", "the child's grave"),
                    ("G940", "the ridge watchers"), ("G941", "eavesdrop: the quartermaster"),
                    ("G942", "the hit squad's silence bubble popped"), ("G943", "S03 Perfume Petal Blossom"),
                    # Scorpion Ch4 "The Eve" (production scorpion-ch4)
                    ("G944", "Scorpion Ch4 started (S01 the box talks)"), ("G945", "S02 the pilgrim troupe's guide"),
                    ("G946", "courier_heard (S03)"), ("G947", "togashi_heard (S04 the garden)"),
                    ("G948", "S05 duty's knife"), ("G949", "gendo_keeps_secret"),
                    ("G950", "b_furnace_elementals won"), ("G951", "b_ash_ghouls won"),
                    ("G952", "S07 the stolen face beaten"), ("G953", "box_destroyed (S08; Scorpion Ch4 complete)"),
                    ("G954", "Tamori Haku travels with Mitsue"), ("G955", "eavesdrop: the Kitsuki clerk"),
                    ("G956", "the procession tip heard"), ("G957", "the lava-step jump (Ward-Robe)"),
                    ("G958", "the courier's pack left alone"), ("G959", "S04 the procession on the road"),
                    ("G960", "S06 the box screams"), ("G961", "S06 the Tamori monks' welcome"),
                    ("G962", "Mitsue Rank 3 (The Shadow Has No Form)"), ("G963", "gendo_in_party (S02)"),
                    ("G964", "the stolen face taken back (boss)"), ("G965", "Yosai guides Mitsue (stand-in)"),
                    ("G966", "the Dragon road signpost (Buried Leaves)"),
                    # Unicorn Ch1 "Fault Lines" (production unicorn-ch1; numeric G975 cases_done 0-3)
                    ("G967", "Unicorn start: Tamotsu"), ("G968", "S01 a seat at the small table"),
                    ("G969", "S02 the camps (the rice)"), ("G970", "camps_fed"), ("G971", "b_camp_thugs won"),
                    ("G972", "case 1: the assassins"), ("G973", "case 2: the salted fields"),
                    ("G974", "case 3: the Temple of Jizo"), ("G976", "Shiro no Soshi court"),
                    ("G977", "S04 Miyahana"), ("G978", "S05 the bombing (rin_joined)"),
                    ("G979", "S06 Yotomo: Sabu"), ("G980", "b_cave_guerrillas won"),
                    ("G981", "S07 Naohida escapes"), ("G982", "S08 judge the living (Unicorn Ch1 complete)"),
                    ("G983", "naohida_named"), ("G984", "the rice bartered"),
                    ("G985", "Gaijin Spyglass (Hiroichi's telescope)"), ("G986", "the supply ledger bartered"),
                    ("G987", "Hitoro's testimony"), ("G988", "Daiyu's carrot"), ("G989", "the camp grandmother"),
                    # Unicorn Ch2 = Tamotsu's view of "Fortunes Lost" (shares G920-G933 with Scorpion Ch3)
                    ("G990", "Unicorn Ch2: S01 the benches (Tamotsu)"), ("G991", "the seppuku as news"),
                    ("G992", "the troupe's props bartered"), ("G993", "verdict iuchi"),
                    ("G994", "Unicorn Ch2 complete"), ("G995", "Persimmon's afternoon with the swing judge"),
                    ("G996", "the Jiochi water-carrier"), ("G997", "the padded armies' ledgers"),
                    # Unicorn Ch3 "The Noblest Blood" (production unicorn-ch3; numeric G1011 servants woken 0-3)
                    ("G998", "Unicorn Ch3: S01 the star field (karasu_joined)"), ("G999", "Covered Ears (wax in)"),
                    ("G1000", "S02 shahai_trusts"), ("G1001", "b_tower_servants won"),
                    ("G1002", "S03 the woods (Daiyu)"), ("G1003", "daiyu_state shattered (else comforted)"),
                    ("G1004", "S04 the Dragon ride"), ("G1005", "mirumoto_terms honour (else jade)"),
                    ("G1006", "S05 the mine graves (Karasu)"), ("G1007", "b_mine_dead_a won"),
                    ("G1008", "b_mine_dead_b won"), ("G1009", "S06 the mine guardian laid to rest"),
                    ("G1010", "S07 Unicorn Ch3 complete"), ("G1012", "the wind-shaft ledge"),
                    ("G1013", "the foreman's ledger"), ("G1014", "raw jade node 1"), ("G1015", "raw jade node 2"),
                    ("G1016", "raw jade node 3"), ("G1017", "raw jade node 4"), ("G1018", "raw jade node 5"),
                    ("G1019", "raw jade node 6"), ("G1020", "Iuchi Karasu: guest"), ("G1021", "the tower's first note"),
                    # Unicorn Ch4 "Regret" (production unicorn-ch4)
                    ("G1022", "Unicorn Ch4: S01 Naohida under the white flag"), ("G1023", "truce_bought"),
                    ("G1025", "S02 the tunnel mouth"), ("G1026", "b_tunnel_legion won"),
                    ("G1027", "S03 the stairs (Shahai)"), ("G1028", "shahai_kept_close"),
                    ("G1029", "S04 Regret banished"), ("G1030", "settlement heir (else treaty)"),
                    ("G1031", "Unicorn Ch4 complete (Tamotsu's path)"), ("G1032", "the pigeon's letter bartered"),
                    ("G1033", "the grandmother's saddle"), ("G1034", "Hiroichi's chest"),
                    ("G1035", "the wind-ledge"), ("G1036", "Naohida: guest"),
                    ("G1037", "the Jade Toll (mirumoto_terms jade, after the chapter)"),
                    # Ronin Ch1 "What's Eating the Eta" (production ronin-ch1; numeric G1039 ronin_school_first 1-3)
                    ("G1038", "Ronin start: Sayo"), ("G1040", "S01 the docks"), ("G1041", "S02 Kagemaro's task"),
                    ("G1042", "sono_link (the chit)"), ("G1043", "S03a the alley ambush won"),
                    ("G1044", "monk_riddle"), ("G1045", "S04 the eta village (Hiro)"), ("G1046", "Akari cameo"),
                    ("G1047", "S05 b_tengu_bridge won"), ("G1048", "S06 b_bakemono won"), ("G1049", "loot_returned"),
                    ("G1050", "the loot kept"), ("G1051", "Grandmother Cedar's Gift"),
                    ("G1052", "S07 the old woman fought"), ("G1053", "hut_burned"), ("G1054", "S07 Tomie Cho falls"),
                    ("G1055", "S08 clean hands (Ronin Ch1 complete)"), ("G1056", "Hiro: guest"),
                    ("G1057", "pilfered: the Sono servant's purse"), ("G1058", "pilfered: the herb seller"),
                    ("G1059", "pilfered: the bargeman"), ("G1060", "the loot choice made"),
                    ("G1061", "the beggar-monk met"), ("G1062", "S01 the memory: Ume-baa"),
                    # Ronin Ch2 "The Noble and the Ronin" (production ronin-ch2; numeric G1073 crawl_results)
                    ("G1063", "Ronin Ch2: the river road"), ("G1064", "S01 b_retainers_road won"),
                    ("G1065", "writ_pilfered"), ("G1066", "S02 the barge (Jinnai joins)"),
                    ("G1067", "S03 Floating Flowers (the poster)"), ("G1068", "S04 night 1: the storm"),
                    ("G1069", "retainers_spared"), ("G1070", "the retainers driven into the river"),
                    ("G1071", "S05 night 2: Jinnai gone"), ("G1072", "S06 the sand room"),
                    ("G1074", "S07 the Voice"), ("G1075", "S08 the enforcers (Jinnai stops it)"),
                    ("G1076", "order_promise kept"), ("G1077", "order_promise refused"),
                    ("G1078", "S09 Ronin Ch2 complete"), ("G1079", "Jinnai: guest"),
                    ("G1080", "Oyuki's cough"), ("G1081", "Kanemori's secret"),
                    ("G1082", "Kanemori asks (Kanemori's Discount)"), ("G1083", "the spy's lantern pilfered"),
                    ("G1084", "pilfered: the fisherman"), ("G1085", "Madame Hagi's secret bought"),
                    ("G1086", "the den alcove"), ("G1087", "the fox shrine"), ("G1088", "Tokubei's office"),
                    ("G1089", "the boatman's warning"), ("G1090", "the enforcer's pack (Snake Ring)"),
                    ("G1091", "the writ choice made"), ("G1093", "S05 the den (Jinnai ahead)"),
                    # Ronin Ch3 "The Village of the Wounded Lion" (production ronin-ch3)
                    ("G1094", "Ronin Ch3: the road north"), ("G1095", "S00 the checkpoint (the writ)"),
                    ("G1096", "S00 b_lion_checkpoint won / toll paid"), ("G1097", "S01 the village (the climbers)"),
                    ("G1098", "S02 the climb begins (Hanae joins)"), ("G1099", "S02 stage 1: the Crane grave"),
                    ("G1100", "S02 stage 2: the scorched gate"), ("G1101", "S02 stage 3: the Mirumoto armour"),
                    ("G1102", "S02 the castle gate"), ("G1103", "replay 1: the kidnapping"),
                    ("G1104", "replay 2: the fight"), ("G1105", "replay 3: the gate"),
                    ("G1106", "replay 4: the flight"), ("G1107", "replay 5: the basin"),
                    ("G1108", "the kneeling Lion (I have failed)"), ("G1109", "S03 the truth (the basin door)"),
                    ("G1110", "S04 the basin broken"), ("G1111", "hikaru_spoke"), ("G1112", "climbers_told"),
                    ("G1113", "S06 the descent"), ("G1114", "mosuke_knows"), ("G1115", "S06 Mosuke (choice made)"),
                    ("G1116", "S07 Ronin Ch3 complete"), ("G1117", "rope point 1"), ("G1118", "rope point 2"),
                    ("G1119", "rope point 3"), ("G1120", "the rock shelter (the frozen yari)"),
                    ("G1121", "pilfered: the Climbing Spikes"), ("G1122", "the spiked ledge"),
                    ("G1123", "the nursery (Silver Rattle)"), ("G1124", "the hero shrine storeroom"),
                    ("G1125", "the frozen shrine on the road"), ("G1126", "Hida Ren's grin"),
                    ("G1127", "the snow mounds (Mosuke)"), ("G1128", "S02 Hikaru first seen"),
                    ("G1129", "Mirumoto Hikaru: guest"), ("G1130", "S03 the fortress (arrival)"),
                    ("G1131", "S00 the checkpoint (first visit)"),
                    # Ronin Ch4 "The Oracle's Choice" (production ronin-ch4; numeric G1133, G1144)
                    ("G1132", "Ronin Ch4: the oracle road"), ("G1134", "S01 Akari (the fire talks to me)"),
                    ("G1135", "the cipher letter (pilfered)"), ("G1136", "the pilgrims calmed (route bonus)"),
                    ("G1137", "the back-gate key"), ("G1138", "S03 the eta quarter (Anatomy)"),
                    ("G1139", "Hiro SS2 unlocked (The Tiger in the Blood)"), ("G1140", "S04 b_well_agents won"),
                    ("G1141", "well_cleansed"), ("G1142", "sayo_saw_nashiko"), ("G1143", "S05 the offer"),
                    ("G1145", "S06 the race begins"), ("G1146", "race battle 1 (the rooftops)"),
                    ("G1147", "race battle 2 (the alley; Hiro stays)"), ("G1148", "race battle 3 (the switchback)"),
                    ("G1149", "race battle 4 (cliff)"), ("G1150", "race battle 5 (cliff)"),
                    ("G1151", "the crater lantern"), ("G1152", "S07 the champion"), ("G1153", "naga_talked_down"),
                    ("G1154", "S08 Ronin Ch4 complete"), ("G1155", "the lava tube den"),
                    ("G1156", "the snake scout"), ("G1157", "S04 the well (scene)"),
                    ("G1158", "S08 the ascension (scene)"),
                    # The finale "The Empress of Nothing" (production/finale.md; numeric G1160 the reserve)
                    ("G1161", "finale: the Plains of Thunder road"), ("G1162", "F01 eight roads (the join-up)"),
                    ("G1163", "F02 wave 1"), ("G1164", "F02 wave 2"), ("G1165", "F02 wave 3"),
                    ("G1166", "F02 wave 4"), ("G1167", "F02 wave 5"), ("G1168", "F02 wave 6"),
                    ("G1169", "F02 wave 7"), ("G1170", "F03 the herald (Act 1 complete)"),
                    ("G1171", "the thunder-split rock (Moonlit Yumi)"), ("G1172", "the burned village"),
                    ("G1173", "the shrine defence (in progress)"), ("G1174", "Ryozo's name given back"),
                    ("G1175", "Kage's Hiruma came a wave early (the flare)"), ("G1176", "the abbot saved"),
                    ("G1177", "the finale road-marker read"),
                    ("G1178", "F04 Stich'Kik freed (the guide)"), ("G1179", "F05 the Naga marks"),
                    ("G1180", "F05 the carved mock"), ("G1181", "b_shinomen_a"), ("G1182", "the Naga shrine (root-wall)"),
                    ("G1183", "b_shinomen_b"), ("G1184", "F06 Mamoru's fire"), ("G1185", "mamoru_hint (Two Voices)"),
                    ("G1186", "b_kumo_spiders (rude to Mamoru)"), ("G1187", "F07 the glade (the Duty plaque)"),
                    ("G1188", "a Naga scout killed"), ("G1190", "F08 the debate (the Empress rises)"),
                    ("G1191", "F08 the debate (scene)"), ("G1192", "F09 phase 1 won (the Bride)"),
                    ("G1193", "F09 phase 2 won (Body of Damned Time)"), ("G1194", "F09 phase 3 won (she flees)"),
                    ("G1195", "F09 the final battle (scene)"), ("G1196", "F09 the best four chosen (menu)"),
                    ("G1197", "F11 she is dead (the glade is just a glade)"), ("G1198", "E01 coda: Natsuko"),
                    ("G1199", "E01 coda: Rensei"), ("G1200", "E01 coda: Gendo"), ("G1201", "E01 coda: Shizue"),
                    ("G1202", "E01 coda: Haruki"), ("G1203", "E01 coda: Tamotsu"), ("G1204", "E01 coda: Sayo"),
                    ("G1205", "E01 coda: Mitsue"), ("G1206", "E02 the final image"),
                    ("G1207", "the finale cleared (post-game)"), ("G1208", "E01 leaving the glade"),
                    ("G1209", "post-game: back at the shrine (the clear save)"),
                    ("G1210", "F02 wave 5: the escort (in battle)"), ("G1211", "F02 wave 5: the abbot fell"),
                    ("G1212", "Hiruma Kage: guest (the finale)"),
                    ("G1213", "inquisitors_hunt_done (SS-TEAM)"), ("G1214", "benjiro_father_home (Benjiro SS2)"),
                    ("G1215", "post-game: Shiro Hiruma sighted"), ("G1216", "post-game: the outer bailey (the map)"),
                    ("G1217", "post-game: Oni no Okura (the hall)"), ("G1218", "post-game: Shiro Hiruma cleared"),
                    ("G1219", "post-game: the Hiruma tablets set up (the keep)"),
                    ("G1220", "post-game: the Orochi (scene)"), ("G1221", "post-game: the Orochi yielded"),
                    ("G1222", "post-game: the Orochi killed (a killing blow)"),
                    ("G1223", "the shifting waste: the last move was south"),
                    ("G1224", "dojo kata taught (Hida dojo: Natsuko's Striking as Earth)"),
                    ("G1225", "dojo kata taught (Kakita academy: Rensei's Kakita's First Stance)"),
                    ("G1226", "this battle: the Wave-woman trait is worn (Flee always works; RokuganJobs.sk)"),
                    ("G1229", "Crab Ch4: the cellar-stair objective shown"),
                    ("G1230", "the finale road-marker objective shown (any path)"),
                    ("G1232", "Winter Court: the Yumi contest won with the bow (mini-game)"),
                    ("G1233", "Winter Court: Takeo's three laps won (mini-game)"),
                    ("G1234", "road walked: Hiruma Natsuko (Crab)"), ("G1235", "road walked: Kakita Rensei (Crane)"),
                    ("G1236", "road walked: Kitsuki Gendo (Dragon)"), ("G1237", "road walked: Akodo Shizue (Lion)"),
                    ("G1238", "road walked: Isawa Haruki (Phoenix)"),
                    ("G1239", "road walked: Shosuro Mitsue (Scorpion)"),
                    ("G1240", "road walked: Ide Tamotsu (Unicorn)"), ("G1241", "road walked: Sayo (Ronin)"),
                    ("G1242", "Crane Ch1 -> Ch2: the way-to-Garden-Under-Shadow objective shown"),
                    ("G1243", "Crane Ch2: the castle-gate-guard objective shown")):
        gv[gid] = {"defval": False, "name": nm, "type": 1}
    gv["G1160"] = {"defval": 0, "name": "finale Party B (bitmask over P100-P107)", "type": 2}
    for _k in range(16):                                # side quests: G1250 + 3k taken / hunted / done (gen_maps
        for _o, _what in enumerate(("taken", "hunted", "done")):     # SIDE_QUESTS, quest k; room for 16)
            gv["G%d" % (1250 + 3 * _k + _o)] = {"defval": False, "name": "side quest %d: %s" % (_k, _what), "type": 1}
    for _k in range(20):                                # connecting routes: gate k open (gen_maps ROUTE_GATES,
        gv["G%d" % (1300 + _k)] = {"defval": False, "name": "route gate %d open (RokuganField routeFlags)" % _k,
                                   "type": 1}                                           # set on every map launch)
    for _n in range(100, 142):                          # RokuganParty partyFlags: Pnnn is in the party (gen_maps
        gv["G%d" % (1220 + _n)] = {"defval": False, "name": "in the party: P%d" % _n, "type": 1}   # party_npc_pass)
    for _k in range(5):                                 # Cakon odd jobs (gen_maps FETCH_QUESTS): taken / found / done
        for _o, _what in enumerate(("taken", "found", "done")):
            gv["G%d" % (1382 + 3 * _k + _o)] = {"defval": False, "name": "odd job %d: %s" % (_k, _what), "type": 1}
    gv["G1362"] = {"defval": 0, "name": "guests met (bits by guest number; RokuganBattle guestSkills)", "type": 2}
    gv["G1363"] = {"defval": False, "name": "the finale: 8 party places (RokuganParty partyCap)", "type": 1}
    for _n in range(1, 18):                             # RokuganAI guestVar: lifetime calls spent
        gv["G%d" % (1364 + _n)] = {"defval": 0, "name": "guest %d: calls spent (lifetime)" % _n, "type": 2}
    gv["G1244"] = {"defval": 0,"name": "Journal: the tracked entry (0 = the main story; RokuganJournal.sk)", "type": 2}
    gv["G1189"] = {"defval": 0, "name": "finale: Nashiko's shields broken in the debate (0-8)", "type": 2}
    gv["G1092"] = {"defval": 0, "name": "ronin_technique_second (Ronin Ch2 Rank 2: 1-3 another school's R1, 4 Punish "
                                        "the Arrogant, 5 Taking the Measure, 6 Will Not Flesh)", "type": 2}
    gv["G1133"] = {"defval": 0, "name": "ronin_technique_third (Ronin Ch4 Rank 3: 1-6 an R1/R2 she lacks, 7 Desperate "
                                        "Speed, 8 Strike Like Wind, 9 Hasten the Blade)", "type": 2}
    gv["G1144"] = {"defval": 0, "name": "race_route (Ronin Ch4: 1 the pilgrim road, 2 the cliff path)", "type": 2}
    gv["G1073"] = {"defval": 0, "name": "crawl_results (Ronin Ch2 sand room: +1 Sayo crawled, +2 Yosai crawled)",
                   "type": 2}
    gv["G304"] = {"defval": 0, "name": "ebisu_saved_how (1 charm, 2 steel, 3 coin)", "type": 2}
    gv["G833"] = {"defval": 0, "name": "rumours_found (Scorpion Ch1 S01, 0-3)", "type": 2}
    gv["G851"] = {"defval": 0, "name": "Kudo suspects heard (Scorpion Ch1 S04)", "type": 2}
    gv["G883"] = {"defval": 0, "name": "masks_got (Scorpion Ch2, 0-4)", "type": 2}
    gv["G905"] = {"defval": 0, "name": "souls freed (Scorpion Ch2 stitched monks, Honor +1 each up to 3)", "type": 2}
    gv["G924"] = {"defval": 0, "name": "grievances proven (Scorpion Ch3, 0-4)", "type": 2}
    gv["G975"] = {"defval": 0, "name": "cases_done (Unicorn Ch1, 0-3)", "type": 2}
    gv["G1011"] = {"defval": 0, "name": "singing servants woken (Unicorn Ch3, Honor +1 each up to 3)", "type": 2}
    gv["G1039"] = {"defval": 0, "name": "ronin_school_first (Ronin Ch1: 1 warrior, 2 duelist, 3 yojimbo)", "type": 2}
    gv["G319"] = {"defval": 0, "name": "dawn_route (1 blade, 2 law, 3 bandits, 4 challenge)", "type": 2}
    gv["G330"] = {"defval": 3, "name": "Pleasant Eaves standing (failed Charms cost it; 0 = refuses)", "type": 2}
    gv["G342"] = {"defval": 3, "name": "Goroso's castle standing (failed Charms cost it; 0 = refuses)", "type": 2}
    gv["G353"] = {"defval": 0, "name": "camp_split (1 split, 2 together)", "type": 2}
    gv["G356"] = {"defval": 0, "name": "uji_won_by (1 argument, 2 tadaka)", "type": 2}
    gv["G360"] = {"defval": 0, "name": "Iron Crane generals freed (0-3)", "type": 2}
    gv["G370"] = {"defval": 3, "name": "Garden Under Shadow standing (failed Charms cost it)", "type": 2}
    gv["G404"] = {"defval": 3, "name": "Crane port standing (failed Charms cost it)", "type": 2}
    gv["G416"] = {"defval": 3, "name": "Kyuden Doji standing (failed Charms cost it)", "type": 2}
    gv["G421"] = {"defval": 0, "name": "play_known_scenes (0-3)", "type": 2}
    gv["G438"] = {"defval": 0, "name": "rehearsal score (0-5)", "type": 2}
    gv["G453"] = {"defval": 0, "name": "clues_found (Lion Ch1, 0-6)", "type": 2}
    gv["G527"] = {"defval": 0, "name": "message_route (1 deliver, 2 ask the karo)", "type": 2}
    gv["G556"] = {"defval": 0, "name": "go_between (1 Rensei, 2 Atsuko, 3 Shizue)", "type": 2}
    gv["G626"] = {"defval": 0, "name": "torii debate: strong answers", "type": 2}
    gv["G650"] = {"defval": 0, "name": "sick_treated (0-10)", "type": 2}
    gv["G684"] = {"defval": 0, "name": "echoes_blessed (0-3)", "type": 2}
    gv["G691"] = {"defval": 0, "name": "dream_keys (0-3)", "type": 2}
    gv["G697"] = {"defval": 0, "name": "mieko_answer (1 yet, 2 eight)", "type": 2}
    gv["G807"] = {"defval": 0, "name": "fronts_won (0-3)", "type": 2}
    gv["G770"] = {"defval": 0, "name": "dinner (1 Bayushi, 2 Doji, 3 Shiba)", "type": 2}
    gv["G748"] = {"defval": 100, "name": "History meter (Dragon Ch2-4, 0-100; anachronisms lower it)", "type": 2}
    for gid, nm in (("G492", "painting_answer (1 best .. 4)"), ("G494", "bracket_result (0 lost, 1 won)"),
                    ("G505", "atsuko_promise (0 none, 1 honest, 2 lie)")):
        gv[gid] = {"defval": 0, "name": nm, "type": 2}
    gv["G211"] = {"defval": 0, "name": "accusation (1 Mutsuye, 2 Shigeru, 3 one more night)", "type": 2}
    gv["G219"] = {"defval": 0, "name": "archery choice (1 win, 2 lose politely, 3 the goblin's hat)", "type": 2}
    gv["G282"] = {"defval": 0, "name": "dread_count (Crab Ch4 stalk, 0-3)", "type": 2}
    gv["G283"] = {"defval": 0, "name": "travelers knocked out by Nashiko (Crab Ch4)", "type": 2}
    gv["G293"] = {"defval": 0, "name": "current hireling (tools/hirelings.py; 0 none)", "type": 2}
    gv["G294"] = {"defval": 0, "name": "hireling charges left", "type": 2}
    gv["G291"] = {"defval": 0, "name": "courtiers hurt by the cellar ogre (Crab Ch4)", "type": 2}
    gv["G232"] = {"defval": 0, "name": "current guest (0 none, 1 Kitsu Takeo, 2 Yogo Mai, 3 Ide Fujio, 4 Daidoji "
                  "Sakura)", "type": 2}
    for code, name, fl, _m, _p in __import__("gen_maps").TRAVEL:       # world map: visited nodes
        gv[fl] = {"defval": False, "name": "visited: %s (%s)" % (name, code), "type": 1}
    gv["G061"] = {"defval": 3, "name": "Hoshi-no-Ichi standing (failed chance path actions lower it; 0 = refused)",
                  "type": 2}
    for gid, nm in (("G062", "Sumai: the Wall veteran beaten"), ("G063", "Kite Mirror returned"),
                    ("G064", "Wooden Fish returned"), ("G065", "Pearl Hairpin returned")):
        gv[gid] = {"defval": False, "name": nm, "type": 1}
    gv["G020"] = {"defval": 0, "name": "S04 Sumai losses vs Gonta (2 = he lets her win)", "type": 2}
    gv["G1227"] = {"defval": 0, "name": "field HUD: the current objective (1-based into RokuganObjectives.sk; 0 = "
                                        "none)", "type": 2}
    gv["G1228"] = {"defval": 0, "name": "field HUD: the chapter's recommended level (from its chapter card)", "type": 2}
    gv["G1231"] = {"defval": 0, "name": "last mini-game result (RokuganMini.sk: 1 won, 2 lost, 0 narrated fallback)",
                   "type": 2}
    save("gvar", gv)
    for kind in ("job", "item"):
        dd = load(kind)
        localise(kind, dd)
        if kind == "item":
            crab_items(dd)
        if kind == "job":                              # jobs + traits (tools/jobs_data.py, progression-v2.md)
            _jobs.build(dd, copy.deepcopy(dd["J000"]), copy.deepcopy(dd["J105"]))
        save(kind, dd)
    ar = load("armor")
    crab_armor(ar)
    save("armor", ar)
    st = load("store")
    crab_stores(st)
    save("store", st)

    # ---- skill.json
    s = load("skill")
    TPL_PUTCOND = copy.deepcopy(s["S003"])         # plain Strike (NOT S101 "mine-uchi": that one barely scratches)
    TPL_PUTCOND.update({"flags": 255, "dmgrate": [1.0, 1.0]})
    base = s["S010"]
    weapons = [("S100", "Katana", "slash1", "SE204"), ("S101", "Yari", "slash1", "SE205"),
               ("S102", "Tanto", "slash1", "SE204"), ("S103", "Tetsubo", "punch1", "SE201"),
               ("S104", "Yumi", "slash1", "SE205"), ("S105", "Bo", "punch1", "SE201")]
    for sid, w, ani, snd in weapons:
        k = copy.deepcopy(base)
        k["name"] = w + " Strike"
        k["desc"] = "A plain %s attack. (%s weapon bit)" % (w.lower(), w)
        k["elembits"] = B[w]
        k["eqtypebits"] = 2047
        k["enemyuse"] = True
        k["atkact"]["atkani"]["id"] = ani
        k["hitact"]["hitsnd"] = snd
        s[sid] = k
    # Razor's Edge (Natsuko's Talent, simplified for the prototype): defend stance
    re_ = copy.deepcopy(s["S001"])
    re_.update({"name": "Razor's Edge", "desc": "Stand in the gap: halve damage taken this turn.", "addlist": True})
    s["S110"] = re_
    # Jade Strike (Haruki / Karasu): Jade bolt
    js = copy.deepcopy(base)
    js.update({"name": "Jade Strike", "desc": "A bolt of jade light. Burns the Tainted.", "elembits": B["Jade"],
               "addlist": True, "eqtypebits": 2047, "dmgform": 1, "atkform": spell_atk(40), "consume": [0, 6],
               "enemyuse": False})   # magic formula needs a spell power in atkform
    s["S111"] = js
    # Traveler Talents (rules/schools.md R1 "Octopath translation"; plugin RokuganBattle.sk handles the special parts)
    COND_BIT = lambda kid: 1 << int(kid[1:])  # noqa: E731  cond K0nn -> putconds/remconds bit nn (keep nn < 50!)
    PUT_BY_ID = lambda kid: {"condid": kid, "efx_start": None, "opttype": "opt_putcond", "rate": 1.0,  # noqa: E731
                             "showmiss": False, "when": 0, "whom": 0}    # conditions K050+: put them by id instead
    noop = copy.deepcopy(s["S001"])
    noop["option"] = []
    def talent(sid, src, **kw):
        t = copy.deepcopy(src)
        t.update({"addlist": False, "enemyuse": False, "consume": [0, 0]})
        t.update(kw)
        s[sid] = t
    s["S110"]["desc"] = "School technique. Stand in the gap: halve damage taken and draw every enemy's eye for two turns."
    # Iaijutsu stacks (production crane-ch1 tutorial; plugin RokuganBattle onTalent): Focus builds up to 3; Strike
    # hits x(1 + 0.75 per stack) and is a certain critical only at full Focus
    talent("S120", noop, name="Iaijutsu: Focus", desc="School technique. Breathe, measure the distance: one stack of Focus "
           "(up to 3).")
    talent("S121", s["S100"], name="Iaijutsu: Strike", desc="School technique. One draw, one cut: x1.75 / x2.5 / x3.25 by "
           "Focus. At full Focus, a certain critical.", dmgrate=[1.0, 1.0], option=[])
    talent("S122", s["S004"], name="Deduce", option=[], desc="School technique. Read the foe: reveals all of its weaknesses.")
    talent("S123", s["S045"], name="Command", cmdtgt=11, putconds=COND_BIT("K020"),
           desc="School technique. Akodo orders: party ATK up, and the whole party acts first next turn.")
    talent("S124", noop, name="Attune", desc="School technique. Listen to the kami: the next spell is 50% stronger.")
    talent("S125", s["S004"], name="Many Faces: Steal", desc="School technique. A smile, a brush of sleeves: steal an item.")
    talent("S505", noop, name="Many Faces: Copy", cmdtgt=1, option=[], desc="School technique. Be the enemy for a moment: turn "
           "the last skill it used back on it.")
    talent("S126", s["S103"], name="Barter Coin", elembits=0,
           desc="School technique. Every man has his price: spend coin for a blow that grows with the purse.")
    talent("S127", s["S035"], name="Ume-baa's Poultice", remconds=COND_BIT("K001"),
           desc="Remedy (School), no ingredients: Ume-baa's poultice. Heal one ally and cure poison.")
    # English names for the template's shared commands
    s["S001"]["name"] = "Defend"
    s["S002"]["name"] = "Flee"
    s["S003"]["name"] = "Strike"
    s["S000"]["name"] = "Wait"
    # Sumai (Natsuko's path action bout): bare-handed throws carry the Unarmed bit
    th = copy.deepcopy(s["S103"])
    th.update({"name": "Throw", "desc": "Sumai. Grip the belt, drop the hips, throw. (Unarmed)",
               "elembits": B["Unarmed"]})
    s["S106"] = th
    cw = copy.deepcopy(th)                                                       # claw weapons: unarmed art, so they ride the Unarmed bit
    cw.update({"name": "Claw Strike", "desc": "Iron claws over the knuckles. (Unarmed)"})
    assert "S690" not in s
    s["S690"] = cw
    def putcond_skill(sid, src, name, cond, desc, rate=1.0, **kw):
        k = copy.deepcopy(src)
        k.update({"name": name, "desc": desc, "enemyuse": True, "addlist": True, "eqtypebits": 2047})
        k["option"] = [{"condid": cond, "efx_start": None, "opttype": "opt_putcond", "rate": rate,
                        "showmiss": True, "when": 0, "whom": 0}]
        k.update(kw)
        s[sid] = k
    src_pc = TPL_PUTCOND
    putcond_skill("S130", src_pc, "Name-Magic", "K003", "Nezumi name-magic: you forget your own name. (Silence)",
                  rate=0.8, dmgrate=[0.5, 0.5], elembits=0)
    putcond_skill("S179", src_pc, "Peck Eyes", "K002", "The crow goes for the eyes. (Blind chance)", rate=0.35,
                  dmgrate=[0.8, 0.8], elembits=0, consume=[0, 0])
    putcond_skill("S180", src_pc, "Lure", "K004", "The soul-flame sways, and you follow it. (Confuse)", rate=0.45,
                  dmgrate=[0.3, 0.3], elembits=0, consume=[0, 0])
    putcond_skill("S182", src_pc, "Venom Fang", "K001", "A mamushi bite. (Poison)", rate=0.5, dmgrate=[0.9, 0.9],
                  elembits=0, consume=[0, 0])
    chg = copy.deepcopy(TPL_PUTCOND)               # Wild Boar: Charge (bestiary B3)
    chg.update({"name": "Charge", "desc": "Head down, tusks first.", "option": [], "elembits": 0,
                "dmgrate": [1.6, 1.8], "hitrate": 0.85, "consume": [0, 0], "enemyuse": True, "addlist": False})
    s["S181"] = chg
    pb = copy.deepcopy(chg)                        # Grey Wolf: Pack Bite (bestiary F; +25% per other wolf alive, plugin)
    pb.update({"name": "Pack Bite", "desc": "The pack closes in. Each wolf still standing makes it worse.",
               "dmgrate": [1.1, 1.2], "hitrate": 0.95})
    s["S402"] = pb
    # Kakita Yasurugi (bosses.md b_boss_yasurugi): the duel strike, Kakita's First Stance, Way of the Crane
    ys = copy.deepcopy(chg)
    ys.update({"name": "Kakita Iaijutsu", "desc": "One draw. You do not see it; you see the sword already back in its "
               "scabbard.", "dmgrate": [1.0, 1.0], "hitrate": 1.0, "hitform": "999", "elembits": B["Katana"],
               "atkform": "dst.PDEF+dst.MAXHP*0.7"})   # dmgrate scales after DEF: a signature blow needs atkform
    s["S403"] = ys
    fs = copy.deepcopy(chg)
    fs.update({"name": "Kakita's First Stance", "desc": "The opening cut of the Kakita school, perfectly made.",
               "dmgrate": [1.0, 1.0], "hitrate": 0.95, "elembits": B["Katana"], "atkform": "dst.PDEF+dst.MAXHP*0.28"})
    s["S404"] = fs
    wc = copy.deepcopy(noop)
    wc.update({"name": "Way of the Crane", "desc": "He settles, and next turn he moves first.", "cmdtgt": 11,
               "enemyuse": True, "addlist": False, "consume": [0, 0]})
    s["S405"] = wc
    putcond_skill("S132", src_pc, "Pocket Sand", "K002", "Squeak's secret weapon. (Blind one enemy)",
                  dmgrate=[0.2, 0.2], elembits=0, consume=[0, 8])
    # Crab Ch2 foes (bosses.md, bestiary.md)
    putcond_skill("S133", src_pc, "No Pure Breaths", "K003", "Maho: the breath stops in your throat. (Silence + "
                  "damage)", rate=0.7, dmgrate=[1.3, 1.3], elembits=0)
    putcond_skill("S134", src_pc, "Veil Lash", "K002", "A strip of veil, snapped like a whip across the eyes.",
                  rate=0.4, dmgrate=[1.1, 1.1], elembits=0)
    putcond_skill("S135", src_pc, "Screech", "K003", "The swarm shrieks. (Silence)", rate=0.5, dmgrate=[0.3, 0.3],
                  elembits=0)
    putcond_skill("S136", src_pc, "Grief Wail", "K007", "A drowned girl's wail. (Terror)", rate=0.5,
                  dmgrate=[0.6, 0.6], elembits=B["Water"])
    putcond_skill("S137", src_pc, "Troll Smash", "K021", "A fist like a falling wall. (ATK down)", rate=0.25,
                  dmgrate=[1.25, 1.25], elembits=0, hitrate=0.85, consume=[0, 0])
    # Shosuro Mitsue: attack denial (user; battle-skills.md). Gates approximate the skill ranks.
    putcond_skill("S140", TPL_PUTCOND, "Poisoned Edge", "K001", "A tanto with something on it. (Poison)", rate=0.6,
                  dmgrate=[0.9, 1.0], elembits=B["Tanto"], consume=[0, 6], enemyuse=False)
    putcond_skill("S141", TPL_PUTCOND, "Metsubishi", "K002", "Blinding powder in every face. (Blind all enemies)",
                  rate=0.6, dmgrate=[0.2, 0.2], elembits=0, consume=[0, 12], cmdtgt=7, enemyuse=False)
    sf = copy.deepcopy(TPL_PUTCOND)
    sf.update({"name": "Shuriken Fan", "desc": "Three throwing stars, low damage each.", "elembits": B["Tanto"],
               "atknum": [3, 3], "dmgrate": [0.45, 0.5], "consume": [0, 8], "option": [], "addlist": True,
               "enemyuse": False})
    s["S142"] = sf
    tb = copy.deepcopy(TPL_PUTCOND)                # Hiruma Goro (story/04 B3 #7)
    tb.update({"name": "Troll-Breaker", "desc": "Goro drops his bent katana and hits with both fists. (Unarmed)",
               "elembits": B["Unarmed"], "dmgrate": [2.2, 2.4], "consume": [0, 10], "option": [], "addlist": True,
               "rt_uses": 2,
               "enemyuse": False})
    s["S139"] = tb
    tb2 = copy.deepcopy(tb)                        # Goro SS2 "The Bent Sword": [UPGRADE Troll-Breaker -> 3 uses; ignores
    tb2.update({"name": "Troll-Breaker", "desc": "The bent katana that has taken every hit. Bent things know how to "
                "take one. (Katana, ignores armour, 3 uses)", "elembits": B["Katana"], "rt_uses": 3,
                "atkform": "src.PATK*rnd(2.0,2.2)*0.8+dst.PDEF"})       # armour] (atk - PDEF: PDEF added back)
    s["S172"] = tb2
    am = copy.deepcopy(s["S111"])                  # Isawa Michio (story/04 B3 #12)
    am.update({"name": "Amaterasu's Fire", "desc": "Sun-fire that burns only the Tainted. (Fire, Jade)",
               "elembits": B["Fire"] | B["Jade"], "atkform": spell_atk(70), "consume": [0, 12], "addlist": True, "rt_uses": 2})
    s["S138"] = am
    rite = copy.deepcopy(s["S035"])
    rite.update({"name": "Egg Rite", "desc": "Ryozo paints a sign on an egg and cracks it over an ally. It works "
                 "because they believe.", "enemyuse": True, "atkform": "60"})
    s["S131"] = rite
    for sid, src, name, bits in (("S107", "S101", "Jade Yari Strike", B["Yari"] | B["Jade"]),
                                 ("S108", "S103", "Jade Tetsubo Strike", B["Tetsubo"] | B["Jade"]),
                                 ("S437", "S102", "Jade Tanto Strike", B["Tanto"] | B["Jade"]),
                                 ("S562", "S100", "Jade Katana Strike", B["Katana"] | B["Jade"]),
                                 ("S563", "S104", "Jade Yumi Shot", B["Yumi"] | B["Jade"])):
        k = copy.deepcopy(s[src])
        k.update({"name": name, "elembits": bits, "desc": "A jade-edged strike. Burns the Tainted."})
        s[sid] = k
    # Guests (Octopath II "Call Guest": battle command "guest", RokuganBattle.sk; uses shared by the party). One per
    # guest: their first signature skill from story/04 B3, uses per battle as listed there.
    def guest_skill(sid, src, name, desc, uses, **kw):
        k = copy.deepcopy(src)
        k.update({"name": name, "desc": desc, "addlist": False, "enemyuse": False, "consume": [0, 0],
                  "eqtypebits": 2047, "rt_uses": uses, "rt_guest": True})
        k.update(kw)
        s[sid] = k
    guest_skill("S143", TPL_PUTCOND, "Kitsu Takeo: Charge", "Takeo rides through the whole enemy line. (Yari, all "
                "enemies)", 2, option=[], cmdtgt=7, elembits=B["Yari"], dmgrate=[1.3, 1.4])
    guest_skill("S144", s["S123"], "Yogo Mai: Ward", "Mai's ofuda over the party: DEF up.", 2,
                putconds=COND_BIT("K022"))
    guest_skill("S145", TPL_PUTCOND, "Ide Fujio: Scandalous Letter", "A letter about the enemy, read aloud. It "
                "loses its actions while it recovers. (Scandalized)", 1, elembits=0, dmgrate=[0.1, 0.1],
                option=[{"condid": "K025", "efx_start": None, "opttype": "opt_putcond", "rate": 1.0,
                         "showmiss": True, "when": 0, "whom": 0}])
    # Crane Ch1 guests (story/04 B3 #19-20; G-1: one active guest)
    guest_skill("S400", s["S122"], "Kitsuki Seigen: Evidence", "Seigen reads the scene: every enemy's weaknesses, and "
                "what each one is about to do.", 2, cmdtgt=7, dmgrate=[0.0, 0.0])
    guest_skill("S401", TPL_PUTCOND, "Matsu Kiku: Battle-Joy", "Kiku stops trying not to hit anyone. One enormous "
                "blow with the pilgrim's staff. (Bo)", 1, option=[], elembits=B["Bo"], dmgrate=[3.0, 3.2])
    gr = copy.deepcopy(s["S139"])                  # Crane Ch2 end: Goro answers the Call (story/04 #7 guest)
    gr.update({"name": "Hiruma Goro: Troll-Breaker", "desc": "Goro drops his bent katana and hits with both fists. "
               "(Unarmed)", "addlist": False, "consume": [0, 0], "eqtypebits": 2047, "rt_uses": 2, "rt_guest": True})
    s["S406"] = gr
    guest_skill("S146", s["S123"], "Daidoji Sakura: Blank Scroll", "Sakura raises a blank scroll against the kami: "
                "party E.DEF up. (Void Guard)", 2, putconds=COND_BIT("K024"))
    # Crab Ch3 (production/crab-ch3.md, bosses.md b_boss_kommei)
    ls = copy.deepcopy(TPL_PUTCOND)               # Gonta (Ch3 companion if hidden_ones_cleared): Landslide
    ls.update({"name": "Landslide", "desc": "Gonta brings the hillside down on every enemy. (Earth)", "option": [],
               "cmdtgt": 7, "elembits": B["Earth"], "dmgrate": [1.5, 1.6], "consume": [0, 0], "rt_uses": 1,
               "addlist": True, "enemyuse": False})
    s["S147"] = ls
    bz = copy.deepcopy(TPL_PUTCOND)               # Hiruma Kage (the boss, if he fights): Berserk Smash
    bz.update({"name": "Berserk Smash", "desc": "Grief with a tetsubo in it. (Tetsubo)", "option": [],
               "elembits": B["Tetsubo"], "dmgrate": [1.5, 1.6], "consume": [0, 0], "rt_uses": 1, "addlist": True,
               "enemyuse": False})
    s["S148"] = bz
    tf = copy.deepcopy(TPL_PUTCOND)
    tf.update({"name": "Two-Faced Strike", "desc": "Both faces bite.", "option": [], "atknum": [2, 2],
               "dmgrate": [0.75, 0.8], "elembits": 0, "consume": [0, 0], "enemyuse": True})
    s["S149"] = tf
    putcond_skill("S150", src_pc, "Command the Taint", "K026", "The oni calls to the Shadowlands in your blood. "
                  "(Taint +1 to all)", rate=0.8, dmgrate=[1.0, 1.0], elembits=0, cmdtgt=7, consume=[0, 0],
                  atkform="dst.PDEF+30+src.PATK*0.4")       # always lands (light damage), so the Taint roll happens
    putcond_skill("S151", src_pc, "Poppy Dust", "K005", "A puff of red pollen. (Sleep)", rate=0.5,
                  dmgrate=[0.3, 0.3], elembits=0, consume=[0, 0])
    putcond_skill("S152", src_pc, "Grave Grip", "K021", "Cold fingers that don't let go. (ATK down)", rate=0.4,
                  dmgrate=[0.9, 0.9], elembits=0, consume=[0, 0])
    sc3 = copy.deepcopy(TPL_PUTCOND)
    sc3.update({"name": "Shadow Charge", "desc": "A demon horse comes out of its own shadow.", "option": [],
                "dmgrate": [1.3, 1.35], "elembits": 0, "consume": [0, 0], "enemyuse": True})
    s["S153"] = sc3
    spell_skills(s)
    sp_ids = {sp["name"]: sp["skill"] for sp in json.load(open(os.path.join(DATA, "rt_spells.json"), encoding="utf-8"))}
    for nm in ("Courage of the Seven Thunders", "Stillness of the Void"):          # (Courage did nothing before:
        if nm in sp_ids:                                                           # "immune" matched no condition)
            s[sp_ids[nm]].update({"putconds": 0, "option": [PUT_BY_ID("K058")], "remconds": 1 << 7})   # (+ cures Terror)
    if "Return the Soul" in sp_ids:                                                # the revive: the engine's Raise
        k = s[sp_ids["Return the Soul"]]                                           # (S043: cures Down, % of max HP)
        k.update({"remconds": 1, "dmgform": 2, "atkform": "50", "flags": s["S043"].get("flags", k.get("flags"))})
    # Hireables (tools/hirelings.py): one powered-up action each, called by a traveler ("Call"). Power follows the
    # area's expected level (hirelings.py lv), not the caller's. The skill also carries the roster for the plugin.
    def hire_skill(h, src, desc, **kw):
        k = copy.deepcopy(src)
        k.update({"name": "%s: %s" % (h["name"], kw.pop("act")), "desc": desc, "addlist": False, "enemyuse": False,
                  "consume": [0, 0], "eqtypebits": 2047, "rt_hire": h["n"], "rt_hname": h["name"],
                  "rt_hmdl": _sc_epid(h["key"]), "rt_hcharges": h["charges"], "rt_hhome": h["home"]})
        if "atkform" in kw:                                  # the area's level, not the caller's (hirelings.py)
            kw["atkform"] = kw["atkform"].replace("src.LV", str(h["lv"]))
        k.update(kw)
        s[h["sid"]] = k
    H = _hire.BY_N
    hire_skill(H[1], TPL_PUTCOND, "A volley from the back row onto every enemy. Arrows don't care about armour. (Yumi, "
               "all enemies)", act="Arrow Volley", option=[], cmdtgt=7, elembits=B["Yumi"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF+20+src.LV*4.5")
    hire_skill(H[2], TPL_PUTCOND, "Earth Becomes Sky: the earth kami fling a boulder that never misses and ignores half "
               "its armour, and knock it Prone (DEF down; a Prone foe takes double). Void 2+ (two Raises): Earth "
               "Becomes Jade, a jade boulder. (Earth)", act="Earth Becomes Sky", cmdtgt=1, elembits=B["Earth"],
               dmgrate=[1.0, 1.0], hitform="999", rt_jade_raise=True,
               atkform='dst.PDEF*0.5+(60+src.LV*11)*(dst.hasCondition("K029")?2.0:1.0)',
               option=[{"condid": "K029", "efx_start": None, "opttype": "opt_putcond", "rate": 1.0,
                        "showmiss": False, "when": 0, "whom": 0}])
    hire_skill(H[3], s["S123"], "Timber and rope, up in a breath: a barricade in front of the party. (DEF and E.DEF "
               "up, all allies)", act="Barricade", putconds=COND_BIT("K022") | COND_BIT("K024"))
    hire_skill(H[4], s["S300"], "Ginseng tea for everyone, and none of it optional. (Heal all allies, cure Poison)",
               act="Ginseng Tea", cmdtgt=11, atkform="dst.MAXHP*0.3+src.LV*2.0", remconds=COND_BIT("K001"))
    hire_skill(H[5], TPL_PUTCOND, "A weighted net over one enemy: it spends its next turn getting out. (Netted)",
               act="Throw Net", elembits=0, dmgrate=[1.0, 1.0], atkform="dst.PDEF+10+src.LV*1.0",
               option=[{"condid": "K028", "efx_start": None, "opttype": "opt_putcond", "rate": 1.0,
                        "showmiss": True, "when": 0, "whom": 0}])
    hire_skill(H[7], TPL_PUTCOND, "Gonta brings the hillside down on every enemy. (Earth, all enemies)",
               act="Landslide", option=[], cmdtgt=7, elembits=B["Earth"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF*0.4+30+src.LV*6.5")
    hire_skill(H[8], TPL_PUTCOND, "Jade-tipped arrows from the back row into every enemy. (Yumi, Jade, all enemies)",
               act="Jade Arrows", option=[], cmdtgt=7, elembits=B["Yumi"] | B["Jade"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF+15+src.LV*4.0")
    hire_skill(H[9], s["S300"], "Ofuda and jade water: the Taint burns out of the whole party, and the wounds close a "
               "little. (Cure Taint and Poison, heal all allies)", act="Purify", cmdtgt=11,
               atkform="dst.MAXHP*0.25+src.LV*2.0", remconds=COND_BIT("K026") | COND_BIT("K001"))
    hire_skill(H[10], TPL_PUTCOND, "A siege roller off the yard stair onto one enemy: it ends up flat. (Tetsubo, "
               "knocks it Prone)", act="Trap Roller", elembits=B["Tetsubo"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF*0.3+70+src.LV*12",
               option=[{"condid": "K029", "efx_start": None, "opttype": "opt_putcond", "rate": 1.0,
                        "showmiss": False, "when": 0, "whom": 0}])
    hire_skill(H[6], TPL_PUTCOND, "Thirty years of Wall in one swing. Armour helps a little. (Tetsubo, one enemy)",
               act="Tetsubo Smash", option=[], elembits=B["Tetsubo"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF*0.3+80+src.LV*14")
    # Crane Ch1 (Pleasant Eaves, the Green Ronin's village): recruited by Rensei's Charm or for zeni
    hire_skill(H[11], s["S300"], "The old woman's prayer for the Green Ronin, said over all of you. (Heal all allies)",
               act="Green Ronin's Blessing", cmdtgt=11, atkform="dst.MAXHP*0.25+src.LV*2.0")
    hire_skill(H[12], TPL_PUTCOND, "A hungry man's cut: everything in one swing, aim be damned. (Katana, one enemy)",
               act="Desperate Cut", option=[], elembits=B["Katana"], dmgrate=[1.0, 1.0], hitrate=0.85,
               atkform="dst.PDEF*0.3+60+src.LV*12")
    hire_skill(H[13], TPL_PUTCOND, "Paper lanterns swing out of the dark on their pulley ropes. Eyes follow them. "
               "(Blind chance, all enemies)", act="Lantern Lure", cmdtgt=7, elembits=0, dmgrate=[0.2, 0.2],
               atkform="dst.PDEF+10+src.LV*1.0",
               option=[{"condid": "K002", "efx_start": None, "opttype": "opt_putcond", "rate": 0.6,
                        "showmiss": True, "when": 0, "whom": 0}])
    # Crane Ch2 (Garden Under Shadow): a Yari for Miyako's generals (weak to Yari), and the Suitengu priest
    hire_skill(H[14], TPL_PUTCOND, "A boarding pike, swung like the deck is pitching. Daidoji generals hate it. (Yari, "
               "one enemy)", act="Boarding Pike", option=[], elembits=B["Yari"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF*0.3+60+src.LV*9")
    hire_skill(H[15], s["S300"], "Suitengu's tide washes over the party: wounds close, poison rinses away. (Heal all "
               "allies, cure Poison; Water)", act="Tide Blessing", cmdtgt=11, atkform="dst.MAXHP*0.22+src.LV*2.0",
               remconds=COND_BIT("K001"))
    # Crane Ch3 (the Crane port): the counters to Chihaya's evasion charm (weak Yumi, Air)
    hire_skill(H[16], TPL_PUTCOND, "Two daikyu shafts from the back row. A Tsuruchi arrow never misses, charm or no "
               "charm. (Yumi x2, one enemy)", act="Daikyu Shot", option=[], elembits=B["Yumi"], dmgrate=[1.0, 1.0],
               hitrate=1.0, hitform="999", atknum=[2, 2], atkform="dst.PDEF*0.3+50+src.LV*7")
    hire_skill(H[17], TPL_PUTCOND, "Two hard gusts across the whole enemy line. (Air x2, all enemies)",
               act="Storm Gust", option=[], cmdtgt=7, elembits=B["Air"], dmgrate=[1.0, 1.0], atknum=[2, 2],
               atkform="dst.PDEF+15+src.LV*2.6")
    # Crab Ch4 (bosses.md b_boss_tsukakoro; bestiary IV wolf-rider)
    bc = copy.deepcopy(TPL_PUTCOND)
    bc.update({"name": "Bounce Chain", "desc": "The bone-cage bounces from one traveler to the next.", "option": [],
               "dmgrate": [0.85, 0.9], "elembits": 0, "consume": [0, 0], "enemyuse": True})
    s["S160"] = bc                                       # the chain itself: plugin RokuganHazard (2-4 hits in a row)
    putcond_skill("S161", src_pc, "Rattle", "K007", "Every bone in the cage rattles at once. (Terror, all)", rate=0.5,
                  dmgrate=[1.0, 1.0], elembits=0, cmdtgt=7, consume=[0, 0], atkform="dst.PDEF+15+src.PATK*0.25")
    wl = copy.deepcopy(TPL_PUTCOND)
    wl.update({"name": "Wolf Lunge", "desc": "The wolf leaps; the goblin stabs on the way down.", "option": [],
               "dmgrate": [1.3, 1.35], "elembits": 0, "consume": [0, 0], "enemyuse": True})
    s["S162"] = wl
    jt = copy.deepcopy(s["S102"])
    jt.update({"name": "Jade Tanto Strike", "elembits": B["Tanto"] | B["Jade"], "desc": "A jade-inlaid blade."})
    s["S163"] = jt
    # Squeak's memory sticks (Enemies of the Empire, "Rememberers and Memory Sticks" p.113-117, and the shaman's Mend
    # Name p.120; user: "name magic sticks, HIGH mp cost... a heal or buff, not a shugenja"). Any nezumi can use a
    # stick, so the power comes from the story chewed into it: heals scale with the target and Squeak's level, not MATK.
    def stick(sid, src, name, desc, sp, **kw):
        k = copy.deepcopy(s[src])
        k.update({"name": name, "desc": desc, "consume": [0, sp], "addlist": True, "enemyuse": False,
                  "occasion": 3})                       # (user 2026-11-12: doubled, Squeak couldn't afford them)
        k.update(kw)
        s[sid] = k
    stick("S154", "S300", "Mend-Name Stick", "A shaman's mending, chewed into a stick: a wounded Name returns to its "
          "rightful form. (Heal one ally)", 14, atkform="dst.MAXHP*0.35+src.LV*2.0")
    stick("S155", "S305", "Armor Stick", "The tale of the Nezumi's friendship with the Crab: an ally fights as if in "
          "heavy armour. (DEF up)", 16, putconds=COND_BIT("K022"))
    stick("S156", "S305", "Warrior's Stick", "The tale of a mighty warrior, sharpened at one end. (ATK up, one ally)",
          16, putconds=COND_BIT("K020"))
    stick("S157", "S300", "Sunlit Stick", "The tale of a hero who never lost his way: every eye sees clearly. (Cure "
          "Blind, all allies)", 14, cmdtgt=11, atkform="dst.MAXHP*0.05", remconds=COND_BIT("K002"))
    stick("S158", "S300", "Life Stick", "The tale of a wounded warrior who prevailed against all odds; the wood stays "
          "green while it works. (Big heal + cure Poison, one ally)", 40, atkform="dst.MAXHP*0.7+src.LV*3.0",
          remconds=COND_BIT("K001"))
    mdnm = copy.deepcopy(s["S123"])                 # Hida Sachiko: Hida Bushi R2 (3e core, docs/rules/schools.md)
    mdnm.update({"name": "The Mountain Does Not Move", "desc": "Hida Bushi technique: she braces and turns the blow "
                 "onto bone and armour. Damage taken halved for 2 turns.", "cmdtgt": 13, "consume": [0, 16],
                 "putconds": COND_BIT("K027"), "addlist": True, "enemyuse": False, "occasion": 1,
                 "rt_guard": "K027"})
    s["S169"] = mdnm
    stick("S159", "S123", "Evil Stick", "The Terrible Day When Air Became Fire, told in the darkest wood: Tainted "
          "things find it hard to harm the party. (DEF + E.DEF up, all allies)", 48,
          putconds=COND_BIT("K022") | COND_BIT("K024"), addlist=True)
    # Minion tricks (user: "minions should have tricks to keep the bosses alive"): RokuganHazard aims every skill
    # flagged rt_minion at the boss of the fight (or the most wounded ally when there is no boss)
    def minion(sid, src, name, desc, **kw):
        k = copy.deepcopy(s[src])
        k.update({"name": name, "desc": desc, "enemyuse": True, "addlist": False, "consume": [0, 0], "rt_minion": True})
        k.update(kw)
        s[sid] = k
    minion("S164", "S300", "Blood Ward", "A maho-bujin opens its own palm and feeds its master.",
           atkform="dst.MAXHP*0.06")
    minion("S165", "S305", "Shield the Master", "Blood-sigils over the master's armour. (DEF up)",
           putconds=COND_BIT("K022"))
    minion("S166", "S305", "War Chant", "A goblin war-song: the big one hits harder. (ATK up)", putconds=COND_BIT("K020"))
    minion("S167", "S300", "Grave Feast", "The dead feed what rides them.", atkform="dst.MAXHP*0.05")
    s["S047"].update({"name": "War Cry", "desc": "A goblin howl. It hits harder for a while. (ATK up)"})   # the sample
    # skill kept its Japanese name; the Goblin Warmongers (E230, E240) use it
    minion("S168", "S300", "Rally", "Nezumi chitter round the shaman and lend it their names.", atkform="dst.MAXHP*0.06")
    # Crane Ch3 "The White Squid" (bestiary A5/B5, bosses.md b_midboss_chihaya / b_storm_yosuke / b_boss_katsuo)
    def blow(sid, name, desc, **kw):
        k = copy.deepcopy(chg)
        k.update({"name": name, "desc": desc})
        k.update(kw)
        s[sid] = k
    blow("S407", "Boarding Hook", "A grappling hook on a rope, swung like a flail.", dmgrate=[1.3, 1.4], hitrate=0.9)
    blow("S408", "Strike of the Cliff's Edge", "A Mantis kata thrown from range, all shoulder.", dmgrate=[1.5, 1.6],
         hitrate=0.9, elembits=B["Air"])
    putcond_skill("S409", src_pc, "Electric Coil", "K052", "The eel wraps and shocks. (Shocked: loses a turn)", rate=0.3,
                  dmgrate=[1.0, 1.0], elembits=0, consume=[0, 0])
    putcond_skill("S410", src_pc, "Wave Wall", "K051", "A black wave over the whole deck. (Speed down, all)", rate=0.6,
                  dmgrate=[0.6, 0.6], elembits=B["Water"], cmdtgt=7, consume=[0, 0])
    blow("S411", "Oar Dance", "Chihaya runs along an oar and kicks you twice on the way past.", dmgrate=[0.75, 0.75],
         hitrate=1.0, atknum=[2, 2])
    rc = copy.deepcopy(s["S305"])
    rc.update({"name": "Rally the Crew", "desc": "Yosuke roars into the storm, and his crew stand to the rail. (DEF up, "
               "all allies)", "cmdtgt": 11, "putconds": COND_BIT("K022"), "enemyuse": True, "addlist": False,
               "consume": [0, 0]})
    s["S412"] = rc
    blow("S413", "Captain's Cut", "A huge overhead cut, thrown like a man who has never lost a deck.",
         dmgrate=[1.0, 1.0], hitrate=0.95, elembits=B["Katana"], atkform="dst.PDEF+dst.MAXHP*0.18")
    putcond_skill("S414", src_pc, "Blood Ink", "K026", "Maho: Katsuo cuts his palm and flicks the ink. (Taint; he "
                  "pays 5% HP)", rate=0.6, dmgrate=[1.2, 1.2], elembits=0, consume=[0, 0], rt_maho=5)
    blow("S415", "Nunchaku Flurry", "Stick, chain, stick: three blows before the first one lands.",
         dmgrate=[0.55, 0.55], hitrate=0.95, atknum=[3, 3], elembits=B["Bo"])
    minion("S416", "S305", "Cover the Brother", "Ryohei steps in front of Katsuo. (DEF up)", putconds=COND_BIT("K022"))
    # Crane Ch4 "The Play No One Performs" (bestiary D tsukumogami; bosses.md b_archive_guardian, b_boss_masanori)
    putcond_skill("S417", src_pc, "Paper Cut", "K055", "A thousand edges at once. (Bleeding)", rate=0.3,
                  dmgrate=[0.9, 0.9], elembits=0, consume=[0, 0])
    putcond_skill("S418", src_pc, "Ink Splash", "K002", "A face full of four-hundred-year-old ink. (Blind)", rate=0.3,
                  dmgrate=[0.8, 0.8], elembits=B["Water"], consume=[0, 0])
    putcond_skill("S419", src_pc, "Lick", "K054", "A long red tongue, very wet. (Dazed)", rate=0.4, dmgrate=[0.5, 0.5],
                  elembits=0, consume=[0, 0])
    putcond_skill("S420", src_pc, "Flare", "K021", "The lantern flares white. (ATK down, all)", rate=0.3,
                  dmgrate=[0.5, 0.5], elembits=B["Fire"], cmdtgt=7, consume=[0, 0])
    putcond_skill("S421", src_pc, "Ancestor's Rebuke", "K021", "A Doji ancestor's cold disapproval, all at once. "
                  "(Void; ATK down, all)", rate=0.4, dmgrate=[0.8, 0.8], elembits=B["Void"], cmdtgt=7, consume=[0, 0])
    putcond_skill("S422", src_pc, "Seal the Shelf", "K003", "Wards flare along the shelves. (Silence)", rate=0.6,
                  dmgrate=[0.6, 0.6], elembits=0, consume=[0, 0])
    blow("S423", "Kakita Iaijutsu", "His father's draw. You have watched it all your life and never once seen it.",
         dmgrate=[1.0, 1.0], hitrate=1.0, hitform="999", elembits=B["Katana"], atkform="dst.PDEF+dst.MAXHP*0.35")
    blow("S424", "Kakita's First Stance", "The opening cut of the school, made by a man who teaches it.",
         dmgrate=[1.0, 1.0], hitrate=0.95, elembits=B["Katana"], atkform="dst.PDEF+dst.MAXHP*0.16")
    wf = copy.deepcopy(s["S305"])
    wf.update({"name": "Watchful Falcon", "desc": "He settles, and watches. (Accuracy and critical hits up)",
               "cmdtgt": 13, "putconds": 0, "enemyuse": True, "addlist": False, "consume": [0, 0],
               "option": [PUT_BY_ID("K053")]})    # by id: putconds bits above ~50 don't survive the engine
    s["S425"] = wf
    rf = copy.deepcopy(wf)                             # Rensei's kata (kata.md Kakita 2, Lv 25): the same falcon's eye
    rf.update({"desc": "Kakita kata: the falcon's eye. Accuracy and critical hits up for 3 turns.", "enemyuse": False,
               "addlist": True, "consume": [0, 12], "occasion": 1})
    s["S426"] = rf
    hire_skill(H[18], TPL_PUTCOND, "A verse of reproach, read aloud to every enemy. Sword arms forget themselves. "
               "(ATK down, all enemies)", act="Verse of Reproach", cmdtgt=7, elembits=0, dmgrate=[0.2, 0.2],
               atkform="dst.PDEF+10+src.LV*1.0",
               option=[{"condid": "K021", "efx_start": None, "opttype": "opt_putcond", "rate": 0.9,
                        "showmiss": True, "when": 0, "whom": 0}])
    # Lion Ch1 (Hiruto's castle town): a spear, and a Kitsu acolyte's prayer
    hire_skill(H[20], TPL_PUTCOND, "An ashigaru's thrust from the second rank. (Yari, one enemy)", act="Spear Thrust",
               option=[], elembits=B["Yari"], dmgrate=[1.0, 1.0], atkform="dst.PDEF*0.3+40+src.LV*10")
    hire_skill(H[21], s["S300"], "A Kitsu prayer over the party's wounds. (Heal all allies)", act="Ancestor's Prayer",
               cmdtgt=11, atkform="dst.MAXHP*0.25+src.LV*2.0")
    # Lion Ch1 guests (G-1: one at a time): Akodo Ijako (S03a) and Shiba Ashimita (after the S04 Duel)
    guest_skill("S429", TPL_PUTCOND, "Akodo Ijako: Call the Dead", "Ijako lifts her mask, and an Akodo ancestor "
                "strikes through her. (Void, one enemy)", 1, option=[], elembits=B["Void"], dmgrate=[1.0, 1.0],
                atkform="dst.PDEF+60+src.LV*14")
    guest_skill("S430", TPL_PUTCOND, "Shiba Ashimita: Yojimbo's Cut", "Ashimita steps in front of the party and "
                "cuts. His grandfather screams the whole time. (Katana, one enemy)", 2, option=[],
                elembits=B["Katana"], dmgrate=[1.0, 1.0], atkform="dst.PDEF*0.5+40+src.LV*10")
    gb = copy.deepcopy(s["S305"])                       # Lion Ch2 guest: Moto Benjiro's Death Trance (party: no
    gb.update({"name": "Moto Benjiro: Death Trance", "desc": "Benjiro paints the death-mask on every face. Nobody "  # fear,
               "fears, nobody is charmed, for a round. (Party: immune to Terror and charm)", "cmdtgt": 11,  # no charm)
               "putconds": 0, "option": [PUT_BY_ID("K056")], "addlist": False, "enemyuse": False, "consume": [0, 0],
               "rt_uses": 2, "rt_guest": True, "eqtypebits": 2047})   # by id (bit 56 decoded as Down: DEFEATED)
    s["S439"] = gb
    gb = copy.deepcopy(gb)                              # Benjiro SS2 "The Moto Curse": [UPGRADE Death Trance -> more
    gb.update({"desc": "Benjiro paints the death-mask on every face - and leaves his own bare. Nobody fears, nobody is "
               "charmed, for a round. (Party: immune to Terror and charm; 3 uses)", "rt_uses": 3})   # uses] (G1214)
    s["S634"] = gb
    fw = copy.deepcopy(s["S305"])                       # Akodo Shogen: Fury Without End (the stance: ATK up)
    fw.update({"name": "Fury Without End", "desc": "Pain is a rumour. Ignore it. (ATK up)", "cmdtgt": 13,
               "putconds": COND_BIT("K020"), "enemyuse": True, "addlist": False, "consume": [0, 0]})
    s["S445"] = fw
    blow("S446", "Seppun Iaijutsu", "A long perfect blade, drawn once.", dmgrate=[1.0, 1.0], hitrate=0.95,
         elembits=B["Katana"], atkform="dst.PDEF+dst.MAXHP*0.12")
    putcond_skill("S447", src_pc, "Volley from the Rocks", "K021", "Arrows from above, all at once. (all; ATK down)",
                  rate=0.1, dmgrate=[0.45, 0.45], elembits=B["Yumi"], cmdtgt=7, consume=[0, 0])
    putcond_skill("S449", src_pc, "Terror Aura", "K007", "Both armies cower. \"Run. Everyone runs from Sorrow's "
                  "Path eventually.\" (all; Terror)", rate=0.4, dmgrate=[0.3, 0.3], elembits=0, cmdtgt=7,
                  consume=[0, 0])
    # Togashi Yosai's tattoos (kiho.md: Dragon - fire breath that burns him too; Arrowroot - heal an ally, he takes
    # the wounds). rt_selfburn = the share of his max HP it costs him (plugin); his regeneration pays it back.
    blow("S460", "Dragon's Breath", "The dragon tattoo breathes fire across the enemy line. It burns Yosai too. "
         "(Fire, all enemies; costs 10% of his HP)", dmgrate=[0.9, 0.9], hitrate=1.0, elembits=B["Fire"], cmdtgt=7,
         consume=[0, 8], addlist=True, enemyuse=False, eqtypebits=2047, rt_selfburn=0.10)
    ar_k = copy.deepcopy(s["S300"])
    ar_k.update({"name": "Arrowroot", "desc": "The arrowroot tattoo draws an ally's wounds into Yosai's own skin. (Heal one "
                 "ally, more as he levels, but never more than half their HP; costs 15% of his HP)", "cmdtgt": 8, "consume": [0, 6], "addlist": True,
                 "enemyuse": False, "eqtypebits": 2047, "atkform": "dst.MAXHP*0.6+src.LV*8.0", "rt_selfburn": 0.15})
    # (user: twice the old dst.MAXHP*0.4+src.LV*2.0 heal, scaling with his level; the HP cost unchanged)
    s["S461"] = ar_k
    putcond_skill("S462", src_pc, "Blood Bolt (maho)", "K026", "\"My blood - for power - gladly - less gladly.\" "
                  "Maho paid in his own blood. (Taint chance; costs him 3% of his HP)", rate=0.3, dmgrate=[1.1, 1.1],
                  elembits=0, consume=[0, 0], rt_selfburn=0.03)
    blow("S463", "Painted Frenzy", "A cultist hurls himself forward, chanting.", dmgrate=[1.3, 1.4], hitrate=0.85)
    putcond_skill("S476", src_pc, "Interrogate", "K021", "Gendo questions a human foe mid-fight: reveals its "
                  "weaknesses, and it fears being seen through (ATK down). A hypnotised foe stops fighting.",
                  rate=0.8, dmgrate=[0.3, 0.3], elembits=0, consume=[0, 4], rt_interrogate=True, enemyuse=False)
    guest_skill("S478", TPL_PUTCOND, "Kitsuki Momo: Perfect Recall", "Momo remembers every detail of the foe, the "
                "way she remembers plums. Its weaknesses are revealed. (one enemy)", 2, option=[], elembits=0,
                dmgrate=[0.2, 0.2], rt_interrogate=True)
    # Dragon Ch2: Gendo's Subdue (G740), the Bow (G757) and the Mirumoto school's Daisho Technique (G742)
    putcond_skill("S481", src_pc, "Daisho Technique", "K000", "Mirumoto school, Rank 1: two blades, two truths. One "
                  "hand states, the other checks. (Katana, 2 hits; answers an iaijutsu draw)", rate=0.0,
                  option=[], atknum=[2, 2], dmgrate=[0.8, 0.8], elembits=B["Katana"], consume=[0, 6],
                  rt_daisho=True, enemyuse=False)
    putcond_skill("S482", src_pc, "Subdue", "K000", "A Bo strike to the wrist: meant to disarm, not to kill. (Bo, "
                  "light; it ends a fight with a man who wants to die)", rate=0.0, option=[], dmgrate=[0.5, 0.5],
                  elembits=B["Bo"], consume=[0, 4], rt_subdue=True, enemyuse=False)
    putcond_skill("S483", src_pc, "Bow", "K000", "A deep, correct bow. A kappa must bow back, and spills the water "
                  "from its head-dish (Suki). Nothing else is impressed.", rate=0.0, option=[], dmgrate=[0.0, 0.0],
                  elembits=0, consume=[0, 0], rt_bow=True, enemyuse=False)
    blow("S484", "Ushimo's Draw", "Seppun iaijutsu, perfect, drawn once at the nearest man.", dmgrate=[1.0, 1.0],
         hitrate=1.0, elembits=B["Katana"], atkform="dst.PDEF+dst.MAXHP*0.3")
    blow("S485", "Seppun Guard's Cut", "The cut the Seppun teach to men who stand in front of Emperors.",
         dmgrate=[1.25, 1.3], hitrate=0.95, elembits=B["Katana"])
    putcond_skill("S486", src_pc, "Drag Under", "K051", "The kappa grabs an ankle and pulls for the water. (Grapple: "
                  "Speed down)", rate=0.5, dmgrate=[1.0, 1.0], elembits=B["Water"], consume=[0, 0])
    # Dragon Ch3: Seppun Ushimo (P134, companion after tsuhime_helped), the gaijin, Akuro, the vanguard captain
    blow("S489", "Seppun Draw", "Ushimo's iaijutsu, drawn now for someone else's sake. (Katana, one enemy)",
         dmgrate=[0.65, 0.7], hitrate=1.0, elembits=B["Katana"], consume=[0, 8], addlist=True, enemyuse=False,
         eqtypebits=2047)
    blow("S490", "Wasp Sting", "The Wasp tattoo: two blows where there should be one.", dmgrate=[0.55, 0.55],
         hitrate=1.0, atknum=[2, 2])
    blow("S491", "Volley", "A crack, a cloud of white smoke, and lead.", dmgrate=[1.1, 1.15], hitrate=0.8,
         elembits=B["Yumi"])
    rc2 = copy.deepcopy(s["S412"])
    rc2.update({"name": "Pike Wall", "desc": "The pikes come down in a hedge. (DEF up, all allies)"})
    s["S492"] = rc2
    blow("S493", "Broadsword Cleave", "A foreign sword, heavy and straight, swung like an axe.", dmgrate=[1.3, 1.4],
         hitrate=0.95, elembits=B["Katana"], atkform="dst.PDEF+dst.MAXHP*0.1")
    # Dragon Ch4: Kumpei's living ink, the marines' rush, Sanro's ward-fire (P135, the lighthouse escort)
    blow("S496", "Living Ink", "A brush-stroke that leaves the silk and keeps going. (Water)", dmgrate=[1.2, 1.3],
         hitrate=1.0, elembits=B["Water"])
    blow("S498", "Boarding Rush", "Axes first, questions never.", dmgrate=[1.3, 1.35], hitrate=0.9)
    # Scorpion Ch1 "Blood and Iron": Yoritomo Rui (P136, from S05), the Kommei brood, the leeches, Kansen-Hana
    blow("S506", "Storm Heart", "Yoritomo courtiers learn to stand in a storm. Rui throws one. (Air, one enemy)",
         dmgrate=[1.0, 1.0], hitrate=1.0, elembits=B["Air"], consume=[0, 6], addlist=True, enemyuse=False,
         eqtypebits=2047, atkform="dst.PDEF+30+src.PATK*1.1")
    blow("S507", "Kama Flurry", "Two hooked cuts, low and high. (Tanto x2, one enemy)", dmgrate=[0.6, 0.65],
         hitrate=0.95, atknum=[2, 2], elembits=B["Tanto"], consume=[0, 4], addlist=True, enemyuse=False,
         eqtypebits=2047)
    putcond_skill("S508", src_pc, "Drain", "K026", "The leech latches on and drinks. (Taint chance)", rate=0.15,
                  dmgrate=[0.9, 0.9], elembits=0, consume=[0, 0])
    putcond_skill("S509", src_pc, "Spirit Leeching", "K007", "Yellow fog from the oni's mouth. Breathe it and you "
                  "forget who you are. (Terror chance)", rate=0.4, dmgrate=[1.0, 1.0], elembits=0, consume=[0, 0])
    putcond_skill("S510", src_pc, "Choking Death", "K003", "Maho: the air in your throat turns to wool. (Air; "
                  "Silence chance)", rate=0.35, dmgrate=[1.1, 1.1], elembits=B["Air"], consume=[0, 0])
    putcond_skill("S511", src_pc, "Drain Soul", "K026", "Maho: something in the box drinks. (Taint chance)",
                  rate=0.3, dmgrate=[1.3, 1.3], elembits=0, consume=[0, 0])
    # Scorpion Ch2 "City of Masks": stitched monks, the plains (python, hornet), Doji Siko, Abbot Munashii
    # Scorpion Ch3 = Unicorn Ch2: the Iuchi hit squad (meishodo: one-round spells), Akodo Rin's guard
    blow("S523", "Katana of Fire", "A blade of fire bursts from the shugenja's hand, roaring like a forge. (Fire)",
         dmgrate=[1.2, 1.3], hitrate=0.95, elembits=B["Fire"])
    putcond_skill("S524", src_pc, "Suitengu's Embrace", "K051", "Sea water fills your lungs from nowhere. (Water; "
                  "Slowed)", rate=0.5, dmgrate=[1.0, 1.0], elembits=B["Water"], consume=[0, 0])
    sm = copy.deepcopy(s["S123"])
    sm.update({"name": "Sharing the Strength of Many", "desc": "An amulet twisted, and the squad grows strong. (ATK "
               "up, all allies)", "cmdtgt": 11, "putconds": COND_BIT("K020"), "enemyuse": True, "addlist": False,
               "consume": [0, 0]})
    s["S525"] = sm
    cv = copy.deepcopy(s["S123"])
    cv.update({"name": "Cover", "desc": "Rin steps in front of an ally: every enemy blow comes to her for two turns.",
               "cmdtgt": 11, "putconds": 0, "enemyuse": False, "addlist": True, "consume": [0, 6],
               "eqtypebits": 2047})
    s["S526"] = cv
    cp = copy.deepcopy(s["S123"])
    cp.update({"name": "The Clouds Part", "desc": "An Akodo war-shout: ATK up, and the whole party acts first next "
               "turn.", "enemyuse": False, "addlist": True, "consume": [0, 10], "eqtypebits": 2047})
    s["S527"] = cp
    # Scorpion Ch4 "The Eve": the Dragon mountains and Tamori's Furnace (bestiary rows), the Bloodspeaker remnant
    # (bosses.md b_boss_stolen_face: maho, Taint on hit; the face-steal is the plugin's rt_stolenface)
    blow("S530", "Flare", "The elemental flares white-hot across the whole party. (Fire, all)", dmgrate=[0.6, 0.65],
         hitrate=1.0, elembits=B["Fire"], cmdtgt=7)
    putcond_skill("S531", src_pc, "Crushing Hug", "K051", "The bear rears and squeezes. Your ribs creak. (Slowed)",
                  rate=0.5, dmgrate=[1.2, 1.25], elembits=0, consume=[0, 0])
    blow("S532", "Feather Blade", "A crow-warrior's sword, too fast to see. Black feathers in the air after. (Katana)",
         dmgrate=[1.3, 1.35], hitrate=0.95, elembits=B["Katana"])
    putcond_skill("S533", src_pc, "Moon Howl", "K007", "A howl from somewhere that isn't the mountain. (all; Terror)",
                  rate=0.4, dmgrate=[0.3, 0.3], elembits=0, cmdtgt=7, consume=[0, 0])
    putcond_skill("S534", src_pc, "Choking Ash", "K002", "A handful of hot ash, flung in your eyes. (Blind)", rate=0.4,
                  dmgrate=[0.9, 0.95], elembits=0, consume=[0, 0])
    putcond_skill("S535", src_pc, "Blood Lash", "K026", "A whip of the Bloodspeaker's own blood. (Taint chance)",
                  rate=0.6, dmgrate=[1.1, 1.15], elembits=0, consume=[0, 0], atkform="dst.PDEF+40+src.PATK*0.45")
    putcond_skill("S536", src_pc, "My Blood Is a Key", "K026", "\"My blood is a key. Every lock opens.\" Maho paid in "
                  "the caster's own blood. (all; Taint chance; costs it 4% of its HP)", rate=0.3, dmgrate=[0.75, 0.8],
                  elembits=0, cmdtgt=7, consume=[0, 0], rt_selfburn=0.04)
    blow("S537", "Ember Palm", "Haku's palm, a coal from the Furnace pressed into it. (Fire, one enemy)",
         dmgrate=[1.4, 1.5], hitrate=1.0, elembits=B["Fire"], consume=[0, 6], addlist=True, enemyuse=False,
         eqtypebits=2047)
    hwd = copy.deepcopy(s["S123"])
    hwd.update({"name": "Heat-Ward", "desc": "Haku's Tamori ward over the party: Fire damage halved for three turns.",
                "cmdtgt": 11, "putconds": 0, "option": [PUT_BY_ID("K057")], "addlist": True, "enemyuse": False,
                "consume": [0, 8], "eqtypebits": 2047})
    s["S538"] = hwd
    # Unicorn Ch1 "Fault Lines": Ide Tamotsu (battle-skills.md; user: a support, buffing diplomat, not a fighter)
    talent("S541", noop, name="Barter Coin: Bribe", cmdtgt=1, option=[], desc="School technique. Coin in an open hand. A "
           "person-for-hire takes it and goes home; anyone else loses their next move counting it. (Costs zeni)")
    putcond_skill("S542", src_pc, "Words of Peace", "K021", "An Ide emissary's voice: reasonable, warm, impossible "
                  "to fight against. (ATK down, all enemies)", rate=0.85, dmgrate=[0.0, 0.0], elembits=0, cmdtgt=7,
                  consume=[0, 8], enemyuse=False, atkform="0")
    ki = copy.deepcopy(s["S123"])
    ki.update({"name": "Song of the Ki-Rin", "desc": "A Unicorn tale of the ki-rin who carried Shinjo home. The party "
               "heals a little each turn. (Regen, all allies)", "cmdtgt": 11, "putconds": 0,
               "option": [PUT_BY_ID("K040")], "addlist": True, "enemyuse": False, "consume": [0, 10],
               "eqtypebits": 2047})
    s["S543"] = ki
    st_ = copy.deepcopy(s["S300"])
    st_.update({"name": "Share the Stores", "desc": "Tamotsu's rice cakes, handed round the whole party whether "
                "they're hungry or not. (Heal all allies)", "cmdtgt": 11, "consume": [0, 9], "addlist": True,
                "enemyuse": False, "eqtypebits": 2047, "atkform": "dst.MAXHP*0.18+src.LV*3.0"})
    s["S544"] = st_
    for sid in ("S542", "S543", "S527"):               # voice skills: lost while the speaker's ears are covered
        s[sid]["rt_voice"] = True                      # (Unicorn Ch3 Covered Ears; plugin RokuganHazard)
    talent("S545", s["S122"], name="Gaijin Spyglass", cmdtgt=7, dmgrate=[0.0, 0.0], addlist=True, consume=[0, 6],
           desc="Iuchi Hiroichi's gaijin telescope, turned on the enemy line: every enemy's weaknesses.")
    s["S545"]["eqtypebits"] = 2047
    vow = copy.deepcopy(s["S123"])                     # Shinjo Ryuko, his guardian: the Cover taunt (plugin)
    vow.update({"name": "Guardian's Vow", "desc": "Ryuko plants herself in front of the emissary: every enemy blow "
                "comes to her for two turns.", "cmdtgt": 13, "putconds": 0, "enemyuse": False, "addlist": True,
                "consume": [0, 5], "eqtypebits": 2047})
    s["S546"] = vow
    blow("S547", "Shinjo Sweep", "A Unicorn horsewoman's cut, swung wide from the saddle she isn't in. (Katana, all "
         "enemies)", dmgrate=[0.75, 0.8], hitrate=0.95, elembits=B["Katana"], cmdtgt=7, consume=[0, 8],
         addlist=True, enemyuse=False, eqtypebits=2047)
    blow("S548", "Powder Bomb", "Gaijin pepper in a clay pot. \"Burn, then! Burn like Motobu burned!\" (Fire, all; "
         "sets off any powder keg)", dmgrate=[0.55, 0.6], hitrate=1.0, elembits=B["Fire"], cmdtgt=7)
    blow("S549", "Dai Dao Cleave", "Naohida's gaijin broadsword, two-handed, all his hatred in it.", dmgrate=[1.4, 1.5],
         hitrate=0.9)
    # Unicorn Ch3 "The Noblest Blood": Iuchi Karasu's guest call (story/04 #21: Jade Strike, anti-Taint, 2 uses)
    guest_skill("S559", TPL_PUTCOND, "Iuchi Karasu: Jade Strike", "Karasu's glowing eyes, and a palmful of jade "
                "driven into the foe. \"I learned this one from a very angry oni.\" (Jade, one enemy)", 2, option=[],
                elembits=B["Jade"], dmgrate=[1.0, 1.0], atkform="dst.PDEF+60+src.LV*14")
    # the singing servants (bestiary D III: Hum = Silence unless the ears are covered; the plugin's rt_hum decides who
    # hears it) and their grab at the wax (Fortune's Lost: they pull the hands away from the ears)
    putcond_skill("S555", src_pc, "Hum", "K003", "The servants' song, all in the same breath. Whoever hears it falls "
                  "silent and starts to sway. (Silence, unless your ears are covered)", rate=0.0, dmgrate=[0.0, 0.0],
                  elembits=0, cmdtgt=7, consume=[0, 0], rt_hum=True)
    blow("S556", "Pull the Wax", "Fingers in your ear, scrabbling for the wax. (Your ears are uncovered for the rest "
         "of the battle)", dmgrate=[0.7, 0.75], hitrate=0.9, rt_pullwax=True)
    blow("S557", "Stay With Us", "\"Stay! Stay with us! The dark is quiet!\" A miner's pick three hundred years old.",
         dmgrate=[1.5, 1.6], hitrate=0.9)
    putcond_skill("S558", src_pc, "The Quiet Dark", "K007", "The lanterns gutter and the dead lean in. (all; Terror "
                  "chance)", rate=0.3, dmgrate=[0.55, 0.6], elembits=0, cmdtgt=7, consume=[0, 0])
    # Unicorn Ch4 "Regret": Naohida's guest call (production S01: Powder Charge, Fire AoE, 1 use); Tamotsu's Rank 3
    # (schools.md R3 When the Veil Moves: once a battle, act before a telegraphed attack: the party is Veiled); the
    # possessed Legion's chant (a Hum: Silence unless covered); the Shuten Doji and Kurosho (Fortune's Lost p.43:
    # Bo of Water, Fury of Osano-Wo)
    guest_skill("S565", TPL_PUTCOND, "Naohida: Powder Charge", "Naohida runs at the enemy line with a lit keg. \"Burn, "
                "then - just not them!\" (Fire, all enemies)", 1, option=[], cmdtgt=7, elembits=B["Fire"],
                dmgrate=[1.0, 1.0], atkform="dst.PDEF*0.5+40+src.LV*8")
    vm = copy.deepcopy(s["S123"])
    vm.update({"name": "When the Veil Moves", "desc": "Rank 3. Tamotsu sees the next blow coming and moves first: the "
               "party is Veiled for three turns - no Wail or song can take them - and guards. (Once a battle)",
               "cmdtgt": 11, "putconds": 0, "option": [PUT_BY_ID("K058")], "addlist": True, "enemyuse": False,
               "consume": [0, 12], "eqtypebits": 2047, "rt_uses": 1})
    s["S566"] = vm
    ch = copy.deepcopy(s["S555"])
    ch.update({"name": "Chant", "desc": "\"Himeko. The war is over, Himeko.\" Whoever hears it falls silent. (Silence, "
               "unless your ears are covered)"})
    s["S564"] = ch
    putcond_skill("S569", src_pc, "Every Apology", "K026", "A wind made of every apology nobody ever made. (all; maho, "
                  "Taint chance)", rate=0.2, dmgrate=[0.7, 0.75], elembits=B["Void"], cmdtgt=7, consume=[0, 0])
    blow("S570", "Tears of Regret", "Salt tears like thrown glass.", dmgrate=[1.4, 1.5], hitrate=0.9,
         elembits=B["Water"])
    blow("S571", "Bo of Water", "Kurosho's innate prayer: a staff of water hard as oak.", dmgrate=[1.3, 1.4],
         hitrate=0.95, elembits=B["Water"])
    blow("S572", "Fury of Osano-Wo", "A lightning bolt from an old man's fingers. (all)", dmgrate=[0.6, 0.65],
         hitrate=1.0, elembits=B["Fire"], cmdtgt=7)
    # Ronin Ch1 "What's Eating the Eta": Sayo's Remedy (sayo-remedy.md: base + catalyst; the plugin's Remedy pick list
    # greys out what she can't make and spends the two ingredients, skill field rt_recipe), her skills (battle-skills.md:
    # Pilfer in battle, Field Dressing, Bitter Root; the production's Compliment), Hiro's call (No-dachi Sweep, 2 uses),
    # the tengu, the goblins, Tomie Cho
    def recipe(sid, src, name, desc, items, **kw):
        k = copy.deepcopy(src)
        k.update({"name": name, "desc": desc, "addlist": False, "enemyuse": False, "consume": [0, 0],
                  "eqtypebits": 2047, "rt_recipe": items})
        k.update(kw)
        s[sid] = k
    recipe("S573", s["S300"], "Ginseng + Rice Wine", "A strong draught: a big heal for one ally.", ["I418", "I421"],
           cmdtgt=8, atkform="dst.MAXHP*0.55+src.LV*6.0", rt_heal=0.55)
    recipe("S574", s["S300"], "Ginseng + Moxa", "Ginseng smoke over everyone: heals the whole party.", ["I418", "I422"],
           cmdtgt=11, atkform="dst.MAXHP*0.3+src.LV*3.0")
    recipe("S575", s["S035"], "Rhubarb + Rice Wine", "A purge: cures poison, blindness and silence, and heals a little.",
           ["I419", "I421"], cmdtgt=8, remconds=COND_BIT("K001") | COND_BIT("K002") | COND_BIT("K003"))
    recipe("S576", s["S035"], "Rhubarb + Moxa", "A purge for everyone: the whole party is cured of poison, blindness "
           "and silence.", ["I419", "I422"], cmdtgt=11,
           remconds=COND_BIT("K001") | COND_BIT("K002") | COND_BIT("K003"))
    recipe("S577", TPL_PUTCOND, "Hanabi + Rice Wine", "A festival burst thrown into one face. (Fire, one enemy)",
           ["I420", "I421"], option=[], cmdtgt=1, elembits=B["Fire"], dmgrate=[1.0, 1.0],
           atkform="dst.PDEF*0.3+40+src.LV*11")
    recipe("S578", TPL_PUTCOND, "Hanabi + Moxa", "The festival burst, spread wide. (Fire, all enemies)",
           ["I420", "I422"], option=[], cmdtgt=7, elembits=B["Fire"], dmgrate=[1.0, 1.0],
           atkform="dst.PDEF*0.3+20+src.LV*6")
    recipe("S579", s["S300"], "Ginseng + Willow Bark", "A heal with a splint in it: heals one ally and guards them "
           "(DEF up).", ["I418", "I423"], cmdtgt=8, atkform="dst.MAXHP*0.35+src.LV*4.0",
           option=[PUT_BY_ID("K022")], putconds=0)
    pf = copy.deepcopy(s["S004"])
    pf.update({"name": "Pilfer", "desc": "Low Skill: a quick hand in a busy fight. Steal an item.", "addlist": True,
               "enemyuse": False, "consume": [0, 2], "eqtypebits": 2047, "rt_noauto": True})
    s["S580"] = pf
    cm = copy.deepcopy(noop)
    cm.update({"name": "Compliment", "desc": "Etiquette, of a sort. Something vain loses its next turn preening.",
               "addlist": True, "enemyuse": False, "consume": [0, 3], "cmdtgt": 1, "eqtypebits": 2047, "option": [],
               "rt_noauto": True})
    s["S581"] = cm
    fd = copy.deepcopy(s["S300"])
    fd.update({"name": "Field Dressing", "desc": "A bandage and a bitter leaf: heal one ally.", "cmdtgt": 8,
               "addlist": True, "enemyuse": False, "consume": [0, 6], "eqtypebits": 2047,
               "atkform": "dst.MAXHP*0.3+src.LV*3.0", "rt_heal": 0.3})
    s["S583"] = fd
    putcond_skill("S584", src_pc, "Bitter Root", "K001", "A paste no one should eat, flicked into a wound. (one enemy; "
                  "Poison chance, E.Def down)", rate=0.5, dmgrate=[0.6, 0.6], elembits=0, consume=[0, 5],
                  enemyuse=False)
    s["S584"]["option"].append(dict(s["S584"]["option"][0], condid="K023", rate=0.8))    # (DEF down: the wound)
    guest_skill("S588", TPL_PUTCOND, "Hiro: No-dachi Sweep", "Hiro swings the rusty no-dachi he butchers with, wide "
                "enough to take a whole line. (all enemies; double against the man-eater)", 2, option=[], cmdtgt=7,
                elembits=0, dmgrate=[1.0, 1.0], atkform="dst.PDEF*0.5+30+src.LV*8")
    blow("S589", "Claw Combo", "Two claws and a bite, one after another.", dmgrate=[0.7, 0.75], hitrate=0.9,
         atknum=[3, 3])
    putcond_skill("S585", src_pc, "Roar", "K007", "\"RUN, wave-girl! Run like the eta run!\" (all; Terror chance)",
                  rate=0.35, dmgrate=[0.3, 0.3], elembits=0, cmdtgt=7, consume=[0, 0])
    blow("S590", "Feather Blade", "A katana, fenced with a crow's wrist. Heavy hits knock you into the canal.",
         dmgrate=[1.3, 1.4], hitrate=0.9)
    blow("S591", "Wing Baffle", "Black wings in your face, then the blade.", dmgrate=[0.9, 1.0], hitrate=1.0,
         elembits=B["Air"])
    blow("S592", "Spear Throw", "A bamboo spear, thrown before the biting starts.", dmgrate=[0.9, 1.0], hitrate=0.85,
         elembits=B["Yari"])
    blow("S593", "\"Be Gone!\"", "\"Be gone, you fat, rice-eating fools!\" A walking stick, swung from the dark.",
         dmgrate=[0.9, 1.0], hitrate=0.9)
    putcond_skill("S513", src_pc, "Give Us Your Face", "K003", "Hands at your mask, chanting. (Silence chance)",
                  rate=0.35, dmgrate=[1.0, 1.0], elembits=0, consume=[0, 0])
    putcond_skill("S514", src_pc, "Constrict", "K051", "The python coils round you and squeezes. (Grapple: Speed "
                  "down)", rate=0.5, dmgrate=[1.0, 1.0], elembits=0, consume=[0, 0])
    putcond_skill("S515", src_pc, "Sting", "K001", "A sting as long as a finger. (Poison)", rate=0.5,
                  dmgrate=[0.9, 0.9], elembits=0, consume=[0, 0])
    blow("S516", "Doji Iaijutsu", "A Crane magistrate's draw, still perfect, in a cultist's hands.",
         dmgrate=[1.0, 1.0], hitrate=1.0, elembits=B["Katana"], atkform="dst.PDEF+dst.MAXHP*0.3")
    blow("S517", "Empty Hand", "The abbot's open palm. There's nothing behind it either.", dmgrate=[1.3, 1.4],
         hitrate=0.95)
    putcond_skill("S518", src_pc, "A Mask Is a Mercy", "K004", "\"No more being anyone.\" (all; Confuse chance)",
                  rate=0.3, dmgrate=[0.6, 0.6], elembits=0, cmdtgt=7, consume=[0, 0])
    putcond_skill("S512", src_pc, "Harvest of Death", "K021", "Maho from the iron box: every heart stumbles at once. "
                  "(all; ATK down chance)", rate=0.3, dmgrate=[0.7, 0.7], elembits=0, cmdtgt=7, consume=[0, 0])
    sw = copy.deepcopy(s["S123"])
    sw.update({"name": "Feed the Ward-fire", "desc": "Sanro feeds the Isawa ward-fire: the spirit in it helps. (Void "
               "Guard, all allies)", "cmdtgt": 11, "putconds": COND_BIT("K024"), "enemyuse": False, "addlist": True,
               "consume": [0, 0]})
    s["S499"] = sw
    blow("S471", "Stolen Bo of Water", "Haruki's own spell, in her shadow's hands. (Water)", dmgrate=[1.1, 1.1],
         hitrate=1.0, elembits=B["Water"])
    sp_k = copy.deepcopy(s["S300"])
    sp_k.update({"name": "Stolen Peace", "desc": "Haruki's own Path to Inner Peace, cast by a shadow on itself.",
                 "cmdtgt": 13, "enemyuse": True, "addlist": False, "consume": [0, 0],
                 "atkform": "dst.MAXHP*0.2"})
    s["S472"] = sp_k
    blow("S468", "Fever Touch", "A touch like a hot coal under the skin. (Water heals ease it)", dmgrate=[1.0, 1.1],
         hitrate=0.95, elembits=B["Fire"])
    blow("S469", "Black-glass Void", "She looks at you, and something in you cracks. (Void, all)", dmgrate=[0.7, 0.7],
         hitrate=1.0, elembits=B["Void"], cmdtgt=7)
    blow("S470", "Endless Tumble", "It falls on you, forever. (Earth)", dmgrate=[1.5, 1.6], hitrate=0.9,
         elembits=B["Earth"])
    blow("S457", "Howling Silence", "A storm that makes no sound, all at once. (all; Air)", dmgrate=[0.6, 0.6],
         hitrate=1.0, elembits=B["Air"], cmdtgt=7)
    blow("S450", "Matsu's Fury", "A Matsu champion's whole weight behind one cut.", dmgrate=[1.7, 1.8], hitrate=0.9)
    putcond_skill("S455", src_pc, "Arrows Across the River", "K021", "Arrows out of the mist from the far bank. (all; "
                  "ATK down)", rate=0.1, dmgrate=[0.45, 0.45], elembits=B["Yumi"], cmdtgt=7, consume=[0, 0])
    blow("S456", "Flames on the Ford", "Burning planks and sparks across the shield-line. (all; Fire)",
         dmgrate=[0.55, 0.55], hitrate=1.0, elembits=B["Fire"], cmdtgt=7)
    wh = copy.deepcopy(s["S405"])                       # Oni no Ianwa's turn: it whispers (the plugin's charm). A bare
    wh.update({"name": "Coward's Whisper", "desc": "It asks, very politely, for everything.", "cmdtgt": 11})  # Wait
    s["S440"] = wh                                      # has no target, so the AI never acted at all
    putcond_skill("S431", src_pc, "Ancestral Rage", "K007", "Many voices, one sword. (Terror)", rate=0.3,
                  dmgrate=[1.3, 1.3], elembits=0, consume=[0, 0])
    putcond_skill("S435", src_pc, "Blood Bolt", "K021", "Maho through borrowed hands. (ATK down)", rate=0.3,
                  dmgrate=[1.05, 1.05], elembits=0, consume=[0, 0])
    putcond_skill("S438", src_pc, "Dread Touch", "K007", "Cold fingers on the back of the neck. (Terror)", rate=0.4,
                  dmgrate=[0.8, 0.8], elembits=0, consume=[0, 0])
    blow("S436", "Breath-eater", "The red shadow crawls over you and drinks. (Drains SP and VP: soul damage)",
         dmgrate=[0.4, 0.4], hitrate=0.95, rt_soul=True)
    vd = copy.deepcopy(s["S436"])                       # the red oni's Breath-eater: SP and VP drained (rt_soul)
    vd.update({"name": "Void Drain", "desc": "\"Your Void tastes like mine. We're made of the same night.\" (drains "
               "SP and 1 VP)", "elembits": B["Void"]})
    s["S473"] = vd
    hire_skill(H[22], TPL_PUTCOND, "Jade discs, blessed and thrown: they burn what feeds on fear. (Jade, all enemies)",
               act="Jade Prayer", option=[], cmdtgt=7, elembits=B["Jade"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF+20+src.LV*3.6")
    hire_skill(H[23], s["S300"], "A loud war-song: nobody stays afraid through the third verse. (Heal all allies a "
               "little, cure Terror)", act="War-Song", cmdtgt=11, atkform="dst.MAXHP*0.12+src.LV*1.0",
               remconds=COND_BIT("K007"))
    hire_skill(H[24], TPL_PUTCOND, "A hunting arrow from behind a tent. (Yumi, one enemy)", act="Hunter's Arrow",
               option=[], elembits=B["Yumi"], dmgrate=[1.0, 1.0], hitrate=1.0, atkform="dst.PDEF*0.3+60+src.LV*9")
    hire_skill(H[38], TPL_PUTCOND, "A novice's practice staff, swung with conviction. (Bo, one enemy)",
               act="Novice's Staff", option=[], elembits=B["Bo"], dmgrate=[1.0, 1.0], atkform="dst.PDEF*0.3+12+src.LV*6")
    hire_skill(H[39], s["S300"], "Sea-salt poultices for everyone. (Heal all allies)", act="Salt Poultice",
               cmdtgt=11, atkform="dst.MAXHP*0.25+src.LV*2.0")
    hire_skill(H[40], TPL_PUTCOND, "Forty years of spearing fish from a rock. (Yari, one enemy)",
               act="Diver's Harpoon", option=[], elembits=B["Yari"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF*0.3+40+src.LV*6")
    hire_skill(H[41], s["S300"], "Rejuvenating tea for everyone, poured slowly. (Heal all allies)", act="Shrine Tea",
               cmdtgt=11, atkform="dst.MAXHP*0.25+src.LV*2.0")
    hire_skill(H[42], TPL_PUTCOND, "A Crane ashigaru's yari, straight at the foreigners. (Yari, one enemy)",
               act="Ashigaru Thrust", option=[], elembits=B["Yari"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF*0.3+40+src.LV*6")
    hire_skill(H[43], s["S300"], "A blessing, mostly aimed. (Heal all allies)", act="Novice's Blessing",
               cmdtgt=11, atkform="dst.MAXHP*0.25+src.LV*2.0")
    hire_skill(H[44], TPL_PUTCOND, "Three arrows from a Centipede bow, into the gaijin line. (Yumi, all enemies)",
               act="Centipede Volley", option=[], cmdtgt=7, elembits=B["Yumi"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF+30+src.LV*4.5")
    hire_skill(H[45], s["S300"], "Bandages and a court song. (Heal all allies)", act="Field Dressing",
               cmdtgt=11, atkform="dst.MAXHP*0.25+src.LV*2.0")
    # Scorpion Ch1 (Kyuden Bayushi castle town; Kudo): a stagehand's smoke, a Suzume's rake, a Kitsune's herbs
    hire_skill(H[46], TPL_PUTCOND, "Smoke and a falling backdrop: the old stage trick. (Blind chance, all enemies)",
               act="Smoke and Mirrors", cmdtgt=7, elembits=0, dmgrate=[0.2, 0.2], atkform="dst.PDEF+10+src.LV*1.0",
               option=[{"condid": "K002", "efx_start": None, "opttype": "opt_putcond", "rate": 0.65,
                        "showmiss": True, "when": 0, "whom": 0}])
    hire_skill(H[47], TPL_PUTCOND, "A Suzume samurai sweeps courtyards for noble poverty, and enemies for you. (Bo, "
               "one enemy)", act="Swept Clean", option=[], elembits=B["Bo"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF*0.3+50+src.LV*11")
    hire_skill(H[48], s["S300"], "Fox herbs in hot water, and a song to the kami of the woods. (Heal all allies)",
               act="Fox Herbs", cmdtgt=11, atkform="dst.MAXHP*0.25+src.LV*2.0")
    # Scorpion Ch2: a Shinjo yoriki's horse-bow; a shadow hunter's cut from the dark
    hire_skill(H[49], TPL_PUTCOND, "A Shinjo horse-archer's volley from the back row. (Yumi, all enemies)",
               act="Horse-bow Volley", option=[], cmdtgt=7, elembits=B["Yumi"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF+20+src.LV*4.0")
    hire_skill(H[51], TPL_PUTCOND, "A Mirumoto ashigaru's yari, between you and the enemy. (Yari, one enemy)",
               act="Picket Thrust", option=[], elembits=B["Yari"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF*0.3+60+src.LV*10")
    hire_skill(H[52], s["S300"], "Bitter roots from a refugee midwife. (Heal all allies)", act="Midwife's Roots",
               cmdtgt=11, atkform="dst.MAXHP*0.25+src.LV*2.0")
    # Unicorn Ch2 (Tamotsu's view, Lv 22-30): the same picket ashigaru and camp midwife, hired at his band
    hire_skill(H[57], TPL_PUTCOND, "A Mirumoto ashigaru's yari, between you and the enemy. (Yari, one enemy)",
               act="Picket Thrust", option=[], elembits=B["Yari"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF*0.3+60+src.LV*10")
    hire_skill(H[58], s["S300"], "Bitter roots from a refugee midwife. (Heal all allies)", act="Midwife's Roots",
               cmdtgt=11, atkform="dst.MAXHP*0.25+src.LV*2.0")
    # Ronin Ch1 (Cakon): a hanabi seller (Fire: the bakemono, Tomie Cho) and a Mantis ferry archer (Yumi: the tengu,
    # the tiger)
    hire_skill(H[63], TPL_PUTCOND, "Festival rockets into the enemy line. Legal ones. (Fire, all enemies)",
               act="Hanabi Volley", option=[], cmdtgt=7, elembits=B["Fire"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF*0.5+10+src.LV*4.5")
    hire_skill(H[64], TPL_PUTCOND, "A ferry archer's arrow, aimed at anything with feathers. (Yumi, one enemy)",
               act="Ferry Shot", option=[], elembits=B["Yumi"], dmgrate=[1.0, 1.0], atkform="dst.PDEF*0.3+40+src.LV*10")
    # Ronin Ch2 "The Noble and the Ronin": the barge's story brew (production S02: Ginseng + Willow bark + Snow-lotus,
    # a heal with a defence buff and regeneration; no Medicine 5 needed) and Ginseng + Snow-Lotus (sayo-remedy.md
    # "heal + regen"); Jinnai's guest call (kiho.md: Freezing the Lifeblood, paralyze, 2 uses; Chi Protection is the
    # plugin's once-a-battle catch); the retainers, the enforcers and the shadow-snakes (bosses.md, bestiary III
    # Shadow Bite); the Floating Flowers hirelings
    recipe("S594", s["S300"], "Ginseng + Willow + Snow-Lotus", "Ume-baa's two-catalyst brew: heals one ally, guards "
           "them (DEF up) and keeps on healing (Regen).", ["I418", "I423", "I429"], cmdtgt=8,
           atkform="dst.MAXHP*0.4+src.LV*4.0", rt_heal=0.4, option=[PUT_BY_ID("K022"), PUT_BY_ID("K040")], putconds=0,
           rt_learn="G1066")
    recipe("S595", s["S300"], "Ginseng + Snow-Lotus", "A slow brew: heals one ally, and keeps on healing (Regen).",
           ["I418", "I429"], cmdtgt=8, atkform="dst.MAXHP*0.3+src.LV*3.0", rt_heal=0.3,
           option=[PUT_BY_ID("K040")], putconds=0, rt_learn="G1066")
    guest_skill("S596", TPL_PUTCOND, "Jinnai: Freezing the Lifeblood", "Two fingers to a pressure point, and the blood "
                "forgets to move. (one enemy; Paralysis, never misses)", 2,
                option=[dict(PUT_BY_ID("K006"), showmiss=True)], elembits=B["Unarmed"], dmgrate=[0.6, 0.6],
                hitrate=1.0)
    putcond_skill("S597", src_pc, "Shadow Bite", "K001", "Teeth of cold shadow. (Poison)", rate=0.35,
                  dmgrate=[0.9, 0.9], elembits=0, consume=[0, 0])
    blow("S598", "Yari Line", "Three retainers, three spear-points, one direction.", dmgrate=[1.2, 1.3], hitrate=0.9,
         elembits=B["Yari"])
    putcond_skill("S599", src_pc, "Serpent's Cut", "K001", "A katana with the edge painted black. (Poison chance)",
                  rate=0.25, dmgrate=[1.25, 1.35], elembits=B["Katana"], consume=[0, 0])
    hire_skill(H[65], TPL_PUTCOND, "A Sparrow ronin's old blade, between the laces. (Katana, one enemy)",
               act="Between the Laces", option=[], elembits=B["Katana"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF*0.3+40+src.LV*10")
    # Ronin Ch3 "The Village of the Wounded Lion": Mirumoto Hikaru's guest call (kata.md: Endless Strike, up to 3 extra
    # hits at reduced damage), Matsu Hanae (a Lion: the hardest hitter, the user's clan roles), the ghost-guard, the
    # basin, the hirelings
    guest_skill("S602", TPL_PUTCOND, "Mirumoto Hikaru: Endless Strike", "Two swords move like a hurricane: one cut, and "
                "then up to three more. (Katana, one enemy, 2-4 hits)", 2, option=[], elembits=B["Katana"],
                dmgrate=[0.75, 0.75], atknum=[2, 4], hitrate=1.0)
    guest_skill("S633", TPL_PUTCOND, "Hiruma Kage: Father's Tanto", "Kage's father's jade tanto, into the place a "   # the
                "Hiruma always find. (Tanto and Jade, one enemy)", 2, option=[],                       # finale, from
                elembits=B["Tanto"] | B["Jade"], dmgrate=[2.2, 2.4], hitrate=1.0)                  # wave 4 (flare)
    # The finale's phase 3 exploits (production F09 "commands appear when available"): under Call, once a battle each,
    # only against the true form (plugin RokuganHazard exploitsFor; the effect runs as the command starts)
    for sid, name, desc, key in (
            ("S635", "\"Empress\" Bait", "Rensei, with awe, exactly as rehearsed: \"...Empress.\" Her guard drops. "
                     "(Breaks her; half her shields if the play was handed over)", "bait"),
            ("S636", "Two Voices", "Mamoru's word: two travelers speak to her at once. She can't answer both. (She "
                     "loses her next action)", "voices"),
            ("S637", "Smooth Stone Decoy", "Sayo holds out a grey pebble. The Empress can't see colour: a jewel, "
                     "surely. (She loses her next action)", "stone"),
            ("S638", "The Immovable Hand of Peace", "\"I won't strike you. And so you won't strike me.\" (Rank 5: "
                     "she's locked for her next action)", "hand")):
        guest_skill(sid, s["S400"], name, desc, 1, cmdtgt=7, dmgrate=[0.0, 0.0], rt_exploit=key)
    blow("S605", "Red Pulse", "The bloodstones beat like a heart. Everyone in the hall feels it in their teeth. (all)",
         dmgrate=[0.45, 0.5], hitrate=1.0, elembits=B["Void"], cmdtgt=7)
    putcond_skill("S606", src_pc, "Frozen Cut", "K051", "A blade three hundred years cold. (Speed down chance)", rate=0.35,
                  dmgrate=[1.15, 1.25], elembits=B["Yari"], consume=[0, 0])
    blow("S607", "Matsu Fury", "Hanae stops being careful. One cut, all of her in it. (Katana, one enemy)",
         dmgrate=[1.9, 2.0], hitrate=0.9, elembits=B["Katana"], enemyuse=False, addlist=True, consume=[0, 8])
    blow("S608", "Lion's Charge", "The Matsu charge: straight through the enemy line. (Katana, all enemies)",
         dmgrate=[0.9, 1.0], hitrate=0.95, elembits=B["Katana"], cmdtgt=7, enemyuse=False, addlist=True,
         consume=[0, 12])
    hire_skill(H[67], TPL_PUTCOND, "A goat-herd's hunting arrow, aimed for the soft place under the fur. (Yumi, one "
               "enemy)", act="Bear Arrow", option=[], elembits=B["Yumi"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF*0.3+40+src.LV*10")
    hire_skill(H[68], TPL_PUTCOND, "Handfuls of jade dust thrown over the enemy line. Things that should be dead hate "
               "it. (Jade, all enemies)", act="Jade Dust", option=[], cmdtgt=7, elembits=B["Jade"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF*0.6+40+src.LV*11")
    # Ronin Ch4 "The Oracle's Choice": Ume-baa's Anatomy (sayo-remedy.md §4: Diagnosis, the next Remedy on that target
    # gets +1 tier - plugin x1.5; in the Remedy pick list once taught, G1138), the Ember Charm (equipment.md: once per
    # battle a small Fire hit or a revive; the two skills share one use, rt_usekey), the Naga's champion (bosses.md:
    # Pearl Spear, Coil), the Scorpion agents' and assassins' needle, the hirelings
    recipe("S609", s["S300"], "Diagnosis", "Anatomy (Ume-baa's low knowledge): hands on the body, not across the room. "
           "Heals one ally a little; the next Remedy on them is one tier stronger.", None, cmdtgt=8,
           atkform="dst.MAXHP*0.08+src.LV*1.0", rt_learn="G1138", rt_diag=True)
    sp = copy.deepcopy(TPL_PUTCOND)
    sp.update({"name": "Ember: Spark", "desc": "The ember charm spits one coal. Once a battle (shared with Rekindle). "
               "(Fire, one enemy)", "option": [], "cmdtgt": 1, "elembits": B["Fire"], "dmgrate": [1.0, 1.0],
               "atkform": "dst.PDEF*0.3+30+src.LV*6", "addlist": True, "enemyuse": False, "consume": [0, 0],
               "eqtypebits": 2047, "rt_uses": 1, "rt_usekey": "ember", "rt_noauto": True})
    s["S615"] = sp
    rk = copy.deepcopy(s["S300"])
    rk.update({"name": "Ember: Rekindle", "desc": "The ember charm breathes on someone who has gone cold. Once a battle "
               "(shared with Spark). (Revive one ally, a quarter of their HP)", "cmdtgt": 8, "remconds": 1,
               "atkform": "dst.MAXHP*0.25", "addlist": True, "enemyuse": False, "consume": [0, 0],
               "eqtypebits": 2047, "rt_uses": 1, "rt_usekey": "ember", "rt_noauto": True})
    s["S616"] = rk
    blow("S610", "Pearl Spear", "The spear-point glows like a pearl under deep water, and goes in very deep. (Yari, "
         "Water)", dmgrate=[1.55, 1.65], hitrate=0.95, elembits=B["Yari"] | B["Water"])
    putcond_skill("S611", src_pc, "Coil", "K051", "The great serpent body sweeps round the whole stair and tightens. "
                  "(all; Speed down chance)", rate=0.4, dmgrate=[0.6, 0.65], elembits=0, cmdtgt=7, consume=[0, 0])
    putcond_skill("S612", src_pc, "Poison Needle", "K001", "A needle from a pilgrim's sleeve, wet at the tip. (Poison "
                  "chance)", rate=0.45, dmgrate=[0.9, 0.95], elembits=B["Tanto"], consume=[0, 0])
    # The finale, Act 1 (the Shrine of Osano-Wo: bosses.md, the seven waves): the burning fanatics, the ogres' ram,
    # the thing that took Ryozo's name, the wave boss (a many-legged horror out of the Shinomen); the shrine hirelings
    blow("S619", "Burning Leap", "A goblin soaked in lamp oil, alight and laughing, jumps on you. (Fire)",
         dmgrate=[1.3, 1.4], hitrate=0.9, elembits=B["Fire"])
    blow("S620", "Battering Ram", "The ram the ogres carry, swung at whoever stands in the gate.", dmgrate=[1.9, 2.0],
         hitrate=0.8)
    putcond_skill("S621", src_pc, "A Good Man's Name", "K007", "It says the name it stole, and it is pleased with "
                  "itself. (all; Fear chance)", rate=0.35, dmgrate=[0.55, 0.6], elembits=0, cmdtgt=7, consume=[0, 0])
    putcond_skill("S622", src_pc, "Web of the Mori", "K028", "Grey silk out of the dark, over everyone. (all; Netted "
                  "chance: loses its next action)", rate=0.3, dmgrate=[0.45, 0.5], elembits=0, cmdtgt=7,
                  consume=[0, 0])
    putcond_skill("S623", src_pc, "Black Fang", "K026", "Fangs wet with something from the Festering Pit. (Taint "
                  "chance)", rate=0.5, dmgrate=[1.4, 1.5], elembits=0, consume=[0, 0])
    # The finale, Act 2 (the Shinomen: bestiary Kumo Brood "Cocoon", Lava Tree Dryad "Ember Rain")
    putcond_skill("S624", src_pc, "Cocoon", "K028", "Grey silk, round and round, until one of you is a parcel. (Netted "
                  "chance: loses its next action)", rate=0.45, dmgrate=[0.7, 0.75], elembits=0, consume=[0, 0])
    blow("S625", "Ember Rain", "The Lava Tree shakes its branches, and it rains fire on everyone. (Fire, all)",
         dmgrate=[0.7, 0.75], hitrate=0.95, elembits=B["Fire"], cmdtgt=7)
    # The finale, Act 4 "The Empress of Nothing" (production F09; bosses.md b_final_nashiko_p1-p3)
    putcond_skill("S626", src_pc, "Look at Me", "K004", "She turns her loveliest face on one of you, and for a moment "
                  "you'd do anything she asked. (Confuse chance)", rate=0.4, dmgrate=[0.6, 0.65], elembits=0,
                  consume=[0, 0])
    blow("S627", "Wings of Smoke", "She rises on wings of smoke and comes down on all of you. (Air, all)",
         dmgrate=[0.7, 0.75], hitrate=0.95, elembits=B["Air"], cmdtgt=7)
    putcond_skill("S628", src_pc, "How You End", "K007", "Each of you sees, for a moment, your own death: old and alone "
                  "in the dark. (all; Fear chance)", rate=0.35, dmgrate=[0.55, 0.6], elembits=0, cmdtgt=7,
                  consume=[0, 0])
    blow("S629", "The Long Night", "A hand of starless dark closes on one of you.", dmgrate=[1.6, 1.7],
         hitrate=0.95)
    putcond_skill("S630", src_pc, "Fu Leng's Blood", "K026", "The wound in her throat pulses, and black blood rains on "
                  "everyone. (all; Taint chance)", rate=0.3, dmgrate=[0.75, 0.8], elembits=0, cmdtgt=7, consume=[0, 0])
    blow("S631", "The Empress's Claw", "Nails like a court of knives. (heavy, one)", dmgrate=[1.9, 2.0], hitrate=0.95)
    putcond_skill("S632", src_pc, "A Court of the Dead", "K007", "She speaks in the voice of every soul she drank. "
                  "(all; Fear chance)", rate=0.3, dmgrate=[0.85, 0.9], elembits=0, cmdtgt=7, consume=[0, 0])
    # the post-game, P2 Shiro Hiruma: Oni no Okura (the 1999 card: Akuma took the Jade Champion's name, and with its
    # power made a daughter to carry on his rage; she stands at the edge of the Shadowlands)
    putcond_skill("S639", src_pc, "Akuma's Rage", "K007", "Her father's rage, all of it, in one roar. (all; Fear "
                  "chance)", rate=0.35, dmgrate=[0.8, 0.85], elembits=0, cmdtgt=7, consume=[0, 0])
    blow("S640", "The Stolen Name", "She speaks a Jade Champion's name, and it cuts. (heavy, one)",
         dmgrate=[1.9, 2.0], hitrate=0.95)
    putcond_skill("S641", src_pc, "The Castle Remembers", "K026", "The Hiruma dead in the walls cry out, and the "
                  "Taint comes with them. (all; Taint chance)", rate=0.3, dmgrate=[0.7, 0.75], elembits=0, cmdtgt=7,
                  consume=[0, 0])
    # the post-game, P3 the Orochi (wiki "Orochi": sea serpents of Sakkaku, humourless and intelligent; they keep the
    # ships they sink, and the souls aboard)
    blow("S642", "Tidal Lash", "The tail comes over the rail like the sea itself. (Water, all)", dmgrate=[0.85, 0.9],
         hitrate=0.95, elembits=B["Water"], cmdtgt=7)
    blow("S643", "Coil", "A coil of green scale as thick as a mast closes on one of you. (heavy, one)",
         dmgrate=[2.0, 2.1], hitrate=0.95)
    putcond_skill("S644", src_pc, "The Drowned Crews", "K007", "The souls of every ship it ever sank rise in the spray "
                  "and look at you. (all; Fear chance)", rate=0.35, dmgrate=[0.7, 0.75], elembits=0, cmdtgt=7,
                  consume=[0, 0])
    hire_skill(H[71], TPL_PUTCOND, "An Osano-Wo monk claps his hands, and it thunders. (Air, all enemies)",
               act="Thunderclap", option=[], cmdtgt=7, elembits=B["Air"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF*0.6+40+src.LV*11")
    hire_skill(H[72], TPL_PUTCOND, "A jade-tipped arrow from the Wall's own stores. Shadowlands things hate it. (Yumi + "
               "Jade, one enemy)", act="Jade Arrow", option=[], elembits=B["Yumi"] | B["Jade"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF*0.3+60+src.LV*11")
    hire_skill(H[69], TPL_PUTCOND, "An arrow from the crater wall's guard, fletched in Phoenix orange. (Yumi, one "
               "enemy)", act="Crater-wall Arrow", option=[], elembits=B["Yumi"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF*0.3+40+src.LV*10")
    hire_skill(H[70], TPL_PUTCOND, "An Isawa reminds the mountain's smoke which way the wind blows. (Air, all "
               "enemies)", act="Wind Off the Crater", option=[], cmdtgt=7, elembits=B["Air"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF*0.6+40+src.LV*11")
    hire_skill(H[66], TPL_PUTCOND, "A wandering priest reminds the air how to move. Shadows blow out. (Air, all "
               "enemies)", act="Remembered Wind", option=[], cmdtgt=7, elembits=B["Air"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF*0.6+40+src.LV*11")
    # Unicorn Ch4 (the siege camp): an Iuchi water-shugenja (Water: the Doji) and a Mirumoto yari sergeant (Yari: the
    # possessed Legion)
    hire_skill(H[61], TPL_PUTCOND, "An Iuchi water-prayer over the enemy line. (Water, all enemies)",
               act="Iuchi Tide", option=[], cmdtgt=7, elembits=B["Water"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF*0.5+12+src.LV*4.5")
    hire_skill(H[62], TPL_PUTCOND, "A Mirumoto sergeant's yari, from the second rank. (Yari, one enemy)",
               act="Sergeant's Thrust", option=[], elembits=B["Yari"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF*0.3+60+src.LV*10")
    # Unicorn Ch3 (the Mirumoto camp): a Togashi Bo-monk (Bo: the servants' and the dead's weakness) and an Agasha
    # fire-shugenja (Fire: the dead)
    hire_skill(H[59], TPL_PUTCOND, "A Togashi monk's Bo: it wakes a sleeper and drops a corpse. (Bo, one enemy)",
               act="Waking Blow", option=[], elembits=B["Bo"], dmgrate=[1.0, 1.0], atkform="dst.PDEF*0.3+60+src.LV*10")
    hire_skill(H[60], TPL_PUTCOND, "An Agasha fire-prayer across the enemy line. (Fire, all enemies)",
               act="Agasha Flame", option=[], cmdtgt=7, elembits=B["Fire"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF*0.5+12+src.LV*4.5")
    # Scorpion Ch4 (the Dragon mountains, Tamori's Furnace): Tamori Haku's two wards, two hirelings
    # Unicorn Ch1: an Iuchi water-shugenja from the camps' relief squads (Rolling River: water spoils powder) and a
    # Moto outrider (horse-archer volley)
    hire_skill(H[55], TPL_PUTCOND, "Master of the Rolling River: a wave out of nowhere over every enemy. Wet powder "
               "won't burn. (Water, all enemies)", act="Rolling River", option=[], cmdtgt=7, elembits=B["Water"],
               dmgrate=[1.0, 1.0], atkform="dst.PDEF*0.5+12+src.LV*4.5")
    hire_skill(H[56], TPL_PUTCOND, "A Moto rider's volley from the saddle, at a gallop. (Yumi, all enemies)",
               act="Saddle Volley", option=[], cmdtgt=7, elembits=B["Yumi"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF*0.5+10+src.LV*4.5")
    hire_skill(H[53], TPL_PUTCOND, "Cold rain called down out of a clear mountain sky. Fire spirits hate it. (Water, "
               "all enemies)", act="Cooling Rain", option=[], cmdtgt=7, elembits=B["Water"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF*0.5+30+src.LV*6")
    hire_skill(H[54], TPL_PUTCOND, "Two blades, one breath: a Mirumoto guide's daisho. (Katana, one enemy, twice)",
               act="Two Swords", option=[], elembits=B["Katana"], dmgrate=[1.0, 1.0], atknum=[2, 2],
               atkform="dst.PDEF*0.3+30+src.LV*6")
    hire_skill(H[50], TPL_PUTCOND, "A cut from the dark, and soot in the eyes. (Tanto, one enemy; Blind chance)",
               act="Hunter's Cut", elembits=B["Tanto"], dmgrate=[1.0, 1.0], atkform="dst.PDEF*0.3+60+src.LV*10",
               option=[{"condid": "K002", "efx_start": None, "opttype": "opt_putcond", "rate": 0.5,
                        "showmiss": True, "when": 0, "whom": 0}])
    hire_skill(H[36], s["S300"], "A sea-shrine prayer against the storm. (Heal all allies)", act="Storm Prayer",
               cmdtgt=11, atkform="dst.MAXHP*0.25+src.LV*2.0")
    hire_skill(H[37], TPL_PUTCOND, "An oak staff through a shadow. (Bo, one enemy)", act="Gate Staff", option=[],
               elembits=B["Bo"], dmgrate=[1.0, 1.0], atkform="dst.PDEF*0.3+55+src.LV*9")
    hire_skill(H[34], TPL_PUTCOND, "A temple staff, spun and swung. (Bo, one enemy)", act="Temple Staff",
               option=[], elembits=B["Bo"], dmgrate=[1.0, 1.0], atkform="dst.PDEF*0.3+50+src.LV*9")
    hire_skill(H[35], s["S300"], "A survivor's prayer for everyone near her. (Heal all allies)", act="Survivor's Prayer",
               cmdtgt=11, atkform="dst.MAXHP*0.22+src.LV*2.0")
    hire_skill(H[32], TPL_PUTCOND, "A rice-porter's carrying-pole across the shins. (Bo, one enemy)",
               act="Pole Sweep", option=[], elembits=B["Bo"], dmgrate=[1.0, 1.0], atkform="dst.PDEF*0.3+40+src.LV*8")
    hire_skill(H[33], s["S300"], "Prayers for the dead, said for the living. (Heal all allies)", act="Memorial Prayer",
               cmdtgt=11, atkform="dst.MAXHP*0.25+src.LV*2.0")
    hire_skill(H[30], TPL_PUTCOND, "A small flame, cupped and thrown. (Fire, one enemy)", act="Acolyte's Flame",
               option=[], elembits=B["Fire"], dmgrate=[1.0, 1.0], atkform="dst.PDEF*0.3+20+src.LV*7")
    hire_skill(H[31], TPL_PUTCOND, "An oak staff across the knees. (Bo, one enemy)", act="Staff Sweep",
               option=[], elembits=B["Bo"], dmgrate=[1.0, 1.0], atkform="dst.PDEF*0.3+18+src.LV*7")
    hire_skill(H[27], s["S300"], "A Kitsu prayer to the river's dead, over everyone's wounds. (Heal all allies)",
               act="River Prayer", cmdtgt=11, atkform="dst.MAXHP*0.25+src.LV*2.0")
    hire_skill(H[28], s["S300"], "The Ikoma war-song, very loud. (Heal all allies a little, cure Terror)",
               act="War-Song", cmdtgt=11, atkform="dst.MAXHP*0.12+src.LV*1.0", remconds=COND_BIT("K007"))
    hire_skill(H[29], TPL_PUTCOND, "A Matsu spear-thrust. (Yari, one enemy)", act="Matsu Thrust", option=[],
               elembits=B["Yari"], dmgrate=[1.0, 1.0], atkform="dst.PDEF*0.3+50+src.LV*9")
    hire_skill(H[26], s["S300"], "Poultices and arrow-pulling for everyone. (Heal all allies)", act="Field Poultice",
               cmdtgt=11, atkform="dst.MAXHP*0.25+src.LV*2.0")
    hire_skill(H[25], TPL_PUTCOND, "A deserter's spear, still very good. (Yari, one enemy)", act="Deserter's Thrust",
               option=[], elembits=B["Yari"], dmgrate=[1.0, 1.0], atkform="dst.PDEF*0.3+50+src.LV*9")
    hire_skill(H[19], TPL_PUTCOND, "A jar of lamp oil, lit, thrown along the enemy line. (Fire, all enemies)",
               act="Lamp Oil", option=[], cmdtgt=7, elembits=B["Fire"], dmgrate=[1.0, 1.0],
               atkform="dst.PDEF+20+src.LV*4.0")
    for sid, hv in (("S154", 0.35), ("S157", 0.05), ("S158", 0.7), ("S300", 0.5), ("S127", 0.1)):
        if sid in s:
            s[sid]["rt_heal"] = hv                  # heal strength for the auto-battle AI (RokuganAI smartCommand)
    # Area skills read like spells (user: "not clear what is happening when the aoe attack goes off; it's clear when
    # Path to Inner Peace is cast"): a wind-up in place, the cast sound, and a spell effect on every target, picked by
    # element (the gen_spellfx effects); the plugin also pops the skill's name over the user (RokuganField).
    AOE_FX = [("Fire", "FX422"), ("Air", "FX404"), ("Yumi", "FX458"), ("Water", "FX452"), ("Jade", "FX463"),
              ("Earth", "FX479"), ("Void", "FX485")]
    for sid, k in s.items():
        if not isinstance(k, dict) or k.get("cmdtgt") not in (3, 7) or "S300" <= sid <= "S391":
            continue
        if (k.get("useact") or {}).get("id") != "use_normal":
            continue
        bits = k.get("elembits") or 0
        fx = next((f for n, f in AOE_FX if bits & B[n]), None)
        if not fx:
            terror = any(o.get("condid") == "K007" for o in (k.get("option") or []) if isinstance(o, dict))
            fx = "FX485" if terror else "FX418"
        k["useact"] = {"id": "use_charge", "scp": None, "eefx": "FX099", "useefx": None, "usesnd": "SE229",
                       "useani": {"id": "cast_area", "mdlid": "CV000", "part": 0, "spd": 1.0}}
        k["aimani"] = {"id": "cast_area", "mdlid": "CV000", "part": 0, "spd": 1.0}
        k["atkact"] = {"id": "noop", "scp": None}
        k["hitact"] = dict(k.get("hitact") or {}, hitefx=fx, hitsnd="SE204")
        k["rt_aoe"] = True
    # Single-target spells swung a weapon (user 2026-11-12: "spells are showing up as fist attacks a lot instead of the
    # char making some sort of prayer move then colorful representation on the screen, example amaterasu flame"): every
    # magic attack (magic damage form, or a MATK formula) that still uses the plain weapon swing gets the bolt cast of
    # Death of Flame (S337) and a spell effect on the target by element.
    bolt = s.get("S337") or {}
    for sid, k in s.items():
        if not isinstance(k, dict) or k.get("rt_aoe") or (k.get("atkact") or {}).get("id") != "atk_normal":
            continue
        el = sum(B[n] for n in ("Fire", "Water", "Air", "Earth", "Void") if n in B)
        wp = sum(B[n] for n in ("Katana", "Yari", "Tanto", "Tetsubo", "Yumi", "Bo", "Unarmed") if n in B)
        bits0 = k.get("elembits") or 0
        magic = (k.get("dmgform") == 1 or "MATK" in str(k.get("atkform") or "") or
                 (bits0 & el and not bits0 & wp and k.get("flags") != 255))           # (Amaterasu's Fire: MATK)
        if not magic or k.get("skilltype") != "attack":
            continue
        bits = k.get("elembits") or 0
        fx = next((f for n, f in AOE_FX if bits & B[n]), None) or "FX437"
        for fld in ("useact", "aimani"):
            if fld in bolt:
                k[fld] = copy.deepcopy(bolt[fld])
        k["atkact"] = copy.deepcopy(bolt.get("atkact")) or {"id": "noop", "scp": None}     # no weapon swing
        k["hitact"] = dict(k.get("hitact") or {}, hitefx=fx, hitsnd="SE204")
    # School ranks (docs/rules/progression-v2.md, user 2026-11-11): passive skills, given at Lv 15/30/45/60 by the
    # players' lvoption (RANK_OPTIONS below); the level-up panel names them. Effects: plugin RokuganRanks.sk.
    for sid, (name, desc) in (list(RANK_SKILLS.items()) + [(k, (v[2], v[3])) for k, v in ADV_SKILLS.items()] +
                              [(k, (v[2], v[3])) for k, v in COMP_RANK_SKILLS.items()]):
        r = copy.deepcopy(noop)
        # (user 2026-11-12: "new schools are not showing up as School selections") listed under School, greyed out:
        # always-on techniques (plugin: rt_passive is never usable)
        r.update({"name": name, "desc": desc + " (Always active.)", "addlist": True, "enemyuse": False, "occasion": 1,
                  "consume": [0, 0], "rt_school": True, "rt_passive": True})
        s[sid] = r
    # Kata / kiho / tattoos (tools/kata_data.py): School-list commands; the plugin swaps in the user's own weapon
    # attack x rt_kmul and puts the rt_kata stance on them (RokuganRanks.sk useKata).
    for sid, cid, pid, lv, kind, name, mult, turns, mods, extra, desc in _kata.KATA:
        k = copy.deepcopy(s["S100"])
        k.update({"name": name, "desc": "%s (%s)" % (desc, {"kata": "Kata", "kiho": "Kiho", "tattoo": "Tattoo"}[kind]),
                  "addlist": True, "enemyuse": False, "occasion": 1, "eqtypebits": 2047,
                  "elembits": 0,       # (the banner read the katana template's element; the strike is the weapon's)
                  # (user 2026-11-12: "Kiho and Kata should use TP points") TP by the level it is learned at
                  "consume": [1, 4 + (lv or 12) // 3],
                  "rt_school": True, "rt_kata": cid, "rt_kmul": mult, "rt_kkind": kind,
                  "rt_kreq": list(_kata.REQ.get(sid, ())), "rt_knostrike": sid in _kata.NO_STRIKE})
        if _kata.REQ.get(sid):
            k["desc"] += " Needs: %s." % " or ".join("bare hands / claws" if w == "Unarmed" else
                                                       ("yari / naginata" if w == "Yari" else w.lower())
                                                       for w in _kata.REQ[sid])
        s[sid] = k
    sw = copy.deepcopy(s["S045"])                      # Stand Against the Waves (a Water spell; cond K136)
    sw.update({"name": "Stand Against the Waves", "desc": "Stand Against the Waves (Water 2). One ally strikes once more "
               "for each of the caster's Insight Ranks on their next turn, a little less accurately. (Prayers & "
               "Treasures)", "consume": [0, 12], "elembits": B["Water"], "putconds": 0, "addlist": True,
               "enemyuse": False, "occasion": 1, "eqtypebits": 2047,
               "option": [o for o in (sw.get("option") or []) if o.get("opttype") != "opt_putcond"] +
               [dict(PUT_BY_ID("K136"))]})
    s["S799"] = sw
    save("skill", s)

    # ---- weapon.json  (eqtype: 1 dagger, 2 sword, 3 spear, 5 staff, 6 bow, 7 hammer)
    w = load("weapon")
    wbase = w["W010"]
    WDESC = {
        "W100": "A plain, honest katana. Every ronin's first and often last blade.",
        "W101": "The spear of the Wall's ashigaru. Goblins hate the long end.",
        "W102": "A small utility knife from a sword's scabbard. Quick in the hand. Speed +2.",
        "W103": "An iron-shod oak club, the Crab's answer to armour. Pierces some defence.",
        "W104": "A light bamboo bow. Strikes from the back row.",
        "W105": "A staff of oiled oak. Turns blows aside. Evasion +10%.",
        "W107": "A Seppun blade, small and very sharp. Satomi's thank-you. Speed +2.",
        "W110": "A clan-forged katana. Good steel, plain fittings.",
        "W111": "Black-lacquered shaft, a broad blade. The Hida yari.",
        "W112": "A guardless dagger for close work. Speed +3.",
        "W113": "Oak bound in iron and studded. Pierces some defence.",
        "W114": "Rattan-wrapped, stiffer draw. Strikes from the back row.",
        "W115": "Ironwood: heavy as stone, never splits. Turns blows aside.",
        "W116": "A Lacquered Yari with a jade-inlaid blade. (Jade)",
        "W117": "An Iron-studded Tetsubo with jade studs. (Jade)",
        "W120": "A Kaiu forge's masterwork club, iron to the grip. Pierces some defence.",
        "W138": "A long Matsu spear with a lion's-mane tassel. Pushes burning timber into a river very nicely.",
        "W121": "A clean, honest blade from a Hiruma scout's cache. Found hanging in the lava trees.",
        "W130": "Heaven's Glory Reflected in the Soul's Steel. Look at it and you measure yourself against the ideal "
                "samurai. Rensei can bear to, now. (Critical +15)",
        "W131": "A Kakita smith's best work for sale: no name, no story, and a perfect edge.",
        "W132": "A Tsuruchi-pattern great bow, from a crate in the Crane port's customs house.",
        "W144": "A monk's staff from the Kitsuki outfitter, ringed with a Togashi tattoo pattern. Patience made "
                "visible.",
        "W145": "Shosuro Norie's gift for three true rumours: \"You'll need a smaller knife than you think.\"",
        "W146": "A Mantis sickle, blade hooked for cutting rigging and anything else.",
        "W147": "Mountain-forged by a Togashi smith who never asks what a pilgrim needs a knife for. (Tanto)",
        "W148": "A Mirumoto katana with jade set along the back of the blade, from the Iuchi mines. (Katana + Jade)",
        "W149": "An Iuchi hunting bow, its arrowheads cut from mine jade. (Yumi + Jade)",
        "W150": "Grandmother Cedar's Gift: a jade-handled knife buried under the cedar, wrapped in oiled cotton. "
                "(Tanto + Jade)",
        "W140": "A Bayushi dinner gift: a Shosuro knife, very thin, very sharp, very deniable.",
        "W141": "Doji Seikidera's ancestral sword. It rings for its true wielder. It does not ring for Gendo.",
        "W142": "A gaijin matchlock picked up at Shiro Izumida. It does not belong here. (History -15 when taken)",
        "W143": "The year-400 smiths' best: a long straight-backed tachi, polished like water.",
        "W139": "A long, curved cavalry blade of the old pattern, from the year-400 market. Nobody will make "
                "one like it for seven hundred years.",
        "W133": "The short blade of a Kakita daisho, sold alone. Lady Sanae: your father has never faced anything but a "
                "katana. (Tanto)",
        "W134": "Excellent steel from the Kakita smiths. No story yet.",
        "W135": "A Mantis great bow, sold in a Crane gallery with an apology.",
        "W136": "Matsu Nagai's training sword. He wants you to have it. He wants never to see it again.",
        "W137": "The bokken tournament's prize: a miniature jade-bladed tanto. Every prize at this court is jade. "
                "(Tanto, Jade)",
        "W122": "A long Hida yari with a heavy cross-blade.",
        "W123": "A Hida War Yari with jade set in the blade. (Jade)",
        "W124": "The Hiruma daimyo's father's tanto, its blade inlaid with jade. Kage's thank-you. (Jade)",
        "W125": "The Hida clan's iron club, for breaking things that ought to stay broken.",
        "W126": "A Kaiu tetsubo so heavy it has a name. Slow, and it doesn't care.",
        "W127": "A Kaiu-forged spear with a long cross-blade.",
        "W128": "A Kaiu War Spear set with jade along the blade. (Jade)",
        "W129": "A Kaiu smith bound Tsukakoro's rib into an iron club. It still twitches when oni are near.",
        "W106": "No weapon. In a monk's hands, fists grow with every level and end up the deadliest thing in the Empire.",
        # the finale: the shrine smith of Osano-Wo (T5), and the thunder-split rock on the Plains of Thunder
        "W151": "The shrine smith's own blade, forged in a thunderstorm on purpose. He says the lightning tempers it. "
                "He may be joking. (T5)",
        "W152": "A long Utaku cavalry spear, traded up the Unicorn road for the shrine's jade. (T5)",
        "W153": "Found in a rock the lightning split: a bow of pale wood that never warps. It shines a little at "
                "night. (T5)",
        "W154": "A thunder monk's staff, iron-shod, struck by lightning twice. The monks call that a blessing. (T5)",
        "W158": "The Crab's sacred sword, born in the Great Forge. Steel a shade darker than any other, and it has never once needed a whetstone.",
        "W159": "Iron claws strapped across the knuckles. A monk's answer to a sword, until the fists catch up. (Unarmed)",
        "W160": "Claws forged at the shrine of the Thunder, still warm. Better than most swords. (Unarmed)",
        "W155": "A blade too thin to see edge-on. The smith won't say who ordered it, or why they never collected. (T5)",
        "W156": "The smith's master katana with a seam of Wall jade along the back of the blade. (T5, Katana + Jade)",
        "W157": "A katana with a running hare on the tsuba, found on the throne of Shiro Hiruma. How a Usagi blade came "
                "to the Hiruma's lost castle, nobody living knows. (Crit +15)",
    }
    wlist = [("W100", "Ronin's Katana", 2, "S100", "EV000", 30), ("W101", "Ashigaru Yari", 3, "S101", "EV007", 24),
             ("W102", "Kozuka", 1, "S102", "EV016", 16), ("W103", "Oak Tetsubo", 7, "S103", "EV001", 22),
             ("W104", "Bamboo Yumi", 6, "S104", "EV005", 22), ("W105", "Oak Bo", 5, "S105", "EV006", 15),
             ("W106", "Bare Hands", 0, "S106", "EV001", 18),
             ("W107", "Seppun Tanto", 1, "S102", "EV016", 30),
             ("W110", "Clan Katana", 2, "S100", "EV000", 62), ("W111", "Lacquered Yari", 3, "S101", "EV007", 50),
             ("W112", "Aiguchi", 1, "S102", "EV016", 34), ("W113", "Iron-studded Tetsubo", 7, "S103", "EV001", 46),
             ("W114", "Rattan Yumi", 6, "S104", "EV005", 46), ("W115", "Ironwood Bo", 5, "S105", "EV006", 32),
             ("W116", "Jade Lacquered Yari", 3, "S107", "EV007", 50),
             ("W117", "Jade-studded Tetsubo", 7, "S108", "EV001", 46),
             ("W120", "Kaiu Tetsubo", 7, "S103", "EV001", 74), ("W121", "Fine Katana", 2, "S100", "EV000", 84),
             ("W122", "Hida War Yari", 3, "S101", "EV007", 76), ("W123", "Jade War Yari", 3, "S107", "EV007", 76),
             ("W124", "Kage's Father's Tanto", 1, "S163", "EV016", 88),
             ("W125", "Hida Tetsubo", 7, "S103", "EV001", 104), ("W126", "Kaiu Iron Mountain", 7, "S103", "EV001", 118),
             ("W127", "Kaiu War Spear", 3, "S101", "EV007", 106), ("W128", "Jade Kaiu Spear", 3, "S107", "EV007", 106),
             ("W129", "Bone-cage Tetsubo", 7, "S103", "EV001", 138),
             ("W130", "Heaven's Glory", 2, "S100", "EV000", 96),
             ("W131", "Kakita Blade", 2, "S100", "EV000", 108), ("W132", "Daikyu-pattern Yumi", 6, "S104", "EV005", 98),
             ("W133", "Kakita Wakizashi", 1, "S102", "EV016", 110), ("W134", "Excellent Katana", 2, "S100", "EV000", 124),
             ("W135", "Tsuruchi Longbow", 6, "S104", "EV005", 118),
             ("W136", "Matsu Sensei's Bokken", 2, "S100", "EV000", 36),
             ("W137", "Jade Tanto", 1, "S437", "EV016", 70),
             ("W138", "Matsu War Yari", 3, "S101", "EV007", 132),
             ("W139", "Tachi-pattern Katana", 2, "S100", "EV000", 90),
             ("W140", "Shosuro Tanto", 1, "S102", "EV016", 98), ("W141", "Shukujo", 2, "S100", "EV000", 128),
             ("W142", "Gaijin Musket", 6, "S104", "EV005", 150),
             ("W143", "Tachi-pattern Fine Katana", 2, "S100", "EV000", 104),
             ("W144", "Togashi Bo", 5, "S105", "EV006", 126),
             ("W145", "Norie's Kozuka", 1, "S102", "EV016", 24), ("W146", "Mantis Kama", 1, "S102", "EV016", 22),
             ("W147", "Mountain Tanto", 1, "S102", "EV016", 128),
             ("W148", "Jade-backed Katana", 2, "S562", "EV000", 110),
             ("W149", "Jade-tipped Yumi", 6, "S563", "EV005", 100),
             ("W150", "Jade-handled Knife", 1, "S437", "EV016", 34),
             ("W151", "Master-forged Katana", 2, "S100", "EV000", 156), ("W152", "Utaku Yari", 3, "S101", "EV007", 154),
             ("W153", "Moonlit Yumi", 6, "S104", "EV005", 152), ("W154", "Thunder Monk's Bo", 5, "S105", "EV006", 150),
             ("W155", "Whisper Blade", 1, "S102", "EV016", 152),
             ("W156", "Jade-seamed Master Katana", 2, "S562", "EV000", 146),
             ("W157", "The Hare Sword", 2, "S100", "EV000", 176),
             ("W158", "Kaiu Blade", 2, "S100", "EV000", 126),
             ("W159", "Iron Nekode", 0, "S690", "EV001", 64), ("W160", "Thunder Claws", 0, "S690", "EV001", 140)]
    for wid, name, et, sid, mdl, atk in wlist:
        x = copy.deepcopy(wbase)
        x.update({"name": name, "eqtype": et, "skillid": sid, "mdlid": mdl, "PATK": atk, "price": atk * 10,
                  "desc": WDESC[wid]})
        if wid == "W106":
            x["price"] = 0
        if wid == "W156":
            x["price"] = int(atk * 10 * 1.25)
        if wid in ("W124", "W129", "W130", "W145", "W146", "W148", "W149", "W150", "W153", "W157"):
            x["price"] = 0
        if wid == "W142":
            x["rt_look"] = "musket"                          # drawn as a matchlock (gen_sprites2d look_variant)
        if wid in ("W130", "W157"):                          # Rensei's Rank 2 blade (Crane Ch2 end), the Hare: +crit
            x.setdefault("option", []).append({"LV": 1, "opttype": "opt_status", "propid": "CRI", "val": 15,
                                               "valtype": "supply"})
        if wid in ("W116", "W117", "W123", "W128"):
            x["price"] = int(atk * 10 * 1.25)
        w[wid] = x
    save("weapon", w)

    # ---- enemy.json (Crab Ch1 foes)
    e = load("enemy")
    gob = e["E001"]

    def enemy(eid, name, mdl, lv, hp, atk, df, agi, res, weak, desc, hsv=None, exp=8, money=12):
        x = copy.deepcopy(gob)
        x.update({"name": name, "mdlid": mdl, "LV": lv, "MAXHP": hp, "PATK": atk, "PDEF": df, "AGI": agi,
                  "RES": res, "desc": desc, "exp": exp, "money": money, "defskillid": "S003",
                  "option": [weak_opt(*weak)]})
        e[eid] = x

    enemy("E100", "Goblin", "EP106", 1, 40, 9, 6, 8, 2, ["Yari", "Jade", "Fire"],
          "A bakemono raider. Spears and jade make it squeal.")
    enemy("E101", "Goblin in a Hat", "EP100", 2, 90, 11, 8, 9, 3, ["Yari", "Jade", "Fire"],
          "The one with the straw hat. Very fetching. (Crab Ch1 tutorial)", exp=20, money=30)
    enemy("E102", "Nezumi Warrior", "EP101", 4, 70, 12, 8, 14, 2, ["Yari", "Fire", "Bo"],
          "A ratling who distrusts Squeak. Quick and nervous.")
    enemy("E103", "Cave Beetle", "EP102", 4, 80, 11, 16, 5, 3, ["Tetsubo", "Fire"],
          "Carapace shrugs off knives. Crush it.")
    enemy("E104", "Mamushi Viper", "EP103", 3, 45, 13, 5, 16, 2, ["Tanto", "Fire"],
          "Venomous and fast.")
    enemy("E105", "Tide Crab", "EP104", 3, 60, 10, 14, 6, 3, ["Tetsubo", "Earth"],
          "Pinches. Resists water.")
    # the rest of the Crab coast table (bestiary F "Kaiu Wall & Crab coast": Carrion Crow; rare Will-o'-wisp) and
    # the Hunting side path's boars (storyboard crab-ch1 R1)
    enemy("E107", "Carrion Crow", "EP437", 3, 35, 10, 4, 18, 1, ["Yumi", "Air"],
          "It wants your eyes. It'll settle for your rice ball.")
    enemy("E108", "Will-o'-wisp", "EP438", 6, 55, 12, 6, 14, 1, ["Water", "Bo"],
          "A hitodama: a soul-flame that leads travellers off the cliff path. Blades pass half through it.",
          exp=30, money=20)
    e["E108"]["option"].append({"opttype": "opt_elemdef", **{"EDR.%d" % ELEMS.index(n): 50
                                                            for n in ("Katana", "Yari", "Tanto", "Tetsubo", "Yumi",
                                                                      "Unarmed")}})
    enemy("E109", "Wild Boar", "EP439", 5, 110, 15, 9, 10, 3, ["Yari", "Yumi"],
          "Head down, tusks first. Taller than it looks when it's coming at you.")
    # Boss: the Grasping Paw (nezumi shaman), bosses.md §1 b_boss_grasping_paw (L7 HPx7 Resolve 6)
    enemy("E106", "Nezumi Shaman", "EP105", 7, 900, 17, 11, 12, 6, ["Yari", "Fire", "Bo"],
          "The tribe's shaman. Name-magic makes you forget your own name.", exp=120, money=150)
    e["E106"]["ai"][0]["cmds"] = [dict(e["E106"]["ai"][0]["cmds"][0], rate=60),
                                  dict(e["E106"]["ai"][0]["cmds"][0], skillid="S130", rate=40)]
    e["E106"]["item0"].update({"itemid": "A105", "rate": 100.0})          # Nezumi Bone Charm
    e["E106"]["item1"].update({"itemid": "I114", "rate": 100.0})          # steal: Painted Egg
    enemy("E121", "Seppun Ryozo", "EP348", 7, 260, 11, 9, 9, 4, ["Katana", "Water"],
          "An Imperial guardsman painting eggs in the dark. His Egg Rite works because they believe.", exp=60,
          money=0)
    e["E121"]["ai"][0]["cmds"] = [dict(e["E121"]["ai"][0]["cmds"][0], rate=40),
                                  dict(e["E121"]["ai"][0]["cmds"][0], skillid="S131", rate=60)]
    e["E121"]["item0"]["itemid"] = e["E121"]["item1"]["itemid"] = None
    # Gonta of the Hidden Ones: the S04 Sumai bout (b_hidden_ones_sumai). Only bare-handed throws break him.
    enemy("E120", "Gonta", "EP342", 5, 300, 17, 10, 7, 3, ["Unarmed"],
          "A mountain of a ronin. Doesn't talk to Crab dogs. Wrestles them.", exp=40, money=0)
    e["E120"]["item0"]["itemid"] = e["E120"]["item1"]["itemid"] = None          # a wrestling match, not a mugging
    # (user) the Sumai match: one enemy, renamed, redressed and scaled to Natsuko at run time (plugin ::Rokugan.sumaiMatch)
    enemy("E121", "Wrestler", "EP342", 5, 300, 17, 10, 7, 3, ["Unarmed"], "Belt, hips and the ground.", exp=0, money=0)
    e["E121"]["item0"]["itemid"] = e["E121"]["item1"]["itemid"] = None
    # Training target for automated Suki/Boost tests
    enemy("E190", "Straw-Hat Brute (training)", "EP100", 8, 30000, 14, 12, 6, 3, ["Yari", "Bo", "Fire"],
          "A sturdy test goblin for battle-system checks.", exp=1, money=1)
    # Human enemies (bestiary.md A1-A7) -> E200-E227, sprites EP400+ (tools/gen_human_enemies.py, same order)
    HPX = {}                                     # eid -> (HPx, ATKx) as designed, for the area tuning below
    humans = [  # name, level (mid of range), HPx, Resolve, weak
        ("Road Bandit", 4, 1.0, 2, ["Katana", "Yumi"]), ("Mountain Bandit", 21, 1.0, 3, ["Katana", "Yumi", "Fire"]),
        ("Bandit Captain", 31, 1.6, 5, ["Katana", "Air"]), ("Kolat-paid Brigand", 43, 1.4, 4, ["Tanto", "Yumi"]),
        ("Hungry Ronin", 5, 1.1, 3, ["Yari", "Yumi"]), ("Sword-for-Hire", 22, 1.2, 4, ["Yari", "Air"]),
        ("Wave-man Duelist", 32, 1.3, 5, ["Tanto", "Earth"]), ("Masterless Champion", 44, 1.6, 6, ["Yari", "Bo"]),
        ("Drunken Samurai", 6, 1.2, 3, ["Bo", "Water"]), ("Glory-Hungry Bushi", 22, 1.3, 4, ["Yari", "Air"]),
        ("Clan Duellist", 32, 1.4, 5, ["Yari", "Air"]), ("Hatamoto's Champion", 44, 1.6, 6, ["Tanto", "Water"]),
        ("Ashigaru Spearman", 5, 1.0, 3, ["Katana", "Tanto"]), ("Border Patrol", 21, 1.1, 3, ["Tanto", "Yumi"]),
        ("Sergeant of Spears", 31, 1.4, 5, ["Katana", "Fire"]), ("Heavy Infantry", 43, 1.6, 6, ["Tetsubo", "Bo"]),
        ("Dock Ruffian", 4, 1.0, 2, ["Bo", "Katana"]), ("Wako Raider", 22, 1.1, 3, ["Katana", "Yumi"]),
        ("Mantis Corsair", 32, 1.3, 4, ["Air", "Yari"]), ("Storm Legion Renegade", 44, 1.5, 5, ["Bo", "Air"]),
        ("Painted Cultist", 7, 1.0, 2, ["Water", "Bo"]), ("Blood-Hungry Acolyte", 22, 1.1, 3, ["Jade", "Water"]),
        ("Stitched-face Monk", 22, 1.0, 4, ["Tanto", "Fire"]), ("Maho-tsukai", 32, 1.3, 5, ["Jade", "Fire"]),
        ("Bloodspeaker Adept", 45, 1.6, 6, ["Jade", "Void"]), ("Shadow-in-Black", 23, 1.0, 3, ["Fire", "Yumi"]),
        ("Kolat Agent", 32, 1.1, 4, ["Jade", "Bo"]), ("Shosuro Renegade", 44, 1.2, 5, ["Fire", "Bo"]),
    ]
    for n, (name, lv, hpx, res, weak) in enumerate(humans):
        f = foe_stats(lv, hpx)
        HPX["E%03d" % (200 + n)] = (hpx, 1.0)
        enemy("E%03d" % (200 + n), name, "EP%03d" % (400 + n), lv, f["MAXHP"], f["PATK"], f["PDEF"], f["AGI"], res,
              weak, "See docs/rules/bestiary.md.", exp=6 + 3 * lv, money=10 + 4 * lv)
        e["E%03d" % (200 + n)]["MDEF"] = f["MDEF"]
    # Crab Ch1 regulars onto the same curve (user: random monsters reflect the expected party for the area, fixed per
    # area). They were hand-set for the first tutorial and barely scratched a Lv 3 Natsuko. Level and HPx from the
    # bestiary tier; the old hand values keep their shape (the beetle's armour, the viper's speed) as ratios.
    # The coast foes (Lv 2-3; E100 also runs the Lv 1 tutorial beside Ryoichi) stay "avg"; the gap is small there. The
    # Egg Caves and the boss (Lv 5-8, Natsuko solo or with Squeak) are tuned to a Crab.
    for eid, lv, hpx, vs in (("E100", 2, 0.8, "avg"), ("E107", 2, 0.5, "avg"), ("E105", 2, 0.7, "avg"),
                             ("E104", 4, 0.5, "crab"), ("E103", 5, 0.8, "crab"), ("E102", 5, 0.9, "crab"),
                             ("E109", 5, 1.2, "avg"), ("E108", 5, 0.5, "avg"), ("E106", 7, 7.0, "crab"),
                             ("E121", 7, 3.0, "crab")):
        x, f = e[eid], foe_stats(lv, hpx, vs=vs)
        HPX[eid] = (hpx, 1.0)
        old = foe_stats(x["LV"], 1.0)
        shape = {k: x[k] / max(1, old[k]) for k in ("PDEF", "AGI")}
        x.update({"LV": lv, "MAXHP": f["MAXHP"], "PATK": f["PATK"], "MDEF": f["MDEF"],
                  "PDEF": int(round(f["PDEF"] * min(1.6, max(0.5, shape["PDEF"] / 0.35)))),
                  "AGI": int(round(f["AGI"] * min(1.5, max(0.6, shape["AGI"] / 0.7)))),
                  "exp": max(x.get("exp") or 0, 6 + 3 * lv), "money": max(x.get("money") or 0, 10 + 4 * lv)})
    # ---- Crab Ch2: Kyuden Hida (production/crab-ch2.md; bosses.md §1; bestiary F "Kyuden Hida")
    def hum(eid, name, mdl, lv, hpx, res, weak, desc, atkx=1.0, **kw):
        HPX[eid] = (hpx, atkx)
        f = foe_stats(lv, hpx, atkx)
        enemy(eid, name, mdl, lv, f["MAXHP"], f["PATK"], f["PDEF"], f["AGI"], res, weak, desc,
              exp=kw.get("exp", 6 + 3 * lv), money=kw.get("money", 10 + 4 * lv))
        e[eid]["MDEF"] = f["MDEF"]
    hum("E230", "Goblin Warmonger", "EP110", 21, 1.0, 3, ["Jade", "Yari"], "A bakemono veteran in an iron hat. "
        "Frenzied.")
    hum("E231", "Goblin Experiment", "EP114", 21, 0.9, 3, ["Yari", "Jade"], "Escaped from the Kuni cells. Stitched, "
        "angry, and very fast.")
    hum("E232", "Cave Bat Swarm", "EP111", 21, 0.5, 1, ["Yumi", "Fire"], "A cloud of teeth. Screeches.")
    hum("E233", "Yurei", "EP112", 22, 1.1, 3, ["Water", "Void"], "A restless ghost. Blades pass half through her.")
    e["E233"]["option"].append({"opttype": "opt_elemdef", **{"EDR.%d" % i: 50 for i in range(6)}})
    hum("E237", "Drunken Samurai", "EP115", 20, 1.2, 3, ["Bo", "Water"], "The same drunk, twenty years and a "
        "promotion later.")
    hum("E236", "Shiba Noboru", "EP428", 22, 3.0, 5, ["Yari", "Air"], "Mutsuye's humble yojimbo. He fights to "
        "first blood, and he means it.", atkx=1.3, exp=180, money=0)
    hum("E235", "Maho Puppet", "EP429", 24, 11.0, 8, ["Jade", "Fire", "Yari"], "A kitchen servant with someone "
        "else's voice in his mouth.", atkx=1.15, exp=900, money=600)
    hum("E234", "Troll", "EP113", 24, 30.0, 99, [], "Chained in the donjon for the Kuni. Its chains were filed.",
        atkx=1.15, exp=0, money=0)
    hum("E238", "Daidoji Agent", "EP430", 20, 1.5, 3, ["Tanto", "Fire"], "A Crane Iron Warrior with a warrant "
        "for a deserter and no sense of humour.", atkx=1.05)
    hum("E239", "Matsu Braggart", "EP431", 19, 1.3, 3, ["Yari", "Air"], "A Lion who races the way he fights: early, "
        "loud and with his elbows.")
    # The Egg Caves after the nezumi (G049; user 2026-11-11: "re fill the different caves with progressively harder
    # creatures up to level 15 (so first cave 8-9, 2nd cave 10-12, 3rd cave 13-15)" - a place to level before the Hida
    # road, Lv 18+). gen_maps ENCOUNTERS M130 / M131 / M132.
    for eid, nm, mdl, lv, hpx, res, weak, desc in (
            ("E608", "Old Cave Beetle", "EP102", 9, 1.2, 3, ["Tetsubo", "Fire"], "Bigger than the ones before. The "
             "nezumi are gone, so it ate their scraps."),
            ("E609", "Pit Viper", "EP103", 8, 0.7, 2, ["Tanto", "Fire"], "Moved into the empty nests."),
            ("E610", "Goblin Scavenger", "EP106", 8, 0.9, 2, ["Yari", "Jade", "Fire"], "Picking through what the "
             "nezumi left."),
            ("E611", "Giant Cave Beetle", "EP102", 12, 1.4, 3, ["Tetsubo", "Fire"], "A carapace like a temple bell."),
            ("E612", "Mamushi Brood", "EP103", 11, 0.8, 2, ["Tanto", "Fire"], "A knot of vipers, all of them awake."),
            ("E613", "Goblin Raider", "EP110", 10, 1.0, 3, ["Yari", "Jade", "Fire"], "Iron hat, rusty spear, no "
             "manners."),
            ("E614", "Cave Bat Swarm", "EP111", 11, 0.5, 1, ["Yumi", "Fire"], "A cloud of teeth in the dark."),
            ("E615", "Armoured Beetle", "EP102", 15, 1.6, 4, ["Tetsubo", "Fire"], "Its shell turns spears. Crush "
             "it."),
            ("E616", "Mamushi Matriarch", "EP103", 13, 1.0, 3, ["Tanto", "Fire"], "The mother of the brood, and in "
             "a mood."),
            ("E617", "Goblin Sergeant", "EP110", 14, 1.2, 3, ["Yari", "Jade", "Fire"], "Shouts at the others. Hits "
             "harder than it shouts."),
            ("E618", "Great Bat Swarm", "EP111", 14, 0.6, 2, ["Yumi", "Fire"], "The whole roof comes down at you, "
             "squeaking.")):
        hum(eid, nm, mdl, lv, hpx, res, weak, desc)
    CH3 = -5                                   # CH3_LV_SHIFT (see NOTES); HPx tuned for Natsuko + 1-2 companions
    hum("E240", "Goblin Warmonger", "EP110", 31 + CH3, 0.6, 3, ["Jade", "Yari"], "Shadowlands-born, Taint in its "
        "teeth. Frenzied, and there are always more.")
    hum("E241", "Zombie", "EP432", 29 + CH3, 1.3, 3, ["Jade", "Fire"], "A dead man the Shadowlands kept walking. "
        "Slow; it doesn't let go.")
    hum("E242", "Onikage", "EP116", 32 + CH3, 1.2, 5, ["Jade", "Yari", "Fire"], "A demon horse: bone, shadow and "
        "a red eye. Very fast.")
    hum("E243", "Ogre", "EP118", 33 + CH3, 2.4, 5, ["Jade", "Yari"], "A slab of Shadowlands muscle with a club.",
        atkx=1.2)
    hum("E244", "Toothed Poppy", "EP117", 28 + CH3, 0.6, 2, ["Fire", "Katana"], "A red flower with teeth. It turns "
        "to follow you.")
    hum("E245", "Moto Akutsukai", "EP434", 34 + CH3, 3.2, 6, ["Jade", "Fire", "Bo"], "A dead Unicorn rider on "
        "skeletal wings. It hunts by sight.", atkx=1.15)
    hum("E246", "Maho-bujin", "EP433", 33 + CH3, 0.9, 4, ["Yari", "Katana"], "A maho-warrior in stolen Crab armour.")
    hum("E247", "Oni no Kommei", "EP435", 35 + CH3, 4.0, 12, ["Jade", "Tetsubo", "Fire"], "A patrol leader with a "
        "second face on the back of its head. Every third turn it swaps two travelers' commands.", atkx=1.1,
        exp=1400, money=900)
    e["E247"]["option"].append({"opttype": "opt_elemdef", "EDR.%d" % ELEMS.index("Water"): 50})
    hum("E248", "The Other Face", "EP119", 35 + CH3, 0.8, 4, ["Jade", "Katana", "Yumi"], "The face on the back of "
        "the Kommei's head. Break it and the swaps stop.", exp=200, money=0)
    CH4 = -8                    # CH4_LV_SHIFT: designed Lv 41-46, Natsuko arrives ~32-34 (+ Sachiko and Goro)
    hum("E250", "Bakemono Wolf-rider", "EP436", 42 + CH4, 1.4, 5, ["Jade", "Yari"], "A goblin on a Shadowlands "
        "wolf. Kill the wolf and the goblin falls; kill the goblin and the wolf goes mad.")
    hum("E251", "Goblin Warmonger", "EP110", 42 + CH4, 0.8, 3, ["Jade", "Yari"], "Up the ladders with a knife in "
        "its teeth.")
    hum("E252", "Maho-bujin", "EP433", 43 + CH4, 1.0, 4, ["Yari", "Katana"], "Blood-sorcery in Crab armour, "
        "inside the castle walls.")
    hum("E253", "Cellar Ogre", "EP124", 45 + CH4, 7.0, 6, ["Jade", "Tetsubo"], "It broke through to the cellar "
        "stair and it wants the courtiers. Draw it off them.", atkx=1.6)
    hum("E254", "Ogre", "EP118", 44 + CH4, 2.2, 5, ["Jade", "Yari"], "A slab of Shadowlands muscle on the wrong "
        "side of the Wall.", atkx=1.15)
    hum("E255", "Oni no Tsukakoro", "EP125", 45 + CH4, 24.0, 14, ["Tetsubo", "Jade", "Earth"], "A bone-cage full of "
        "tentacles that bounces like a monstrous ball. Its bounces chain from traveler to traveler.", atkx=1.4,
        exp=0, money=1400)
    e["E255"]["option"].append({"opttype": "opt_elemdef", "EDR.%d" % ELEMS.index("Air"): 50,
                                "EDR.%d" % ELEMS.index("Tanto"): 50})
    e["E255"]["item0"].update({"itemid": "I138", "rate": 100.0})              # drop: Bone-cage Fragment
    hum("E256", "Wall Troll", "EP121", 40 + CH4, 6.0, 5, ["Jade", "Fire", "Katana"], "A troll that climbed the "
        "Wall in the night and went for the nearest watchtower. Bent swords bother it.", atkx=1.3, money=300)
    # ---- Crane Ch1 "Heaven's Glory" (bosses.md §2; production/crane-ch1.md). Sprites: gen_human_enemies EP by key.
    import gen_human_enemies as _he
    hum("E300", "Senior Student", _he.EP["kakita_senior"], 1, 1.6, 3, ["Tanto", "Air"], "A Kakita senior with a "
        "bokken and a big mouth. The graduation bout (b_bokken_bout).", exp=30, money=0)
    e["E300"]["item0"]["itemid"] = e["E300"]["item1"]["itemid"] = None        # a bout, not a mugging
    hum("E302", "Grey Wolf", "EP440", 4, 0.8, 2, ["Yari", "Fire", "Yumi"], "Lean and grey, and never alone.")
    hum("E301", "Forest Bandit", _he.EP["forest_bandit"], 5, 1.0, 2, ["Katana", "Yumi"], "One of the Green Ronin's "
        "people: a farmer with a stick and a straw hat. Surrenders when hurt (b_forest_bandits_a/b).")
    e["E301"]["rt_surrender"] = 30                  # plugin RokuganHazard: gives up at 30% HP (forest_village_spared)
    # Boss: Kakita Yasurugi (bosses.md §2: L 8, HPx 7, Resolve 8; weak Yari, Tanto, Air; resists Katana). Phase 1 is
    # the duel (plugin RokuganHazard YASURUGI), phase 2 the skirmish.
    hum("E313", "Kakita Yasurugi", "EP126", 8, 4.5, 8, ["Yari", "Tanto", "Air"], "Silent, inhumanly calm. He "
        "hesitated once, to cut a peasant. Never again.", exp=300, money=0)
    f8 = foe_stats(8, 7.0, 1.0, vs="crane")
    e["E313"]["PATK"] = f8["PATK"]
    e["E313"]["option"].append({"opttype": "opt_elemdef", "EDR.%d" % ELEMS.index("Katana"): 50})
    e["E313"]["item0"]["itemid"] = None
    e["E313"]["item1"].update({"itemid": "A117", "rate": 100.0})             # steal: Yasurugi's Spare Hilt-wrap
    # ---- Crane Ch2 "The Iron Cranes" (bosses.md b_camp_sentries, b_boss_iron_cranes): Miyako's charmed (rt_charmed:
    # 1 sentry, 2 general; plugin RokuganHazard frees them on Suki and heals the generals each turn)
    hum("E314", "Seduced Sentry", _he.EP["seduced_sentry"], 22, 1.0, 3, ["Katana", "Bo"], "A Daidoji sentry with "
        "glazed eyes. The lady said the Crab come at dawn.")
    e["E314"]["rt_charmed"] = 1
    hum("E315", "Daidoji General", _he.EP["charmed_general"], 25, 3.0, 4, ["Yari", "Tanto", "Water"], "An Iron Crane general, held by "
        "Miyako's charm. She heals him while he fights. Break him to free him.", exp=180, money=0)
    e["E315"]["rt_charmed"] = 2
    e["E315"]["PATK"] = int(e["E315"]["PATK"] * 0.85)     # two travelers (Rensei + Goro): freeing three takes time
    e["E315"]["item0"]["itemid"] = e["E315"]["item1"]["itemid"] = None
    # Doji Miyako watches from the ridge (boss art EP127): untargetable, she only heals her generals (the hold) and
    # leaves once none is left fighting (plugin RokuganHazard rt_watcher)
    hum("E326", "Doji Miyako", "EP127", 30, 50.0, 99, [], "The woman in white, on the ridge. She never fights. She "
        "never risks herself.", exp=0, money=0)
    e["E326"]["rt_watcher"] = 1
    e["E326"]["item0"]["itemid"] = e["E326"]["item1"]["itemid"] = None
    # ---- Crane Ch3 "The White Squid" (bosses.md; bestiary A5/B5). Rensei sails alone (a Call guest and a hireling):
    # HPx is the solo share of the design value; the false charms (plugin RokuganHazard) do the rest.
    hum("E327", "Chihaya the Quick", "EP128", 31, 4.0, 4, ["Yumi", "Air"], "A barefoot ronin who walks on mooring "
        "ropes. Her charm makes her hard to hit; break her to shatter it.", exp=1200, money=0)
    e["E327"]["AGI"] = int(e["E327"]["AGI"] * 1.5)       # Resolve 4, not bosses.md's 7: the charm tutorial must be
                                                         # breakable by one hireling (2 weak hits per call, 3 calls)
    e["E327"]["rt_charm"] = "K044"
    e["E327"]["item0"]["itemid"] = None                                      # Tadanobu's Letters: the S03 scene
    e["E327"]["item1"].update({"itemid": "A121", "rate": 100.0})             # steal: Chihaya's Charm
    hum("E328", "Yosuke the Bold", "EP129", 33, 4.0, 7, ["Katana", "Water"], "The second brother, laughing at the "
        "prow in a storm. He fights like the deck is his.", exp=1400, money=1200)
    e["E328"]["rt_captain"] = True                                           # his crew flee when he falls
    e["E328"]["rt_broadside"] = True                                         # Tessai's archers loose on turn 2 (F-1)
    e["E328"]["item0"]["itemid"] = e["E328"]["item1"]["itemid"] = None
    hum("E330", "Katsuo the White Brother", "EP130", 35, 6.0, 12, ["Jade", "Katana", "Fire"], "An albino maho-tsukai "
        "who paints charms in his own blood. Every turn he hands one out.", exp=0, money=2500)
    e["E330"]["rt_charmer"] = e["E330"]["rt_captain"] = True                # (and his crew, and Ryohei, give up)
    e["E330"]["item0"].update({"itemid": "A122", "rate": 100.0})             # drop: White Squid Pearl
    e["E330"]["item1"].update({"itemid": "A123", "rate": 100.0})             # steal: Blood-ink Brush
    hum("E331", "Ryohei the Eldest", _he.EP["ryohei"], 34, 3.5, 8, ["Katana", "Bo"], "The eldest brother: a Mantis "
        "tactician, tired, with a nunchaku. He offered you a way out.", exp=900, money=0)
    e["E331"]["item0"]["itemid"] = e["E331"]["item1"]["itemid"] = None
    hum("E334", "Sea Serpent Eel", "EP441", 31, 1.3, 4, ["Air", "Yari"], "A long grey eel that rises out of the "
        "swell and wraps the rail.")
    e["E334"]["option"].append({"opttype": "opt_elemdef", "EDR.%d" % ELEMS.index("Water"): 50})
    hum("E337", "Umibozu Shade", "EP442", 34, 2.0, 6, ["Fire", "Void"], "A bald head the size of a hill, rising out "
        "of a storm. Blades pass half through it.")
    e["E337"]["option"].append({"opttype": "opt_elemdef", "EDR.%d" % ELEMS.index("Water"): 50,
                                **{"EDR.%d" % i: 50 for i in range(6)}})
    # ---- Crane Ch4 "The Play No One Performs" (bestiary D tsukumogami; bosses.md). Rensei alone again (a Call guest,
    # a hireling); the archive row is solo-tuned below (AREA).
    hum("E342", "Paper-spirit", "EP443", 41, 0.6, 2, ["Fire", "Tanto"], "A sheet of forbidden text that got up and "
        "walked. Its edges are very sharp.")
    hum("E343", "Ink-pot Spirit", "EP444", 42, 0.9, 3, ["Fire", "Bo"], "An ink pot four hundred years old, still full. "
        "It throws.")
    e["E343"]["option"].append({"opttype": "opt_elemdef", "EDR.%d" % ELEMS.index("Water"): 50})
    hum("E344", "Lantern Spirit", "EP445", 43, 0.8, 3, ["Water", "Yumi"], "A paper lantern with a grin and a tongue. "
        "The censor-monks swear they never light it.")
    e["E344"]["option"].append({"opttype": "opt_elemdef", "EDR.%d" % ELEMS.index("Fire"): 50})
    hum("E346", "Shelf Kami", "EP132", 43, 4.0, 6, ["Fire", "Void"], "A Doji ancestor, set to guard shelf nine. It "
        "does not approve of you.", exp=0, money=0)
    e["E346"]["item0"]["itemid"] = e["E346"]["item1"]["itemid"] = None
    # ---- Lion Ch1 "The Blood of Family" (bosses.md §3 b_warehouse_raid: Phoenix guard x3, L1, Resolve 2, weak
    # Katana, Yari: the Command tutorial)
    hum("E348", "Phoenix Guard", _he.EP["phoenix_guard"], 1, 0.9, 2, ["Katana", "Yari"], "A Shiba ashigaru guarding "
        "Phoenix rice warehouses. Rice meant for the Crane army.")
    # b_nagai_possessed (L6 HPx4 Res6, weak Jade + Water; drop Matsu Sensei's Bokken) and the Duels (Shizue's path
    # action; rt_duel: no seconds, and a lethal blow makes them yield). Lion-side duelists are weak to Yari and Air.
    hum("E349", "Possessed Matsu Nagai", _sc_epid("nagai"), 6, 4.0, 6, ["Jade", "Water"], "The visiting Matsu sensei, "
        "with many voices in his mouth. Break the possession to save him.", exp=200, money=0)
    e["E349"]["item0"].update({"itemid": "W136", "rate": 100.0})               # drop: Matsu Sensei's Bokken
    e["E349"]["mdlid"] = "EP135"                                              # boss art (gen_bossart): mini-boss
    # b_boss_otamai (bosses.md: L9 HPx8 Res8, weak Jade/Fire/Katana; the red-shadow oni's soul damage; 3 jade chains =
    # victory). Shizue alone (a guest, a hireling): Resolve 4, so three breaks are 12 weak hits, not 24. He cannot die
    # before the third chain (plugin rt_chains). E360 is the harder copy (Hojiki went to the Phoenix: no host ready).
    hum("E358", "O-Tamai", "EP133", 9, 6.0, 2, ["Jade", "Fire", "Katana"], "A Bloodspeaker, the beloved of Iuchiban, "
        "in a borrowed body. Break him to bind a jade chain; three chains hold him.", exp=0, money=600)
    e["E358"]["rt_chains"] = 3
    e["E358"]["rt_captain"] = True
    e["E358"]["item0"].update({"itemid": "I154", "rate": 100.0})              # drop: Jade Chain Fragment
    e["E358"]["item1"].update({"itemid": "I155", "rate": 100.0})              # steal: Bloodspeaker's Ring
    e["E360"] = copy.deepcopy(e["E358"])
    HPX["E360"] = (7.5, 1.1)
    hum("E359", "Red-shadow Oni", "EP134", 9, 2.0, 4, ["Jade", "Fire"], "A shadow that crawls up behind its master. "
        "It eats the breath, not the blood.", exp=0, money=0)
    # ---- Lion Ch2 "Shadow of a Doubt" (bosses.md §3: the bracket L20-22 Res 3/4/6; b_fear_shades L22; b_boss_ianwa L25
    # HPx7 Res10, no attacks of its own, charm, flees at the first Suki). Shizue alone (+ a guest, a hireling).
    for eid, nm, key, lv, hpx, res, weak in (("E361", "Ikoma Bard", "ikomabard", 20, 1.6, 3, ["Katana", "Air"]),
                                             ("E362", "Matsu Duellist", "matsuduel", 21, 2.0, 4, ["Yari", "Water"]),
                                             ("E363", "Kaiu Yutaka", "yutaka", 22, 2.6, 5, ["Air", "Tanto"])):
        hum(eid, nm, _sc_epid(key), lv, hpx, res, weak, "The bokken tournament: first blood, no seconds.",
            exp=40 * lv, money=0)
        e[eid]["rt_duel"] = True
        e[eid]["item0"]["itemid"] = e[eid]["item1"]["itemid"] = None
    e["E363"]["PDEF"] = int(e["E363"]["PDEF"] * 1.25)                         # he never moves his feet
    hum("E364", "Fear Shade", "EP446", 22, 0.8, 3, ["Jade", "Fire"], "Ianwa's leavings: a crawling shape of dread. "
        "Blades pass half through it.")
    e["E364"]["option"].append({"opttype": "opt_elemdef", **{"EDR.%d" % i: 50 for i in range(6)}})
    hum("E365", "Oni no Ianwa", "EP136", 25, 5.0, 5, ["Jade", "Fire"], "A cowardly oni the size of a horse. It has "
        "no attacks of its own: it charms. At its first Suki it flees.", exp=0, money=0)
    e["E365"].update({"rt_charmer_ally": True, "rt_coward": True, "rt_captain": True})
    e["E365"]["item0"].update({"itemid": "I158", "rate": 100.0})              # drop: Kafu's Love Letters
    e["E365"]["item1"].update({"itemid": "A132", "rate": 100.0})              # steal: Coward's Tooth
    # ---- Lion Ch3 "The Deadly Message" (bosses.md: b_bridge_bandit L30 Res5 Duel; b_pass_ronin L32 Res4, surrender;
    # b_shogen_test L34 Res8 Duel (route A); b_boss_miya_killers L35: duelist HPx8 Res10 + archers HPx3 Res4)
    hum("E372", "Bandit Chief", "EP402", 30, 6.0, 5, ["Katana", "Yari"], "He collects a toll from people who have "
        "nothing. A duel: first blood.", atkx=1.25, exp=600, money=0)
    e["E372"]["rt_duel"] = True
    e["E372"]["item0"]["itemid"] = e["E372"]["item1"]["itemid"] = None
    hum("E373", "Pass Ronin", "EP405", 32, 1.2, 4, ["Yari", "Yumi"], "\"Bandits\" in good boots. Paid in Imperial "
        "coin. They surrender at low HP.")
    e["E373"]["rt_surrender"] = 30
    e["E373"]["rt_mercy"] = "Enough! We yield! We were only paid to take a tube!"
    hum("E374", "Akodo Shogen", _sc_epid("shogen"), 34, 10.0, 8, ["Air", "Tanto"], "The old man of Kaze-no-Tani. "
        "Pain, he says, is a rumour.", atkx=1.5, exp=1200, money=0)
    e["E374"]["rt_duel"] = True
    e["E374"]["item0"]["itemid"] = e["E374"]["item1"]["itemid"] = None
    hum("E375", "Seppun-trained Duelist", "EP137", 35, 6.5, 10, ["Yari", "Tanto", "Earth"], "A tall man with a long, "
        "perfect blade. His order: the message never arrives.", exp=0, money=1800)
    e["E375"]["rt_captain"] = True
    e["E375"]["item0"].update({"itemid": "I160", "rate": 100.0})              # drop: Miya Letters (more of them)
    e["E375"]["item1"].update({"itemid": "I161", "rate": 100.0})              # steal: Duelist's Inro
    hum("E376", "Miya Archer", _he.EP["miya_archer"], 33, 2.0, 4, ["Katana", "Air"], "An archer on the rocks above, "
        "in no colours at all.", atkx=0.7)
    # ---- Lion Ch4 "Sorrow's Path" (bosses.md: b_gusai_duel L42 Res6 Duel; b_ford_waves_1-5 L42-44 Res3-5;
    # b_boss_rokuro_demon L45 Res16 (8 here: a lone traveler), weak Jade/Yari/Water/obsidian)
    hum("E381", "Matsu Berserker", _he.EP["matsu_berserker"], 42, 1.3, 3, ["Bo", "Yari"], "A Matsu who charged the "
        "ford by mistake. Knock him down; don't kill your own.", atkx=0.4)
    hum("E382", "Matsu Berserker", _he.EP["matsu_berserker"], 42, 1.3, 2, ["Bo", "Yari"], "A Matsu who charged the "
        "ford by mistake. Matsu Joruri's victory stone told you where he'd break.", atkx=0.4)
    for eid in ("E381", "E382"):
        e[eid].update({"rt_surrender": 40, "rt_killflag": "G577",
                       "rt_mercy": "...Akodo-sama? Why are we in the river? Why was I so afraid?"})
    hum("E383", "Crane Rider", "EP430", 43, 1.3, 4, ["Yari", "Yumi"], "The Crane counter-charge. They fall back when "
        "beaten. Don't pursue.", atkx=0.4)
    e["E383"].update({"rt_surrender": 25, "rt_mercy": "Fall back! Back to the bank! They're not following!"})
    hum("E384", "Crane Archer", _he.EP["crane_archer"], 43, 1.0, 3, ["Katana", "Air"], "Archers on the far bank, "
        "shooting into the mist.", atkx=0.5)
    hum("E385", "Burning Bridge", "EP447", 43, 2.5, 2, ["Yari", "Water"], "The old bridge, burning. Push the burning "
        "timbers into the river: a spear does it best.", atkx=0.4, exp=0, money=0)
    hum("E388", "Matsu Rokuro", "EP138", 45, 9.0, 8, ["Jade", "Yari", "Water"], "The Matsu champion, ridden by a "
        "Fear-demon. Its eyes are black and wide. Obsidian strips its guard, at a price.", exp=0, money=2400)
    e["E388"]["rt_obsidian_weak"] = True
    e["E388"]["item0"].update({"itemid": "I164", "rate": 100.0})              # drop: Rokuro's Gratitude
    e["E388"]["item1"].update({"itemid": "A134", "rate": 100.0})              # steal: Demon's Shadow
    hum("E389", "Akodo Gusai", _sc_epid("gusai"), 42, 7.0, 6, ["Yari", "Air"], "Your cousin. He started this war "
        "in one night. A duel: first blood, nobody dies.", atkx=1.1, exp=1500, money=0)
    hum("E390", "Matsu Berserker", _he.EP["matsu_berserker"], 42, 6.0, 4, ["Bo", "Yari"], "A Matsu who wants a "
        "duel before dawn. First blood.", atkx=1.2, exp=900, money=0)
    for eid in ("E389", "E390"):
        e[eid]["rt_duel"] = True
        e[eid]["item0"]["itemid"] = e[eid]["item1"]["itemid"] = None
    # ---- Phoenix Ch1 "The Silent Kami" (bosses.md: b_shrine_guardian_shards L5 Res3 weak Water/Bo; b_ashimoshi L7
    # HPx5 Res6 weak Water/Void, physical halved, Silent Wind every other turn, drop Hurricane Bead). Haruki alone
    # (+ Ashimita as the guest, a hireling).
    hum("E394", "Guardian-stone", "EP448", 5, 1.2, 3, ["Water", "Bo"], "A shard of the broken shrine's stone guardian, "
        "lurching upright. It doesn't know the shrine is gone.", atkx=0.8)
    hum("E395", "Ashimoshi", "EP139", 7, 5.0, 6, ["Water", "Void"], "A samurai's ghost in a silent hurricane. Blades "
        "pass half through him. Every other turn his wind seals spells.", exp=0, money=300)
    e["E395"]["option"].append({"opttype": "opt_elemdef", **{"EDR.%d" % i: 50 for i in range(6)}})
    e["E395"]["rt_silentwind"] = True
    e["E395"]["item0"].update({"itemid": "A136", "rate": 100.0})              # drop: Hurricane Bead
    e["E395"]["item1"]["itemid"] = None
    # the shared climax for a shugenja and his yojimbo (user): Resolve 4, not the 2 a lone Shizue needed
    e["E399"] = copy.deepcopy(e["E358"])
    HPX["E399"] = HPX["E358"]
    e["E399"]["RES"] = 4
    # ---- Phoenix Ch2 "The Silent Court" (bosses.md: b_pass_cultists L22 Kokujin cultist x4 Res3 weak Water/Bo/Air,
    # they give up if Hioninmaru flees; b_boss_hioninmaru L25 HPx7 Res10 weak Jade/Water/Void, maho pays HP, Taint on
    # hit, a coward who loses Resolve once his cultists fall). Haruki + Ashimita (+ Yosai, + a hireling).
    hum("E400", "Painted Cultist", _he.EP["painted_cultist"], 22, 1.2, 3, ["Water", "Bo", "Air"], "One of Kokujin's "
        "peasants, with the Togashi tattoos painted on wrong. Fights in a frenzy.", atkx=0.8)
    hum("E401", "Hioninmaru", _he.EP["bloodspeaker"], 22, 2.0, 3, ["Jade", "Water", "Void"], "A thin man in red at the "
        "back of the mob, gesturing, sweating. He'll run the moment it turns.", atkx=0.6, exp=300, money=200)
    e["E401"].update({"rt_coward": True, "rt_captain": True})
    e["E401"]["item0"]["itemid"] = e["E401"]["item1"]["itemid"] = None
    hum("E402", "Hioninmaru", "EP140", 25, 9.0, 8, ["Jade", "Water", "Void"], "Kokujin's bloodspeaker, back for the "
        "Consumer scroll. His maho costs him blood; his blood Taints. Without his cultists he loses his nerve.",
        atkx=0.9, exp=0, money=1200)
    e["E402"].update({"rt_fearful": True, "rt_gold": 2})          # (user) "I have gold!" buys his cultists back twice
    e["E402"]["item0"]["itemid"] = None
    e["E402"]["item1"].update({"itemid": "I170", "rate": 100.0})              # steal: Bloodspeaker Tattoo-ink
    # ---- Phoenix Ch3 "The Darkfever" (bosses.md: b_forest_fever_spirits L32 Res3 weak Water/Jade; b_mieko_dark_mid
    # L33 HPx5 Res9 weak Water/Void, flees at 50%; b_boss_oni_no_kuzushi L35 HPx11 Res14 (+1 stayed) weak Jade/Water/
    # Bo, Unbalancing Breath, Darkfever aura). Haruki + Ashimita (+ Yosai, + a hireling).
    hum("E405", "Fever Spirit", "EP449", 32, 1.1, 3, ["Water", "Jade"], "Bruised smoke from the Darkfever, drifting "
        "between the trees. Its touch burns.", atkx=0.8)
    hum("E406", "Gaki", "EP160", 31, 1.0, 3, ["Jade", "Fire"], "A hungry ghost, drawn to the dying villages.", atkx=0.8)
    hum("E407", "Tsuchigumo", "EP161", 33, 1.4, 4, ["Fire", "Yari"], "An earth spider with a demon's face on its back. "
        "It webs the old shrines.", atkx=0.85)
    hum("E408", "Mieko (dark half)", "EP142", 33, 7.0, 6, ["Water", "Void"], "Isawa Mieko's other half, black-glass "
        "eyes. She came back to where she was broken. She'll run at half her strength.", exp=0, money=0)
    e["E408"]["rt_flee_pct"] = 50
    e["E408"]["item0"]["itemid"] = e["E408"]["item1"]["itemid"] = None
    hum("E409", "Oni no Kuzushi", "EP141", 35, 8.0, 10, ["Jade", "Water", "Bo"], "Like a body falling down stairs "
        "forever. Every second turn its breath knocks a traveler Off-Balance and it steadies itself (+2 Resolve). The "
        "Darkfever burns everyone near it.", exp=0, money=3000)
    e["E409"].update({"rt_unbalance": True, "rt_fever": 0.06})
    e["E409"]["item0"].update({"itemid": "A138", "rate": 100.0})              # drop: Cracked Seal Shard
    e["E409"]["item1"].update({"itemid": "I175", "rate": 100.0})              # steal: Fever-black Pearl
    e["E410"] = copy.deepcopy(e["E409"])                # "stay one more day": the oni grew while Haruki was kind
    HPX["E410"] = HPX["E409"]
    e["E410"]["RES"] = 11
    # ---- Dragon Ch2 "The Painting" (production dragon-ch2.md; bestiary F "Tortoise Island & cove" 20-25): the cove's
    # kappa (the Bow: instant Suki) and fixed fights (b_cove_crabs, b_cove_guards: Akuro's hypnotised guards); the boss
    # b_boss_ushimo (Resolve 10, weak Bo/Yari/Water; don't kill him: plugin rt_ushimo). Gendo alone (+ the Momo guest).
    hum("E430", "Kappa", "EP459", 21, 1.1, 4, ["Fire"], "A river imp with a dish of water on its head. Bow to it: "
        "it must bow back, and the water spills out. (the Bow: instant Suki)")
    e["E430"]["rt_kappa"] = True
    hum("E434", "Hypnotised Guard", _he.EP["ashigaru"], 22, 1.3, 4, ["Katana", "Water"], "One of Akuro's guards, dull "
        "eyed: \"...the end of your rope...\" Interrogate cuts the sentence.")
    e["E434"]["rt_hypno"] = True
    hum("E435", "Seppun Ushimo", "EP143", 25, 7.0, 10, ["Bo", "Yari", "Water"], "An Imperial guard of the year 400. "
        "Perfect iaijutsu. He wants to die; don't let him. (Below 25%: break him or Subdue him)", atkx=1.2,
        exp=0, money=0)
    e["E435"]["rt_ushimo"] = True
    # ---- Dragon Ch3 "Past Mistakes" (production dragon-ch3.md; bestiary E "the past" + F "Year 400 capital & coast"):
    # deserter palace guards, gaijin pikemen and musketeers; b_boss_parley: the vanguard captain (Res 12, weak Katana/
    # Water/Air; when he falls the rest give up, rt_captain) beside Togashi Akuro, who can't be beaten (rt_untouchable:
    # hits do nothing; the Wasp tattoo: two actions a turn).
    hum("E436", "Palace Guard", _he.EP["palace_deserter"], 30, 1.1, 3, ["Bo", "Yari"], "A palace guard with a straight "
        "tachi, deserted when the gaijin landed. Resists Katana.")
    e["E436"]["option"].append({"opttype": "opt_elemdef", "EDR.%d" % ELEMS.index("Katana"): 50})
    hum("E437", "Gaijin Pikeman", _he.EP["gaijin_pikeman"], 31, 1.2, 4, ["Tanto", "Air"], "A foreign soldier behind a "
        "very long pike. Resists Yari.")
    e["E437"]["option"].append({"opttype": "opt_elemdef", "EDR.%d" % ELEMS.index("Yari"): 50})
    hum("E438", "Gaijin Musketeer", _he.EP["gaijin_musketeer"], 32, 1.0, 4, ["Yari", "Bo"], "A foreign soldier with a "
        "smoking tube that throws lead. (Using a dropped musket: History -15)")
    hum("E440", "Vanguard Captain", _he.EP["gaijin_captain"], 35, 6.0, 12, ["Katana", "Water", "Air"], "The gaijin "
        "vanguard's captain, with a broadsword. When he falls, his men give up.", atkx=1.15, exp=0, money=0)
    e["E440"]["rt_captain"] = "The powder room explodes. When the smoke clears, Akuro is gone."
    hum("E441", "Togashi Akuro", "EP144", 40, 3.0, 9, [], "An old ise zumi who wears faces. The Crab tattoo takes his "
        "wounds; the Wasp gives him a second blow. He can't be beaten: fell the vanguard captain.", atkx=0.8,
        exp=0, money=0)
    e["E441"].update({"rt_untouchable": True, "RES": 9})
    # ---- Dragon Ch4 "The Battle of the White Stag" (production dragon-ch4.md; bestiary F "Year 400 capital & coast"
    # IV): the three fronts (b_front_land: hold 6 turns, rt_hold; b_front_mantis: Iami's champion, a duel;
    # b_front_lighthouse: Gusai marines, Sanro escorted), the harbour musketeers, and the boss b_boss_kumpei_flagship
    # (Kumpei Res 14, weak Katana/Water/Air; plugin rt_kumpei: cannons, the sigil, the vial). Gendo + Togashi Yosai.
    hum("E445", "Gusai Mantis Marine", _he.EP["mantis_corsair"], 43, 1.3, 5, ["Air", "Katana"], "A Gusai marine with "
        "a boarding axe, paid in gaijin silver. Resists Water.")
    e["E445"]["option"].append({"opttype": "opt_elemdef", "EDR.%d" % ELEMS.index("Water"): 50})
    hum("E446", "Gaijin Vanguard", _he.EP["gaijin_pikeman"], 42, 3.0, 6, ["Tanto", "Air"], "The gaijin pike wall, "
        "pushing up the hill. Hold for six turns and the relief arrives.", atkx=0.9)
    e["E446"]["rt_hold"] = 6
    hum("E447", "Iami's Champion", _sc_epid("mbushi"), 43, 5.0, 8, ["Air", "Katana"], "Gusai Iami's hired blade. A "
        "duel: no seconds.", atkx=1.1, exp=0, money=0)
    e["E447"]["rt_duel"] = True
    hum("E448", "Kakita Kumpei", "EP145", 45, 8.0, 14, ["Katana", "Water", "Air"], "The failed artist, painting at the "
        "rail with the last vial of kami-ichor at his hip. Break him before the 8th round, or the vial goes "
        "overboard.", atkx=1.0, exp=0, money=0)
    e["E448"]["rt_kumpei"] = True
    for eid in ("E446", "E447", "E448"):
        e[eid]["item0"]["itemid"] = e[eid]["item1"]["itemid"] = None
    # (the Wasp's second blow is the Wasp Sting skill: two hits; one action a turn so a lone Gendo can stand)
    for eid in ("E440", "E441"):
        e[eid]["item0"]["itemid"] = e[eid]["item1"]["itemid"] = None
    for eid in ("E434", "E435"):
        e[eid]["item0"]["itemid"] = e[eid]["item1"]["itemid"] = None
    # ---- Dragon Ch1 "Under the Skin" (bosses.md / script: b_dock_tutorial; b_gusai_thugs_a/b kama thugs weak Bo/
    # Katana; b_boss_tide: hypnotised ronin shugenja x2 Res5 weak Air/Bo + Mantis thugs Res3 weak Katana/Yari, the tide
    # timer). Gendo alone, then with Togashi Yosai (the story companion here), a guest (Momo), a hireling.
    hum("E421", "Drunk Sailor", _he.EP["dock_ruffian"], 1, 1.0, 2, ["Bo", "Katana"], "He swings a gaff at anyone who "
        "stares. Gendo was deducing.", atkx=0.7)
    hum("E422", "Kama Thug", _he.EP["mantis_corsair"], 5, 1.0, 3, ["Bo", "Katana"], "One of Tadayasu's Storm Legion "
        "thugs, kama in each hand. Told to put the fish back in the water.", atkx=0.8)
    hum("E425", "Kama Thug", _he.EP["mantis_corsair"], 6, 1.1, 3, ["Bo", "Katana"], "One of Tadayasu's Storm Legion "
        "thugs, kama in each hand.", atkx=0.8)
    hum("E423", "Hypnotised Shugenja", _he.EP["stitched_monk"], 8, 1.6, 5, ["Air", "Bo"], "A ronin shugenja with dull "
        "eyes, murmuring the same sentence. While the callers stand, the tide comes in. Interrogate cuts the "
        "sentence.", atkx=0.8)
    e["E423"].update({"rt_tidecaller": True, "rt_hypno": True})
    hum("E424", "Mantis Thug", _he.EP["dock_ruffian"], 7, 1.0, 3, ["Katana", "Yari"], "A Mantis thug with the same "
        "dull eyes and the same sentence.", atkx=0.8)
    for eid in ("E421", "E422", "E425", "E423", "E424"):
        e[eid]["item0"]["itemid"] = e[eid]["item1"]["itemid"] = None
    # ---- Scorpion Ch1 "Blood and Iron" (bosses.md: b_road_bandits L2 Res2 weak Tanto/Yumi, the Steal tutorial;
    # b_kommei_brood L5 HPx4 Res6 weak Jade/Fire, one command swap; b_marsh_leeches L6 Res2 weak Fire/Jade;
    # b_boss_kansen_hana L8 HPx7 weak Air/Water/Crystal, physical halved, the ritual counter). Mitsue alone, then with
    # Yoritomo Rui (S05 on).
    hum("E449", "Road Bandit", _he.EP["road_bandit"], 2, 0.9, 2, ["Tanto", "Yumi"], "\"Hand over the purse, pretty!\" "
        "He has a purse of his own, very loosely tied.", atkx=0.7)
    hum("E455", "Kommei-brood Oni", "EP123", 5, 4.0, 6, ["Jade", "Fire"], "The thing that wore the Kitsune governor, "
        "face slipping, standing on the river. Its breath makes you forget who you are.", atkx=0.9, exp=0, money=0)
    e["E455"]["rt_kommei_once"] = True
    hum("E456", "Blood Leech", "EP163", 5, 0.8, 2, ["Fire", "Jade"], "A leech as long as a dog, from the marsh that "
        "used to be a wood. Salt makes it let go.", atkx=0.8)
    hum("E457", "Blood Leech", "EP163", 6, 1.0, 2, ["Fire", "Jade"], "Bloated on the dead from the barge.", atkx=0.85)
    hum("E460", "Kansen-Hana", "EP146", 8, 7.0, 7, ["Air", "Water", "Crystal"], "Kitsune Hana, possessed by a "
        "Greater Kansen, lifting the iron box over the blood pit. Steel only annoys it; crystal and magic hurt it. "
        "Break her and she drops the box.", atkx=1.0, exp=0, money=0)
    e["E460"]["option"].append({"opttype": "opt_elemdef", **{"EDR.%d" % ELEMS.index(n): 50 for n in (
        "Katana", "Yari", "Tanto", "Tetsubo", "Yumi", "Bo", "Unarmed")}})
    e["E460"].update({"rt_ritual": True, "rt_crystal": True})
    e["E449"]["item1"].update({"itemid": "I186", "rate": 100.0})          # steal: the bandit's purse
    e["E460"]["item1"].update({"itemid": "I135", "rate": 100.0})          # steal: Kansen Mist (bosses.md)
    e["E455"]["item0"].update({"itemid": "A144", "rate": 100.0})          # drop: the Fox Charm
    e["E449"]["item0"]["itemid"] = e["E460"]["item0"]["itemid"] = e["E455"]["item1"]["itemid"] = None
    # ---- Scorpion Ch2 "City of Masks" (bosses.md: b_stitched_monks_a/b L22-23 Res4 weak Tanto/Fire, freed on Suki;
    # b_boss_munashii L25 HPx9 Res12, crystal full / everything else half, weak Katana/Fire/Air, phase 2 copies
    # buffs; Giseiki's counter-word = a free Suki). Doji Siko (research: the fallen Emerald Magistrate, iaijutsu).
    # Mitsue alone until S05, then with Isawa Kasiko (P137).
    hum("E462", "Paddy Python", "EP164", 20, 1.2, 3, ["Katana", "Fire"], "A python thick as a man's thigh, from the "
        "flooded paddies.", atkx=0.9)
    hum("E463", "Giant Hornet", "EP165", 19, 0.6, 2, ["Fire", "Air"], "A hornet the size of a cat. There's never "
        "only one.", atkx=0.8)
    for eid, lv, desc in (("E466", 22, "A monk of the Silent Self with a cloth face sewn over his own. Break him and "
                                      "the stitches tear: the soul inside goes free."),
                          ("E467", 23, "A stitched-face monk on the temple paths. \"Give us your face.\"")):
        hum(eid, "Stitched-face Monk", _he.EP["stitched_monk"], lv, 1.0, 4, ["Tanto", "Fire"], desc, atkx=0.85)
        e[eid]["rt_freed"] = True
    hum("E470", "Doji Siko", _sc_epid("siko"), 22, 3.0, 6, ["Yari", "Air"], "An Emerald Magistrate's badge on her "
        "obi. She favours her right leg and doesn't let you see it. She is no longer a magistrate of the Empire.",
        atkx=1.0, exp=0, money=0)
    hum("E471", "Abbot Munashii", "EP147", 25, 9.0, 12, ["Katana", "Fire", "Air", "Crystal"], "The abbot of the "
        "Monastery of the Silent Self, kneeling before the faceless shadow. Only crystal hurts him fully. Halfway "
        "down he puts on his true mask, and copies your courage.", atkx=1.0, exp=0, money=0)
    e["E471"]["option"].append({"opttype": "opt_elemdef", **{"EDR.%d" % ELEMS.index(n): 50 for n in (
        "Yari", "Tanto", "Tetsubo", "Yumi", "Bo", "Unarmed", "Water", "Earth", "Void", "Jade")}})
    e["E471"].update({"rt_munashii": True, "rt_crystal": True})
    e["E471"]["item0"].update({"itemid": "A151", "rate": 100.0})          # drop: Munashii's Mask
    e["E471"]["item1"].update({"itemid": "I400", "rate": 100.0})          # steal: a Crystal Rosary
    for eid in ("E466", "E467", "E470"):
        e[eid]["item0"]["itemid"] = e[eid]["item1"]["itemid"] = None
    # ---- Scorpion Ch3 = Unicorn Ch2 "Fortunes Lost" (bosses.md b_boss_iuchi_hit_squad L28, Mitsue's view 30-35:
    # shugenja x3 Res5 weak Yari/Yumi/Air, the amulet-bearer Res7 weak Tanto/Katana; the silence bubble every other
    # turn until the bearer breaks). Mitsue + Akodo Rin (P138).
    for eid, nm in (("E477", "Iuchi Shugenja"),):
        hum(eid, nm, _he.EP["iuchi_shugenja"], 33, 2.2, 5, ["Yari", "Yumi", "Air"], "One of the Iuchi officers who "
            "'disappeared' in the war: a basket hat, a mask, meishodo amulets. They rose out of the earth.",
            atkx=0.9, exp=0, money=0)
    hum("E478", "Amulet-bearer", _he.EP["amulet_bearer"], 34, 4.0, 7, ["Tanto", "Katana"], "The squad's anchor, "
        "hung with amulets. While he stands, the air goes still every other turn: no spell makes a sound.",
        atkx=0.9, exp=0, money=0)
    e["E478"]["rt_bubble"] = True
    for eid in ("E477", "E478"):
        e[eid]["item0"]["itemid"] = e[eid]["item1"]["itemid"] = None
    # ---- Phoenix Ch4 "Howl" (bosses.md: b_mieko_shadows_a/b L42-43 shadow fragment x3 Res4 weak Water/Void, they copy
    # Haruki's spells; b_boss_mieko_dark L45 HPx12 Res16 (-2 per dream key) weak Water/Bo/Void, Void Drain; each
    # blessed echo cancels a drain). Haruki + Hayato (+ Yosai, + a hireling): Resolve 12 / 10 / 8 / 6 by keys.
    hum("E412", "Mieko's Shadow", "EP162", 42, 1.3, 4, ["Water", "Void"], "A fragment of the dark half. It knows every "
        "spell Haruki knows.", atkx=0.8)
    hum("E413", "Mieko's Shadow", "EP162", 43, 1.5, 4, ["Water", "Void"], "A fragment of the dark half, nearer the "
        "torii. It knows every spell Haruki knows.", atkx=0.85)
    for eid, res in (("E414", 12), ("E415", 10), ("E416", 8), ("E417", 6)):
        hum(eid, "Mieko (dark half)", "EP142", 45, 9.0, res, ["Water", "Bo", "Void"], "Mieko's dark half on the red "
            "torii cliff, the book in her hands. Her Void drains yours. The dream keys loosened her; the gentle echoes "
            "stand between you.", exp=0, money=0)
        e[eid]["rt_echo_block"] = True
        e[eid]["item0"]["itemid"] = e[eid]["item1"]["itemid"] = None
    e["E359"]["item0"]["itemid"] = e["E359"]["item1"]["itemid"] = None
    e["E349"]["item1"]["itemid"] = None
    for eid, nm, key, lv, hpx, res in (("E350", "Akodo Ozaki", "ozaki", 4, 2.0, 4), ("E351", "Akodo Gusai", "gusai", 4, 2.2, 4),
                                       ("E352", "Shiba Ashimita", "ashimita", 6, 3.0, 5)):
        hum(eid, nm, _sc_epid(key), lv, hpx, res, ["Yari", "Air"], "A duel: first blood. No seconds.", exp=60 + 20 * lv,
            money=0)
        e[eid]["rt_duel"] = True
        e[eid]["item0"]["itemid"] = e[eid]["item1"]["itemid"] = None
    hum("E357", "Shiba Guard", _he.EP["phoenix_guard"], 4, 1.8, 3, ["Katana", "Bo"], "A Shiba guard at Kamatori who "
        "wants to know what a Lion is made of. A duel: first blood.", exp=120, money=0)
    e["E357"]["rt_duel"] = True
    e["E357"]["item0"]["itemid"] = e["E357"]["item1"]["itemid"] = None
    # Kakita Masanori (b_boss_masanori: formal duel, first blood). Resolve 8, not 14: the duel is fought alone (no
    # guest, no hireling) and his weak points (Yari, Tanto, Air) only reach him through a short blade.
    hum("E347", "Kakita Masanori", "EP131", 45, 6.0, 8, ["Yari", "Tanto", "Air"], "Rensei's father. The duel he has "
        "feared all his life: first blood, at dawn.", exp=0, money=0)
    e["E347"]["option"].append({"opttype": "opt_elemdef", "EDR.%d" % ELEMS.index("Katana"): 50})
    e["E347"]["rt_firstblood"] = True
    e["E347"]["item0"]["itemid"] = e["E347"]["item1"]["itemid"] = None
    e["E242"]["AGI"] = int(e["E242"]["AGI"] * 1.4)
    e["E241"]["AGI"] = int(e["E241"]["AGI"] * 0.7)
    e["E247"]["item0"].update({"itemid": "A114", "rate": 100.0})              # drop: Kommei Mask
    e["E247"]["item1"].update({"itemid": "I136", "rate": 100.0})              # steal: Oni Ichor
    for eid, cmds in (("E230", [(None, 70), ("S047", 30)]), ("E232", [(None, 60), ("S135", 40)]),
                      ("E233", [(None, 50), ("S136", 50)]), ("E235", [("S134", 45), ("S133", 35), (None, 20)]),
                      ("E234", [("S137", 100)]), ("E107", [(None, 65), ("S179", 35)]),
                      ("E108", [(None, 50), ("S180", 50)]), ("E109", [(None, 60), ("S181", 40)]),
                      ("E104", [(None, 60), ("S182", 40)]), ("E240", [(None, 70), ("S047", 30)]),
                      ("E241", [(None, 45), ("S152", 30), ("S167", 25)]), ("E242", [(None, 40), ("S153", 60)]),
                      ("E244", [(None, 50), ("S151", 50)]), ("E247", [("S149", 55), ("S150", 25), (None, 20)]),
                      ("E248", [(None, 100)]), ("E250", [(None, 50), ("S162", 50)]),
                      ("E102", [(None, 60), ("S168", 40)]), ("E246", [(None, 50), ("S164", 30), ("S165", 20)]),
                      ("E252", [(None, 50), ("S164", 30), ("S165", 20)]), ("E251", [(None, 60), ("S166", 40)]),
                      ("E253", [(None, 70), ("S152", 30)]), ("E255", [("S160", 55), ("S161", 25), (None, 20)]),
                      ("E256", [(None, 65), ("S137", 35)]), ("E302", [(None, 60), ("S402", 40)]),
                      ("E313", [("S404", 45), (None, 35), ("S405", 20)]), ("E326", [("S000", 100)]),
                      ("E217", [(None, 65), ("S407", 35)]), ("E218", [(None, 60), ("S408", 40)]),
                      ("E327", [(None, 40), ("S411", 60)]), ("E328", [(None, 40), ("S413", 35), ("S412", 25)]),
                      ("E330", [("S414", 50), (None, 50)]), ("E331", [(None, 40), ("S415", 40), ("S416", 20)]),
                      ("E334", [(None, 60), ("S409", 40)]), ("E337", [(None, 50), ("S410", 50)]),
                      ("E342", [(None, 55), ("S417", 45)]), ("E343", [(None, 55), ("S418", 45)]),
                      ("E344", [(None, 40), ("S419", 35), ("S420", 25)]),
                      ("E346", [(None, 35), ("S421", 40), ("S422", 25)]),
                      ("E347", [("S424", 45), (None, 35), ("S425", 20)]),
                      ("E349", [(None, 55), ("S431", 45)]), ("E358", [(None, 40), ("S435", 60)]),
                      ("E359", [(None, 30), ("S436", 70)]), ("E360", [(None, 40), ("S435", 60)]),
                      ("E364", [(None, 50), ("S438", 50)]), ("E365", [("S440", 100)]),
                      ("E374", [(None, 45), ("S445", 30), ("S404", 25)]), ("E375", [(None, 45), ("S446", 55)]),
                      ("E376", [(None, 50), ("S447", 50)]),
                      ("E384", [(None, 50), ("S455", 50)]), ("E385", [("S456", 100)]),
                      ("E388", [(None, 35), ("S449", 40), ("S450", 25)]),
                      ("E389", [(None, 60), ("S450", 40)]), ("E395", [(None, 50), ("S457", 50)]),
                      ("E400", [(None, 60), ("S463", 40)]), ("E401", [(None, 40), ("S462", 60)]),
                      ("E402", [(None, 30), ("S462", 70)]), ("E405", [(None, 50), ("S468", 50)]),
                      ("E408", [(None, 40), ("S469", 60)]), ("E409", [(None, 60), ("S470", 40)]),
                      ("E412", [(None, 40), ("S471", 30), ("S472", 30)]), ("E413", [(None, 40), ("S471", 30),
                                                                                    ("S472", 30)]),
                      ("E414", [(None, 25), ("S473", 40), ("S469", 35)]), ("E415", [(None, 25), ("S473", 40),
                                                                                    ("S469", 35)]),
                      ("E416", [(None, 25), ("S473", 40), ("S469", 35)]), ("E417", [(None, 25), ("S473", 40),
                                                                                    ("S469", 35)]),
                      ("E430", [(None, 55), ("S486", 45)]), ("E435", [(None, 40), ("S485", 40), ("S446", 20)]),
                      ("E436", [(None, 60), ("S485", 40)]), ("E437", [(None, 75), ("S492", 25)]),
                      ("E438", [(None, 45), ("S491", 55)]), ("E440", [(None, 45), ("S493", 55)]),
                      ("E441", [(None, 65), ("S490", 35)]),
                      ("E445", [(None, 60), ("S498", 40)]), ("E446", [(None, 70), ("S492", 30)]),
                      ("E447", [(None, 40), ("S446", 60)]), ("E448", [(None, 35), ("S496", 65)]),
                      ("E455", [(None, 55), ("S509", 45)]), ("E456", [(None, 60), ("S508", 40)]),
                      ("E457", [(None, 55), ("S508", 45)]), ("E460", [(None, 25), ("S510", 35), ("S511", 25),
                                                                     ("S512", 15)]),
                      ("E462", [(None, 55), ("S514", 45)]), ("E463", [(None, 50), ("S515", 50)]),
                      ("E466", [(None, 60), ("S513", 40)]), ("E467", [(None, 60), ("S513", 40)]),
                      ("E470", [(None, 50), ("S516", 50)]), ("E471", [(None, 30), ("S517", 45), ("S518", 25)]),
                      ("E477", [(None, 30), ("S523", 45), ("S524", 25)]), ("E478", [(None, 50), ("S525", 50)])):
        base = e[eid]["ai"][0]["cmds"][0]
        e[eid]["ai"][0]["cmds"] = [dict(base, skillid=sk, rate=w) for sk, w in cmds]
    # Area tuning (user: random monsters are fixed per area, tuned for the party expected there). The curve assumes a
    # foe falls to ~2 party actions, so with 2-4 travelers a group died in 1-2 rounds; and the Ch2/Ch4 parties are
    # Crab tanks (Natsuko, Goro, Sachiko), whom "avg" foes barely scratch. eid -> (HP x for the area, defender, ATK x).
    # Measured with tools/balance_encounters.py (target: 3-5 rounds, 50-90% party HP left).
    for src, dst in (("E201", "E257"), ("E213", "E258"), ("E233", "E259")):     # the Hida road's own copies (2 travelers)
        e[dst] = copy.deepcopy(e[src])                                        # (same name, so the same bestiary drops)
        HPX[dst] = HPX[src]
    AREA = {}
    for eid in ("E257", "E237", "E258", "E259"):                             # Ch2 Hida road: Natsuko + Goro
        AREA[eid] = (1.7, "crab", 1.3)
    for eid in ("E230", "E231", "E232", "E233"):                             # Ch2 donjon: + Michio, Sachiko
        AREA[eid] = (2.2, "crab", 1.4)
    for eid in ("E240", "E241", "E242", "E243", "E244"):                     # Ch3 Shadowlands: + Squeak (+ Kage)
        AREA[eid] = (1.0 if eid == "E241" else 1.3, "avg", 1.3)              # zombies feed (Grave Feast): less HP
    for eid in ("E250", "E251", "E252", "E254"):                             # Ch4 siege: + Sachiko, Goro
        AREA[eid] = (1.8, "crab", 1.3)
    # Crane Ch1 road_west (Lv 2-3 on arrival, Rensei + one guest): the region's foes at the road's own level (copies,
    # same names and drops). The forest (Lv 4-8) keeps the originals.
    def relevel(src, dst, lv, hpm=0.65, atm=1.0, vs="crane"):
        e[dst] = copy.deepcopy(e[src])
        HPX[dst] = HPX[src]
        old, new = foe_stats(int(e[src]["LV"])), foe_stats(lv)
        e[dst]["LV"] = lv
        for k in ("PDEF", "MDEF", "AGI"):                                    # keep the foe's shape (armour, speed)
            e[dst][k] = max(1, int(round(e[src][k] * new[k] / max(1, old[k]))))
        e[dst]["exp"], e[dst]["money"] = 6 + 3 * lv, 10 + 4 * lv
        AREA[dst] = (hpm, vs, atm)                                          # road: a wolf falls to one or two cuts
    for src, dst, lv in (("E302", "E303", 2), ("E200", "E304", 2), ("E109", "E305", 3), ("E204", "E306", 4),
                         ("E108", "E307", 3)):
        relevel(src, dst, lv)
    # Mountains' Cloak Forest (Danger 3-8; Rensei ~Lv 4-6 + one guest): the shared foes at the forest's level
    for src, dst, lv in (("E200", "E308", 5), ("E109", "E309", 6), ("E204", "E310", 6), ("E108", "E311", 6)):
        relevel(src, dst, lv, hpm=1.0, atm=1.4)
    relevel("E302", "E312", 5, hpm=1.0)                    # wolves: Pack Bite already stacks per wolf
    # Crane Ch2: the new "Crab-Crane border" row (storyboard F-6; Lv 20-25). The Crane coast road (Rensei alone) and
    # the land-bridge (Rensei + Goro): copies at the border's levels.
    for src, dst, lv, hpm in (("E213", "E316", 21, 1.0), ("E105", "E317", 21, 0.75), ("E209", "E318", 22, 1.0),
                              ("E205", "E319", 23, 1.0), ("E233", "E320", 23, 0.7)):   # armour / half-physical: less HP
        relevel(src, dst, lv, hpm=hpm, atm=0.8 if dst == "E320" else 1.0)     # the yurei's wail also terrifies
    # ...and the land-bridge, crossed with Goro (a Crab tank with Troll-Breaker): sturdier copies for two travelers
    for src, dst, lv, hpm in (("E213", "E321", 22, 1.8), ("E105", "E322", 22, 1.4), ("E209", "E323", 23, 1.8),
                              ("E205", "E324", 24, 1.8), ("E233", "E325", 24, 1.3)):
        relevel(src, dst, lv, hpm=hpm, atm=1.3)
    AREA["E302"] = (1.0, "crane", 1.0)                                     # Crane-only foes: tuned in place
    AREA["E314"] = (0.6, "crane", 0.85)      # Crane Ch2 sentries: after the split Rensei walks the camp alone
    AREA["E301"] = (1.6, "crane", 0.7)       # farmers with sticks: two plain cuts make one surrender; only a big hit
                                             # (a full Iaijutsu Strike, a Boost) kills outright
    # Crane Ch3 (Lv 30-35, Rensei alone): the sea row, Yosuke's and Katsuo's crews, the shrine row
    for eid in ("E327", "E328", "E330", "E334", "E337", "E346", "E347"):
        AREA[eid] = (1.0, "crane", 1.0)
    AREA["E342"] = (1.0, "crane", 0.8)          # Crane Ch4 archives (solo, Lv 41-43): paper-spirits come in swarms,
                                                # and their Paper Cut bleeds (K055: 5% of max HP a turn, 3 turns)
    AREA["E343"] = (0.85, "crane", 0.9)         # ink-pots blind (a blind solo traveler drags the fight out)
    AREA["E344"] = (1.25, "crane", 1.1)
    # Lion Ch1 (Shizue alone, Lv 3-6, + a guest and a hireling): the mid-boss and the Duels
    AREA["E349"] = (0.55, "avg", 0.8)
    AREA["E358"] = (0.6, "avg", 0.5)            # solo + guest + hireling: the fight is the three breaks (about 10
    AREA["E360"] = (0.6, "avg", 0.55)           # rounds), not HP, so the damage is low
    AREA["E359"] = (0.6, "avg", 0.4)
    for eid in ("E361", "E362", "E363"):
        AREA[eid] = (0.6, "avg", 0.8)
    AREA["E364"] = (0.8, "avg", 0.85)
    AREA["E365"] = (0.6, "avg", 0.5)
    for eid, a in (("E372", (0.6, "avg", 0.8)), ("E373", (0.9, "avg", 0.8)), ("E374", (0.55, "avg", 0.75)),
                   ("E375", (0.65, "avg", 0.7)), ("E376", (0.8, "avg", 0.55))):
        AREA[eid] = a
    # the west road (spring) and the pass (bestiary F "Lion west road" / "Lion mountains", Lv 28-35)
    for src, dst, lv, hpm, atm in (("E202", "E377", 30, 0.7, 0.85), ("E205", "E378", 30, 0.75, 0.85),
                                   ("E302", "E379", 30, 0.55, 0.7), ("E209", "E380", 31, 0.6, 0.75)):
        relevel(src, dst, lv, hpm=hpm, atm=atm, vs="avg")
    e["E379"]["name"] = "Winter Wolf"
    AREA["E394"] = (0.7, "avg", 0.6)
    AREA["E395"] = (0.6, "avg", 0.75)
    AREA["E399"] = (0.6, "avg", 0.7)
    for eid, a in (("E421", (0.6, "avg", 0.6)), ("E422", (1.1, "avg", 0.85)), ("E425", (0.8, "avg", 0.7)),
                   ("E423", (1.1, "avg", 1.05)), ("E424", (0.9, "avg", 0.95))):
        AREA[eid] = a
    for eid, a in (("E412", (0.8, "avg", 0.75)), ("E413", (0.8, "avg", 0.75)), ("E414", (0.6, "avg", 1.15)),
                   ("E415", (0.6, "avg", 1.15)), ("E416", (0.6, "avg", 1.15)), ("E417", (0.6, "avg", 1.15))):
        AREA[eid] = a
    for eid, a in (("E405", (0.8, "avg", 0.7)), ("E406", (0.8, "avg", 0.7)), ("E407", (0.8, "avg", 0.7)),
                   ("E408", (0.6, "avg", 0.8)), ("E409", (0.6, "avg", 1.0)), ("E410", (0.6, "avg", 1.0))):
        AREA[eid] = a
    for eid, a in (("E400", (0.8, "avg", 0.7)), ("E401", (0.7, "avg", 0.6)), ("E402", (0.6, "avg", 0.9))):
        AREA[eid] = a
    for eid, a in (("E381", (0.8, "avg", 0.8)), ("E382", (0.8, "avg", 0.8)), ("E383", (0.8, "avg", 0.8)),
                   ("E384", (0.8, "avg", 0.6)), ("E385", (0.8, "avg", 0.7)), ("E388", (0.65, "avg", 0.75)),
                   ("E389", (0.55, "avg", 0.75)), ("E390", (0.55, "avg", 0.75))):
        AREA[eid] = a
    # Lion Ch4: the wave-4 spearmen, the terror wave, and Sorrow's Path road (bestiary F, 40-46)
    for src, dst, lv, hpm, atm in (("E212", "E386", 43, 0.8, 0.45), ("E364", "E387", 44, 0.6, 0.4),
                                   ("E215", "E391", 42, 0.7, 0.8), ("E211", "E392", 43, 0.65, 0.65),
                                   ("E214", "E393", 42, 0.6, 0.6)):
        relevel(src, dst, lv, hpm=hpm, atm=atm, vs="avg")
    e["E386"]["name"] = "Crane Spearman"
    e["E387"]["desc"] = "The demon's terror wave: shapes of dread rising out of the mist."
    # the winter road (bestiary F "Shiro Akodo roads (winter)", Lv 18-25) and the under-dojo (Fear Shade, Cave Bats)
    for src, dst, lv, hpm in (("E312", "E366", 20, 0.9), ("E209", "E367", 21, 0.8), ("E213", "E368", 20, 0.8),
                              ("E233", "E369", 22, 0.6), ("E232", "E370", 21, 0.7)):
        relevel(src, dst, lv, hpm=hpm, atm=0.85, vs="avg")
    e["E366"]["name"] = "Mountain Wolf"                  # the winter road's wolves (bestiary F)
    relevel("E364", "E371", 22, hpm=0.7, atm=0.65, vs="avg")             # Ianwa's own shades: softer (the charm costs
                                                                         # Shizue turns as it is)
    # the shrine road (road_west_phoenix; bestiary F "Lion plains & border" / "Phoenix roads", Lv 4-7, Shizue alone)
    for src, dst, lv in (("E212", "E353", 5), ("E302", "E354", 5), ("E200", "E355", 5), ("E108", "E356", 6)):
        relevel(src, dst, lv, hpm=0.8, atm=0.85, vs="avg")
    # Phoenix Ch1: the shrine road for Haruki (bestiary F "Phoenix roads & Kamatori", 1-8): the same wolves, bandits
    # and wisps as Shizue's road, younger (ENCOUNTERS rt_if G585)
    for src, dst, lv, hpm, atm in (("E354", "E396", 2, 1.2, 0.9), ("E355", "E397", 3, 1.2, 0.9),
                                   ("E356", "E398", 3, 1.1, 0.9)):
        relevel(src, dst, lv, hpm=hpm, atm=atm, vs="avg")
    # Phoenix Ch3: looters on the fever road (bestiary F "Isawa Mori (Darkfever)" 28-35)
    relevel("E221", "E411", 31, hpm=0.8, atm=0.75, vs="avg")
    # Phoenix Ch2: the snowbound pass (bestiary F, 18-25): mountain wolves, a yurei
    for src, dst, lv, hpm, atm in (("E366", "E403", 21, 0.8, 0.75), ("E233", "E404", 22, 0.8, 0.75)):
        relevel(src, dst, lv, hpm=hpm, atm=atm, vs="avg")
    # Dragon Ch2: the Tortoise cove (bestiary F "Tortoise Island & cove" 20-25): wako, bats, the uncommon tide crab
    for src, dst, lv, hpm, atm in (("E217", "E431", 21, 0.8, 0.75), ("E232", "E432", 20, 1.3, 0.8),
                                   ("E322", "E433", 22, 1.15, 0.9)):
        relevel(src, dst, lv, hpm=hpm, atm=atm, vs="avg")
    AREA["E430"] = (1.0, "avg", 0.9)
    AREA["E434"] = (1.0, "avg", 0.85)
    AREA["E435"] = (0.45, "avg", 0.85)
    # Dragon Ch3: the year-400 capital and the Izumida road (Gendo + Seppun Ushimo if Tsuhime was helped)
    relevel("E217", "E442", 33, hpm=1.0, atm=0.6, vs="avg")
    # Dragon Ch4: the year-400 coast (IV): the gaijin come again, harder
    for src, dst, lv in (("E437", "E443", 42), ("E438", "E444", 43)):
        relevel(src, dst, lv, hpm=0.9, atm=0.8, vs="avg")
    for eid, a in (("E445", (0.9, "avg", 0.7)), ("E446", (0.9, "avg", 0.7)), ("E447", (0.6, "avg", 0.85)),
                   ("E448", (0.7, "avg", 1.2))):
        AREA[eid] = a             # Gusai Iami's pirates on the parley ship
    for eid, a in (("E436", (0.9, "avg", 0.8)), ("E437", (0.9, "avg", 0.8)), ("E438", (0.8, "avg", 0.75)),
                   ("E440", (1.4, "avg", 0.8)), ("E441", (1.0, "avg", 0.4))):    # Akuro is unhurried
        AREA[eid] = a                                    # Gendo alone (+ the Momo guest)
    # Scorpion Ch1: the roads south (bestiary F "Scorpion south & Kudo" 1-8: Mitsue alone) and the west-bank marsh
    # ("River of Gold west bank (marsh)" 4-8: Mitsue + Rui)
    for src, dst, lv, hpm, atm in (("E304", "E450", 2, 0.75, 0.5), ("E104", "E451", 3, 1.0, 0.75),
                                   ("E107", "E452", 2, 0.7, 0.42), ("E204", "E453", 4, 0.8, 0.65),
                                   ("E307", "E454", 4, 1.1, 0.8), ("E100", "E458", 5, 1.6, 1.05),
                                   ("E104", "E459", 6, 1.5, 1.05)):
        relevel(src, dst, lv, hpm=hpm, atm=atm, vs="avg")
    e["E458"]["name"] = "Goblin"
    # Scorpion Ch2: the plains north of Shiro no Soshi (bestiary F 18-25: Mitsue alone) and the Temple District
    # ("City of Masks: Temple District" 22-25: Mitsue + Isawa Kasiko)
    for src, dst, lv, hpm, atm in (("E225", "E461", 21, 0.8, 0.7), ("E209", "E464", 22, 0.8, 0.7),
                                   ("E233", "E465", 22, 0.5, 0.7), ("E356", "E468", 23, 1.0, 0.6),
                                   ("E342", "E469", 24, 1.0, 0.8)):
        relevel(src, dst, lv, hpm=hpm, atm=atm, vs="avg")
    # Scorpion Ch3: the Ojatara Valleys (bestiary F 30-35 in Mitsue's view) and the grave path toward the jade mines
    for src, dst, lv, hpm, atm in (("E201", "E472", 31, 1.3, 0.95), ("E213", "E473", 32, 1.3, 0.95),
                                   ("E366", "E474", 31, 1.0, 0.8), ("E406", "E475", 32, 1.5, 1.0),
                                   ("E221", "E476", 33, 1.4, 1.0)):
        relevel(src, dst, lv, hpm=hpm, atm=atm, vs="avg")
    e["E473"]["name"] = "Border Patrol"
    for eid, a in (("E477", (0.8, "avg", 0.62)), ("E478", (1.0, "avg", 0.7))):
        AREA[eid] = a
    e["E468"]["name"] = "Kansen Wisp"                   # (bestiary: Kansen are hurt by crystal)
    e["E468"]["option"].append(weak_opt("Crystal"))
    for eid, a in (("E462", (0.7, "avg", 0.6)), ("E463", (0.8, "avg", 0.7)), ("E466", (1.7, "avg", 1.15)),
                   ("E467", (1.0, "avg", 0.9)), ("E470", (0.8, "avg", 0.95)), ("E471", (0.8, "avg", 1.8))):
        AREA[eid] = a
    for eid, a in (("E449", (0.7, "avg", 0.6)), ("E455", (1.45, "avg", 2.1)), ("E456", (1.5, "avg", 1.15)),
                   ("E457", (0.8, "avg", 0.95)), ("E460", (1.5, "avg", 1.6))):
        AREA[eid] = a
    # Dragon Ch1: the silk hill path and the Gusai ruins (bestiary F "Mantis isles (present)" 1-8)
    for src, dst, lv, hpm, atm in (("E216", "E426", 3, 0.8, 0.75), ("E105", "E427", 3, 0.8, 0.75),
                                   ("E107", "E428", 3, 0.8, 0.75), ("E204", "E429", 5, 0.8, 0.75)):
        relevel(src, dst, lv, hpm=hpm, atm=atm, vs="avg")
    # Phoenix Ch4: the sea-cliffs (bestiary F "Phoenix sea-cliffs" 40-46): frost spirits, wako, Kansen wisps
    for src, dst, lv, hpm, atm in (("E404", "E418", 42, 0.8, 0.75), ("E217", "E419", 42, 0.8, 0.75),
                                   ("E356", "E420", 43, 0.8, 0.75)):
        relevel(src, dst, lv, hpm=hpm, atm=atm, vs="avg")
    e["E418"]["name"] = "Frost Spirit"
    e["E420"]["name"] = "Kansen Wisp"
    AREA["E357"] = (0.6, "avg", 0.8)
    for eid in ("E350", "E351", "E352"):
        AREA[eid] = (0.6, "avg", 0.8)
    AREA["E331"] = (1.0, "crane", 0.65)          # Ryohei fights tired, beside his brother
    for src, dst, lv, hpm in (("E217", "E333", 30, 1.0), ("E105", "E335", 30, 0.75), ("E218", "E336", 32, 1.0),
                              ("E217", "E338", 33, 1.0), ("E218", "E339", 34, 1.0), ("E334", "E340", 33, 0.85),
                              ("E337", "E341", 35, 1.0)):
        relevel(src, dst, lv, hpm=hpm)
    relevel("E217", "E329", 32, hpm=0.7, atm=0.6)          # the boss crews are there to carry charms, not to kill
    relevel("E217", "E332", 34, hpm=0.6, atm=0.55)
    for eid, charm in (("E329", "K045"), ("E332", None)):
        e[eid].update({"name": "White Squid Pirate", "RES": 3, "desc": "One of the brothers' crew, in a white sash, "
                       "with a paper charm tucked in it."})
        if charm:
            e[eid]["rt_charm"] = charm                                     # Yosuke's crew sail charmed
    # ---- Unicorn Ch1 "Fault Lines" (bosses.md: b_camp_thugs L2, b_cave_guerrillas L6, b_boss_naohida L8 HPx7 Res 7
    # weak Yari/Yumi/Water; storyboard: the valley road Ch1 band 1-8, the pigeon cave). Tamotsu + Shinjo Ryuko (+ Rin)
    hum("E489", "Camp Thug", _he.EP["dock_ruffian"], 2, 0.8, 2, ["Yumi", "Yari"], "A refugee with a club and nothing to "
        "lose, after the rice.", atkx=0.75)
    hum("E490", "Peasant Guerrilla", _he.EP["peasant_guerrilla"], 6, 1.0, 2, ["Yari", "Water"], "A farmer with "
        "powder-black hands and a kama. He'd rather go home.", atkx=0.8)
    hum("E491", "Naohida", "EP150", 8, 10.0, 7, ["Yari", "Yumi", "Water"], "Tamotsu's fellow student. Silk under dirty "
        "cotton, a gaijin dao, and a hatred of both castles. Water spoils his powder.", atkx=1.6, exp=0, money=0)
    hum("E492", "Powder Keg", "EP174", 8, 0.05, 1, [], "A keg of gaijin pepper. Any Fire sets it off: a blast that "
        "hits everyone, on both sides.", atkx=0.0, exp=0, money=0)
    e["E492"]["rt_keg"] = True
    e["E491"]["rt_naohida"] = True
    for eid in ("E489", "E490"):
        e[eid]["rt_bribe"] = True                                                # paid off: they go home (plugin)
    e["E490"]["rt_surrender"] = True                                             # below 40% HP: hands up (plugin)
    e["E491"]["item0"].update({"itemid": None, "rate": 0.0})
    e["E491"]["item1"].update({"itemid": "I409", "rate": 100.0})                 # steal: a Powder Bomb
    for eid in ("E489", "E490", "E492"):
        e[eid]["item0"]["itemid"] = e[eid]["item1"]["itemid"] = None
    for src, dst, lv, hpm, atm in (("E449", "E493", 3, 1.5, 2.0), ("E303", "E494", 3, 1.2, 1.6),
                                   ("E213", "E495", 5, 1.0, 1.5), ("E453", "E496", 5, 1.8, 2.0),
                                   ("E103", "E497", 6, 2.4, 3.2)):
        relevel(src, dst, lv, hpm=hpm, atm=atm, vs="avg")
    e["E495"]["name"] = "Border Patrol"
    hum("E498", "Pigeon Swarm", "EP171", 5, 0.6, 2, ["Yumi", "Air"], "Startled doves from the cliff, a hundred of "
        "them, all beak.", atkx=0.7)
    hum("E499", "Peasant Guerrilla", _he.EP["peasant_guerrilla"], 6, 0.9, 2, ["Yari", "Water"], "A cave guard with a "
        "pitchfork. He'd rather go home.", atkx=0.75)
    e["E499"]["rt_bribe"] = e["E499"]["rt_surrender"] = True
    e["E499"]["item0"]["itemid"] = e["E499"]["item1"]["itemid"] = None
    for eid, cmds in (("E491", [(None, 45), ("S548", 30), ("S549", 25)]), ("E498", [(None, 60), ("S179", 40)])):
        base = e[eid]["ai"][0]["cmds"][0]
        e[eid]["ai"][0]["cmds"] = [dict(base, skillid=sk, rate=w) for sk, w in cmds]
    e["E491"]["ai"][0]["actnum"] = [1, 2]                                    # a boss against three
    base = e["E492"]["ai"][0]["cmds"][0]
    e["E492"]["ai"][0]["cmds"] = [dict(base, skillid="S000", rate=100)]           # a keg just sits there
    for eid, a in (("E489", (1.0, "avg", 1.0)), ("E490", (1.0, "avg", 1.0)), ("E491", (1.0, "avg", 1.0)),
                   ("E492", (1.0, "avg", 1.0)), ("E498", (1.8, "avg", 3.2)), ("E499", (1.8, "avg", 2.4))):
        AREA[eid] = a
    # ---- Scorpion Ch4 "The Eve" (bestiary F "Dragon mountains" 40-48, "Tamori's Furnace" 42-46; Mitsue + her guide)
    relevel("E379", "E479", 41, hpm=1.0, atm=0.8, vs="avg")                   # Winter Wolf
    relevel("E201", "E480", 42, hpm=1.0, atm=0.85, vs="avg")                  # Mountain Bandit IV
    e["E480"]["name"] = "Mountain Bandit"
    hum("E481", "Snow Bear", "EP166", 42, 1.8, 5, ["Fire", "Yari"], "White fur, a black muzzle, and very little "
        "patience. It hugs.", atkx=0.85)
    e["E481"]["option"].append({"opttype": "opt_elemdef", "EDR.7": 50})        # resists Water
    hum("E482", "Tengu Crow-Warrior", "EP167", 43, 1.2, 4, ["Yumi", "Air"], "A crow's head, a swordsman's hands. It "
        "fights the way a crow laughs.", atkx=0.85)
    hum("E483", "Wolf-Spirit", "EP170", 44, 1.5, 6, ["Fire", "Void"], "A pale wolf that casts no shadow. Blades "
        "pass half through it.", atkx=0.85)
    e["E483"]["option"].append({"opttype": "opt_elemdef", **{"EDR.%d" % i: 50 for i in range(6)}})
    hum("E484", "Fire Elemental", "EP168", 43, 1.4, 4, ["Water", "Bo"], "A walking flame with a coal for a heart. "
        "The Tamori say it's the Furnace thinking.", atkx=0.85)
    e["E484"]["option"].append({"opttype": "opt_elemdef", "EDR.6": 50})      # Fire barely touches it
    hum("E485", "Ash Ghoul", "EP169", 43, 1.2, 4, ["Jade", "Water"], "A pilgrim the Furnace took, still walking, made "
        "of ash and old prayers.", atkx=0.85)
    hum("E487", "Fire Elemental", "EP168", 43, 2.0, 4, ["Water", "Bo"], "Three flames in a lava tube, standing guard "
        "for no one.", atkx=0.85, exp=0, money=0)
    e["E487"]["option"].append({"opttype": "opt_elemdef", "EDR.6": 50})
    hum("E488", "Ash Ghoul", "EP169", 44, 1.8, 4, ["Jade", "Water"], "Ash-shrine dead, risen out of the offerings.",
        atkx=0.85, exp=0, money=0)
    hum("E486", "Bloodspeaker Remnant", "EP148", 45, 12.0, 14, ["Jade", "Katana", "Air"], "A maho-tsukai who has "
        "hunted the Iron Box since Kudo, wearing Mitsue's face. At two-thirds and one-third of its blood it steals "
        "another face, and that face's weaknesses.", atkx=1.0, exp=0, money=0)
    e["E486"]["rt_stolenface"] = True
    e["E486"]["item0"].update({"itemid": None, "rate": 0.0})                 # drop: none (story)
    e["E486"]["item1"].update({"itemid": "A154", "rate": 100.0})             # steal: Bloodspeaker's Mirror
    for eid in ("E487", "E488"):
        e[eid]["item0"]["itemid"] = e[eid]["item1"]["itemid"] = None
    for eid, cmds in (("E481", [(None, 55), ("S531", 45)]), ("E482", [(None, 45), ("S532", 55)]),
                      ("E483", [(None, 60), ("S533", 40)]), ("E484", [(None, 50), ("S530", 50)]),
                      ("E485", [(None, 60), ("S534", 40)]), ("E487", [(None, 45), ("S530", 55)]),
                      ("E488", [(None, 55), ("S534", 45)]), ("E486", [(None, 30), ("S535", 45), ("S536", 25)])):
        base = e[eid]["ai"][0]["cmds"][0]
        e[eid]["ai"][0]["cmds"] = [dict(base, skillid=sk, rate=w) for sk, w in cmds]
    e["E486"]["ai"][0]["actnum"] = [2, 2]                                    # a boss against two: two actions a round
    for eid, a in (("E481", (1.0, "avg", 1.35)), ("E482", (1.0, "avg", 1.0)), ("E483", (0.9, "avg", 1.4)),
                   ("E484", (0.5, "avg", 1.2)), ("E485", (1.0, "avg", 1.0)), ("E487", (0.45, "avg", 1.5)),
                   ("E488", (0.6, "avg", 1.3)), ("E486", (1.0, "avg", 1.15))):
        AREA[eid] = a
    # ---- Unicorn Ch2 = Tamotsu's view of "Fortunes Lost" (Lv 22-30; storyboard C-1, F-2): the Ojatara foes and the
    # Iuchi hit squad at his band. Tamotsu (support) + Shinjo Ryuko + Akodo Rin.
    for src, dst, lv, hpm, atm in (("E472", "E500", 23, 2.0, 1.6), ("E473", "E501", 24, 2.0, 1.6),
                                   ("E474", "E502", 23, 1.6, 1.4), ("E475", "E503", 26, 2.4, 2.4),
                                   ("E476", "E504", 27, 2.0, 2.2)):
        relevel(src, dst, lv, hpm=hpm, atm=atm, vs="avg")
    hum("E505", "Iuchi Shugenja", _he.EP["iuchi_shugenja"], 28, 2.2, 5, ["Yari", "Yumi", "Air"], "One of the Iuchi "
        "officers who 'disappeared' in the war: a basket hat, a mask, meishodo amulets. They rose out of the earth.",
        atkx=0.9, exp=0, money=0)
    hum("E506", "Amulet-bearer", _he.EP["amulet_bearer"], 29, 4.0, 7, ["Tanto", "Katana"], "The squad's anchor, "
        "hung with amulets. While he stands, the air goes still every other turn: no spell makes a sound.",
        atkx=0.9, exp=0, money=0)
    e["E506"]["rt_bubble"] = True
    for src, dst in (("E477", "E505"), ("E478", "E506")):
        e[dst]["ai"] = copy.deepcopy(e[src]["ai"])
        e[dst]["item0"]["itemid"] = e[dst]["item1"]["itemid"] = None
    for eid, a in (("E505", (1.1, "avg", 1.05)), ("E506", (1.3, "avg", 1.05))):
        AREA[eid] = a
    # ---- Unicorn Ch3 "The Noblest Blood" (bosses.md b_tower_servants L31 Res3 weak Bo/Jade, b_mine_dead_a/b L33 Res3
    # weak Jade/Fire/Bo, b_boss_mine_guardian L35 HPx10 Res12 weak Jade/Fire/Yari; bestiary D III Singing Servant
    # 30-35 Water/Bo, "Ojatara Valleys" Ch3: Zombie, Gaki, Cave Bat Swarm). Tamotsu + Ryuko + Rin (+ Karasu's call)
    hum("E507", "Singing Servant", _he.EP["singing_servant"], 31, 0.9, 2, ["Water", "Bo", "Jade"], "A castle "
        "servant, possessed through the ears. Still in an apron. Break it and it wakes.", atkx=0.8)
    hum("E508", "Singing Servant", _he.EP["singing_servant"], 31, 1.3, 2, ["Bo", "Jade", "Water"], "The ones on "
        "the stair, at a child's barricaded door. Break them and they wake.", atkx=0.85, exp=0, money=0)
    for eid in ("E507", "E508"):                       # Resolve 2, not 3: a break has to land before the kill
        e[eid]["rt_singing"] = True
    e["E508"]["item0"]["itemid"] = e["E508"]["item1"]["itemid"] = None
    for src, dst, lv, hpm, atm in (("E241", "E509", 33, 1.6, 1.6), ("E406", "E510", 33, 1.6, 1.6),
                                   ("E232", "E511", 32, 1.4, 1.6)):
        relevel(src, dst, lv, hpm=hpm, atm=atm, vs="avg")
    e["E509"]["name"] = "Risen Dead"
    e["E509"]["desc"] = "A miner, or a miner's wife, or a miner's child. The mine didn't let them rest."
    hum("E512", "Risen Dead", "EP432", 33, 1.5, 3, ["Jade", "Fire", "Bo"], "The quiet dead of the jade mines, "
        "standing in rows. They feel no fear.", atkx=0.9, exp=0, money=0)
    hum("E513", "Mine Guardian", "EP152", 35, 7.0, 12, ["Jade", "Fire", "Yari"], "A corpse in Iuchi armour three "
        "hundred years old, risen from the mine's cracked shrine. Woken by the Regret above.", atkx=1.0, exp=0,
        money=0)
    e["E513"]["rt_guardian"] = True
    e["E513"]["item0"].update({"itemid": None, "rate": 0.0})                 # drop: the jade weapons (the story)
    e["E513"]["item1"].update({"itemid": "A156", "rate": 100.0})             # steal: Guardian's Lantern
    e["E512"]["item0"]["itemid"] = e["E512"]["item1"]["itemid"] = None
    for eid, cmds in (("E507", [(None, 40), ("S555", 30), ("S556", 30)]), ("E508", [(None, 40), ("S555", 30),
                                                                                    ("S556", 30)]),
                      ("E512", [(None, 100)]), ("E513", [(None, 30), ("S557", 40), ("S558", 30)])):
        base = e[eid]["ai"][0]["cmds"][0]
        e[eid]["ai"][0]["cmds"] = [dict(base, skillid=sk, rate=w) for sk, w in cmds]
    e["E513"]["ai"][0]["actnum"] = [2, 2]                                    # a boss against three: two a round
    for eid, a in (("E507", (1.4, "avg", 1.5)), ("E508", (1.9, "avg", 2.2)), ("E512", (1.4, "avg", 1.5)),
                   ("E513", (1.0, "avg", 1.5))):
        AREA[eid] = a
    # ---- Unicorn Ch4 "Regret" (bosses.md b_tunnel_legion L42 Res4 weak Jade/Yari; b_boss_kurosho_regret L45: the Doji
    # HPx14 Res18 weak Jade/Water/Void, Kurosho HPx6 Res10 weak Air/Bo; bestiary "Shiro Iuchi wind tunnel" 40-46:
    # possessed Legion, Moto Akutsukai (palette), uncommon Singing Servant). Tamotsu + Ryuko + Rin (+ Naohida's call)
    hum("E514", "Possessed Legionnaire", _he.EP["possessed_legion"], 42, 1.0, 4, ["Jade", "Yari"], "One of the "
        "Emperor's own Emerald Legion, wax-less, marching in a circle in the wind, chanting a dead woman's name.",
        atkx=0.85)
    relevel("E245", "E515", 43, hpm=0.9, atm=1.5, vs="avg")                   # Moto Akutsukai (the tunnel palette)
    relevel("E507", "E516", 43, hpm=1.4, atm=1.5, vs="avg")                   # Singing Servant (IV palette)
    e["E516"]["rt_singing"] = True
    hum("E517", "Possessed Legionnaire", _he.EP["possessed_legion"], 42, 1.5, 4, ["Jade", "Yari"], "A Legion "
        "squad marching in a circle at the tunnel's narrowest point, chanting.", atkx=0.9, exp=0, money=0)
    for eid in ("E514", "E517"):
        e[eid]["rt_legion"] = True
    e["E517"]["item0"]["itemid"] = e["E517"]["item1"]["itemid"] = None
    hum("E518", "Shuten Doji of Regret", "EP154", 45, 11.0, 18, ["Jade", "Water", "Void"], "One of the three Shuten "
        "Doji, Fu Leng's sensei of maho: a shape made of every apology no one ever made. Its servants' song possesses "
        "whoever hears it. Jade hurts it.", atkx=1.0, exp=0, money=0)
    hum("E519", "Iuchi Kurosho", "EP156", 45, 6.0, 10, ["Air", "Bo"], "Eighty, a monk's robe, the kanji for Void burned "
        "into his skull. He summoned Regret for want of a son. Possessed, he still prays like a master.", atkx=1.0,
        exp=0, money=0)
    e["E518"]["rt_wail"] = e["E518"]["rt_doji"] = True
    e["E519"]["rt_kurosho"] = True
    e["E518"]["item0"].update({"itemid": "A158", "rate": 100.0})               # drop: Regret's Silence
    e["E518"]["item1"].update({"itemid": None, "rate": 0.0})
    e["E519"]["item0"]["itemid"] = e["E519"]["item1"]["itemid"] = None
    for eid, cmds in (("E514", [(None, 60), ("S564", 40)]), ("E517", [(None, 55), ("S564", 45)]),
                      ("E516", [(None, 40), ("S555", 30), ("S556", 30)]),
                      ("E518", [(None, 25), ("S569", 40), ("S570", 35)]),
                      ("E519", [(None, 20), ("S571", 45), ("S572", 35)])):
        base = e[eid]["ai"][0]["cmds"][0]
        e[eid]["ai"][0]["cmds"] = [dict(base, skillid=sk, rate=w) for sk, w in cmds]
    e["E518"]["ai"][0]["actnum"] = [1, 2]
    for eid, a in (("E514", (1.6, "avg", 1.5)), ("E517", (1.8, "avg", 1.8)), ("E518", (1.0, "avg", 1.15)),
                   ("E519", (1.0, "avg", 1.2))):
        AREA[eid] = a
    # ---- Ronin Ch1 "What's Eating the Eta" (bosses.md 8. RONIN: b_dock_thugs L1, b_alley_ambush L4 Tetsuo Res3 + the
    # disguised Lion Res4, b_tengu_bridge L5 HPx4 Res5 weak Yumi/Air, b_bakemono L6 x6 Res2 weak Katana/Fire/Jade,
    # b_boss_tomie_cho L8 HPx8 Res9 weak Fire/Yari/Yumi in three forms; bestiary F "Cakon & the eta roads" 1-8). Sayo
    # alone; Hiro answers the Guest call from S04
    hum("E520", "Dock Thug", _he.EP["dock_ruffian"], 1, 0.7, 2, ["Katana", "Yumi"], "A dock thug who shoves fish-"
        "sellers into the river for fun.", atkx=0.7)
    hum("E521", "Tetsuo", _he.EP["tetsuo"], 4, 1.8, 3, ["Katana", "Yumi"], "A ronin of Daigoro's band, a scarred lip, "
        "dirty leather armour, a good wakizashi. He'll run at half.", atkx=0.8)
    hum("E522", "Disguised Lion", _he.EP["glory_bushi"], 4, 1.6, 4, ["Katana", "Yumi"], "A 'merchant' with a Lion's "
        "posture and a concealed katana. First blood satisfies him.", atkx=0.75)
    hum("E523", "Crow-Tengu", "EP158", 5, 3.0, 5, ["Yumi", "Air"], "A crow-headed tengu in a red silk kimono, fencing on "
        "a log to make travellers look foolish. Vain about its feathers.", atkx=0.8, exp=0, money=0)
    hum("E525", "Goblin", "EP106", 6, 0.42, 2, ["Katana", "Fire", "Jade"], "A bakemono with a basket of stolen pilgrim "
        "offerings. Each one looks slightly different from his neighbour.", atkx=0.7)
    hum("E526", "Tomie Cho", _he.EP["tomie_old"], 8, 2.5, 4, ["Fire", "Yari", "Yumi"], "An old woman with cloudy "
        "eyes, inside her mud hut. The walls take most of the blows. Fire will flush her out.", atkx=0.8, exp=0,
        money=0)
    hum("E527", "Tomie Cho", "EP182", 8, 6.0, 9, ["Fire", "Yari", "Yumi"], "The last of a family cursed for drinking "
        "from a sacred well: a weretiger, too old to catch rabbits. The eta don't run very fast.", atkx=1.0, exp=0,
        money=0)
    for eid in ("E521", "E522", "E523"):
        e[eid]["rt_flee"] = True                                                   # they fight to half, then go
    e["E521"]["rt_fleebark"] = "Not for Daigoro's money. Not for this."
    e["E522"]["rt_fleebark"] = "(dropping the merchant's hat) First blood. My honour is satisfied. Good day."
    e["E523"]["rt_fleebark"] = "Caw! A worthy crossing! (it flaps off, sulking)"
    e["E523"]["rt_tengu"] = True
    e["E526"]["rt_tomie_old"] = True
    e["E527"]["rt_tomie"] = True
    e["E523"]["item0"]["itemid"] = e["E523"]["item1"]["itemid"] = None            # (they flee: the feather is the
                                                                                  # bridge event's)
    e["E527"]["item0"].update({"itemid": "A162", "rate": 100.0})                  # drop: Tiger's Fang
    e["E527"]["item1"].update({"itemid": "I424", "rate": 100.0})                  # steal: Old Woman's Tea
    e["E526"]["item0"]["itemid"] = e["E526"]["item1"]["itemid"] = None
    for src, dst, lv, hpm, atm in (("E216", "E528", 3, 1.4, 1.6), ("E107", "E529", 3, 0.9, 1.5),
                                   ("E109", "E530", 4, 1.0, 1.4), ("E204", "E531", 5, 1.0, 1.1),
                                   ("E100", "E532", 4, 1.2, 1.5)):
        relevel(src, dst, lv, hpm=hpm, atm=atm, vs="avg")
    for eid, cmds in (("E523", [(None, 30), ("S590", 40), ("S591", 30)]), ("E525", [(None, 60), ("S592", 40)]),
                      ("E526", [(None, 50), ("S593", 50)]), ("E527", [(None, 20), ("S589", 50), ("S585", 30)])):
        base = e[eid]["ai"][0]["cmds"][0]
        e[eid]["ai"][0]["cmds"] = [dict(base, skillid=sk, rate=w) for sk, w in cmds]
    for eid, a in (("E520", (1.0, "avg", 1.0)), ("E521", (1.0, "avg", 1.0)), ("E522", (1.0, "avg", 1.0)),
                   ("E523", (1.0, "avg", 1.0)), ("E525", (1.0, "avg", 1.0)), ("E526", (1.0, "avg", 1.0)),
                   ("E527", (1.0, "avg", 0.88))):
        AREA[eid] = a
    # ---- Ronin Ch2 "The Noble and the Ronin" (bosses.md 8. RONIN: b_retainers_road L20 retainer x3 Res3 weak
    # Katana/Yumi, they flee at half; b_storm_jetties L22 retainer x4 + captain Res3/5, they surrender at low HP;
    # b_boss_snake_enforcers L25 HPx4 each x2 Res7 weak Katana/Fire/Jade + shadow-snake summons Res2 weak Fire/Air,
    # Poison bites, every 2 turns; the battle ends when the first enforcer is broken. Bestiary F "Floating Flowers &
    # river" 18-25: Wako Raider, Paddy Python, Kappa; uncommon Glory-Hungry Bushi; the den: Shadow-Snake (physical half),
    # Paddy Python, uncommon an Order "watcher" (the Kolat Agent's row). Sayo alone; Jinnai answers the Guest call
    hum("E533", "Ikoma Retainer", _he.EP["ikoma_retainer"], 20, 1.2, 3, ["Katana", "Yumi"], "One of Lord Ikoma "
        "Sadanobu's retainers. He beat a pilgrim into the snow because he was told to. He'll run at half.", atkx=0.9)
    hum("E534", "Ikoma Retainer", _he.EP["ikoma_retainer"], 22, 1.3, 3, ["Katana", "Yumi"], "Sadanobu's men, down "
        "the jetties with torches in a storm. Not paid enough for this. They'll give up when it goes badly.", atkx=0.9)
    hum("E535", "Retainer Captain", _he.EP["retainer_captain"], 22, 2.6, 5, ["Katana", "Yumi"], "Sadanobu's "
        "captain. Old enough to know better, loyal enough not to say so.", atkx=1.0)
    hum("E536", "Snake Enforcer", _he.EP["snake_enforcer"], 25, 3.0, 7, ["Katana", "Fire", "Jade"], "An enforcer of "
        "the Order of the Snake, a tattoo on the wrist, the face covered. The Order removes usurpers. Spies too.",
        atkx=1.0, exp=0, money=0)
    hum("E537", "Shadow-Snake", "EP175", 25, 0.6, 2, ["Fire", "Air"], "A snake of shadow, peeled off the den wall. "
        "Blades pass half through it. Fire and wind blow it out.", atkx=0.9, exp=0, money=0)
    hum("E538", "Shadow-Snake", "EP175", 23, 0.6, 2, ["Fire", "Air"], "A snake of shadow that slides along the den "
        "walls. Blades pass half through it. Fire and wind blow it out.", atkx=1.0)
    hum("E543", "Order Watcher", _he.EP["order_watcher"], 24, 1.1, 4, ["Jade", "Bo"], "One of the Order's watchers: a "
        "farmer by day, a black-edged tanto by night. He knows two other members. He'd die before naming them.")
    hum("E544", "Enforcer of the Order", "EP176", 25, 3.0, 7, ["Katana", "Fire", "Jade"], "The enforcer who speaks for "
        "the den. Grey robes, a black-edged blade, eyes that catch the candlelight. He has removed usurpers before.",
        atkx=1.0, exp=0, money=0)                                                  # (boss art: gen_bossart)
    # ---- Ronin Ch3 "The Village of the Wounded Lion" (bosses.md 8. RONIN: b_lion_checkpoint L30 Border Patrol x3 Res3
    # weak Tanto/Yumi; b_snow_beasts L31 x2 Res4 weak Fire/Yumi; b_frost_spirits L32 x3 Res3 weak Fire/Jade;
    # b_boss_ghost_guard_basin L35 HPx4 x3 Res5 weak Fire/Katana, physical halved + the basin Res10 weak Jade/Water/Bo,
    # every 2 turns a fallen guard rises, break the basin to end it. Bestiary F "Mountain of the White Snow" 28-35: Snow
    # Bear, Winter Wolf, Frost Spirit; uncommon Ghost-Guard; rare Wolf-Spirit). Sayo + Matsu Hanae; Hikaru for the
    # boss. The third guard is the shade of the Crab lord whose guards stole the prince (boss art)
    hum("E551", "Ghost-Guard", _he.EP["ghost_guard"], 33, 1.0, 4, ["Fire", "Katana"], "A rebel Imperial guard of "
        "three hundred years ago, frost in his lacing, replaying the night. Blades other than the katana pass half "
        "through him.")
    hum("E552", "Ghost-Guard", _he.EP["ghost_guard"], 35, 4.0, 5, ["Fire", "Katana"], "A rebel guard of the White "
        "Snow. The basin behind him keeps calling him back to his post.", atkx=1.0, exp=0, money=0)
    hum("E553", "Shade of the Crab Lord", "EP178", 35, 4.5, 6, ["Fire", "Katana", "Jade"], "The lord whose guards stole "
        "the prince, cut in two in the pagoda three hundred years ago. He still wants the throne. He still screams.",
        atkx=1.0, exp=0, money=0)
    hum("E554", "Bloodstone Basin", "EP181", 35, 6.0, 10, ["Jade", "Water", "Bo"], "A stone basin on a pedestal, "
        "heaped with red stones. Pure blood touched impure stone here. It is empty, and very still, and it calls the "
        "dead back to their posts.", atkx=1.0, exp=0, money=0)
    for eid in ("E551", "E552", "E553"):                                           # physical halved, except the katana
        e[eid]["option"].append({"opttype": "opt_elemdef", **{"EDR.%d" % i: 50 for i in range(1, 6)}})
    for eid in ("E552", "E553"):
        e[eid]["rt_ghostguard"] = True
        e[eid]["item0"]["itemid"] = e[eid]["item1"]["itemid"] = None
    e["E554"]["rt_basin"] = True
    e["E554"]["item0"].update({"itemid": "A163", "rate": 100.0})                  # drop: Bloodstone Shard
    e["E554"]["item1"]["itemid"] = None
    e["E551"]["item0"]["itemid"] = None
    for src, dst, lv, hpm, atm in (("E368", "E545", 30, 0.55, 0.9), ("E481", "E546", 31, 1.0, 1.2),
                                   ("E481", "E547", 31, 1.8, 1.1), ("E418", "E548", 32, 1.0, 1.2),
                                   ("E379", "E549", 31, 1.0, 1.3), ("E483", "E550", 34, 1.0, 1.2)):
        relevel(src, dst, lv, hpm=hpm, atm=atm, vs="avg")
    e["E545"]["name"] = "Lion Border Guard"
    e["E545"]["desc"] = "A Lion ashigaru at the north road checkpoint. Wave-folk go round by the goat track."
    e["E547"]["name"] = "Snow Beast"
    e["E547"]["desc"] = "A bear the size of a hut, white with old snow, that has eaten climbers before."
    for eid, cmds in (("E551", [(None, 55), ("S606", 45)]), ("E552", [(None, 50), ("S606", 50)]),
                      ("E553", [(None, 40), ("S606", 60)]), ("E554", [("S605", 100)])):
        base = e[eid]["ai"][0]["cmds"][0]
        e[eid]["ai"][0]["cmds"] = [dict(base, skillid=sk, rate=w) for sk, w in cmds]
    for eid in ("E551", "E552", "E553", "E554"):
        AREA[eid] = (1.0, "avg", 1.0)
    for eid in ("E537", "E538"):                                                   # physical half (bestiary III)
        e[eid]["option"].append({"opttype": "opt_elemdef", **{"EDR.%d" % i: 50 for i in range(6)}})
    e["E533"]["rt_flee"] = True
    e["E533"]["rt_fleebark"] = "(dropping the spear in the snow) The lord can hold his own criminals!"
    for eid in ("E534", "E535"):
        e[eid].update({"rt_surrender": 30, "rt_killflag": "G1070",
                       "rt_mercy": "Enough! Enough! Lord Sadanobu doesn't pay us for storms!"})
    e["E535"]["rt_mercy"] = "(lowering the katana) ...Enough. I yield. The boy isn't worth my men."
    e["E536"]["rt_enforcer"] = e["E544"]["rt_enforcer"] = True
    e["E537"]["rt_shadow"] = True
    e["E536"]["item0"]["itemid"] = None                                           # (Jinnai ends it: no spoils)
    e["E536"]["item1"].update({"itemid": "I434", "rate": 100.0})                  # steal: Shadow-snake Fang
    e["E544"]["item0"]["itemid"] = None
    e["E544"]["item1"].update({"itemid": "I434", "rate": 100.0})
    # ---- Ronin Ch4 "The Oracle's Choice" (bosses.md 8. RONIN: b_well_agents L42 Scorpion agent x3 Res4 weak Yumi/Katana,
    # they flee at low HP (script S4); b_race_assassins_1-5 L42-44 assassin x2-3 Res4 weak Yumi/Air, no full heal between;
    # b_boss_naga_champion L45 HPx12 Res16 weak Air/Yari/Fire, resist Water, Pearl Spear and Coil, talk-down on Suki
    # (naga_talked_down, Honor +), drop Naga Pearl, no steal. Bestiary F "Oracle's volcano town" 40-46: Kolat Agent,
    # Shosuro Renegade, Fire Elemental; the lava tube's den: fire elementals). Sayo; Hiro answers the Guest call (#14)
    hum("E555", "Scorpion Agent", _sc_epid("pilgrimagent"), 42, 1.2, 4, ["Yumi", "Katana"], "A pilgrim in plain robes "
        "and very good sandals, a needle in each sleeve. Paid to make a choice look like a curse. He runs when it hurts.")
    hum("E556", "Scorpion Assassin", _he.EP["shadow_in_black"], 42, 1.0, 4, ["Yumi", "Air"], "Black cloth, soft "
        "feet, and orders to make sure the eta girl never reaches the crater. The rooftops are his road.")
    hum("E557", "Scorpion Assassin", _he.EP["shadow_in_black"], 44, 1.1, 4, ["Yumi", "Air"], "Waiting on the "
        "switchback, where the stair is narrow and the drop is long. The last of the two dozen.")
    hum("E559", "The Naga's Champion", "EP184", 45, 12.0, 16, ["Air", "Yari", "Fire"], "A great serpent-bodied "
        "warrior in a pearl-white robe, the Great Naga's champion, the Order's guardian. Not evil. Poison runs off "
        "him like seawater. Sent to make sure "
        "the choice is the right one.", atkx=1.0)
    e["E559"]["option"].append({"opttype": "opt_elemdef", "EDR.%d" % ELEMS.index("Water"): 50})   # resists Water
    e["E559"]["rt_naga"] = True
    e["E559"]["item0"]["itemid"] = None                       # the Naga Pearl: given by the event (he coils aside,
    e["E559"]["item1"]["itemid"] = None                       # escaped, and escaped foes drop nothing); no steal
    for eid in ("E555",):
        e[eid].update({"rt_flee_pct": 25, "rt_fleebark": "(dropping the needle) Not for what they're paying!"})
    for src, dst, lv, hpm, atm in (("E484", "E558", 43, 0.6, 0.85), ("E226", "E560", 41, 1.0, 1.2),
                                   ("E227", "E561", 44, 1.1, 0.95)):
        relevel(src, dst, lv, hpm=hpm, atm=atm, vs="avg")
    for eid, cmds in (("E555", [(None, 60), ("S612", 40)]), ("E556", [(None, 65), ("S612", 35)]),
                      ("E557", [(None, 65), ("S612", 35)]), ("E559", [(None, 35), ("S610", 40), ("S611", 25)])):
        base = e[eid]["ai"][0]["cmds"][0]
        e[eid]["ai"][0]["cmds"] = [dict(base, skillid=sk, rate=w) for sk, w in cmds]
    # Sayo travels alone (Hiro's call twice a battle until the alley; hirelings; Yosai if met): the race is three to
    # five fights with no rest, so each one is light (like Ch3's checkpoint for a lone Sayo); the champion is a long
    # solo boss, his Resolve 16 the real wall
    for eid, a in (("E555", (0.6, "avg", 0.85)), ("E556", (0.45, "avg", 0.7)), ("E557", (0.5, "avg", 0.7)),
                   ("E559", (1.4, "avg", 1.0))):
        AREA[eid] = a
    # ---- The finale, Act 1 (production/finale.md; storyboard R: thunder_plain_road Danger 50-56, Goblin V, Ogre V,
    # Onikage IV+, uncommon Moto Akutsukai, rare Oni Spawn; F02 the seven waves at the Shrine of Osano-Wo, Lv 55-58).
    # From here the travelers fight four at a time (Party A / Party B), so every foe is tuned for a full party.
    for src, dst, lv in (("E251", "E562", 52), ("E254", "E563", 54), ("E242", "E564", 53), ("E515", "E565", 55),
                         ("E455", "E566", 56),                                        # the road
                         ("E251", "E567", 55), ("E231", "E568", 55), ("E254", "E569", 56), ("E254", "E570", 57),
                         ("E242", "E572", 56), ("E241", "E573", 56), ("E515", "E574", 57)):   # the waves
        relevel(src, dst, lv, vs="avg")
    for eid, name, desc in (
            ("E562", "Goblin Raider", "Out of the Shinomen with the host, ahead of it, looting as it goes."),
            ("E566", "Oni Spawn", "A small oni with no name yet, newly crawled out of a summoner's mistake. It wants "
                                  "one."),
            ("E567", "Goblin Raider", "The host's vanguard. The first wave is always goblins. It's tradition."),
            ("E568", "Goblin Fanatic", "Soaked in lamp oil and set alight by its friends, still laughing. Water puts "
                                       "it out. So does dying."),
            ("E569", "Ogre", "A slab of Shadowlands muscle under the ram."),
            ("E570", "Ogre Captain", "The ogre at the front of the ram, iron-collared, shouting in a language of "
                                     "grunts."),
            ("E572", "Onikage", "A demon horse loose inside the stockade, going for the abbot's hall."),
            ("E573", "Zombie", "Last year's dead from the burned villages, walked back across the plain."),
            ("E574", "Moto Akutsukai", "A dead Unicorn rider at the breach, and the dead come after it.")):
        e[eid]["name"], e[eid]["desc"] = name, desc
    e["E568"]["option"] = [weak_opt("Water", "Yari", "Jade")]
    hum("E571", "\"Ryozo\"", "EP186", 57, 7.0, 10, ["Jade", "Fire", "Katana"], "Polished Seppun armour over something "
        "that isn't a man. It took the name Natsuko left in a tunnel, and it loves it.", atkx=1.1)
    hum("E575", "Many-Legged Horror", "EP188", 58, 12.0, 12, ["Fire", "Jade", "Yumi"], "Out of the Shinomen behind the "
        "host: a spider the size of a hut, eyes like wet coals, and a smell of the Festering Pit.", atkx=1.05)
    for eid in ("E571", "E575"):
        e[eid]["item0"].update({"itemid": "I130", "rate": 100.0})                # drop: a Jade Pouch
        e[eid]["item1"]["itemid"] = None
    for eid, cmds in (("E568", [(None, 40), ("S619", 60)]), ("E570", [(None, 55), ("S620", 45)]),
                      ("E571", [(None, 50), ("S621", 25), ("S620", 25)]),
                      ("E575", [(None, 30), ("S622", 30), ("S623", 40)])):
        base = e[eid]["ai"][0]["cmds"][0]
        e[eid]["ai"][0]["cmds"] = [dict(base, skillid=sk, rate=w) for sk, w in cmds]
    # four travelers (T4/T5 gear, Lv 52-58) and a hireling: road fights of 2-3 foes, waves of 2-4, two wave leaders
    # (tested Lv 55, the arrival kits: each party fights three or four waves with no rest, so even the first ones
    # should cost something)
    for eid, a in (("E562", (2.2, "avg", 1.45)), ("E563", (2.4, "avg", 1.2)), ("E564", (1.8, "avg", 1.1)),
                   ("E565", (2.6, "avg", 1.1)), ("E566", (2.2, "avg", 1.1)),
                   ("E567", (2.3, "avg", 1.35)), ("E568", (2.6, "avg", 1.35)), ("E569", (2.6, "avg", 1.4)),
                   ("E570", (3.4, "avg", 1.6)), ("E572", (1.8, "avg", 1.0)), ("E573", (2.0, "avg", 1.0)),
                   ("E574", (2.8, "avg", 1.0)), ("E571", (2.4, "avg", 1.0)), ("E575", (2.0, "avg", 1.5))):
        AREA[eid] = a
    # ---- The finale, Act 2 "Shinomen Mori" (storyboard D Danger 55-60: Kumo Brood, Naga Scout, Lava Tree Dryad,
    # Toothed Poppy; uncommon Oni Spawn (E566); rare Wolf-Spirit. bosses.md: b_shinomen_a/b L56 Shadowlands beasts,
    # b_kumo_spiders L56 Kumo x3 weak Fire, only if rude to Mamoru)
    for src, dst, lv in (("E407", "E576", 56), ("E244", "E580", 56), ("E407", "E581", 57), ("E483", "E582", 59),
                         ("E455", "E579", 58)):
        relevel(src, dst, lv, vs="avg")
    for eid, name, mdl, desc in (
            ("E576", "Kumo Brood", "EP109", "Pale violet spiders the size of dogs, out of the silk under the Shinomen's "
                                            "roots. They come in clutches."),
            ("E580", "Toothed Poppy", "EP117", "A Shadowlands poppy, growing where nothing of hers should grow. It "
                                               "turns to follow you, and it has teeth."),
            ("E581", "Kumo", "EP109", "One of the old hermit's children, from the branches over his fire. It was "
                                      "listening. It did not like your tone."),
            ("E582", "Wolf-Spirit", "EP170", "A pale wolf that runs a hand's breadth above the moss and does not "
                                             "bend the ferns."),
            ("E579", "Oni Spawn", "EP208", "A young oni guarding the path for her, fat on silk and fear. It has no "
                                           "name yet, and it would very much like yours.")):
        e[eid].update({"name": name, "mdlid": mdl, "desc": desc})
    e["E566"]["mdlid"] = "EP208"              # the road's Oni Spawn too: boss art is for bosses (generated sprite)
    for eid in ("E576", "E581"):
        e[eid]["option"] = [weak_opt("Fire"), {"opttype": "opt_elemdef", "EDR.%d" % ELEMS.index("Earth"): 50}]
    hum("E577", "Naga Scout", "EP107", 57, 1.6, 6, ["Air", "Yari"], "A pearl-and-bronze serpent warrior of the "
        "waking Naga, scouting a forest that has changed while it slept. Not evil. Not hers. Break its guard and it "
        "will listen.")
    e["E577"]["option"].append({"opttype": "opt_elemdef", "EDR.%d" % ELEMS.index("Water"): 50})
    e["E577"].update({"rt_surrender": 25, "rt_yield_broken": True, "rt_killflag": "G1188",
                      "rt_mercy": "(the pearl spear lowers; a hiss like surf) Not ours to stop. Pass, warm-bloods."})
    hum("E578", "Lava Tree Dryad", "EP108", 57, 1.8, 6, ["Water", "Jade"], "The spirit of a Lava Tree, carried out of "
        "the Shadowlands and planted in the Shinomen: charred bark, fire in the cracks, roots for hair.")
    e["E578"]["option"].append({"opttype": "opt_elemdef", "EDR.%d" % ELEMS.index("Fire"): 50})
    for eid, cmds in (("E576", [(None, 60), ("S624", 40)]), ("E581", [(None, 50), ("S624", 50)]),
                      ("E577", [(None, 55), ("S610", 45)]), ("E578", [(None, 50), ("S625", 50)]),
                      ("E579", [(None, 60), ("S621", 40)])):
        base = e[eid]["ai"][0]["cmds"][0]
        e[eid]["ai"][0]["cmds"] = [dict(base, skillid=sk, rate=w) for sk, w in cmds]
    # a party of four (T5 gear, Lv 56-60): road fights of 2-4, two fixed fights (tuned by test)
    for eid, a in (("E576", (1.5, "avg", 1.45)), ("E577", (2.6, "avg", 1.4)), ("E578", (2.4, "avg", 1.35)),
                   ("E579", (1.4, "avg", 1.3)), ("E580", (1.0, "avg", 1.3)), ("E581", (1.8, "avg", 1.3)),
                   ("E582", (2.2, "avg", 1.2))):
        AREA[eid] = a
    # ---- The finale, Act 4 "The Empress of Nothing" (production F09; script ACT 4; bosses.md b_final_nashiko_p1-p3).
    # Party A fights phase 1, Party B phase 2, the best four phase 3. Plugin RokuganHazard (the finale): rt_bride (she
    # vanishes; jade or crystal reveals her; Blood Shouting through her champions, rt_bloodshout, unless the Phoenix
    # book "Against the Bloodspeakers" I177 broke it), rt_aging (the party ages each round), rt_trueform (Resolve 28
    # minus the debate's shields G1189; the exploits), rt_flee_pct (at 10% she flees: F10).
    hum("E583", "Doji Nashiko", "EP190", 60, 10.0, 20, ["Jade", "Crystal", "Yumi", "Air"], "The Bride, rising into the "
        "air on wings of smoke. Her seduced champions take her wounds for her. Sometimes she isn't there at all: crystal "
        "or jade finds her.", atkx=1.1, exp=0, money=0)
    hum("E584", "Seduced Champion", _he.EP["charmed_general"], 58, 2.0, 5, ["Yari", "Tanto", "Water"], "A samurai who "
        "met her at a court, once. His eyes are on her and nowhere else. Her wounds open on him. (Blood Shouting)",
        exp=0, money=0)
    hum("E585", "Body of Damned Time", "EP192", 60, 12.0, 24, ["Jade", "Crystal", "Water", "Bo"], "The glade is gone: "
        "an inky starfield, and her in it. Every moment here, you grow older.", atkx=1.05, exp=0, money=0)
    hum("E586", "The Empress of Nothing", "EP194", 61, 16.0, 28, ["Jade", "Crystal", "Katana", "Fire"], "Her loveliness "
        "peeled away: a black-edged wound in her throat pulsing with Fu Leng's glowing blood, empty sockets glowing "
        "blue. Jade, crystal and obsidian hurt her. She is colour-blind, she fears disfigurement, and she wanted one "
        "word all her life.", atkx=1.1, exp=0, money=0)
    e["E583"]["rt_bride"] = True
    e["E584"]["rt_bloodshout"] = True
    e["E585"]["rt_aging"] = True
    e["E586"].update({"rt_trueform": True, "rt_obsidian_weak": True, "rt_flee_pct": 10,
                      "rt_fleebark": "(cornered, her face flickering through every disguise) I was going to be "
                                     "EMPRESS-"})
    for eid in ("E583", "E584", "E585", "E586"):
        e[eid]["item0"]["itemid"] = e[eid]["item1"]["itemid"] = None
    for eid, cmds in (("E583", [(None, 35), ("S626", 30), ("S627", 35)]), ("E584", [(None, 100)]),
                      ("E585", [(None, 30), ("S628", 35), ("S629", 35)]),
                      ("E586", [(None, 20), ("S630", 30), ("S631", 30), ("S632", 20)])):
        base = e[eid]["ai"][0]["cmds"][0]
        e[eid]["ai"][0]["cmds"] = [dict(base, skillid=sk, rate=w) for sk, w in cmds]
    for eid, a in (("E583", (1.0, "avg", 0.75)), ("E584", (1.3, "avg", 0.9)), ("E585", (2.4, "avg", 1.1)),
                   ("E586", (1.6, "avg", 1.0))):
        AREA[eid] = a
    for eid in ("E585", "E586"):
        e[eid]["ai"][0]["actnum"] = [2, 2]                                    # a final boss against four: two a round
    for eid, rate in (("E537", 20.0), ("E538", 15.0)):
        e[eid]["item0"].update({"itemid": "I433", "rate": rate})                   # drop: Shadow Scale
        e[eid]["item1"]["itemid"] = None
    for src, dst, lv, hpm, atm in (("E431", "E539", 20, 1.0, 1.4), ("E462", "E540", 20, 1.0, 1.4),
                                   ("E430", "E541", 21, 1.0, 1.4), ("E464", "E542", 21, 1.0, 1.3)):
        relevel(src, dst, lv, hpm=hpm, atm=atm, vs="avg")
    for eid, cmds in (("E533", [(None, 60), ("S598", 40)]), ("E534", [(None, 60), ("S598", 40)]),
                      ("E535", [(None, 50), ("S598", 50)]), ("E536", [(None, 45), ("S599", 55)]),
                      ("E537", [(None, 40), ("S597", 60)]), ("E538", [(None, 40), ("S597", 60)]),
                      ("E544", [(None, 45), ("S599", 55)]),
                      ("E543", [(None, 50), ("S599", 50)])):
        base = e[eid]["ai"][0]["cmds"][0]
        e[eid]["ai"][0]["cmds"] = [dict(base, skillid=sk, rate=w) for sk, w in cmds]
    for eid, atm in (("E533", 1.0), ("E534", 0.75), ("E535", 0.85), ("E536", 0.7), ("E537", 0.45), ("E538", 1.0),
                     ("E543", 1.0), ("E544", 0.7)):                                  # (tested: Sayo alone + Jinnai, Lv 20-25)
        AREA[eid] = (1.0, "avg", atm)
    # Side stories that feed the finale's flight: SS-TEAM "The Inquisitors' Last Hunt" (sidestories/guests-07-12.md;
    # after Crab Ch4, Lv 45+: Natsuko, Goro and Michio clear the nest she left under the Wall) and Benjiro SS2 "The Moto
    # Curse" (guests-19-23.md #22: his father, a Moto akutsukai; on the Plains of Thunder road, Lv 52-56, the four)
    for src, dst, lv in (("E251", "E587", 46), ("E242", "E588", 46), ("E455", "E589", 47)):
        relevel(src, dst, lv, vs="avg")
    for eid, name, desc in (
            ("E587", "Nest Goblin", "Born under the Wall, in a nest a woman with blue eyes paid for. It has never seen "
                                    "the sky."),
            ("E588", "Nest Onikage", "A demon horse stabled in the dark under the Kaiu Wall, waiting for a rider."),
            ("E589", "Nest Oni Spawn", "Something small and new that the nest was feeding. It was going to be big.")):
        e[eid]["name"], e[eid]["desc"] = name, desc
    hum("E590", "Moto Akutsukai", "EP122", 55, 20.0, 14, ["Jade", "Fire", "Yari"], "A Unicorn rider in white death-"
        "paint, years dead, on a horse that isn't one. He rode in to die well, and something rode out wearing him. "
        "Benjiro's father.", atkx=1.25)
    e["E590"]["ai"][0]["actnum"] = [2, 2]
    e["E589"]["mdlid"] = "EP208"                        # (its source uses the Oni no Kommei boss art: bosses only)
    # The post-game, P1 "the gate back" (bestiary F row "Post-game: Shadowlands deep / Hiruma Castle", Lv 61-80: the
    # IV/V Shadowlands archetypes "Fallen", +30% stats; uncommon Troll Elder, rare Orochi-spawn V). The Fallen are
    # the finale's foes re-levelled, tuned below with AREA (the finale's road foes are 0.65 HP; x1.3).
    for src, dst, lv, name, desc in (
            ("E562", "E591", 62, "Fallen Goblin", "A goblin from the deep Shadowlands, where nothing has ever seen "
                                                  "the sun and everything is hungry."),
            ("E563", "E592", 64, "Fallen Ogre", "Bigger than the ones that come to the Wall. The deep makes them "
                                                "bigger."),
            ("E564", "E593", 63, "Fallen Onikage", "A demon horse gone feral in the deep, with no rider to want."),
            ("E565", "E594", 65, "Fallen Akutsukai", "A Moto rider dead so long the white paint has worn to bone."),
            ("E420", "E595", 63, "Fallen Kansen", "A kami of the deep places, corrupted past remembering its name."),
            ("E566", "E596", 66, "Fallen Oni Spawn", "A young oni that crawled out of the Festering Pit and kept "
                                                     "going."),
            ("E224", "E597", 64, "Fallen Bloodspeaker", "A maho-tsukai who walked into the deep to be closer to his "
                                                        "master, and found him.")):
        relevel(src, dst, lv, vs="avg")
        e[dst]["name"], e[dst]["desc"] = name, desc
    e["E596"]["mdlid"] = "EP208"
    hum("E598", "Troll Elder", "EP113", 66, 6.0, 10, ["Tetsubo", "Fire", "Jade"], "An old troll of the deep, grey as "
        "a cliff. It has eaten Crab armour for three hundred years and it still regrows what you cut off.", atkx=1.9)
    hum("E599", "Orochi-spawn", "EP441", 67, 5.0, 9, ["Air", "Yari"], "A young orochi, green scales gone grey, "
        "lost up the black rivers into the Shadowlands and mad with it.", atkx=1.9)
    for eid in ("E591", "E592", "E593", "E594", "E595", "E596", "E597"):
        AREA[eid] = (1.7, "avg", 1.4)
    for eid, n in (("E598", [2, 2]), ("E599", [2, 2]), ("E596", [1, 2])):     # the lone big ones: more than one
        e[eid]["ai"][0]["actnum"] = n                                            # action against a party of four
    AREA["E596"] = (1.7, "avg", 2.0)
    # P2 Shiro Hiruma (Lv 68-75): the castle's dead and the deep's Fallen a band higher; Oni no Okura holds the hall
    for src, dst, lv, name, desc in (
            ("E573", "E600", 69, "Restless Hiruma", "A Hiruma bushi who died holding the castle, fifteen generations "
                                                    "ago, and is holding it still. Against you."),
            ("E563", "E601", 70, "Fallen Ogre", "A castle ogre, fat on the old stores. It sleeps in the stables."),
            ("E565", "E602", 71, "Fallen Akutsukai", "A dead rider who stables in the Hiruma's own stalls now."),
            ("E224", "E603", 72, "Fallen Bloodspeaker", "A maho-tsukai who keeps Okura's court, and her rage."),
            ("E566", "E604", 72, "Fallen Oni Spawn", "One of Okura's brood, playing in the ruins.")):
        relevel(src, dst, lv, vs="avg")
        e[dst]["name"], e[dst]["desc"] = name, desc
        AREA[dst] = (1.7, "avg", 1.4)
    e["E604"]["mdlid"] = "EP208"
    AREA["E604"] = (1.7, "avg", 2.0)
    e["E604"]["ai"][0]["actnum"] = [1, 2]
    hum("E605", "Troll Elder", "EP113", 72, 6.0, 10, ["Tetsubo", "Fire", "Jade"], "An old troll of the deep, grey "
        "as a cliff, living in the Hiruma's well.", atkx=1.9)
    e["E605"]["ai"][0]["actnum"] = [2, 2]
    hum("E606", "Oni no Okura", "EP196", 75, 16.0, 22, ["Jade", "Crystal", "Tetsubo", "Fire"], "Akuma took the "
        "Jade Champion's name, and with its power made a daughter to carry on his rage. She has Shiro Hiruma now, "
        "and the Hiruma ancestors in its walls.", atkx=1.2)
    e["E606"]["ai"][0]["actnum"] = [2, 2]
    base = e["E606"]["ai"][0]["cmds"][0]
    e["E606"]["ai"][0]["cmds"] = [dict(base, skillid=sk, rate=w) for sk, w in
                                  ((None, 30), ("S639", 25), ("S640", 25), ("S641", 20))]
    for eid in ("E605", "E606"):
        e[eid]["item0"]["itemid"] = e[eid]["item1"]["itemid"] = None
    # P3 the Orochi (superboss, Lv 80; the Crane Ch3 sighting): it yields at 10% (rt_surrender), it isn't killed
    hum("E607", "The Orochi", "EP198", 80, 30.0, 30, ["Air", "Yari", "Tetsubo"], "A sea serpent out of Sakkaku, "
        "green as deep water, with eyes gold in the lightning. It keeps the ships it sinks, and the souls aboard them. "
        "It has no sense of humour at all.", atkx=1.3)
    e["E607"]["ai"][0]["actnum"] = [2, 2]
    e["E607"]["rt_surrender"] = 10
    e["E607"]["rt_killflag"] = "G1222"                                         # (not Crane Ch1's G336)
    base = e["E607"]["ai"][0]["cmds"][0]
    e["E607"]["ai"][0]["cmds"] = [dict(base, skillid=sk, rate=w) for sk, w in
                                  ((None, 25), ("S642", 30), ("S643", 25), ("S644", 20))]
    e["E607"]["item0"]["itemid"] = e["E607"]["item1"]["itemid"] = None
    e["E607"]["option"].append({"opttype": "opt_elemdef", "EDR.7": 50})        # (Water: its own sea)
    for eid, a in (("E587", (1.0, "avg", 0.9)), ("E588", (1.0, "avg", 0.9)), ("E589", (1.0, "avg", 0.9))):
        AREA[eid] = a
    for eid, (hpm, vs, atm) in AREA.items():
        hpx, atkx = HPX[eid]
        f = foe_stats(int(e[eid]["LV"]), hpx * hpm, atkx * atm, vs=vs)
        e[eid].update({"MAXHP": f["MAXHP"], "PATK": f["PATK"]})
    e["E235"]["item0"].update({"itemid": "I121", "rate": 100.0})              # drop: Filed Chain Link
    e["E235"]["item1"].update({"itemid": "A107", "rate": 100.0})              # steal: Torn Veil
    for eid in ("E234", "E236"):
        e[eid]["item0"]["itemid"] = e[eid]["item1"]["itemid"] = None
    # Grinding (user: "RNG encounters should be able to grind up some levels"): a foe pays 4% of the EXP a
    # traveler of its own level needs for the next level (the engine curve, RPGSystem.getExpByLV with expcurv
    # [50, 40]), so a 2-3 foe fight at your level is ~10% of a level: ~10 fights per level, Octopath-like. Bosses x
    # BOSS_EXP. Gold grows with it so T3 gear is reachable by grinding. Hand-tuned early values are kept if higher.
    def exp_by_lv(lv, et=(50, 40)):
        m, n, v = et[0], 0.5 + et[1] / 150.0, 0
        for _ in range(lv - 1):
            v += m
            m *= 1 + n
            n *= 0.91
        return int(v)
    BOSS_EXP = {"E527": 8, "E526": 3, "E523": 3, "E518": 8, "E519": 3, "E517": 2, "E513": 8, "E512": 2, "E508": 2, "E506": 6, "E505": 3, "E491": 8, "E490": 2, "E486": 8, "E487": 3, "E488": 3, "E478": 6, "E477": 3, "E471": 8, "E470": 3, "E460": 8, "E455": 3, "E448": 8, "E447": 3, "E440": 8, "E435": 8, "E423": 2, "E414": 8, "E415": 8, "E416": 8, "E417": 8, "E409": 8, "E410": 8, "E408": 3, "E402": 8, "E399": 8, "E395": 3, "E388": 8, "E389": 3, "E375": 8, "E374": 3, "E365": 8, "E363": 2, "E358": 6, "E360": 6, "E349": 3, "E346": 4, "E347": 8, "E327": 4, "E328": 4, "E331": 3, "E330": 8, "E315": 2, "E313": 5, "E106": 5, "E121": 3, "E235": 6, "E236": 3, "E245": 2, "E247": 6, "E248": 1, "E253": 2, "E255": 6, "E256": 3}
    BOSS_EXP.update({"E571": 3, "E575": 6, "E583": 6, "E585": 6, "E586": 8, "E590": 4, "E606": 8, "E607": 12})   # the finale: wave leaders, Nashiko
    for eid, x in e.items():
        if not ("E100" <= eid < "E999") or not isinstance(x, dict) or not x.get("LV") or x.get("rt_watcher"):
            continue                                         # (E3xx Crane, E4xx Lion/Phoenix/Dragon; a watcher pays nothing)
        lv = int(x["LV"])
        nxt = exp_by_lv(lv + 1) - exp_by_lv(lv)
        if eid == "E234":                                    # the troll hazard isn't killed, it sits down
            continue
        x["exp"] = max(int(x.get("exp") or 0), 6 + 3 * lv, int(round(0.04 * nxt * BOSS_EXP.get(eid, 1))))
        x["money"] = max(int(x.get("money") or 0), int(10 + 9 * lv * BOSS_EXP.get(eid, 1) ** 0.5))
    for eid, mdl in (("E486", "EP148"), ("E106", "EP120"), ("E234", "EP121"), ("E245", "EP122"), ("E247", "EP123"), ("E253", "EP124"),
                     ("E255", "EP125")):
        e[eid]["mdlid"] = mdl                                # boss art (tools/gen_bossart.py): bosses and mid-bosses
                                                             # ONLY; random-encounter foes keep the cast-style sprites
                                                             # (user). Never put these ids in an ENCOUNTERS table.
    itm = json.load(open(os.path.join(DATA, "item.json"), encoding="utf-8"))   # saved above: add drop items
    n_drops = bestiary_drops(e, itm)
    for eid, iid, rate in (("E576", "A169", 8.0), ("E581", "A169", 25.0), ("E577", "A165", 15.0)):
        e[eid]["item0"].update({"itemid": iid, "rate": rate})       # the finale's Shinomen: the accessories themselves
    salt = next(k for k, v in itm.items() if isinstance(v, dict) and v.get("name") == "Sea Salt")   # a Wako drop
    itm[salt] = dict(copy.deepcopy(itm["I130"]), name="Sea Salt", price=60,      # (by name: a new item called Sea
                     desc="Purifying salt, the Shinto way. Cleanses all Taint from one ally.")   # Salt renumbers I2xx)
    for eid in ("E329", "E332"):                         # the renamed Wako copies: Wako loot (set after relevel)
        e[eid]["item0"], e[eid]["item1"] = copy.deepcopy(e["E217"]["item0"]), copy.deepcopy(e["E217"]["item1"])
    for v in itm.values():                               # v4 sprites: using an item plays "item" (reach, raise, glow);
        ani = ((v.get("atkact") or {}).get("atkani") or {}) if isinstance(v, dict) else {}   # RokuganLook.sk falls
        if ani.get("id") == "magic1":                    # back to magic1 on sheets without it
            ani["id"] = "item"
    save("item", itm)
    import gen_sidecast as _sc                         # side-cast characters fought as enemies face the party
    _foe = {_sc.epid(i): _sc.foe_epid(i) for i in range(len(_sc.CAST))}
    for x in e.values():
        if isinstance(x, dict) and x.get("mdlid") in _foe:
            x["mdlid"] = _foe[x["mdlid"]]
    # Levelling ladders (tools/ladders.py; gen_maps apply_ladders writes the list): the chapter's own foes at a higher
    # level, scaled from the base foe's final stats by the level curve (foe_stats), exp ~ level^2, money ~ level.
    lad_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_ladder_foes.json")
    lad = json.load(open(lad_path, encoding="utf-8")) if os.path.exists(lad_path) else {}
    for nid, (base, lv) in sorted(lad.items()):
        b = e.get(base)
        if not isinstance(b, dict):
            print("ladder: no base foe %s for %s" % (base, nid))
            continue
        blv = max(1, int(b.get("LV") or 1))
        f0, f1 = foe_stats(blv), foe_stats(lv)
        x = copy.deepcopy(b)
        x["LV"] = lv
        for k in ("MAXHP", "PATK", "PDEF", "MDEF", "AGI"):
            if isinstance(b.get(k), (int, float)) and f0.get(k):
                x[k] = max(1, int(round(b[k] * f1[k] / f0[k])))
        x["exp"] = max(1, int(round((b.get("exp") or 1) * (lv / blv) ** 2)))
        x["money"] = max(1, int(round((b.get("money") or 1) * lv / blv)))
        e[nid] = x
    if lad:
        print("ladder foes: %d" % len(lad))
    # Sparring foes for testing (user 2026-11-12: "you will need a lot tougher enemies to test that stuff"): a debug
    # party kills ordinary foes before a Void critical, a stance or Stand Against the Waves shows. Lv 60, huge HP, they
    # hit back, weak to every weapon and element (Suki breaks); no EXP or money. M001 group 199 (TEST: sparring).
    f60 = foe_stats(60)
    for eid, nm, base, hpx, atkx in (("E998", "Sparring Oni", "E243", 60.0, 0.6),
                                     ("E997", "Sparring Ashigaru", "E200", 25.0, 0.5)):
        if base not in e:
            continue
        x = copy.deepcopy(e[base])
        x.update({"name": nm, "LV": 60, "MAXHP": int(f60["MAXHP"] * hpx), "PATK": int(f60["PATK"] * atkx),
                  "PDEF": f60["PDEF"], "MDEF": f60["MDEF"], "AGI": f60["AGI"], "RES": 6, "exp": 0, "money": 0,
                  "desc": "A test foe: it takes a beating and gives one back. (debug)",
                  "option": [weak_opt("Katana", "Yari", "Tanto", "Tetsubo", "Yumi", "Bo", "Fire", "Water", "Air",
                                      "Earth", "Void", "Jade", "Unarmed")]})
        e[eid] = x
    # Weakness memory (user 2026-11-12: "once a weakness for a species is revealed it should always stay revealed even
    # in the next time you see them"): one saved int var per species (same name = same species, so the ladder clones
    # share it) holding the revealed weakness bits; plugin RokuganJobs.sk loads / stores it.
    names = sorted({x["name"] for x in e.values() if isinstance(x, dict) and x.get("name")})
    assert len(names) < 1000, "species vars past G2999"
    species_var = {nm: "G%d" % (2000 + i) for i, nm in enumerate(names)}
    for x in e.values():
        if isinstance(x, dict) and x.get("name"):
            x["rt_species"] = species_var[x["name"]]
    gv2 = load_built("gvar")
    for k in [k for k in gv2 if k[1:].isdigit() and 2000 <= int(k[1:]) <= 2999]:
        del gv2[k]
    for nm, v in species_var.items():
        gv2[v] = {"defval": 0, "name": "weakness memory: %s (revealed weakness bits)" % nm, "type": 2}
    save("gvar", gv2)
    for x in e.values():                                # job EXP (jobs_data.py): the same from every foe
        if isinstance(x, dict) and "jxp" in x:
            x["jxp"] = _jobs.ENEMY_JXP
    save("enemy", e)
    print("bestiary drops:", n_drops, "enemies")

    # ---- player.json (travelers)
    import gen_sidecast as _sc
    SC_EP = {c["key"]: _sc.epid(i) for i, c in enumerate(_sc.CAST)}
    p = load("player")
    import traits as _traits
    TRAIT_CURVES = _traits.curves(p["P000"]["lvcurve"])
    pb = p["P000"]
    COMPANION_CURVES = {"P120": ("P100", {"MAXHP": 1.35, "PDEF": 1.15, "PATK": 1.1, "AGI": 0.8}),   # Hida: biggest
                        "P123": ("P100", {"MAXHP": 1.15, "PDEF": 1.05, "AGI": 0.9}),               # Kage's bodyguard
                        "P132": ("P100", {"MAXHP": 0.9, "PATK": 0.8, "PDEF": 0.75, "AGI": 1.1}),     # Yosai
                        "P133": ("P100", {"MAXHP": 0.75, "PATK": 0.45, "PDEF": 0.55, "AGI": 1.15}),  # Hayato
                        "P134": ("P100", {"MAXHP": 1.0, "PATK": 1.05, "PDEF": 0.95, "AGI": 1.0}),   # Ushimo
                        "P135": ("P100", {"MAXHP": 0.7, "PATK": 0.3, "PDEF": 0.6, "AGI": 1.0}),     # Sanro
                        "P136": ("P100", {"MAXHP": 0.8, "PATK": 0.9, "PDEF": 0.85, "AGI": 1.1}),   # Rui
                        "P137": ("P104", {"MAXHP": 0.95}),                                         # Kasiko
                        "P138": ("P103", {"MAXHP": 1.0, "PATK": 1.05}),                            # Akodo Rin
                        "P139": ("P100", {"MAXHP": 0.85, "PATK": 0.8, "PDEF": 0.8, "AGI": 1.05}),   # Tamori Haku
                        "P140": ("P100", {"MAXHP": 1.1, "PATK": 1.0, "PDEF": 1.05, "AGI": 1.1}),    # Shinjo Ryuko
                        "P141": ("P100", {"MAXHP": 0.95, "PATK": 1.2, "PDEF": 0.9, "AGI": 1.0}),    # Matsu Hanae
                        "P131": ("P100", {"MAXHP": 0.75, "PATK": 0.45, "PDEF": 0.55, "AGI": 1.05})}  # Haruki's
    # yojimbo guards; Haruki's spells carry the fight (user: shugenja lean heavy on spells)
    travelers = [
        ("P100", "Hiruma Natsuko", "EP200", "W101", "Hiruma scout of the Kaiu Wall. Gallows humour; holds the line."),
        ("P101", "Kakita Rensei", "EP201", "W100", "Kakita duelist, yojimbo to the Keeper of the House Honour."),
        ("P102", "Kitsuki Gendo", "EP202", "W105", "Kitsuki junior yoriki. Evidence over testimony."),
        ("P103", "Akodo Shizue", "EP203", "W100", "Akodo strategist from a minor house. Thinks in go."),
        ("P104", "Isawa Haruki", "EP204", "W105", "Isawa shugenja of Water and Void. Counts on his fingers."),
        ("P105", "Shosuro Mitsue", "EP205", "W102", "Shosuro agent. Nobody is very easy to be."),
        ("P106", "Ide Tamotsu", "EP206", "W104", "Ide emissary. Being liked is his only weapon; he keeps it sharp."),
        ("P107", "Sayo", "EP207", "W100", "Wave-woman herbalist born on a rice barge."),
        # guests who fight alongside a traveler in scripted scenes (S01 goblin raid: whoever is on the Wall)
        ("P120", "Hida Sachiko", "EP303", "W103", "Hida Sachiko. A loud Wall veteran with a big hammer."),
        ("P121", "Hiruma Ryoichi", "EP304", "W102", "Hiruma Ryoichi. Natsuko's friend; peasant weapons."),
        ("P122", "Squeak", "EP351", "W102", "Squeak-of-Many-Eggs. Talk good-good. Steals maps for a good cause."),
        # Crab Ch2 short-term companions (only Natsuko is playable; paths use companions until travelers meet)
        ("P123", "Hiruma Goro", SC_EP["goro"], "W110", "Kage's bodyguard at court. A bent katana and big fists."),
        ("P124", "Isawa Michio", SC_EP["michio"], "W115", "Phoenix Inquisitor, Earth tensai. Brilliant, and he knows "
                                                          "it."),
        # Crab Ch3
        ("P125", "Gonta", "EP342", "W113", "Gonta of the Hidden Ones. Big, patient, and fond of landslides."),
        ("P126", "Hiruma Kage", SC_EP["kage_ch3"], "W113", "The Hiruma daimyo, without armour. A fallen tetsubo."),
        # Lion Ch1 (the Magonojo raid, S01): short-term companions
        ("P127", "Akodo Gusai", SC_EP["gusai"], "W100", "Hiruto's younger son. Matsu-trained, war-hungry, grinning."),
        ("P128", "Lion rider", SC_EP["lionrider"], "W101", "One of Lord Hiruto's riders. Does what Gusai says, mostly."),
        # Lion Ch2: Akodo Kafu fights beside Shizue against Ianwa if the talk-down reaches him (kafu_joins)
        ("P129", "Akodo Kafu", SC_EP["kafu_nosword"], "W102", "Toturi's advisor. A short sword, and nothing left to lose."),
        # Lion Ch4: if Shizue crosses the river herself, her uncle and cousin hold the ford (production S03)
        ("P130", "Akodo Hiruto", SC_EP["hiruto"], "W110", "Shizue's uncle. Calm as a go board, and as hard to read."),
        # Phoenix Ch1: Kamasari's yojimbo, told to "keep the boy from falling off his horse" (user: a shugenja never
        # travels alone; at least a yojimbo in the front row)
        ("P131", "Shiba Ashimita", SC_EP["ashimita"], "W110", "Kamasari's yojimbo. Lean, controlled; his grandfather "
                                                               "screams in his ear."),
        # every path until the travelers join up (user): a tattooed Togashi who is never serious (cast #27)
        # Phoenix Ch4: the Emerald Magistrates' tired Crane yoriki walks Haruki to the cliffs (user: a yojimbo)
        # Dragon Ch3: Seppun Ushimo travels with Gendo once Tsuhime sleeps (tsuhime_helped), through Ch4
        ("P134", "Seppun Ushimo", SC_EP["ushimo"], "W121", "An Imperial guard of the year 400. He was at the end of his "
                                                           "rope. Gendo cut a different sentence."),
        # Dragon Ch4: the boy Isawa Sanro rides along to the lighthouse front (an escort: if he falls, History -30)
        ("P135", "Isawa Sanro", SC_EP["sanro"], "W105", "A bright boy of twelve with ink on his fingers. He thinks the "
                                                        "fire has a spirit. He's right."),
        # Scorpion Ch1: the acting Mantis magistrate of Kudo walks into the marsh with Mitsue (S05 to the end)
        ("P136", "Yoritomo Rui", SC_EP["rui"], "W146", "A junior Mantis yoriki running a magistracy alone. Loud "
                                                       "when she's frightened, so: loud."),
        # Scorpion Ch2: the last Emerald Magistrate of her team, hidden by the shadow hunters (S05 to the end)
        ("P137", "Isawa Kasiko", SC_EP["kasiko"], "W105", "An Emerald Magistrate, Phoenix, very small, very "
                                                           "precise. Her whole team is dead or worse."),
        # Scorpion Ch3: the tribunal's Lion escort, a drop of Seppun blood in her (S01 to the end)
        ("P138", "Akodo Rin", SC_EP["akodorin"], "W121", "The tribunal's escort. Raised as the son her father wanted; "
                                                          "fights as herself now, mostly."),
        # Unicorn Ch1: Tsune's yojimbo for his junior negotiator (user: Tamotsu is never without a Shinjo guardian)
        ("P140", "Shinjo Ryuko", SC_EP["ryuko"], "W100", "Tsune's niece, assigned to keep the emissary alive. Says "
                                                         "very little. Stands in front of things."),
        # Ronin Ch3: the leader of the five grandchildren climbs beside Sayo (the climb, the fortress, the descent)
        ("P141", "Matsu Hanae", SC_EP["hanae"], "W134", "A Matsu, granddaughter of a legend. Proud, sharp, and about to "
                                                        "find out what her family's glory is made of."),
        # Scorpion Ch4: a young Tamori monk sent down to escort "pilgrims" (only while Yosai is lost in the ink)
        ("P139", "Tamori Haku", SC_EP["haku"], "W106", "A young Tamori monk in heat-wards. Says what he smells. "
                                                       "Usually right."),
        ("P133", "Doji Hayato", SC_EP["hayato"], "W110", "A tired Crane yoriki. Eats rice balls on steps; listens when "
                                                         "nobody else will."),
        ("P132", "Togashi Yosai", SC_EP["yosai"], "W106", "A tattooed Togashi. Keeps a tally of the Fortunes' attempts "
                                                           "on his life. He is winning."),
    ]
    for pid, name, mdl, wid, desc in travelers:
        x = copy.deepcopy(pb)
        x.update({"name": name, "mdlid": mdl, "desc": desc, "equips": [wid, "A000"], "defskillid": "S003",
                  "voiceid": "", "lvoption": [{"LV": 1, "opttype": "opt_getskill", "skillid": "S110"}] if pid == "P100"
                  else haruki_spells() if pid == "P104"
                  else [{"LV": lv, "opttype": "opt_getskill", "skillid": k} for lv, k in (
                      (1, "S132"), (1, "S154"), (8, "S155"), (12, "S156"), (16, "S157"), (22, "S158"), (26, "S159"))]
                  if pid == "P122"
                  else [{"LV": 1, "opttype": "opt_getskill", "skillid": "S139"}] if pid == "P123"
                  else [{"LV": 1, "opttype": "opt_getskill", "skillid": "S169"}] if pid == "P120"
                  else [{"LV": lv, "opttype": "opt_getskill", "skillid": k} for lv, k in ((3, "S140"), (6, "S142"),
                                                                                         (22, "S141"))]
                  if pid == "P105"
                  else [{"LV": 1, "opttype": "opt_getskill", "skillid": k} for k in ("S138", "S363", "S300", "S305")]
                  if pid == "P124"
                  else [{"LV": 1, "opttype": "opt_getskill", "skillid": "S147"}] if pid == "P125"
                  else [{"LV": 1, "opttype": "opt_getskill", "skillid": "S148"},      # "takes huge damage"
                        {"LV": 1, "opttype": "opt_status", "propid": "PDEF", "val": -50, "valtype": "totalrate"},
                        {"LV": 1, "opttype": "opt_status", "propid": "PATK", "val": 15, "valtype": "totalrate"}]
                  if pid == "P126"
                  else [{"LV": 25, "opttype": "opt_getskill", "skillid": "S426"}] if pid == "P101"
                  else [{"LV": 5, "opttype": "opt_getskill", "skillid": "S476"}] if pid == "P102"   # Interrogate
                  else [{"LV": 1, "opttype": "opt_getskill", "skillid": k} for k in ("S460", "S461")] if pid == "P132"
                  else [{"LV": 1, "opttype": "opt_getskill", "skillid": "S489"}] if pid == "P134"
                  else [{"LV": 1, "opttype": "opt_getskill", "skillid": "S499"}] if pid == "P135"
                  else [{"LV": 1, "opttype": "opt_getskill", "skillid": k} for k in ("S506", "S507")]
                  if pid == "P136"
                  else [{"LV": 1, "opttype": "opt_getskill", "skillid": k} for k in ("S303", "S304", "S300")]
                  if pid == "P137"
                  else [{"LV": 1, "opttype": "opt_getskill", "skillid": k} for k in ("S526", "S527")]
                  if pid == "P138"
                  else [{"LV": 1, "opttype": "opt_getskill", "skillid": k} for k in ("S537", "S538")]
                  if pid == "P139"
                  else [{"LV": 1, "opttype": "opt_getskill", "skillid": k} for k in ("S546", "S547")]
                  if pid == "P140"
                  else [{"LV": 1, "opttype": "opt_getskill", "skillid": k} for k in ("S607", "S608")]
                  if pid == "P141"
                  else [{"LV": lv, "opttype": "opt_getskill", "skillid": k} for lv, k in ((1, "S542"), (3, "S544"),
                                                                                         (5, "S543"), (41, "S566"))]
                  if pid == "P106"
                  else [{"LV": lv, "opttype": "opt_getskill", "skillid": k} for lv, k in ((1, "S580"), (1, "S581"),
                                                                                         (3, "S583"), (6, "S584"))]
                  if pid == "P107"
                  else []})
        x["lvoption"] = list(x["lvoption"]) + rank_options(pid) + _kata.level_options(pid)   # progression-v2.md
        if pid in SHUGENJA_ELEM and pid != "P104":     # shugenja companions: two spells of their element per rank
            x["lvoption"] += rank_spells(pid, {o.get("skillid") for o in x["lvoption"]})
        if pid in SCHOOL_KEY:
            x["rt_school_key"] = SCHOOL_KEY[pid]
        if pid in ADV_SCHOOLS:
            x["MAXLV"] = 100                       # (user: the advanced school's last technique at Lv 100)
        if pid == "P122":
            x["INILV"] = 10                        # joins for the S08 boss (user 2026-11-12: Lv 6 was too weak to help
            # against the shaman)
        if pid in TRAIT_CURVES:                    # docs/rules/stats.md traits -> per-traveler growth (tools/traits.py)
            x["lvcurve"] = TRAIT_CURVES[pid]
        elif pid == "P124" and x.get("lvcurve"):  # companion shugenja (Michio): magic grows like a bushi's attack
            lc = x["lvcurve"] = copy.deepcopy(x["lvcurve"])
            lc["ATK"], lc["MATK"] = lc["MATK"], lc["ATK"]
        if pid in COMPANION_CURVES:                # clan roles: the Crab companions get Natsuko's curve, more HP
            base, mult = COMPANION_CURVES[pid]
            lc = x["lvcurve"] = copy.deepcopy(TRAIT_CURVES[base])
            for k, m in mult.items():
                lc[k] = [max(1, int(round(v * m))) for v in lc[k]]
        p[pid] = x
    # (user 2026-11-12: "why do the travelers and companions lose stats on some level ups?") the trait curves wobble
    # (Natsuko's AGI 220 -> 214): every stat curve only ever rises
    for x in p.values():
        if isinstance(x, dict) and isinstance(x.get("lvcurve"), dict):
            lc = x["lvcurve"] = copy.deepcopy(x["lvcurve"])
            for k, arr in lc.items():
                if isinstance(arr, list) and arr and all(isinstance(v, (int, float)) for v in arr):
                    top = arr[0]
                    for i, v in enumerate(arr):
                        top = max(top, v)
                        arr[i] = top
    # Haruki had no TP at all; kiho cost TP (user 2026-11-12) -> a small pool, 60% of Sayo's curve
    if "P104" in p and "P107" in p and p["P107"].get("lvcurve", {}).get("MAXTP"):
        lc = p["P104"]["lvcurve"] = copy.deepcopy(p["P104"]["lvcurve"])
        if not any(lc.get("MAXTP") or []):
            lc["MAXTP"] = [max(0, int(v * 0.6)) for v in p["P107"]["lvcurve"]["MAXTP"]]
    save("player", p)
    party_typed_attacks(p)

    # ---- map.json: M001 random encounters -> Crab Ch1 groups (keeps the sample's battle backdrops M800/M804)
    mp = load("map")
    groups = mp["M001"]["encount"]
    g1, g2 = copy.deepcopy(groups[0]), copy.deepcopy(groups[1])
    g1.update({"name": "Goblin raid (b_goblin_raid)", "rate": 70, "mapid": "M810", "enemies": [
        {"id": "E100", "x": -0.9, "z": 1.5}, {"id": "E100", "x": -1.6, "z": -1.9},
        {"id": "E101", "x": 0.5, "z": -0.3}, {"id": "E100", "x": -2.4, "z": 0.25}]})
    g2.update({"name": "Egg caves (b_cave_nezumi_a)", "rate": 50, "enemies": [
        {"id": "E102", "x": -1.5, "z": -0.25}, {"id": "E103", "x": 0.8, "z": -0.2},
        {"id": "E102", "x": -0.4, "z": 1.4}]})
    g3 = copy.deepcopy(groups[0])
    g3.update({"name": "TEST: Suki/Boost training", "rate": 0, "gid": 3, "enemies": [{"id": "E190", "x": 0.0, "z": 0.0}]})
    g4 = copy.deepcopy(groups[0])
    g4.update({"name": "TEST: human mobs (bandit/ronin/samurai/ashigaru)", "rate": 0, "gid": 4, "enemies": [
        {"id": "E200", "x": -0.9, "z": 1.5}, {"id": "E204", "x": -1.6, "z": -1.9},
        {"id": "E208", "x": 0.5, "z": -0.3}, {"id": "E212", "x": -2.4, "z": 0.25}]})
    g5 = copy.deepcopy(groups[0])
    g5.update({"name": "TEST: cultists & ninja", "rate": 0, "gid": 5, "enemies": [
        {"id": "E220", "x": -0.9, "z": 1.5}, {"id": "E222", "x": -1.6, "z": -1.9},
        {"id": "E225", "x": 0.5, "z": -0.3}, {"id": "E215", "x": -2.4, "z": 0.25}]})
    g6 = copy.deepcopy(groups[0])
    g6.update({"name": "Sumai: Gonta (b_hidden_ones_sumai)", "rate": 0, "gid": 6, "mapid": "M812",
               "enemies": [{"id": "E120", "x": -0.6, "z": 0.0}]})
    g_sumai = copy.deepcopy(g6)
    g_sumai.update({"name": "Sumai match (set up by ::Rokugan.sumaiMatch)", "gid": 900, "enemies": [{"id": "E121", "x": -0.6, "z": 0.0}]})
    cave = []
    for gid, nm, foes in ((7, "b_cave_nezumi_a", ["E102", "E102", "E102"]),
                          (8, "b_cave_beetles", ["E103", "E103", "E103"]),
                          (9, "b_cave_nezumi_b", ["E102", "E102", "E102"]),
                          (10, "b_boss_grasping_paw", ["E102", "E106", "E102"]),
                          (11, "b_boss_grasping_paw_ryozo", ["E102", "E106", "E121"])):
        g = copy.deepcopy(groups[0])
        spots = [(-1.5, -0.25), (0.6, -0.2), (-0.4, 1.4)]
        g.update({"name": "Egg Caves (%s)" % nm, "rate": 0, "gid": gid, "mapid": "M813",
                  "enemies": [{"id": f, "x": spots[i][0], "z": spots[i][1]} for i, f in enumerate(foes)]})
        cave.append(g)
    g12 = copy.deepcopy(g3)
    g12.update({"name": "TEST: Rumble meter (training dummy in the Egg Caves)", "gid": 12, "mapid": "M813"})
    ch2 = []
    for gid, nm, bmap, foes in ((13, "b_donjon_goblins", "M815", ["E231", "E231", "E231"]),
                                (14, "b_boss_puppet_troll", "M815", ["E235", "E234"]),
                                (15, "b_duel_noboru", "M816", ["E236"]),
                                (16, "b_ss_sakura_agent", "M816", ["E238", "E238"]),
                                (17, "b_ss_takeo_race", "M814", ["E239", "E239"]),
                                (18, "b_sl_goblins", "M817", ["E240", "E240", "E240", "E240"]),
                                (19, "b_sl_onikage", "M817", ["E242", "E242"]),
                                (20, "b_sl_akutsukai", "M817", ["E245", "E241"]),
                                (21, "b_boss_kommei", "M818", ["E247", "E248", "E246", "E246"]),
                                (22, "b_siege_breach_a", "M810", ["E250", "E251", "E250", "E251"]),
                                (23, "b_siege_breach_b", "M815", ["E253", "E252", "E252"]),
                                (24, "b_boss_tsukakoro", "M810", ["E255"]),
                                (25, "b_ss_goro_troll", "M810", ["E256"]),
                                (26, "b_hunt_boars", "M811", ["E109", "E109"]),
                                (27, "b_bokken_bout", "M820", ["E300"]),
                                (28, "b_hunt_boar_west", "M821", ["E305"]),
                                (29, "b_forest_bandits_a", "M822", ["E301", "E301", "E301"]),
                                (30, "b_forest_bandits_b", "M821", ["E301", "E301", "E301"]),
                                (31, "b_boss_yasurugi", "M823", ["E313"]),
                                (32, "b_boss_yasurugi_cells", "M824", ["E313"]),
                                (33, "b_camp_sentries_a", "M825", ["E314", "E314", "E314"]),
                                (34, "b_camp_sentries_b", "M825", ["E314", "E314", "E314"]),
                                (35, "b_boss_iron_cranes", "M825", ["E326", "E315", "E315", "E315"]),
                                (36, "b_midboss_chihaya", "M828", ["E327"]),
                                (37, "b_storm_yosuke", "M830", ["E328", "E329", "E329"]),
                                (38, "b_boss_katsuo", "M829", ["E330", "E332", "E332"]),
                                (39, "b_boss_katsuo_ryohei", "M829", ["E330", "E331", "E332"]),
                                # Crane Ch3 sea legs (gen_maps ship_deck sea chart: 1-2 roll-picked fights per leg)
                                (40, "b_sea_wako", "M827", ["E333", "E333"]),
                                (41, "b_sea_eel", "M827", ["E334", "E333"]),
                                (42, "b_sea_crabs", "M827", ["E335", "E335", "E335"]),
                                (43, "b_sea_corsair", "M827", ["E336", "E333"]),
                                (44, "b_sea_umibozu", "M830", ["E337"]),
                                # Crane Ch4 (production crane-ch4.md)
                                (45, "b_archive_spirits", "M831", ["E342", "E342", "E342", "E342"]),
                                (46, "b_archive_guardian", "M831", ["E346"]),
                                (47, "b_boss_masanori", "M832", ["E347"]),
                                # Lion Ch1 (production lion-ch1.md)
                                (48, "b_warehouse_raid", "M833", ["E348", "E348", "E348"]),
                                (49, "b_nagai_possessed", "M834", ["E349"]),
                                (50, "b_duel_ozaki", "M834", ["E350"]),
                                (51, "b_duel_gusai", "M834", ["E351"]),
                                (52, "b_duel_ashimita", "M834", ["E352"]),
                                (53, "b_duel_shiba_guard", "M835", ["E357"]),
                                (54, "b_boss_otamai", "M836", ["E358", "E359"]),
                                (55, "b_boss_otamai_yard", "M834", ["E358", "E359"]),
                                (56, "b_boss_otamai_nohost", "M836", ["E360", "E359"]),
                                (57, "b_boss_otamai_yard_nohost", "M834", ["E360", "E359"]),
                                # Lion Ch2 (production lion-ch2.md)
                                (58, "b_bracket_1", "M838", ["E361"]), (59, "b_bracket_2", "M838", ["E362"]),
                                (60, "b_bracket_3", "M838", ["E363"]),
                                (61, "b_fear_shades", "M839", ["E364", "E364", "E364"]),
                                (62, "b_boss_ianwa", "M839", ["E365", "E371", "E371"]),
                                (63, "b_winter_den", "M837", ["E366", "E366", "E366"]),
                                # Lion Ch3 (production lion-ch3.md)
                                (64, "b_bridge_bandit", "M840", ["E372"]),
                                (65, "b_pass_ronin", "M837", ["E373", "E373", "E373"]),
                                (66, "b_shogen_test", "M837", ["E374"]),
                                (67, "b_boss_miya_killers", "M837", ["E375", "E376", "E376"]),
                                # Lion Ch4 (production lion-ch4.md); the waves and the boss at the ford (M842)
                                (68, "b_gusai_duel", "M833", ["E389"]),
                                (69, "b_ford_waves_1", "M842", ["E381", "E381", "E381"]),
                                (70, "b_ford_waves_1 (victory stone)", "M842", ["E382", "E382", "E382"]),
                                (71, "b_ford_waves_2", "M842", ["E383", "E383", "E383"]),
                                (72, "b_ford_waves_3", "M842", ["E384", "E384", "E384"]),
                                (73, "b_ford_waves_4", "M842", ["E385", "E386", "E386"]),
                                (74, "b_ford_waves_5", "M842", ["E387", "E387", "E387"]),
                                (75, "b_boss_rokuro_demon", "M842", ["E388"]),
                                (76, "b_berserker_duel", "M841", ["E390"]),
                                # Phoenix Ch1 (production phoenix-ch1.md)
                                (77, "b_shrine_guardian_shards", "M835", ["E394", "E394", "E394"]),
                                (78, "b_ashimoshi", "M843", ["E395"]),
                                (79, "b_boss_otamai (Phoenix: Haruki and his yojimbo)", "M836", ["E399", "E359"]),
                                # Phoenix Ch2 (production phoenix-ch2.md)
                                (80, "b_pass_cultists", "M844", ["E401", "E400", "E400", "E400"]),
                                (81, "b_boss_hioninmaru", "M845", ["E402", "E400", "E400", "E400"]),
                                (82, "pass: the mountain-wolf den", "M844", ["E403", "E403", "E403"]),
                                # Phoenix Ch3 (production phoenix-ch3.md)
                                (83, "b_forest_fever_spirits", "M846", ["E405", "E405", "E405"]),
                                (84, "b_mieko_dark_mid", "M846", ["E408"]),
                                (85, "b_boss_oni_no_kuzushi", "M847", ["E409"]),
                                (86, "b_boss_oni_no_kuzushi (stayed a day)", "M847", ["E410"]),
                                # Phoenix Ch4 (production phoenix-ch4.md): the boss by dream keys 0 / 1 / 2 / 3
                                (87, "b_mieko_shadows_a", "M848", ["E412", "E412", "E412"]),
                                (88, "b_mieko_shadows_b", "M848", ["E413", "E413", "E413"]),
                                (89, "b_boss_mieko_dark (0 keys)", "M849", ["E414"]),
                                (90, "b_boss_mieko_dark (1 key)", "M849", ["E415"]),
                                (91, "b_boss_mieko_dark (2 keys)", "M849", ["E416"]),
                                (92, "b_boss_mieko_dark (3 keys)", "M849", ["E417"]),
                                # Dragon Ch1 (production dragon-ch1.md)
                                (93, "b_dock_tutorial", "M850", ["E421"]),
                                (94, "b_gusai_thugs_a", "M851", ["E422", "E422"]),
                                (95, "b_gusai_thugs_b", "M851", ["E425", "E425", "E425"]),
                                (96, "b_boss_tide", "M852", ["E423", "E423", "E424", "E424"]),
                                # Dragon Ch2 (production dragon-ch2.md)
                                (97, "b_cove_crabs", "M853", ["E433", "E433", "E433"]),
                                (98, "b_cove_guards", "M853", ["E434", "E434", "E434"]),
                                (99, "b_boss_ushimo", "M854", ["E435"]),
                                # Dragon Ch3 (production dragon-ch3.md)
                                (100, "b_scout_camp", "M855", ["E438", "E437", "E437"]),
                                (101, "b_izumida_musketeers", "M855", ["E438", "E438", "E438"]),
                                (102, "b_boss_parley", "M856", ["E440", "E442", "E441"]),
                                # (Gendo alone: Tsuhime not helped, no Ushimo) the same fights, one foe fewer
                                (103, "b_izumida_musketeers (alone)", "M855", ["E438", "E438"]),
                                (104, "b_scout_camp (alone)", "M855", ["E438", "E437"]),
                                # Dragon Ch4 (production dragon-ch4.md)
                                (105, "b_front_land", "M857", ["E446", "E446", "E443"]),
                                (106, "b_front_mantis (a duel)", "M856", ["E447"]),
                                (107, "b_front_lighthouse", "M858", ["E445", "E445", "E444"]),
                                (108, "b_harbour_musketeers", "M859", ["E444", "E444", "E444"]),
                                (109, "b_boss_kumpei_flagship", "M860", ["E448", "E444"]),
                                # Scorpion Ch1 (production scorpion-ch1.md)
                                (110, "b_road_bandits", "M861", ["E449", "E449", "E449"]),
                                (111, "b_kommei_brood", "M862", ["E455"]),
                                (112, "b_marsh_leeches", "M863", ["E457", "E457", "E457", "E457"]),
                                (113, "b_boss_kansen_hana", "M864", ["E460"]),
                                # Scorpion Ch2 (production scorpion-ch2.md; Doji Siko from the adventure)
                                (114, "b_siko (Doji Siko's ambush)", "M866", ["E470", "E466"]),
                                (115, "b_stitched_monks_a", "M867", ["E466", "E466", "E466"]),
                                (116, "b_stitched_monks_b", "M867", ["E467", "E467", "E467"]),
                                (117, "b_boss_munashii", "M868", ["E471"]),
                                # Scorpion Ch3 = Unicorn Ch2 (production unicorn-ch2-scorpion-ch3.md)
                                (118, "b_boss_iuchi_hit_squad", "M871", ["E478", "E477", "E477", "E477"]),
                                # Scorpion Ch4 "The Eve" (production scorpion-ch4 S06-S07)
                                (119, "b_furnace_elementals", "M873", ["E487", "E487", "E487"]),
                                (120, "b_ash_ghouls", "M873", ["E488", "E488", "E488"]),
                                (121, "b_boss_stolen_face", "M874", ["E486"]),
                                # Unicorn Ch1 "Fault Lines" (production unicorn-ch1 S02, S06, S07)
                                (122, "b_camp_thugs", "M875", ["E489", "E489", "E489"]),
                                (123, "b_cave_guerrillas", "M876", ["E490", "E490", "E490", "E490"]),
                                (124, "b_boss_naohida", "M877", ["E491", "E490", "E490", "E492"]),
                                # Unicorn Ch2: the hit squad at Tamotsu's band (production S04)
                                (125, "b_boss_iuchi_hit_squad", "M871", ["E506", "E505", "E505", "E505"]),
                                # Unicorn Ch3 "The Noblest Blood" (production S02, S05, S06)
                                (126, "b_tower_servants", "M878", ["E508", "E508", "E508"]),
                                (127, "b_mine_dead_a", "M879", ["E512", "E512", "E512", "E512"]),
                                (128, "b_mine_dead_b", "M879", ["E512", "E512", "E512", "E512"]),
                                (129, "b_boss_mine_guardian", "M880", ["E513", "E512", "E512"]),
                                # Unicorn Ch4 "Regret" (production S02, S04)
                                (130, "b_tunnel_legion", "M881", ["E517", "E517", "E517", "E517"]),
                                (131, "b_boss_kurosho_regret", "M882", ["E518", "E519"]),
                                # Ronin Ch1 "What's Eating the Eta" (production S01, S03a, S05, S06, S07)
                                (132, "b_dock_thugs", "M883", ["E520", "E520"]),
                                (133, "b_alley_ambush", "M883", ["E521", "E522"]),
                                (134, "b_tengu_bridge", "M884", ["E523", "E523"]),
                                (135, "b_bakemono", "M885", ["E525", "E525", "E525", "E525"]),
                                (136, "b_boss_tomie_old", "M887", ["E526"]),
                                (137, "b_boss_tomie_cho", "M886", ["E527"]),     # (BOSS_LAYOUT)
                                # Ronin Ch2 "The Noble and the Ronin" (production S01, S04, S08). The jetties: four
                                # retainers and the captain, or three if the spy's lantern was pilfered (G1083)
                                (138, "b_retainers_road", "M888", ["E533", "E533", "E533"]),
                                (139, "b_storm_jetties", "M889", ["E535", "E534", "E534", "E534", "E534"]),
                                (140, "b_storm_jetties (one squad lost)", "M889", ["E535", "E534", "E534", "E534"]),
                                (141, "b_boss_snake_enforcers", "M890", ["E544", "E536", "E537", "E537"]),
                                # Ronin Ch3 "The Village of the Wounded Lion" (production S00, S02, S04)
                                (142, "b_lion_checkpoint", "M891", ["E545", "E545", "E545"]),
                                (143, "b_snow_beasts", "M892", ["E547", "E547"]),
                                (144, "b_frost_spirits", "M892", ["E548", "E548", "E548"]),
                                (145, "b_boss_ghost_guard_basin", "M893", ["E553", "E552", "E552", "E554"]),
                                # Ronin Ch4 "The Oracle's Choice" (production S04, S06, S07; the storyboard's lava tube)
                                (146, "b_well_agents", "M895", ["E555", "E555", "E555"]),
                                (147, "b_race_assassins_1", "M895", ["E556", "E556"]),
                                (148, "b_race_assassins_2", "M895", ["E556", "E556"]),
                                (149, "b_race_assassins_3", "M896", ["E557", "E557", "E557"]),
                                (150, "b_race_assassins_4", "M896", ["E557", "E557"]),
                                (151, "b_race_assassins_5", "M896", ["E557", "E557"]),
                                (152, "b_lava_tube", "M894", ["E558", "E558"]),
                                (153, "b_boss_naga_champion", "M896", ["E559"]),
                                # The finale, Act 1: the seven waves at the Shrine of Osano-Wo (production F02; the
                                # "k" variants: Kage's Hiruma hold a flank, one foe fewer; 158: "Ryozo" leads the ram)
                                (154, "b_shrine_wave_1", "M898", ["E567", "E567", "E567", "E567"]),
                                (155, "b_shrine_wave_2", "M898", ["E569", "E567", "E567"]),
                                (156, "b_shrine_wave_3", "M898", ["E568", "E568", "E568"]),
                                (157, "b_shrine_wave_4", "M898", ["E570", "E569"]),
                                (158, "b_shrine_wave_4_ryozo", "M898", ["E571", "E569"]),
                                (159, "b_shrine_wave_5", "M898", ["E572", "E572", "E567", "E567"]),
                                (160, "b_shrine_wave_5_kage", "M898", ["E572", "E567", "E567"]),
                                (161, "b_shrine_wave_6", "M898", ["E574", "E573", "E573"]),
                                (162, "b_shrine_wave_6_kage", "M898", ["E574", "E573"]),
                                (163, "b_shrine_wave_7", "M898", ["E575"]),
                                # The finale, Act 2: the Shinomen's fixed fights (bosses.md)
                                (164, "b_shinomen_a", "M899", ["E579", "E576", "E576"]),
                                (165, "b_shinomen_b", "M899", ["E578", "E578", "E580", "E580"]),
                                (166, "b_kumo_spiders", "M899", ["E581", "E581", "E581"]),
                                # The finale, Act 4: the three phases (backdrops M806 the glade, M807 the starfield)
                                (167, "b_boss_final_nashiko_p1", "M806", ["E583", "E584", "E584"]),
                                (168, "b_boss_final_nashiko_p2", "M807", ["E585"]),
                                (169, "b_boss_final_nashiko_p3", "M806", ["E586"]),
                                (170, "b_ss_team_nest", "M813", ["E588", "E587", "E589", "E587"]),
                                (171, "b_ss_benjiro_father", "M897", ["E590"]),
                                (172, "b_boss_okura", "M808", ["E606"]),
                                (173, "b_superboss_orochi", "M809", ["E607"])):
        g = copy.deepcopy(groups[0])
        spots = ([(-0.6, 1.2), (-2.6, -0.8)] if gid == 14 else
                 [(-0.6, 0.2), (-1.2, 1.7), (-2.6, -0.8), (-2.8, 1.4)] if gid == 21 else
                 [(-2.6, 0.4), (-0.4, -1.0), (-0.6, 1.4), (-1.6, -2.2), (-1.8, 2.4)] if gid == 139 else
                 [(-0.4, 0.0), (-2.4, -0.4), (-1.5, 1.6), (-2.9, 1.3)])
        g.update({"name": "Scripted (%s)" % nm, "rate": 0, "gid": gid, "mapid": bmap,
                  "enemies": [{"id": f, "x": spots[i][0], "z": spots[i][1]} for i, f in enumerate(foes)]})
        ch2.append(g)
    # Octopath bosses (user): the boss looms large at the back-left (gen_bossart wiki art), minions stand in front
    BOSS_LAYOUT = {135: [("E525", -2.4, -1.4), ("E525", -2.4, 0.4), ("E525", -2.2, 2.1), ("E525", -0.8, -0.6),
                         ("E525", -0.6, 1.2), ("E525", -1.3, 3.0)],           # six goblins with baskets
                   134: [("E523", -2.8, -1.8), ("E523", -0.6, 2.0)],          # two tengu on the log
                   131: [("E518", -2.7, 1.3), ("E519", -0.4, -1.3)],        # the Doji behind, Kurosho in front
                   124: [("E491", -2.4, 0.3), ("E490", -1.2, -1.5), ("E490", -1.2, 1.9), ("E492", -0.2, -0.5),
                         ("E492", -0.2, 1.0)],                         # Naohida, his guerrillas, the powder kegs
                   10: [("E106", -2.3, 0.7), ("E102", -0.4, -0.7), ("E102", -0.6, 0.8)],
                   11: [("E106", -2.3, 0.7), ("E102", -0.4, -0.7), ("E121", -0.6, 0.8)],
                   14: [("E235", -0.5, -0.6), ("E234", -2.4, 0.8)],
                   20: [("E245", -2.3, 0.6), ("E241", -0.4, -0.7)],
                   21: [("E247", -2.2, 0.8), ("E248", -1.2, 1.6), ("E246", -0.3, -0.9), ("E246", -0.5, 0.7)],
                   23: [("E253", -2.3, 0.7), ("E252", -0.4, -0.8), ("E252", -0.6, 0.7)],
                   24: [("E255", -2.0, 0.6)],
                   25: [("E256", -2.0, 0.6)], 31: [("E313", -2.0, 0.6)], 32: [("E313", -2.0, 0.6)],
                   35: [("E326", -2.3, 0.5), ("E315", -0.5, -0.9), ("E315", -0.3, 0.5), ("E315", -1.3, 1.8)],
                   36: [("E327", -2.0, 0.6)],
                   37: [("E328", -2.3, 0.6), ("E329", -0.4, -0.8), ("E329", -0.6, 0.8)],
                   38: [("E330", -2.3, 0.6), ("E332", -0.4, -0.8), ("E332", -0.6, 0.8)],
                   39: [("E330", -2.3, 0.7), ("E331", -0.5, -0.7), ("E332", -0.6, 0.9)],
                   46: [("E346", -2.0, 0.6)], 47: [("E347", -2.0, 0.6)],
                   49: [("E349", -2.0, 0.6)],
                   54: [("E358", -2.5, 1.0), ("E359", -0.4, -1.0)], 55: [("E358", -2.5, 1.0), ("E359", -0.4, -1.0)],
                   56: [("E360", -2.5, 1.0), ("E359", -0.4, -1.0)], 57: [("E360", -2.5, 1.0), ("E359", -0.4, -1.0)],
                   62: [("E365", -2.4, 0.8), ("E371", -0.4, -0.9), ("E371", -0.6, 0.9)],
                   67: [("E375", -2.3, 0.7), ("E376", -0.6, -1.0), ("E376", -0.4, 1.2)],
                   73: [("E385", -2.2, 0.0), ("E386", -0.5, -1.1), ("E386", -0.5, 1.1)],
                   75: [("E388", -2.4, 0.0)], 78: [("E395", -2.4, 0.0)],
                   79: [("E399", -2.5, 1.0), ("E359", -0.4, -1.0)],
                   80: [("E401", -2.6, 0.0), ("E400", -0.6, -1.4), ("E400", -0.3, 0.0), ("E400", -0.6, 1.4)],
                   81: [("E402", -2.5, 0.0), ("E400", -0.6, -1.4), ("E400", -0.3, 0.0), ("E400", -0.6, 1.4)],
                   84: [("E408", -2.3, 0.0)], 85: [("E409", -2.4, 0.0)], 86: [("E410", -2.4, 0.0)],
                   89: [("E414", -2.3, 0.0)], 90: [("E415", -2.3, 0.0)], 91: [("E416", -2.3, 0.0)],
                   92: [("E417", -2.3, 0.0)], 111: [("E455", -2.2, 0.0)], 113: [("E460", -2.4, 0.0)],
                   117: [("E471", -2.4, 0.0)],
                   141: [("E544", -2.5, 0.4), ("E536", -0.4, -1.0), ("E537", -0.6, 1.3), ("E537", -1.3, 2.7)],
                   145: [("E553", -2.6, 0.2), ("E554", -1.2, 2.4), ("E552", -0.3, -1.2), ("E552", -0.4, 1.0)],
                   153: [("E559", -2.2, 0.6)],
                   157: [("E570", -2.0, 0.4), ("E569", -0.4, 1.6)], 158: [("E571", -2.2, 0.5), ("E569", -0.4, 1.7)],
                   163: [("E575", -2.2, 0.6)],
                   167: [("E583", -2.4, 0.3), ("E584", -0.4, -1.2), ("E584", -0.5, 1.6)],
                   168: [("E585", -2.3, 0.4)], 169: [("E586", -2.4, 0.5)],
                   171: [("E590", -2.4, 0.2)], 172: [("E606", -2.4, 0.3)], 173: [("E607", -2.6, 0.2)]}
    for g in cave + ch2:
        if g["gid"] in BOSS_LAYOUT:
            g["enemies"] = [{"id": f, "x": x, "z": z} for f, x, z in BOSS_LAYOUT[g["gid"]]]
    import gen_maps as _gm                              # a backdrop not built yet (Crane Ch3 slices D-G): the Crane
    for g in ch2:                                       # coast (map.json is rebuilt here, so ask gen_maps)
        if g["mapid"] not in mp and g["mapid"] not in _gm.MAPS:
            g["mapid"] = "M826"
    g_spar = copy.deepcopy(groups[0])                   # (user: tough foes to test Void crits, kata, stances)
    g_spar.update({"name": "TEST: sparring (Lv 60, huge HP)", "rate": 0, "gid": 199, "mapid": "M838", "enemies": [
        {"id": "E998", "x": -0.9, "z": 0.2}, {"id": "E997", "x": -1.8, "z": -1.6}, {"id": "E997", "x": -1.8, "z": 1.8}]})
    mp["M001"]["encount"] = [g1, g2, g3, g4, g5, g6, g_sumai] + cave + [g12] + ch2 + [g_spar]
    import gen_music as _mu                             # the soundtrack (user: "more medieval Japanese"): each boss
    for g in mp["M001"]["encount"]:                     # gets its theme (gen_music BATTLE_MUSIC: standard, oni, duel,
        g["bgmid"] = _mu.battle_music(g.get("name"))    # intrigue, mini-boss, the finale's three, the superbosses)
    mp["M000"]["bgmid"] = _mu.MUSIC["travelers"]        # the title screen: the travelers' theme
    title_update_entry(mp["M000"]["event"]["#1000001#"])
    mp["M001"]["bgmid"] = _mu.MUSIC["town"]             # (the template map the generated maps copy)
    # field placeholders -> HD-2D sprites: villager = Hiruma Ryoichi (EP304), wandering symbol enemies = goblins
    ev = mp["M001"]["event"]
    ev["#1000002#"]["mdlid"] = "EP304"
    ev["#1000002#"]["msg"] = "Natsuko! The karo wants you. He said \"at once\" - for Kaiu-sama that means an hour ago."
    # side cast standing around the garrison yard (gen_sidecast EP300+ order: kisada 300, kage 301, takakana 302,
    # sachiko 303, ryoichi 304 ...)
    for eid, mdl, pos, msg in (
            ("#1000010#", "EP302", [48, 5, 58, 2],
             "Men are dumb enough to fight fair. The Shadowlands are not. Remember the flares: red, green... "
             "and pray you never see blue."),
            ("#1000011#", "EP303", [52, 5, 66, 2],
             "Sach watch is over! Anyone seen my shochu? ...No? Then nobody saw me looking for it.")):
        x = copy.deepcopy(ev["#1000002#"])
        x.update({"mdlid": mdl, "pos": pos, "msg": msg, "name": "*villager-%s" % eid.strip("#")[-2:]})
        ev[eid] = x
    for k in ("#1000001#", "#1000008#"):
        ev[k]["mdlid"] = "EP106"
    save("map", mp)

    # ---- setting.json
    st = load("setting")
    st.update({"title": "Rokugan Traveler", "subtitle": "An unofficial L5R fan game", "projname": "RokuganTraveler",
               "projlang": "en", "inimembers": ["P100"], "battlecmd4": "boost",   # Octopath: each chapter starts solo
               "inimap": __import__("gen_maps").START,
               "battlecmd5": "talent", "battlecmd7": "guest",    # Guest replaces Formation (no Octopath rows)
               "maxmembers": 8})        # (user 2026-11-14) 8 places in two rows; at most 4 until the finale (RokuganParty)
    save("setting", st)

    # ---- plugin.json
    pj_path = os.path.join(PROJ, "plugin", "plugin.json")
    pj = json.load(open(pj_path, encoding="utf-8"))
    pj["rokugan"] = {"enable": True, "bpmax": 5, "boostmax": 3, "sukirate": 50}
    json.dump(pj, open(pj_path, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")
    english_leftovers()
    print("data generated")


def english_leftovers():
    """The template's Japanese that a player can see (user: "I don't know kanji"): the menu labels in type.json and
    the descriptions of template records still in use. Unused template records are left alone. (Reads the files
    as generated above: load() returns the untouched template.)"""
    def load(name):                                       # noqa: F811 - the current generated file, not the template
        return json.load(open(os.path.join(DATA, name + ".json"), encoding="utf-8"))
    t = load("type")
    names = {
        "eqslot": ["Weapon", "Shield", "Head", "Body", "Accessory"],
        "eqtype": ["Unarmed", "Tanto", "Katana", "Yari", "Axe", "Bo", "Yumi", "Tetsubo", "Light Shield",
                   "Heavy Shield", "Hat", "Helmet", "Hair Ornament", "Clothes", "Light Armour", "Heavy Armour",
                   "Accessory", "Accessory"],
        "dmgform": ["Physical attack", "Magic attack", "Healing magic", "Physical magic", "Attack item",
                    "Healing item", "Debuff"],
        "eqflag": ["Traveler's gear", "Women's gear", "Elven gear", "Heavy gear"],
        "jobflag": ["Hero's mark", "Royal blood"],
        "jobslot": __import__("jobs_data").JOB_SLOTS,       # Job + Trait 1-4 (user 2026-11-14: "up to 4 traits")
        "resistg": ["Death resist", "Poison resist", "Sleep resist", "Paralysis resist", "Mind resist",
                    "Curse resist", "Exhaustion resist", "Focus resist"],
        "tribe": ["Human", "Male", "Female", "Flying", "Construct", "Undead", "Insect", "Demon", "Beast", "Spirit",
                  "Dragon", "Aquatic"]}
    while len(t.get("jobslot", [])) < len(names["jobslot"]):          # more slots than the template's two
        t["jobslot"].append(dict(t["jobslot"][-1]))
    for key, lst in names.items():
        for i, nm in enumerate(lst):
            if i < len(t.get(key, [])) and isinstance(t[key][i], dict):
                t[key][i]["name"] = nm
    for js in t.get("jobslot", []):                    # (user 2026-11-12: the Job slot showed a padlock - jobs could
        if isinstance(js, dict):                       # not be changed; progression-v2 jobs need both slots open)
            js["lock"] = 0
    save("type", t)
    fixes = {"armor": {"A141": {"desc": "Light and sturdy."}},
             "item": {"I000": {"desc": "A useless thing."}, "I001": {"desc": "Restores HP."},
                      "I004": {"desc": "A night's rest in the open: restores the whole party's HP and MP. Not usable "
                                       "in dangerous places."},
                      "I010": {"desc": "Restores HP."}, "I011": {"desc": "Restores HP."},
                      "I016": {"desc": "Revives a fallen ally."}},
             "job": {"J105": {"desc": "Attack up at the start of each battle."}},   # (J000: jobs_data.py)
             "cond": {"K005": {"desc": "Asleep: can't act for a while. A physical hit wakes them."}},
             "skill": {"S003": {"desc": "A plain attack with no weapon."}, "S190": {"name": "Auto-Revive"}},
             "player": {}}
    for f, recs in fixes.items():
        d = load(f)
        for rid, upd in recs.items():
            if rid in d:
                d[rid].update(upd)
        if f == "player":                                 # no template Wooden Shield on the travelers (no samurai
            for pid, pl in d.items():                     # carries one): drop A000 from every starting kit
                if isinstance(pl, dict) and isinstance(pl.get("equips"), list):
                    pl["equips"] = [None if e == "A000" else e for e in pl["equips"]]
        save(f, d)
    english_pass()


# (user 2026-11-12: "Lots of Japanese characters still in the game, example selecting spell when using a bushi gives
# Japanese explanation") Template entries the game can show, in English; then any Japanese name / desc left in the
# player-facing tables is replaced with a plain English stand-in and listed.
ENGLISH = {
    "skill": {"S004": ("Steal", None), "S010": ("Slash", None), "S011": ("Heavy Slash", None),
              "S012": ("Thrust", None), "S013": ("Strike", None), "S014": ("Shot", None), "S020": ("Claw", None),
              "S027": ("Drain Blood", None), "S035": ("Heal", "Restores a little HP to one ally."),
              "S036": ("Greater Heal", "Restores a lot of HP to one ally."),
              "S038": ("Heal All", "Restores a little HP to every ally."),
              "S040": ("Cure", "Cures poison, blindness, silence and sealed skills on one ally."),
              "S043": ("Raise", "Revives a fallen ally."),
              "S045": ("Guard Up", "Raises one ally's defence for a while."),
              "S046": ("Guard Up All", "Raises every ally's defence for a while."),
              "S073": ("Fire", None), "S074": ("Greater Fire", "A middle-rank fire spell."),
              "S076": ("Ice", None), "S077": ("Greater Ice", None)},
    "item": {"I019": (None, "Cures poison, paralysis, blindness and sealing."),
             "I020": (None, "Cures sleep, confusion and charm.")},
    "job": {"J001": (None, "A special calling only the chosen may take."),
            "J101": (None, "A heart of iron that nothing shakes: resists mind-affecting ailments."),
            "J102": (None, "Shields a weakened ally."), "J104": (None, "A light step that slips past attacks.")},
    "store": {"R000": ("Village Goods", None), "R001": ("Healing Arts", None)},
}


def english_pass():
    import re
    jp = re.compile(r"[぀-ヿ一-鿿]")
    left = []
    for f in ("skill", "item", "job", "store", "weapon", "armor", "cond", "enemy", "player"):
        d = load_built(f)
        for rid, (nm, desc) in ENGLISH.get(f, {}).items():
            if rid in d and isinstance(d[rid], dict):
                if nm:
                    d[rid]["name"] = nm
                if desc:
                    d[rid]["desc"] = desc
        for rid, x in d.items():
            if not isinstance(x, dict):
                continue
            for fld in ("name", "desc"):
                if isinstance(x.get(fld), str) and jp.search(x[fld]):
                    x[fld] = ("(unused %s %s)" % (f, rid)) if fld == "name" else ""
                    left.append("%s %s %s" % (f, rid, fld))
            # (user 2026-11-12 screenshot: an empty description shows the engine's Japanese sample text in the skill
            # tooltip) never leave one empty
            if f in ("skill", "item", "weapon", "armor") and not (x.get("desc") or "").strip() and x.get("name"):
                x["desc"] = x["name"] + "."
        save(f, d)
    print("english pass: %d template strings blanked (unused sample data)" % len(left))


if __name__ == "__main__":
    main()
    import apply_resources
    apply_resources.main()
    import gen_maps                     # Crab Ch1 maps (M100+): re-register after map.json was rebuilt
    gen_maps.register_all()
    import re                           # every global flag an event uses must be declared in gvar.json
    used = set(re.findall(r'"(G\d{3})"', open(os.path.join(DATA, "map.json"), encoding="utf-8").read()))
    used |= set(re.findall(r"\b(G\d{3})\b", "".join(re.findall(r'"code": "([^"]*)"', open(os.path.join(
        DATA, "map.json"), encoding="utf-8").read()))))
    missing = sorted(used - set(json.load(open(os.path.join(DATA, "gvar.json"), encoding="utf-8"))))
    if missing:
        print("WARNING: flags used by map events but missing from gvar.json:", ", ".join(missing))
