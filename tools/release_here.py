"""Release this checkout as the next game version: the same steps as release.py, without the D: mirror.

    py -3.12 -E tools\\release_here.py "message" [path ...]

Stages tracked changes plus the given paths, bumps version.json, rebuilds rt_manifest.json (crc32 and size of
every committed file, as the in-game updater expects), commits "Version N: message" and pushes HEAD to main.
"""
import datetime
import json
import os
import subprocess
import sys
import zlib

TRAILER = "Co-authored-by: Copilot App <223556219+Copilot@users.noreply.github.com>"


def git(*args):
    return subprocess.run(["git", "-c", "core.quotepath=off", *args], capture_output=True, text=True,
                          encoding="utf-8", check=True).stdout


def crc(path):
    value = 0
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value = zlib.crc32(block, value)
    return value - (1 << 32) if value >= 1 << 31 else value      # signed, as the engine's crc32 returns it


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    git("fetch", "-q", "origin", "main")
    if subprocess.run(["git", "merge-base", "--is-ancestor", "origin/main", "HEAD"]).returncode:
        sys.exit("origin/main has commits this checkout lacks; merge them first")
    git("add", "-u")
    if sys.argv[2:]:
        git("add", "--", *sys.argv[2:])
    version = json.load(open("version.json"))["version"] + 1
    json.dump({"version": version, "date": datetime.date.today().isoformat()}, open("version.json", "w", newline="\n"))
    files = {path: [str(crc(path)), os.path.getsize(path)] for path in git("ls-files").splitlines()
             if path not in ("version.json", "rt_manifest.json") and not path.lower().endswith((".exe", ".dll"))}
    json.dump({"version": version, "files": files}, open("rt_manifest.json", "w", newline="\n"),
              separators=(",", ":"), sort_keys=True)
    git("add", "version.json", "rt_manifest.json")
    git("commit", "-q", "-m", f"Version {version}: {sys.argv[1]}", "-m", TRAILER)
    git("push", "-q", "origin", "HEAD:main")
    print(f"released version {version}: {len(files)} files, {git('log', '--oneline', '-1').strip()}")


if __name__ == "__main__":
    main()
