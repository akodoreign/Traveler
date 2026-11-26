"""Create and run independent native Traveler playtest windows on Windows."""

import argparse
from contextlib import contextmanager
import ctypes as ct
from ctypes import wintypes as w
from datetime import datetime, timezone
from hashlib import sha256
import json
import msvcrt
import os
from pathlib import Path
import re
import shutil
import subprocess

DEFAULT_TOOL = Path(__file__).resolve().parents[1] / "_tools" / "rpgcobo-tool"
LOCAL_DATA = Path(os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData" / "Local"))
DEFAULT_PROFILES = LOCAL_DATA / "RokuganTraveler" / "Instances"

FILES = ("rpgcobo.exe", "sakanagl.dll", "boot.sk")
RUNTIME_TREES = ("project", "addon", "tools", "util")
WRITABLE_DIRS = ("savedata", "tmp", "tmp/rt_shot", "log", "backup", "build", "work", "os-temp", "roaming", "local")


def instance_id(directory):
    """The checked rpgcobo.exe build's path-scoped -testplay window ID."""
    path = str(directory).encode("utf-16le")
    value = 0x811C9DC5
    for start in range(0, len(path), 2):
        value ^= int.from_bytes(path[start:start + 2], "little")
        value = value * 0x01000193 & 0xFFFFFFFF
    return ((value ^ 0x91236109) + 1) & 0xFFFFFFFF


def copy_tree(source, target):
    proc = subprocess.run(
        ["robocopy.exe", str(source), str(target), "/E", "/XJ", "/COPY:DAT", "/DCOPY:DAT",
         "/MT:12", "/R:2", "/W:1", "/NP", "/NFL", "/NDL"],
        capture_output=True, text=True, errors="replace", check=False,
    )
    if proc.returncode >= 8:
        raise RuntimeError(f"Copy of {source.name} failed with robocopy status {proc.returncode}\n{proc.stdout}\n{proc.stderr}")


def slot_path(profile_root, slot):
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,30}", slot):
        raise ValueError("A slot uses lower-case letters, digits and hyphens.")
    if profile_root.is_symlink() or profile_root.is_junction():
        raise ValueError("Profile root must be a local directory.")
    target = profile_root.resolve() / slot
    if target.is_symlink() or target.is_junction():
        raise ValueError("A slot must be an independent local directory.")
    return target


def ensure_state(target):
    for directory in WRITABLE_DIRS:
        folder = target / directory
        if folder.is_symlink() or folder.is_junction():
            raise ValueError(f"Shared writable directory is not allowed: {folder}")
        folder.mkdir(exist_ok=True)


def require_separate(source, target):
    if source == target or source.is_relative_to(target) or target.is_relative_to(source):
        raise ValueError("Source and instance must be separate directories.")


def sync_runtime(source, target):
    require_separate(source, target)
    for name in FILES:
        path = target / name
        if path.is_symlink() or (path.exists() and path.stat().st_nlink > 1):
            raise ValueError(f"Runtime file is not independent: {path}")
    for folder in RUNTIME_TREES:
        path = target / folder
        if path.is_symlink() or path.is_junction():
            raise ValueError(f"Runtime folder is not independent: {path}")
    ensure_state(target)
    # The launcher requires a completed manifest, so a failed sync cannot silently launch a mixed snapshot.
    manifest = target / "profile.json"
    marker = target / ".sync-in-progress"
    marker.touch()
    hashes = {}
    for filename in FILES:
        original, copy = source / filename, target / filename
        shutil.copy2(original, copy)
        hashes[filename] = sha256(copy.read_bytes()).hexdigest()
        assert hashes[filename] == sha256(original.read_bytes()).hexdigest()
    for folder in RUNTIME_TREES:
        if (source / folder).is_dir():
            copy_tree(source / folder, target / folder)
    assert (target / "project/testplay.sk").is_file()
    assert (target / "project/sakana.proj").is_file()
    assert (target / "project/data/map.json").is_file()
    exe_id = instance_id(target)
    assert exe_id != instance_id(source)
    data = {"source": str(source), "profile": str(target), "testplay_window_id": f"0x{exe_id:08x}",
            "sha256": hashes, "writable_directories": WRITABLE_DIRS}
    manifest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    marker.unlink()
    return data


def prepare(source, slot, profile_root=DEFAULT_PROFILES):
    target = slot_path(profile_root, slot)
    require_separate(source, target)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.mkdir()
    return sync_runtime(source, target)


class ProcessEntry(ct.Structure):
    _fields_ = [
        ("size", w.DWORD), ("usage", w.DWORD), ("pid", w.DWORD),
        ("heap", ct.c_size_t), ("module", w.DWORD), ("threads", w.DWORD),
        ("parent", w.DWORD), ("priority", w.LONG), ("flags", w.DWORD), ("name", w.WCHAR * 260),
    ]


def process_ids(image_name):
    """Find process IDs directly through Toolhelp, independent of shell visibility."""
    kernel = ct.WinDLL("kernel32", use_last_error=True)
    kernel.CreateToolhelp32Snapshot.argtypes = (w.DWORD, w.DWORD)
    kernel.CreateToolhelp32Snapshot.restype = w.HANDLE
    kernel.CloseHandle.argtypes = (w.HANDLE,)
    for call in (kernel.Process32FirstW, kernel.Process32NextW):
        call.argtypes = (w.HANDLE, ct.POINTER(ProcessEntry))
        call.restype = w.BOOL
    snapshot = kernel.CreateToolhelp32Snapshot(2, 0)  # TH32CS_SNAPPROCESS
    if snapshot == ct.c_void_p(-1).value:
        raise ct.WinError(ct.get_last_error())
    try:
        result = []
        item = ProcessEntry(size=ct.sizeof(ProcessEntry))
        ok = kernel.Process32FirstW(snapshot, ct.byref(item))
        while ok:
            if item.name.casefold() == image_name.casefold():
                result.append(item.pid)
            ok = kernel.Process32NextW(snapshot, ct.byref(item))
        if ct.get_last_error() not in (0, 18):  # ERROR_NO_MORE_FILES
            raise ct.WinError(ct.get_last_error())
        return result
    finally:
        kernel.CloseHandle(snapshot)


def process_image(pid):
    kernel = ct.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = (w.DWORD, w.BOOL, w.DWORD)
    kernel.OpenProcess.restype = w.HANDLE
    kernel.CloseHandle.argtypes = (w.HANDLE,)
    kernel.QueryFullProcessImageNameW.argtypes = (w.HANDLE, w.DWORD, w.LPWSTR, ct.POINTER(w.DWORD))
    image = ct.create_unicode_buffer(32768)
    process = kernel.OpenProcess(0x1000, False, pid)
    if process:
        try:
            size = w.DWORD(len(image))
            kernel.QueryFullProcessImageNameW(process, 0, image, ct.byref(size))
        finally:
            kernel.CloseHandle(process)
    return image.value


def windows():
    user = ct.WinDLL("user32", use_last_error=True)
    callback = ct.WINFUNCTYPE(w.BOOL, w.HWND, w.LPARAM)
    user.GetPropW.argtypes = (w.HWND, w.LPCWSTR)
    user.GetPropW.restype = w.HANDLE
    user.GetWindowThreadProcessId.argtypes = (w.HWND, ct.POINTER(w.DWORD))
    user.GetWindowTextW.argtypes = (w.HWND, w.LPWSTR, ct.c_int)
    user.IsWindowVisible.argtypes = (w.HWND,)
    user.EnumWindows.argtypes = (callback, w.LPARAM)
    found = []

    @callback
    def collect(hwnd, _):
        value = user.GetPropW(hwnd, "sakana-id")
        if value:
            pid = w.DWORD()
            title = ct.create_unicode_buffer(512)
            user.GetWindowThreadProcessId(hwnd, ct.byref(pid))
            user.GetWindowTextW(hwnd, title, len(title))
            found.append({"hwnd": f"0x{hwnd:x}", "pid": pid.value, "window_id": f"0x{value & 0xffffffff:08x}",
                          "title": title.value, "visible": bool(user.IsWindowVisible(hwnd)),
                          "executable": process_image(pid.value)})
        return True

    user.EnumWindows(collect, 0)
    return found


@contextmanager
def hold_slot(target):
    with (target / ".traveler-slot.lock").open("a+b") as lock:
        lock.seek(0, os.SEEK_END)
        if lock.tell() == 0:
            lock.write(b"\0")
            lock.flush()
        lock.seek(0)
        try:
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError as exc:
            raise RuntimeError(f"Instance {target.name} is already launching, running or syncing.") from exc
        try:
            yield
        finally:
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)


def metadata(target, allow_pending=False):
    if not allow_pending and (target / ".sync-in-progress").exists():
        raise RuntimeError(f"Finish syncing {target.name} before launching it.")
    data = json.loads((target / "profile.json").read_bytes())
    if Path(data["profile"]).resolve() != target:
        raise ValueError("This profile has been moved. Provision a slot at the new location.")
    return data


def assert_closed(target):
    exe = target / "rpgcobo.exe"
    identifier = instance_id(target)
    ids = {identifier, (identifier - 1) & 0xFFFFFFFF}  # isolated player and editor IDs
    for window in windows():
        if int(window["window_id"], 16) in ids:
            raise RuntimeError(f"Instance {target.name} is running as PID {window['pid']}. Close it before syncing.")
    try:
        candidates = process_ids(exe.name)
    except OSError:
        candidates = ()
    for pid in candidates:
        image = process_image(pid)
        if image and Path(image).resolve() == exe:
            raise RuntimeError(f"Instance {target.name} is running as PID {pid}. Close it before syncing.")
    # Windows denies write opens for a mapped executable. This probes the actual slot even when a process
    # cannot be interrogated and hasn't reached native window creation. No bytes are changed.
    if exe.exists():
        try:
            with exe.open("r+b"):
                pass
        except OSError as exc:
            raise RuntimeError(f"Cannot write the {target.name} executable. Close its window before syncing.") from exc


def launch_plan(target, game_args):
    game_args = list(game_args)
    if game_args and game_args[0] == "--":
        game_args = game_args[1:]
    if game_args and game_args[0].casefold() == "-testplay":
        game_args = game_args[1:]
    env = os.environ.copy()
    scoped = {key: str(target / folder) for key, folder in (
        ("TMP", "os-temp"), ("TEMP", "os-temp"), ("APPDATA", "roaming"), ("LOCALAPPDATA", "local"))}
    env.update(scoped)
    return [str(target / "rpgcobo.exe"), "-testplay", *game_args], env, scoped


def launch(target, game_args, dry_run=False):
    compiled = metadata(target)
    exe = target / "rpgcobo.exe"
    if sha256(exe.read_bytes()).hexdigest() != compiled["sha256"][exe.name]:
        raise RuntimeError("The isolated binary differs from its provisioned runtime. Sync before launching.")
    args, env, scoped = launch_plan(target, game_args)
    if dry_run:
        print(json.dumps({"args": args, "cwd": str(target), "game_environment": scoped,
                          "testplay_window_id": f"0x{instance_id(target):08x}"}, indent=2))
        return 0
    with hold_slot(target):
        # Check again inside the lock, in case a sync started after planning this launch.
        metadata(target)
        ensure_state(target)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        logpath = target / "log" / f"launch-{stamp}-{os.getpid()}.log"
        with logpath.open("xb") as log:
            child = subprocess.Popen(args, cwd=target, env=env, stdout=log, stderr=subprocess.STDOUT)
            print(f"Traveler {target.name} is PID {child.pid}. Log: {logpath}", flush=True)
            code = child.wait()
        if code == 7:
            print(f"RPG-Cobo found an existing window for this native slot ({instance_id(target):08x}).")
        elif code:
            print(f"RPG-Cobo returned {code}. See {logpath}.")
        return code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profiles", type=Path, default=DEFAULT_PROFILES)
    commands = parser.add_subparsers(dest="action", required=True)
    create = commands.add_parser("provision", help="copy a clean independent instance")
    create.add_argument("slot")
    create.add_argument("--tool", type=Path, default=DEFAULT_TOOL, help="source _tools/rpgcobo-tool directory")
    sync = commands.add_parser("sync", help="refresh assets from the recorded or supplied tool directory")
    sync.add_argument("slot")
    sync.add_argument("--tool", type=Path)
    info = commands.add_parser("info", help="show the isolated locations and native window ID")
    info.add_argument("slot")
    run = commands.add_parser("launch", help="open a visible testplay window")
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("slot")
    run.add_argument("game_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    target = slot_path(args.profiles, args.slot)
    try:
        if args.action == "provision":
            data = prepare(args.tool.resolve(strict=True), args.slot, args.profiles)
        elif args.action == "sync":
            with hold_slot(target):
                assert_closed(target)
                if args.tool and not (target / "profile.json").exists() and (target / ".sync-in-progress").is_file():
                    source = args.tool
                else:
                    recorded = metadata(target, allow_pending=True)
                    source = args.tool or Path(recorded["source"])
                data = sync_runtime(source.resolve(strict=True), target)
        elif args.action == "info":
            data = metadata(target, allow_pending=True)
            data["testplay_window_id"] = f"0x{instance_id(target):08x}"
        else:
            return launch(target, args.game_args, dry_run=args.dry_run)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"{exc}\n")
    print(json.dumps(data, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
