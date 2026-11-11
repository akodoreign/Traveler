"""Kata, kiho and Togashi tattoos learned on level-up (docs/rules/progression-v2.md; user 2026-11-11: "they should be
part of an attack, you activate them and then for X turns (sometimes the whole battle) you gain the effect";
"Bushi learn kata, Shugenja and Monks get Kiho, monks get more as that's their skill, also the togashi should get a
new tattoo at the school levels, like Tiger, Raven, and something at 5th").

Each entry is an attack with the user's own weapon (x mult) that puts a stance condition on the user for `turns`
turns (99 = the whole battle). One stance at a time: a new kata replaces the old (plugin RokuganRanks.sk).
Content from kata.md / kiho.md (the 3e effects translated to stats; the fiddly ones simplified).

Fields: (sid, cid, pid, level, kind, name, mult, turns, mods, extra, desc)
  level None = not learned by level (a dojo or story reward: DOJO_KATA)
  mods = [(prop, val)], prop in PATK PDEF MATK MDEF AGI (percent of the stat) or PHIT PEVA CRI CEVA TGR (points)
  extra = extra cond options (opt_counter / opt_conddef / opt_autocond dicts) or None
"""

RATE = ("PATK", "PDEF", "MATK", "MDEF", "AGI", "MAXHP")       # totalrate (percent of the stat); the rest are points

COUNTER = lambda rate: {"opttype": "opt_counter", "skillid": None, "formbits": 1, "elembits": 0,  # noqa: E731
                        "rate": rate, "hittype": 0, "hitact": None}
RESIST = lambda *bits: dict({"opttype": "opt_conddef"}, **{"CDR.%d" % b: 100 for b in bits})     # noqa: E731
AUTOREVIVE = {"opttype": "opt_autocond", "condid": "K042", "req": "hp25"}

N, R, G, S, H, M, Y, YO = "P100", "P101", "P102", "P103", "P104", "P105", "P107", "P132"

KATA = [
    # ---- Hiruma Natsuko (Hiruma Scout; Hida dojo gives Striking as Earth)
    ("S740", "K070", N, None, "kata", "Striking as Earth", 1.0, 3, [("PEVA", 15), ("PHIT", -10)], None,
     "Crab kata. Settle like the mountain: +15% evasion, -10% accuracy for 3 turns."),
    ("S741", "K071", N, 10, "kata", "Striking as Wind", 1.0, 3, [("AGI", 20), ("PATK", -15)], None,
     "Move like the wind: Speed +20%, damage -15% for 3 turns."),
    ("S742", "K072", N, 25, "kata", "Shell of Stone", 1.0, 3, [("PDEF", 50), ("PHIT", -10)], None,
     "Hiruma kata. Armour mode: DEF +50%, accuracy -10% for 3 turns."),
    ("S743", "K073", N, 41, "kata", "Stance of the Wall", 1.0, 99, [("PEVA", 10), ("TGR", 100), ("AGI", -20)],
     [COUNTER(0.3)], "Hiruma kata. Draw the enemy's eye (+evasion, foes target her) and strike back at 30% of those "
     "who attack her. Speed -20%. The whole battle."),
    ("S744", "K074", N, 51, "kata", "Shards of Earth", 1.6, 1, [("PATK", 30)], None,
     "Hiruma kata. A blow through the carapace: x1.6, and ATK +30% next turn."),
    ("S745", "K075", N, 61, "kata", "Unyielding Fury", 1.0, 99, [("PDEF", 20)], [COUNTER(0.6)],
     "Hida kata. Every blow she takes may be answered (60% counter). The whole battle."),
    # ---- Kakita Rensei (Kakita Bushi)
    # Kakita's First Stance: the Kakita academy dojo (M200) teaches it
    ("S746", "K076", R, None, "kata", "Kakita's First Stance", 1.0, 99, [("CRI", 10)], None,
     "Kakita kata. The duelist's stance: +10% criticals for the whole battle."),
    ("S747", "K077", R, 10, "kata", "The Empire Rests on Its Edge", 1.0, 3, [("PATK", 20)], None,
     "The sword over the court: ATK +20% for 3 turns."),
    ("S748", "K078", R, 25, "kata", "Watchful Falcon", 1.0, 3, [("PHIT", 20)], None,
     "Kakita kata. Nothing escapes him: accuracy +20% for 3 turns."),
    ("S749", "K079", R, 30, "kata", "Victory of the Wind", 1.3, 3, [("CRI", 10), ("PATK", -10)], None,
     "Execute stance: x1.3 now, then +10% criticals and -10% ATK for 3 turns."),
    ("S750", "K080", R, 41, "kata", "One Leg Stance", 1.0, 3, [("AGI", 30)], None,
     "Kakita kata. Speed +30% for 3 turns: he leaps ahead in the turn order."),
    ("S751", "K081", R, 51, "kata", "One Strike Blade", 1.8, 1, [("AGI", 30)], None,
     "Kakita kata. Everything in one cut: x1.8, and Speed +30% next turn."),
    ("S752", "K082", R, 61, "kata", "One Truth", 1.0, 99, [("TGR", -80), ("PATK", -15)], None,
     "Kakita kata. Honourable foes hardly target him; his damage -15%. The whole battle."),
    ("S753", "K083", R, 70, "kata", "Standing on the Heavens", 1.0, 3, [("PEVA", 35)], None,
     "The sky does not get hit: +35% evasion for 3 turns."),
    # ---- Kitsuki Gendo (Mirumoto secondary school)
    ("S754", "K084", G, 25, "kata", "Thunder and Steel", 1.0, 3, [("PATK", 20), ("PDEF", 20)], None,
     "Mirumoto kata. Fire in the arm, earth in the feet: ATK and DEF +20% for 3 turns."),
    ("S755", "K085", G, 30, "kata", "The Empire Rests on Its Edge", 1.0, 3, [("PATK", 20)], None,
     "The blade over the investigation: ATK +20% for 3 turns."),
    ("S756", "K086", G, 41, "kata", "My Brother's Soul", 1.0, 3, [("MDEF", 40), ("AGI", -10)], None,
     "Mirumoto kata. Spells slide off: MDEF +40%, Speed -10% for 3 turns."),
    ("S757", "K087", G, 51, "kata", "Time Between Breaths", 1.0, 3, [("PDEF", 15)], [COUNTER(0.5)],
     "Mirumoto kata. Every attack on him may be answered (50% counter) for 3 turns."),
    ("S758", "K088", G, 61, "kata", "Breaking Waves", 1.0, 3, [("PATK", 30)], None,
     "Mirumoto kata. Break the foe's rhythm: ATK +30% for 3 turns."),
    ("S759", "K089", G, 70, "kata", "Victory of the River", 1.0, 99, [("PATK", 25), ("PEVA", -20)], None,
     "The river does not stop: ATK +25%, evasion -20% for the whole battle."),
    # ---- Akodo Shizue (Akodo Bushi)
    ("S760", "K090", S, 5, "kata", "Striking as Water", 1.0, 3, [("PATK", 20), ("PEVA", -10)], None,
     "Damage +20%, evasion -10% for 3 turns."),
    ("S761", "K091", S, 15, "kata", "Striking as Fire", 1.0, 3, [("PHIT", 10), ("CRI", 5), ("AGI", -10)], None,
     "Accuracy +10%, criticals +5%, Speed -10% for 3 turns."),
    ("S762", "K092", S, 41, "kata", "Fury Without End", 1.0, 99, [("PATK", 10)], [RESIST(4, 7, 8)],
     "Akodo kata. Fear, charm and confusion can't touch her; ATK +10%. The whole battle."),
    ("S763", "K093", S, 45, "kata", "The Soul's Roar", 1.0, 3, [("PATK", 35), ("PEVA", -10)], None,
     "Matsu kata. ATK +35%, evasion -10% for 3 turns."),
    ("S764", "K094", S, 51, "kata", "Gentle Blade of Winter", 1.2, 3, [("PATK", 15)], None,
     "Akodo kata. Cold, patient cuts: x1.2 now, ATK +15% for 3 turns."),
    ("S765", "K095", S, 61, "kata", "Matsu's Vengeance", 1.0, 99, [("AGI", 20), ("PATK", 50), ("PEVA", -40)], None,
     "Akodo kata. The glass-cannon capstone: Speed +20%, ATK +50%, evasion -40% for the whole battle."),
    # ---- Shosuro Mitsue (Shosuro Shinobi)
    ("S766", "K096", M, 5, "kata", "Striking as Wind", 1.0, 3, [("AGI", 20), ("PATK", -15)], None,
     "Speed +20%, damage -15% for 3 turns."),
    ("S767", "K097", M, 25, "kata", "The Tail's Reach", 1.0, 3, [("PATK", 20), ("PEVA", -10)], None,
     "Shosuro kata. ATK +20%, evasion -10% for 3 turns."),
    ("S768", "K098", M, 41, "kata", "Cut Under the Mountain", 1.0, 3, [("PEVA", 20), ("AGI", 10)], None,
     "Shosuro kata. Under the big man's swing: evasion +20%, Speed +10% for 3 turns."),
    ("S769", "K099", M, 45, "kata", "Sundering Grace", 0.8, 3, [("PHIT", 15)], None,
     "Bayushi kata. Light cuts that find the gaps: x0.8 now, accuracy +15% for 3 turns."),
    ("S770", "K100", M, 51, "kata", "Blackened Sight", 1.0, 3, [("CEVA", 100), ("PDEF", 20)], None,
     "Shosuro kata. Foes can't land a critical on her; DEF +20% for 3 turns."),
    ("S771", "K101", M, 61, "kata", "Choking Air", 1.0, 99, [("PEVA", 30), ("PATK", -20)], None,
     "Bayushi kata. A second evasion tank: evasion +30%, ATK -20% for the whole battle."),
    # ---- Sayo (the five common Strikings)
    ("S772", "K102", Y, 5, "kata", "Striking as Water", 1.0, 3, [("PATK", 20), ("PEVA", -10)], None,
     "Damage +20%, evasion -10% for 3 turns."),
    ("S773", "K103", Y, 10, "kata", "Striking as Earth", 1.0, 3, [("PEVA", 15), ("PHIT", -10)], None,
     "+15% evasion, -10% accuracy for 3 turns."),
    ("S774", "K104", Y, 15, "kata", "Striking as Fire", 1.0, 3, [("PHIT", 10), ("CRI", 5), ("AGI", -10)], None,
     "Accuracy +10%, criticals +5%, Speed -10% for 3 turns."),
    ("S775", "K105", Y, 20, "kata", "Striking as Wind", 1.0, 3, [("AGI", 20), ("PATK", -15)], None,
     "Speed +20%, damage -15% for 3 turns."),
    ("S776", "K106", Y, 25, "kata", "Striking as Void", 1.0, 3, [("PATK", 15), ("PEVA", 10), ("PHIT", 10),
                                                                  ("AGI", 10)], None,
     "All four elements at once: ATK, evasion, accuracy and Speed up for 3 turns."),
    # ---- Isawa Haruki (shugenja kiho: one per rank and one more)
    ("S777", "K107", H, 8, "kiho", "Self No Self", 1.0, 3, [("MDEF", 20)], None,
     "Void kiho. A staff tap, and the self empties: +2 VP, MDEF +20% for 3 turns."),
    ("S778", "K108", H, 14, "kiho", "Heart of Stone", 1.0, 3, [("PDEF", 30), ("MDEF", 30)], None,
     "Earth kiho. DEF and MDEF +30% for 3 turns."),
    ("S779", "K109", H, 20, "kiho", "Ebb and Flow", 1.0, 3, [("PEVA", 10)], [COUNTER(0.4)],
     "Water kiho. Each attack on him may be answered (40% counter) for 3 turns."),
    ("S780", "K110", H, 30, "kiho", "Parting the Waves", 1.0, 99, [("PDEF", 25), ("MDEF", 25), ("MATK", -15)], None,
     "Water kiho. The tide parts around him: DEF and MDEF +25%, his spells -15%. The whole battle."),
    ("S781", "K111", H, 42, "kiho", "Touch the Void Dragon", 1.0, 3, [("MATK", 30)], None,
     "Void kiho. The land's element answers: spells +30% for 3 turns."),
    ("S782", "K112", H, 54, "kiho", "Grasp the Earth Dragon", 1.0, 99, [("PDEF", 20)], [AUTOREVIVE],
     "Earth kiho. The earth holds him up: once he falls to a quarter HP he is braced to survive. The whole battle."),
    # ---- Togashi Yosai (monk: the most kiho)
    ("S783", "K113", YO, 1, "kiho", "Fire Fist", 1.2, 3, [("PATK", 20)], None,
     "Martial kiho. A burning blow: x1.2, ATK +20% for 3 turns."),
    ("S784", "K114", YO, 5, "kiho", "Water Fist", 1.0, 3, [("PEVA", 20)], None,
     "Martial kiho. Flow around the blade: evasion +20% for 3 turns."),
    ("S785", "K115", YO, 10, "kiho", "Earth Fist", 1.0, 3, [("PDEF", 40)], None,
     "Martial kiho. Root like the mountain: DEF +40% for 3 turns."),
    ("S786", "K116", YO, 15, "kiho", "Air Fist", 1.0, 3, [("AGI", 30)], None,
     "Martial kiho. Speed +30% for 3 turns."),
    ("S787", "K117", YO, 20, "kiho", "Falling Star Strike", 1.4, 2, [("CRI", 20)], None,
     "Martial kiho. A blow from above: x1.4, criticals +20% for 2 turns."),
    ("S788", "K118", YO, 28, "kiho", "Kharmic Strike", 1.0, 3, [("PDEF", 10)], [COUNTER(0.7)],
     "Kharmic kiho. What is done to him returns (70% counter) for 3 turns."),
    ("S789", "K119", YO, 35, "kiho", "Freezing the Lifeblood", 1.0, 2, [("PHIT", 20)], None,
     "Atemi kiho. A finger on the nerve: the foe may freeze (Paralysis); accuracy +20% for 2 turns."),
    ("S790", "K120", YO, 45, "kiho", "Void Fist", 1.3, 3, [("MDEF", 20)], None,
     "Martial kiho. x1.3, +1 VP, MDEF +20% for 3 turns."),
    # Togashi tattoos at the school levels (R2-R5)
    ("S791", "K121", YO, 15, "tattoo", "Tiger Tattoo", 1.5, 3, [("PATK", 30)], None,
     "The tiger wakes on his back: x1.5, ATK +30% for 3 turns."),
    ("S792", "K122", YO, 30, "tattoo", "Raven Tattoo", 1.0, 3, [("PEVA", 30), ("AGI", 15)], None,
     "The raven lifts him out of the blow: evasion +30%, Speed +15% for 3 turns."),
    ("S793", "K123", YO, 45, "tattoo", "Centipede Tattoo", 1.0, 99, [("AGI", 50)], None,
     "A hundred legs: Speed +50% for the whole battle."),
    ("S794", "K124", YO, 60, "tattoo", "Phoenix Tattoo", 1.0, 99, [("PATK", 20), ("MATK", 20)], [AUTOREVIVE],
     "The phoenix rises: ATK and spells +20%, and he comes back once from the brink. The whole battle."),
]

# Specials the plugin handles by name (RokuganRanks.sk): Self No Self +2 VP, Void Fist +1 VP, Freezing the Lifeblood
# 50% Paralysis (K006) on the target.

# Dojo rewards (user: "change the dojo to give out a Kata appropriate to crab clan like Earth instead of school rank").
DOJO_KATA = {"natsuko_hida_dojo M164 (G1224)": "S740", "rensei_kakita_academy M200 (G1225)": "S746"}


def cond_for(entry, template):
    """A stance condition from a template cond (deep-copied by the caller)."""
    sid, cid, pid, lv, kind, name, mult, turns, mods, extra, desc = entry
    t = dict(template)
    opts = []
    for prop, val in mods:
        opts.append({"LV": 1, "opttype": "opt_status", "propid": prop, "val": val,
                     "valtype": "totalrate" if prop in RATE else "supply"})
    for e in extra or []:
        opts.append(dict(e, LV=1))
    n = turns if turns >= 99 else turns + 1     # put before the strike: the current turn counts (Hasten the Blade: 2)
    t.update({"name": name, "desc": desc, "option": opts, "MAXLV": 1, "rem_turn": [n, n],
              "rem_battle": True, "rem_die": True, "revcondid": None, "showpop": True, "showstat": True,
              "rt_kata": True})
    return t


def level_options(pid):
    return [{"LV": lv, "opttype": "opt_getskill", "skillid": sid} for sid, _c, p, lv, *_ in KATA
            if p == pid and lv is not None]
