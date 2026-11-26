"""Build and trial-install bounded, compressed Traveler asset packs.

The installer deliberately requires an isolated-profile marker; it is not the
in-game updater and must not be used to migrate an existing installation.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zlib

LIMIT = 49 * 1024 * 1024
EXTENSIONS = {".mdl", ".mot", ".pm", ".png"}
MARKER = ".rt-pack-isolated-profile"
CUTOVER_TOOLS = ("rt_packs.py", "rt_pack_cutover.py", "traveler_instances.py")
CUTOVER_README = """\
Traveler pack cleanup (Windows, Python 3.12 or newer)

Close the game and coordinate with anyone editing this installation first.
From the game folder, run:

py -3 rtpack-tools\\rt_pack_cutover.py prepare .
py -3 rtpack-tools\\rt_pack_cutover.py apply . TRANSACTION_ID
py -3 rtpack-tools\\rt_pack_cutover.py seal . TRANSACTION_ID

The prepare command prints the transaction ID. Apply moves only verified
duplicate loose assets to quarantine. Seal is a separate choice that frees
disk space; retain the transaction and its referenced pack generation.
To restore, close the game and run:

py -3 rtpack-tools\\rt_pack_cutover.py restore . TRANSACTION_ID

Restore never overwrites existing files. Do not remove the retained pack
generation; sealed files need it for recovery.
"""


def signed_crc(data):
    value = zlib.crc32(data)
    return str(value - (1 << 32) if value >= 1 << 31 else value)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def extended_path(path):
    path = Path(path).resolve()
    if os.name == "nt" and not str(path).startswith("\\\\?\\"):
        text = str(path)
        path = Path("\\\\?\\UNC\\" + text[2:] if text.startswith("\\\\") else "\\\\?\\" + text)
    return path


def asset_path(name):
    p = PurePosixPath(name)
    if (str(p) != name or len(p.parts) < 3 or p.parts[0] != "resource"
            or not p.parts[1].startswith("native_")
            or any(part in ("", ".", "..") or "\\" in part or ":" in part for part in p.parts)
            or p.suffix.lower() not in EXTENSIONS):
        raise ValueError(f"Invalid asset path: {name}")
    return p


def no_links(root, path):
    current = root
    for part in path.parts:
        current = current / part
        if current.is_symlink() or (hasattr(current, "is_junction") and current.is_junction()):
            raise ValueError(f"Linked path is not allowed: {current}")
    return current


def build(project, output, limit=LIMIT, previous=None, overlay=False, remove=()):
    project, output = Path(project).resolve(), Path(output).resolve()
    if limit <= 0 or limit > LIMIT:
        raise ValueError("Pack limit must be between 1 byte and 49 MiB")
    if output == project or project in output.parents:
        raise ValueError("Output must be outside the source project")
    output.mkdir(parents=True, exist_ok=True)
    previous = Path(previous).resolve() if previous else None
    old = None
    if previous:
        old = json.loads((previous / "active.json").read_bytes())
        verify(previous, old)
    if overlay and not old:
        raise ValueError("Overlay builds require a previous generation")
    if remove and not overlay:
        raise ValueError("Explicit removals require an overlay build")
    removed = set(remove)
    for name in removed:
        asset_path(name)
        if name not in old["entries"]:
            raise ValueError(f"Cannot remove missing asset: {name}")
    staging = output / (".building-" + uuid.uuid4().hex)
    staging.mkdir()
    entries, packs = {}, {}
    try:
        resource = project / "resource"
        def find_files():
            return sorted(p for directory in resource.glob("native_*") if directory.is_dir()
                          for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in EXTENSIONS)

        files = find_files()
        if not files and not overlay:
            raise ValueError("No native assets found")
        paths, snapshot = {}, {}
        for path in files:
            rel = path.relative_to(project)
            no_links(project, rel)
            name = rel.as_posix()
            asset_path(name)
            stat = path.stat()
            paths[name] = path
            snapshot[name] = (stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)

        old_entries = old["entries"] if old else {}
        if removed.intersection(paths):
            raise ValueError("An asset cannot be both supplied and removed")
        selected = ((set(old_entries) - removed) | set(paths)) if overlay else set(paths)
        if not selected:
            raise ValueError("No native assets remain")
        groups = {}
        if old:
            for name, entry in sorted(old_entries.items(), key=lambda item: (item[1][0], item[1][1])):
                if name in selected:
                    groups.setdefault(entry[0], []).append(name)
        new_names = sorted(set(paths) - set(old_entries))
        if groups:
            groups[sorted(groups)[-1]].extend(new_names)
        else:
            groups["pack00000.pak"] = new_names or sorted(paths)
        next_number = max((int(name[4:9]) for name in (old["packs"] if old else {})), default=-1) + 1
        if not old:
            next_number = 1
        deferred = []

        def write_group(pack, names):
            size, stream = 0, None
            try:
                for position, name in enumerate(names):
                    path = paths.get(name)
                    raw = None
                    if path:
                        raw = path.read_bytes()
                        stat = path.stat()
                        if snapshot[name] != (stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns):
                            raise ValueError(f"Asset changed during build: {name}")
                    compressed = None
                    prior = old_entries.get(name)
                    if prior:
                        with (previous / prior[0]).open("rb") as source:
                            source.seek(prior[1])
                            existing = source.read(prior[2])
                        if raw is None or zlib.decompress(existing) == raw:
                            compressed = existing
                    if compressed is None:
                        compressed = zlib.compress(raw, 6)
                    if len(compressed) > limit:
                        raise ValueError(f"Compressed asset exceeds pack limit: {name}")
                    if size + len(compressed) > limit:
                        deferred.extend(names[position:])
                        break
                    if stream is None:
                        stream = (staging / pack).open("wb")
                    raw_size = len(raw) if raw is not None else prior[3]
                    raw_crc = signed_crc(raw) if raw is not None else prior[4]
                    entries[name] = [pack, size, len(compressed), raw_size, raw_crc]
                    stream.write(compressed)
                    size += len(compressed)
            finally:
                if stream:
                    stream.close()

        for pack, names in sorted(groups.items()):
            write_group(pack, names)
        while deferred:
            if next_number > 99999:
                raise ValueError("Pack number limit exceeded")
            names, deferred = deferred, []
            write_group(f"pack{next_number:05d}.pak", names)
            next_number += 1
        if find_files() != files:
            raise ValueError("Asset list changed during build")
        for name, path in paths.items():
            stat = path.stat()
            if snapshot[name] != (stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns):
                raise ValueError(f"Asset changed during build: {name}")
        for path in sorted(staging.glob("*.pak")):
            data = path.read_bytes()
            packs[path.name] = [len(data), digest(data)]
        identity = json.dumps({"entries": entries, "packs": packs}, sort_keys=True,
                              separators=(",", ":")).encode()
        generation = "v" + digest(identity)[:24]
        index = {"format": 1, "generation": generation, "packs": packs, "entries": entries}
        encoded = json.dumps(index, sort_keys=True, separators=(",", ":")).encode()
        if len(encoded) > LIMIT:
            raise ValueError("Index exceeds GitHub pack limit")
        (staging / "active.json").write_bytes(encoded)
        verify(staging, index)
        final = output / generation
        if final.exists():
            verify(final, index)
            return final
        staging.rename(final)
        return final
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def verify(folder, index, expected_hashes=None):
    folder = Path(folder)
    if folder.is_symlink() or (hasattr(folder, "is_junction") and folder.is_junction()):
        raise ValueError("Linked pack generation")
    if index.get("format") != 1 or not index.get("entries") or not index.get("packs"):
        raise ValueError("Invalid pack index")
    generation = index.get("generation", "")
    if not generation.startswith("v") or len(generation) != 25 or any(c not in "0123456789abcdef" for c in generation[1:]):
        raise ValueError("Invalid generation")
    packs = index["packs"]
    if expected_hashes is not None and set(expected_hashes) != set(index["entries"]):
        raise ValueError("Staged native asset paths differ from the pack generation")
    for name, (size, sha) in packs.items():
        if not re.fullmatch(r"pack[0-9]{5}\.pak", name) or size <= 0 or size > LIMIT:
            raise ValueError("Invalid pack name or size")
        data = no_links(folder, Path(name)).read_bytes()
        if len(data) != size or digest(data) != sha:
            raise ValueError(f"Pack checksum mismatch: {name}")
    for name, entry in index["entries"].items():
        asset_path(name)
        if len(entry) != 5:
            raise ValueError("Invalid entry")
        pack, offset, length, size, crc = entry
        if pack not in packs or not all(isinstance(n, int) for n in (offset, length, size)):
            raise ValueError("Invalid entry")
        if offset < 0 or length <= 0 or size < 0 or offset + length > packs[pack][0]:
            raise ValueError("Invalid entry bounds")
        with (folder / pack).open("rb") as stream:
            stream.seek(offset)
            compressed = stream.read(length)
        decoder = zlib.decompressobj()
        data = decoder.decompress(compressed, size + 1)
        if (len(data) != size or not decoder.eof or decoder.unused_data or
                signed_crc(data) != crc):
            raise ValueError(f"Asset checksum mismatch: {name}")
        if expected_hashes is not None and digest(data) != expected_hashes[name]:
            raise ValueError(f"Staged asset differs from pack: {name}")
    identity = json.dumps({"entries": index["entries"], "packs": packs}, sort_keys=True,
                          separators=(",", ":")).encode()
    if generation != "v" + digest(identity)[:24]:
        raise ValueError("Generation does not match contents")


def extract(generation, overlay, names):
    """Extract selected assets to a sparse overlay without overwriting files."""
    generation, overlay = Path(generation).resolve(), Path(overlay).resolve()
    index = json.loads((generation / "active.json").read_bytes())
    verify(generation, index)
    if not names or len(set(names)) != len(names):
        raise ValueError("Supply unique asset paths")
    targets = []
    for name in names:
        relative = asset_path(name)
        if name not in index["entries"]:
            raise ValueError(f"Asset not in pack: {name}")
        target = no_links(overlay, relative)
        if target.exists():
            raise FileExistsError(target)
        targets.append((name, target))
    for name, target in targets:
        entry = index["entries"][name]
        with (generation / entry[0]).open("rb") as source:
            source.seek(entry[1])
            data = zlib.decompress(source.read(entry[2]))
        target.parent.mkdir(parents=True, exist_ok=True)
        no_links(overlay, asset_path(name))
        with target.open("xb") as destination:
            destination.write(data)
    return len(targets)


def stage_compatible_release(manifest_path, generation, output, version, *,
                             staged_hashes=None, content_provider=None):
    """Stage pack additions while keeping every loose file in the release manifest."""
    manifest_path, generation, output = map(lambda p: Path(p).resolve(),
                                            (manifest_path, generation, output))
    if output.exists() or output == generation or generation in output.parents:
        raise ValueError("Release staging output must be a new directory outside the generation")
    manifest = json.loads(manifest_path.read_bytes())
    if not isinstance(manifest.get("files"), dict) or not isinstance(manifest.get("version"), int):
        raise ValueError("Invalid source release manifest")
    if version <= manifest["version"]:
        raise ValueError("Release version must increase")
    index = json.loads((generation / "active.json").read_bytes())
    verify(generation, index, staged_hashes)
    if generation.name != index["generation"]:
        raise ValueError("Generation directory name does not match index")
    files = dict(manifest["files"])
    prefix = "_tools/rpgcobo-tool/project/"
    required = ("_tools/rpgcobo-tool/boot.sk", prefix + "rt_pack.sk",
                prefix + "plugin/rokugan/RokuganUpdate.sk")
    for name in required:
        source = manifest_path.parent.joinpath(*PurePosixPath(name).parts)
        expected = files.get(name)
        if not expected or (content_provider is None and not source.is_file()):
            raise ValueError("Source manifest must contain pack-enabled boot, loader and updater")
        data = content_provider(name) if content_provider else source.read_bytes()
        if [signed_crc(data), len(data)] != [str(expected[0]), expected[1]]:
            raise ValueError(f"Pack integration differs from source manifest: {name}")
    tool_data = {}
    for name in CUTOVER_TOOLS:
        path = "tools/" + name
        expected = files.get(path)
        source = manifest_path.parent / "tools" / name
        if not expected or (content_provider is None and not source.is_file()):
            raise ValueError(f"Source manifest must contain cutover tool: {path}")
        data = content_provider(path) if content_provider else source.read_bytes()
        if [signed_crc(data), len(data)] != [str(expected[0]), expected[1]]:
            raise ValueError(f"Cutover tool differs from source manifest: {path}")
        tool_data[name] = data
    boot = required[0]
    boot_data = content_provider(boot) if content_provider else (
        manifest_path.parent / "_tools" / "rpgcobo-tool" / "boot.sk").read_bytes()
    if b'runsk("/rt_pack.sk")' not in boot_data:
        raise ValueError("Boot script does not enable the pack loader")
    updater_data = content_provider(required[2]) if content_provider else (
        manifest_path.parent.joinpath(*PurePosixPath(required[2]).parts).read_bytes())
    if b"updInstallPackIndex" not in updater_data:
        raise ValueError("Updater does not safely activate pack generations")
    mismatches = []
    for name, entry in index["entries"].items():
        existing = files.get(prefix + name)
        if not existing or str(existing[0]) != entry[4] or existing[1] != entry[3]:
            mismatches.append(name)
    if mismatches:
        raise ValueError("Loose release asset differs from pack or is not staged: "
                         + ", ".join(mismatches[:10]) + f" ({len(mismatches)} total)")
    pack_prefix = prefix + "rtpacks/"
    tool_prefix = "_tools/rpgcobo-tool/rtpack-tools/"
    files = {path: value for path, value in files.items()
             if not path.startswith(pack_prefix) and not path.startswith(tool_prefix)}
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = extended_path(output.parent) / (".rt-release-" + uuid.uuid4().hex)
    staging.mkdir()
    try:
        root = staging / "_tools" / "rpgcobo-tool" / "project" / "rtpacks"
        target = root / index["generation"]
        target.mkdir(parents=True)
        for name in index["packs"]:
            shutil.copyfile(generation / name, target / name)
        shutil.copyfile(generation / "active.json", root / "active.json")
        verify(target, index)
        tool_root = staging / "_tools" / "rpgcobo-tool" / "rtpack-tools"
        tool_root.mkdir()
        for name, data in tool_data.items():
            (tool_root / name).write_bytes(data)
        loader_data = content_provider(required[1]) if content_provider else (
            manifest_path.parent.joinpath(*PurePosixPath(required[1]).parts).read_bytes())
        (tool_root / "loader.sha256").write_text(digest(loader_data), encoding="ascii")
        (tool_root / "README.txt").write_text(CUTOVER_README, encoding="utf-8")
        for path in [root / "active.json", *target.glob("*.pak"), *tool_root.iterdir()]:
            data = path.read_bytes()
            files[path.relative_to(staging).as_posix()] = [signed_crc(data), len(data)]
        encoded = json.dumps({"version": version, "files": files}, sort_keys=True,
                             separators=(",", ":")).encode()
        if len(encoded) > LIMIT:
            raise ValueError("Release manifest exceeds GitHub pack limit")
        (staging / "rt_manifest.json").write_bytes(encoded)
        (staging / "version.json").write_text(json.dumps({
            "version": version, "date": datetime.date.today().isoformat()
        }), encoding="utf-8")
        staging.rename(output)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return output


def apply_compatible_overlay(stage, candidate, *, staged_hashes=None):
    """Apply a prepared overlay to a release candidate, without deleting loose assets."""
    stage, candidate = extended_path(stage), extended_path(candidate)
    prefix = Path("_tools") / "rpgcobo-tool" / "project"
    pack_root = stage / prefix / "rtpacks"
    encoded = (pack_root / "active.json").read_bytes()
    index = json.loads(encoded)
    generation = pack_root / index["generation"]
    verify(generation, index, staged_hashes)
    manifest = json.loads((stage / "rt_manifest.json").read_bytes())
    version = json.loads((stage / "version.json").read_bytes())
    if manifest.get("version") != version.get("version"):
        raise ValueError("Overlay version mismatch")
    no_links(candidate, prefix)
    if staged_hashes is None:
        for name in ("_tools/rpgcobo-tool/boot.sk", "_tools/rpgcobo-tool/project/rt_pack.sk",
                     "_tools/rpgcobo-tool/project/plugin/rokugan/RokuganUpdate.sk"):
            data = no_links(candidate, Path(*PurePosixPath(name).parts)).read_bytes()
            if manifest["files"].get(name) != [signed_crc(data), len(data)]:
                raise ValueError(f"Candidate pack integration changed: {name}")
        for name in CUTOVER_TOOLS:
            relative = "tools/" + name
            data = no_links(candidate, Path("tools") / name).read_bytes()
            if manifest["files"].get(relative) != [signed_crc(data), len(data)]:
                raise ValueError(f"Candidate cutover tool changed: {name}")
        for name, entry in index["entries"].items():
            path = no_links(candidate / prefix, asset_path(name))
            data = path.read_bytes()
            with (generation / entry[0]).open("rb") as stream:
                stream.seek(entry[1])
                expected = zlib.decompress(stream.read(entry[2]))
            if data != expected:
                raise ValueError(f"Candidate asset differs from pack: {name}")
    tool_root = stage / "_tools" / "rpgcobo-tool" / "rtpack-tools"
    expected_tools = [tool_root / name for name in (*CUTOVER_TOOLS, "loader.sha256", "README.txt")]
    for path in [pack_root / "active.json", *generation.glob("*.pak"), *expected_tools]:
        relative = path.relative_to(stage).as_posix()
        data = path.read_bytes()
        if manifest["files"].get(relative) != [signed_crc(data), len(data)]:
            raise ValueError(f"Overlay manifest mismatch: {relative}")
    root = no_links(candidate / prefix, Path("rtpacks"))
    root.mkdir(exist_ok=True)
    target = no_links(root, Path(index["generation"]))
    if target.exists():
        verify(target, index)
    else:
        temp = root / (".copying-" + uuid.uuid4().hex)
        try:
            shutil.copytree(generation, temp)
            verify(temp, index)
            temp.rename(target)
        finally:
            if temp.exists():
                shutil.rmtree(temp)
    candidate_tools = no_links(candidate, Path("_tools") / "rpgcobo-tool" / "rtpack-tools")
    candidate_tools.mkdir(exist_ok=True)
    replacements = [(path, candidate_tools / path.name) for path in expected_tools]
    replacements.extend(((pack_root / "active.json", root / "active.json"),
                           (stage / "rt_manifest.json", candidate / "rt_manifest.json"),
                           (stage / "version.json", candidate / "version.json")))
    for source, target in replacements:
        if target.is_symlink() or (hasattr(target, "is_junction") and target.is_junction()):
            raise ValueError(f"Linked release target: {target}")
        temp = target.with_name("." + target.name + "-" + uuid.uuid4().hex)
        try:
            shutil.copyfile(source, temp)
            os.replace(temp, target)
        finally:
            if temp.exists():
                temp.unlink()


def checked_profile(profile):
    if os.name != "nt":
        raise ValueError("Cannot verify that the Windows test profile is stopped")
    import traveler_instances
    metadata = traveler_instances.metadata(profile)
    traveler_instances.require_separate(Path(metadata["source"]).resolve(), profile)
    project = profile / "project"
    if project.is_symlink() or (hasattr(project, "is_junction") and project.is_junction()):
        raise ValueError("Linked project is not an isolated profile")
    loader = project / "rt_pack.sk"
    boot = profile / "boot.sk"
    expected = Path(__file__).resolve().parents[1] / "_tools" / "rpgcobo-tool" / "project" / "rt_pack.sk"
    if (not loader.is_file() or loader.read_bytes() != expected.read_bytes() or
            not boot.is_file() or b'runsk("/rt_pack.sk")' not in boot.read_bytes()):
        raise ValueError("Profile lacks the matching pack loader; provision a fresh profile")
    return traveler_instances


def enable_test_profile(profile):
    profile = Path(profile).resolve()
    if not (profile / "rpgcobo.exe").is_file():
        raise ValueError("Missing isolated runtime")
    instances = checked_profile(profile)
    with instances.hold_slot(profile):
        instances.assert_closed(profile)
        (profile / MARKER).touch(exist_ok=True)


def install(profile, source, prune=False, _allow_fixture=False):
    """Activate a fully verified generation in a marked, stopped test profile."""
    profile, source = Path(profile).resolve(), Path(source).resolve()
    if not (profile / MARKER).is_file():
        raise ValueError("Not a marked isolated test profile")
    if (profile / "rpgcobo.exe").exists():
        instances = checked_profile(profile)
        with instances.hold_slot(profile):
            instances.assert_closed(profile)
            return _install_stopped(profile, source, prune)
    if not _allow_fixture:
        raise ValueError("Missing isolated runtime")
    return _install_stopped(profile, source, prune)


def _install_stopped(profile, source, prune):
    project = profile / "project"
    if (not (project / "sakana.proj").is_file() or project.is_symlink() or
            (hasattr(project, "is_junction") and project.is_junction())):
        raise ValueError("Missing or linked project")
    index = json.loads((source / "active.json").read_bytes())
    verify(source, index)
    target = project / "rtpacks"
    if target.is_symlink() or (hasattr(target, "is_junction") and target.is_junction()):
        raise ValueError("Linked pack directory")
    target.mkdir(exist_ok=True)
    old_index = None
    active = target / "active.json"
    if active.is_symlink():
        raise ValueError("Linked active index")
    if active.is_file():
        old_index = json.loads(active.read_bytes())
        if not re.fullmatch(r"v[0-9a-f]{24}", old_index.get("generation", "")):
            raise ValueError("Invalid previous generation")
        verify(no_links(target, Path(old_index["generation"])), old_index)
    generation = no_links(target, Path(index["generation"]))
    if generation.exists():
        verify(generation, index)
    else:
        staging = target / (".installing-" + uuid.uuid4().hex)
        staging.mkdir()
        try:
            for name in index["packs"]:
                shutil.copyfile(source / name, staging / name)
            verify(staging, index)
            staging.rename(generation)
        finally:
            if staging.exists():
                shutil.rmtree(staging)
    temp = target / (".active-" + uuid.uuid4().hex)
    try:
        temp.write_bytes(json.dumps(index, sort_keys=True, separators=(",", ":")).encode())
        os.replace(temp, active)
    finally:
        if temp.exists():
            temp.unlink()
    removed = 0
    if prune:
        names = set(index["entries"])
        if old_index:
            names.update(old_index["entries"])
        for name in sorted(names):
            path = no_links(project, asset_path(name))
            if not path.is_file():
                continue
            local = path.read_bytes()
            candidates = []
            if name in index["entries"]:
                candidates.append((generation, index["entries"][name]))
            if old_index and name in old_index["entries"]:
                candidates.append((target / old_index["generation"], old_index["entries"][name]))
            matches = False
            for directory, candidate in candidates:
                with (directory / candidate[0]).open("rb") as stream:
                    stream.seek(candidate[1])
                    unpacked = zlib.decompress(stream.read(candidate[2]))
                if local == unpacked:
                    matches = True
                    break
            if matches:
                path.unlink()
                removed += 1
    return removed


def update_from_url(profile, index_url, prune=False, allow_http_loopback=False, _allow_fixture=False):
    """Fetch and verify an immutable set before activating it in a test profile."""
    profile = Path(profile).resolve()
    if not (profile / MARKER).is_file():
        raise ValueError("Not a marked isolated test profile")
    parsed = urllib.parse.urlsplit(index_url)
    if (parsed.username or parsed.password or parsed.query or parsed.fragment or
            not parsed.hostname or not parsed.path.endswith("/active.json")):
        raise ValueError("Expected an active.json URL without credentials, query, or fragment")
    if parsed.scheme != "https" and not (
            allow_http_loopback and parsed.scheme == "http" and
            parsed.hostname in ("127.0.0.1", "::1", "localhost")):
        raise ValueError("HTTPS is required")
    origin = (parsed.scheme, parsed.hostname, parsed.port)

    class SameOriginRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            target = urllib.parse.urlsplit(newurl)
            if (target.scheme, target.hostname, target.port) != origin:
                raise ValueError("Cross-origin or insecure redirect")
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    opener = urllib.request.build_opener(SameOriginRedirect())

    def download(url, limit, destination=None, expected=None):
        request = urllib.request.Request(url, headers={"Accept-Encoding": "identity"})
        try:
            response = opener.open(request, timeout=30)
        except urllib.error.HTTPError as error:
            error.close()
            raise
        with response:
            final = urllib.parse.urlsplit(response.geturl())
            if (final.scheme, final.hostname, final.port) != origin:
                raise ValueError("Cross-origin or insecure redirect")
            total, hasher, chunks = 0, hashlib.sha256(), []
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > limit:
                    raise ValueError("Download exceeds allowed size")
                hasher.update(chunk)
                if destination is None:
                    chunks.append(chunk)
                else:
                    destination.write(chunk)
            if expected and (total != expected[0] or hasher.hexdigest() != expected[1]):
                raise ValueError("Downloaded pack checksum mismatch")
            return b"".join(chunks)

    encoded = download(index_url, LIMIT)
    index = json.loads(encoded)
    generation = index.get("generation", "")
    packs = index.get("packs")
    if (index.get("format") != 1 or not re.fullmatch(r"v[0-9a-f]{24}", generation)
            or not isinstance(packs, dict) or not packs):
        raise ValueError("Invalid pack index")
    for name, metadata in packs.items():
        if (not re.fullmatch(r"pack[0-9]{5}\.pak", name)
                or not isinstance(metadata, list) or len(metadata) != 2
                or not isinstance(metadata[0], int) or not 0 < metadata[0] <= LIMIT
                or not isinstance(metadata[1], str)
                or not re.fullmatch(r"[0-9a-f]{64}", metadata[1])):
            raise ValueError("Invalid pack metadata")
    reusable = {}
    try:
        pack_root = no_links(profile, Path("project") / "rtpacks")
        active = no_links(pack_root, Path("active.json"))
        prior = json.loads(active.read_bytes())
        old_generation = prior.get("generation", "")
        if re.fullmatch(r"v[0-9a-f]{24}", old_generation):
            for name, info in prior.get("packs", {}).items():
                if (re.fullmatch(r"pack[0-9]{5}\.pak", name)
                        and isinstance(info, list) and len(info) == 2):
                    reusable[(info[0], info[1])] = no_links(pack_root, Path(old_generation) / name)
    except (OSError, ValueError, TypeError):
        pass

    staging = profile / (".rt-pack-download-" + uuid.uuid4().hex)
    staging.mkdir()
    try:
        (staging / "active.json").write_bytes(encoded)
        for name, metadata in packs.items():
            target = staging / name
            previous = reusable.get(tuple(metadata))
            reused = False
            if previous:
                try:
                    hasher, size = hashlib.sha256(), 0
                    with previous.open("rb") as source, target.open("wb") as stream:
                        while True:
                            chunk = source.read(1024 * 1024)
                            if not chunk:
                                break
                            size += len(chunk)
                            if size > metadata[0]:
                                break
                            hasher.update(chunk)
                            stream.write(chunk)
                    reused = size == metadata[0] and hasher.hexdigest() == metadata[1]
                except OSError:
                    reused = False
            if not reused:
                url = urllib.parse.urljoin(index_url, name)
                with target.open("wb") as stream:
                    download(url, metadata[0], stream, metadata)
        return install(profile, staging, prune, _allow_fixture)
    finally:
        shutil.rmtree(staging)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    builder = commands.add_parser("build")
    builder.add_argument("project")
    builder.add_argument("output")
    builder.add_argument("--previous", help="previous verified generation directory")
    builder.add_argument("--overlay", action="store_true", help="retain unmentioned assets from previous")
    builder.add_argument("--remove-list", help="UTF-8 file of resource paths to remove, one per line")
    extractor = commands.add_parser("extract")
    extractor.add_argument("generation")
    extractor.add_argument("overlay")
    extractor.add_argument("assets", nargs="+", help="resource-relative asset paths")
    release = commands.add_parser("stage-compatible-release")
    release.add_argument("manifest", help="release manifest for matching loose assets and pack-enabled code")
    release.add_argument("generation")
    release.add_argument("output", help="new directory for the release overlay")
    release.add_argument("--version", type=int, required=True)
    enable = commands.add_parser("enable-test-profile")
    enable.add_argument("profile")
    installer = commands.add_parser("install-test-profile")
    installer.add_argument("profile")
    installer.add_argument("source")
    installer.add_argument("--prune-matching", action="store_true")
    updater = commands.add_parser("update-test-profile")
    updater.add_argument("profile")
    updater.add_argument("index_url")
    updater.add_argument("--prune-matching", action="store_true")
    args = parser.parse_args()
    if args.command == "build":
        removed = []
        if args.remove_list:
            removed = [line.strip() for line in Path(args.remove_list).read_text(encoding="utf-8").splitlines()
                       if line.strip() and not line.lstrip().startswith("#")]
        print(build(args.project, args.output, previous=args.previous, overlay=args.overlay, remove=removed))
    elif args.command == "extract":
        print(f"Extracted {extract(args.generation, args.overlay, args.assets)} assets")
    elif args.command == "stage-compatible-release":
        print(stage_compatible_release(args.manifest, args.generation, args.output, args.version))
    elif args.command == "enable-test-profile":
        enable_test_profile(args.profile)
        print("Enabled packs in the stopped, independent profile")
    elif args.command == "install-test-profile":
        print(f"Activated test generation; removed {install(args.profile, args.source, args.prune_matching)} matching loose files")
    else:
        print(f"Activated test generation; removed {update_from_url(args.profile, args.index_url, args.prune_matching)} matching loose files")


if __name__ == "__main__":
    main()
