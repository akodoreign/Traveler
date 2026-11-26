"""Release this checkout as the next game version: the same steps as release.py, without the D: mirror.

    py -3 -E tools\\release_here.py "message" [path ...] [--pack-generation DIRECTORY]
        [--scoped] [--paths-file FILE] [--from-index] [--pack-only]

Without --scoped, stages all tracked changes plus the given paths. With --scoped, stages only the specified
paths and builds the manifest from staged Git blobs. Both modes commit and push HEAD to main immediately.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid
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


def manifest_from_index(with_asset_hashes=False):
    """Hash staged Git blobs, not unrelated modifications in the working tree."""
    listing = subprocess.run(["git", "ls-files", "--stage", "-z"], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, check=True).stdout
    blobs = []
    for item in listing.split(b"\0"):
        if not item:
            continue
        meta, name = item.split(b"\t", 1)
        mode, oid, stage = meta.split()
        if stage != b"0":
            raise ValueError("Unmerged files cannot be released")
        path = name.decode("utf-8")
        if (path in ("version.json", "rt_manifest.json") or path.lower().endswith((".exe", ".dll"))
                or path.startswith("_tools/rpgcobo-tool/project/rtpacks/")
                or path.startswith("_tools/rpgcobo-tool/rtpack-tools/")):
            continue
        if mode not in (b"100644", b"100755"):
            raise ValueError(f"Unsupported indexed file mode for release: {path}")
        blobs.append((path, oid))
    proc = subprocess.Popen(["git", "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    files, hashes = {}, {}
    try:
        for path, oid in blobs:
            proc.stdin.write(oid + b"\n")
            proc.stdin.flush()
            header = proc.stdout.readline().split()
            if len(header) != 3 or header[0] != oid or header[1] != b"blob":
                raise ValueError(f"Cannot read staged blob: {path}")
            size = int(header[2])
            left, value = size, 0
            prefix = "_tools/rpgcobo-tool/project/"
            relative = path[len(prefix):] if path.startswith(prefix) else ""
            is_asset = (relative.startswith("resource/native_") and
                        Path(relative).suffix.lower() in (".mdl", ".mot", ".pm", ".png"))
            hasher = hashlib.sha256() if with_asset_hashes and is_asset else None
            while left:
                block = proc.stdout.read(min(left, 1024 * 1024))
                if not block:
                    raise ValueError(f"Truncated staged blob: {path}")
                left -= len(block)
                value = zlib.crc32(block, value)
                if hasher:
                    hasher.update(block)
            if proc.stdout.read(1) != b"\n":
                raise ValueError(f"Invalid staged blob boundary: {path}")
            if value >= 1 << 31:
                value -= 1 << 32
            files[path] = [str(value), size]
            if hasher:
                hashes[relative] = hasher.hexdigest()
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError(proc.stderr.read().decode("utf-8", errors="replace"))
    finally:
        if proc.poll() is None:
            proc.terminate()
            proc.wait()
        proc.stdout.close()
        proc.stderr.close()
    return (files, hashes) if with_asset_hashes else files


def release_index_signature():
    """Detect any change to reviewed source entries while building the release."""
    data = subprocess.run(["git", "ls-files", "--stage", "-z"], stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, check=True).stdout
    kept = []
    for item in data.split(b"\0"):
        if not item:
            continue
        _, name = item.split(b"\t", 1)
        if (name in (b"version.json", b"rt_manifest.json")
                or name.startswith(b"_tools/rpgcobo-tool/project/rtpacks/")
                or name.startswith(b"_tools/rpgcobo-tool/rtpack-tools/")):
            continue
        kept.append(item)
    return hashlib.sha256(b"\0".join(kept)).hexdigest()


def indexed_bytes(path):
    return subprocess.run(["git", "show", ":" + path], stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, check=True).stdout


def staged_reserved_paths():
    staged = subprocess.run(["git", "diff", "--cached", "--name-only", "-z"], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, check=True).stdout.split(b"\0")
    return {name.decode("utf-8") for name in staged if name and (
        name in (b"version.json", b"rt_manifest.json")
        or name.startswith(b"_tools/rpgcobo-tool/project/rtpacks/")
        or name.startswith(b"_tools/rpgcobo-tool/rtpack-tools/"))}


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    arguments = sys.argv[2:]
    pack_only = "--pack-only" in arguments
    if arguments.count("--pack-only") > 1:
        sys.exit("Specify --pack-only at most once")
    if pack_only:
        arguments = [arg for arg in arguments if arg != "--pack-only"]
    from_index = "--from-index" in arguments
    if arguments.count("--from-index") > 1:
        sys.exit("Specify --from-index at most once")
    if from_index:
        arguments = [arg for arg in arguments if arg != "--from-index"]
    scoped = "--scoped" in arguments
    if arguments.count("--scoped") > 1:
        sys.exit("Specify --scoped at most once")
    if scoped:
        arguments = [arg for arg in arguments if arg != "--scoped"]
    generation = None
    if "--pack-generation" in arguments:
        position = arguments.index("--pack-generation")
        if position + 1 >= len(arguments) or "--pack-generation" in arguments[position + 2:]:
            sys.exit("Specify --pack-generation once, followed by its directory")
        generation = arguments[position + 1]
        arguments = arguments[:position] + arguments[position + 2:]
    if "--paths-file" in arguments:
        position = arguments.index("--paths-file")
        if position + 1 >= len(arguments) or "--paths-file" in arguments[position + 2:]:
            sys.exit("Specify --paths-file once, followed by its UTF-8 path list")
        extra = Path(arguments[position + 1]).read_text(encoding="utf-8-sig").splitlines()
        if not extra or any(not item or "\0" in item for item in extra):
            sys.exit("The path list must contain one nonempty path per line")
        arguments = arguments[:position] + arguments[position + 2:] + extra
    pack_root = Path("_tools") / "rpgcobo-tool" / "project" / "rtpacks"
    if (pack_root / "active.json").exists() and not generation:
        sys.exit("An active pack exists; supply a matching --pack-generation for this release")
    if from_index and (scoped or arguments or not generation):
        sys.exit("--from-index requires --pack-generation and no paths or --scoped")
    if pack_only and not from_index:
        sys.exit("--pack-only requires --from-index")
    if scoped and (not generation or not arguments):
        sys.exit("--scoped requires --pack-generation and explicit approved paths")
    git("fetch", "-q", "origin", "main")
    if subprocess.run(["git", "merge-base", "--is-ancestor", "origin/main", "HEAD"]).returncode:
        sys.exit("origin/main has commits this checkout lacks; merge them first")
    if scoped or from_index:
        if scoped and subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode:
            sys.exit("--scoped requires a clean staging area")
        indexed_version = indexed_bytes("version.json")
        if Path("version.json").read_bytes() != indexed_version:
            sys.exit("version.json has uncommitted changes; review them before release")
        if from_index:
            if staged_reserved_paths():
                sys.exit("Do not pre-stage generated pack, bundle, version or manifest files")
            for name in ("tools/release_here.py", "tools/rt_packs.py"):
                if Path(name).read_bytes() != indexed_bytes(name):
                    sys.exit(f"Stage the exact pack release tool before using --from-index: {name}")
    else:
        git("add", "-u")
    if arguments:
        if scoped:
            pathspec = Path(".rt-release-paths-" + uuid.uuid4().hex)
            try:
                pathspec.write_bytes(b"".join(path.encode("utf-8") + b"\0" for path in arguments))
                git("add", "--pathspec-from-file=" + str(pathspec), "--pathspec-file-nul")
            finally:
                if pathspec.exists():
                    pathspec.unlink()
        else:
            git("add", "--", *arguments)
    with open("version.json", encoding="utf-8") as stream:
        version = json.load(stream)["version"] + 1
    signature = release_index_signature() if from_index else None
    if from_index:
        files, asset_hashes = manifest_from_index(with_asset_hashes=True)
        if release_index_signature() != signature:
            sys.exit("Reviewed index changed while reading; review and retry")
    else:
        asset_hashes = None
        files = manifest_from_index() if scoped else {
        path: [str(crc(path)), os.path.getsize(path)] for path in git("ls-files").splitlines()
        if path not in ("version.json", "rt_manifest.json") and not path.lower().endswith((".exe", ".dll"))}
    if generation:
        import rt_packs
        # The candidate manifest describes the staged loose files. The helper
        # checks that those bytes and the pack-enabled code match the generation.
        token = uuid.uuid4().hex
        candidate_manifest = Path(".rt-release-manifest-" + token + ".json")
        overlay = Path(".rt-release-overlay-" + token)
        try:
            with candidate_manifest.open("x", encoding="utf-8", newline="\n") as stream:
                json.dump({"version": version - 1, "files": files}, stream, separators=(",", ":"), sort_keys=True)
            rt_packs.stage_compatible_release(candidate_manifest, generation, overlay, version,
                                              staged_hashes=asset_hashes,
                                              content_provider=indexed_bytes if from_index else None,
                                              pack_only=pack_only)
            if from_index and (release_index_signature() != signature or staged_reserved_paths()):
                sys.exit("Reviewed index changed while preparing packs; review and retry")
            rt_packs.apply_compatible_overlay(overlay, ".", staged_hashes=asset_hashes, pack_only=pack_only)
        finally:
            if candidate_manifest.exists():
                candidate_manifest.unlink()
            if overlay.exists():
                shutil.rmtree(rt_packs.extended_path(overlay))
        index = json.loads((pack_root / "active.json").read_bytes())
        git("add", "--", str(pack_root / "active.json"), str(pack_root / index["generation"]),
            str(pack_root.parent.parent / "rtpack-tools"))
        watched = [pack_root.parent / "resource", pack_root.parent / "rt_pack.sk",
                   pack_root.parent / "plugin" / "rokugan" / "RokuganUpdate.sk",
                   pack_root.parent.parent / "boot.sk",
                   *(Path("tools") / name for name in rt_packs.CUTOVER_TOOLS)]
        if not from_index and subprocess.run(
                ["git", "diff", "--quiet", "--", *(str(path) for path in watched)]).returncode:
            sys.exit("Assets or pack integration changed while preparing the release; review and retry")
        files = json.loads(Path("rt_manifest.json").read_bytes())["files"]
    else:
        json.dump({"version": version, "date": datetime.date.today().isoformat()}, open("version.json", "w", newline="\n"))
        json.dump({"version": version, "files": files}, open("rt_manifest.json", "w", newline="\n"),
                  separators=(",", ":"), sort_keys=True)
    git("add", "version.json", "rt_manifest.json")
    if from_index:
        allowed = {"version.json", "rt_manifest.json"} | {
            path for path in files if path.startswith(("_tools/rpgcobo-tool/project/rtpacks/",
                                                       "_tools/rpgcobo-tool/rtpack-tools/"))}
        if release_index_signature() != signature or staged_reserved_paths() - allowed:
            sys.exit("Reviewed index changed during release preparation; review and retry")
        if subprocess.run(["git", "diff", "--quiet", "--", *sorted(allowed)]).returncode:
            sys.exit("Generated release files changed after staging; review and retry")
    git("commit", "-q", "-m", f"Version {version}: {sys.argv[1]}", "-m", TRAILER)
    git("push", "-q", "origin", "HEAD:main")
    print(f"released version {version}: {len(files)} files, {git('log', '--oneline', '-1').strip()}")


if __name__ == "__main__":
    main()
