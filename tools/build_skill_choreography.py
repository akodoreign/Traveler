"""Inventory the installed combat metadata for the 3D choreography design."""
import argparse
from collections import defaultdict
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHOOLS = {
    "hiruma": ("yari_leap", "cold wind and a low scout's crouch"),
    "kakita": ("kakita_pass", "one clean cut, turn, optional brim touch"),
    "kitsuki": ("study", "glasses catch the light, evidence markers resolve one by one"),
    "akodo": ("formation", "planted command gesture, staggered Lion standards"),
    "isawa": ("spell", "small finger counters converge into a five-element seal"),
    "shosuro": ("shadow", "a layered shadow conceals the first step, not the impact"),
    "ide": ("accord", "open hands, a measured breath, gold ripples"),
    "ronin": ("remedy", "low center of gravity, a hand-ground medicine pouch"),
    "hida": ("club_swing", "delayed, full-body tetsubo turn, dust and shock ring"),
    "matsu": ("line_charge", "shoulders drive a committed charge, rust-gold afterimage"),
    "shiba_yojimbo": ("ward", "catch into a planted cross-guard, ember ward"),
    "seppun": ("ward", "tall guard with ivory edge light, little recoil"),
    "yoritomo": ("storm", "low shoulder-led sweep with a close spray"),
    "shinjo": ("mounted_pass", "passing draw or shot, trail of dust"),
    "doji": ("kanji_cut", "brief blade-written Justice, then a diagonal closure cut"),
    "tamori": ("spell", "grounded invocation with coarse earth fragments"),
    "togashi": ("tattoo_dragon", "inking wake, a rising Eastern dragon, a full-screen fire sweep"),
}
TRAVELERS = {
    "hiruma": ("P100", "Low and alert. Gaze scans first, hips compress, and feet land fast and quiet.",
               "Razor's Edge, scout reads, yari leaps, and Earth stances. Map and satchel are useful props."),
    "kakita": ("P101", "Reserved and upright at rest. Small hand motions prepare an abrupt decisive release.",
               "Focus, draw, hat-brim finish, and one narrow Void line. Hold the clean cut for a beat."),
    "kitsuki": ("P102", "Curiosity arrives as a small head turn. Confirm with glasses, a page or one pointed finger.",
                "Deduce and Interrogate share a read. Use disciplined wrists and stance changes in Mirumoto actions."),
    "akodo": ("P103", "Level gaze and proud chest. Command from the feet up, with firm shoulders and a short signal.",
              "Stagger the formation standards from her hand, and resolve a charge with a grounded forward finish."),
    "isawa": ("P104", "Pause to count fingers and check the count. Attention sharpens on release.",
              "Use both hands for counted spell beats. Keep Water smooth, Earth weighty, Fire abrupt and Void quiet."),
    "shosuro": ("P105", "Make the first gesture a feint. Reveal the real hand and gaze only when the effect lands.",
                "Misdirection, powder, outfit-specific sleeve use, and the knife return read like stagecraft."),
    "ide": ("P106", "Warm eye line and generous open hands. Take time to breathe and include the party.",
            "The Heart Listens opens both arms into a rising drawn heart. S543 is a separate showy vocal performance."),
    "ronin": ("P107", "Grounded and pragmatic. Work with compact hands and follow through like someone used to weather.",
              "A pouch ties herbs and dressing together. Pilfer is swift and modest. Return notice to the fight."),
}
SKILL_OVERRIDES = {
    "S110": "evade_guard", "S120": "sheathed_focus", "S121": "kakita_pass",
    "S140": "short_lunge", "S141": "powder", "S142": "thrown",
    "S460": "tattoo_breath", "S461": "tattoo_heal",
    "S542": "accord", "S543": "virtuoso_song", "S544": "remedy", "S545": "study",
    "S566": "accord", "S580": "steal", "S581": "accord", "S583": "remedy",
    "S584": "powder", "S592": "thrown", "S608": "line_charge",
    "S609": "remedy", "S638": "accord", "S724": "heart_listens",
}
WEAPON_TRACKS = (
    (0, "blade_cut"), (1, "yari_thrust"), (2, "short_lunge"),
    (3, "club_swing"), (4, "draw_shot"), (5, "staff_sweep"), (12, "unarmed"),
)
ELEMENTS = {6: "fire", 7: "water", 8: "air", 9: "earth", 10: "void", 11: "jade", 13: "crystal"}


def by_skill(sid, entry):
    if sid in SKILL_OVERRIDES:
        return SKILL_OVERRIDES[sid]
    if entry.get("rt_passive"):
        return "passive"
    if entry.get("rt_dragonbreath"):
        return "tattoo_breath"
    if entry.get("rt_kata"):
        return "kata_stance" if entry.get("rt_knostrike") else "kiho_or_kata"
    if entry.get("rt_hire") is not None or entry.get("rt_guest"):
        return "guest"
    if entry.get("rt_voice"):
        return "accord"
    if entry.get("rt_diag"):
        return "remedy"
    if entry.get("rt_selfburn") and entry.get("skilltype") == "heal":
        return "tattoo_heal"

    action = entry.get("skilltype")
    if action in {"heal", "buff", "debuff"}:
        return {"heal": "healing_cast", "buff": "ward", "debuff": "control_cast"}[action]
    if action == "macro":
        return "scripted"
    if action != "attack":
        return "system"
    bits = entry.get("elembits") or 0
    attack = entry.get("atkact") or {}
    if attack.get("id") == "atk_normal":
        for bit, route in WEAPON_TRACKS:
            if bits & (1 << bit):
                return route
    if any(bits & (1 << bit) for bit in ELEMENTS):
        return "spell"
    if attack.get("id") == "noop":
        return "control_cast"
    return "weapon_family"


def read(source):
    return json.loads(source.read_text(encoding="utf-8-sig"))


def build(data):
    players = read(data / "player.json")
    skill_table = read(data / "skill.json")
    school_players = defaultdict(list)
    learned_by = defaultdict(set)
    for pid, entry in players.items():
        if not isinstance(entry, dict):
            continue
        school = entry.get("rt_school_key")
        if school:
            school_players[school].append(pid)
            for option in entry.get("lvoption", []):
                sid = option.get("skillid")
                if sid:
                    learned_by[sid].add(school)
    unknown = set(school_players) - set(SCHOOLS)
    if unknown:
        raise ValueError(f"Schools missing choreography designs: {', '.join(sorted(unknown))}")
    schools = {key: {"actors": school_players[key], "signature": route, "staging": styling}
               for key, (route, styling) in SCHOOLS.items()}
    for key, (actor, performance, skill_cluster) in TRAVELERS.items():
        schools[key]["traveler"] = {"actor": actor, "performance": performance, "skill_cluster": skill_cluster}
    skills = {}
    for sid, entry in sorted(skill_table.items()):
        if not isinstance(entry, dict) or not entry.get("name"):
            continue
        route = by_skill(sid, entry)
        bits = entry.get("elembits") or 0
        skills[sid] = {"name": entry["name"], "type": entry.get("skilltype"),
                       "route": route, "elements": [name for bit, name in ELEMENTS.items() if bits & (1 << bit)],
                       "school_unlocks": sorted(learned_by[sid]), "equip_or_list": bool(entry.get("addlist"))}
    return {"schools": schools, "skills": skills}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    data = args.repo / "_tools/rpgcobo-tool/project/data"
    out = args.out or args.repo / "_art/sources/human3d/skill-choreography.json"
    out.write_text(json.dumps(build(data), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
