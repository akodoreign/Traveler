import re, sys, glob, os
# usage: consistency.py <docs_dir>
docs = sys.argv[1]
files = glob.glob(os.path.join(docs, "story", "production", "*.md")) + \
        glob.glob(os.path.join(docs, "story", "sidestories", "*.md"))
sets, reads, battles = {}, {}, {}
for f in files:
    name = os.path.basename(f)
    t = open(f, encoding="utf-8").read()
    # header lists
    for m in re.finditer(r"\*\*Flags set:\*\*([^\n]+(?:\n(?!\*\*)[^\n]+)*)", t):
        for fl in re.findall(r"`([a-z_]+)", m.group(1)):
            sets.setdefault(fl, set()).add(name)
    for m in re.finditer(r"\*\*Flags read[^*]*:\*\*([^·\n]+)", t):
        for fl in re.findall(r"`([a-z_]+)", m.group(1)):
            reads.setdefault(fl, set()).add(name)
    for fl in re.findall(r"\[SET ([a-z0-9_]+)", t):
        sets.setdefault(fl, set()).add(name)
    for cond in re.findall(r"\[(?:ELSE )?IF ([^\]]+)\]", t):
        for fl in re.findall(r"\b([a-z][a-z0-9_]{3,})\b", cond):
            if fl in ("and", "or", "not", "in", "party", "recruited", "present", "route", "owner", "true", "false",
                      "any", "ally", "samurai", "turn", "honor", "rank", "used", "active", "side", "story", "done", "from"):
                continue
            reads.setdefault(fl, set()).add(name)
    for b in re.findall(r"\[BATTLE (b_[a-z0-9_]+)", t):
        battles.setdefault(b, set()).add(name)
bosses = open(os.path.join(docs, "rules", "bosses.md"), encoding="utf-8").read()
def in_bosses(b):
    if b in bosses: return True
    base = re.sub(r"_\d+$", "", b)          # b_ford_waves_3 -> b_ford_waves
    base2 = re.sub(r"_[ab]$", "", b)        # b_cave_nezumi_a -> b_cave_nezumi
    return (base + "_") in bosses or base2 in bosses
print("=== FLAGS SET BUT NEVER READ ===")
for fl in sorted(set(sets) - set(reads)):
    print(f"  {fl}  (set in {', '.join(sorted(sets[fl]))})")
print("=== FLAGS READ BUT NEVER SET ===")
for fl in sorted(set(reads) - set(sets)):
    print(f"  {fl}  (read in {', '.join(sorted(reads[fl]))})")
print("=== BATTLE IDS MISSING FROM bosses.md ===")
for b in sorted(battles):
    if not in_bosses(b):
        print(f"  {b}  ({', '.join(sorted(battles[b]))})")
print(f"files={len(files)} flags_set={len(sets)} flags_read={len(reads)} battles={len(battles)}")
