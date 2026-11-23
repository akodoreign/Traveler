"""Create material scans for Hoshi-no-Ichi's fitted cedar entrance leaves."""

from comfy_furnace import generate

PROMPTS = {
    "town_door_cedar": (
        "Square orthographic diffuse texture scan. Straight on, weathered late 1500s Japanese "
        "door made of seven narrow vertical cedar planks, irregular narrow dark grooves, "
        "rich warm dark reddish brown, fine grain, slight hand-planed waviness, naturally "
        "darkening toward the foot, tiny old pegs. Continuous wood texture edge to edge. "
        "No hardware, no hinges, no walls, no frame, no buildings, no perspective, no words."
    ),
    "town_door_iron": (
        "Orthographic full square seamless albedo material scan of worn dark hand-forged iron, "
        "brownish black patina, irregular tiny hammer marks and faint polished edges, natural "
        "detail at fingernail scale, even soft light, smooth material scan, no object or border."
    ),
}

if __name__ == "__main__":
    generate(PROMPTS, "comfy-town-door-receipts.json", 35290)
