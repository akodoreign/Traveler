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

# parts, back to front: (name, bone from, bone to); "body" is hip -> shoulder midpoint, the head rides on it
PARTS = [("thigh_b", "hip", "kn_b"), ("shin_b", "kn_b", "ft_b"),
         ("upper_b", "sh_b", "el_b"), ("fore_b", "el_b", "ha_b"),
         ("body", "hip", "shm"),
         ("waist", "hip", "hipd"),                  # (user: "create a upperleg/waist sprite") moves with the hip
         ("thigh_f", "hip", "kn_f"), ("shin_f", "kn_f", "ft_f"),
         ("upper_f", "sh_f", "el_f"), ("fore_f", "el_f", "ha_f"),
         ("weapon", "ha_f", "wtip")]


_CAST = {}


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
    if kind in s2.V4_KINDS:
        P = s2.pose_v4(T, kind, i)
    else:
        P = s2.pose(kind, i, s2.STYLE.get(T["weapon"], "thrust"), spear=T["weapon"] in ("yari", "naginata"))
    P = s2.mark_upright(T, P, kind)
    P = s2.stature(T, s2.build_pose(T, P))
    if P.get("_upright"):
        P = s2.upright(P)
    P = s2.rig_arms(T, s2.rig_legs(T, P))
    J = {k: np.array(v, float) for k, v in P.items()
         if isinstance(v, tuple) and len(v) == 2 and k in ("sh_b", "el_b", "ha_b", "sh_f", "el_f", "ha_f", "hip",
                                                            "kn_b", "ft_b", "kn_f", "ft_f")}
    J["shm"] = (J["sh_b"] + J["sh_f"]) / 2.0
    J["hipd"] = J["hip"] + np.array([0.0, 4.0])            # the waist bone: a short stub straight down
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
ARM_ROT = 0.6              # arms swing at 60% of the rig (full swing tore the sleeves)


def weapon_reach(master, J):
    """The weapon's real length on the master: the farthest solid pixel along the hand->tip direction, near the line."""
    ys, xs = np.nonzero(master[..., 3] >= 128)
    px = np.stack([xs, ys], 1).astype(float)
    a, b = J["ha_f"], J["wtip"]
    u = (b - a) / max(1e-6, np.linalg.norm(b - a))
    along = (px - a) @ u
    perp = np.abs((px - a) @ np.array([-u[1], u[0]]))
    on = (perp <= 1.6) & (along > 0)
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
            if c == keep or st[c, cv2.CC_STAT_AREA] > 8:
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
    closed = cv2.morphologyEx(a, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)).astype(bool)
    holes = closed & ~a.astype(bool)
    for y, x in zip(*np.nonzero(holes)):
        nb = out[max(0, y - 1):y + 2, max(0, x - 1):x + 2].reshape(-1, 4)
        nb = nb[nb[:, 3] > 0]
        if len(nb):
            out[y, x] = nb[len(nb) // 2]
    return out


def labels(master, J):
    """Each master pixel -> the nearest part (weapon only along its line, beyond the hand)."""
    J = weapon_reach(master, J)
    ys, xs = np.nonzero(master[..., 3] > 0)
    px = np.stack([xs, ys], 1).astype(float)
    d = np.stack([seg_dist(px, J[a], J[b]) for _n, a, b in PARTS], 1)
    wi = [p[0] for p in PARTS].index("weapon")
    d[:, wi] = np.where(d[:, wi] <= 1.6, d[:, wi] - 3.0, 99.0)   # the weapon wins its own thin line
    # the head (well above the shoulders) is body, whatever the arms say; so is the torso core - in side view the
    # back arm lies over the torso, and only what sticks out of the body may swing (Rensei's chest tore off with it)
    bi = [p[0] for p in PARTS].index("body")
    head = ys < J["shm"][1] - 1
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
    lab[ys, xs] = best
    return smooth_labels(lab)


def xform(a0, b0, a1, b1):
    """Rigid 2D transform taking segment a0->b0 to a1->b1 (rotation about a, then translation)."""
    t0 = math.atan2(*(b0 - a0)[::-1])
    t1 = math.atan2(*(b1 - a1)[::-1])
    r = t1 - t0
    c, s = math.cos(r), math.sin(r)
    R = np.array([[c, -s], [s, c]])
    return R, a1 - R @ a0


def rig_frame(master, lab, J0, J1):
    h, w = master.shape[:2]
    out = np.zeros_like(master)
    yy, xx = np.mgrid[0:h, 0:w]
    q = np.stack([xx.ravel(), yy.ravel()], 1).astype(float)
    for pi, (name, a, b) in enumerate(PARTS):
        if name == "waist":                                # follows the hip, never turns
            R, t = np.eye(2), J1["hip"] - J0["hip"]
        elif name == "weapon":                             # moves with the hand, a damped share of the rig's turn
            d0, d1 = J0[b] - J0[a], J1[b] - J1[a]
            r = (math.atan2(d1[1], d1[0]) - math.atan2(d0[1], d0[0]) + math.pi) % (2 * math.pi) - math.pi
            r *= WEAPON_ROT
            c_, s_ = math.cos(r), math.sin(r)
            R = np.array([[c_, -s_], [s_, c_]])
            t = J1[a] - R @ J0[a]
        else:
            R, t = xform(J0[a], J0[b], J1[a], J1[b])
            if name in ("upper_b", "fore_b", "upper_f", "fore_f"):    # arms: a damped share of the swing
                ang = math.atan2(R[1, 0], R[0, 0]) * ARM_ROT
                c_, s_ = math.cos(ang), math.sin(ang)
                R = np.array([[c_, -s_], [s_, c_]])
                t = J1[a] - R @ J0[a]
        src = (q - t) @ R                                  # inverse: R^T (q - t)
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
            if c != main_c and st[c, cv2.CC_STAT_AREA] < 12:
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


def rig_frames(key, master, frame_ids):
    T = traveler(key)
    if T is None:
        return {}, None
    k0, i0 = s2.FRAMES[0]
    rig0 = np.asarray(s2.frame(T, k0, i0))
    rbox = bbox(rig0[..., 3] >= 128)
    mbox = bbox(master[..., 3] >= 128)
    J0 = to_master_space(joints(T, k0, i0), rbox, mbox)
    lab = labels(master, J0)                               # (also measures the weapon: J0["wtip"])
    reach = np.linalg.norm(J0["wtip"] - J0["ha_f"])
    out = {}
    for n in frame_ids:
        kind, i = s2.FRAMES[n]
        J = joints(T, kind, i)
        if J is None:
            continue
        J = to_master_space(J, rbox, mbox)
        u = J["wtip"] - J["ha_f"]
        J["wtip"] = J["ha_f"] + u / max(1e-6, np.linalg.norm(u)) * reach
        out[n] = rig_frame(master, lab, J0, J)
    return out, lab


# ---- Conversation gestures (user 2026-11-15: "now we can add animations to even conversations. like when hiruma
# says 'who did my lord marry' the pixel art can do a face palm as well") - one extra sheet row, side view.
GESTURES = [("facepalm", 4), ("shrug", 3), ("crossarms", 2), ("scratch", 3), ("point", 2)]   # 14 frames = 1 row
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
    return J, tilt


def gesture_frames(key, master):
    """The 14 gesture frames (row order of GESTURES) for a sheet's side master, or None (no rig / no master)."""
    T = traveler(key)
    if T is None or master is None:
        return None
    k0, i0 = s2.FRAMES[0]
    rig0 = np.asarray(s2.frame(T, k0, i0))
    rbox, mbox = bbox(rig0[..., 3] >= 128), bbox(master[..., 3] >= 128)
    if not rbox or not mbox:
        return None
    J0 = to_master_space(joints(T, k0, i0), rbox, mbox)
    lab = labels(master, J0)
    names = [p[0] for p in PARTS]
    hy, hx = np.nonzero((lab == names.index("body")) & (np.arange(master.shape[0])[:, None] < J0["shm"][1] - 1))
    head_c = np.array([hx.mean(), hy.mean()]) if len(hx) else J0["shm"] + np.array([0.0, -8.0])
    neck = J0["shm"] + np.array([0.0, -1.0])
    out = []
    for name, n in GESTURES:
        for k in range(n):
            J, tilt = gesture_joints(J0, head_c, name, k, n)
            out.append(gesture_frame(master, lab, J0, J, tilt, neck, head_c))
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


def gesture_frames_hd(key, master, z=2):
    """The gesture row for the HD (z x) sheet: the rig body at 1x, upscaled (nearest), then the gesturing arms drawn
    at the z-times grid (finer outline and hands)."""
    T = traveler(key)
    if T is None or master is None:
        return None
    k0, i0 = s2.FRAMES[0]
    rig0 = np.asarray(s2.frame(T, k0, i0))
    rbox, mbox = bbox(rig0[..., 3] >= 128), bbox(master[..., 3] >= 128)
    if not rbox or not mbox:
        return None
    J0 = to_master_space(joints(T, k0, i0), rbox, mbox)
    lab = labels(master, J0)
    names = [p[0] for p in PARTS]
    hy, hx = np.nonzero((lab == names.index("body")) & (np.arange(master.shape[0])[:, None] < J0["shm"][1] - 1))
    head_c = np.array([hx.mean(), hy.mean()]) if len(hx) else J0["shm"] + np.array([0.0, -8.0])
    neck = J0["shm"] + np.array([0.0, -1.0])
    sleeve, skin, ink = arm_colours(master, lab, J0, head_c)
    out = []
    for name, n in GESTURES:
        for k in range(n):
            J, tilt = gesture_joints(J0, head_c, name, k, n)
            f1 = gesture_frame(master, lab, J0, J, tilt, neck, head_c, arms=False)
            fz = np.repeat(np.repeat(f1, z, 0), z, 1)
            c = (z - 1) / 2.0                              # pixel centres on the finer grid
            if np.linalg.norm(J["ha_b"] - J0["ha_b"]) > 1.5:
                fz = draw_arm_px(fz, J["sh_b"] * z + c, J["el_b"] * z + c, J["ha_b"] * z + c, sleeve, skin, ink, z)
            fz = draw_arm_px(fz, J["sh_f"] * z + c, J["el_f"] * z + c, J["ha_f"] * z + c, sleeve, skin, ink, z)
            out.append(fz)
    return out


def gesture_frame(master, lab, J0, J1, tilt, neck, head_c, arms=True):
    """Like rig_frame, plus: the head (body pixels above the neck) tilts about the neck; the weapon stands upright
    behind the body, held at the back hand (the front arm is busy); the front arm draws over the head."""
    h, w = master.shape[:2]
    names = [p[0] for p in PARTS]
    bi, wi = names.index("body"), names.index("weapon")
    head = (lab == bi) & (np.arange(h)[:, None] < neck[1])
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
    for nm in ("thigh_b", "shin_b", "upper_b", "fore_b", "body", "waist", "thigh_f", "shin_f"):
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
            if c != main_c and st[c, cv2.CC_STAT_AREA] < 12:
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
