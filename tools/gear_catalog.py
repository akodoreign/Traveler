"""Wearable equipment designs keyed by the game's stable armor IDs."""

# Body garments use the same bind dimensions as the 349 native bodies.
# (style, hem height, brocade, extra layer)
BODY = {
    "A100": ("travel", 0, "", ""),
    "A101": ("lamellar", 28, "", ""),
    "A108": ("plate", 26, "", "cuirass"),
    "A109": ("lamellar", 24, "", "lacquer"),
    "A111": ("robe", 24, "stripes", "ofuda"),
    "A112": ("plate", 25, "", "heavy"),
    "A116": ("lamellar", 21, "", "scales"),
    "A120": ("silk", 23, "diamonds", "lacquer"),
    "A124": ("robe", 15, "blossoms", "ofuda"),
    "A127": ("silk", 16, "stripes", ""),
    "A128": ("robe", 17, "clouds", "mantle"),
    "A135": ("lamellar", 25, "", "crest"),
    "A140": ("robe", 19, "blossoms", ""),
    "A141": ("lamellar", 27, "", "rivet"),
    "A153": ("robe", 16, "stripes", "ward"),
    "A155": ("riding", 29, "", "leather"),
    "A159": ("lamellar", 29, "", "riding"),
    "A166": ("plate", 22, "", "champion"),
    "A167": ("robe", 14, "rings", "ward"),
    "A168": ("lamellar", 27, "", "storm"),
}

HEAD = {
    "A102": "jingasa", "A103": "guard", "A110": "kabuto", "A113": "scout",
    "A143": "champion_band", "A160": "legion", "A170": "straw",
    "A171": "eboshi", "A172": "band",
}
ACCESSORY = {
    "A114": "oni", "A145": "iron", "A146": "cedar", "A147": "ink", "A148": "silk",
    "A149": "jade", "A150": "giseiki", "A151": "abbot",
}
CAPE = "A125"

WEAPONS = {
    "tanto": "short", "katana": "blade", "kakita": "blade", "yari": "pole",
    "bo": "pole", "yumi": "bow", "tetsubo": "club", "musket": "bow",
}


def registry():
    return {**dict.fromkeys(BODY, "body"), **dict.fromkeys(HEAD, "head"),
            **dict.fromkeys(ACCESSORY, "mask"), CAPE: "cape"}
