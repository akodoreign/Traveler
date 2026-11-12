"""Atomic writes into the game's resources (tester 2026-11-11: a running game loaded a sprite sheet while it was 0 bytes,
mid-rewrite, and hit "EventRunner ERROR"; the user plays while the agents work). Write a temp file in the same folder
(suffix .tmp, so it never looks like a .png to the game), then os.replace() it over the target. On Windows the replace
fails while another process has the target open (the game, another tool reading it): retry for up to ~30 s, then
give up and remove the temp file (the old sheet stays whole)."""
import os
import shutil
import time


def _replace(tmp, path):
    for k in range(60):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            time.sleep(0.5)
    try:
        os.remove(tmp)
    finally:
        raise PermissionError("could not replace %s (in use for 30 s); left unchanged" % path)


def save_png(im, path, **kw):
    tmp = path + ".tmp"
    im.save(tmp, format="PNG", **kw)
    _replace(tmp, path)


def copy_file(src, dst):
    tmp = dst + ".tmp"
    shutil.copyfile(src, tmp)
    _replace(tmp, dst)
