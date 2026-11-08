"""Same-length byte patches for Japanese labels baked into binary .ui layouts (idempotent; originals backed up
to _tools/data_orig/ui/). Each replacement must have exactly the same UTF-8 byte length as the original.
Run: python -E tools/patch_ui.py"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
UI = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "presetui")
BACKUP = os.path.join(HERE, "..", "_tools", "data_orig", "ui")
PATCHES = {
    "misc_levelup.ui": [("習得能力", "Learned Arts")],
    "battleui_cmditem.ui": [("uiimg/item_n.png", "uiimg/bctl_n.png"), ("uiimg/item_g.png", "uiimg/bctl_g.png")],
    "parts/choiceitem.ui": [("uiimg/item_n.png", "uiimg/bctl_n.png"), ("uiimg/item_g.png", "uiimg/bctl_g.png")],
    "parts/dialogback.ui": [("uiimg/dialog.png", "uiimg/msgwin.png")],
    "dialog_confirm.ui": [("uiimg/dialog.png", "uiimg/msgwin.png")],
    "message_talk.ui": [("uiimg/window.png", "uiimg/msgwin.png"), ("uiimg/frame.png", "uiimg/mfram.png"), ("uiimg/nameplate.png", "uiimg/msgplate1.png")],
    "message_talk_pic.ui": [("uiimg/window.png", "uiimg/msgwin.png"), ("uiimg/frame.png", "uiimg/mfram.png"), ("uiimg/nameplate.png", "uiimg/msgplate1.png")],
    "message_big.ui": [("uiimg/window.png", "uiimg/msgwin.png")],
    "battleui.ui": [("parts/listitem3.ui", "parts/listitem9.ui")],
}

for fname, reps in PATCHES.items():
    src = os.path.join(UI, fname)
    os.makedirs(BACKUP, exist_ok=True)
    bak = os.path.join(BACKUP, fname.replace("/", "_"))
    if not os.path.exists(bak):
        shutil.copy(src, bak)
    data = open(bak, "rb").read()
    for a, b in reps:
        ab, bb = a.encode("utf-8"), b.encode("utf-8")
        assert len(ab) == len(bb), (a, b, len(ab), len(bb))
        assert ab in data, a
        data = data.replace(ab, bb)
    open(src, "wb").write(data)
    print("patched", fname)

# the battle skill list gets its own copy of the shared list item (listitem3 also serves the item menu and a dialog)
d = open(os.path.join(UI, "parts", "listitem3.ui"), "rb").read()
for a, b in (("uiimg/item_n.png", "uiimg/bctl_n.png"), ("uiimg/item_g.png", "uiimg/bctl_g.png")):
    d = d.replace(a.encode(), b.encode())
open(os.path.join(UI, "parts", "listitem9.ui"), "wb").write(d)
print("wrote parts/listitem9.ui")
