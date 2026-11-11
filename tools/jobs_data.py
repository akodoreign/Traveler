"""Jobs and traits (docs/rules/progression-v2.md section 3; user 2026-11-11: Traveler "should go from 0-50% extra exp
and money. Then there should be a Job for each of them as well like scout ... Each char should have at least one
other job they can swap out to, and then you can have it pop up those traits as you level them as well so they can
be swapped out"). The user approved the per-traveler list.

Slot 1 "Job": Traveler (J000) or the traveler's own job (J010-J017). Slot 2 "Trait": traits unlocked at that job's
levels 2 / 5 / 8 (the plugin RokuganJobs.sk adds them to the traveler's jobs; they stay once learned). Effects are in
RokuganJobs.sk, except the plain stat / resistance ones, which are job options here.
"""

JOB_CURVE = [8, 15]            # engine getExpByLV: ~JLv 10 after a chapter or two at 2 job EXP a foe
ENEMY_JXP = 2

RESIST = lambda pct, *bits: dict({"opttype": "opt_conddef"}, **{"CDR.%d" % b: pct for b in bits})  # noqa: E731
STAT = lambda prop, val, kind="totalrate": {"opttype": "opt_status", "propid": prop, "val": val,   # noqa: E731
                                            "valtype": kind}

# (job id, player id, name, desc, [trait ids at JLv 2, 5, 8])
JOBS = [
    ("J010", "P100", "Scout", "Hiruma scout craft: ambushes, quiet roads, reading tracks.", ["J110", "J111", "J112"]),
    ("J011", "P101", "Duelist", "The iaijutsu duelist: first draw, the measure, the ready blade.", ["J113", "J114", "J115"]),
    ("J012", "P102", "Magistrate", "Evidence over testimony - and a bounty for the guilty.", ["J116", "J117", "J118"]),
    ("J013", "P103", "Tactician", "The go player's war: the vanguard, the rally, the banner.", ["J119", "J120", "J121"]),
    ("J014", "P104", "Scholar", "Scrolls, meditation and wards.", ["J122", "J123", "J124"]),
    ("J015", "P105", "Shinobi", "Quiet feet, light fingers, the knife from behind.", ["J111", "J103", "J126"]),
    ("J016", "P106", "Merchant", "The Ide trade: haggling, the purse and friends everywhere.", ["J127", "J128", "J129"]),
    ("J017", "P107", "Herbalist", "The wave-woman's road craft: forage, brew, and always a way out.", ["J130", "J131", "J132"]),
]

# (trait id, name, desc, data options)
TRAITS = [
    ("J110", "Surprise Round", "Scout trait. A chance to catch random foes unaware: they lose their first action. "
     "From Scout Lv 5, criticals up against foes that haven't acted yet.", []),
    ("J111", "Sneak", "Trait. Quiet feet: fewer random encounters (half as many).", []),
    ("J112", "Tracker", "Scout trait. Read the tracks: every foe's weaknesses are known at the start of a battle.", []),
    ("J113", "First Draw", "Duelist trait. In the first turn of a battle, Speed is doubled.", []),
    ("J114", "Measure the Foe", "Duelist trait. +20% critical hits against a lone foe.", []),
    ("J115", "Ready Blade", "Duelist trait. Iaijutsu starts every battle with 1 Focus.", []),
    ("J116", "Read the Foe", "Magistrate trait. At the start of a battle, one foe's weaknesses are known.", []),
    ("J117", "Honest Eyes", "Magistrate trait. Resists charm and confusion.", [RESIST(100, 4, 8)]),
    ("J118", "Bounty", "Magistrate trait. +20% money from battles.", []),
    ("J119", "Vanguard", "Tactician trait. The whole party moves faster in the first turn.", []),
    ("J120", "Rally", "Tactician trait. +1 VP at the start of every battle.", []),
    ("J121", "Banner", "Tactician trait. While she is under half HP, the party hits 15% harder.", []),
    ("J122", "Learned", "Scholar trait. Max SP +20%.", [STAT("MAXMP", 20)]),
    ("J123", "Meditation", "Scholar trait. Recovers 5% of max SP every turn.", []),
    ("J124", "Ward", "Scholar trait. Resists poison, blindness, silence and sleep (50%).", [RESIST(50, 1, 2, 3, 5)]),
    ("J126", "Ambush", "Shinobi trait. A chance to catch random foes unaware; her criticals are up against foes "
     "that haven't acted yet.", []),
    ("J127", "Haggle", "Merchant trait. Shop prices -10%.", []),
    ("J128", "Golden Purse", "Merchant trait. +30% money from battles.", []),
    ("J129", "Connections", "Merchant trait. The first hireling call each battle costs no charge.", []),
    ("J130", "Forager", "Herbalist trait. After a battle, a chance to find a Healing Herb.", []),
    ("J131", "Strong Brew", "Herbalist trait. Her healing is 25% stronger.", []),
    ("J132", "Wave-woman", "Herbalist trait. Escape always works.", []),
]
TRAIT_LEVELS = (2, 5, 8)


def build(jobs, template_job, template_trait):
    """Add / update job.json entries. template_*: deep copies of J000 / J105 (the caller copies)."""
    import copy
    t = jobs["J000"]
    t.update({"MAXLV": 10, "expcurv": list(JOB_CURVE), "desc": "A traveler on the roads of Rokugan. Extra EXP and money "
              "from battles: +0% at job Lv 1, rising to +50% at Lv 10.", "lvoption": []})
    for jid, pid, name, desc, traits in JOBS:
        j = copy.deepcopy(template_job)
        j.update({"name": name, "desc": desc + " Traits at job Lv 2, 5 and 8.", "MAXLV": 10, "expcurv": list(JOB_CURVE),
                  "jobflag": -1, "jobslotbits": 1, "option": [], "learn": [],
                  "lvoption": [{"LV": lv, "opttype": "opt_getjob", "jobid": tid} for lv, tid in zip(TRAIT_LEVELS, traits)],
                  "rt_owner": pid})
        jobs[jid] = j
    for tid, name, desc, opts in TRAITS:
        j = copy.deepcopy(template_trait)
        j.update({"name": name, "desc": desc, "MAXLV": 1, "jobflag": -1, "jobslotbits": 2, "lvoption": [],
                  "option": [dict(o) for o in opts]})
        jobs[tid] = j
