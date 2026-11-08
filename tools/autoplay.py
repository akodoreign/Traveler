"""Scripted playtest driver for the running rpgcobo test window.
Usage: python -E tools/autoplay.py "<steps>"   steps separated by ';':
  z / x / v / c / up / down / left / right   tap a key
  zN          tap Z N times, 0.9 s apart (advance dialogue)
  wait:MS     sleep
  hold:KEY:MS hold a key (walking)
  shot:NAME   capture _art/preview/ap_NAME.png
"""
import ctypes
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
u = ctypes.windll.user32
VK = {"up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27, "enter": 0x0D, "esc": 0x1B, "space": 0x20}


def game_focused():
    """True when the foreground window belongs to the game (keys are global; never type into another app)."""
    p = pid()
    if not p:
        return False
    hwnd = u.GetForegroundWindow()
    fp = ctypes.c_ulong(0)
    u.GetWindowThreadProcessId(hwnd, ctypes.byref(fp))
    return str(fp.value) == p


def ensure_focus():
    if game_focused():
        return True
    cap("refocus")                       # wincap --front
    time.sleep(0.4)
    return game_focused()


def vk(k):
    return VK.get(k, ord(k.upper()) if len(k) == 1 else 0)


def tap(code, hold=0.06):
    if not ensure_focus():
        print("game window lost focus - stopping (no keys sent to other apps)")
        sys.exit(2)
    sc = u.MapVirtualKeyW(code, 0)
    u.keybd_event(code, sc, 0, 0)
    time.sleep(hold)
    u.keybd_event(code, sc, 2, 0)


def pid():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq rpgcobo.exe", "/FO", "CSV", "/NH"], capture_output=True,
                         text=True).stdout.strip().splitlines()
    return out[0].split(",")[1].strip('"') if out and "," in out[0] else None


def cap(name, front=True):
    p = pid()
    if not p:
        print("no game window")
        return
    args = [sys.executable, "-E", os.path.join(HERE, "wincap.py"), p,
            os.path.join(HERE, "..", "_art", "preview", "ap_%s.png" % name)]
    if front:
        args.append("--front")
    subprocess.run(args, capture_output=True)


def main():
    cap("start")
    for st in [x.strip() for x in sys.argv[1].split(";") if x.strip()]:
        if st.startswith("wait:"):
            time.sleep(int(st[5:]) / 1000)
        elif st.startswith("shot:"):
            cap(st[5:], front=False)
        elif st.startswith("hold:"):
            _, k, ms = st.split(":")
            tap(vk(k), int(ms) / 1000)
        elif st[0] == "z" and st[1:].isdigit():
            for _ in range(int(st[1:])):
                tap(vk("z"))
                time.sleep(0.9)
        else:
            tap(vk(st))
            time.sleep(0.35)


if __name__ == "__main__":
    main()
