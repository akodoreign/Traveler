"""Jobs and traits (docs/rules/progression-v2.md section 3).

User 2026-11-11: Traveler "should go from 0-50% extra exp and money. Then there should be a Job for each of them as
well like scout ... Each char should have at least one other job they can swap out to, and then you can have it pop
up those traits as you level them". User 2026-11-12: Traveler "+1% exp 1% gold (for level 1 traveler)"; "the extra
traits, should be one for each of the jobs"; Ishiken-do for the shugenja "full void at its max level and 1 ... at its
beginning level (make this a Equip able trait at max level, all should do similar) ... once they are all together
they can each level up the different jobs to get the different traits so they can mix and match a job and a trait".

So:
- Slot 1 "Job": Traveler (J000) or a personal job (J010-J017). While a job is worn, its perks work, unlocking at job
  Lv 1 / 4 / 7 (the perk ids below; plugin RokuganJobs.sk hasPerk).
- At job Lv 10 the job's ONE signature trait is learned: it can be worn in slot 2 "Trait" with any job.
- Travelers in the party together can take each other's jobs (RokuganJobs.sk ensureJobs).
"""

JOB_CURVE = [8, 15]            # engine getExpByLV: ~JLv 10 after a chapter or two at 2 job EXP a foe
ENEMY_JXP = 2
PERK_LEVELS = (1, 4, 7)
TRAIT_LEVEL = 10

RESIST = lambda pct, *bits: dict({"opttype": "opt_conddef"}, **{"CDR.%d" % b: pct for b in bits})  # noqa: E731
STAT = lambda prop, val, kind="totalrate": {"opttype": "opt_status", "propid": prop, "val": val,   # noqa: E731
                                            "valtype": kind}

# perk / trait id -> (name, description, data options that apply while it is in effect)
PERKS = {
    "J110": ("Surprise Round", "A chance to catch random foes unaware: they lose their first action; criticals up "
             "against foes that haven't acted yet.", []),
    "J111": ("Sneak", "Quiet feet: half as many random encounters.", []),
    "J112": ("Tracker", "Every foe's weaknesses are known at the start of a battle.", []),
    "J113": ("First Draw", "Speed up in the first turn of a battle.", []),
    "J114": ("Measure the Foe", "+20% critical hits against a lone foe.", []),
    "J115": ("Ready Blade", "Iaijutsu starts every battle with 1 Focus.", []),
    "J116": ("Read the Foe", "One foe's weaknesses are known at the start of a battle.", []),
    "J117": ("Honest Eyes", "Resists charm and confusion.", [RESIST(100, 4, 8)]),
    "J118": ("Bounty", "+20% money from battles.", []),
    "J119": ("Vanguard", "The whole party moves faster in the first turn.", []),
    "J120": ("Rally", "+1 VP at the start of every battle.", []),
    "J121": ("Banner", "While its wearer is under half HP, the party hits 15% harder.", []),
    "J122": ("Learned", "Max MP +20%.", [STAT("MAXMP", 20)]),
    "J124": ("Ward", "Resists poison, blindness, silence and sleep (50%).", [RESIST(50, 1, 2, 3, 5)]),
    "J133": ("Ishiken-do", "The Void answers at once: every battle starts with full VP.", []),
    "J103": ("Light Fingers", "Steals succeed more often.", None),           # (template trait: keeps its own options)
    "J126": ("Ambush", "A chance to catch random foes unaware; criticals up against foes that haven't acted yet.", []),
    "J127": ("Haggle", "Shop prices -10%.", []),
    "J128": ("Golden Purse", "+30% money from battles.", []),
    "J129": ("Connections", "The first hireling call each battle costs no charge.", []),
    "J130": ("Forager", "After a battle, a chance to find a Healing Herb.", []),
    "J131": ("Strong Brew", "Healing 25% stronger.", []),
    "J132": ("Wave-woman", "Escape always works.", []),
    "J134": ("Seasoned Traveler", "+25% EXP and money from battles.", []),
}

# (job id, owner, name, description, [perks at Lv 1, 4, 7], signature trait at Lv 10)
JOBS = [
    ("J010", "P100", "Scout", "Hiruma scout craft: ambushes, quiet roads, reading tracks.", ["J110", "J111", "J112"],
     "J110"),
    ("J011", "P101", "Duelist", "The iaijutsu duelist: the first draw, the measure, the ready blade.",
     ["J113", "J114", "J115"], "J114"),
    ("J012", "P102", "Magistrate", "Evidence over testimony - and a bounty for the guilty.", ["J116", "J117", "J118"],
     "J116"),
    ("J013", "P103", "Tactician", "The go player's war: the vanguard, the rally, the banner.", ["J119", "J120", "J121"],
     "J120"),
    ("J014", "P104", "Ishiken-do", "The Void shugenja's art. Battles start with 1 VP at job Lv 1, rising to full VP "
     "at Lv 10.", ["J124", "J122", "J120"], "J133"),
    ("J015", "P105", "Shinobi", "Quiet feet, light fingers, the knife from behind.", ["J111", "J103", "J126"], "J126"),
    ("J016", "P106", "Merchant", "The Ide trade: haggling, the purse, friends everywhere.", ["J127", "J128", "J129"],
     "J128"),
    ("J017", "P107", "Herbalist", "The wave-woman's road craft: forage, brew, always a way out.", ["J130", "J131",
                                                                                                    "J132"], "J132"),
]
TRAVELER_TRAIT = "J134"


def traveler_pct(lv):
    """Traveler's EXP and money bonus: +1% at job Lv 1 to +50% at Lv 10 (user)."""
    return 0 if lv < 1 else int(round(1 + (min(lv, 10) - 1) * 49 / 9.0))


def _perk_line(tid, lv):
    return "Lv %d %s: %s" % (lv, PERKS[tid][0], PERKS[tid][1])


def build(jobs, template_job, template_trait):
    """Add / update job.json entries. template_*: deep copies of J000 / J105 (the caller copies)."""
    import copy
    t = jobs["J000"]
    t.update({"MAXLV": 10, "expcurv": list(JOB_CURVE), "option": [], "lvoption": [
        {"LV": TRAIT_LEVEL, "opttype": "opt_getjob", "jobid": TRAVELER_TRAIT}],
        "desc": "A traveler on the roads of Rokugan. EXP and money from battles +%d%% at job Lv 1, rising to +%d%% "
                "at Lv 10. Lv 10 trait: Seasoned Traveler." % (traveler_pct(1), traveler_pct(10))})
    for jid, pid, name, desc, perks, sig in JOBS:
        j = copy.deepcopy(template_job)
        lvo = [{"LV": TRAIT_LEVEL, "opttype": "opt_getjob", "jobid": sig}]
        for lv, tid in zip(PERK_LEVELS, perks):                 # data-option perks apply while the job is worn
            for o in PERKS[tid][2] or []:
                lvo.append(dict(o, LV=lv))
        j.update({"name": name, "MAXLV": 10, "expcurv": list(JOB_CURVE), "jobflag": -1, "jobslotbits": 1,
                  "option": [], "learn": [], "lvoption": lvo, "rt_owner": pid,
                  "rt_perks": [[tid, lv] for lv, tid in zip(PERK_LEVELS, perks)],
                  "desc": desc + " " + " ".join(_perk_line(t_, lv) for lv, t_ in zip(PERK_LEVELS, perks)) +
                  " Lv 10 trait: %s." % PERKS[sig][0]})
        jobs[jid] = j
    for tid, (name, desc, opts) in PERKS.items():
        if opts is None:                                        # a template trait (J103): name only
            jobs[tid]["name"] = name
            continue
        j = copy.deepcopy(template_trait)
        j.update({"name": name, "desc": "Trait. " + desc, "MAXLV": 1, "jobflag": -1, "jobslotbits": 2,
                  "lvoption": [], "option": [dict(o) for o in opts]})
        jobs[tid] = j
