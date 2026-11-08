"""Capture a top-level window of a process (Windows): python -E tools/wincap.py <pid|exe-name> <out.png> [--front]"""
import ctypes
import ctypes.wintypes as wt
import subprocess
import sys
import time

from PIL import ImageGrab

user32 = ctypes.windll.user32
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wt.HWND, wt.LPARAM)


def pids_for(name_or_pid):
    if name_or_pid.isdigit():
        return {int(name_or_pid)}
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq %s" % name_or_pid, "/FO", "CSV", "/NH"],
                         capture_output=True, text=True).stdout
    return {int(l.split('","')[1]) for l in out.splitlines() if l.count('","') >= 2}


def windows_for(pids):
    found = []

    def cb(hwnd, _):
        pid = wt.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value in pids and user32.IsWindowVisible(hwnd):
            r = wt.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(r))
            n = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(n + 1)
            user32.GetWindowTextW(hwnd, buf, n + 1)
            found.append((hwnd, buf.value, (r.left, r.top, r.right, r.bottom)))
        return True

    user32.EnumWindows(EnumWindowsProc(cb), 0)
    return found


def main():
    target, out = sys.argv[1], sys.argv[2]
    wins = windows_for(pids_for(target))
    wins = [w for w in wins if (w[2][2] - w[2][0]) > 200]
    if not wins:
        print("no window")
        return
    hwnd, title, rect = max(wins, key=lambda w: (w[2][2] - w[2][0]) * (w[2][3] - w[2][1]))
    if "--front" in sys.argv:
        user32.ShowWindow(hwnd, 9)        # SW_RESTORE
        user32.SetForegroundWindow(hwnd)
        time.sleep(1.0)
        r = wt.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(r))
        rect = (r.left, r.top, r.right, r.bottom)
    img = ImageGrab.grab(bbox=rect, all_screens=True)
    img.save(out)
    print(title, rect, img.size)


if __name__ == "__main__":
    main()
