"""Queue every dialog bust still needed into ComfyUI in one go (no waiting), and write the manifest.
python -E tools/queue_busts.py [--dry] [--limit N]
  - redo jobs for traveler scene looks that came out wrong (Gendo / Shizue travel + bath: the "straw hat" drinking-straw
    bug, the bath splotches): masked inpaint on the approved base, 3 seeds each;
  - ONE neutral bust per non-playable speaker (user: only the 8 travelers get emotion sets), ordered by dialog line
    count in map.json, Crab path (M1xx) first: 3 candidates for named side cast, 2 for generic roles.
Writes _art/preview/agents/busts/QUEUE.md + queue.json (character, kind, prompt, seed, prompt id, output folder).
Nothing is wired into the game: tools/collect_busts.py downloads the results after the queue finishes into
_art/busts/<key>/review/ and builds contact sheets; picking a candidate is gen_busts.py's job (NPC_PICK / approved_base).
"""
import json
import os
import re
import sys
import collections
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.argv = sys.argv[:1] + [a for a in sys.argv[1:]]
ARGS = sys.argv[1:]
_argv = sys.argv
sys.argv = [sys.argv[0]]
import gen_busts as g  # noqa: E402
sys.argv = _argv

from PIL import Image  # noqa: E402

ROOT = g.ROOT
MAPJSON = os.path.join(g.PROJ, "data", "map.json")
SIDECAST = os.path.join(HERE, "gen_sidecast.py")
OUTMD = os.path.join(g.PREVIEW, "QUEUE.md")
OUTJS = os.path.join(g.PREVIEW, "queue.json")

TRAVELER_NAMES = {n for k in ("natsuko", "rensei", "gendo", "shizue", "haruki", "mitsue", "tamotsu", "sayo")
                  for n in g.CHARS[k]["names"]}

# Family name -> clan and CLOTHES colours. Never put the clan's animal word in a prompt: "unicorn clan" gave horns and
# purple hair, "lion clan" lion ears (review 2026-11-08).
CLAN = {
    "crab": (["Hida", "Hiruma", "Kaiu", "Kuni", "Yasuki", "Toritaka"], "dark blue-grey and slate blue clothes"),
    "crane": (["Doji", "Kakita", "Daidoji", "Asahina"], "pale blue and white clothes"),
    "lion": (["Akodo", "Matsu", "Ikoma", "Kitsu"], "gold and brown clothes with red"),
    "phoenix": (["Isawa", "Shiba", "Asako", "Agasha"], "orange and red clothes with gold"),
    "dragon": (["Mirumoto", "Kitsuki", "Togashi", "Tamori"], "dark green and gold clothes"),
    "scorpion": (["Bayushi", "Shosuro", "Soshi", "Yogo"], "crimson and black clothes"),
    "unicorn": (["Shinjo", "Ide", "Iuchi", "Moto", "Utaku"], "purple and white clothes"),
    "imperial": (["Seppun", "Miya", "Otomo", "Hantei", "Mibu"], "white, green and gold court clothes"),
    "fox": (["Kitsune"], "green and brown clothes"),
    "sparrow": (["Suzume"], "plain brown and grey clothes"),
    "mantis": (["Yoritomo", "Tsuruchi", "Moshi"], "green and dark teal clothes"),
}
FAMILY = {f: (c, col) for c, (fs, col) in CLAN.items() for f in fs}
FEMALE_END = ("ko", "mi", "e", "yo", "na", "ka", "ri", "ne", "me", "ya", "sa", "hime", "ume")
FEMALE_WORDS = ("woman", "wife", "maiden", "girl", "grandmother", "auntie", "nun", "priestess", "actress", "hostess",
                "maid", "lady", "mother", "sister", "widow", "baa")
NEG_NPC = ["horns", "horn", "single horn", "animal ears", "purple hair", "pink hair", "western clothes", "maid headdress", "apron",
           "school uniform", "military uniform", "buttons", "shirt", "t-shirt", "modern clothes", "drinking straw",
           "receding hairline", "bald forehead", "multiple people",
           # review 2026-11-08: clothes colours leaked into the hair (crane "pale blue" -> blue hair), and some came out
           # as uncoloured sketches
           "blue hair", "aqua hair", "light blue hair", "green hair", "teal hair", "monochrome", "greyscale", "sketch",
           "lineart only", "unfinished", "uncolored"]


def cast_looks_md():
    """docs/art/cast-looks.md: name -> look text."""
    out = {}
    for ln in open(os.path.join(ROOT, "docs", "art", "cast-looks.md"), encoding="utf-8"):
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0] and not cells[0].startswith(("Traveler", "Character", "---")):
            t = re.sub(r"\*+", "", cells[-1])
            out[cells[0]] = re.sub(r"(Unicorn|Lion|Crane|Crab|Phoenix|Dragon|Scorpion|Mantis);?", "", t)
    return out


def sidecast_looks():
    """name -> (female, clan, hair, extras) from gen_sidecast.py's CAST (read as text: that file belongs to the sprite
    agent; nothing of it is imported or run)."""
    txt = open(SIDECAST, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r'dict\(key="[^"]+"(.*?)\)\s*,\s*\n\s*(?=dict\(|#|\])', txt, re.S):
        body = m.group(1)
        nm = re.search(r'name="([^"]+)"', body)
        if not nm:
            continue
        f = "female=True" in body
        clan = (re.search(r'clan="([^"]+)"', body) or [None, ""])[1]
        hs = (re.search(r'hairstyle="([^"]+)"', body) or [None, ""])[1]
        fac = (re.search(r'facial="([^"]+)"', body) or [None, ""])[1]
        old = 'age="old"' in body or "GREY" in body or "WHITE" in body
        out.setdefault(nm.group(1), (f, clan, hs, fac, old))
    return out


def speaker_counts():
    m = json.load(open(MAPJSON, encoding="utf-8"))
    allc, crab = collections.Counter(), collections.Counter()

    def walk(x, mid):
        if isinstance(x, dict):
            if x.get("cmd") == "cmd_showmsg" and x.get("name"):
                allc[x["name"]] += 1
                if mid.startswith("M1"):
                    crab[x["name"]] += 1
            for v in x.values():
                walk(v, mid)
        elif isinstance(x, list):
            for v in x:
                walk(v, mid)
    for mid, mp in m.items():
        walk(mp, mid)
    return allc, crab


def keyname(name):
    k = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return "npc_" + k


def npc_prompt(name, looks, md=None):
    """A prompt from what we know: cast-looks.md, the side-cast design, else the family name's clothes colours and the
    role words. Returns (prompt, extra negatives)."""
    parts = name.split()
    fam = FAMILY.get(parts[0]) if parts else None
    lk = looks.get(name)
    low = name.lower()
    if "nezumi" in low or re.search(r"[A-Z][a-z]*'[A-Z]", name):
        return ("nezumi, anthropomorphic rat, ratfolk, realistic rat head, long tapered snout, small rounded ears set "
                "back, beady eyes, long whiskers, short fur with visible texture, clawed pink hands, scrappy cloth rags, "
                "rope belt, %s, no humans, feudal japan, master splinter style" % name), \
            ["cartoon", "mouse", "tom and jerry", "jerry", "mickey", "chibi", "cute big ears", "round head", "panther",
             "cat", "dog"]
    if lk:
        female, clan, hs, fac, old = lk
    else:
        given = parts[-1].lower() if parts else ""
        female = any(w in low for w in FEMALE_WORDS) or (bool(fam) and given.endswith(FEMALE_END))
        clan, hs, fac, old = (fam[0] if fam else ""), "", "", False
    old = old or any(w in low for w in ("old ", "elder", "grandmother", "veteran", "abbot", "baa", "eldest"))
    child = any(w in low for w in ("child", "boy", "girl", "twins", "young ")) and "boy's" not in low
    who = ("1girl, little girl" if female else "1boy, little boy") if child else \
        ("1girl, woman" if female else "1boy, male focus, man")
    who += ", old, grey hair, wrinkles" if old else ", (black hair:1.2)"
    who += ", natural skin tone, full colour"
    col = CLAN[clan][1] if clan in CLAN else ""
    role = "samurai" if fam else name.lower().replace("'s", "")
    if fam and clan == "imperial":
        role = "imperial courtier"
    if any(w in low for w in ("innkeeper", "merchant", "fisherman", "fishwife", "farmer", "villager", "child", "boy",
                              "girl", "herbalist", "porter", "sailor", "peasant", "servant", "maid", "pedlar", "seller",
                              "boatman", "ferryman", "dock", "driver", "carrier", "burner", "keeper", "refugee")):
        col = "plain worn commoner kimono, muted browns and greys"
    if any(w in low for w in ("guard", "sergeant", "veteran", "ashigaru", "bushi", "soldier", "archer", "sapper",
                              "scout", "engineer", "captain", "sentry", "spearman", "marine", "yojimbo", "outrider")):
        role += ", soldier, lacquered lamellar armor"
    if any(w in low for w in ("monk", "priest", "abbot", "shugenja", "nun", "acolyte", "novice")):
        role += ", robes"
    desc = (md or {}).get(name, "")
    bits = [who, role, desc, col, "%s hair" % hs if hs else "", fac or "", "japanese clothing, kimono",
            "feudal japan, rokugan"]
    return ", ".join(b for b in bits if b), list(NEG_NPC)


def main():
    dry = "--dry" in ARGS
    only = set(ARGS[ARGS.index("--only") + 1].split(",")) if "--only" in ARGS else None   # speaker names
    bad, badlook, badseed = set(), {}, {}
    if "--bad" in ARGS:                                  # tools/bad_busts.json: busts found bad in testing, redo them
        badl = json.load(open(os.path.join(HERE, "bad_busts.json"), encoding="utf-8"))["busts"]
        bad = {b["speaker"] for b in badl if not b.get("fixed")}
        badlook = {b["speaker"]: b.get("look", "") for b in badl}       # what the new candidates must show
        badseed = {b["speaker"]: b.get("seed_add", 0) for b in badl}    # another round: new seeds
        only = (only & bad) if only else bad                      # --bad --only X: just that bad one
    redo = "--redo" in ARGS or bool(only) or "--bad" in ARGS              # only speakers without a pick yet, improved prompts, name-hashed seeds
    md = cast_looks_md()
    picked = set()
    for k, c in g.CHARS.items():
        if c.get("npc") and (c.get("seed") or c.get("base_file")):
            picked.update(c["names"])
    limit = int(ARGS[ARGS.index("--limit") + 1]) if "--limit" in ARGS else None
    os.makedirs(g.PREVIEW, exist_ok=True)
    jobs = []

    # 1. traveler look redos (masked inpaint on the approved base; composited by collect_busts.py)
    for key, vns in (() if redo else (("gendo", ["travel", "bath"]), ("shizue", ["travel", "bath"]))):
        c = g.CHARS[key]
        base = g.base_image(key)
        look = c.get("look", c["prompt"])
        for vn in vns:
            v = g.VARIANTS[vn]
            vt = v["tags"].format(colors=c.get("colors", ""), court=c.get("court", ""), night=c.get("night", ""))
            pos = "%s, %s, (%s:1.2), expressionless, calm" % (g.style_for(c), look, vt)
            neg = g.neg_for(v.get("neg_drop", ()), v.get("neg_add", ()))
            for s in (211, 212, 213):
                jobs.append(dict(key=key, kind="variant", variant=vn, seed=s, prompt=pos, neg=neg,
                                 denoise=v["denoise"], regions=v["regions"]))

    # 2. one neutral bust per non-playable speaker
    looks = sidecast_looks()
    allc, crab = speaker_counts()
    done = set(os.listdir(os.path.join(g.PROJ, "resource", "bust"))) if os.path.isdir(
        os.path.join(g.PROJ, "resource", "bust")) else set()
    named = {n: k for k, c in g.CHARS.items() for n in c["names"]}
    order = sorted(allc, key=lambda n: (0 if crab[n] else 1, -crab[n], -allc[n], n))
    order += sorted(n for n in bad if n not in allc)          # bad_busts speakers the map scan misses (script-set names)
    for name in order:
        base_name = name.split(" (")[0]
        if not name.strip() or base_name in TRAVELER_NAMES or base_name != name or name in ("Note",)                 or not re.search(r"[A-Za-z]", name):
            continue
        key = named.get(name)
        if key and key in done and name not in bad:
            continue                                         # already exported (picked earlier)
        if redo and name in picked and name not in bad:
            continue
        if only is not None and name not in only:
            continue
        if key == "squeak":
            continue                                         # Splinter-style candidates already made (seeds 11-14)
        if key:
            c = g.CHARS[key]
            if os.path.exists(g.cand_path(key, 1)) and not redo:
                continue                                     # candidates already made by gen_busts.py base
            pos, extra = g.base_prompt(c), c.get("neg_add", [])
            if not c.get("prompt"):                          # picked from candidates (base_file): no prompt kept
                p, extra = npc_prompt(name, looks, md)
                pos = "%s, %s, %s" % (g.STYLE, p, g.EMO["neutral"][0])
        else:
            key = keyname(name)
            p, extra = npc_prompt(name, looks, md)
            pos = "%s, %s, %s" % (g.STYLE, p, g.EMO["neutral"][0])
        if badlook.get(name):                                # bad_busts.json "look": the person described, ONLY -
            # the speaker label is left out of the prompt (it misleads: "Bloodspeaker" drew loudspeakers, "Old nun"
            # a western habit, "Otomo Shinken" a girl)
            pos = "%s, (%s:1.3), upper body portrait, japanese clothing, feudal japan, rokugan, %s" % (
                g.STYLE, badlook[name], g.EMO["neutral"][0])
            extra = list(extra) + ["loudspeaker", "speaker", "western clothes", "nun habit", "veil"]
        neg = g.neg_for((), list(extra) + ["drinking straw", "straw (drink)", "receding hairline", "bald forehead"]
                        if "bald" not in pos else list(extra) + ["drinking straw"])
        n = 3 if (name in looks or name in named) else 2
        # no two speakers share a seed (same face). "|v2": new seeds for the fixed prompts, so the rejected speakers'
        # old candidates (kept on disk) don't count as done
        s0 = ((zlib.crc32((name + "|v2").encode()) % 90000 + 1000) if redo else 0) + badseed.get(name, 0)
        for s in [s0 + i for i in range(1, n + 1)]:
            if redo and os.path.exists(os.path.join(g.WORK, key, "review", "cand_s%d.png" % s)):
                continue                                     # resumable: already generated
            jobs.append(dict(key=key, kind="npc", name=name, lines=allc[name], crab_lines=crab[name], seed=s,
                             prompt=pos, neg=neg))
    if limit:
        jobs = jobs[:limit]

    # folders + submit
    for j in jobs:
        os.makedirs(os.path.join(g.WORK, j["key"], "review"), exist_ok=True)
    if not dry:
        uploaded = {}
        for j in jobs:
            if j["kind"] == "variant":
                c = g.CHARS[j["key"]]
                if j["key"] not in uploaded:
                    uploaded[j["key"]] = g.upload(g.base_image(j["key"]), "rt_bust_%s_base.png" % j["key"])
                base = g.base_image(j["key"])
                m = g.variant_mask(c, base, j["regions"])
                mname = g.upload(Image.merge("RGB", (m, m, m)), "rt_bust_%s_vmask_%s.png" % (j["key"], j["variant"]))
                wf = g.wf_inpaint(j["prompt"], j["neg"], j["seed"], uploaded[j["key"]], mname, j["denoise"])
                wf["10"]["inputs"]["filename_prefix"] = "rt_bust_queue/%s/var_%s_s%d" % (j["key"], j["variant"],
                                                                                         j["seed"])
            else:
                wf = g.wf_txt2img(j["prompt"], j["neg"], j["seed"])
                wf["7"]["inputs"]["filename_prefix"] = "rt_bust_queue/%s/cand_s%d" % (j["key"], j["seed"])
            r = json.loads(g._req("/prompt", json.dumps({"prompt": wf, "client_id": "rt_bust_queue"}).encode()))
            j["prompt_id"] = r["prompt_id"]
    if redo and os.path.exists(OUTJS) and not dry:                       # keep the earlier jobs in the manifest (collect reads all)
        jobs = json.load(open(OUTJS, encoding="utf-8")) + jobs
    if not dry:                                  # a dry run must leave the job list alone
        json.dump(jobs, open(OUTJS, "w", encoding="utf-8"), indent=1)
    lines = ["# Dialog bust queue (%d ComfyUI jobs, %s)" % (len(jobs), "dry run" if dry else "submitted"),
             "", "Collect after the queue finishes: `python -E tools/collect_busts.py` (downloads into "
             "_art/busts/<key>/review/, sheets in _art/preview/agents/busts/review_*.png). Nothing here is in the "
             "game until a candidate is picked (gen_busts.py NPC_PICK / approved_base + `npc <key>`).", "",
             "| # | character | kind | lines (crab) | seed | output | prompt (start) |", "|---|---|---|---|---|---|---|"]
    for i, j in enumerate(jobs):
        out = "_art/busts/%s/review/%s_s%d.png" % (j["key"], ("var_" + j["variant"]) if j["kind"] == "variant"
                                                   else "cand", j["seed"])
        lines.append("| %d | %s | %s | %s | %d | %s | %s |" % (
            i + 1, j.get("name", j["key"]), j["kind"] + (" " + j.get("variant", "") if j["kind"] == "variant" else ""),
            "%s (%s)" % (j.get("lines", ""), j.get("crab_lines", "")) if j["kind"] == "npc" else "-", j["seed"], out,
            j["prompt"].replace(g.STYLE, "").strip(", ")[:90].replace("|", "/")))
    open(OUTMD, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("%d jobs %s; manifest %s" % (len(jobs), "listed" if dry else "queued", OUTMD))


if __name__ == "__main__":
    main()
