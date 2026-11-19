"""Mitsue's story costumes. Costume identity survives tailoring."""
from copy import deepcopy

# Item, tailored item, identity, name, defence, lining, quest material, count, clue.
COSTUMES = (
    ("A180", "A184", "shinobi", "Shosuro Shinobi Costume", 10, 21, "I244", 2, "Steal two Shells from Tide Crabs on the Crab coast."),
    ("A181", "A185", "maid", "Willow Teahouse Maid Uniform", 14, 26, "I571", 1, "Find the Cave Spider Silk in the Egg Caves, near the first nests."),
    ("A182", "A186", "fox", "Fox Household Kimono", 16, 31, "I572", 1, "Find the Sea-glass Clasp on the Crane coast road, beside the dock."),
    ("A189", "A191", "clerk", "Castle Records Clerk Robe", 18, 30, "I244", 3, "Steal three Shells from Tide Crabs on the Crab coast."),
    ("A190", "A192", "pilgrim", "Mountain Pilgrim Habit", 26, 41, "I244", 4, "Steal four Shells from Tide Crabs on the Crab coast."),
    ("A183", "A187", "soldier", "Iuchi Camp Uniform", 23, 38, "I244", 4, "Steal four Shells from Tide Crabs on the Crab coast."),
)
ARTS = {"shinobi": "Steal and Copy", "maid": "herbal tea and a healing poultice",
        "clerk": "Deduce", "pilgrim": "Elemental Ward", "fox": "Trickster", "soldier": "Cover and Heavy Slash"}


def armor(table):
    for base, upgraded, role, name, defense, improved, *_ in COSTUMES:
        for item, value in ((base, defense), (upgraded, improved)):
            table[item] = dict(deepcopy(table["A100"]), name=("Reinforced " if item == upgraded else "") + name,
                               desc=f"Mitsue alone can wear this disguise. Grants {ARTS[role]}.",
                               PDEF=value, price=0, rt_costume=role)


    table["A188"] = dict(deepcopy(table["A102"]), name="Shinobi Mask", PDEF=1, price=0,
                         rt_costume_head="shinobi", desc="Mitsue's folded cloth mask. Worn with her shinobi costume.")


def materials(table):
    for item, name in (("I571", "Cave Spider Silk"), ("I572", "Sea-glass Clasp")):
        table[item] = dict(deepcopy(table["I244"]), name=name, price=0, desc="Bring this material to a Scorpion shrine tailor.")


def skills(table):
    for sid, source, name in (("S950", "S127", "Willow Poultice"), ("S951", "S176", "Restorative Herb Tea"),
                              ("S952", "S505", "Trickster")):
        skill = deepcopy(table[source])
        for k in list(skill):
            if k.startswith("rt_"):
                del skill[k]
        skill.update(name=name, addlist=True, consume=[1,8], rt_school=True)
        table[sid] = skill
    table["S950"]["desc"] = "Maid outfit art. Spend TP to heal one ally and cure poison."
    table["S951"]["desc"] = "Maid outfit art. Spend TP to heal all allies and cure poison."
    table["S952"]["desc"] = "Spend 8 TP to borrow a random battle art from another character for this action. Other requirements are waived."
