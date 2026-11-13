"""Push a new game version to GitHub (user 2026-11-12: the title screen's Update "will keep track by version number on
git (increment with each push)").

    python tools/release.py <commit message file>

1. tools/sync_licensed.py refreshes D:/RokuganTraveler-licensed (no wiki art: the committed placeholders stay);
2. version.json {version: N+1, date} in the repo root;
3. rt_manifest.json {version, files: {path: [crc32, size]}} for every committed file but version.json / rt_manifest.json
   and .exe/.dll (locked while the game runs, so the in-game updater can't replace them anyway);
4. commit (the message file as given, UTF-8 without BOM) and push licensed-demo -> origin main. Never forced.
The game's RokuganUpdate.sk reads both files from raw.githubusercontent.com.
"""
import datetime, json, os, subprocess, sys, zlib

DST = "D:/RokuganTraveler-licensed"
PY = sys.executable


def git(*a, out=False):
    r = subprocess.run(["git", "-C", DST, "-c", "core.quotepath=off", *a], capture_output=True, text=True,
                       encoding="utf-8")
    if r.returncode:
        sys.exit("git %s failed:\n%s%s" % (" ".join(a), r.stdout, r.stderr))
    return r.stdout if out else None


def crc(path):
    c = 0
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            c = zlib.crc32(b, c)
    c &= 0xffffffff
    return c - (1 << 32) if c >= 1 << 31 else c      # signed, as the engine's ByteBuffer.crc32 returns it


def main():
    if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]):
        sys.exit(__doc__)
    msg = open(sys.argv[1], encoding="utf-8-sig").read()
    subprocess.run([PY, "D:/RokuganTraveler/tools/sync_licensed.py"], check=True)
    vf = DST + "/version.json"
    ver = json.load(open(vf))["version"] + 1 if os.path.exists(vf) else 1
    json.dump({"version": ver, "date": datetime.date.today().isoformat()}, open(vf, "w", newline="\n"))
    git("add", "-A")
    files = {}
    for p in git("ls-files", out=True).splitlines():
        if p in ("version.json", "rt_manifest.json") or p.lower().endswith((".exe", ".dll")):
            continue
        fp = DST + "/" + p
        files[p] = [crc(fp), os.path.getsize(fp)]
    json.dump({"version": ver, "files": files}, open(DST + "/rt_manifest.json", "w", newline="\n"),
              separators=(",", ":"), sort_keys=True)
    git("add", "-A")
    tmp = DST + "/.git/RT_COMMIT_MSG"
    open(tmp, "w", encoding="utf-8", newline="\n").write("Version %d: %s" % (ver, msg))
    git("commit", "-q", "-F", tmp)
    git("push", "-q", "origin", "licensed-demo:main")
    print("released version %d: %d files in the manifest, %s" % (ver, len(files), git("log", "--oneline", "-1", out=True).strip()))


if __name__ == "__main__":
    main()
