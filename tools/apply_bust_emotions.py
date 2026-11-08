"""Hand-read dialog expressions for the eight travelers (user, 2026-11-08). tools/bust_emotions.json holds "speaker<TAB>text" -> emotion.
Sets the "emo" field on each matching line of map.json and macro.json. A [tag] written in the text still wins; a bustHold beats emo.
"sad" reads as crying on the bust, so it is kept for real grief; "hurt" for actual injury.
Runs at the end of tools/regen.py, and can be run alone: python -E tools/apply_bust_emotions.py"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "data"))
TRAVELERS = {"Hiruma Natsuko", "Kakita Rensei", "Kitsuki Gendo", "Akodo Shizue", "Isawa Haruki", "Shosuro Mitsue", "Ide Tamotsu", "Sayo",
             "Natsuko", "Rensei", "Gendo", "Shizue", "Haruki", "Mitsue", "Tamotsu"}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    table = json.load(open(os.path.join(HERE, "bust_emotions.json"), encoding="utf-8"))
    count, missing = collections.Counter(), []

    def walk(o):
        if isinstance(o, dict):
            if o.get("key") == "message_talk" and isinstance(o.get("text"), str):
                n = o.get("name") or ""
                e = table.get(n + "\t" + o["text"])
                if e:
                    o["emo"] = e
                    count[e] += 1
                elif n.split(" (")[0] in TRAVELERS:
                    missing.append(n + ": " + o["text"][:50])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    for name in ("map", "macro"):
        p = os.path.join(DATA, name + ".json")
        d = json.load(open(p, encoding="utf-8"))
        walk(d)
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent="\t")
    print("expressions set:", dict(count))
    if missing:
        print(len(missing), "traveler lines have no hand-read expression (keyword guess used), e.g.", missing[:5])


if __name__ == "__main__":
    main()
