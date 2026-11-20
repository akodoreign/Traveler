"""Author death motion on existing flat-rigged generated foe assets."""
from pathlib import Path
import json
import math
import sys

root, output = (Path(x).resolve() for x in sys.argv[1:])
sys.path.insert(0, str(root / "tools"))

from foe_fidgets import motion_bytes, product, rotate, rotation, side_and_delay
from motfile import load


DURATION = 32
PILOTS = {
    "EP459": "kappa",
    "EP165": "air",
    "EP438": "spirit",
    "EP120": "heavy",
}


def ease(t, start, end):
    u = min(1.0, max(0.0, (t - start) / (end - start)))
    return u * u * (3.0 - 2.0 * u)


def pulse(t, start, peak, tail, end):
    return ease(t, start, peak) * (1.0 - ease(t, tail, end))


def kappa(t, name, side, ground):
    recoil = pulse(t, .02, .17, .23, .48)
    tuck = ease(t, .19, .57)
    roll = ease(t, .29, .72)
    bounce = pulse(t, .66, .74, .78, .87)
    orbit = (65.0 * roll + 7.0 * bounce, -7.0 * recoil, 18.0 * roll)
    delta = (-10.5 * roll - 4.1 * recoil, (19.0 - ground) * roll + 1.6 * bounce, 3.4 * roll)
    adjust = (0., 0., 0.)
    if name.startswith("leg"):
        adjust = (-32.0 * tuck, 5.0 * side * tuck, 11.0 * side * roll)
    elif name.startswith("arm"):
        adjust = (25.0 * recoil - 24.0 * tuck, -12.0 * side * tuck, -17.0 * side * roll)
    elif name == "head":
        adjust = (19.0 * recoil - 22.0 * roll, 6.0 * roll, -5.0 * roll)
    return orbit, delta, adjust, 1.0


def hornet(t, name, side, ground):
    shock = pulse(t, .02, .13, .18, .34)
    fall = ease(t, .20, .65) ** 1.45
    bounce = pulse(t, .63, .72, .75, .86)
    spin = ease(t, .17, .66)
    orbit = (-26.0 * spin + 12.0 * shock, 24.0 * spin, 49.0 * spin - 6.0 * bounce)
    delta = (12.2 * fall, (15.5 - ground) * fall + 4.5 * shock + 3.5 * bounce, -6.0 * fall)
    adjust = (0., 0., 0.)
    if name.startswith("wing"):
        flap = math.sin(math.tau * (5.2 * t + .3 * (side < 0)))
        flap *= pulse(t, 0.0, .15, .22, .52)
        fold = ease(t, .37, .75)
        adjust = (9.0 * flap, 19.0 * side * fold, side * (31.0 * flap + 62.0 * fold))
    elif name.startswith("leg"):
        adjust = (38.0 * fall, -12.0 * side * fall, 14.0 * side * fall)
    elif name == "abdomen":
        adjust = (14.0 * shock + 25.0 * fall, 12.0 * spin, 0.0)
    return orbit, delta, adjust, 1.0


def spirit(t, name, side, ground):
    recoil = pulse(t, .0, .14, .21, .46)
    draw = ease(t, .22, .82)
    release = ease(t, .72, 1.0)
    swirl = math.sin(math.tau * (t - .26)) * pulse(t, .12, .30, .49, .81)
    orbit = (12.0 * swirl, 31.0 * draw, 18.0 * recoil)
    delta = (-5.0 * recoil, 5.0 * recoil - .53 * ground * draw, 6.0 * swirl)
    adjust = (25.0 * swirl, 17.0 * draw, 27.0 * draw) if name.startswith("tail") else (0., 0., 0.)
    return orbit, delta, adjust, max(.03, 1.0 - .72 * draw - .25 * release)


def heavy(t, name, side, ground):
    stagger = pulse(t, .03, .18, .27, .51)
    buckle = ease(t, .18, .47)
    fall = ease(t, .36, .82) ** 1.15
    damp = pulse(t, .77, .83, .85, .95)
    orbit = (62.0 * fall - 13.0 * stagger, 18.0 * fall, -38.0 * fall + 4.0 * damp)
    delta = (-18.0 * fall - 7.0 * stagger, -5.0 * buckle + (22.0 - ground) * fall + 1.6 * damp, 10.0 * fall)
    adjust = (0., 0., 0.)
    if name.startswith("arm"):
        adjust = (20.0 * stagger - 41.0 * fall, side * 21.0 * stagger, -side * 15.0 * fall)
    elif name.startswith("leg"):
        adjust = (35.0 * buckle - 18.0 * fall, side * 10.0 * fall, side * 12.0 * fall)
    elif name == "head" or name.startswith("tail"):
        adjust = (-15.0 * stagger + 21.0 * buckle - 7.0 * damp, 15.0 * fall, 12.0 * fall)
    return orbit, delta, adjust, 1.0


STYLES = {"kappa": kappa, "air": hornet, "spirit": spirit, "heavy": heavy}


def motion(part, pivot, style, start):
    name = part["name"]
    initial = part["keys"][start - part["start"]]
    side, _ = side_and_delay(name)
    relative = tuple(p - origin for p, origin in zip(initial["p"], pivot))
    for frame in range(DURATION + 1):
        t = frame / DURATION
        orbit, delta, adjust, scale = style(t, name, side, pivot[1])
        q = rotation(*orbit)
        placed = rotate(q, tuple(x * scale for x in relative))
        yield {
            "p": tuple(p + x + d for p, x, d in zip(pivot, placed, delta)),
            "q": product(q, product(rotation(*adjust), initial["q"])),
            "s": tuple(x * scale for x in initial["s"]),
        }


def main():
    output.mkdir(parents=True, exist_ok=True)
    native = root / "_tools/rpgcobo-tool/project/resource/native_foe"
    records = json.loads((native / "index.json").read_text(encoding="utf-8-sig"))
    for key, body in PILOTS.items():
        parts = load(native / f"{key}.mot")["parts"]
        start = next(record["st"] for record in records[key]["animap"] if record["id"] == "stand")
        root_part = next(part for part in parts if part["name"] == "root")
        pivot = root_part["keys"][start - root_part["start"]]["p"]
        tracks = (list(motion(part, pivot, STYLES[body], start)) for part in parts)
        (output / f"{key}.mot").write_bytes(motion_bytes(parts, tracks))


if __name__ == "__main__":
    main()

