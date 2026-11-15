"""Direct pixel corrections for an animation sheet (user 2026-11-15: "make corrections to the pixel art sheets directly
... enhance 1 then match features image 1 and 2, then 1 and 3 etc"; chosen: palette lock, size / position match,
cleanup + consistent outline, enhance the reference frame; the head transplant only for stationary NPCs).

Per facing (side / front / back) one reference frame (stand frame 0, stand_f, stand_b):
  1. enhance the reference: hard alpha, specks removed, a one-pixel outline in the sheet's own darkest ink;
  2. palette lock: every frame's colours snap to the palette of the enhanced reference frames (no shade shimmer);
  3. size / position: upright frames (stand, walk, run, talk, nod - not attacks, casts, falls, sitting) are scaled to the
     reference's body height and set on its foot line and centre, so the figure doesn't pop or float;
  4. cleanup: hard alpha, specks gone, the same outline.
Writes previews only, unless --install: _art/preview/fixsheet/<sheet>_compare.png (before over after) and
<sheet>_walk.gif. python -E tools/fix_sheet.py trav_natsuko [--install]"""
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "_tools", "rpgcobo-tool", "project", "resource")
OUT = os.path.join(HERE, "..", "_art", "preview", "fixsheet")
UPRIGHT = {"stand", "walk", "run", "talk", "nod", "stand_f", "walk_f", "stand_b", "walk_b", "talk_f", "nod_f",
           "nod_b"}


def facing(aid):
    return "front" if aid.endswith("_f") else "back" if aid.endswith("_b") else "side"


def clean(fr, ink, min_px=6):
    """Solid pixels made fully solid, specks under min_px gone, a one-pixel outline (ink) on the edge of the BODY only
    (thin parts - a spear shaft, a tassel - keep their colour; they are all edge). Faint pixels (the ground shadow)
    are left as they are."""
    a = fr[..., 3] >= 128
    n, lab, st, _ = cv2.connectedComponentsWithStats(a.astype(np.uint8), connectivity=8)
    keep = np.zeros_like(a)
    for k in range(1, n):
        if st[k, cv2.CC_STAT_AREA] >= min_px:
            keep |= lab == k
    out = fr.copy()
    faint = (fr[..., 3] > 0) & (fr[..., 3] < 128)
    out[..., 3] = np.where(keep, 255, np.where(faint, fr[..., 3], 0))
    gone = ~keep & ~faint
    out[gone, :3] = 0
    k3 = np.ones((3, 3), np.uint8)
    body = cv2.dilate(cv2.erode(keep.astype(np.uint8), k3, iterations=2), k3, iterations=3).astype(bool)
    edge = keep & ~cv2.erode(keep.astype(np.uint8), k3).astype(bool) & body
    lum = out[..., :3].astype(int).sum(-1)
    dark = lum <= int(np.sum(ink[:3])) + 60                                 # already ink-dark: leave it
    out[edge & ~dark, :3] = ink[:3]
    return out


# Hand pixel patches on a facing's master frame (every derived frame inherits them): {key: {facing: [(x, y, rgb)]}}
_EYE, _HI = (40, 26, 24), (222, 214, 204)
PATCH = {
    # (offered 11-15: grey "goggles" where the front-view eyes should be) dark irises with a highlight
    "trav_natsuko": {"front": [(38, 28, _HI), (39, 28, _EYE), (38, 29, _EYE), (39, 29, _EYE),
                               (42, 28, _HI), (43, 28, _EYE), (42, 29, _EYE), (43, 29, _EYE)],
                     # (user 2026-11-15, red circle on the rig preview) generator specks through the sash: majority
                     # colour inside the waist box (x0, y0, x1, y1)
                     "side": [("smooth", 32, 41, 50, 52)]},
}
def smooth_box(fr, x0, y0, x1, y1, passes=2):
    """Majority colour inside a box (solid pixels only, ink outline kept): specks go, shapes of 3+ px stay."""
    out = fr.copy()
    for _ in range(passes):
        src = out.copy()
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if src[y, x, 3] < 128 or src[y, x, :3].sum() == 0:
                    continue
                nb = src[y - 1:y + 2, x - 1:x + 2].reshape(-1, 4)
                nb = nb[(nb[:, 3] >= 128) & (nb[:, :3].sum(1) > 0)]
                if len(nb) < 5:
                    continue
                # a speck: much brighter than its neighbourhood (pairs of specks too) -> a typical neighbour colour
                nl = nb[:, :3].astype(int).sum(1)
                me = int(src[y, x, :3].astype(int).sum())
                med = int(np.median(nl))
                if me > med + 150:
                    dark = nb[nl <= med + 40]
                    if len(dark):
                        out[y, x, :3] = dark[np.argmin(np.abs(dark[:, :3].astype(int).sum(1) - med))][:3]
    return out


GLARE = {"trav_natsuko"}       # sheets whose dark armour carries white glare patches (user 2026-11-15 marks)


def denoise(fr, ink, glare=False):
    """(user 2026-11-15, marked shots) generator noise inside the figure, after the palette lock:
    - a lone pixel whose colour appears nowhere else in its 3x3 takes the colour most of its neighbours share;
    - a small bright smear (<= 14 px) inside dark armour, not touching the edge (a spear tip) and not inside skin
      (the eyes), takes the armour colour around it;
    - a one-pixel spur of outline ink (one solid neighbour) is trimmed."""
    out = fr.copy()
    h, w = fr.shape[:2]
    solid = out[..., 3] == 255
    rgb = out[..., :3].astype(np.int32)
    key = (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if not solid[y, x]:
                continue
            nb = [(key[y + dy, x + dx], (y + dy, x + dx)) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                  if (dy or dx) and solid[y + dy, x + dx]]
            if len(nb) < 6 or any(k == key[y, x] for k, _ in nb):
                continue
            vals = [k for k, _ in nb]
            best = max(set(vals), key=vals.count)
            me = int(rgb[y, x].sum())
            bl = ((best >> 16) & 255) + ((best >> 8) & 255) + (best & 255)
            if vals.count(best) >= 4 and me >= bl - 150:          # a dark dot on lighter ground is an eye: keep
                out[y, x, :3] = [(best >> 16) & 255, (best >> 8) & 255, best & 255]
    lum = out[..., :3].astype(int).sum(-1)
    sat = out[..., :3].astype(int).max(-1) - out[..., :3].astype(int).min(-1)
    is_ink = np.all(out[..., :3] == np.array(ink[:3], np.uint8), -1)
    # (only grey-white noise: a lit face, an eye, a glowing orb are coloured or framed by outline ink - keep those)
    bright = solid & (lum > 560) & (sat < 40)
    if glare:                                   # (opt-in per sheet: dark-armour figures; orbs / beards elsewhere)
        bright = solid & (lum > 540) & (sat < 60)
        # a glare spot plus the light grey halo it sits in (judged as one patch, so the halo isn't the ground)
        light = solid & (lum > 300) & (sat < 60)
        ln, llab = cv2.connectedComponents(light.astype(np.uint8), connectivity=8)
        seeds = np.unique(llab[bright])
        bright = np.isin(llab, seeds[seeds > 0])
    n, lab, st, _ = cv2.connectedComponentsWithStats(bright.astype(np.uint8), connectivity=8)
    edge_near = cv2.dilate((~solid).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    # the torso: the biggest blob left after erosion (a staff is thin, so its orb drops off and is never "noise")
    er = cv2.erode(solid.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=2)
    bn, blab, bst, _ = cv2.connectedComponentsWithStats(er, connectivity=4)
    torso = np.zeros_like(solid)
    if bn > 1:
        torso = cv2.dilate((blab == 1 + bst[1:, cv2.CC_STAT_AREA].argmax()).astype(np.uint8), np.ones((3, 3), np.uint8),
                           iterations=3).astype(bool)
    for k in range(1, n):
        area = st[k, cv2.CC_STAT_AREA]
        m = lab == k
        if area >= 4 and cv2.connectedComponents(m.astype(np.uint8), connectivity=4)[0] - 1 >= 3:
            continue                     # (side_gesshin's white X mon) a drawn pattern, diagonal strokes: not a smear
        if glare and area <= 60 and not (m & ~torso).any():
            # (user 2026-11-15, Natsuko marks 2) a white / blue-grey glare patch inside dark armour, even at the
            # outline (a collar plate, a foot): each pixel takes the colour of the nearest armour pixel around it
            ring = cv2.dilate(m.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & ~m & solid
            body0 = ring & ~is_ink
            body = body0 & (sat < 60)                                      # the grey armour, not the neck skin
            if body.sum() >= 6 and body.sum() >= 0.5 * body0.sum() and lum[body].mean() <= 330 \
                    and sat[body].mean() <= 45:
                _d, lb = cv2.distanceTransformWithLabels((~body).astype(np.uint8), cv2.DIST_L2, 3,
                                                         labelType=cv2.DIST_LABEL_PIXEL)
                ys, xs = np.nonzero(body)
                src = np.zeros((lb.max() + 1, 3), np.uint8)
                src[lb[ys, xs]] = out[ys, xs, :3]
                out[m, :3] = src[lb[m]]
            continue
        if area > 14:
            continue
        if (m & ~torso).any():
            continue                                                       # off the body: an orb, a blade
        if (m & edge_near).any():
            continue                                                       # touches the outside: a tip, a rim light
        ring = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~m & solid
        if not ring.any() or lum[ring].mean() > 300:
            continue                                                       # skin or light cloth around it: keep
        if sat[ring].mean() > 45 or (is_ink[ring] | (lum[ring] < 150)).mean() > 0.4:
            continue                                                       # skin / hair, or an outlined detail
        rr = out[ring][:, :3].astype(np.int32)
        rk = (rr[:, 0] << 16) | (rr[:, 1] << 8) | rr[:, 2]
        best = np.bincount(np.unique(rk, return_inverse=True)[1]).argmax()
        out[m, :3] = rr[np.unique(rk, return_inverse=True)[1] == best][0]
    solid = out[..., 3] == 255
    inkm = np.all(out[..., :3] == np.array(ink[:3], np.uint8), -1) & solid
    n4 = (np.roll(solid, 1, 0).astype(int) + np.roll(solid, -1, 0) + np.roll(solid, 1, 1) + np.roll(solid, -1, 1))
    spur = inkm & (n4 <= 1)
    out[spur, 3] = 0
    out[spur, :3] = 0
    return out


def palette_of(frames, n=40):
    px = np.concatenate([f[f[..., 3] > 0][:, :3] for f in frames]).astype(np.float32)
    k = min(n, len(np.unique(px.astype(np.uint8), axis=0)))
    _c, _l, centers = cv2.kmeans(px, k, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5), 3,
                                 cv2.KMEANS_PP_CENTERS)
    return centers.astype(np.float32)


def lock(fr, pal, far=48.0):
    """Snap to the reference palette - but a colour with no close match (a lit face where the references are in
    shade) keeps its own: forcing it went to the nearest dark (hair brown on faces)."""
    out = fr.copy()
    m = out[..., 3] > 0
    px = out[m][:, :3].astype(np.float32)
    d = ((px[:, None, :] - pal[None, :, :]) ** 2).sum(-1)
    best = d.argmin(1)
    near = d[np.arange(len(best)), best] <= far * far
    snapped = px.copy()
    snapped[near] = pal[best[near]]
    out[m, :3] = snapped.round().astype(np.uint8)
    return out


def bbox(fr):
    """The BODY's box: solid pixels opened by 2 (a spear or a tassel is thin and drops out), so a raised weapon
    doesn't make a frame look tall."""
    solid = (fr[..., 3] >= 128).astype(np.uint8)
    k3 = np.ones((3, 3), np.uint8)
    body = cv2.dilate(cv2.erode(solid, k3, iterations=2), k3, iterations=2)
    ys, xs = np.nonzero(body if body.any() else solid)
    return (xs.min(), ys.min(), xs.max(), ys.max()) if len(xs) else None


def full_box(fr):
    ys, xs = np.nonzero(fr[..., 3] > 0)
    return (xs.min(), ys.min(), xs.max(), ys.max()) if len(xs) else None


def fit(fr, ref_box):
    """Scale to the reference's body height (nearest neighbour: pixel art), feet on its foot line, centred on it."""
    b = bbox(fr)
    if not b or not ref_box:
        return fr
    h, rh = b[3] - b[1] + 1, ref_box[3] - ref_box[1] + 1
    s = rh / float(h)
    if abs(s - 1) < 0.04 or abs(s - 1) > 0.25:                           # (tiny: leave; huge: a crouch, not drift)
        s = 1.0
    fb_ = full_box(fr)                                                      # move the whole drawing (weapon too)
    crop = fr[fb_[1]:fb_[3] + 1, fb_[0]:fb_[2] + 1]
    if s != 1.0:
        crop = cv2.resize(crop, (max(1, int(round(crop.shape[1] * s))), max(1, int(round(crop.shape[0] * s)))),
                          interpolation=cv2.INTER_NEAREST)
    # where the body's feet and centre land after scaling, inside the crop
    bx_c = ((b[0] + b[2]) / 2.0 - fb_[0]) * s
    by_f = (b[3] + 1 - fb_[1]) * s
    out = np.zeros_like(fr)
    ch, cw = crop.shape[:2]
    cx = (ref_box[0] + ref_box[2]) / 2.0
    x0, y0 = int(round(cx - bx_c)), int(round(ref_box[3] + 1 - by_f))
    sx0, sy0 = max(0, -x0), max(0, -y0)                                     # clip to the frame
    dx0, dy0 = max(0, x0), max(0, y0)
    w_ = min(cw - sx0, fr.shape[1] - dx0)
    h_ = min(ch - sy0, fr.shape[0] - dy0)
    if w_ > 0 and h_ > 0:
        out[dy0:dy0 + h_, dx0:dx0 + w_] = crop[sy0:sy0 + h_, sx0:sx0 + w_]
    return out


STILL = {"stand", "talk", "nod", "stand_f", "talk_f", "nod_f", "stand_b", "talk_b", "nod_b"}
HEAD = 0.33                                          # the chibi head: the top third of the body box (0.42 took
#                                                      the shoulders and a chest crest with it)


def _head_span(fr, box):
    solid = (fr[..., 3] >= 128).astype(np.uint8)
    k3 = np.ones((3, 3), np.uint8)
    body = cv2.dilate(cv2.erode(solid, k3, iterations=2), k3, iterations=2).astype(bool)
    hh = max(4, int(round((box[3] - box[1] + 1) * HEAD)))
    band = body[box[1]:box[1] + hh]
    xs = np.nonzero(band.any(0))[0]
    return hh, (xs.min(), xs.max()) if len(xs) else (box[0], box[2])


def head_transplant(fr, ref):
    """(user 2026-11-15, option 2 "good for stationary NPCs") the enhanced reference's head pasted onto a standing /
    talking / nodding frame: same face every frame, set on this frame's own head position (a nod keeps its dip)."""
    rb, fb = bbox(ref), bbox(fr)
    if not rb or not fb:
        return fr
    hh, (rx0, rx1) = _head_span(ref, rb)
    _hh, (fx0, fx1) = _head_span(fr, fb)
    dx = int(round((fx0 + fx1) / 2.0 - (rx0 + rx1) / 2.0))
    dy = fb[1] - rb[1]
    out = fr.copy()
    h, w = fr.shape[:2]
    y0, y1 = max(0, rb[1] - 3), rb[1] + hh                                  # (-3: hair tufts above the body box)
    x0, x1 = max(0, rx0 - 2), min(w, rx1 + 3)
    # clear this frame's own head, then lay the reference head in
    cy0, cy1 = max(0, y0 + dy), min(h, y1 + dy)
    cx0, cx1 = max(0, x0 + dx), min(w, x1 + dx)
    # only the head MASS (the opened body: a spear shaft or staff through the band is thin, so it stays)
    k3 = np.ones((3, 3), np.uint8)
    solid = (fr[..., 3] >= 128).astype(np.uint8)
    mass = cv2.dilate(cv2.erode(solid, k3, iterations=2), k3, iterations=3).astype(bool)
    box = np.zeros_like(mass)
    box[cy0:cy1, cx0:cx1] = True
    out[mass & box] = 0
    for y in range(y0, y1):
        ty = y + dy
        if not 0 <= ty < h:
            continue
        for x in range(x0, x1):
            tx = x + dx
            if 0 <= tx < w and ref[y, x, 3] > 0:
                out[ty, tx] = ref[y, x]
    # the band just below the head keeps this frame's pixels; anything the clear cut off in the band edges that the
    # reference has no pixel for stays empty (the reference head is the complete head)
    return out


MOVE = {"walk", "run", "walk_f", "run_f", "walk_b", "run_b"}   # (user 2026-11-15 video: the side walk / run were
CUT = 0.56                                           # sword-lunges and staff swings, a new pose every frame)


def move_from_ref(ref, aid, k, n, cut=0.6):
    """(user 2026-11-15: "its the multiple different outfits that all animate together (even though they are same
    color)") a walk / run frame drawn from the stand frame ONLY - the AI walk frames each wore a differently cut
    outfit. Side view: the lower body scissors open from the hips (left half back, right half forward, more at the
    feet), the body dips 1 px at the widest stride. Front / back: the feet lift 1 px in turn, the body bobs."""
    rb = bbox(ref)
    if not rb:
        return ref.copy()
    h, w = ref.shape[:2]
    H = rb[3] - rb[1] + 1
    hip = rb[1] + int(round(H * cut))
    feet = rb[3]
    run = aid.startswith("run")
    out = np.zeros_like(ref)
    ph = 2 * np.pi * k / max(1, n)
    if facing(aid) == "side":
        amp = 3 if run else 2
        # (user 2026-11-15: "the left leg always stays back") signed stride: the legs swap on every step, so the
        # back leg comes through to the front - open one way, closed, open the other way, closed
        s = np.sin(ph)
        a = s * amp
        dip = 1 if abs(a) >= amp * 0.7 else 0
        solid = ref[..., 3] > 0
        xs = np.nonzero(solid[hip:feet + 1].any(0))[0]
        cx = (xs.min() + xs.max()) / 2.0 if len(xs) else w / 2.0
        for y in range(h):
            row = ref[y]
            ty = y + dip if y < hip else y                 # the body dips onto the legs; the feet stay planted
            if not 0 <= ty < h:
                continue
            if y < hip:
                m = row[:, 3] > 0
                out[ty][m] = row[m]
                continue
            t = (y - hip) / float(max(1, feet - hip))
            off = int(round(a * t))
            xs_ = np.nonzero(row[:, 3] > 0)[0]
            near_first = sorted(xs_, key=lambda x: (x < cx) == (s >= 0))   # the leg swinging forward is drawn on top
            for x in near_first:
                tx = x - off if x < cx else x + off
                if 0 <= tx < w and out[y, tx, 3] == 0:
                    out[y, tx] = row[x]
        if dip:                                             # close the 1-px seam the dip opens at the hip
            seam = out[hip]
            m = (seam[:, 3] == 0) & (ref[hip - 1, :, 3] > 0)
            out[hip][m] = ref[hip - 1][m]
    else:
        lift = 2 if run else 1
        quarter = int(4 * k / max(1, n)) % 4               # 0: left up, 1: down, 2: right up, 3: down
        bob = 1 if quarter in (1, 3) else 0
        foot0 = feet - max(3, int(round(H * 0.14)))
        xs = np.nonzero((ref[foot0:feet + 1, :, 3] > 0).any(0))[0]
        cx = (xs.min() + xs.max()) / 2.0 if len(xs) else w / 2.0
        for y in range(h):
            for x in np.nonzero(ref[y, :, 3] > 0)[0]:
                ty = y
                if y < foot0:
                    ty = y + bob
                elif (quarter == 0 and x < cx) or (quarter == 2 and x >= cx):
                    ty = y - lift
                if 0 <= ty < h and (out[ty, x, 3] == 0 or y < foot0):
                    out[ty, x] = ref[y, x]
    return out


FLOW_Z, FLOW_SIGMA, FLOW_MAX, FLOW_IOU = 4, 9.0, 6.0, 0.72
FLOW_IDS = {"walk", "run", "walk_f", "run_f", "walk_b", "run_b", "talk", "talk_f", "talk_b"}


def flow_from_ref(master, fr):
    """(user 2026-11-15: "can you get more of the animation back") the MOTION of an AI frame, the PIXELS of the
    master: dense optical flow from the (cleaned, fitted) AI frame back to the master, smoothed (so a spear moves as
    one piece) and capped, then the master is remapped along it (nearest: pixel art). Returns (frame, score); score is
    the outline match (IoU) between the warped master and the AI frame - a drifted pose (a sword lunge in a walk)
    scores low and the caller falls back to the procedural motion."""
    h, w = master.shape[:2]

    def gray(f):
        g = (f[..., :3].astype(np.float32).mean(-1) * (f[..., 3] > 0)).astype(np.uint8)
        return cv2.resize(g, (w * FLOW_Z, h * FLOW_Z), interpolation=cv2.INTER_NEAREST)
    dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    fl = dis.calc(gray(fr), gray(master), None)
    fl = cv2.GaussianBlur(fl, (0, 0), FLOW_SIGMA)
    fl = cv2.resize(fl, (w, h), interpolation=cv2.INTER_AREA) / FLOW_Z
    mag = np.sqrt((fl ** 2).sum(-1, keepdims=True))
    fl = fl * np.minimum(1.0, FLOW_MAX / np.maximum(mag, 1e-6))
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    out = cv2.remap(master, xx + fl[..., 0], yy + fl[..., 1], interpolation=cv2.INTER_NEAREST,
                    borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    a, b = out[..., 3] >= 128, fr[..., 3] >= 128
    iou = (a & b).sum() / float(max(1, (a | b).sum()))
    return out, iou


def animate_move(ref, aid, k, n, cut=0.6):
    """(user 2026-11-15: "can you get more of the animation back using your current technique?") walk / run from the
    stand frame alone (one outfit), with more life than move_from_ref:
    side  - a signed scissor stride (3 px walking, 4 running) whose legs swap each step; the upper body leans into
            the move (1 / 2 px at the head, sheared from the hips); the body dips at the wide stride (1 / 2 px);
            the trailing foot lifts 1 px at toe-off
    front / back - the feet lift in turn (1 / 2 px), the body dips while both feet are down and shifts 1 px over
            the planted foot (weight shift)."""
    rb = bbox(ref)
    if not rb:
        return ref.copy()
    h, w = ref.shape[:2]
    top, feet = rb[1], rb[3]
    H = feet - top + 1
    hip = top + int(round(H * cut))
    run = aid.startswith("run")
    out = np.zeros_like(ref)
    ph = 2 * np.pi * k / max(1, n)
    ys, xs = np.nonzero(ref[..., 3] > 0)
    lowx = xs[ys >= hip]
    cx = (lowx.min() + lowx.max()) / 2.0 if len(lowx) else w / 2.0

    def put(y, x, ty, tx, over):
        if 0 <= ty < h and 0 <= tx < w and (over or out[ty, tx, 3] == 0):
            out[ty, tx] = ref[y, x]

    if facing(aid) == "side":
        amp, lean = (4, 2) if run else (3, 1)
        s = np.sin(ph)
        a = s * amp
        wide = abs(s) > 0.7
        dip = (2 if run else 1) if wide else 0
        back_left = s >= 0                                 # which half trails this step
        order = np.argsort(ys, kind="stable")
        for y, x in zip(ys[order], xs[order]):             # legs first (only into empty pixels) ...
            if y < hip:
                continue
            t = (y - hip) / float(max(1, feet - hip))
            off = int(round(a * t))
            left = x < cx
            tx = x - off if left else x + off
            ty = y - 1 if (wide and y >= feet - 1 and left == back_left) else y
            put(y, x, ty, tx, False)
        for y, x in zip(ys, xs):                           # ... then the leaning, dipping upper body over them
            if y >= hip:
                continue
            sh = int(round(lean * (hip - y) / float(max(1, hip - top))))
            put(y, x, y + dip, x + sh, True)
        for d in range(dip):                               # close the seam the dip opens at the hip
            row = hip + d
            if row < h:
                m = (out[row, :, 3] == 0) & (ref[hip - 1, :, 3] > 0)
                out[row][m] = ref[hip - 1][m]
    else:
        lift = 2 if run else 1
        quarter = int(4 * k / max(1, n)) % 4               # 0: left foot up, 1: both down, 2: right up, 3: down
        bob = 1 if quarter in (1, 3) else 0
        sway = {0: 1, 2: -1}.get(quarter, 0)               # weight over the planted foot
        foot0 = feet - max(3, int(round(H * 0.14)))
        for y, x in zip(ys, xs):
            if y >= foot0:
                up = (quarter == 0 and x < cx) or (quarter == 2 and x >= cx)
                put(y, x, y - lift if up else y, x, False)
        for y, x in zip(ys, xs):
            if y < foot0:
                put(y, x, y + bob, x + sway, True)
        for d in range(bob):
            row = foot0 + d
            m = (out[row, :, 3] == 0) & (ref[foot0 - 1, :, 3] > 0)
            out[row][m] = np.roll(ref[foot0 - 1], sway, axis=0)[m]
    return out


def still_from_ref(ref, aid, k, n):
    """(user 2026-11-15: "look at how the shirts change to different types in all the npc animations") a standing /
    talking / nodding frame IS the stand frame - the outfit can't drift - with the head moved: a nod dips it 1-2 px
    through the middle of the animation, talking bobs it 1 px on alternate frames."""
    out = ref.copy()
    rb = bbox(ref)
    if not rb:
        return out
    hh = max(4, int(round((rb[3] - rb[1] + 1) * HEAD)))
    if aid.startswith("stand") or aid.startswith("talk"):
        # (user 2026-11-15: "get more of the animation back") breathing: the whole upper body settles 1 px on the
        # out-breath (the legs stay planted); talking adds a head bob on top
        if (k // 2) % 2:
            hip = rb[1] + int(round((rb[3] - rb[1] + 1) * 0.6))
            up = ref[:hip].copy()
            out[:hip] = 0                                  # the upper body comes down a row; the legs stay
            m = up[..., 3] > 0
            dst = out[1:hip + 1]
            dst[m] = up[m]
            ref = out.copy()
        if aid.startswith("stand"):
            return out
    if aid.startswith("nod"):
        dy = (0, 1, 2, 2, 1, 0)[min(5, int(6 * k / max(1, n)))]
    else:
        dy = k % 2
    if not dy:
        return out
    y0, y1 = max(0, rb[1] - 3), rb[1] + hh
    band = ref[y0:y1].copy()
    out[y0:y1 + dy] = np.where(ref[y0:y1 + dy, :, 3:4] > 0, out[y0:y1 + dy], 0)
    out[y0:y0 + dy] = 0                                    # the top rows the head leaves
    dst = out[y0 + dy:y1 + dy]
    m = band[..., 3] > 0
    dst[m] = band[m]
    return out


def body_transplant(fr, ref, cut=CUT, bob_max=2):
    """(user 2026-11-15, the walking video) the stand frame's whole upper body (head, arms, the weapon as it is held
    standing) on a walk / run frame, which keeps only its own legs: one character whose legs move, not a new drawing
    every frame. The waist line follows the walk frame's own height (the step bob), capped at bob_max px."""
    rb, fb = bbox(ref), bbox(fr)
    if not rb or not fb:
        return fr
    h, w = fr.shape[:2]
    k3 = np.ones((3, 3), np.uint8)
    rh, fh_ = rb[3] - rb[1] + 1, fb[3] - fb[1] + 1
    rcut = rb[1] + int(round(rh * cut))
    # where the waist sits in this frame, measured up from its feet; the bob is capped
    drop = int(np.clip((rh - fh_) * cut, -bob_max, bob_max))
    fcut = rb[3] - (rb[3] - rcut) + drop                   # feet are on the same line after fit()
    fcut = int(np.clip(fcut, 1, h - 2))
    # the legs: this frame below the waist, thin things (a blade, a staff end) dropped
    solid = (fr[..., 3] >= 128).astype(np.uint8)
    low = solid.copy()
    low[:fcut] = 0
    op = cv2.dilate(cv2.erode(low, k3, iterations=1), k3, iterations=1)
    n, lab, st, _ = cv2.connectedComponentsWithStats(op, connectivity=8)
    keep = np.zeros_like(low, bool)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] >= 12 and st[i, cv2.CC_STAT_TOP] + st[i, cv2.CC_STAT_HEIGHT] >= fb[3] - 2:
            keep |= lab == i                               # leg masses that reach the feet
    keep = cv2.dilate(keep.astype(np.uint8), k3, iterations=1).astype(bool) & (low > 0)
    keep |= (fr[..., 3] > 0) & (fr[..., 3] < 128)          # (the soft ground shadow stays)
    out = np.zeros_like(fr)
    out[keep] = fr[keep]
    # (user 2026-11-15: "the shirts change to different types") the legs wear the stand frame's trousers: every leg
    # colour snaps to the nearest colour of the stand frame's lower body
    rlow = ref[rcut:][ref[rcut:, :, 3] >= 128][:, :3].astype(np.float32)
    legs = keep & (fr[..., 3] >= 128)
    if len(rlow) and legs.any():
        pal = np.unique(rlow, axis=0)
        px = out[legs][:, :3].astype(np.float32)
        best = ((px[:, None, :] - pal[None, :, :]) ** 2).sum(-1).argmin(1)
        out[legs, :3] = pal[best].astype(np.uint8)
    # centre the stand body over the legs (the hip row's mass centre)
    def hip_cx(a, row):
        xs = np.nonzero(a[max(0, row):row + 3].any(0))[0]
        return (xs.min() + xs.max()) / 2.0 if len(xs) else None
    lc = hip_cx(keep, fcut)
    rsol = ref[..., 3] >= 128
    rc = hip_cx(rsol, rcut)
    dx = int(round(lc - rc)) if lc is not None and rc is not None else 0
    dx = int(np.clip(dx, -3, 3))
    dy = fcut - rcut
    ys, xs = np.nonzero(ref[:rcut + 1, :, 3] > 0)          # the upper body, one row of overlap at the waist
    ty, tx = ys + dy, xs + dx
    ok = (ty >= 0) & (ty < h) & (tx >= 0) & (tx < w)
    out[ty[ok], tx[ok]] = ref[ys[ok], xs[ok]]
    return out


def main():
    key = sys.argv[1]
    install = "--install" in sys.argv
    glare = "--glare" in sys.argv or key in GLARE
    st_path = os.path.join(OUT, "stationary.txt")
    moves = "--no-outfit" not in sys.argv              # (user 2026-11-15: on for every sheet)
    heads = "--head" in sys.argv or (os.path.exists(st_path) and key in open(st_path).read().split())
    j = json.load(open(os.path.join(RES, "enemy_pic.json"), encoding="utf-8"))
    ep = next(e for e in j.values() if isinstance(e, dict) and e.get("pic3d", "").endswith("/%s.png" % key))
    cols, rows = ep["aniuv"]
    path = os.path.join(RES, "enemy_pic", key + ".png")
    bk0 = os.path.join(OUT, key + "_before.png")                            # (always from the ORIGINAL sheet)
    sheet = np.array(Image.open(bk0 if os.path.exists(bk0) else path).convert("RGBA"))
    # (the game entry may describe the HD sheet - 14x12 - while this works on the 1x original: rows from the image,
    # the character frames being 80x68)
    fw = sheet.shape[1] // cols
    rows = max(1, int(round(sheet.shape[0] / (fw * 68.0 / 80.0))))
    fh = sheet.shape[0] // rows
    frames = [sheet[(i // cols) * fh:(i // cols + 1) * fh, (i % cols) * fw:(i % cols + 1) * fw].copy()
              for i in range(cols * rows)]
    role, span = {}, {}                                                     # frame -> its animation id / range
    for a in ep["animap"]:
        for f in range(a["st"], a["en"]):
            role.setdefault(f, a["id"])
            span.setdefault(f, (a["st"], a["en"]))
    refs = {}
    for a in ep["animap"]:
        if a["id"] in ("stand", "stand_f", "stand_b"):
            refs[facing(a["id"])] = a["st"]
    # (side_tama: its first back frame is bare-backed, no hat - an outfit outlier) the front / back reference is the
    # stand frame whose colours best match the side reference's outfit, not simply the first one
    def hist(f):
        px = f[f[..., 3] >= 128][:, :3] // 32
        hh_ = np.bincount((px[:, 0] * 64 + px[:, 1] * 8 + px[:, 2]).astype(int), minlength=512).astype(float)
        return hh_ / max(1.0, hh_.sum())
    if "side" in refs:
        hs = hist(frames[refs["side"]])
        for a in ep["animap"]:
            if a["id"] in ("stand_f", "stand_b"):
                cand = [i for i in range(a["st"], a["en"]) if (frames[i][..., 3] > 0).any()]
                if cand:
                    refs[facing(a["id"])] = min(cand, key=lambda i: np.abs(hist(frames[i]) - hs).sum())
    lit = [f for f in frames if (f[..., 3] > 0).any()]
    lum = np.concatenate([f[f[..., 3] > 0][:, :3] for f in lit]).astype(int)
    ink = lum[lum.sum(1).argmin()].astype(np.uint8).tolist() + [255]       # the sheet's darkest ink
    enh = {fc: clean(frames[i], ink) for fc, i in refs.items()}            # 1. the enhanced references
    pal = palette_of(list(enh.values()))
    enh = {fc: denoise(lock(f, pal), ink, glare) for fc, f in enh.items()}
    for fc, pts in PATCH.get(key, {}).items():                             # hand fixes on the masters
        if fc in enh:
            for p in pts:
                if p[0] == "smooth":
                    enh[fc] = smooth_box(enh[fc], *p[1:])
                    continue
                x, y, rgb = p
                enh[fc][y, x, :3] = rgb
                enh[fc][y, x, 3] = 255
    ref_box = {fc: bbox(f) for fc, f in enh.items()}
    # (user 2026-11-15: the rig "looks a lot better, apply across the board") side walk / run from the cutout rig:
    # the master cut into parts by the procedural rig's bones, each part moved to the frame's pose
    rig = {}
    if moves and "side" in enh:
        try:
            import rig_anim
            rig_ids = [n for n in range(len(frames)) if role.get(n) in ("walk", "run")
                       and n < len(rig_anim.s2.FRAMES) and rig_anim.s2.FRAMES[n][0] in ("walk8", "run")]
            rig, _lab = rig_anim.rig_frames(key, enh["side"], rig_ids)
        except Exception as ex:
            print("rig skipped:", ex)
            rig = {}
    msolid = int((enh["side"][..., 3] >= 128).sum()) if "side" in enh else 0
    fixed = []
    nflow = [0, 0, 0]                                                        # flow-warped / fell back
    for i, fr in enumerate(frames):
        if not (fr[..., 3] > 0).any():
            fixed.append(fr)
            continue
        aid = role.get(i, "")
        fc = facing(aid)
        if i in refs.values():
            fixed.append(enh[fc])
            continue
        f2 = clean(fr, ink)
        f2 = denoise(lock(f2, pal), ink, glare)                                    # 2. palette lock + noise
        if aid in UPRIGHT and fc in ref_box:
            f2 = fit(f2, ref_box[fc])                                       # 3. size and foot line
        flowed = False
        if i in rig and 0.85 * msolid <= int((rig[i][..., 3] >= 128).sum()) <= 1.15 * msolid:
            f2, flowed = rig[i], True                                       # 5r. the cutout rig
            nflow[2] += 1
        elif moves and aid in FLOW_IDS and fc in enh:                       # 5a. the AI frame's motion on the
            fw_, sc = flow_from_ref(enh[fc], f2)                            #     master's pixels, if it matches
            if sc >= FLOW_IOU:
                f2, flowed = fw_, True
                nflow[0] += 1
            else:
                nflow[1] += 1
        if flowed:
            pass
        elif moves and aid in MOVE and fc in enh:                           # 5b. one outfit: walk / run drawn
            st_, en_ = span.get(i, (i, i + 1))                              #     from the stand frame alone
            f2 = animate_move(enh[fc], aid, i - st_, en_ - st_)
        elif moves and aid in STILL and fc in enh:                          # 6. one outfit: still frames are the
            st_, en_ = span.get(i, (i, i + 1))                              #    stand frame, the head moving
            f2 = still_from_ref(enh[fc], aid, i - st_, en_ - st_)
        elif heads and aid in STILL and fc in enh:
            f2 = head_transplant(f2, enh[fc])                               # 4. stationary NPCs: one steady face
        fixed.append(f2)
    os.makedirs(OUT, exist_ok=True)
    new = np.zeros_like(sheet)
    for i, f in enumerate(fixed):
        new[(i // cols) * fh:(i // cols + 1) * fh, (i % cols) * fw:(i % cols + 1) * fw] = f
    # previews: before / after for the upright rows (x3), and a walk-cycle gif side by side
    show = [i for i in range(len(frames)) if role.get(i, "") in UPRIGHT][:48]
    z = 3
    comp = Image.new("RGBA", (len(show[:24]) * fw * z, 4 * fh * z), (48, 52, 60, 255))
    for row, idx in enumerate((show[:24], show[24:48])):
        for k, i in enumerate(idx):
            for half, src in enumerate((frames, fixed)):
                im = Image.fromarray(src[i]).resize((fw * z, fh * z), Image.NEAREST)
                comp.alpha_composite(im, (k * fw * z, (row * 2 + half) * fh * z))
    for name in (key + "_compare.png", key + "_compare_2.png", key + "_compare_3.png"):
        try:                                                               # (a preview open in a viewer is locked)
            comp.save(os.path.join(OUT, name))
            break
        except OSError:
            continue
    walk = [i for i in range(len(frames)) if role.get(i) == "walk"]
    gif = []
    for i in walk:
        g = Image.new("RGBA", (fw * z * 2 + 8, fh * z), (48, 52, 60, 255))
        g.alpha_composite(Image.fromarray(frames[i]).resize((fw * z, fh * z), Image.NEAREST), (0, 0))
        g.alpha_composite(Image.fromarray(fixed[i]).resize((fw * z, fh * z), Image.NEAREST), (fw * z + 8, 0))
        gif.append(g.convert("P", palette=Image.ADAPTIVE))
    if gif:
        gif[0].save(os.path.join(OUT, key + "_walk.gif"), save_all=True, append_images=gif[1:], duration=120, loop=0)
    if install:
        bk = os.path.join(OUT, key + "_before.png")
        if not os.path.exists(bk):                                         # (keep the FIRST original: a rerun
            Image.fromarray(sheet).save(bk)                                # mustn't back up a corrected sheet)
        Image.fromarray(new).save(path)
        print("installed", path)
    else:
        Image.fromarray(new).save(os.path.join(OUT, key + "_fixed.png"))
    # (user 2026-11-15: "upscale these a small bit to use in game ... you may have to scale riggings as well") the HD
    # sheet the game shows: this sheet at 2x (nearest) + a 12th row of conversation gestures (rig body at 1x, arms
    # drawn on the 2x grid). The 1x sheet stays the tools' working copy; tools/hd_sheets.py points the game at this.
    hd = None
    if moves and "side" in enh:
        try:
            import rig_anim
            g = rig_anim.gesture_frames_hd(key, enh["side"], 2)
            if g:
                up = np.repeat(np.repeat(new, 2, 0), 2, 1)
                # ("you may have to scale riggings as well") walk / run rigged on the 2x master: half-pixel limb
                # steps and finer edges on turned parts, instead of the 1x rig frames blown up
                if rig:
                    m2 = np.repeat(np.repeat(enh["side"], 2, 0), 2, 1)
                    r2, _l2 = rig_anim.rig_frames(key, m2, sorted(rig), 2)
                    s2n = int((m2[..., 3] >= 128).sum())
                    for n_, f_ in r2.items():
                        if 0.85 * s2n <= int((f_[..., 3] >= 128).sum()) <= 1.15 * s2n:
                            y_, x_ = (n_ // cols) * fh * 2, (n_ % cols) * fw * 2
                            up[y_:y_ + fh * 2, x_:x_ + fw * 2] = f_
                row = np.zeros((fh * 2, up.shape[1], 4), np.uint8)
                for q, f in enumerate(g[:cols]):
                    row[:, q * fw * 2:(q + 1) * fw * 2] = f
                hd = np.concatenate([up, row], 0)
                if "front" in enh:                                  # row 13: the same gestures facing the camera
                    gf = rig_anim.front_gestures_hd(enh["front"], 2)
                    if gf:
                        row_f = np.zeros_like(row)
                        for q, f in enumerate(gf[:cols]):
                            row_f[:, q * fw * 2:(q + 1) * fw * 2] = f
                        hd = np.concatenate([hd, row_f], 0)
        except Exception as ex:
            print("hd skipped:", ex)
    if hd is not None:
        hd_dir = os.path.join(RES, "enemy_pic2x") if install else OUT
        os.makedirs(hd_dir, exist_ok=True)
        from atomic_io import save_png
        save_png(Image.fromarray(hd), os.path.join(hd_dir, key + (".png" if install else "_hd.png")))
    print(key, "frames", len(frames), "palette", len(pal), "upright fitted", sum(1 for i in role if role[i] in UPRIGHT), "flow", nflow[0], "fallback", nflow[1], "rig", nflow[2])


if __name__ == "__main__":
    main()
