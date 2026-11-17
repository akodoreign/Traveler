"""Cutout rig animation (user 2026-11-15: "wonder if you could almost do a rigging system under the pixels and just all
the different pieces, then move the rigging system").

The procedural rig (gen_sprites2d: pose_v4 / build_pose / rig_legs / rig_arms) knows every joint of every frame. The
clean master drawing (fix_sheet's stand frame) is cut into parts by nearest bone - back leg, back arm, body (torso +
head), front leg, front arm, the weapon - and each part is moved rigidly from the stand pose to the frame's pose, drawn
back to front. One drawing, so one outfit; real limb swing from the rig.

    python -E tools/rig_anim.py KEY [anim ...]      preview: _art/preview/fixsheet/<key>_rig.png / .gif
Library use: rig_frames(key, master, frame_ids) -> {frame index: RGBA frame}."""
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv, sys.argv = sys.argv, [sys.argv[0]]
import gen_sprites2d as s2  # noqa: E402
sys.argv = _argv

ROOT = os.path.normpath(os.path.join(HERE, ".."))
RES = os.path.join(ROOT, "_tools", "rpgcobo-tool", "project", "resource")
FIXD = os.path.join(ROOT, "_art", "preview", "fixsheet")
FW, FH, COLS = 80, 68, 14
ZF = 1                     # the pixel scale the rig works at (2: on the HD master - thresholds scale with it)

# parts, back to front: (name, bone from, bone to); all animation-driving limbs stay independently articulated
PARTS = [("thigh_b", "hip", "kn_b"), ("shin_b", "kn_b", "ft_b"), ("foot_b", "ft_b", "toe_b"),
         ("upper_b", "sh_b", "el_b"), ("fore_b", "el_b", "ha_b"), ("hand_b", "ha_b", "hand_tip_b"),
         ("body", "hip", "shm"),
         ("waist", "hip", "hipd"),
         ("waistline", "waistline_b", "waistline_f"),
         ("head", "neck", "head_top"),
         ("thigh_f", "hip", "kn_f"), ("shin_f", "kn_f", "ft_f"), ("foot_f", "ft_f", "toe_f"),
         ("upper_f", "sh_f", "el_f"), ("fore_f", "el_f", "ha_f"), ("hand_f", "ha_f", "hand_tip_f"),
         ("weapon", "weapon_grip", "wtip")]

ARM_POSE_CYCLES = {
    "idle8": (0, 0, 0, 0, 0, 0, 0, 0),
    "walk8": (0, 1, 7, 1, 0, 1, 7, 0),
    "run": (7, 1, 7, 1, 7, 1),
    "ready": (2, 2),
    "atk_slash": (2, 3, 5, 3, 1, 0),
    "atk_thrust": (1, 3, 3, 1, 0, 0),
    "atk_overhead": (4, 5, 4, 5, 0, 0),
    "atk_draw": (6, 3, 5, 3, 7, 0),
    "cast": (2, 4),
    "chant": (2, 4, 5, 4),
    "cast_bolt": (2, 4),
    "cast_area": (4, 5),
    "cast_heal": (2, 4),
    "cast_ward": (2, 4),
    "cast_summon": (4, 5),
    "cast_void": (4, 5),
    "item": (1, 2, 1, 0),
    "hurt": (6, 7, 0),
    "evade": (7, 1),
    "guard": (2, 6),
    "ko": (7, 7),
    "collapse": (7, 0, 7, 0),
    "victory2": (4, 9, 8, 0),
    "facepalm": (2, 2, 2, 2),
    "shrug": (8, 9, 8),
    "crossarms": (6, 6),
    "scratch": (4, 4, 4),
    "point": (3, 3),
    "talk": (1, 8, 1, 8),
    "nod": (1, 0, 1, 0),
    "rei": (0, 6, 6, 6, 0, 0),
    "seiza": (6, 6),
    "seiza_rei": (6, 6, 0),
    "think": (2, 0),
    "surprise": (4, 5),
    "laugh": (8, 9),
    "squat": (6, 2, 7, 2, 0),
    "celebration": (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
}


_CAST = {}


def pose_data(T, kind, i):
    if kind in s2.V4_KINDS:
        return s2.pose_v4(T, kind, i)
    return s2.pose(kind, i, s2.STYLE.get(T["weapon"], "thrust"),
                   spear=T["weapon"] in ("yari", "naginata"))


def weapon_sheathed(T, kind, i):
    return bool(T.get("idle") == "iai" and T["weapon"] == "katana" and
                pose_data(T, kind, i).get("sheathed", False))


def traveler(key):
    """The rig definition (T) behind a sheet: trav_<k>[__<weapon>_<hat>] (gen_sprites2d + look_variant),
    side_<k> (gen_sidecast: cast, crew, hirelings), hum_<k> (gen_human_enemies). None if unknown (npc_ ...)."""
    if not _CAST:
        _a, sys.argv = sys.argv, [sys.argv[0]]
        try:
            import gen_sidecast as sc
            import gen_human_enemies as he
            for c in sc.CAST:
                _CAST["side_" + c["key"]] = (sc.config, c)
            for c in he.ENEMIES:
                _CAST["hum_" + c["key"]] = (he.config, c)
        except Exception as ex:
            print("rig: cast tables unavailable:", ex)
        finally:
            sys.argv = _a
    if key in _CAST:
        cfg, c = _CAST[key]
        return cfg(c)
    if key.startswith("trav_"):
        base, _, look = key[5:].partition("__")
        T = next((t for t in s2.TRAVELERS if t["key"] == base), None)
        if T is not None and look:
            w, _, h = look.partition("_")
            try:
                T = s2.look_variant(T, w, None if h in ("", "own") else h)
            except Exception:
                pass
        return T
    return None


def joints(T, kind, i):
    if kind in s2.FB_KINDS:
        return None
    P = pose_data(T, kind, i)
    P = s2.mark_upright(T, P, kind)
    P = s2.stature(T, s2.build_pose(T, P))
    if P.get("_upright"):
        P = s2.upright(P)
    P = s2.rig_arms(T, s2.rig_legs(T, P))
    J = {k: np.array(v, float) for k, v in P.items()
         if isinstance(v, tuple) and len(v) == 2 and k in ("sh_b", "el_b", "ha_b", "sh_f", "el_f", "ha_f", "hip",
                                                            "kn_b", "ft_b", "kn_f", "ft_f")}
    J["shm"] = (J["sh_b"] + J["sh_f"]) / 2.0
    J["weapon_grip"] = J["ha_f"].copy()
    torso = J["shm"] - J["hip"]
    J["hipd"] = J["hip"] + 4.0 * torso / max(1e-6, np.linalg.norm(torso))
    waist_axis = np.array([-torso[1], torso[0]]) / max(1e-6, np.linalg.norm(torso))
    waist_center = J["hip"] + 0.45 * torso
    waist_half = max(4.0, 0.3 * np.linalg.norm(J["kn_f"] - J["hip"]))
    J["waistline_b"] = waist_center - waist_axis * waist_half
    J["waistline_f"] = waist_center + waist_axis * waist_half
    J["neck"] = np.asarray(s2.head_anchor(P), float)
    J["head_top"] = J["neck"] + np.array([0.0, -19.5])
    for side in ("b", "f"):
        pitch = math.radians(float(P.get("pitch_" + side, 0.0)))
        J["toe_" + side] = J["ft_" + side] + 5.0 * np.array([math.cos(pitch), math.sin(pitch)])
        arm = J["ha_" + side] - J["el_" + side]
        J["hand_tip_" + side] = J["ha_" + side] + 2.5 * arm / max(1e-6, np.linalg.norm(arm))
    a = math.radians(float(P.get("wang", 0.0)))
    J["wtip"] = J["ha_f"] + 26.0 * np.array([math.cos(a), math.sin(a)])
    return J


def bbox(a):
    ys, xs = np.nonzero(a)
    return (xs.min(), ys.min(), xs.max(), ys.max()) if len(xs) else None


def seg_dist(px, a, b):
    ab = b - a
    t = np.clip(((px - a) @ ab) / max(1e-6, ab @ ab), 0, 1)
    return np.linalg.norm(px - (a + t[:, None] * ab), axis=1)


WEAPON_ROT = 0.25          # the weapon keeps the master's hold: a quarter of the rig's swing
ARM_ROT = 1.0


def weapon_reach(master, J):
    """The weapon's real length on the master: the farthest solid pixel along the hand->tip direction, near the line."""
    ys, xs = np.nonzero(master[..., 3] >= 128)
    px = np.stack([xs, ys], 1).astype(float)
    a, b = J.get("weapon_grip", J["ha_f"]), J["wtip"]
    u = (b - a) / max(1e-6, np.linalg.norm(b - a))
    along = (px - a) @ u
    perp = np.abs((px - a) @ np.array([-u[1], u[0]]))
    on = (perp <= 1.6 * ZF) & (along > 0)
    L = float(along[on].max()) if on.any() else 26.0
    J["wtip"] = a + u * max(8.0, L + 1)
    return J


def smooth_labels(lab, passes=2):
    """Mode filter + small islands folded into their neighbours (the nearest-bone cut is noisy at borders)."""
    import cv2
    h, w = lab.shape
    for _ in range(passes):
        out = lab.copy()
        for y in range(h):
            for x in range(w):
                if lab[y, x] < 0:
                    continue
                nb = lab[max(0, y - 1):y + 2, max(0, x - 1):x + 2].ravel()
                nb = nb[nb >= 0]
                vals, cnt = np.unique(nb, return_counts=True)
                if cnt.max() >= 6 and vals[cnt.argmax()] != lab[y, x]:
                    out[y, x] = vals[cnt.argmax()]
        lab = out
    for p in np.unique(lab[lab >= 0]):
        n, cc, st, _ = cv2.connectedComponentsWithStats((lab == p).astype(np.uint8), connectivity=8)
        if n <= 2:
            continue
        keep = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        for c in range(1, n):
            if c == keep or st[c, cv2.CC_STAT_AREA] > 8 * ZF * ZF:
                continue
            m = cc == c
            ring = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~m & (lab >= 0)
            if ring.any():
                v, k = np.unique(lab[ring], return_counts=True)
                lab[m] = v[k.argmax()]
    return lab


def fill_seams(out, sil):
    """Holes inside the drawn figure (a joint opened by a rotation) take a neighbour's colour."""
    import cv2
    a = (out[..., 3] > 0).astype(np.uint8)
    span = 2 * ZF + 1
    closed = cv2.morphologyEx(a, cv2.MORPH_CLOSE, np.ones((span, span), np.uint8)).astype(bool)
    holes = closed & ~a.astype(bool)
    for y, x in zip(*np.nonzero(holes)):
        nb = out[max(0, y - 1):y + 2, max(0, x - 1):x + 2].reshape(-1, 4)
        nb = nb[nb[:, 3] > 0]
        if len(nb):
            out[y, x] = nb[len(nb) // 2]
    return out


def labels(master, J, weapon=None):
    """Each master pixel -> the nearest part; long weapons keep the shaft behind the grip with them."""
    if "weapon_grip" not in J:
        J["weapon_grip"] = J["ha_f"].copy()
    J = weapon_reach(master, J)
    ys, xs = np.nonzero(master[..., 3] > 0)
    px = np.stack([xs, ys], 1).astype(float)
    d = np.stack([seg_dist(px, J[a], J[b]) for _n, a, b in PARTS], 1)
    front_grip = np.linalg.norm(px - J["ha_f"], axis=1) <= 2.2 * ZF
    for side in ("b", "f"):
        hi = [p[0] for p in PARTS].index("hand_" + side)
        near_hand = np.linalg.norm(px - J["ha_" + side], axis=1) <= 2.2 * ZF
        d[:, hi] = np.where(near_hand, d[:, hi] - 1.5 * ZF, 99.0)
    wi = [p[0] for p in PARTS].index("weapon")
    grip = J.get("weapon_grip", J["ha_f"])
    axis = J["wtip"] - grip
    length = max(1e-6, np.linalg.norm(axis))
    u = axis / length
    rel = px - grip
    along = rel @ u
    perp = np.abs(rel @ np.array([-u[1], u[0]]))
    back = 1.4 * length if weapon in ("yari", "naginata", "bo", "staff", "shakujo") else 5.0 * ZF
    on_weapon = (perp <= 1.6 * ZF) & (along >= -back) & (along <= length + 1.6 * ZF)
    d[:, wi] = np.where(on_weapon & ~front_grip, -3.0 * ZF, 99.0)
    # the head (well above the shoulders) is body, whatever the arms say; so is the torso core - in side view the
    # back arm lies over the torso, and only what sticks out of the body may swing (Rensei's chest tore off with it)
    bi = [p[0] for p in PARTS].index("body")
    head = ys < J["neck"][1] + 1
    core_r = max(3.0, 0.55 * np.linalg.norm(J["sh_f"] - J["sh_b"]) + 1.5)
    core = d[:, bi] <= core_r
    arm_i = [i for i, p in enumerate(PARTS) if p[0] in ("upper_b", "fore_b", "upper_f", "fore_f")]
    lab = np.full(master.shape[:2], -1, int)
    best = d.argmin(1)
    best[head & (best != wi)] = bi
    best[core & np.isin(best, arm_i)] = bi
    # the waist / upper legs: everything near the hip, so the hips don't tear between torso and thighs
    wai = [p[0] for p in PARTS].index("waist")
    leg_len = np.linalg.norm(J["kn_f"] - J["hip"])
    near_hip = np.linalg.norm(px - J["hip"], axis=1) <= max(3.0, 0.45 * leg_len)
    legs_i = [i for i, p in enumerate(PARTS) if p[0] in ("thigh_b", "thigh_f", "shin_b", "shin_f")]
    best[near_hip & (np.isin(best, legs_i) | (best == bi)) & (ys >= J["hip"][1] - 2)] = wai
    waistline_i = [p[0] for p in PARTS].index("waistline")
    waist_b, waist_f = J["waistline_b"], J["waistline_f"]
    waist_axis = (waist_f - waist_b) / max(1e-6, np.linalg.norm(waist_f - waist_b))
    waist_normal = np.array([-waist_axis[1], waist_axis[0]])
    waist_center = (waist_b + waist_f) / 2.0
    waist_rel = px - waist_center
    waistline = ((np.abs(waist_rel @ waist_axis) <= np.linalg.norm(waist_f - waist_b) / 2 + ZF) &
                 (np.abs(waist_rel @ waist_normal) <= 2.0 * ZF))
    hi = [p[0] for p in PARTS].index("head")
    best[head & (best != wi)] = hi
    lab[ys, xs] = best
    lab = smooth_labels(lab, 2 * ZF)
    waist_candidates = [bi, wai] + [i for i, p in enumerate(PARTS) if p[0] in ("thigh_b", "thigh_f")]
    wl_indices = np.flatnonzero(waistline)
    take = np.isin(lab[ys[wl_indices], xs[wl_indices]], waist_candidates)
    lab[ys[wl_indices[take]], xs[wl_indices[take]]] = waistline_i
    hand_f = [p[0] for p in PARTS].index("hand_f")
    lab[ys[front_grip], xs[front_grip]] = hand_f
    return lab


def apply_label_masks(lab, masks):
    if not masks:
        return lab
    names = {part[0]: i for i, part in enumerate(PARTS)}
    for name, mask in masks.items():
        if name not in names:
            raise ValueError("Unknown rig part for label mask: %s" % name)
        mask = np.asarray(mask, dtype=bool)
        if mask.shape != lab.shape:
            raise ValueError("Label mask for %s does not match the master size" % name)
        lab[mask] = names[name]
    return lab


def xform(a0, b0, a1, b1):
    """Rigid 2D transform taking segment a0->b0 to a1->b1 (rotation about a, then translation)."""
    t0 = math.atan2(*(b0 - a0)[::-1])
    t1 = math.atan2(*(b1 - a1)[::-1])
    r = t1 - t0
    c, s = math.cos(r), math.sin(r)
    R = np.array([[c, -s], [s, c]])
    return R, a1 - R @ a0


def limb_transform(a0, b0, a1, b1, rotation_scale=1.0):
    """Map a limb bone to its target length while optionally damping its rotation."""
    source = b0 - a0
    target = b1 - a1
    source_len, target_len = np.linalg.norm(source), np.linalg.norm(target)
    source_dir = source / max(1e-6, source_len)
    target_dir = target / max(1e-6, target_len)
    source_angle = math.atan2(source_dir[1], source_dir[0])
    target_angle = math.atan2(target_dir[1], target_dir[0])
    delta = (target_angle - source_angle + math.pi) % (2 * math.pi) - math.pi
    angle = source_angle + delta * rotation_scale
    direction = np.array([math.cos(angle), math.sin(angle)])
    normal = np.array([-direction[1], direction[0]])
    source_normal = np.array([-source_dir[1], source_dir[0]])
    R = (target_len / max(1e-6, source_len)) * np.outer(direction, source_dir) + np.outer(normal, source_normal)
    return R, a1 - R @ a0


def arm_pose_index(kind, frame, side, arm_pose_sets):
    """Choose a drawn arm pose for an animation frame; all cycles use the ten generated pose variants."""
    poses = arm_pose_sets.get(side, ())
    if not poses:
        return None
    cycle = ARM_POSE_CYCLES.get(kind)
    if cycle:
        return cycle[frame % len(cycle)] % len(poses)
    return frame % len(poses)


def draw_arm_pose(out, arm_pose, shoulder, hand):
    """Align a separately drawn full arm between its shoulder and hand without shearing its shape."""
    image = np.asarray(arm_pose["image"], dtype=np.uint8)
    source_anchor = np.asarray(arm_pose["anchor"], dtype=float)
    source_tip = np.asarray(arm_pose["tip"], dtype=float)
    target_anchor = np.asarray(shoulder, dtype=float)
    target_tip = np.asarray(hand, dtype=float)
    source_vector, target_vector = source_tip - source_anchor, target_tip - target_anchor
    source_length, target_length = np.linalg.norm(source_vector), np.linalg.norm(target_vector)
    if image.ndim != 3 or image.shape[2] != 4 or source_length < 1e-3 or target_length < 1e-3:
        return out

    angle = math.atan2(target_vector[1], target_vector[0]) - math.atan2(source_vector[1], source_vector[0])
    scale = target_length / source_length
    c, s = math.cos(angle), math.sin(angle)
    transform = scale * np.array([[c, -s], [s, c]])
    inverse = np.linalg.inv(transform)
    ys, xs = np.nonzero(image[..., 3])
    if not len(xs):
        return out
    corners = np.array([[xs.min(), ys.min()], [xs.max() + 1, ys.min()],
                        [xs.min(), ys.max() + 1], [xs.max() + 1, ys.max() + 1]], dtype=float)
    transformed = (corners - source_anchor) @ transform.T + target_anchor
    h, w = out.shape[:2]
    x0 = max(0, int(np.floor(transformed[:, 0].min())) - 1)
    x1 = min(w, int(np.ceil(transformed[:, 0].max())) + 1)
    y0 = max(0, int(np.floor(transformed[:, 1].min())) - 1)
    y1 = min(h, int(np.ceil(transformed[:, 1].max())) + 1)
    if x0 >= x1 or y0 >= y1:
        return out

    yy, xx = np.mgrid[y0:y1, x0:x1]
    dest = np.stack([xx.ravel(), yy.ravel()], axis=1).astype(float)
    source = (dest - target_anchor) @ inverse.T + source_anchor
    sx = np.rint(source[:, 0]).astype(int)
    sy = np.rint(source[:, 1]).astype(int)
    valid = (sx >= 0) & (sx < image.shape[1]) & (sy >= 0) & (sy < image.shape[0])
    pixels = np.zeros((len(dest), 4), dtype=np.uint8)
    pixels[valid] = image[sy[valid], sx[valid]]
    visible = pixels[:, 3] > 0
    if not visible.any():
        return out

    dy, dx = dest[visible, 1].astype(int), dest[visible, 0].astype(int)
    source_pixels = pixels[visible].astype(float)
    destination_pixels = out[dy, dx].astype(float)
    source_alpha = source_pixels[:, 3:4] / 255.0
    destination_alpha = destination_pixels[:, 3:4] / 255.0
    alpha = source_alpha + destination_alpha * (1.0 - source_alpha)
    rgb = (source_pixels[:, :3] * source_alpha +
           destination_pixels[:, :3] * destination_alpha * (1.0 - source_alpha))
    out[dy, dx, :3] = np.where(alpha > 0, rgb / np.maximum(alpha, 1e-6), 0).round().astype(np.uint8)
    out[dy, dx, 3] = (alpha[:, 0] * 255).round().astype(np.uint8)
    return out


def rig_frame(master, lab, J0, J1, weapon_rotation=WEAPON_ROT, hide_weapon=False, arm_pose_sets=None,
              pose_kind=None, pose_index=0):
    h, w = master.shape[:2]
    out = np.zeros_like(master)
    yy, xx = np.mgrid[0:h, 0:w]
    q = np.stack([xx.ravel(), yy.ravel()], 1).astype(float)
    if arm_pose_sets:
        arm_parts = {i for i, part in enumerate(PARTS) if part[0] in
                     ("upper_b", "fore_b", "hand_b", "upper_f", "fore_f", "hand_f")}
        lab = lab.copy()
        lab[np.isin(lab, tuple(arm_parts))] = -1
    for pi, (name, a, b) in enumerate(PARTS):
        if arm_pose_sets and name == "body":
            pose_index_ = arm_pose_index(pose_kind, pose_index, "b", arm_pose_sets)
            if pose_index_ is not None:
                out = draw_arm_pose(out, arm_pose_sets["b"][pose_index_], J1["sh_b"], J1["hand_tip_b"])
        if arm_pose_sets and name == "upper_f":
            pose_index_ = arm_pose_index(pose_kind, pose_index, "f", arm_pose_sets)
            if pose_index_ is not None:
                out = draw_arm_pose(out, arm_pose_sets["f"][pose_index_], J1["sh_f"], J1["hand_tip_f"])
        if hide_weapon and name == "weapon":
            continue
        if name == "waist":                                # follows the hip, never turns
            R, t = np.eye(2), J1["hip"] - J0["hip"]
        elif name == "waistline":
            R, t = xform(J0[a], J0[b], J1[a], J1[b])
        elif name == "weapon":                             # moves with the hand, a damped share of the rig's turn
            d0, d1 = J0[b] - J0[a], J1[b] - J1[a]
            r = (math.atan2(d1[1], d1[0]) - math.atan2(d0[1], d0[0]) + math.pi) % (2 * math.pi) - math.pi
            r *= weapon_rotation
            c_, s_ = math.cos(r), math.sin(r)
            R = np.array([[c_, -s_], [s_, c_]])
            t = J1[a] - R @ J0[a]
        elif name.startswith(("thigh_", "shin_", "foot_", "upper_", "fore_", "hand_")):
            rotation = ARM_ROT if name.startswith(("upper_", "fore_")) else 1.0
            R, t = limb_transform(J0[a], J0[b], J1[a], J1[b], rotation)
        else:
            R, t = xform(J0[a], J0[b], J1[a], J1[b])
        src = (q - t) @ np.linalg.inv(R).T
        sx, sy = np.rint(src[:, 0]).astype(int), np.rint(src[:, 1]).astype(int)
        ok = (sx >= 0) & (sx < w) & (sy >= 0) & (sy < h)
        hit = np.zeros(len(q), bool)
        hit[ok] = lab[sy[ok], sx[ok]] == pi
        oy, ox = q[hit, 1].astype(int), q[hit, 0].astype(int)
        out[oy, ox] = master[sy[hit], sx[hit]]
    out = fill_seams(out, master[..., 3] > 0)
    # (user: "clear the misc sprites from infront of her") small islands cut loose from the figure go
    import cv2
    solid = (out[..., 3] >= 128).astype(np.uint8)
    n, cc, st, _ = cv2.connectedComponentsWithStats(solid, connectivity=8)
    if n > 2:
        main_c = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        for c in range(1, n):
            if c != main_c and st[c, cv2.CC_STAT_AREA] < 28 * ZF * ZF:
                out[cc == c] = 0
    shadow = (master[..., 3] > 0) & (master[..., 3] < 128)  # the soft ground shadow stays put
    out[shadow & (out[..., 3] == 0)] = master[shadow & (out[..., 3] == 0)]
    return out


def to_master_space(J, rig_box, m_box):
    """Map rig joint coords onto the master: same height, feet on the same line, same centre."""
    s = (m_box[3] - m_box[1] + 1) / float(rig_box[3] - rig_box[1] + 1)
    rc = np.array([(rig_box[0] + rig_box[2]) / 2.0, rig_box[3]])
    mc = np.array([(m_box[0] + m_box[2]) / 2.0, m_box[3]])
    return {k: (v - rc) * s + mc for k, v in J.items()}


def apply_master_joints(target, base, overrides):
    """Offset every pose from the rig's base joints so the generated master remains unchanged at rest."""
    if not overrides:
        return target
    adjusted = {k: (v + np.asarray(overrides[k], float) - base[k]) if k in overrides else v
                for k, v in target.items()}
    if "weapon_grip" in adjusted:
        adjusted["weapon_grip"] = adjusted["ha_f"].copy()
        if "weapon_grip" in overrides:
            adjusted["weapon_grip"] += np.asarray(overrides["weapon_grip"], float) - base["weapon_grip"]
    for side in ("b", "f"):
        if "hand_tip_" + side not in adjusted:
            continue
        arm = adjusted["ha_" + side] - adjusted["el_" + side]
        adjusted["hand_tip_" + side] = adjusted["ha_" + side] + 2.5 * arm / max(1e-6, np.linalg.norm(arm))
    return adjusted


def scale_leg_motion(target, rest, scale):
    """Scale pose-driven leg spread while preserving the master's rest-pose joints."""
    if scale == 1.0:
        return target
    adjusted = {k: v.copy() for k, v in target.items()}
    for side in ("b", "f"):
        for joint in ("kn_", "ft_", "toe_"):
            name = joint + side
            if name in adjusted and name in rest:
                rest_rel = rest[name] - rest["hip"]
                pose_rel = target[name] - target["hip"]
                adjusted[name] = target["hip"] + rest_rel + scale * (pose_rel - rest_rel)
    return adjusted


def scale_arm_motion(target, rest, scale):
    """Scale pose-driven arm reach while preserving the master's rest-pose joints."""
    if scale == 1.0:
        return target
    adjusted = {k: v.copy() for k, v in target.items()}
    for side in ("b", "f"):
        shoulder = "sh_" + side
        for joint in ("el_", "ha_", "hand_tip_"):
            name = joint + side
            if name in adjusted and name in rest:
                rest_rel = rest[name] - rest[shoulder]
                pose_rel = target[name] - target[shoulder]
                adjusted[name] = target[shoulder] + rest_rel + scale * (pose_rel - rest_rel)
    return adjusted


def scale_body_motion(target, rest, scale):
    """Reduce torso and head travel while keeping the arms anchored to the scaled shoulders."""
    if scale == 1.0:
        return target
    adjusted = {k: v.copy() for k, v in target.items()}
    for key in ("hip", "shm", "hipd", "neck", "head_top", "waistline_b", "waistline_f",
                "sh_b", "sh_f"):
        if key in adjusted and key in rest:
            adjusted[key] = rest[key] + scale * (target[key] - rest[key])
    return adjusted


def rig_frames(key, master, frame_ids, z=1, master_joints=None, weapon_rotation=WEAPON_ROT,
           leg_motion_scale=1.0, arm_motion_scale=1.0, body_motion_scale=1.0,
           arm_pose_sets=None, label_masks=None):
    global ZF
    ZF = z
    T = traveler(key)
    if T is None:
        ZF = 1
        return {}, None
    k0, i0 = s2.FRAMES[0]
    rig0 = np.asarray(s2.frame(T, k0, i0))
    rbox = bbox(rig0[..., 3] >= 128)
    mbox = bbox(master[..., 3] >= 128)
    base = to_master_space(joints(T, k0, i0), rbox, mbox)
    J0 = apply_master_joints(base.copy(), base, master_joints)
    lab = apply_label_masks(labels(master, J0, T.get("weapon")), label_masks)
    reach = np.linalg.norm(J0["wtip"] - J0["weapon_grip"])
    out = {}
    for n in frame_ids:
        kind, i = s2.FRAMES[n]
        J = joints(T, kind, i)
        if J is None:
            continue
        J = apply_master_joints(to_master_space(J, rbox, mbox), base, master_joints)
        J = scale_body_motion(J, J0, body_motion_scale)
        J = scale_leg_motion(J, J0, leg_motion_scale)
        J = scale_arm_motion(J, J0, arm_motion_scale)
        u = J["wtip"] - J["weapon_grip"]
        J["wtip"] = J["weapon_grip"] + u / max(1e-6, np.linalg.norm(u)) * reach
        if T["weapon"] in ("yari", "naginata", "bo", "staff", "shakujo") and (
                kind.startswith(("cast", "chant")) or kind == "surprise"):
            J["weapon_grip"] = J["ha_b"].copy()
            J["wtip"] = J["weapon_grip"] + J0["wtip"] - J0["weapon_grip"]
        out[n] = rig_frame(master, lab, J0, J, weapon_rotation, weapon_sheathed(T, kind, i),
                           arm_pose_sets=arm_pose_sets, pose_kind=kind, pose_index=i)
    ZF = 1
    return out, lab


# ---- Conversation gestures (user 2026-11-15: "now we can add animations to even conversations. like when hiruma
# says 'who did my lord marry' the pixel art can do a face palm as well") - one extra sheet row, side view.
GESTURES = [("facepalm", 4), ("shrug", 3), ("crossarms", 2), ("scratch", 3), ("point", 2)]   # 14 frames = 1 row
EXTENDED_GESTURES = [("squat", 5), ("celebration", 10)]
GESTURE_SPD = {"facepalm": 5.0, "shrug": 5.0, "crossarms": 4.0, "scratch": 7.0, "point": 5.0}


def ik(S, T, L1, L2):
    """Two-bone IK: the elbow for shoulder S reaching T, bent downward (the natural side for these gestures)."""
    d = T - S
    dist = float(np.linalg.norm(d))
    dist = min(max(dist, 1e-3), L1 + L2 - 1e-3)
    u = d / max(1e-6, np.linalg.norm(d))
    a = (L1 * L1 - L2 * L2 + dist * dist) / (2 * dist)
    hh = math.sqrt(max(0.0, L1 * L1 - a * a))
    P = S + a * u
    perp = np.array([-u[1], u[0]])
    e1, e2 = P + hh * perp, P - hh * perp
    return e1 if e1[1] >= e2[1] else e2


def gesture_joints(J0, head_c, name, k, n):
    """Joints for frame k of a gesture (master space), plus the head's tilt in degrees (+ = chin down)."""
    J = {a: b.copy() for a, b in J0.items()}
    Lf1 = np.linalg.norm(J0["el_f"] - J0["sh_f"])
    Lf2 = np.linalg.norm(J0["ha_f"] - J0["el_f"])
    Lb1 = np.linalg.norm(J0["el_b"] - J0["sh_b"])
    Lb2 = np.linalg.norm(J0["ha_b"] - J0["el_b"])
    face = head_c + np.array([3.0, 2.0])
    tilt = 0.0
    if name == "facepalm":                                 # the hand comes up, the head drops into it
        f = (0.55, 1.0, 1.0, 1.0)[k]
        tgt = J0["ha_f"] + (face - J0["ha_f"]) * f
        tilt = (4.0, 12.0, 14.0, 12.0)[k]
        J["ha_f"] = tgt + np.array([0.0, (0, 0, 1, 0)[k]])
        J["el_f"] = ik(J["sh_f"], J["ha_f"], Lf1, Lf2)
    elif name == "shrug":                                  # shoulders up, open hands out low
        up = (1, 2, 1)[k]
        for s in ("sh_f", "sh_b"):
            J[s] = J[s] + np.array([0.0, -up])
        J["ha_f"] = J["sh_f"] + np.array([Lf1 * 0.6 + 3, Lf1 * 0.7])
        J["ha_b"] = J["sh_b"] + np.array([-(Lb1 * 0.5 + 2), Lb1 * 0.7])
        J["el_f"] = ik(J["sh_f"], J["ha_f"], Lf1, Lf2)
        J["el_b"] = ik(J["sh_b"], J["ha_b"], Lb1, Lb2)
        tilt = (-4.0, -8.0, -4.0)[k]
    elif name == "crossarms":                              # both forearms across the chest
        mid = (J0["sh_f"] + J0["sh_b"]) / 2 + np.array([2.0, Lf1 * 0.75])
        J["ha_f"] = mid + np.array([-2.0, (0, 1)[k]])
        J["ha_b"] = mid + np.array([3.0, 0.0])
        J["el_f"] = ik(J["sh_f"], J["ha_f"], Lf1, Lf2)
        J["el_b"] = ik(J["sh_b"], J["ha_b"], Lb1, Lb2)
    elif name == "scratch":                                # the hand at the back of the head, scratching
        J["ha_f"] = head_c + np.array([-2.0, -3.0 + (0, -1, 0)[k]])
        J["el_f"] = ik(J["sh_f"], J["ha_f"], Lf1, Lf2)
        tilt = (6.0, 8.0, 6.0)[k]
    elif name == "point":                                  # the arm straight out ahead
        J["ha_f"] = J["sh_f"] + np.array([Lf1 + Lf2 - 1.0, -1.0 + (0, 1)[k]])
        J["el_f"] = (J["sh_f"] + J["ha_f"]) / 2
    elif name == "squat":
        depth = (1.0, 3.0, 6.0, 6.0, 2.0)[k]
        upper_shift = np.array([1.0, depth * 0.55])
        J["hip"] += np.array([0.0, depth])
        J["sh_b"] += upper_shift
        J["sh_f"] += upper_shift
        J["shm"] = (J["sh_b"] + J["sh_f"]) / 2.0
        J["kn_b"] += np.array([-1.0, 1.0])
        J["kn_f"] += np.array([3.0, 1.0])
        J["ft_b"] += np.array([-2.0, 0.0])
        J["ft_f"] += np.array([2.0, 0.0])
        J["ha_f"] = J["sh_f"] + np.array([Lf1 * 0.75 + 2.0, Lf2 * 0.65])
        J["ha_b"] = J["sh_b"] + np.array([Lb1 * 0.2, Lb2 * 0.9])
        J["el_f"] = ik(J["sh_f"], J["ha_f"], Lf1, Lf2)
        J["el_b"] = ik(J["sh_b"], J["ha_b"], Lb1, Lb2)
        tilt = (2.0, 5.0, 8.0, 7.0, 3.0)[k]
    elif name == "celebration":
        bob = (0.0, -1.0, -3.0, -1.0, 0.0, -1.0, -3.0, -1.0, 0.0, 0.0)[k]
        lean = (0.0, 1.0, 2.0, 1.0, 0.0, -1.0, -2.0, -1.0, 0.0, 0.0)[k]
        J["hip"] += np.array([lean * 0.35, 0.0])
        for side in ("b", "f"):
            J["sh_" + side] += np.array([lean, bob])
        J["shm"] = (J["sh_b"] + J["sh_f"]) / 2.0
        step_f = ((0, 0), (1, -1), (2, -2), (1, -1), (0, 0),
                  (-1, -1), (-2, -2), (-1, -1), (0, 0), (0, 0))[k]
        step_b = ((0, 0), (-1, -1), (-2, -2), (-1, -1), (0, 0),
                  (1, -1), (2, -2), (1, -1), (0, 0), (0, 0))[k]
        J["kn_f"] += np.array([step_f[0] * 0.5, -step_f[1] * 0.4])
        J["kn_b"] += np.array([step_b[0] * 0.5, -step_b[1] * 0.4])
        J["ft_f"] += np.array(step_f, dtype=float)
        J["ft_b"] += np.array(step_b, dtype=float)
        high_f = k in (1, 2, 3, 6, 7, 8)
        high_b = k in (2, 3, 7, 8)
        J["ha_f"] = J["sh_f"] + np.array([Lf1 * 0.9, -Lf1 * (0.7 if high_f else 0.15)])
        J["ha_b"] = J["sh_b"] + np.array([-Lb1 * 0.25, -Lb1 * (0.75 if high_b else -0.15)])
        J["el_f"] = ik(J["sh_f"], J["ha_f"], Lf1, Lf2)
        J["el_b"] = ik(J["sh_b"], J["ha_b"], Lb1, Lb2)
        tilt = (0.0, -3.0, -5.0, -2.0, 0.0, 1.0, -2.0, -4.0, -1.0, 0.0)[k]
    for side in ("b", "f"):
        arm = J["ha_" + side] - J["el_" + side]
        J["hand_tip_" + side] = J["ha_" + side] + 2.5 * arm / max(1e-6, np.linalg.norm(arm))
    return J, tilt


def gesture_frames(key, master, master_joints=None):
    """The 14 gesture frames (row order of GESTURES) for a sheet's side master, or None (no rig / no master)."""
    global ZF
    ZF = 1
    T = traveler(key)
    if T is None or master is None:
        ZF = 1
        return None
    k0, i0 = s2.FRAMES[0]
    rig0 = np.asarray(s2.frame(T, k0, i0))
    rbox, mbox = bbox(rig0[..., 3] >= 128), bbox(master[..., 3] >= 128)
    if not rbox or not mbox:
        ZF = 1
        return None
    base = to_master_space(joints(T, k0, i0), rbox, mbox)
    J0 = apply_master_joints(base.copy(), base, master_joints)
    lab = labels(master, J0, T.get("weapon"))
    names = [p[0] for p in PARTS]
    hy, hx = np.nonzero(lab == names.index("head"))
    head_c = np.array([hx.mean(), hy.mean()]) if len(hx) else J0["shm"] + np.array([0.0, -8.0])
    neck = J0["neck"]
    out = []
    for name, n in GESTURES:
        for k in range(n):
            J, tilt = gesture_joints(J0, head_c, name, k, n)
            out.append(gesture_frame(master, lab, J0, J, tilt, neck, head_c))
    ZF = 1
    return out


def arm_colours(master, lab, J0, head_c):
    """The sleeve (most common non-ink colour near the front upper arm) and the skin (warm colour on the face)."""
    h, w = master.shape[:2]
    ys, xs = np.nonzero(master[..., 3] >= 128)
    px = np.stack([xs, ys], 1).astype(float)
    rgb = master[ys, xs, :3].astype(int)
    lum = rgb.sum(1)
    near = seg_dist(px, J0["sh_f"], J0["el_f"]) <= 2.5
    pick = near & (lum > 60)

    def mode(m):
        if not m.any():
            return None
        keys, cnt = np.unique(rgb[m], axis=0, return_counts=True)
        return tuple(int(v) for v in keys[cnt.argmax()])
    sleeve = mode(pick) or (90, 90, 110)
    warm = (rgb[:, 0] > rgb[:, 1] + 15) & (rgb[:, 1] > rgb[:, 2]) & (rgb[:, 0] > 110)
    face = np.linalg.norm(px - head_c, axis=1) <= 6
    skin = mode(warm & face) or mode(warm) or (206, 150, 112)
    ink = tuple(int(v) for v in rgb[lum.argmin()]) if len(rgb) else (0, 0, 0)
    return sleeve, skin, ink


def draw_arm_px(out, S, E, H, sleeve, skin, ink, z=1):
    """A clean pixel-art arm: sleeve capsules shoulder->elbow (r 2) and elbow->hand (r 1.5), a darker underside,
    a 1-px ink outline, a 2x2 skin hand. z=2: drawn on a 2x canvas (joints already x2) - the same arm with a 1-px
    outline at the finer grid (the HD sheets' extra detail)."""
    h, w = out.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    px = np.stack([xx.ravel(), yy.ravel()], 1).astype(float)
    d1 = seg_dist(px, S, E).reshape(h, w)
    d2 = seg_dist(px, E, H).reshape(h, w)
    body = (d1 <= 2.0 * z) | (d2 <= 1.5 * z)
    edge = ((d1 <= 2.0 * z + 1) | (d2 <= 1.5 * z + 1)) & ~body
    dark = tuple(int(c * 0.7) for c in sleeve)
    under = body & (np.roll(body, -1, 0) == 0)             # the lowest sleeve row: shade
    out[edge & (out[..., 3] < 128)] = list(ink) + [255]
    out[edge & (out[..., 3] >= 128)] = list(ink) + [255]
    out[body] = list(sleeve) + [255]
    out[under & body] = list(dark) + [255]
    hx, hy = int(round(H[0])), int(round(H[1]))
    r = 1 if z == 1 else 2
    for dy in range(-r + 1, r + 1):
        for dx in range(-r + 1, r + 1):
            if 0 <= hy + dy - 1 < h and 0 <= hx + dx - 1 < w:
                out[hy + dy - 1, hx + dx - 1] = list(skin) + [255]
    if z > 1:                                              # a knuckle shade on the HD hand
        sk2 = tuple(int(c * 0.82) for c in skin)
        if 0 <= hy + r - 1 < h and 0 <= hx - r < w:
            out[hy + r - 1, max(0, hx - r):hx + r] = list(sk2) + [255]
    return out


def gesture_frames_hd(key, master, z=2, master_joints=None, arm_pose_sets=None, label_masks=None,
                      body_motion_scale=1.0):
    """The gesture row for the HD (z x) sheet: the rig body at 1x, upscaled (nearest), then the gesturing arms drawn
    at the z-times grid (finer outline and hands)."""
    global ZF
    ZF = z
    T = traveler(key)
    if T is None or master is None:
        ZF = 1
        return None
    k0, i0 = s2.FRAMES[0]
    rig0 = np.asarray(s2.frame(T, k0, i0))
    rbox, mbox = bbox(rig0[..., 3] >= 128), bbox(master[..., 3] >= 128)
    if not rbox or not mbox:
        ZF = 1
        return None
    base = to_master_space(joints(T, k0, i0), rbox, mbox)
    J0 = apply_master_joints(base.copy(), base, master_joints)
    lab = apply_label_masks(labels(master, J0, T.get("weapon")), label_masks)
    if arm_pose_sets:
        arm_parts = {i for i, part in enumerate(PARTS) if part[0] in
                     ("upper_b", "fore_b", "hand_b", "upper_f", "fore_f", "hand_f")}
        lab = lab.copy()
        lab[np.isin(lab, tuple(arm_parts))] = -1
    names = [p[0] for p in PARTS]
    hy, hx = np.nonzero(lab == names.index("head"))
    head_c = np.array([hx.mean(), hy.mean()]) if len(hx) else J0["shm"] + np.array([0.0, -8.0])
    neck = J0["neck"]
    sleeve, skin, ink = arm_colours(master, lab, J0, head_c)
    out = []
    for name, n in GESTURES + EXTENDED_GESTURES:
        for k in range(n):
            J, tilt = gesture_joints(J0, head_c, name, k, n)
            J = scale_body_motion(J, J0, body_motion_scale)
            f1 = gesture_frame(master, lab, J0, J, tilt, neck, head_c, arms=not arm_pose_sets)
            fz = np.repeat(np.repeat(f1, z, 0), z, 1)
            if arm_pose_sets:
                c = (z - 1) / 2.0
                for side in ("b", "f"):
                    pose_index_ = arm_pose_index(name, k, side, arm_pose_sets)
                    if pose_index_ is None:
                        continue
                    fz = draw_arm_pose(fz, arm_pose_sets[side][pose_index_],
                                       J["sh_" + side] * z + c,
                                       J["hand_tip_" + side] * z + c)
            else:
                c = (z - 1) / 2.0                              # pixel centres on the finer grid
                if np.linalg.norm(J["ha_b"] - J0["ha_b"]) > 1.5:
                    fz = draw_arm_px(fz, J["sh_b"] * z + c, J["el_b"] * z + c, J["ha_b"] * z + c,
                                     sleeve, skin, ink, z)
                fz = draw_arm_px(fz, J["sh_f"] * z + c, J["el_f"] * z + c, J["ha_f"] * z + c,
                                 sleeve, skin, ink, z)
            out.append(fz)
    ZF = 1
    return out


def front_gestures_hd(master, z=2):
    """Front-view gestures (facepalm_f, shrug_f, crossarms_f, scratch_f, point_f; 14 frames like GESTURES) from the
    front master: shoulders from the silhouette just under the head, the head from the pixels above the neck; the
    gesturing side's hanging sleeve is cut away (no third arm) and a fresh arm drawn on the z-times grid."""
    import cv2
    sol = master[..., 3] >= 128
    b = bbox(sol)
    if not b:
        return None
    H = b[3] - b[1] + 1
    neck_y = b[1] + int(round(H * 0.36))
    sh_y = neck_y + 2
    waist_y = b[1] + int(round(H * 0.62))
    xs = np.nonzero(sol[sh_y])[0]
    if len(xs) < 4:
        return None
    L, R = xs.min(), xs.max()
    cx = (L + R) / 2.0
    hy, hx = np.nonzero(sol[:neck_y])
    head_c = np.array([hx.mean(), hy.mean()]) if len(hx) else np.array([cx, b[1] + 6.0])
    head_top = b[1]
    sh = {"r": np.array([R - 2.0, sh_y]), "l": np.array([L + 2.0, sh_y])}   # r = the viewer's right
    upper = (waist_y - sh_y) * 0.55
    fore = (waist_y - sh_y) * 0.5
    ys_, xs_ = np.nonzero(sol)
    rgb = master[ys_, xs_, :3].astype(int)
    near = (np.abs(ys_ - sh_y - 3) <= 3) & ((xs_ >= R - 4) | (xs_ <= L + 4)) & (rgb.sum(1) > 60)
    if near.any():
        k_, c_ = np.unique(rgb[near], axis=0, return_counts=True)
        sleeve = tuple(int(v) for v in k_[c_.argmax()])
    else:
        sleeve = (90, 90, 110)
    warm = (rgb[:, 0] > rgb[:, 1] + 15) & (rgb[:, 1] > rgb[:, 2]) & (rgb[:, 0] > 110) & (ys_ < neck_y)
    if warm.any():
        k_, c_ = np.unique(rgb[warm], axis=0, return_counts=True)
        skin = tuple(int(v) for v in k_[c_.argmax()])
    else:
        skin = (206, 150, 112)
    ink = tuple(int(v) for v in rgb[rgb.sum(1).argmin()])

    def cut(fr, side):
        """The hanging sleeve on that side: the outer 4 columns from the shoulder to the waist, re-outlined."""
        out = fr.copy()
        x0, x1 = (R - 3, R + 1) if side == "r" else (L, L + 4)
        out[sh_y + 2:waist_y + 3, x0:x1] = 0
        a = (out[..., 3] >= 128).astype(np.uint8)
        edge = a.astype(bool) & ~cv2.erode(a, np.ones((3, 3), np.uint8)).astype(bool)
        band = np.zeros_like(edge)
        band[sh_y + 1:waist_y + 4, max(0, x0 - 2):x1 + 2] = True
        out[edge & band, :3] = ink
        return out

    def head_dip(fr, d):
        if not d:
            return fr
        out = fr.copy()
        top = fr[:neck_y].copy()
        out[:neck_y] = 0
        m = top[..., 3] > 0
        dst = out[d:neck_y + d]
        dst[m[:neck_y + d - d]] = top[m]
        return out

    plan = {
        "facepalm": [("r", lambda k: head_c + np.array([1.0, 3.0]), (1, 2, 2, 2))],
        "shrug": [("r", lambda k: sh["r"] + np.array([7.0, 9.0 - k]), (0, 0, 0)),
                  ("l", lambda k: sh["l"] + np.array([-7.0, 9.0 - k]), (0, 0, 0))],
        "crossarms": [("r", lambda k: np.array([cx - 2.0, sh_y + 8.0 + k]), (0, 0)),
                      ("l", lambda k: np.array([cx + 2.0, sh_y + 8.0]), (0, 0))],
        "scratch": [("r", lambda k: np.array([head_c[0] + 5.0, head_top + 4.0 - (k % 2)]), (1, 1, 1))],
        "point": [("r", lambda k: sh["r"] + np.array([upper + fore - 1.0, -1.0 + k]), (0, 0))],
    }
    frames = []
    for name, n in GESTURES:
        for k in range(n):
            arms = plan[name]
            f1 = master.copy()
            for side, _t, _d in arms:
                f1 = cut(f1, side)
            f1 = head_dip(f1, arms[0][2][k])
            fz = np.repeat(np.repeat(f1, z, 0), z, 1)
            c = (z - 1) / 2.0
            for side, tgt, _d in arms:
                S = sh[side]
                T_ = tgt(k)
                E = ik(S, T_, upper, fore)
                fz = draw_arm_px(fz, S * z + c, E * z + c, T_ * z + c, sleeve, skin, ink, z)
            frames.append(fz)
    return frames


def gesture_frame(master, lab, J0, J1, tilt, neck, head_c, arms=True):
    """Like rig_frame, plus: the head (body pixels above the neck) tilts about the neck; the weapon stands upright
    behind the body, held at the back hand (the front arm is busy); the front arm draws over the head."""
    h, w = master.shape[:2]
    names = [p[0] for p in PARTS]
    wi = names.index("weapon")
    head = lab == names.index("head")
    lab2 = lab.copy()
    lab2[head] = 99                                        # the head as its own part
    out = np.zeros_like(master)
    yy, xx = np.mgrid[0:h, 0:w]
    q = np.stack([xx.ravel(), yy.ravel()], 1).astype(float)

    def draw(sel, R, t):
        src = (q - t) @ R
        sx, sy = np.rint(src[:, 0]).astype(int), np.rint(src[:, 1]).astype(int)
        ok = (sx >= 0) & (sx < w) & (sy >= 0) & (sy < h)
        hit = np.zeros(len(q), bool)
        hit[ok] = np.isin(lab2[sy[ok], sx[ok]], sel)
        oy, ox = q[hit, 1].astype(int), q[hit, 0].astype(int)
        out[oy, ox] = master[sy[hit], sx[hit]]

    def rot(deg, about, move=np.zeros(2)):
        r = math.radians(deg)
        R = np.array([[math.cos(r), -math.sin(r)], [math.sin(r), math.cos(r)]])
        return R, about + move - R @ about

    # the weapon: upright (-85 deg) behind the body, its grip at the back hand
    d0 = J0["wtip"] - J0["ha_f"]
    a0 = math.degrees(math.atan2(d0[1], d0[0]))
    Rw, tw = rot(-85.0 - a0, J0["ha_f"], J1["ha_b"] - J0["ha_f"] + np.array([1.0, 0.0]))
    draw([wi], Rw, tw)
    for nm in ("thigh_b", "shin_b", "foot_b", "upper_b", "fore_b", "hand_b", "body", "waist",
               "head", "thigh_f", "shin_f", "foot_f", "upper_f", "fore_f", "hand_f"):
        pi = names.index(nm)
        a, b = PARTS[pi][1], PARTS[pi][2]
        R, t = xform(J0[a], J0[b], J1[a], J1[b])
        draw([pi], R, t)
    Rb, tb = xform(J0["hip"], J0["shm"], J1["hip"], J1["shm"])
    Rh, th = rot(tilt, neck)                               # the head turns about the neck, then rides the body
    draw([99], Rb @ Rh, Rb @ th + tb)
    out = fill_seams(out, master[..., 3] > 0)
    # the gesturing arm(s), drawn clean in the character's colours (the AI drawings paint the arms over the chest,
    # so there is no clean arm to cut out and move)
    if arms:
        sleeve, skin, ink = arm_colours(master, lab, J0, head_c)
        if np.linalg.norm(J1["ha_b"] - J0["ha_b"]) > 1.5:
            out = draw_arm_px(out, J1["sh_b"], J1["el_b"], J1["ha_b"], sleeve, skin, ink)
        out = draw_arm_px(out, J1["sh_f"], J1["el_f"], J1["ha_f"], sleeve, skin, ink)
    import cv2
    solid = (out[..., 3] >= 128).astype(np.uint8)
    n, cc, st, _ = cv2.connectedComponentsWithStats(solid, connectivity=8)
    if n > 2:
        main_c = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        for c in range(1, n):
            if c != main_c and st[c, cv2.CC_STAT_AREA] < 12 * ZF * ZF:
                out[cc == c] = 0
    shadow = (master[..., 3] > 0) & (master[..., 3] < 128)
    out[shadow & (out[..., 3] == 0)] = master[shadow & (out[..., 3] == 0)]
    return out


def main():
    if len(sys.argv) > 2 and sys.argv[2] == "gestures":
        key = sys.argv[1]
        sheet = np.array(Image.open(os.path.join(RES, "enemy_pic", key + ".png")).convert("RGBA"))
        fr = gesture_frames(key, sheet[0:FH, 0:FW].copy())
        S = 4
        img = Image.new("RGBA", (FW * S * 7, FH * S * 2), (60, 90, 60, 255))
        for q, f in enumerate(fr):
            img.alpha_composite(Image.fromarray(f).resize((FW * S, FH * S), Image.NEAREST),
                                ((q % 7) * FW * S, (q // 7) * FH * S))
        img.save(os.path.join(FIXD, key + "_gestures.png"))
        print("ok", len(fr))
        return
    key = sys.argv[1]
    kinds = sys.argv[2:] or ["walk8", "run"]
    sheet = np.array(Image.open(os.path.join(RES, "enemy_pic", key + ".png")).convert("RGBA"))
    master = sheet[0:FH, 0:FW].copy()
    ids = [n for n, (k, i) in enumerate(s2.FRAMES) if k in kinds]
    fr, lab = rig_frames(key, master, ids)
    S = 4
    rows = [[n for n in ids if s2.FRAMES[n][0] == k] for k in kinds]
    img = Image.new("RGBA", (FW * S * 9, FH * S * (len(rows) + 1)), (60, 90, 60, 255))
    pal = np.random.default_rng(3).integers(60, 255, (len(PARTS), 3))
    lv = np.zeros((FH, FW, 4), np.uint8)
    lv[lab >= 0, :3] = pal[lab[lab >= 0]]
    lv[lab >= 0, 3] = 255
    img.alpha_composite(Image.fromarray(master).resize((FW * S, FH * S), Image.NEAREST), (0, 0))
    img.alpha_composite(Image.fromarray(lv).resize((FW * S, FH * S), Image.NEAREST), (FW * S, 0))
    for r, row in enumerate(rows):
        for q, n in enumerate(row[:9]):
            img.alpha_composite(Image.fromarray(fr[n]).resize((FW * S, FH * S), Image.NEAREST),
                                (q * FW * S, (r + 1) * FH * S))
    img.save(os.path.join(FIXD, key + "_rig.png"))
    gif = [Image.alpha_composite(Image.new("RGBA", (FW * S, FH * S), (60, 90, 60, 255)),
                                 Image.fromarray(fr[n]).resize((FW * S, FH * S), Image.NEAREST)).convert("P")
           for n in rows[0]]
    gif[0].save(os.path.join(FIXD, key + "_rig.gif"), save_all=True, append_images=gif[1:], duration=120, loop=0)
    print("ok", len(fr))


if __name__ == "__main__":
    main()
