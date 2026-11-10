"""Refresh D:/RokuganTraveler-licensed from the working game. Boss/banner art stays the committed placeholders."""
import filecmp, os, shutil, sys
sys.path.insert(0, "D:/RokuganTraveler/tools")
SRC, DST = "D:/RokuganTraveler", "D:/RokuganTraveler-licensed"
ENGINE = "_tools/rpgcobo-tool"
TOP = ["tools", "docs", "NOTES.md", "HOW TO PLAY.txt", "Play Rokugan Traveler.bat", ENGINE]
SKIP_ENGINE = {"tmp", "backup", "build", "log", "savedata"}
CHANGED = ["project/src/rpg/action/PlayerMoveAction.sk", "project/src/rpg/RPGMain.sk", "project/src/rpg/RPGObjects.sk",
           "project/src/rpg/RPGEvent.sk", "project/src/rpg/battle/BattleRunnerBase.sk", "project/system/ui/GPUI.sk", "project/testplay.sk"]
MARK = b"//\tModified for the Rokugan Traveler fan project (2026). Original: RPG-Cobo, Apache-2.0."
dry = "--dry" in sys.argv
seen, copied, new_boss = set(), 0, []
for top in TOP:
    s = SRC + "/" + top
    if os.path.isfile(s):
        seen.add(top)
        if not os.path.exists(DST + "/" + top) or not filecmp.cmp(s, DST + "/" + top, False):
            copied += 1
            if not dry:
                shutil.copyfile(s, DST + "/" + top)
        continue
    for dp, dn, fn in os.walk(s):
        rel = os.path.relpath(dp, SRC).replace(os.sep, "/")
        dn[:] = [x for x in dn if x not in (".git", "__pycache__") and not (rel == ENGINE and x in SKIP_ENGINE)]
        for x in fn:
            if x.endswith(".pyc") or x in ("NUL.png", "desktop.ini"):
                continue
            r = rel + "/" + x
            seen.add(r)
            f, t = SRC + "/" + r, DST + "/" + r
            if x.startswith(("boss_", "banner_")) and rel.endswith(("resource/enemy_pic", "efx/portrait")):
                if not os.path.exists(t):
                    new_boss.append(r)
                continue
            if r[len(ENGINE) + 1:] in CHANGED and os.path.exists(t):
                b = open(f, "rb").read()
                bom = b"\xef\xbb\xbf" if b.startswith(b"\xef\xbb\xbf") else b""
                nl = b"\r\n" if b"\r\n" in b[:4000] else b"\n"
                data = bom + MARK + nl + b[len(bom):] if MARK not in b else b
                if open(t, "rb").read() != data:
                    copied += 1
                    if not dry:
                        open(t, "wb").write(data)
                continue
            if not os.path.exists(t) or not filecmp.cmp(f, t, False):
                copied += 1
                if not dry:
                    os.makedirs(os.path.dirname(t), exist_ok=True)
                    shutil.copyfile(f, t)
gone = []
for top in TOP:
    d = DST + "/" + top
    if os.path.isdir(d):
        for dp, dn, fn in os.walk(d):
            rel = os.path.relpath(dp, DST).replace(os.sep, "/")
            dn[:] = [x for x in dn if x not in (".git", "__pycache__") and not (rel == ENGINE and x in SKIP_ENGINE)]
            for x in fn:
                r = rel + "/" + x
                if r not in seen and not x.endswith(".pyc") and not (x.startswith(("boss_", "banner_")) and rel.endswith(("resource/enemy_pic", "efx/portrait"))):
                    gone.append(r)
if not dry:
    for r in gone:
        os.remove(DST + "/" + r)
    open(DST + "/.gitattributes", "w", newline="\n").write("# Every file exactly as committed on every machine: the game reads binary formats and line-sensitive scripts.\n* -text\n")
print("changed/new", copied, "removed", len(gone), gone[:8], "new boss files", len(new_boss), new_boss[:12])
