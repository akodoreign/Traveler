"""Build main-menu-only button layouts from the stock RPG-Cobo layouts.

The battle UI's ink/lacquer buttons are used without changing the shared
character chooser or any other menu. Run from any directory with Python.
"""
from pathlib import Path

UI = Path(__file__).resolve().parent.parent / "_tools" / "rpgcobo-tool" / "project" / "presetui"
ROWS = (("menuitem", "menurt01"), ("memberitem", "memberrt01"))


def replace_once(data, old, new):
    old, new = old.encode(), new.encode()
    if len(old) != len(new) or data.count(old) != 1:
        raise ValueError(f"Unexpected layout reference: {old!r}")
    return data.replace(old, new)


def main():
    for stock, custom in ROWS:
        data = (UI / "parts" / (stock + ".ui")).read_bytes()
        for state in ("n", "g"):
            data = replace_once(data, "uiimg/item_" + state + ".png", "uiimg/bctl_" + state + ".png")
        (UI / "parts" / (custom + ".ui")).write_bytes(data)

    path = UI / "menu_main.ui"
    data = path.read_bytes()
    for stock, custom in ROWS:
        old, new = "parts/" + stock + ".ui", "parts/" + custom + ".ui"
        if new.encode() not in data:
            data = replace_once(data, old, new)
        elif data.count(new.encode()) != 1 or old.encode() in data:
            raise ValueError(f"Unexpected main-menu reference: {new}")
    path.write_bytes(data)


if __name__ == "__main__":
    main()
