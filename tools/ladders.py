"""Levelling ladders between chapters (user 2026-11-11: "anywhere that there is a spread of levels that needs to be
obtained, feel free to re use dungeons for various leveling and sub plot missions"; tools/level_gaps.py found every
path's Ch1 foes top out ~Lv 6 while Ch2 recommends 18-20).

Once a chapter's completion flag is set, its own encounter maps (in story order) get new groups: the same foe types
re-levelled (clones, gen_data) spread over [lo, hi] - each map's groups span its range, so one map can hold a whole
ladder. The chapter's old groups switch off then (rt_ifnot), unless they are already gated by another flag.
gen_maps.apply_ladders() rewrites ENCOUNTERS and writes _ladder_foes.json {new id: [base id, level]}; gen_data
creates those clones (scaled from the base foe's final stats). The Crab Egg Caves have their own hand-made ladder
(gen_data E608-E618, G049).
"""

LADDERS = [
    # (path, done flag, [(map, lo, hi), ...]) - Ch1 -> Ch2 (recommended ~18-20)
    ("Crab", "G054", [("M102", 6, 9)]),                                           # + the Egg Caves (G049, 8-15)
    ("Crane", "G321", [("M201", 8, 11), ("M203", 11, 15), ("M204", 14, 18)]),
    ("Lion", "G486", [("M250", 8, 18)]),
    ("Phoenix", "G462", [("M251", 8, 12), ("M278", 12, 15), ("M279", 15, 18)]),
    ("Dragon", "G727", [("M309", 8, 10), ("M310", 10, 13), ("M311", 13, 15), ("M312", 15, 18)]),
    ("Scorpion", "G861", [("M348", 8, 10), ("M350", 10, 12), ("M356", 13, 15), ("M357", 15, 18)]),
    ("Unicorn", "G982", [("M390", 8, 12), ("M397", 13, 18)]),
    ("Ronin", "G1055", [("M419", 8, 12), ("M420", 13, 18)]),
    # Ch2 -> Ch3 (recommended ~25-30)
    ("Crab", "G216", [("M140", 22, 24), ("M148", 23, 25), ("M149", 24, 27)]),
    ("Crane", "G362", [("M212", 24, 26), ("M214", 25, 27), ("M216", 26, 29)]),
    ("Lion", "G510", [("M254", 23, 26), ("M261", 26, 29)]),
    ("Phoenix", "G630", [("M283", 23, 26), ("M284", 26, 29)]),
    ("Dragon", "G752", [("M318", 23, 26), ("M319", 26, 29)]),
    ("Scorpion", "G909", [("M359", 22, 24), ("M361", 24, 26), ("M365", 26, 28), ("M366", 27, 29)]),
    ("Ronin", "G1078", [("M422", 23, 25), ("M425", 25, 27), ("M428", 27, 29)]),
    # Ch3 -> Ch4 (recommended ~34-41)
    # (tester: the Shadowlands M171-M176 and M152 can't be reached after their chapters -> the Hida road and the
    # Kyuden Hida cells / catacombs carry the Crab ladders, stacked: Ch2 22-27, Ch3 28-34, Ch4 40-50)
    ("Crab", "G255", [("M140", 28, 30), ("M148", 30, 32), ("M149", 32, 34)]),
    ("Crane", "G403", [("M222", 34, 36), ("M225", 36, 38), ("M226", 38, 40)]),
    ("Lion", "G537", [("M266", 32, 35), ("M269", 35, 38), ("M270", 38, 40)]),
    ("Phoenix", "G673", [("M289", 33, 35), ("M291", 35, 37), ("M292", 36, 38), ("M293", 38, 40)]),
    ("Dragon", "G784", [("M333", 33, 35), ("M334", 35, 38), ("M335", 38, 40)]),
    ("Scorpion", "G936", [("M368", 34, 36), ("M374", 36, 38), ("M377", 38, 40)]),     # (shared with Unicorn Ch2)
    # (tester: the Shiro Iuchi tower M400/M401 closes after Ch3 - the ladder stays on the reachable maps)
    ("Unicorn", "G1010", [("M399", 34, 36), ("M405", 36, 38), ("M406", 38, 40)]),
    ("Ronin", "G1116", [("M429", 35, 36), ("M431", 36, 37), ("M432", 37, 38), ("M433", 38, 39), ("M434", 39, 40),
                        ("M435", 39, 40)]),
    # Ch4 -> the finale (recommended ~52)
    ("Crab", "G286", [("M140", 40, 50)]),                    # (M148/M149 are winter-only: gone after Ch4)
    ("Ronin", "G1154", [("M437", 44, 50)]),                  # (tester: "The Oracle's Choice" sets G1154)
    ("Crane", "G434", [("M231", 44, 46), ("M232", 46, 48), ("M233", 48, 50)]),
    ("Lion", "G573", [("M272", 44, 50)]),
    ("Phoenix", "G698", [("M298", 44, 47), ("M299", 47, 50)]),
    ("Scorpion", "G962", [("M380", 44, 46), ("M382", 46, 48), ("M384", 47, 49), ("M385", 48, 50)]),
    ("Unicorn", "G1031", [("M409", 44, 47), ("M410", 47, 50)]),
]

FIRST_ID = 619           # clones E619+ (after the Egg Caves foes E608-E618; deterministic: sorted (base, level)
                         # pairs). The engine's data ids are 3 digits: keep the last one under E1000.
