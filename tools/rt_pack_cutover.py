"""Recoverable, explicitly invoked cutover of a stopped Windows game installation."""
import argparse
from contextlib import contextmanager
import ctypes
import json
import msvcrt
import os
from pathlib import Path
import re
import stat
import sys
import uuid

if sys.version_info < (3, 12):
    raise SystemExit("Pack cleanup requires Python 3.12 or newer")

import rt_packs
import traveler_instances


@contextmanager
def exclusive(path, delete=False):
    """Keep the Windows file locked against other opens, replacement and deletion."""
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateFileW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32,
                                  ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32,
                                  ctypes.c_void_p]
    kernel.CreateFileW.restype = ctypes.c_void_p
    handle = kernel.CreateFileW(str(path), 0x80000000 | (0x10000 if delete else 0),
                                0, None, 3, 0x00200000, None)
    if handle == ctypes.c_void_p(-1).value:
        raise OSError(ctypes.get_last_error(), f"Cannot exclusively open {path}")
    try:
        fd = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
    except Exception:
        kernel.CloseHandle(ctypes.c_void_p(handle))
        raise
    with os.fdopen(fd, "rb") as stream:
        yield stream


def delete_locked(stream):
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.SetFileInformationByHandle.argtypes = [ctypes.c_void_p, ctypes.c_int,
                                                  ctypes.c_void_p, ctypes.c_uint32]
    kernel.SetFileInformationByHandle.restype = ctypes.c_int
    disposition = ctypes.c_ubyte(1)
    handle = ctypes.c_void_p(msvcrt.get_osfhandle(stream.fileno()))
    if not kernel.SetFileInformationByHandle(handle, 4, ctypes.byref(disposition), 1):
        raise OSError(ctypes.get_last_error(), "Cannot delete locked quarantine file")


@contextmanager
def stopped(profile):
    profile = rt_packs.extended_path(profile)
    exe = rt_packs.no_links(profile, Path("rpgcobo.exe"))
    boot = rt_packs.no_links(profile, Path("boot.sk"))
    loader = rt_packs.no_links(profile, Path("project") / "rt_pack.sk")
    bundle_hash = Path(__file__).resolve().parent / "loader.sha256"
    if bundle_hash.is_file():
        expected_hash = bundle_hash.read_text(encoding="ascii").strip()
    else:
        expected = Path(__file__).resolve().parents[1] / "_tools" / "rpgcobo-tool" / "project" / "rt_pack.sk"
        expected_hash = rt_packs.digest(expected.read_bytes())
    if (not exe.is_file() or not boot.is_file() or b'runsk("/rt_pack.sk")' not in boot.read_bytes()
            or not loader.is_file() or rt_packs.digest(loader.read_bytes()) != expected_hash):
        raise ValueError("Installation does not have the matching pack-enabled runtime")
    rt_packs.no_links(profile, Path("project") / "rtpacks")
    with traveler_instances.hold_slot(profile):
        traveler_instances.assert_closed(profile)
        with exclusive(exe):
            yield profile


def read_index(profile):
    root = profile / "project" / "rtpacks"
    active = rt_packs.no_links(root, Path("active.json"))
    encoded = active.read_bytes()
    index = json.loads(encoded)
    generation = rt_packs.no_links(root, Path(index.get("generation", "")))
    rt_packs.verify(generation, index)
    if active.read_bytes() != encoded:
        raise ValueError("Active pack changed during validation")
    return index, encoded, generation


def packed_bytes(folder, entry):
    import zlib
    with (folder / entry[0]).open("rb") as stream:
        stream.seek(entry[1])
        return zlib.decompress(stream.read(entry[2]))


def read_stable(path):
    with exclusive(path) as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise ValueError(f"Not an independent regular file: {path}")
        data = stream.read()
        after = os.fstat(stream.fileno())
        if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
                after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise ValueError(f"File changed while read: {path}")
        return data


def write_new(path, data):
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def transaction(profile, ident, verify_pack=True):
    if not isinstance(ident, str) or len(ident) != 32 or any(c not in "0123456789abcdef" for c in ident):
        raise ValueError("Invalid transaction ID")
    root = rt_packs.no_links(profile, Path(".rt-pack-transactions") / ident)
    manifest = json.loads((root / "journal.json").read_bytes())
    if manifest.get("format") != 1 or manifest.get("id") != ident or not isinstance(manifest.get("files"), dict):
        raise ValueError("Invalid cutover journal")
    index = json.loads((root / "index.json").read_bytes())
    if not re.fullmatch(r"v[0-9a-f]{24}", index.get("generation", "")):
        raise ValueError("Invalid journal generation")
    generation = rt_packs.no_links(profile / "project" / "rtpacks", Path(index["generation"]))
    if verify_pack:
        rt_packs.verify(generation, index)
    for name, sha in manifest["files"].items():
        rt_packs.asset_path(name)
        if name not in index["entries"] or not isinstance(sha, str) or len(sha) != 64:
            raise ValueError("Invalid cutover entry")
    return root, manifest, index, generation


def prepare(profile, *, exclude=()):
    excluded = set(exclude)
    for name in excluded:
        rt_packs.asset_path(name)
    with stopped(profile) as profile:
        index, encoded, generation = read_index(profile)
        files = {}
        for name, entry in sorted(index["entries"].items()):
            if name in excluded:
                continue
            target = rt_packs.no_links(profile / "project", rt_packs.asset_path(name))
            if not target.is_file():
                continue
            data = read_stable(target)
            if len(data) == entry[3] and rt_packs.signed_crc(data) == entry[4] and data == packed_bytes(generation, entry):
                files[name] = rt_packs.digest(data)
        if not files:
            raise ValueError("No matching loose files to cut over")
        if (profile / "project" / "rtpacks" / "active.json").read_bytes() != encoded:
            raise ValueError("Active pack changed while preparing cutover")
        ident = uuid.uuid4().hex
        root = rt_packs.no_links(profile, Path(".rt-pack-transactions") / ident)
        root.mkdir(parents=True)
        write_new(root / "index.json", encoded)
        write_new(root / "journal.json", json.dumps({
            "format": 1, "id": ident, "files": files
        }, sort_keys=True, separators=(",", ":")).encode())
        return ident, len(files)


def apply(profile, ident):
    moved = 0
    with stopped(profile) as profile:
        root, journal, index, generation = transaction(profile, ident)
        active, _, _ = read_index(profile)
        if active["generation"] != index["generation"]:
            raise ValueError("Active pack changed; prepare a new cutover")
        for name, sha in journal["files"].items():
            relative = rt_packs.asset_path(name)
            source = rt_packs.no_links(profile / "project", relative)
            backup = rt_packs.no_links(root / "loose", relative)
            if backup.exists() or not source.is_file():
                continue
            data = read_stable(source)
            if rt_packs.digest(data) != sha or data != packed_bytes(generation, index["entries"][name]):
                continue
            backup.parent.mkdir(parents=True, exist_ok=True)
            rt_packs.no_links(root / "loose", relative)
            os.rename(source, backup)
            if rt_packs.digest(read_stable(backup)) != sha:
                if not source.exists():
                    os.rename(backup, source)
                raise ValueError(f"File changed during cutover; retained: {name}")
            moved += 1
    return moved


def seal(profile, ident):
    """Discard verified quarantined duplicates; the retained pack is the backup."""
    removed = 0
    with stopped(profile) as profile:
        root, journal, index, generation = transaction(profile, ident)
        for name, sha in journal["files"].items():
            relative = rt_packs.asset_path(name)
            backup = rt_packs.no_links(root / "loose", relative)
            if not backup.is_file():
                continue
            with exclusive(backup, delete=True) as stream:
                info = os.fstat(stream.fileno())
                if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                    raise ValueError(f"Not an independent regular file: {backup}")
                data = stream.read()
                if rt_packs.digest(data) != sha or data != packed_bytes(generation, index["entries"][name]):
                    raise ValueError(f"Quarantined file changed; retained: {name}")
                delete_locked(stream)
                removed += 1
    return removed


def restore(profile, ident):
    restored, conflicts = 0, []
    with stopped(profile) as profile:
        root, journal, index, generation = transaction(profile, ident, verify_pack=False)
        try:
            rt_packs.verify(generation, index)
            pack_ok = True
        except (OSError, ValueError):
            pack_ok = False
        for name, sha in journal["files"].items():
            relative = rt_packs.asset_path(name)
            target = rt_packs.no_links(profile / "project", relative)
            backup = rt_packs.no_links(root / "loose", relative)
            if target.exists():
                conflicts.append(name)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            rt_packs.no_links(profile / "project", relative)
            if backup.is_file():
                try:
                    os.rename(backup, target)
                except FileExistsError:
                    conflicts.append(name)
                    continue
            else:
                if not pack_ok:
                    conflicts.append(name)
                    continue
                data = packed_bytes(generation, index["entries"][name])
                if rt_packs.digest(data) != sha:
                    raise ValueError(f"Pack no longer matches journal: {name}")
                temp = root / ("restore-" + uuid.uuid4().hex)
                try:
                    write_new(temp, data)
                    try:
                        os.rename(temp, target)
                    except FileExistsError:
                        conflicts.append(name)
                        continue
                finally:
                    if temp.exists():
                        temp.unlink()
            restored += 1
    return restored, conflicts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("prepare", "apply", "seal", "restore"))
    parser.add_argument("profile", help="stopped game installation")
    parser.add_argument("transaction", nargs="?")
    args = parser.parse_args()
    if args.operation == "prepare":
        if args.transaction:
            parser.error("prepare does not take a transaction")
        ident, count = prepare(args.profile)
        print(f"Prepared {ident}: {count} matching files")
    else:
        if not args.transaction:
            parser.error("transaction ID required")
        print(globals()[args.operation](args.profile, args.transaction))


if __name__ == "__main__":
    main()
