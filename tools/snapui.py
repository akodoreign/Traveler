"""Screenshot one test battle at 1280x720 with extra flags: python -E tools/snapui.py <gid> <out.png> [wait_ms] [flag ...]
Writes the game's stdout next to the image (<out>.txt). Closes any running game first."""
import os, subprocess, sys, time
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.normpath(os.path.join(HERE, "..", "_tools", "rpgcobo-tool"))
gid, out = int(sys.argv[1]), sys.argv[2]
wait = sys.argv[3] if len(sys.argv) > 3 else "7000"
flags = sys.argv[4:]
subprocess.run(["taskkill", "/IM", "rpgcobo.exe", "/F"], capture_output=True)
rel = "tmp/rt_shot/ui_%d_%d.raw" % (gid, int(time.time()))
raw = os.path.join(TOOL, rel)
os.makedirs(os.path.dirname(raw), exist_ok=True)
log = open(out + ".txt", "w")
p = subprocess.Popen([os.path.join(TOOL, "rpgcobo.exe"), "-testplay", "-battle", "M001", str(gid), "-debuglv", "20",
                      "-rtfast", "-rtshot", rel, wait] + flags, cwd=TOOL, stdout=log, stderr=subprocess.STDOUT)
t0 = time.time()
while time.time() - t0 < 60 and not (os.path.exists(raw) and os.path.getsize(raw) > 8):
    time.sleep(0.5)
time.sleep(1)
subprocess.run(["taskkill", "/PID", str(p.pid), "/F"], capture_output=True)
log.close()
if not os.path.exists(raw):
    sys.exit("no shot")
b = open(raw, "rb").read()
w, h = int.from_bytes(b[:4], "little"), int.from_bytes(b[4:8], "little")
Image.fromarray(np.frombuffer(b[8:8 + w * h * 4], np.uint8).reshape(h, w, 4)[..., :3].copy()).save(out)
print("ok", w, h)
