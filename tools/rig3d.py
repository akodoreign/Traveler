"""A light 3-D mannequin under the pixel-art cutouts.

Poses are solved on a 3-D skeleton (fixed bone lengths, planted feet, real depth) and each drawn
part is laid along its projected bone. Torso attachment points are calibrated from every view's
own artwork, so limbs meet the drawing in the side, front and back views.
Character space: x forward, y up, z toward the camera-side ("near", N) half; F is the far half.
"""
import json
import math
from pathlib import Path
from types import SimpleNamespace

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PROFILES = ROOT / "tools" / "cutout_profiles"
SIZE, ORIGIN = (208, 184), (104, 170)
PITCH = .25                                   # screen rows per unit of depth: the camera looks slightly down
VIEW_YAW = {None: 32.0, "front": 90.0, "back": -90.0}
SAYA_DIR = (-.75, -.65, .1)
FAMILY = {"yari": "pole", "naginata": "pole", "bo": "pole", "shakujo": "pole", "katana": "blade",
          "nodachi": "blade", "bokken": "blade", "tetsubo": "club", "tanto": "short", "kama": "short",
          "yumi": "bow", "musket": "gun"}


def unit(v):
    v = np.asarray(v, float)
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def rz(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return np.array(((c, -s, 0), (s, c, 0), (0, 0, 1.)))


def ry(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return np.array(((c, 0, -s), (0, 1., 0), (s, 0, c)))


def rx(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return np.array(((1., 0, 0), (0, c, -s), (0, s, c)))


def ik(a, target, l1, l2, pole):
    """Two fixed-length bones from a toward target; the middle joint bends toward pole."""
    d = target - a
    dist = np.linalg.norm(d)
    u = d / dist if dist > 1e-6 else np.array((0., -1., 0.))
    reach = float(np.clip(dist, abs(l1 - l2) + .05, l1 + l2 - .05))
    along = (l1 * l1 - l2 * l2 + reach * reach) / (2 * reach)
    side = pole - u * (pole @ u)
    if np.linalg.norm(side) < 1e-6:
        side = np.cross(u, (0., 0., 1.))
    return a + u * along + unit(side) * math.sqrt(max(0., l1 * l1 - along * along)), a + u * reach


class Part:
    def __init__(self, pixels, anchor, sockets, scale):
        self.pixels, self.anchor, self.sockets, self.scale = pixels, anchor, sockets, scale
        ys, xs = np.nonzero(pixels[..., 3])
        if not len(xs):
            raise ValueError("Part has no opaque pixels")
        self.bottom = float(ys.max())
        self.hull = cv2.convexHull(np.column_stack((xs, ys)).astype(np.float32)).reshape(-1, 2)

    def bone(self, socket):
        return float(np.linalg.norm((self.sockets[socket] - self.anchor) * self.scale))


def load_parts(spec):
    def definition(name, seen=()):
        data = spec["parts"][name]
        if "source_part" not in data:
            return data
        if name in seen:
            raise ValueError(f"Part inheritance cycle: {name}")
        return definition(data["source_part"], (*seen, name)) | data

    parts = {}
    for name in spec["parts"]:
        data = definition(name)
        with Image.open(ROOT / data["image"]) as source:
            image = source.convert("RGBA")
        if "box" in data:
            image = image.crop(tuple(data["box"]))
        pixels = np.array(image)
        pixels[pixels[..., 3] < 128] = 0
        pixels[pixels[..., 3] >= 128, 3] = 255
        anchor = np.array(data["anchor"], float)
        sockets = {k: np.array(v, float) for k, v in data.get("sockets", {}).items()}
        if data.get("mirror_x"):
            pixels = pixels[:, ::-1].copy()
            for point in (anchor, *sockets.values()):
                point[0] = pixels.shape[1] - 1 - point[0]
        parts[name] = Part(pixels, anchor, sockets, float(data["scale"]))
    return parts


def split_arm(part, overlap=2):
    """Overlapping upper-arm, forearm and hand layers cut from one complete relaxed arm."""
    elbow, wrist = part.sockets["elbow"], part.sockets["wrist"]
    y, x = np.indices(part.pixels.shape[:2])
    points = np.stack((x, y), axis=-1)
    elbow_plane = (points - elbow) @ unit(elbow - part.anchor) * part.scale
    wrist_plane = (points - wrist) @ unit(wrist - elbow) * part.scale
    pieces = {}
    for name, anchor, mask, sockets in (
        ("upper", part.anchor, elbow_plane <= overlap, {"elbow": elbow}),
        ("forearm", elbow, (elbow_plane >= -overlap) & (wrist_plane <= overlap), {"wrist": wrist}),
        ("hand", wrist, wrist_plane >= -overlap, {"grip": part.sockets["grip"]}),
    ):
        pixels = part.pixels.copy()
        pixels[~mask] = 0
        pieces[name] = Part(pixels, anchor.copy(), sockets, part.scale)
    return pieces


def lay(part, end, a, b, floor=.45, side=None, ceiling=1.05):
    """Affine that lays a part along the screen segment a-b, foreshortening only along the bone."""
    axis = (part.sockets[end] - part.anchor) * part.scale
    rest = np.linalg.norm(axis)
    u = axis / rest
    v = b - a
    length = np.linalg.norm(v)
    us = v / length if length > 1e-6 else np.array((0., 1.))
    ns = np.array((-us[1], us[0])) if side is None else side
    return part.scale * (min(max(length / rest, floor), ceiling) * np.outer(us, u) + np.outer(ns, (-u[1], u[0])))


def spin(part, degrees, mirror=False):
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    return part.scale * np.array(((c, -s), (s, c))) @ np.diag((-1. if mirror else 1., 1.))


class Mannequin:
    def __init__(self, key, weapon=None, hat=None, look=None):
        """weapon / hat swap this character's gear for another look; look is their palette spec."""
        self.key = key
        spec = json.loads((PROFILES / f"{key}.json").read_text(encoding="utf-8"))
        self.parts = P = load_parts(spec)
        self.size, self.ground_y = SIZE, ORIGIN[1]
        self.weapon = spec.get("weapon", "katana")
        self.family = spec.get("family") or FAMILY.get(self.weapon, "fist")
        if weapon or hat:
            import rig3d_gear
            if weapon:
                P.pop("saya", None)
                if weapon != "none":
                    P.update(rig3d_gear.weapon_parts(look, weapon))
                self.weapon, self.family = weapon, FAMILY.get(weapon, "fist")
            if hat:
                P["hat"] = rig3d_gear.hat_part(hat, tuple(look.get("armor", (84, 86, 98))))
        for name in ("head", "head_front", "head_back"):
            if name in P and "crown" not in P[name].sockets:
                P[name].sockets["crown"] = P[name].anchor - (0, 22 / P[name].scale)
        views = spec.get("views", {})
        arms = {None: (spec["nodes"]["arm_f"]["part"], spec["nodes"]["arm_b"]["part"])}
        if "front" in views:
            arms["front"] = (views["front"]["arm_f"]["part"], views["front"]["arm_b"]["part"])
        if "back" in views:                     # seen from behind, the near arm is on the right of the drawing
            arms["back"] = (views["back"]["arm_b"]["part"], views["back"]["arm_f"]["part"])
        for source in {name for pair in arms.values() for name in pair}:
            P.update({f"{source}_{segment}": piece for segment, piece in split_arm(P[source]).items()})
        if "saya" in P and "tip" not in P["saya"].sockets:
            saya = P["saya"]
            saya.sockets["tip"] = saya.hull[np.argmax(np.linalg.norm(saya.hull - saya.anchor, axis=1))]
        gear = P["weapon"]
        reach = (gear.hull - gear.anchor) @ unit(gear.sockets["tip"] - gear.anchor) * gear.scale
        self.tail, self.tip = float(-reach.min()), gear.bone("tip")
        self.tsuba = float(spec.get("tsuba", 7.2))
        self.frames = {view: self.calibrate(view, pair) for view, pair in arms.items()}

    def calibrate(self, view, arms):
        """Rest skeleton whose projection lands exactly on this view's drawn sockets."""
        P = self.parts
        suffix = f"_{view}" if view else ""
        body, wide = P["body" + suffix], P.get("body_front", P["body"])
        yaw = math.radians(VIEW_YAW[view])
        c, s = math.cos(yaw), math.sin(yaw)
        offset = {name: (point - body.anchor) * body.scale for name, point in body.sockets.items()}

        def char(d, depth):
            x, z = d[0] * c + depth * s, -d[0] * s + depth * c
            return np.array((x, -d[1] + (depth if view else z * c) * PITCH, z))

        rest = {"neck": char(offset["neck"], 0.)}
        for joint, a, b in (("sh", "shoulder_f", "shoulder_b"), ("hip", "hip_f", "hip_b")):
            half = abs(wide.sockets[a][0] - wide.sockets[b][0]) * wide.scale / 2 * abs(c)
            left, right = sorted((offset[a], offset[b]), key=lambda v: v[0])
            near, far = (right, left) if view == "back" else (left, right)
            rest[joint + "N"], rest[joint + "F"] = char(near, half), char(far, -half)
            if joint == "sh":
                pins = {"N": near / body.scale + body.anchor, "F": far / body.scale + body.anchor}
        leg, arm = {}, {}
        for side, art in (("N", "b"), ("F", "f")):
            foot = P[f"foot_{art}"]
            leg[side] = (P[f"thigh_{art}"].bone("knee"), P[f"shin_{art}"].bone("ankle"),
                         (foot.bottom - foot.anchor[1]) * foot.scale, art)
        for side, source in zip("NF", arms):
            arm[side] = (P[source + "_upper"].bone("elbow"), P[source + "_forearm"].bone("wrist"),
                         P[source + "_hand"].bone("grip"), source)
        length = min(l[0] + l[1] for l in leg.values())
        height = min((l[0] + l[1]) * .985 + l[2] - rest["hip" + side][1] for side, l in leg.items())
        return SimpleNamespace(view=view, suffix=suffix, c=c, s=s, rest=rest, leg=leg, arm=arm, L=length,
                               H=height, saya="saya" in P, pins=pins)

    def screen(self, p, f):
        depth = p[0] * f.s + p[2] * f.c
        tilt = depth if f.view else p[2] * f.c      # a level forward thrust stays level in the side view
        return np.array((ORIGIN[0] + p[0] * f.c - p[2] * f.s, ORIGIN[1] - p[1] + tilt * PITCH)), depth

    def tilt(self, up, f):
        return math.degrees(math.atan2(up[0] * f.c - up[2] * f.s, up[1]))

    def solve(self, c, view=None):
        f, P, J = self.frames[view], self.parts, {}
        L = f.L
        R = rz(-c["lean"]) @ ry(c["twist"]) @ rx(c["bend"])
        pelvis = np.array((0., f.H, 0.)) + np.asarray(c["root"], float) * L
        feet = {}
        for side in "NF":                       # planted feet stay put; the pelvis sinks to keep them in reach
            thigh, shin, sole, _ = f.leg[side]
            x, y, z = c["feet"][side][:3]
            base = f.rest["hip" + side]
            feet[side] = np.array((base[0] + x * L, sole + y * L, base[2] + z * L))
            if side in c["kick"]:
                continue
            reach = (thigh + shin) * .985
            flat = math.hypot(feet[side][0] - pelvis[0] - base[0], feet[side][2] - pelvis[2] - base[2])
            if flat >= reach:
                raise ValueError(f"{side} foot is beyond the leg's reach")
            pelvis[1] = min(pelvis[1], feet[side][1] + math.sqrt(reach * reach - flat * flat) - base[1])
        up = R @ rz(-c["head"]) @ np.array((0., 1., 0.))
        J["pelvis"], J["neck"] = pelvis, pelvis + R @ f.rest["neck"]
        for side in "NF":
            thigh, shin, _, _ = f.leg[side]
            hip = J["hip" + side] = pelvis + f.rest["hip" + side]
            yaw = math.radians(c["feet"][side][3])
            pole = np.asarray(c["poles"].get(side, (math.cos(yaw), .1, math.sin(yaw))), float)
            if side in c["kick"]:
                feet[side], pole = hip + np.asarray(c["kick"][side], float) * L, np.array((.3, 1., 0.))
            J["knee" + side], J["ankle" + side] = ik(hip, feet[side], thigh, shin, pole)
        sdir = unit(c.get("saya", SAYA_DIR))
        mouth = J["saya"] = pelvis + (5., 2.5, f.rest["hipN"][2] + 3.) + sdir * c["saya_pull"]
        J["saya_end"] = mouth + sdir * (P["saya"].bone("tip") if f.saya else 1.)
        w, gear = c["weapon"], None
        sheathed = w is None and f.saya and c["carry"]
        if sheathed:
            out = self.tsuba + c["iai"] * (self.tip - self.tsuba)
            gear = dict(at=mouth - sdir * out, dir=sdir, reveal=out, part="weapon", depth=None)
        sh = {side: pelvis + R @ f.rest["sh" + side] for side in "NF"}
        face = J["neck"] + up * 13

        def goal(side, spec):
            if isinstance(spec, str):
                return gear["at"] if spec == "hilt" else gear["string"] if spec == "string" else mouth + sdir * 3
            if isinstance(spec, dict):
                if "plant" in spec:
                    return np.array((spec["plant"][0] * L, self.tail, f.rest["hipN"][2] + spec["plant"][1] * L))
                return face + R @ np.asarray(spec["face"], float)
            local = np.asarray(spec, float) * (1, 1, 1 if side == "N" else -1)
            return sh[side] + R @ local * sum(f.arm[side][:3])

        for side in ("FN" if w and w["hand"] == "F" else "NF"):
            upper, fore, hand, _ = f.arm[side]
            if w and side != w["hand"] and w.get("sep") is not None:
                target = J["grip" + w["hand"]] + gear["dir"] * w["sep"]
            else:
                target = goal(side, c["arms"][side])
            bend = np.asarray(c["elbows"].get(side, (-.5, -.6, .65)), float) * (1, 1, 1 if side == "N" else -1)
            J["sh" + side] = sh[side]
            J["elbow" + side], J["grip" + side] = ik(sh[side], target, upper, fore + hand, R @ bend)
            J["wrist" + side] = J["elbow" + side] + (J["grip" + side] - J["elbow" + side]) * fore / (fore + hand)
            if w and side == w["hand"]:
                d = unit(w["dir"])
                gear = dict(at=J["grip" + side] - d * w.get("shift", 0), dir=d, reveal=None,
                            part=w.get("part", "weapon"), depth=side)
                if self.family == "bow":
                    part = P[gear["part"]]
                    u = unit(part.sockets["tip"] - part.anchor)
                    q = (part.sockets["string"] - part.anchor) * part.scale
                    across = q @ (-u[1], u[0])
                    gear["side"] = rz(90) @ d * math.copysign(1, across)
                    gear["string"] = gear["at"] + d * (q @ u) + rz(90) @ d * abs(across)
            elif sheathed and isinstance(c["arms"][side], str) and c["arms"][side] == "hilt" and c["iai"] > 0:
                gear["at"] = J["grip" + side]
                gear["dir"], gear["reveal"] = unit(mouth - gear["at"]), float(np.linalg.norm(mouth - gear["at"]))
        body_up = np.array((0., 1., 0.))
        if c["tip"]:                            # a fall: the whole solved figure tips over and lies on the ground
            T = rz(c["tip"])
            up, body_up = T @ up, T @ body_up
            J = {name: T @ p for name, p in J.items()}
            lift = 5 - min(p[1] for p in J.values())
            slide = -(min(p[0] for p in J.values()) + max(p[0] for p in J.values())) / 2
            J = {name: p + (slide, lift, 0.) for name, p in J.items()}
        S = {name: self.screen(p, f) for name, p in J.items()}
        items = []

        def add(depth, name, matrix, at, reveal=None):
            items.append((depth, P[name], matrix, at, reveal))

        (a, za), (b, zn) = S["pelvis"], S["neck"]
        zb, body = (za + zn) / 2, "body" + f.suffix
        torso = lay(P[body], "neck", a, b, .6)
        add(zb + 1, body, torso, a)
        waist = "waist" + f.suffix if "waist" + f.suffix in P else "waist"
        lean = self.tilt(body_up, f)
        add(zb + .5, waist, spin(P[waist], lean), a)
        head, turn = "head" + f.suffix, self.tilt(up, f)
        add(zn + 3, head, spin(P[head], turn), b)
        if "hat" in P:
            add(zn + 3.1, "hat", spin(P["hat"], turn),
                b + spin(P[head], turn) @ (P[head].sockets["crown"] - P[head].anchor))
        for side in "NF":
            art = f.leg[side][3]
            (h, _), (k, zk), (an, _) = S["hip" + side], S["knee" + side], S["ankle" + side]
            depth = zk - 6 + (.3 if side == "N" else 0)
            add(depth, f"thigh_{art}", lay(P[f"thigh_{art}"], "knee", h, k), h)
            add(depth - .1, f"shin_{art}", lay(P[f"shin_{art}"], "ankle", k, an), k)
            yaw, pitch = c["feet"][side][3:5]
            heading = (yaw + VIEW_YAW[f.view] + 180) % 360 - 180
            look = "_camera" if 40 <= heading <= 140 else "_heel" if -140 <= heading <= -40 else ""
            foot = f"foot_{art}{look}" if f"foot_{art}{look}" in P else f"foot_{art}"
            add(depth - .2, foot, spin(P[foot], lean + pitch * math.cos(math.radians(heading)),
                                       not look and abs(heading) > 140), an)
            source = f.arm[side][3]
            (e, ze), (wr, zw), (g, zg) = S["elbow" + side], S["wrist" + side], S["grip" + side]
            s = a + torso @ (f.pins[side] - P[body].anchor)      # the drawn shoulder, so sleeves never gap
            add(ze + 2, source + "_upper", lay(P[source + "_upper"], "elbow", s, e, ceiling=1.2), s)
            add(zw + 2.05, source + "_forearm", lay(P[source + "_forearm"], "wrist", e, wr), e)
            add(zg + 2.1, source + "_hand", lay(P[source + "_hand"], "grip", wr, g, .7), wr)
        if f.saya:
            add(zb + 1.5, "saya", lay(P["saya"], "tip", S["saya"][0], S["saya_end"][0], .3), S["saya"][0])
        if gear:
            at = self.screen(gear["at"], f)[0]
            end = self.screen(gear["at"] + gear["dir"] * self.tip, f)[0]
            side = gear.get("side")
            if side is not None:
                side = np.array((side[0] * f.c - side[2] * f.s, -side[1]))
                side *= max(1., .35 / max(np.linalg.norm(side), 1e-6))
            depth = S["grip" + gear["depth"]][1] + 2.08 if gear["depth"] else zb + 1.6
            add(depth, gear["part"], lay(P[gear["part"]], "tip", at, end, .3, side), at, gear["reveal"])
        return SimpleNamespace(J=J, S=S, items=items, gear=gear)

    def render(self, c, view=None):
        out = Image.new("RGBA", self.size)
        for _, part, matrix, at, reveal in sorted(self.solve(c, view).items, key=lambda item: item[0]):
            pixels = part.pixels
            if reveal is not None:              # the rest of the blade is still inside the scabbard
                y, x = np.indices(pixels.shape[:2])
                hidden = (np.stack((x, y), -1) - part.anchor) @ unit(part.sockets["tip"] - part.anchor)
                pixels = pixels.copy()
                pixels[hidden * part.scale > reveal] = 0
            else:
                bounds = (part.hull - part.anchor) @ matrix.T + at
                if bounds.min() < 0 or np.any(bounds.max(axis=0) > np.array(self.size) - 1):
                    raise ValueError("Pose leaves its cell")
            affine = np.column_stack((matrix, at - matrix @ part.anchor)).astype(np.float32)
            layer = cv2.warpAffine(pixels, affine, self.size, flags=cv2.INTER_NEAREST,
                                   borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
            out.alpha_composite(Image.fromarray(layer))
        return out
