"""Dialogue clean-up pass (user, 2026-11-09: "go through the text dialog for whole game, make sure it makes sense").
Runs at the end of tools/regen.py, after apply_bust_emotions.py, on project/data/map.json. It is a post-pass on purpose:
the lines come from two places (tools/gen_maps.py and the scripts in docs/story/production/*.md), and one table here
is easier to read and to check than fifty scattered edits. Every fix prints how many lines it changed; a fix that no
longer matches anything is listed as STALE (the source text changed: update or delete the entry).
  python -E tools/apply_dialog_fixes.py            apply
  python -E tools/apply_dialog_fixes.py --check    report only, write nothing
Reading copies of the whole script (branches, flags, busts): _art/preview/agents/dialog/ (see NOTES.md)."""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "data"))

# ("sub", where, old fragment, new fragment)       where = None | "M123" | "M123/#4#" | ("M1", "M2")
# ("name", where, old speaker, new speaker[, text fragment])
# ("del", where, exact text)
# ("before" | "after", where, anchor text fragment, [(speaker, text[, emo]), ...])
# ("set", where, exact text, {"name":..., "text":..., "emo":...})
# ("page", "M143/#3#", [reqs], [(speaker, text[, emo]), ...])      a new last page on that event
PAST = ("M325", "M326", "M337")                                    # the year 400: nobody may say "Kitsuki"
FIXES = [
    # ---- leaked stage directions and notes
    ("sub", "M148", " rat-way shortcut through donjon_1) [END]", ""),
    ("sub", "M148", "Filed. Just like the Crab said.", "Filed. Somebody came down here with a rasp."),   # true with or without the veteran's tip
    ("sub", "M174", "A clean stroke, off-screen. She", "A clean stroke. She"),
    ("del", "M174", "(Natsuko leaves his patrol report under a stone.)"),
    ("sub", "M133", "The party turns to leave. Seppun Ryozo, bleeding, crawls into a side tunnel. The camera stays behind.",
     "Natsuko turns to leave. Seppun Ryozo, bleeding, crawls into a side tunnel, and nobody sees him go."),
    ("sub", "M257", "The camera slides past the great names and stops at the last cushion: Akodo Shizue.",
     "Past all the great names, on the very last cushion: Akodo Shizue."),
    ("sub", "M306", "Quick cuts: Kitsuki Gendo shouting for a healer; Kosai \"can't find one\"; Gendo's hands steady as he sniffs the tea.",
     "Gendo shouts for a healer. Kosai \"can't find one\". Gendo's hands are steady as he sniffs the tea."),
    ("sub", "M317", "Training montage. Kitsuki Gendo drops", "An afternoon of it. Kitsuki Gendo drops"),
    ("sub", "M342", "The scene shimmers.", "The room shimmers."),
    ("sub", "M377", "Not this chapter. Not without", "Not today. Not without"),
    ("sub", "M445", "The post-game regions - the Shadowlands deep, Hiruma Castle, Lv 61-80 - aren't built yet.",
     "Two more roads open from the shrine gate: the deep Shadowlands, and a storm off the Crane coast."),
    ("sub", "M220", "Ship'S Master", "ship's master"),
    # ---- lines that answered nothing, or contradicted the scene
    ("sub", "M101/#8#", "Hiruma. Not today. Come back when the court's done with you.",
     "Hiruma. Not today. The Wall will still be here when you get back."),
    ("sub", "M101/#13#", "Back from the Shadowlands and still in one piece. Mostly.",
     "Still in one piece, Natsuko? Mostly? Good. Keep it that way."),
    ("before", "M101/#12#", "Keep it.", [("", "Inside the gate, Kage holds the map case out to Natsuko. Then he draws it back.")]),
    ("page", "M143/#3#", [{"lvar": "G210", "op": "==", "rvar": True}], [
        ("Isawa Mutsuye", "...I didn't do this, Hiruma-san. I don't even know what it is on my skin."),
        ("Hiruma Natsuko", "I know. Somebody threw it at you. I mean to find out who.", "worried")]),
    ("before", "M205/#10#", "Take them. You'll need them more", [("", "The village granary. Imuro has left the lid off a crate of rice balls.")]),
    ("sub", "M207", "Certainty is worse.", "It says Heaven decides. My father thinks Heaven sounds like him. Certainty is worse than cruelty, Kakita-san."),
    ("sub", ("M208", "M209"), "Kakita Morishu dies. Sariko's cry carries across the yard.",
     "Kakita Morishu dies before the sun is up. In the village, Sariko's cry carries a long way."),
    ("sub", ("M208", "M209"), "- and stood beside him.", "- and had to decide what kind of Crane to be."),
    ("sub", ("M208", "M209"), "Kitsuki Seigen and Matsu Kiku go their own ways. (Their side stories come later.)",
     "Kitsuki Seigen and Matsu Kiku take their leave for now. (Either will answer the Guest call again when you find them on the road.)"),
    ("before", "M210", "My father's. A copy of one corner.", [("", "She presses a folded scrap of oiled paper into his hand.")]),
    ("before", "M210", "For the scalding sake.", [("", "He hands her a small porcelain cup, wrapped in white silk.")]),
    ("sub", "M229", "refused his father, and drew first blood - and found", "faced his father on the white sand - and found"),
    ("sub", "M248/#4#", "He's impatient now. He'll do something tonight.", "He's here. In this room. The dead have stopped whispering."),
    ("sub", "M252", "guard. I challenge you. First blood.", "Shiba-san. I challenge you. First blood."),
    ("sub", "M259", "My wedding is in eleven weeks.", "My wedding is before the thaw."),
    ("before", "M260", "...It's lying. It won't come back.", [
        ("", "The oni squeals - \"I will return! I will devour your souls!\" - and is gone through the floor.")]),
    ("del", "M285", "Night falls over the treaty city."),
    ("set", "M289", "Every hour he stays, it spreads further. I'm sorry. I'm so sorry.",
     {"name": "Isawa Haruki", "text": "Every hour I stay, it spreads further. I'm sorry. I'm so sorry.", "emo": "worried"}),
    ("before", "M290", "It won't cure this. Nothing cures this.", [
        ("", "On the last mat, a healer with dark veins to her jaw presses a scroll into Haruki's hands.")]),
    ("sub", "M317", "That's the second time someone's said that to me in a way that sounded like praise.",
     "I'll file that under praise. Nobody will check."),
    ("del", "M326", "You're asking after Seppun Ushimo? ..."),
    ("sub", "M326", "Ushimo? He lives by the south gate", "Seppun Ushimo? He lives by the south gate"),
    ("sub", PAST, "Coin first, Kitsuki-sama.", "Coin first, sir."),
    ("sub", "M328", "Three thousand, magistrate.", "Three thousand, stranger."),
    ("before", "M344", "The son will become the dark brother.", [("", "Later, alone, Gendo opens his notebook and writes down Akuro's prophecy.")]),
    ("del", "M352", "Kitsune Hana: older, in dark green with gold leaves. She bows and makes to leave, the way she leaves every room he is in."),
    ("before", "M352", "The governor hasn't been himself since spring.", [
        ("", "A Fox lady in dark green with gold leaves: Kitsune Hana. She bows, and makes to leave, the way she leaves every room the governor is in.")]),
    ("sub", "M418", "Ume-baa would be proud. She'd also tell you to eat something.",
     "Ume-baa will be proud when she hears. She'll also tell you to eat something."),
    ("before", "M418", "Akari? You're better!", [("", "A thin girl sits by the shrine fire, wrapped in a quilt: Akari.")]),
    ("sub", "M104", "Coin first, Hiruma-sama.", "Coin first, Crab."),
    # ---- speaker names (one name = one bust)
    ("name", None, "Nezumi shaman", "Nezumi Shaman"),
    ("name", None, "Nezumi warrior", "Nezumi Warrior"),
    ("name", None, "Bandit chief", "Bandit Chief"),
    ("name", None, "Seduced sentry", "Seduced Sentry"),
    ("name", None, "Crane Soldier", "Crane soldier"),
    ("name", "M303", "Captain", "Mantis captain"),
    ("name", ("M289", "M290"), "Kitsune Hana", "Little Hana"),         # the Phoenix fever child is not Scorpion Ch1's Fox lady
    ("name", "M379", "Shosuro Norie", "Shosuro Norie (letter)"),
]
REGEX = [                                                          # (where, pattern, replacement) on every line
    (None, r"\bSP\b", "MP"),                                       # the spell resource is MP (user, 2026-11-08)
    (None, r"^A beat\.$", "A pause."),
    (None, r"^\(.+ has had enough\. Make amends at the inn\.\)$", "(Word of the Crane with the speeches has got around. Make amends at the inn.)"),
    ("M205", r"^\(.+ thinks a little less of the stiff young Crane\.\)$", "(The Green Ronin's village thinks a little less of the stiff young Crane.)"),
    ("M210", r"^\(.+ thinks a little less of the stiff young Crane\.\)$", "(Garden Under Shadow thinks a little less of the stiff young Crane.)"),
    ("M220", r"^\(.+ thinks a little less of the stiff young Crane\.\)$", "(The Crane port thinks a little less of the stiff young Crane.)"),
    ("M228", r"^\(.+ thinks a little less of the stiff young Crane\.\)$", "(Kyuden Doji thinks a little less of the stiff young Crane.)"),
]
NOT_SERVANT = "M345"                                               # only at the memorial is Mitsue a tea-pouring maid
EAVES = [("Eyes turn to the servant who is standing much too close.", "Eyes turn to the stranger who is standing much too close."),
         ("...Do you mind? Go and pour tea somewhere else.", "...Do you mind? This is a private conversation.")]


def msg(name, text, emo=None):
    c = {"cmd": "cmd_showmsg", "key": "message_talk", "text": text, "name": name, "uiclose": 2}
    if emo:
        c["emo"] = emo
    return c


def blocks(o):
    """Every command list under o (page cmdblocks, if/choice/battle branches), in order."""
    if isinstance(o, list):
        if o and all(isinstance(c, dict) and "cmd" in c for c in o):
            yield o
        for c in o:
            yield from blocks(c)
    elif isinstance(o, dict):
        for v in o.values():
            yield from blocks(v)


def is_msg(c):
    return isinstance(c, dict) and c.get("cmd") == "cmd_showmsg" and isinstance(c.get("text"), str)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    check = "--check" in sys.argv
    path = os.path.join(DATA, "map.json")
    maps = json.load(open(path, encoding="utf-8"))

    def events(where):
        ws = where if isinstance(where, tuple) else (where,)
        for w in ws:
            mid, _, eid = (w or "").partition("/")
            for m, mp in maps.items():
                if mid and m != mid:
                    continue
                for e, ev in (mp.get("event") or {}).items() if isinstance(mp, dict) else ():
                    if eid and e != eid:
                        continue
                    yield m, ev

    stale, total = [], 0
    for fx in FIXES:
        kind, where, n = fx[0], fx[1], 0
        for m, ev in events(where):
            if kind == "page":
                last = ev["page"][-1]
                if any(is_msg(c) and c["text"] == fx[3][0][1] for b in blocks(ev) for c in b):
                    n += 1                                          # already there
                    continue
                p = dict(last)
                p["reqs"] = fx[2]
                p["cmdblock"] = [msg(*x) for x in fx[3]]
                ev["page"].append(p)
                n += 1
                continue
            for b in blocks(ev):
                i = 0
                while i < len(b):
                    c = b[i]
                    if not is_msg(c):
                        i += 1
                        continue
                    if kind == "sub" and fx[2] in c["text"]:
                        if not (fx[3] and fx[2] in fx[3] and fx[3] in c["text"]):   # already applied (the new text holds the old)
                            c["text"] = c["text"].replace(fx[2], fx[3])
                        n += 1
                    elif kind == "name" and c.get("name") == fx[2] and (len(fx) < 5 or fx[4] in c["text"]):
                        c["name"] = fx[3]
                        n += 1
                    elif kind == "del" and c["text"] == fx[2]:
                        del b[i]
                        n += 1
                        continue
                    elif kind == "set" and c["text"] == fx[2]:
                        c.update(fx[3])
                        n += 1
                    elif kind in ("before", "after") and fx[2] in c["text"]:
                        new = [msg(*x) for x in fx[3]]
                        at = i if kind == "before" else i + 1
                        near = b[at - 1] if kind == "before" and at else b[at] if at < len(b) else None
                        if is_msg(near) and near["text"] == new[0]["text"]:     # already applied (run twice)
                            n += 1
                            i += 1
                            continue
                        b[at:at] = new
                        n += 1
                        i += len(new)
                    i += 1
        total += n
        if not n:
            stale.append(fx)
    rx = [0] * len(REGEX)
    ea = 0
    for m, mp in maps.items():
        if not isinstance(mp, dict):
            continue
        for b in blocks(mp.get("event")):
            for c in b:
                if not is_msg(c):
                    continue
                for k, (w, pat, rep) in enumerate(REGEX):
                    if w and w != m:
                        continue
                    t = re.sub(pat, rep, c["text"])
                    if t != c["text"]:
                        c["text"] = t
                        rx[k] += 1
                if m != NOT_SERVANT:
                    for old, new in EAVES:
                        if old in c["text"]:
                            c["text"] = c["text"].replace(old, new)
                            ea += 1
    mv = 0                                                          # commands after a map move never run (checked in the
    for mp in maps.values():                                        # engine, 2026-11-09: three objectives were lost)
        for b in blocks(mp.get("event") if isinstance(mp, dict) else None):
            for i, c in enumerate(b):
                if c.get("cmd") == "cmd_mapmove" and any(x.get("cmd") in ("cmd_showmsg", "cmd_choices") for x in b[i + 1:]):
                    b.append(b.pop(i))
                    mv += 1
                    break
    print("map moves put last:", mv)
    print("dialog fixes: %d lines from %d entries; patterns %s; eavesdrop wording %d" % (total, len(FIXES) - len(stale), rx, ea))
    for fx in stale:
        print("   STALE (no match):", fx[0], fx[1], repr(fx[2])[:70])
    if not check:
        json.dump(maps, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")


if __name__ == "__main__":
    main()
