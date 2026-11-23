"""Painted backdrops behind the maps (user 2026-11-23: "use comfyui to generate some backgrounds for each of the maps (like
behind the map itself) similar to opening screen background. should be relevant and display the terrain around it").

Each outdoor map gets its own painting (ComfyUI, Z-Image Turbo, tools/comfy/map_bg_api.json): a wide landscape seen from
high up, the land around that map - its name, its builder's comment in gen_maps.py, the clan land its road runs through
(RokuganMarkerData MK_PATH), terrain words, night / cave / Shadowlands lighting. Interiors use the painting of the map
their door opens onto; battle backdrops get their own. Saved as project/resource/mapbg/<map>.webp (1536x640, ~150 KB);
the game draws it with RokuganBackdrop.sk + the "tex_pano" shader.

    python -E tools/gen_map_backgrounds.py list [--only M101,M102]      the prompts, nothing painted
    python -E tools/gen_map_backgrounds.py paint [--only ...] [--force] [--limit N]   paint the missing ones (resumable)
    python -E tools/gen_map_backgrounds.py apply                         point every map's bg at its painting
apply() also runs at the end of every gen_maps.py build, so a rebuilt map.json keeps its backdrops.
"""
import io
import json
import os
import re
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PROJ = os.path.join(ROOT, "_tools", "rpgcobo-tool", "project")
OUTDIR = os.path.join(PROJ, "resource", "mapbg")
WORKFLOW = os.path.join(HERE, "comfy", "map_bg_api.json")
COMFY = "http://127.0.0.1:8188"
LOG = os.path.join(ROOT, "_art", "preview", "mapbg", "paint_log.txt")

# the land each road runs through (MK_PATH: map -> the traveler whose road it is)
CLAN_LAND = {
    "P100": "the Crab clan's provinces in the south: hard grey stone, the colossal Kaiu Wall of grey stone blocks on the horizon, "
            "rocky shores, pine and stubborn fields, the dark blighted Shadowlands far beyond the Wall",
    "P101": "the Crane clan's provinces on the eastern coast: elegant white and pale blue, blossoming trees, neat rice terraces, "
            "graceful pagodas and white-walled estates by a calm bay",
    "P102": "the Dragon clan's provinces in the northern mountains: towering snow-capped peaks, steep pine forests, terraced "
            "mountain villages, monasteries on cliffs, mist in the valleys",
    "P103": "the Lion clan's provinces: wide golden plains and rolling grassland, fortified farm towns, banners on watchtowers, "
            "distant hills",
    "P104": "the Phoenix clan's provinces in the north-west: red maple forests, clear lakes and rivers, mountain shrines and "
            "temples, the Isawa palaces among the hills",
    "P105": "the Scorpion clan's provinces: dark dense forests, winding rivers, misty hills, black-roofed towns with red trim",
    "P106": "the Unicorn clan's provinces in the west: vast open steppe and grass plains, herds of horses, distant blue mountains, "
            "wide skies",
    "P107": "the Mantis Isles and the river roads: green islands in a bright sea, fishing villages on stilts, "
            "harbours, jungle hills, broad rivers",
}
SHARED_LAND = "the heart of Rokugan: rice paddies, villages, forested hills and the Emperor's roads"
# a map with no road of its own (battle backdrops, side maps): the clan its name points to
NAME_LAND = [(r"kaiu|hida|hiruma|yasuki|kuni|crab|shadowland|the wall", "P100"),
             (r"doji|kakita|asahina|daidoji|crane", "P101"),
             (r"togashi|mirumoto|kitsuki|agasha|tamori|dragon", "P102"),
             (r"akodo|matsu|ikoma|kitsu|lion", "P103"),
             (r"isawa|shiba|asako|phoenix", "P104"),
             (r"bayushi|shosuro|soshi|yogo|scorpion|city of lies|ryoko owari", "P105"),
             (r"shinjo|ide|iuchi|utaku|moto|unicorn", "P106"),
             (r"yoritomo|tsuruchi|mantis|kitsune|floating flowers", "P107")]

# words in a map's name / builder comment -> what the land around it shows
TERRAIN = [
    (r"coast|beach|shore|sea\b|bay|harbou?r|dock|pier|tide|island|isle|surf|cove|lighthouse",
     "the sea and a rocky shoreline"),
    (r"river|ferry|bridge|stream|ford|canal", "a broad river winding through the land"),
    (r"lake|pond|marsh|swamp|bog|fen|reed", "lakes, marsh and reed beds"),
    (r"forest|wood|grove|glade|bamboo|thicket", "deep forest"),
    (r"mountain|peak|pass\b|cliff|crag|summit|ridge|gorge|canyon|quarry", "steep mountains, cliffs and gorges"),
    (r"hill|terrace|slope", "rolling hills"),
    (r"plain|steppe|field|meadow|pasture|paddy|farm|rice", "open fields and rice paddies"),
    (r"snow|winter|ice|frost", "snow over everything"),
    (r"castle|kyuden|shiro|keep|fort|donjon|palace|citadel|wall\b|gate", "a great castle with tiered roofs on high "
                                                                         "stone walls"),
    (r"town|village|city|market|ward|district|street|hamlet|toshi|mura", "the rooftops of a town"),
    (r"temple|shrine|monastery|pagoda", "temples and shrines among trees"),
    (r"camp|tent|army|siege|battlefield", "army camps, tents and banners"),
    (r"road|trail|path|way\b", "dirt roads through the countryside"),
    (r"desert|sand|waste", "dry wastes"),
]

STYLE = ("Soft painterly HD-2D style background art, hand-painted anime landscape, muted natural colours, depth haze "
         "in the distance. Clan names are just names: no cranes, lions, dragons or other animals in the picture (horses only on the Unicorn steppe). Feudal Japan only: dirt roads, wooden and thatched buildings, no modern things. No people, "
         "no text, no border, no frame.")


def maps():
    return json.load(open(os.path.join(PROJ, "data", "map.json"), encoding="utf-8"))


def roads():
    """MK_PATH from RokuganMarkerData.sk: map -> P1xx."""
    s = io.open(os.path.join(PROJ, "plugin", "rokugan", "RokuganMarkerData.sk"), encoding="utf-8").read()
    i = s.index("::Rokugan.MK_PATH <- {")
    j = s.index("}", i)
    return dict(re.findall(r"(M\d+) = \"(P\d+)\"", s[i:j]))


def comments():
    """gen_maps.py builder headers: "# ---- M351 Kudo (S04 the hub; ...)" and the comment lines under them."""
    out = {}
    lines = io.open(os.path.join(HERE, "gen_maps.py"), encoding="utf-8").read().splitlines()
    for k, ln in enumerate(lines):
        m = re.match(r"# -+ (M\d{3})\b(.*)", ln)
        if not m:
            continue
        text = [m.group(2)]
        for nxt in lines[k + 1:k + 4]:
            if nxt.startswith("# ") and not nxt.startswith("# ----"):
                text.append(nxt[2:])
            else:
                break
        out.setdefault(m.group(1), " ".join(text))
    return out


def clean(t):
    t = re.sub(r"\([^)]*\)", "", t or "")                       # story codes, tester notes
    t = re.sub(r"\b[SGPEM]\d{2,4}\b|b_\w+|storyboard \w+", "", t)
    t = re.sub(r"[_:;]+", " ", t)
    return re.sub(r"\s+", " ", t).strip(" .,-")


def kind_of(mid, m, interiors):
    rs = m.get("rsetid") or ""
    if "M800" <= mid < "M900" or rs == "rt_hd2d_battle":
        return "battle"
    if mid in interiors or rs.startswith("pbr_df"):
        return "interior"
    if rs == "rt_hd2d_cave":
        return "cave"
    if rs == "rt_hd2d_shadow":
        return "shadow"
    if rs == "rt_hd2d_night":
        return "night"
    return "field"


def interiors_of_gen_maps():
    """gen_maps INTERIORS keys, read from the source (importing gen_maps builds everything)."""
    s = io.open(os.path.join(HERE, "gen_maps.py"), encoding="utf-8").read()
    out = set()
    for blk in re.findall(r"INTERIORS(?: = \{|\.update\(\{)(.*?)\}\)?\n", s, re.S):
        out.update(re.findall(r"\"(M\d{3})\":", blk))
    return out


def parent(mid, mp, kinds, seen=None):
    """An interior's outdoor map: where its doors go, breadth-first."""
    seen = seen or {mid}
    q = [mid]
    while q:
        cur = q.pop(0)
        for e in (mp.get(cur, {}).get("event") or {}).values():
            d = (e.get("dest") or {}).get("mapid") if e.get("role") == "portal" else None
            if not d:
                continue
            if d in mp and d not in seen:
                seen.add(d)
                if kinds.get(d) in ("field", "night", "shadow"):
                    return d
                q.append(d)
    return None


def plan(only=None):
    mp = maps()
    rd, cm, inter = roads(), comments(), interiors_of_gen_maps()
    kinds = {mid: kind_of(mid, m, inter) for mid, m in mp.items()}
    out = {}
    for mid in sorted(mp):
        if mid < "M100":                                       # (the title screen and test maps keep theirs)
            continue
        m, k = mp[mid], kinds[mid]
        if k == "interior":
            p = parent(mid, mp, kinds)
            out[mid] = {"kind": k, "use": p}
            continue
        name = clean(m.get("name") or "")
        desc = clean(cm.get(mid, ""))
        words = (name + " " + desc).lower()
        terr = []
        for rx, t in TERRAIN:
            if re.search(rx, words) and t not in terr:
                terr.append(t)
        road = rd.get(mid) or next((p_ for rx, p_ in NAME_LAND if re.search(rx, words)), None)
        land = CLAN_LAND.get(road, SHARED_LAND)
        about = name + (" - " + desc if desc and desc.lower() not in name.lower() else "")
        if k == "cave":
            prompt = ("Wide panoramic painted backdrop for a Japanese fantasy RPG: a vast dark underground cavern seen "
                      "from above, rock walls, ledges and stalactites fading into deep darkness, faint warm torchlight "
                      "and glints of minerals. The place: %s. %s" % (about, STYLE))
        elif k == "shadow" or "shadowland" in words or "taint" in words:
            prompt = ("Wide panoramic painted landscape backdrop for a Japanese fantasy RPG, seen from high above, "
                      "looking out to a distant horizon; land in the lower two thirds, sky in the top third. The "
                      "blighted Shadowlands: dead grey-purple earth, twisted black trees, bone-strewn wastes, poisoned "
                      "pools, sickly green mist, a dark blood-red sky. %s%s. %s"
                      % ("Around " + about + ". " if about else "", ", ".join(terr[:3]), STYLE))
        else:
            when = ("at night under a bright moon, deep blue shadows, a few warm lantern lights"
                    if k == "night" else "gentle daylight, pale blue sky with soft clouds")
            if k == "battle":
                lead = "the countryside around a battlefield: %s" % about
            else:
                lead = "the land around %s" % about
            prompt = ("Wide panoramic painted landscape backdrop for a Japanese fantasy RPG (feudal Rokugan), seen "
                      "from high above, looking out over the land to a distant horizon; land fills the lower two "
                      "thirds, sky the top third. It shows %s: %s. In %s. %s. %s"
                      % (lead, ", ".join(terr[:4]) or "fields, woods and hills", land, when, STYLE))
        sig = (k, road) if k in ("cave", "shadow") else (k, road, tuple(terr[:3]))
        out[mid] = {"kind": k, "prompt": prompt, "sig": sig}
    # (user 2026-11-23: "you can re use images for similar areas or connected ones that are similar") maps of the same
    # kind, clan land and main terrain share one painting: one already painted if the group has one, else the first
    groups = {}
    for mid, p in out.items():
        if "sig" in p:
            groups.setdefault(p["sig"], []).append(mid)
    for sig, ms in groups.items():
        rep = next((x for x in ms if os.path.exists(os.path.join(OUTDIR, x + ".webp"))), ms[0])
        for x in ms:
            if x != rep:
                out[x] = {"kind": out[x]["kind"], "use": rep, "shared": True}
    # an interior with no outdoor map found keeps the sky
    return {k: v for k, v in out.items() if not only or k in only}


def paint_one(prompt, seed, dest):
    wf = json.load(open(WORKFLOW, encoding="utf-8"))
    wf["5"]["inputs"]["text"] = prompt
    wf["8"]["inputs"]["seed"] = seed
    req = urllib.request.Request(COMFY + "/prompt", json.dumps({"prompt": wf}).encode(),
                                 {"Content-Type": "application/json"})
    pid = json.load(urllib.request.urlopen(req, timeout=30))["prompt_id"]
    t0 = time.time()
    while time.time() - t0 < 900:
        time.sleep(2)
        h = json.load(urllib.request.urlopen(COMFY + "/history/" + pid, timeout=30))
        if pid not in h:
            continue
        st = h[pid].get("status", {})
        if st.get("status_str") == "error":
            raise RuntimeError(json.dumps(st)[:400])
        imgs = [i for o in h[pid]["outputs"].values() for i in o.get("images", [])]
        if imgs:
            i = imgs[0]
            q = "filename=%s&subfolder=%s&type=%s" % (i["filename"], i["subfolder"], i["type"])
            b = urllib.request.urlopen(COMFY + "/view?" + q, timeout=60).read()
            from PIL import Image
            im = Image.open(io.BytesIO(b)).convert("RGB")
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            im.save(dest + ".tmp.webp", "WEBP", quality=85, method=5)
            os.replace(dest + ".tmp.webp", dest)
            return time.time() - t0
    raise RuntimeError("ComfyUI took over 15 minutes")


def apply(mp=None, quiet=False):
    """Every map whose painting exists (its own, or its outdoor map's for an interior) -> bg tex. Idempotent."""
    own = mp is None
    if own:
        mp = maps()
    pl = plan()
    n = 0
    for mid, p in pl.items():
        src, hops = p.get("use") or (None if p["kind"] == "interior" else mid), 0
        while src and src in pl and pl[src].get("use") and hops < 4:      # an interior whose outdoor map shares
            src, hops = pl[src]["use"], hops + 1
        if not src or not os.path.exists(os.path.join(OUTDIR, src + ".webp")) or mid not in mp:
            continue
        bg = {"type": "tex", "tex": "/resource/mapbg/%s.webp" % src}
        if mp[mid].get("bg") != bg:
            mp[mid]["bg"] = bg
            n += 1
    if own and n:
        sys.path.insert(0, HERE)
        import gen_maps as gm
        gm.save_json_locked(os.path.join(PROJ, "data", "map.json"), mp)
    if not quiet:
        print("backdrops: %d maps pointed at their paintings" % n)
    return n


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = sys.argv[1:]
    cmd = args[0] if args else "list"
    only = None
    if "--only" in args:
        only = set(args[args.index("--only") + 1].split(","))
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else 0
    pl = plan(only)
    if cmd == "list":
        for mid, p in pl.items():
            print(mid, p["kind"], ("-> " + str(p.get("use"))) if "use" in p else p["prompt"])
        print(sum(1 for p in pl.values() if "prompt" in p), "to paint,",
              sum(1 for p in pl.values() if "use" in p), "reuse another map's painting")
        return
    if cmd == "apply":
        apply()
        return
    if cmd == "paint":
        todo = [(mid, p) for mid, p in pl.items() if "prompt" in p and
                ("--force" in args or not os.path.exists(os.path.join(OUTDIR, mid + ".webp")))]
        if limit:
            todo = todo[:limit]
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        print("painting %d backdrops" % len(todo), flush=True)
        for k, (mid, p) in enumerate(todo):
            try:
                dt = paint_one(p["prompt"], int(mid[1:]) * 7919 + 17, os.path.join(OUTDIR, mid + ".webp"))
                msg = "PAINTED %s (%d/%d) %.0f s" % (mid, k + 1, len(todo), dt)
            except Exception as ex:                                       # noqa: BLE001 (log it, go on)
                msg = "FAILED %s: %s" % (mid, str(ex)[:300])
            print(msg, flush=True)
            with open(LOG, "a", encoding="utf-8") as f:
                f.write(time.strftime("%H:%M:%S ") + msg + "\n")
        print("ALL PAINTED", flush=True)
        return
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
