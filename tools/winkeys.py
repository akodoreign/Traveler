"""Send key presses to the foreground window and optionally capture a window afterwards.
Usage: python -E tools/winkeys.py <pid> "z,z,down,z" [out.png] [--delay ms]
Keys: letters/digits, up, down, left, right, enter, esc, space, f1-f12.
"""
import ctypes
import subprocess
import sys
import time

user32 = ctypes.windll.user32
VK = {"up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27, "enter": 0x0D, "esc": 0x1B, "space": 0x20}
VK.update({"f%d" % i: 0x6F + i for i in range(1, 13)})


def vk(k):
    if k in VK:
        return VK[k]
    return ord(k.upper())


def press(code, hold=0.06):
    scan = user32.MapVirtualKeyW(code, 0)
    user32.keybd_event(code, scan, 0, 0)
    time.sleep(hold)
    user32.keybd_event(code, scan, 2, 0)


def main():
    pid, seq = sys.argv[1], sys.argv[2]
    delay = 0.45
    if "--delay" in sys.argv:
        delay = int(sys.argv[sys.argv.index("--delay") + 1]) / 1000.0
    # focus the window first
    subprocess.run([sys.executable, "-E", __file__.replace("winkeys.py", "wincap.py"), pid, "NUL", "--front"],
                   capture_output=True)
    for k in [s.strip() for s in seq.split(",") if s.strip()]:
        if k.startswith("wait"):
            time.sleep(int(k[4:]) / 1000.0)
            continue
        press(vk(k))
        time.sleep(delay)
    outs = [a for a in sys.argv[3:] if a.endswith(".png")]
    if outs:
        r = subprocess.run([sys.executable, "-E", __file__.replace("winkeys.py", "wincap.py"), pid, outs[0]],
                           capture_output=True, text=True)
        print(r.stdout.strip())


if __name__ == "__main__":
    main()
