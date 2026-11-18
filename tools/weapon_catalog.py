"""Native inventory weapon shapes and their existing combat motion families."""

FAMILIES = {
    "none": "fist", "claws": "fist", "katana": "blade", "kakita": "blade", "nodachi": "blade",
    "bokken": "blade", "tanto": "short", "kama": "short", "nunchaku": "short", "fan": "short",
    "yari": "pole", "naginata": "pole", "bo": "pole", "shakujo": "pole",
    "yumi": "bow", "musket": "gun", "tetsubo": "club",
}
EQTYPES = {0: "none", 1: "tanto", 2: "katana", 3: "yari", 5: "bo", 6: "yumi", 7: "tetsubo"}
SHAPES = {
    "W136": "bokken", "W141": "shakujo", "W146": "kama", "W159": "claws", "W160": "claws",
}
COMBAT_BANKS = ("bokken", "fan", "kama", "musket", "nunchaku")


def inventory(records):
    items = {}
    for item, data in records.items():
        if not isinstance(data, dict) or not data.get("name") or data["name"].startswith("(unused"):
            continue
        kind = SHAPES.get(item, data.get("rt_look", EQTYPES.get(data.get("eqtype"))))
        if kind not in FAMILIES:
            raise ValueError(f"No native weapon type for {item}: {kind}")
        items[item] = {"kind": kind, "family": FAMILIES[kind]}
    return items
